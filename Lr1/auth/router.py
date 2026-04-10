from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import or_
from sqlmodel import Session, select

from auth.auth import auth_service
from connection import get_session
from models import (
    ApiMessage,
    TokenResponse,
    User,
    UserLogin,
    UserPasswordChange,
    UserRead,
    UserRegister,
)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/register",
    response_model=ApiMessage,
    status_code=status.HTTP_201_CREATED,
)
def register_user(
    user_data: UserRegister,
    db_session: Session = Depends(get_session),
) -> ApiMessage:
    existing_user = db_session.exec(
        select(User).where(
            or_(User.username == user_data.username, User.email == user_data.email)
        )
    ).first()

    if existing_user:
        if existing_user.username == user_data.username:
            raise HTTPException(status_code=400, detail="Username already registered")
        raise HTTPException(status_code=400, detail="Email already registered")

    new_user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=auth_service.hash_password(user_data.password),
    )
    db_session.add(new_user)
    db_session.commit()

    return ApiMessage(message="User created successfully")


@router.post("/login", response_model=TokenResponse)
def login_user(
    login_data: UserLogin,
    db_session: Session = Depends(get_session),
) -> TokenResponse:
    user_record = db_session.exec(
        select(User).where(User.username == login_data.username)
    ).first()

    if not user_record:
        raise HTTPException(status_code=401, detail="Invalid username or password")

    if not auth_service.verify_password(
        login_data.password, user_record.hashed_password
    ):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    return TokenResponse(access_token=auth_service.create_token(user_record.username))


@router.get("/me", response_model=UserRead)
def read_current_user(
    current_user: User = Depends(auth_service.get_current_user),
) -> UserRead:
    return UserRead(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        created_at=current_user.created_at,
    )


@router.patch("/password", response_model=ApiMessage)
def update_password(
    password_data: UserPasswordChange,
    current_user: User = Depends(auth_service.get_current_user),
    db_session: Session = Depends(get_session),
) -> ApiMessage:
    if not auth_service.verify_password(
        password_data.old_password, current_user.hashed_password
    ):
        raise HTTPException(status_code=400, detail="Incorrect current password")

    current_user.hashed_password = auth_service.hash_password(
        password_data.new_password
    )
    db_session.add(current_user)
    db_session.commit()

    return ApiMessage(message="Password updated successfully")
