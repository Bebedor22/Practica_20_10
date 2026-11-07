from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.auth.models import User


def normalize_email(email: str) -> str:
    return email.strip().lower()


class UserRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_by_id(self, user_id: int) -> User | None:
        return self.session.get(User, user_id)

    def get_by_email(self, email: str) -> User | None:
        statement = select(User).where(
            func.lower(User.email) == normalize_email(email)
        )
        return self.session.scalar(statement)

    def create(
        self,
        *,
        name: str,
        email: str,
        password_hash: str,
        role: str = "user",
    ) -> User:
        user = User(
            name=name.strip(),
            email=normalize_email(email),
            password_hash=password_hash,
            role=role,
        )
        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)
        return user
