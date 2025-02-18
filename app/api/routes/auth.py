from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.db.session import SessionLocal
from app.services import user_service

router = APIRouter()

# Dependency for obtaining a database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Pydantic models for request validation
class SignUp(BaseModel):
    email: str
    username: str
    name: str
    department: str
    password: str

class EditProfile(BaseModel):
    user_id: int
    email: str
    username: str
    name: str
    department: str

class Login(BaseModel):
    username: str
    password: str

@router.post("/signup", summary="User sign up")
def signup(user: SignUp, db: Session = Depends(get_db)):
    created_user = user_service.create_user(db, user.email, user.username, user.name, user.department, user.password)
    return {
        "id": created_user.id,
        "email": created_user.email,
        "username": created_user.username,
        "name": created_user.name,
        "department": created_user.department
    }

@router.put("/edit-profile", summary="Edit user profile")
def edit_profile(user: EditProfile, db: Session = Depends(get_db)):
    updated_user = user_service.update_user(db, user.user_id, user.email, user.username, user.name, user.department)
    if not updated_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return {
        "id": updated_user.id,
        "email": updated_user.email,
        "username": updated_user.username,
        "name": updated_user.name,
        "department": updated_user.department
    }

@router.post("/login", summary="User login")
def login(login_data: Login, db: Session = Depends(get_db)):
    result = user_service.login_user(db, login_data.username, login_data.password)
    if not result:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect username or password")
    token, user = result
    return {
        "token": token,
        "user": {
            "id": user.id,
            "email": user.email,
            "username": user.username,
            "name": user.name,
            "department": user.department
        }
    }