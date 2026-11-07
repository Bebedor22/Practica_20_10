from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.auth.models import User
from app.auth.repository import UserRepository
from app.auth.schemas import (
    LoginRequest,
    RegisterRequest,
    TokenResponse,
    UserRead,
)
from app.auth.security import create_access_token, hash_password, verify_password
from app.db.session import get_db

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserRead, status_code=201)
def register(payload: RegisterRequest, db: Session = Depends(get_db)) -> User:
    repository = UserRepository(db)
    if repository.get_by_email(payload.email) is not None:
        raise HTTPException(
            status_code=409,
            detail={
                "error": "email already registered",
                "code": "EMAIL_ALREADY_REGISTERED",
            },
        )

    try:
        return repository.create(
            name=payload.name,
            email=payload.email,
            password_hash=hash_password(payload.password),
        )
    except IntegrityError as error:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail={
                "error": "email already registered",
                "code": "EMAIL_ALREADY_REGISTERED",
            },
        ) from error


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    user = UserRepository(db).get_by_email(payload.email)
    if user is None or not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=401,
            detail={
                "error": "invalid credentials",
                "code": "INVALID_CREDENTIALS",
            },
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = create_access_token(user.id, role=user.role)
    return TokenResponse(
        access_token=token,
        user=UserRead.model_validate(user),
    )


@router.get("/me", response_model=UserRead)
def me(current_user: User = Depends(get_current_user)) -> User:
    return current_user
