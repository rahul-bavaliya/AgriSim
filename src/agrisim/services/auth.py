from fastapi import HTTPException, status
from sqlalchemy.orm import Session
import jwt

from agrisim.core.security import (
    create_access_token,
    get_password_hash,
    verify_password,
    SECRET_KEY,
    ALGORITHM,
)
from agrisim.models.user import UserModel
from agrisim.schemas.auth import UserCreate


class AuthService:
    @staticmethod
    def register_user(db: Session, user_in: UserCreate):
        existing_user = (
            db.query(UserModel).filter(UserModel.email == user_in.email).first()
        )
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered")

        hashed_pwd = get_password_hash(user_in.password)
        new_user = UserModel(email=user_in.email, hashed_password=hashed_pwd)
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return {
            "id": new_user.id,
            "message": "User registered successfully",
            "email": new_user.email,
        }

    @staticmethod
    def authenticate_user(db: Session, username: str, password: str):
        user = db.query(UserModel).filter(UserModel.email == username).first()
        if not user or not verify_password(password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        access_token = create_access_token(data={"sub": user.email})
        return {"access_token": access_token, "token_type": "bearer"}
