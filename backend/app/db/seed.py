from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.auth.repository import UserRepository
from app.auth.security import hash_password
from app.courses.repository import CourseRepository
from app.courses.rules import CourseStatus
from app.db.session import SessionLocal


@dataclass(frozen=True)
class SeedUser:
    key: str
    name: str
    email: str
    password: str
    role: str = "user"


@dataclass(frozen=True)
class SeedCourse:
    author: str
    status: CourseStatus
    title: str
    version: str
    year: int
    category: str
    theme: str
    url: str
    instructor: str
    has_quiz: bool = False
    requires_exam: bool = False
    extends_certificate: bool = False
    organization: str | None = None


SEED_USERS = (
    SeedUser(
        key="admin",
        name="Admin de Prueba",
        email="admin@roadmap.local",
        password="Admin123!",
        role="admin",
    ),
    SeedUser(
        key="instructor",
        name="Docente de Prueba",
        email="instructor@roadmap.local",
        password="Instructor123!",
        role="instructor",
    ),
    SeedUser(
        key="user",
        name="Usuario de Prueba",
        email="user@roadmap.local",
        password="User123!",
    ),
)

SEED_COURSES = (
    SeedCourse(
        author="instructor",
        status=CourseStatus.PUBLISHED,
        title="Python desde cero",
        version="2026.1",
        year=2025,
        category="Programación",
        theme="Python",
        url="https://example.com/cursos/python-desde-cero",
        instructor="Ada Lovelace",
        has_quiz=True,
        extends_certificate=True,
        organization="OpenLearn",
    ),
    SeedCourse(
        author="instructor",
        status=CourseStatus.PUBLISHED,
        title="Diseño de interfaces",
        version="2025.2",
        year=2024,
        category="Diseño",
        theme="UI/UX",
        url="https://example.com/cursos/diseno-de-interfaces",
        instructor="Grace Hopper",
        has_quiz=True,
        organization="Design School",
    ),
    SeedCourse(
        author="instructor",
        status=CourseStatus.PUBLISHED,
        title="Marketing digital",
        version="2025.1",
        year=2025,
        category="Marketing",
        theme="SEO",
        url="https://example.com/cursos/marketing-digital",
        instructor="Philip Kotler",
        requires_exam=True,
        organization="Marketing Academy",
    ),
    SeedCourse(
        author="instructor",
        status=CourseStatus.PUBLISHED,
        title="Finanzas para principiantes",
        version="2024.3",
        year=2024,
        category="Negocios",
        theme="Finanzas",
        url="https://example.com/cursos/finanzas-para-principiantes",
        instructor="Warren Buffett",
        has_quiz=True,
        extends_certificate=True,
    ),
    SeedCourse(
        author="instructor",
        status=CourseStatus.PUBLISHED,
        title="Historia del arte",
        version="2023.1",
        year=2023,
        category="Artes",
        theme="Historia",
        url="https://example.com/cursos/historia-del-arte",
        instructor="Frida Kahlo",
    ),
    SeedCourse(
        author="instructor",
        status=CourseStatus.PUBLISHED,
        title="Astronomía básica",
        version="2025.4",
        year=2025,
        category="Ciencias",
        theme="Astronomía",
        url="https://example.com/cursos/astronomia-basica",
        instructor="Carl Sagan",
        has_quiz=True,
        organization="Observatorio Abierto",
    ),
    SeedCourse(
        author="user",
        status=CourseStatus.IN_REVIEW,
        title="Introducción a Rust",
        version="2026.1",
        year=2026,
        category="Programación",
        theme="Rust",
        url="https://example.com/cursos/introduccion-a-rust",
        instructor="Graydon Hoare",
    ),
)


def seed_data(session: Session | None = None) -> None:
    owns_session = session is None
    db = session or SessionLocal()

    try:
        user_repository = UserRepository(db)
        users = {}
        for spec in SEED_USERS:
            user = user_repository.get_by_email(spec.email)
            if user is None:
                user = user_repository.create(
                    name=spec.name,
                    email=spec.email,
                    password_hash=hash_password(spec.password),
                    role=spec.role,
                )
            users[spec.key] = user

        course_repository = CourseRepository(db)
        for spec in SEED_COURSES:
            if course_repository.url_exists(spec.url):
                continue
            course_repository.create(
                {
                    "title": spec.title,
                    "version": spec.version,
                    "year": spec.year,
                    "category": spec.category,
                    "theme": spec.theme,
                    "url": spec.url,
                    "instructor": spec.instructor,
                    "has_quiz": spec.has_quiz,
                    "requires_exam": spec.requires_exam,
                    "extends_certificate": spec.extends_certificate,
                    "organization": spec.organization,
                },
                user_id=users[spec.author].id,
                status=spec.status,
            )
    finally:
        if owns_session:
            db.close()
