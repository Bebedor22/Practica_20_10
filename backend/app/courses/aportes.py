from dataclasses import dataclass
from enum import StrEnum
from typing import Iterable

from app.courses.rules import (
    CourseStatus,
    CourseSubmission,
    ReviewAction,
    RuleViolation,
    transition,
    validate_course_submission,
)


class UserRole(StrEnum):
    USER = "user"
    INSTRUCTOR = "instructor"
    ADMIN = "admin"


VALIDATOR_ROLES = frozenset({UserRole.INSTRUCTOR, UserRole.ADMIN})


class AporteRuleError(ValueError):
    def __init__(self, code: str, message: str) -> None:
        self.code = code
        super().__init__(message)


@dataclass(frozen=True)
class Actor:
    id: int
    role: UserRole | str


@dataclass(frozen=True)
class CourseReview:
    id: int
    user_id: int
    status: CourseStatus | str


def _actor_role(actor: Actor) -> UserRole:
    if isinstance(actor.role, UserRole):
        return actor.role
    try:
        return UserRole(actor.role)
    except ValueError as error:
        raise AporteRuleError(
            "ROLE_NOT_ALLOWED",
            "El usuario no tiene un rol válido para validar aportes",
        ) from error


def _course_status(course: CourseReview) -> CourseStatus:
    if isinstance(course.status, CourseStatus):
        return course.status
    try:
        return CourseStatus(course.status)
    except ValueError as error:
        raise AporteRuleError(
            "COURSE_NOT_IN_REVIEW",
            "Solo se pueden validar cursos en revisión",
        ) from error


def validate_aporte(
    submission: CourseSubmission,
    *,
    existing_urls: Iterable[str] = (),
    current_year: int | None = None,
) -> list[RuleViolation]:
    return validate_course_submission(
        submission,
        existing_urls=existing_urls,
        current_year=current_year,
    )


def ensure_can_validate(actor: Actor, course: CourseReview) -> None:
    if _actor_role(actor) not in VALIDATOR_ROLES:
        raise AporteRuleError(
            "ROLE_NOT_ALLOWED",
            "Solo administradores e instructores pueden validar aportes",
        )

    if actor.id == course.user_id:
        raise AporteRuleError(
            "SELF_VALIDATION_FORBIDDEN",
            "El autor no puede validar su propio aporte",
        )

    if _course_status(course) is not CourseStatus.IN_REVIEW:
        raise AporteRuleError(
            "COURSE_NOT_IN_REVIEW",
            "Solo se pueden validar cursos en revisión",
        )


def can_validate(actor: Actor, course: CourseReview) -> bool:
    try:
        ensure_can_validate(actor, course)
    except AporteRuleError:
        return False
    return True


def resolve_validation(
    actor: Actor, course: CourseReview, *, approved: bool
) -> CourseStatus:
    ensure_can_validate(actor, course)
    current_status = _course_status(course)
    action = ReviewAction.APPROVE if approved else ReviewAction.REJECT
    return transition(current_status, action)
