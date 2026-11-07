from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

import bcrypt
import jwt

from app.core.config import get_settings

BCRYPT_ROUNDS = 12
JWT_ALGORITHM = "HS256"


class TokenError(ValueError):
    pass


@dataclass(frozen=True)
class TokenPayload:
    user_id: int
    role: str


def hash_password(password: str) -> str:
    password_bytes = password.encode("utf-8")
    return bcrypt.hashpw(
        password_bytes, bcrypt.gensalt(rounds=BCRYPT_ROUNDS)
    ).decode("ascii")


def verify_password(password: str, password_hash: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("ascii"))
    except (TypeError, ValueError):
        return False


def create_access_token(
    user_id: int,
    *,
    role: str,
    expires_minutes: int | None = None,
) -> str:
    settings = get_settings()
    now = datetime.now(UTC)
    expires_at = now + timedelta(
        minutes=expires_minutes or settings.jwt_expires_minutes
    )
    payload = {
        "sub": str(user_id),
        "role": role,
        "iat": now,
        "exp": expires_at,
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=JWT_ALGORITHM)


def decode_access_token(token: str) -> TokenPayload:
    settings = get_settings()
    try:
        payload = jwt.decode(
            token, settings.jwt_secret, algorithms=[JWT_ALGORITHM]
        )
        subject = payload.get("sub")
        if subject is None:
            raise TokenError("Token sin sujeto")
        return TokenPayload(
            user_id=int(subject),
            role=str(payload.get("role", "user")),
        )
    except (jwt.InvalidTokenError, TypeError, ValueError) as error:
        raise TokenError("Token inválido o expirado") from error
