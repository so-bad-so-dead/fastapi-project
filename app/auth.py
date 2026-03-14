import os
from datetime import datetime, timedelta
import jwt
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from . import models, db

SECRET_KEY = os.getenv("SECRET_KEY", "change-me-in-prod")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24

security = HTTPBearer()
security_optional = HTTPBearer(auto_error=False)

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(token: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(db.get_db)):
    try:
        payload = jwt.decode(token.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid auth token")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Could not validate credentials")
    user = db.query(models.User).filter(models.User.username == username).first()
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return user

def get_current_user_optional(token: HTTPAuthorizationCredentials = Depends(security_optional), db: Session = Depends(db.get_db)):
    if token is None:
        return None
    try:
        payload = jwt.decode(token.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            return None
    except jwt.PyJWTError:
        return None
    user = db.query(models.User).filter(models.User.username == username).first()
    return user
