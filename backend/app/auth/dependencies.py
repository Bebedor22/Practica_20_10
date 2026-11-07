from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.auth.models import User
from app.auth.security import TokenError, decode_access_token
from app.db.session import get_db

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login", auto_error=False)


def unauthorized() -> HTTPException:
    return HTTPException(
        status_code=401,
        detail={"error": "unauthorized", "code": "AUTH_001"},
        headers={"WWW-Authenticate": "Bearer"},
    )


def get_current_user(
    token: str | None = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    if not token:
        raise unauthorized()

    try:
        payload = decode_access_token(token)
    except TokenError as error:
        raise unauthorized() from error

    user = db.get(User, payload.user_id)
    if user is None:
        raise unauthorized()
    return user
