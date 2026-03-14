from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from .db import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(150), unique=True, index=True, nullable=False)
    password_hash = Column(String(200), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    links = relationship("Link", back_populates="owner")

class Link(Base):
    __tablename__ = "links"
    id = Column(Integer, primary_key=True, index=True)
    short_code = Column(String(50), unique=True, index=True, nullable=False)
    original_url = Column(Text, nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=True)
    clicks = Column(Integer, default=0)
    last_used_at = Column(DateTime(timezone=True), nullable=True)
    custom_alias = Column(String(100), unique=True, nullable=True)

    owner = relationship("User", back_populates="links")
