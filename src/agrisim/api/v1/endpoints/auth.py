from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from agrisim.core.database import SessionLocal
from agrisim.core.security import (
    create_access_token,
    get_password_hash,
    verify_password,
)
from agrisim.models.user import UserModel

router = APIRouter(prefix="/auth", tags=["Authentication"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class UserCreate(BaseModel):
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


@router.post("/register", status_code=status.HTTP_201_CREATED)
def register_user(user_in: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(UserModel).filter(UserModel.email == user_in.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_pwd = get_password_hash(user_in.password)
    new_user = UserModel(email=user_in.email, hashed_password=hashed_pwd)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "User registered successfully", "email": new_user.email}


@router.post("/login")
def login_user(user_in: UserLogin, db: Session = Depends(get_db)):
    user = db.query(UserModel).filter(UserModel.email == user_in.email).first()
    if not user or not verify_password(user_in.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}
