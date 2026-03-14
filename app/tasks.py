import time
import threading
from sqlalchemy.exc import OperationalError
from .db import SessionLocal, engine, Base
from .crud import delete_expired


def wait_for_db(retries: int = 30, delay: int = 1):
    for i in range(retries):
        try:
            conn = engine.connect()
            conn.close()
            return True
        except OperationalError:
            time.sleep(delay)
    return False


def create_db():
    ok = wait_for_db()
    if not ok:
        # give one last try and let the error propagate
        Base.metadata.create_all(bind=engine)
    else:
        Base.metadata.create_all(bind=engine)


def start_cleanup_task(interval_seconds: int = 60):
    def loop():
        while True:
            db = SessionLocal()
            try:
                delete_expired(db)
            except Exception:
                pass
            finally:
                db.close()
            time.sleep(interval_seconds)

    t = threading.Thread(target=loop, daemon=True)
    t.start()
