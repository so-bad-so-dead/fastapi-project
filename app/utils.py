import string
import random
from passlib.context import CryptContext
from datetime import datetime

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")


def generate_short_code(length: int = 6):
    alphabet = string.ascii_letters + string.digits
    return ''.join(random.choice(alphabet) for _ in range(length))


def get_now():
    return datetime.now()


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)
