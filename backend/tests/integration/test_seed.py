from fastapi.testclient import TestClient
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.auth.models import User
from app.courses.models import Course
from app.courses.rules import CourseStatus
from app.db.seed import SEED_COURSES, SEED_USERS, seed_data


def count_rows(session: Session, model: type) -> int:
    return session.scalar(select(func.count()).select_from(model)) or 0


def test_seed_creates_users_and_courses(db_session: Session) -> None:
    # Act
    seed_data(db_session)

    # Assert
    assert count_rows(db_session, User) == len(SEED_USERS)
    assert count_rows(db_session, Course) == len(SEED_COURSES)
    published = db_session.scalar(
        select(func.count())
        .select_from(Course)
        .where(Course.status == CourseStatus.PUBLISHED.value)
    )
    assert published == 6
    admin = db_session.scalar(select(User).where(User.role == "admin"))
    assert admin is not None
    assert admin.email == "admin@roadmap.local"


def test_seed_is_idempotent(db_session: Session) -> None:
    # Act
    seed_data(db_session)
    seed_data(db_session)

    # Assert
    assert count_rows(db_session, User) == len(SEED_USERS)
    assert count_rows(db_session, Course) == len(SEED_COURSES)


def test_seeded_admin_can_login(
    client: TestClient, db_session: Session
) -> None:
    # Arrange
    seed_data(db_session)

    # Act
    response = client.post(
        "/auth/login",
        json={"email": "admin@roadmap.local", "password": "Admin123!"},
    )

    # Assert
    assert response.status_code == 200
    assert response.json()["user"]["role"] == "admin"
