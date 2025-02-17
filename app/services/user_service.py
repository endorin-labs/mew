from sqlalchemy.orm import Session
from app.models.user import User
from app.core.security import hash_password, verify_password, create_access_token

def create_user(db: Session, email: str, username: str, name: str, department: str, password: str) -> User:
    hashed = hash_password(password)
    user = User(email=email, username=username, name=name, department=department, hashed_password=hashed)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def update_user(db: Session, user_id: int, email: str, username: str, name: str, department: str) -> User:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return None
    user.email = email
    user.username = username
    user.name = name
    user.department = department
    db.commit()
    db.refresh(user)
    return user

def authenticate_user(db: Session, username: str, password: str):
    user = db.query(User).filter(User.username == username).first()
    if user and verify_password(password, user.hashed_password):
        return user
    return None

def login_user(db: Session, username: str, password: str):
    user = authenticate_user(db, username, password)
    if not user:
        return None
    token = create_access_token({"user_id": user.id})
    return token, user
