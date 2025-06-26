from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

# Import Base from database.py
from database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    points = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship to poems
    poems = relationship("Poem", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}')>"

class Poem(Base):
    __tablename__ = "poems"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    content = Column(Text, nullable=False)  # Use Text for longer poems
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    title = Column(String(200), nullable=True)  # Optional title for poems
    
    # Relationship to user
    user = relationship("User", back_populates="poems")
    
    def __repr__(self):
        return f"<Poem(id={self.id}, user_id={self.user_id}, title='{self.title}')>"