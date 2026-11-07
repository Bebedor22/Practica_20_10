import os
from collections.abc import Callable, Iterator
from itertools import count

import psycopg
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine, make_url
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import get_settings

settings = get_settings()
os.environ["DATABASE_URL"] = settings.test_database_url
get_settings.cache_clear()

from app.auth.models import User
from app.courses.models import Course
from app.db.base import Base
from app.roadmaps.models import Roadmap


def _ensure_database_exists() -> None:
    url = make_url(settings.test_database_url)
    maintenance_dsn = (
        f"host={url.host} port={url.port} user={url.username} "
        f"password={url.password} dbname=postgres"
    )
    try:
        with psycopg.connect(maintenance_dsn, autocommit=True) as connection:
            exists = connection.execute(
                "SELECT 1 FROM pg_database WHERE datname = %s",
                (url.database,),
            ).fetchone()
            if exists is None:
                connection.execute(f'CREATE DATABASE "{url.database}"')
    except psycopg.OperationalError as error:
        raise pytest.UsageError(
            "No se pudo conectar a PostgreSQL para los tests de integración. "
            "Ejecutá `docker compose up -d postgres` y revisá TEST_DATABASE_URL."
        ) from error


@pytest.fixture(scope="session")
def test_engine() -> Iterator[Engine]:
    _ensure_database_exists()
    engine = create_engine(settings.test_database_url, pool_pre_ping=True)
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture(autouse=True)
def clean_database(test_engine: Engine) -> Iterator[None]:
    with test_engine.begin() as connection:
        connection.execute(
            text("TRUNCATE TABLE roadmaps, courses, users RESTART IDENTITY CASCADE")
        )
    yield


@pytest.fixture
def db_session(test_engine: Engine) -> Iterator[Session]:
    factory = sessionmaker(
        bind=test_engine,
        autoflush=False,
        autocommit=False,
        expire_on_commit=False,
    )
    with factory() as session:
        yield session


@pytest.fixture
def client(test_engine: Engine) -> Iterator[TestClient]:
    from app.db.session import get_db
    from app.main import app

    factory = sessionmaker(
        bind=test_engine,
        autoflush=False,
        autocommit=False,
        expire_on_commit=False,
    )

    def override_get_db() -> Iterator[Session]:
        with factory() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def user_factory(
    db_session: Session,
) -> Callable[..., User]:
    sequence = count(1)

    def create_user(
        *,
        role: str = "user",
        email: str | None = None,
        name: str | None = None,
        password_hash: str = "hash",
    ) -> User:
        index = next(sequence)
        user = User(
            name=name or f"User {index}",
            email=email or f"user{index}@example.com",
            password_hash=password_hash,
            role=role,
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        return user

    return create_user
