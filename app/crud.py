from sqlalchemy.orm import Session
from . import models, utils
from datetime import datetime

def create_user(db: Session, username: str, password: str):
    hashed = utils.hash_password(password)
    user = models.User(username=username, password_hash=hashed)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def authenticate_user(db: Session, username: str, password: str):
    user = db.query(models.User).filter(models.User.username == username).first()
    if not user:
        return None
    if not utils.verify_password(password, user.password_hash):
        return None
    return user

def create_link(db: Session, original_url: str, owner_id: int | None = None, custom_alias: str | None = None, expires_at: datetime | None = None):
    if custom_alias:
        exists = db.query(models.Link).filter((models.Link.custom_alias == custom_alias) | (models.Link.short_code == custom_alias)).first()
        if exists:
            raise ValueError("Alias already in use")
        short_code = custom_alias
    else:
        short_code = utils.generate_short_code()
        while db.query(models.Link).filter(models.Link.short_code == short_code).first():
            short_code = utils.generate_short_code()
    link = models.Link(short_code=short_code, original_url=original_url, owner_id=owner_id, expires_at=expires_at, custom_alias=custom_alias)
    db.add(link)
    db.commit()
    db.refresh(link)
    return link

def get_link(db: Session, short_code: str):
    return db.query(models.Link).filter((models.Link.short_code == short_code) | (models.Link.custom_alias == short_code)).first()

def increment_click(db: Session, link: models.Link):
    link.clicks = (link.clicks or 0) + 1
    link.last_used_at = datetime.utcnow()
    db.add(link)
    db.commit()
    db.refresh(link)
    return link

def update_link(db: Session, link: models.Link, original_url: str | None = None, expires_at: datetime | None = None):
    if original_url is not None:
        link.original_url = original_url
    if expires_at is not None:
        link.expires_at = expires_at
    db.add(link)
    db.commit()
    db.refresh(link)
    return link

def delete_link(db: Session, link: models.Link):
    db.delete(link)
    db.commit()

def search_by_original(db: Session, original_url: str):
    return db.query(models.Link).filter(models.Link.original_url == original_url).all()

def delete_expired(db: Session):
    now = datetime.utcnow()
    expired = db.query(models.Link).filter(models.Link.expires_at != None).filter(models.Link.expires_at < now).all()
    for l in expired:
        db.delete(l)
    db.commit()
    return len(expired)
