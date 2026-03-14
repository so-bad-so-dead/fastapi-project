
from pydantic import BaseModel, HttpUrl
from datetime import datetime
from typing import Optional


class UserCreate(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class LinkCreate(BaseModel):
    original_url: HttpUrl
    custom_alias: Optional[str] = None
    expires_at: Optional[datetime] = None

class LinkUpdate(BaseModel):
    original_url: Optional[HttpUrl]
    expires_at: Optional[datetime]

class LinkOut(BaseModel):
    short_code: str
    original_url: HttpUrl
    created_at: datetime
    expires_at: Optional[datetime]
    clicks: int

    class Config:
        orm_mode = True
