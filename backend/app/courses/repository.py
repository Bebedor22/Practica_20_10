from typing import Any, Mapping

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.courses.models import Course
from app.courses.rules import CourseStatus, normalize_url


class CourseRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def create(
        self,
        data: Mapping[str, Any],
        *,
        user_id: int,
        status: CourseStatus | str = CourseStatus.IN_REVIEW,
    ) -> Course:
        payload = dict(data)
        course = Course(
            **payload,
            user_id=user_id,
            status=status.value if isinstance(status, CourseStatus) else status,
        )
        self.session.add(course)
        self.session.commit()
        self.session.refresh(course)
        return course

    def get_by_id(self, course_id: int) -> Course | None:
        return self.session.get(Course, course_id)

    def list(
        self,
        *,
        page: int = 1,
        limit: int = 20,
        q: str | None = None,
        category: str | None = None,
        status: CourseStatus | str | None = CourseStatus.PUBLISHED,
    ) -> tuple[list[Course], int]:
        filters = []

        if status is not None:
            filters.append(
                Course.status
                == (status.value if isinstance(status, CourseStatus) else status)
            )
        if category:
            filters.append(Course.category == category)
        if q and q.strip():
            pattern = f"%{q.strip()}%"
            filters.append(
                or_(
                    Course.title.ilike(pattern),
                    Course.theme.ilike(pattern),
                    Course.instructor.ilike(pattern),
                )
            )

        total = self.session.scalar(
            select(func.count()).select_from(Course).where(*filters)
        ) or 0
        statement = (
            select(Course)
            .where(*filters)
            .order_by(Course.id)
            .offset((page - 1) * limit)
            .limit(limit)
        )
        return list(self.session.scalars(statement)), total

    def update(
        self, course_id: int, data: Mapping[str, Any]
    ) -> Course | None:
        course = self.get_by_id(course_id)
        if course is None:
            return None

        for field, value in data.items():
            setattr(course, field, value)
        self.session.commit()
        self.session.refresh(course)
        return course

    def delete(self, course_id: int) -> bool:
        course = self.get_by_id(course_id)
        if course is None:
            return False

        self.session.delete(course)
        self.session.commit()
        return True

    def url_exists(self, url: str) -> bool:
        normalized = normalize_url(url)
        statement = (
            select(Course.id)
            .where(func.rtrim(func.lower(Course.url), "/") == normalized)
            .limit(1)
        )
        return self.session.scalar(statement) is not None

    def all_urls(self) -> list[str]:
        return list(self.session.scalars(select(Course.url)))
