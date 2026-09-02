from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from agrisim.schemas.envelope import ResponseEnvelope
from agrisim.services.deps import get_db
from agrisim.schemas.auth import UserCreate, UserResponse, Token
from agrisim.services.auth import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=ResponseEnvelope[UserResponse],
    status_code=status.HTTP_201_CREATED,
)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    user = AuthService.register_user(db=db, user_in=user_in)
    return ResponseEnvelope[UserResponse](
        status="success",
        code=201,
        message="User registered successfully",
        data=user,
    )


@router.post("/login", response_model=Token, status_code=status.HTTP_200_OK)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    return AuthService.authenticate_user(
        db=db, username=form_data.username, password=form_data.password
    )
