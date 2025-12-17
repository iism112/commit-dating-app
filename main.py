from fastapi import FastAPI, Depends, HTTPException, Body, UploadFile, File, Header, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Optional
from pydantic import BaseModel
import datetime
import math
import os
import shutil
import json
from fastapi import WebSocket, WebSocketDisconnect

# Ensure uploads directory exists
UPLOAD_DIR = "static/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

import models
from database import engine, get_db

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Mount static/uploads specifically to be accessible at /static/uploads
app.mount("/static", StaticFiles(directory="static"), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- WebSocket Manager ---
class ConnectionManager:
    def __init__(self):
        # Map user_id -> WebSocket
        self.active_connections: Dict[int, WebSocket] = {}

    async def connect(self, websocket: WebSocket, user_id: int):
        await websocket.accept()
        self.active_connections[user_id] = websocket
        print(f"WS: User {user_id} connected")

    def disconnect(self, user_id: int):
        if user_id in self.active_connections:
            del self.active_connections[user_id]
            print(f"WS: User {user_id} disconnected")

    async def send_personal_message(self, message: dict, user_id: int):
        if user_id in self.active_connections:
            websocket = self.active_connections[user_id]
            try:
                await websocket.send_json(message)
            except Exception as e:
                print(f"WS Error sending to {user_id}: {e}")
                self.disconnect(user_id)

manager = ConnectionManager()

# Pydantic Schemas
class ActionCreate(BaseModel):
    target_id: int
    action_type: str # 'like', 'pass'

class MessageCreate(BaseModel):
    match_id: int
    text: str

class UserRegister(BaseModel):
    name: str
    email: str
    password: str
    role: str

class UserLogin(BaseModel):
    email: str
    password: str

class UserUpdate(BaseModel):
    name: Optional[str] = None
    role: Optional[str] = None
    bio: Optional[str] = None
    stack: Optional[List[str]] = None
    image: Optional[str] = None

class UserRead(BaseModel):
    id: int
    name: str
    role: str
    bio: str
    stack: List[str]
    image: str
    location_lat: float
    location_lng: float
    match_score: int = 0
    
    class Config:
        orm_mode = True

# Auth Dependency
def get_current_user(x_user_id: Optional[str] = Header(None)):
    if not x_user_id:
        # For simplicity in this demo, we allow missing header to mean "Not Logged In" 
        # or raise 401. But endpoints usually require it.
        # Let's enforce it.
        raise HTTPException(status_code=401, detail="Missing X-User-Id header")
    return int(x_user_id)

# Helper: Jaccard Similarity
def calculate_match_score(stack1: List[str], stack2: List[str]) -> int:
    if not stack1 or not stack2:
        return 0
    s1 = set([s.lower() for s in stack1])
    s2 = set([s.lower() for s in stack2])
    intersection = len(s1.intersection(s2))
    union = len(s1.union(s2))
    if union == 0: return 0
    return int((intersection / union) * 100)

@app.get("/api/profiles", response_model=List[UserRead])
def get_profiles(current_user_id: int = Depends(get_current_user), db: Session = Depends(get_db)):
    # Get current user for matching
    me = db.query(models.User).filter(models.User.id == current_user_id).first()
    if not me:
        raise HTTPException(status_code=404, detail="Current user not found")

    # Get profiles NOT acted upon by current user
    acted_ids = [a.target_id for a in db.query(models.Action).filter(models.Action.user_id == current_user_id).all()]
    acted_ids.append(current_user_id) # Don't show myself
    
    profiles = db.query(models.User).filter(models.User.id.notin_(acted_ids)).all()
    
    # Calculate Scores and Sort
    results = []
    for p in profiles:
        p_dict = UserRead.from_orm(p).dict()
        p_dict['match_score'] = calculate_match_score(me.stack, p.stack)
        results.append(p_dict)
        
    # Sort by Score DESC
    return sorted(results, key=lambda x: x['match_score'], reverse=True)

@app.get("/api/profiles/{user_id}", response_model=UserRead)
def get_profile(user_id: int, db: Session = Depends(get_db), current_user_id: Optional[int] = Depends(get_current_user)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    # Optional: Calculate score if looking at someone else
    score = 0
    if current_user_id:
         me = db.query(models.User).filter(models.User.id == current_user_id).first()
         if me:
             score = calculate_match_score(me.stack, user.stack)
             
    p_dict = UserRead.from_orm(user).dict()
    p_dict['match_score'] = score
    return p_dict

@app.get("/api/profile/me", response_model=UserRead)
def get_my_profile(current_user_id: int = Depends(get_current_user), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == current_user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.put("/api/profile/me", response_model=UserRead)
def update_my_profile(update_data: UserUpdate, current_user_id: int = Depends(get_current_user), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == current_user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if update_data.name is not None: user.name = update_data.name
    if update_data.role is not None: user.role = update_data.role
    if update_data.bio is not None: user.bio = update_data.bio
    if update_data.stack is not None: user.stack = update_data.stack
    if update_data.image is not None: user.image = update_data.image
    
    db.commit()
    db.refresh(user)
    return user

@app.post("/api/upload")
async def upload_image(file: UploadFile = File(...)):
    file_location = f"{UPLOAD_DIR}/{file.filename}"
    with open(file_location, "wb+") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return {"url": f"/{file_location}"}

# Auth Endpoints
@app.post("/api/register")
def register(user: UserRegister, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    new_user = models.User(
        name=user.name,
        email=user.email,
        password=user.password,
        role=user.role,
        bio="Hello! I'm new here.",
        stack=[],
        image="https://ui-avatars.com/api/?name=" + user.name,
        location_lat=40.7128 + (math.sin(datetime.datetime.now().timestamp()) * 0.01), # Random-ish
        location_lng=-74.0060 + (math.cos(datetime.datetime.now().timestamp()) * 0.01)
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"id": new_user.id, "name": new_user.name}

@app.post("/api/login")
def login(creds: UserLogin, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == creds.email, models.User.password == creds.password).first()
    if not user:
        raise HTTPException(status_code=400, detail="Invalid credentials")
    return {"id": user.id, "name": user.name}

@app.post("/api/action")
def perform_action(action: ActionCreate, current_user_id: int = Depends(get_current_user), db: Session = Depends(get_db)):
    # Save action
    new_action = models.Action(
        user_id=current_user_id,
        target_id=action.target_id,
        action_type=action.action_type,
        timestamp=datetime.datetime.now()
    )
    db.add(new_action)
    db.commit()
    
    # Check Match if Like
    is_match = False
    if action.action_type == 'like':
        reverse_like = db.query(models.Action).filter(
            models.Action.user_id == action.target_id,
            models.Action.target_id == current_user_id,
            models.Action.action_type == 'like'
        ).first()
        
        if reverse_like:
            match = models.Match(
                user1_id=current_user_id,
                user2_id=action.target_id,
                timestamp=datetime.datetime.now()
            )
            db.add(match)
            db.commit()
            is_match = True
            
    return {"success": True, "match": is_match}

@app.get("/api/matches", response_model=List[UserRead])
def get_matches(current_user_id: int = Depends(get_current_user), db: Session = Depends(get_db)):
    matches = db.query(models.Match).filter(
        or_(models.Match.user1_id == current_user_id, models.Match.user2_id == current_user_id)
    ).all()
    
    matched_ids = []
    for m in matches:
        if m.user1_id == current_user_id:
            matched_ids.append(m.user2_id)
        else:
            matched_ids.append(m.user1_id)
            
    return db.query(models.User).filter(models.User.id.in_(matched_ids)).all()

@app.get("/api/notifications")
def get_notifications(current_user_id: int = Depends(get_current_user), db: Session = Depends(get_db)):
    count = db.query(models.Message).filter(
        models.Message.sender_id != current_user_id, # Msg from others
        models.Message.match_id.in_(
            db.query(models.Match.id).filter(
                or_(models.Match.user1_id == current_user_id, models.Match.user2_id == current_user_id)
            )
        ),
        models.Message.is_read == False
    ).count()
    return {"unread_count": count}

@app.get("/api/messages/{match_partner_id}")
def get_messages(match_partner_id: int, current_user_id: int = Depends(get_current_user), db: Session = Depends(get_db)):
    # Find match ID
    match = db.query(models.Match).filter(
        or_(
            (models.Match.user1_id == current_user_id) & (models.Match.user2_id == match_partner_id),
            (models.Match.user1_id == match_partner_id) & (models.Match.user2_id == current_user_id)
        )
    ).first()
    
    if not match:
        return []
        
    msgs = db.query(models.Message).filter(models.Message.match_id == match.id).all()
    
    # Mark incoming messages as read
    for m in msgs:
        if m.sender_id != current_user_id and not m.is_read:
            m.is_read = True
            db.add(m)
    db.commit()
    
    # Format for frontend 
    formatted = []
    for m in msgs:
        formatted.append({
            "text": m.content,
            "sender": "me" if m.sender_id == current_user_id else "them",
            "timestamp": m.timestamp
        })
    return formatted

@app.post("/api/messages")
async def send_message(msg: MessageCreate, current_user_id: int = Depends(get_current_user), db: Session = Depends(get_db)):
    # 'match_id' in legacy JS was actually PROFILE ID of the other user. 
    partner_id = msg.match_id 
    
    match = db.query(models.Match).filter(
        or_(
            (models.Match.user1_id == current_user_id) & (models.Match.user2_id == partner_id),
            (models.Match.user1_id == partner_id) & (models.Match.user2_id == current_user_id)
        )
    ).first()
    
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
        
    db_msg = models.Message(
        match_id=match.id,
        sender_id=current_user_id,
        content=msg.text,
        timestamp=datetime.datetime.now().isoformat(),
        is_read=False
    )
    db.add(db_msg)
    db.commit()
    
    # --- WebSocket Broadcast ---
    await manager.send_personal_message({
        "type": "new_message",
        "sender_id": current_user_id,
        "text": msg.text,
        "timestamp": db_msg.timestamp
    }, partner_id)
    
    return {"success": True}

@app.get("/api/nearby")
def get_nearby(lat: float, lng: float, current_user_id: int = Depends(get_current_user), db: Session = Depends(get_db)):
    # Simple calculation in python
    # Get all users
    users = db.query(models.User).filter(models.User.id != current_user_id).all()
    
    results = []
    for u in users:
        # Haversine
        R = 6371
        dLat = (u.location_lat - lat) * (math.pi / 180)
        dLon = (u.location_lng - lng) * (math.pi / 180)
        a = math.sin(dLat/2) * math.sin(dLat/2) + \
            math.cos(lat * (math.pi/180)) * math.cos(u.location_lat * (math.pi/180)) * \
            math.sin(dLon/2) * math.sin(dLon/2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        d = R * c
        
        # Return user dict with distance
        u_dict = UserRead.from_orm(u).dict()
        u_dict['distance'] = round(d)
        results.append(u_dict)
        
    return sorted(results, key=lambda x: x['distance'])

@app.get("/api/likes/received", response_model=List[UserRead])
def get_likes_received(current_user_id: int = Depends(get_current_user), db: Session = Depends(get_db)):
    actions = db.query(models.Action).filter(
        models.Action.target_id == current_user_id,
        models.Action.action_type == 'like'
    ).all()
    sender_ids = [a.user_id for a in actions]
    return db.query(models.User).filter(models.User.id.in_(sender_ids)).all()

@app.get("/api/likes/sent", response_model=List[UserRead])
def get_likes_sent(current_user_id: int = Depends(get_current_user), db: Session = Depends(get_db)):
    actions = db.query(models.Action).filter(
        models.Action.user_id == current_user_id,
        models.Action.action_type == 'like'
    ).all()
    target_ids = [a.target_id for a in actions]
    return db.query(models.User).filter(models.User.id.in_(target_ids)).all()

# Static Files
app.mount("/", StaticFiles(directory=".", html=True), name="static")


if __name__ == "__main__":
    import uvicorn
    # Kill old process on 8080 if possible? No.
    # Run on 8000.
    uvicorn.run(app, host="0.0.0.0", port=8000)
