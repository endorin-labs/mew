import bcrypt
import jwt
from app.core.config import get_settings


def hash_password(password: str) -> str:
    hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))


def create_access_token(data: dict) -> str:
    settings = get_settings()  # Get an instance of Settings
    return jwt.encode(data, settings.secret_key, algorithm="HS256")  # Use settings.SECRET_KEY
