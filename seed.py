from database import SessionLocal, engine
import models
import json

# Re-create tables
models.Base.metadata.drop_all(bind=engine)
models.Base.metadata.create_all(bind=engine)

db = SessionLocal()

# Initial Data
profiles = [
    {
        "id": 1,
        "name": "Sarah Chen",
        "role": "Frontend Architect",
        "bio": "git commit -m 'looking for someone to center my div'",
        "stack": ["React", "TypeScript", "Tailwind", "Three.js", "Figma"],
        "image": "https://images.unsplash.com/photo-1494790108377-be9c29b29330?auto=format&fit=crop&w=500&q=80",
        "location_lat": 40.7228, "location_lng": -73.9960
    },
    {
        "id": 2,
        "name": "Alex Rodriguez",
        "role": "Systems Engineer",
        "bio": "Rust enthusiast. I promise not to rewrite your codebase.",
        "stack": ["Rust", "Go", "Kubernetes", "Linux", "C++"],
        "image": "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?auto=format&fit=crop&w=500&q=80",
        "location_lat": 40.6928, "location_lng": -74.0010
    },
    {
        "id": 3,
        "name": "Jordan Taylor",
        "role": "AI Researcher",
        "bio": "Training models by day, debugging life by night.",
        "stack": ["Python", "PyTorch", "TensorFlow", "CUDA", "FastAPI"],
        "image": "https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?auto=format&fit=crop&w=500&q=80",
        "location_lat": 40.7278, "location_lng": -74.0160
    },
    {
        "id": 4,
        "name": "Emily Zhang",
        "role": "Full Stack Dev",
        "bio": "Tabs over spaces. VIM over VS Code. Fight me.",
        "stack": ["Node.js", "Vue", "Postgres", "AWS", "Python"],
        "image": "https://images.unsplash.com/photo-1580489944761-15a19d654956?auto=format&fit=crop&w=500&q=80",
        "location_lat": 40.7078, "location_lng": -74.0260
    },
    {
        "id": 5,
        "name": "David Kim",
        "role": "DevOps Engineer",
        "bio": "If it works on my machine, we ship my machine.",
        "stack": ["Docker", "Terraform", "CI/CD", "Bash", "Go"],
        "image": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?auto=format&fit=crop&w=500&q=80",
        "location_lat": 40.7428, "location_lng": -73.9760
    }
]

for p in profiles:
    user = models.User(
        id=p['id'],
        username=f"user{p['id']}",
        name=p['name'],
        role=p['role'],
        bio=p['bio'],
        stack=p['stack'],
        image=p['image'],
        location_lat=p['location_lat'],
        location_lng=p['location_lng'],
        email=f"user{p['id']}@test.com",
        password="password"
    )
    db.merge(user)

# Matches to test chat
# Sarah (1) likes Jordan (3)
action1 = models.Action(user_id=1, target_id=3, action_type='like', timestamp='2025-01-01T12:00:00')
db.add(action1)
# Jordan (3) likes Sarah (1) -> Match
action2 = models.Action(user_id=3, target_id=1, action_type='like', timestamp='2025-01-01T12:05:00')
db.add(action2)
match = models.Match(user1_id=3, user2_id=1, timestamp='2025-01-01T12:05:00')
db.add(match)

db.commit()
db.close()
print("Database re-seeded with rich stacks.")
