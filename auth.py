from passlib.context import CryptContext
from jose import jwt, JWTError
from datetime import datetime, timedelta
import os

# Use environment variables for security
SECRET_KEY = os.getenv("SECRET_KEY", "your_default_secret_key_here")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)

def create_token(data: dict, expires_delta: timedelta = None) -> str:
    """Create a JWT token"""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire, "iat": datetime.utcnow()})
    
    try:
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    except Exception as e:
        raise ValueError(f"Token creation failed: {str(e)}")

def decode_token(token: str) -> dict:
    """Decode and verify a JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # Check if token has expired
        exp = payload.get("exp")
        if exp and datetime.utcnow() > datetime.fromtimestamp(exp):
            return None
            
        return payload
    except JWTError as e:
        print(f"JWT Error: {str(e)}")  # Log for debugging
        return None
    except Exception as e:
        print(f"Token decode error: {str(e)}")  # Log for debugging
        return None

def create_access_token(username: str) -> str:
    """Create an access token for a specific user"""
    token_data = {"sub": username, "type": "access"}
    return create_token(token_data)

def get_username_from_token(token: str) -> str:
    """Extract username from token"""
    payload = decode_token(token)
    if payload:
        return payload.get("sub")
    return None