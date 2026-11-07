from datetime import datetime

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Integer,
    SmallInteger,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.courses.rules import CATEGORIES, CourseStatus
from app.db.base import Base

ALLOWED_STATUSES = ", ".join(f"'{status.value}'" for status in CourseStatus)
ALLOWED_CATEGORIES = ", ".join(f"'{category}'" for category in CATEGORIES)


class Course(Base):
    __tablename__ = "courses"
    __table_args__ = (
        CheckConstraint("year >= 2000", name="ck_courses_year"),
        CheckConstraint(
            f"category IN ({ALLOWED_CATEGORIES})", name="ck_courses_category"
        ),
        CheckConstraint(
            f"status IN ({ALLOWED_STATUSES})", name="ck_courses_status"
        ),
        UniqueConstraint("url", name="uq_courses_url"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    version: Mapped[str] = mapped_column(String(50), nullable=False)
    year: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    category: Mapped[str] = mapped_column(String(50), nullable=False)
    theme: Mapped[str] = mapped_column(String(100), nullable=False)
    url: Mapped[str] = mapped_column(String(500), nullable=False)
    instructor: Mapped[str] = mapped_column(String(200), nullable=False)
    has_quiz: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default="false"
    )
    requires_exam: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default="false"
    )
    extends_certificate: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default="false"
    )
    organization: Mapped[str | None] = mapped_column(String(200), nullable=True)
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default=CourseStatus.IN_REVIEW.value,
        server_default=CourseStatus.IN_REVIEW.value,
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    @property
    def validated(self) -> bool:
        return self.status == CourseStatus.PUBLISHED.value
