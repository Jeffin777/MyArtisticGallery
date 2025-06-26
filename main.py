from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, validator
from sqlalchemy.orm import Session
from sarvamai import SarvamAI
from database import SessionLocal, create_db, get_db

from models import User, Poem
from auth import hash_password, verify_password, create_token, decode_token

from datetime import datetime
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()
create_db()

# Allow frontend to call this backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Use environment variable for API key (fallback to placeholder for development)
SARVAM_API_KEY = "your_sarvam_api"  
client = SarvamAI(api_subscription_key=SARVAM_API_KEY)

class ChatRequest(BaseModel):
    message: str
    
    @validator('message')
    def message_must_not_be_empty(cls, v):
        if not v.strip():
            raise ValueError('Message cannot be empty')
        if len(v) > 1000:
            raise ValueError('Message too long (max 1000 characters)')
        return v.strip()

class SavePoemRequest(BaseModel):
    token: str
    message: str
    
    @validator('message')
    def message_must_not_be_empty(cls, v):
        if not v.strip():
            raise ValueError('Poem content cannot be empty')
        if len(v) > 5000:
            raise ValueError('Poem too long (max 5000 characters)')
        return v.strip()

class UserCreate(BaseModel):
    username: str
    password: str
    
    @validator('username')
    def username_validator(cls, v):
        if len(v) < 3:
            raise ValueError('Username must be at least 3 characters')
        if len(v) > 50:
            raise ValueError('Username too long (max 50 characters)')
        return v.strip()
    
    @validator('password')
    def password_validator(cls, v):
        if len(v) < 6:
            raise ValueError('Password must be at least 6 characters')
        return v

# Route for generating poems (AI chat)
@app.post("/generate-poem")
async def generate_poem(request: ChatRequest):
    try:
        logger.info(f"Generating poem for message: {request.message[:50]}...")
        
        messages = [
            {
                "role": "system",
                "content": (
                   "You are a poetic soul and emotional storyteller. When the user shares a small, joyful, or meaningful moment from their day — "
                "even something ordinary — transform it into a beautiful poem with at least four to five lines. Your poem should feel like a memory captured in verse: "
                "expressive, flowing, and filled with warmth. Use full, complete poetic lines — not just phrases or fragments. Avoid overusing commas or short word bursts. "
                "Write with imagery, gentle emotion, and elegance, as if the poem belongs in a handwritten diary. Respond only with the poem, and nothing else."
                "put '#' at starting and ending of the poem"
        
                )
            },
            {
                "role": "user",
                "content": request.message
            }
        ]
        
        response = client.chat.completions(
            messages=messages, 
            temperature=0.7, 
            reasoning_effort="low", 
        )
        
        poem_content = response.choices[0].message.content
        
        logger.info(f"Generated poem successfully: {len(poem_content)} characters")
        
        
        return {"reply": poem_content}
    
    except Exception as e:
        logger.error(f"Failed to generate poem: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate poem: {str(e)}")

# Route for saving poems
@app.post("/save-poem")
async def save_poem(request: SavePoemRequest, db: Session = Depends(get_db)):
    try:
        logger.info(f"Attempting to save poem for token: {request.token[:20]}...")
        
        # Decode and validate token
        payload = decode_token(request.token)
        if not payload:
            logger.warning("Invalid or expired token provided")
            raise HTTPException(status_code=401, detail="Invalid or expired token")

        username = payload.get("sub")
        if not username:
            logger.warning("Token missing username")
            raise HTTPException(status_code=401, detail="Invalid token format")

        # Find user
        user = db.query(User).filter(User.username == username).first()
        if not user:
            logger.warning(f"User not found: {username}")
            raise HTTPException(status_code=404, detail="User not found")
            
        logger.info(f"Found user: {user.username} (ID: {user.id})")
        
        # Create new poem
        new_poem = Poem(
            user_id=user.id, 
            content=request.message, 
            timestamp=datetime.utcnow()
        )
        
        db.add(new_poem)
        db.commit()
        db.refresh(new_poem)
        
        logger.info(f"Poem saved successfully with ID: {new_poem.id}")

        return {
            "msg": "Poem saved successfully", 
            "poem_id": new_poem.id,
            "timestamp": new_poem.timestamp
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to save poem: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to save poem: {str(e)}")

@app.post("/register")
def register(user: UserCreate, db: Session = Depends(get_db)):
    try:
        logger.info(f"Registering new user: {user.username}")
        
        # Check if username already exists
        existing_user = db.query(User).filter(User.username == user.username).first()
        if existing_user:
            logger.warning(f"Username already exists: {user.username}")
            raise HTTPException(status_code=400, detail="Username already exists")
        
        new_user = User(
            username=user.username, 
            hashed_password=hash_password(user.password)
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        logger.info(f"User registered successfully: {new_user.username} (ID: {new_user.id})")
        
        return {"msg": "User registered successfully", "user_id": new_user.id}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration failed: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Registration failed: {str(e)}")

@app.post("/login")
def login(user: UserCreate, db: Session = Depends(get_db)):
    try:
        logger.info(f"Login attempt for user: {user.username}")
        
        db_user = db.query(User).filter(User.username == user.username).first()
        if not db_user:
            logger.warning(f"User not found: {user.username}")
            raise HTTPException(status_code=401, detail="Invalid username or password")
        
        if not verify_password(user.password, db_user.hashed_password):
            logger.warning(f"Invalid password for user: {user.username}")
            raise HTTPException(status_code=401, detail="Invalid username or password")
        
        token = create_token({"sub": db_user.username})
        logger.info(f"Login successful for user: {user.username}")
        
        return {"token": token, "username": db_user.username}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Login failed: {str(e)}")

# Get user's saved poems
@app.get("/my-poems")
def get_my_poems(token: str, db: Session = Depends(get_db)):
    try:
        logger.info(f"Fetching poems for token: {token[:20]}...")
        
        payload = decode_token(token)
        if not payload:
            raise HTTPException(status_code=401, detail="Invalid or expired token")

        username = payload.get("sub")
        user = db.query(User).filter(User.username == username).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
            
        poems = db.query(Poem).filter(Poem.user_id == user.id).order_by(Poem.timestamp.desc()).all()
        
        logger.info(f"Found {len(poems)} poems for user: {username}")
        
        return {
            "poems": [
                {
                    "id": p.id, 
                    "content": p.content, 
                    "timestamp": p.timestamp,
                    "title": p.title
                } 
                for p in poems
            ]
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to fetch poems: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch poems: {str(e)}")

# Keep the chat alias for backward compatibility
@app.post("/chat")
async def chat_alias(request: ChatRequest):
    """Alias endpoint for generating poems - kept for backward compatibility"""
    return await generate_poem(request)

# Health check endpoint
@app.get("/health")
def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow()}

# Debug endpoint to check database
@app.get("/debug/users")
def debug_users(db: Session = Depends(get_db)):
    """Debug endpoint to check users in database"""
    users = db.query(User).all()
    return {
        "total_users": len(users),
        "users": [{"id": u.id, "username": u.username, "created_at": u.created_at} for u in users]
    }

@app.get("/debug/poems")
def debug_poems(db: Session = Depends(get_db)):
    """Debug endpoint to check poems in database"""
    poems = db.query(Poem).all()
    return {
        "total_poems": len(poems),
        "poems": [
            {
                "id": p.id, 
                "user_id": p.user_id, 
                "content": p.content[:100] + "..." if len(p.content) > 100 else p.content,
                "timestamp": p.timestamp
            } 
            for p in poems
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")