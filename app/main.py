import os
from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from . import db, models, crud, schemas, auth
import redis
from datetime import datetime

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
redis_client = redis.from_url(REDIS_URL)

app = FastAPI(title="API-сервис сокращения ссылок")

@app.on_event("startup")
def startup():
    from .tasks import create_db, start_cleanup_task
    create_db()
    start_cleanup_task()

@app.post('/register', response_model=schemas.Token)
def register(user: schemas.UserCreate, db: Session = Depends(db.get_db)):
    existing = db.query(models.User).filter(models.User.username == user.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username taken")
    u = crud.create_user(db, user.username, user.password)
    token = auth.create_access_token({"sub": u.username})
    return {"access_token": token}

@app.post('/login', response_model=schemas.Token)
def login(form: schemas.UserCreate, db: Session = Depends(db.get_db)):
    user = crud.authenticate_user(db, form.username, form.password)
    if not user:
        raise HTTPException(status_code=400, detail="Invalid credentials")
    token = auth.create_access_token({"sub": user.username})
    return {"access_token": token}

@app.post('/links/shorten', response_model=schemas.LinkOut)
def shorten(link_in: schemas.LinkCreate, current_user = Depends(auth.get_current_user_optional), db: Session = Depends(db.get_db)):
    owner_id = getattr(current_user, 'id', None) if current_user else None
    try:
        link = crud.create_link(db, link_in.original_url, owner_id=owner_id, custom_alias=link_in.custom_alias, expires_at=link_in.expires_at)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    # cache mapping
    redis_client.set(link.short_code, link.original_url)
    return link

@app.get('/{short_code}')
def redirect_short(short_code: str, db: Session = Depends(db.get_db)):
    # try cache
    original = redis_client.get(short_code)
    if original:
        original = original.decode()
    else:
        link = crud.get_link(db, short_code)
        if not link:
            raise HTTPException(status_code=404, detail="Not found")
        if link.expires_at and link.expires_at < datetime.utcnow():
            crud.delete_link(db, link)
            redis_client.delete(short_code)
            raise HTTPException(status_code=404, detail="Expired")
        original = link.original_url
    # increment stats in DB
    link = crud.get_link(db, short_code)
    if link:
        crud.increment_click(db, link)
    return RedirectResponse(original)

@app.get('/links/{short_code}/stats')
def stats(short_code: str, db: Session = Depends(db.get_db)):
    link = crud.get_link(db, short_code)
    if not link:
        raise HTTPException(status_code=404, detail="Not found")
    return {
        "original_url": link.original_url,
        "created_at": link.created_at,
        "clicks": link.clicks,
        "last_used_at": link.last_used_at,
        "expires_at": link.expires_at,
    }

@app.delete('/links/{short_code}')
def delete(short_code: str, current_user = Depends(auth.get_current_user), db: Session = Depends(db.get_db)):
    link = crud.get_link(db, short_code)
    if not link:
        raise HTTPException(status_code=404, detail="Not found")
    if link.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not allowed")
    crud.delete_link(db, link)
    redis_client.delete(short_code)
    return {"ok": True}

@app.put('/links/{short_code}', response_model=schemas.LinkOut)
def update(short_code: str, upd: schemas.LinkUpdate, current_user = Depends(auth.get_current_user), db: Session = Depends(db.get_db)):
    link = crud.get_link(db, short_code)
    if not link:
        raise HTTPException(status_code=404, detail="Not found")
    if link.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not allowed")
    link = crud.update_link(db, link, original_url=upd.original_url, expires_at=upd.expires_at)
    redis_client.set(link.short_code, link.original_url)
    return link

@app.get('/links/search')
def search(original_url: str, db: Session = Depends(db.get_db)):
    results = crud.search_by_original(db, original_url)
    return [ {"short_code": r.short_code, "original_url": r.original_url} for r in results ]
