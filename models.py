from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    # Simple profile data stored directly on user for MVP
    name = Column(String)
    role = Column(String)
    bio = Column(String)
    stack = Column(JSON) # List of strings
    image = Column(String) 
    location_lat = Column(Float)
    location_lng = Column(Float)
    
    # Auth
    email = Column(String, unique=True, index=True)
    password = Column(String) # Storing plain for MVP, ideally Hash

class Action(Base):
    __tablename__ = "actions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id")) # Who performed the action
    target_id = Column(Integer, ForeignKey("users.id")) # Who was acted upon
    action_type = Column(String) # 'like', 'pass'
    timestamp = Column(String)

class Match(Base):
    __tablename__ = "matches"

    id = Column(Integer, primary_key=True, index=True)
    user1_id = Column(Integer, ForeignKey("users.id"))
    user2_id = Column(Integer, ForeignKey("users.id"))
    timestamp = Column(String)

class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    match_id = Column(Integer, ForeignKey("matches.id"))
    sender_id = Column(Integer, ForeignKey("users.id"))
    content = Column(String)
    timestamp = Column(String)
    is_read = Column(Boolean, default=False)
