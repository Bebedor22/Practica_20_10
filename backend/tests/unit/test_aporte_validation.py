import pytest

from app.courses.aportes import (
    Actor,
    AporteRuleError,
    CourseReview,
    UserRole,
    can_validate,
    ensure_can_validate,
    resolve_validation,
    validate_aporte,
)
from app.courses.rules import CourseStatus, CourseSubmission

CURRENT_YEAR = 2026


def make_submission(**overrides: object) -> CourseSubmission:
    values = {
        "title": "Curso de Python",
        "version": "2026.1",
        "year": 2025,
        "category": "Programación",
        "theme": "Python",
        "url": "https://example.com/curso-python",
        "instructor": "Ada Lovelace",
        "organization": "Universidad Ejemplo",
    }
    values.update(overrides)
    return CourseSubmission(**values)


def make_course(
    *, user_id: int = 10, status: CourseStatus | str = CourseStatus.IN_REVIEW
) -> CourseReview:
    return CourseReview(id=1, user_id=user_id, status=status)


def make_actor(
    *, actor_id: int = 1, role: UserRole | str = UserRole.ADMIN
) -> Actor:
    return Actor(id=actor_id, role=role)


def test_validate_aporte_valid_submission_returns_no_violations() -> None:
    # Arrange
    submission = make_submission()

    # Act
    violations = validate_aporte(submission, current_year=CURRENT_YEAR)

    # Assert
    assert violations == []


def test_validate_aporte_invalid_submission_returns_rule_codes() -> None:
    # Arrange
    submission = make_submission(title="", url="ftp://example.com/curso")

    # Act
    violations = validate_aporte(submission, current_year=CURRENT_YEAR)

    # Assert
    assert [violation.code for violation in violations] == [
        "TITLE_REQUIRED",
        "URL_INVALID",
    ]


def test_can_validate_admin_on_in_review_course_returns_true() -> None:
    # Arrange
    actor = make_actor(role=UserRole.ADMIN)
    course = make_course(status=CourseStatus.IN_REVIEW)

    # Act
    result = can_validate(actor, course)

    # Assert
    assert result is True


def test_can_validate_instructor_on_in_review_course_returns_true() -> None:
    # Arrange
    actor = make_actor(role=UserRole.INSTRUCTOR)
    course = make_course(status=CourseStatus.IN_REVIEW)

    # Act
    result = can_validate(actor, course)

    # Assert
    assert result is True


def test_can_validate_user_role_returns_false() -> None:
    # Arrange
    actor = make_actor(role=UserRole.USER)
    course = make_course()

    # Act
    result = can_validate(actor, course)

    # Assert
    assert result is False


def test_ensure_can_validate_user_role_raises_role_not_allowed() -> None:
    # Arrange
    actor = make_actor(role=UserRole.USER)
    course = make_course()

    # Act / Assert
    with pytest.raises(AporteRuleError) as error:
        ensure_can_validate(actor, course)

    assert error.value.code == "ROLE_NOT_ALLOWED"


def test_ensure_can_validate_unknown_role_raises_role_not_allowed() -> None:
    # Arrange
    actor = make_actor(role="superuser")
    course = make_course()

    # Act / Assert
    with pytest.raises(AporteRuleError) as error:
        ensure_can_validate(actor, course)

    assert error.value.code == "ROLE_NOT_ALLOWED"


def test_ensure_can_validate_author_raises_self_validation_forbidden() -> None:
    # Arrange
    actor = make_actor(actor_id=10, role=UserRole.ADMIN)
    course = make_course(user_id=10)

    # Act / Assert
    with pytest.raises(AporteRuleError) as error:
        ensure_can_validate(actor, course)

    assert error.value.code == "SELF_VALIDATION_FORBIDDEN"


@pytest.mark.parametrize(
    "status",
    [
        CourseStatus.DRAFT,
        CourseStatus.REJECTED,
        CourseStatus.PUBLISHED,
        "draft",
        "rejected",
        "published",
    ],
)
def test_ensure_can_validate_course_not_in_review_raises_course_not_in_review(
    status: CourseStatus | str,
) -> None:
    # Arrange
    actor = make_actor(role=UserRole.ADMIN)
    course = make_course(status=status)

    # Act / Assert
    with pytest.raises(AporteRuleError) as error:
        ensure_can_validate(actor, course)

    assert error.value.code == "COURSE_NOT_IN_REVIEW"


def test_resolve_validation_approved_returns_published() -> None:
    # Arrange
    actor = make_actor(role=UserRole.ADMIN)
    course = make_course(status=CourseStatus.IN_REVIEW)

    # Act
    status = resolve_validation(actor, course, approved=True)

    # Assert
    assert status is CourseStatus.PUBLISHED


def test_resolve_validation_rejected_returns_rejected() -> None:
    # Arrange
    actor = make_actor(role=UserRole.INSTRUCTOR)
    course = make_course(status=CourseStatus.IN_REVIEW)

    # Act
    status = resolve_validation(actor, course, approved=False)

    # Assert
    assert status is CourseStatus.REJECTED


def test_resolve_validation_user_role_raises_role_not_allowed() -> None:
    # Arrange
    actor = make_actor(role=UserRole.USER)
    course = make_course()

    # Act / Assert
    with pytest.raises(AporteRuleError) as error:
        resolve_validation(actor, course, approved=True)

    assert error.value.code == "ROLE_NOT_ALLOWED"


def test_resolve_validation_author_raises_self_validation_forbidden() -> None:
    # Arrange
    actor = make_actor(actor_id=10, role=UserRole.ADMIN)
    course = make_course(user_id=10)

    # Act / Assert
    with pytest.raises(AporteRuleError) as error:
        resolve_validation(actor, course, approved=True)

    assert error.value.code == "SELF_VALIDATION_FORBIDDEN"
