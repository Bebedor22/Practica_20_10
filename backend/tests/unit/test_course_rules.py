from dataclasses import replace

import pytest

from app.courses.rules import (
    CourseStatus,
    CourseSubmission,
    InvalidTransitionError,
    ReviewAction,
    can_transition,
    transition,
    validate_course_submission,
)

CURRENT_YEAR = 2026


def make_submission(**overrides: object) -> CourseSubmission:
    base = CourseSubmission(
        title="Curso de Python",
        version="2026.1",
        year=2025,
        category="Programación",
        theme="Python",
        url="https://example.com/curso-python",
        instructor="Ada Lovelace",
        has_quiz=True,
        requires_exam=False,
        extends_certificate=True,
        organization="Universidad Ejemplo",
    )
    return replace(base, **overrides)


def test_validate_course_submission_valid_payload_returns_no_violations() -> None:
    # Arrange
    submission = make_submission()

    # Act
    violations = validate_course_submission(submission, current_year=CURRENT_YEAR)

    # Assert
    assert violations == []


def test_validate_course_submission_missing_title_returns_title_required() -> None:
    # Arrange
    submission = make_submission(title=None)

    # Act
    violations = validate_course_submission(submission, current_year=CURRENT_YEAR)

    # Assert
    assert [violation.code for violation in violations] == ["TITLE_REQUIRED"]


def test_validate_course_submission_short_title_returns_title_too_short() -> None:
    # Arrange
    submission = make_submission(title="ab")

    # Act
    violations = validate_course_submission(submission, current_year=CURRENT_YEAR)

    # Assert
    assert [violation.code for violation in violations] == ["TITLE_TOO_SHORT"]


def test_validate_course_submission_long_title_returns_title_too_long() -> None:
    # Arrange
    submission = make_submission(title="x" * 201)

    # Act
    violations = validate_course_submission(submission, current_year=CURRENT_YEAR)

    # Assert
    assert [violation.code for violation in violations] == ["TITLE_TOO_LONG"]


def test_validate_course_submission_missing_version_returns_version_required() -> None:
    # Arrange
    submission = make_submission(version=None)

    # Act
    violations = validate_course_submission(submission, current_year=CURRENT_YEAR)

    # Assert
    assert [violation.code for violation in violations] == ["VERSION_REQUIRED"]


def test_validate_course_submission_long_version_returns_version_too_long() -> None:
    # Arrange
    submission = make_submission(version="v" * 51)

    # Act
    violations = validate_course_submission(submission, current_year=CURRENT_YEAR)

    # Assert
    assert [violation.code for violation in violations] == ["VERSION_TOO_LONG"]


def test_validate_course_submission_missing_year_returns_year_required() -> None:
    # Arrange
    submission = make_submission(year=None)

    # Act
    violations = validate_course_submission(submission, current_year=CURRENT_YEAR)

    # Assert
    assert [violation.code for violation in violations] == ["YEAR_REQUIRED"]


def test_validate_course_submission_year_before_2000_returns_year_before_2000() -> None:
    # Arrange
    submission = make_submission(year=1999)

    # Act
    violations = validate_course_submission(submission, current_year=CURRENT_YEAR)

    # Assert
    assert [violation.code for violation in violations] == ["YEAR_BEFORE_2000"]


def test_validate_course_submission_future_year_returns_year_in_future() -> None:
    # Arrange
    submission = make_submission(year=CURRENT_YEAR + 1)

    # Act
    violations = validate_course_submission(submission, current_year=CURRENT_YEAR)

    # Assert
    assert [violation.code for violation in violations] == ["YEAR_IN_FUTURE"]


@pytest.mark.parametrize("year", [2000, CURRENT_YEAR])
def test_validate_course_submission_boundary_years_are_valid(year: int) -> None:
    # Arrange
    submission = make_submission(year=year)

    # Act
    violations = validate_course_submission(submission, current_year=CURRENT_YEAR)

    # Assert
    assert violations == []


def test_validate_course_submission_missing_category_returns_category_required() -> None:
    # Arrange
    submission = make_submission(category=None)

    # Act
    violations = validate_course_submission(submission, current_year=CURRENT_YEAR)

    # Assert
    assert [violation.code for violation in violations] == ["CATEGORY_REQUIRED"]


def test_validate_course_submission_unknown_category_returns_category_invalid() -> None:
    # Arrange
    submission = make_submission(category="Idiomas")

    # Act
    violations = validate_course_submission(submission, current_year=CURRENT_YEAR)

    # Assert
    assert [violation.code for violation in violations] == ["CATEGORY_INVALID"]


def test_validate_course_submission_missing_theme_returns_theme_required() -> None:
    # Arrange
    submission = make_submission(theme=None)

    # Act
    violations = validate_course_submission(submission, current_year=CURRENT_YEAR)

    # Assert
    assert [violation.code for violation in violations] == ["THEME_REQUIRED"]


def test_validate_course_submission_short_theme_returns_theme_too_short() -> None:
    # Arrange
    submission = make_submission(theme="x")

    # Act
    violations = validate_course_submission(submission, current_year=CURRENT_YEAR)

    # Assert
    assert [violation.code for violation in violations] == ["THEME_TOO_SHORT"]


def test_validate_course_submission_long_theme_returns_theme_too_long() -> None:
    # Arrange
    submission = make_submission(theme="x" * 101)

    # Act
    violations = validate_course_submission(submission, current_year=CURRENT_YEAR)

    # Assert
    assert [violation.code for violation in violations] == ["THEME_TOO_LONG"]


def test_validate_course_submission_missing_url_returns_url_required() -> None:
    # Arrange
    submission = make_submission(url=None)

    # Act
    violations = validate_course_submission(submission, current_year=CURRENT_YEAR)

    # Assert
    assert [violation.code for violation in violations] == ["URL_REQUIRED"]


@pytest.mark.parametrize(
    "url",
    ["no-es-una-url", "ftp://example.com/curso", "https://", "https://example.com/a b"],
)
def test_validate_course_submission_invalid_url_returns_url_invalid(url: str) -> None:
    # Arrange
    submission = make_submission(url=url)

    # Act
    violations = validate_course_submission(submission, current_year=CURRENT_YEAR)

    # Assert
    assert [violation.code for violation in violations] == ["URL_INVALID"]


def test_validate_course_submission_long_url_returns_url_too_long() -> None:
    # Arrange
    submission = make_submission(url=f"https://example.com/{'x' * 500}")

    # Act
    violations = validate_course_submission(submission, current_year=CURRENT_YEAR)

    # Assert
    assert [violation.code for violation in violations] == ["URL_TOO_LONG"]


def test_validate_course_submission_duplicate_url_returns_url_duplicate() -> None:
    # Arrange
    submission = make_submission(url="https://example.com/curso-python")

    # Act
    violations = validate_course_submission(
        submission,
        existing_urls=["https://example.com/curso-python"],
        current_year=CURRENT_YEAR,
    )

    # Assert
    assert [violation.code for violation in violations] == ["URL_DUPLICATE"]


def test_validate_course_submission_duplicate_url_ignores_case_and_trailing_slash() -> (
    None
):
    # Arrange
    submission = make_submission(url="https://Example.com/Curso-Python/")

    # Act
    violations = validate_course_submission(
        submission,
        existing_urls=["https://example.com/curso-python"],
        current_year=CURRENT_YEAR,
    )

    # Assert
    assert [violation.code for violation in violations] == ["URL_DUPLICATE"]


def test_validate_course_submission_different_url_returns_no_violations() -> None:
    # Arrange
    submission = make_submission(url="https://example.com/otro-curso")

    # Act
    violations = validate_course_submission(
        submission,
        existing_urls=["https://example.com/curso-python"],
        current_year=CURRENT_YEAR,
    )

    # Assert
    assert violations == []


def test_validate_course_submission_missing_instructor_returns_instructor_required() -> (
    None
):
    # Arrange
    submission = make_submission(instructor=None)

    # Act
    violations = validate_course_submission(submission, current_year=CURRENT_YEAR)

    # Assert
    assert [violation.code for violation in violations] == ["INSTRUCTOR_REQUIRED"]


def test_validate_course_submission_short_instructor_returns_instructor_too_short() -> (
    None
):
    # Arrange
    submission = make_submission(instructor="A")

    # Act
    violations = validate_course_submission(submission, current_year=CURRENT_YEAR)

    # Assert
    assert [violation.code for violation in violations] == ["INSTRUCTOR_TOO_SHORT"]


def test_validate_course_submission_long_instructor_returns_instructor_too_long() -> (
    None
):
    # Arrange
    submission = make_submission(instructor="x" * 201)

    # Act
    violations = validate_course_submission(submission, current_year=CURRENT_YEAR)

    # Assert
    assert [violation.code for violation in violations] == ["INSTRUCTOR_TOO_LONG"]


def test_validate_course_submission_long_organization_returns_organization_too_long() -> (
    None
):
    # Arrange
    submission = make_submission(organization="x" * 201)

    # Act
    violations = validate_course_submission(submission, current_year=CURRENT_YEAR)

    # Assert
    assert [violation.code for violation in violations] == ["ORGANIZATION_TOO_LONG"]


def test_validate_course_submission_organization_at_limit_is_valid() -> None:
    # Arrange
    submission = make_submission(organization="x" * 200)

    # Act
    violations = validate_course_submission(submission, current_year=CURRENT_YEAR)

    # Assert
    assert violations == []


@pytest.mark.parametrize(
    ("has_quiz", "requires_exam", "extends_certificate"),
    [
        (False, False, False),
        (True, True, True),
        (True, False, True),
        (False, True, False),
    ],
)
def test_validate_course_submission_flag_combinations_are_valid(
    has_quiz: bool, requires_exam: bool, extends_certificate: bool
) -> None:
    # Arrange
    submission = make_submission(
        has_quiz=has_quiz,
        requires_exam=requires_exam,
        extends_certificate=extends_certificate,
    )

    # Act
    violations = validate_course_submission(submission, current_year=CURRENT_YEAR)

    # Assert
    assert violations == []


def test_validate_course_submission_multiple_errors_returns_all_codes() -> None:
    # Arrange
    submission = make_submission(title=None, year=1999, url="no-es-una-url")

    # Act
    violations = validate_course_submission(submission, current_year=CURRENT_YEAR)

    # Assert
    assert [violation.code for violation in violations] == [
        "TITLE_REQUIRED",
        "YEAR_BEFORE_2000",
        "URL_INVALID",
    ]


@pytest.mark.parametrize(
    ("current", "action", "expected"),
    [
        (CourseStatus.DRAFT, ReviewAction.SUBMIT, CourseStatus.IN_REVIEW),
        (CourseStatus.IN_REVIEW, ReviewAction.APPROVE, CourseStatus.PUBLISHED),
        (CourseStatus.IN_REVIEW, ReviewAction.REJECT, CourseStatus.REJECTED),
        (CourseStatus.REJECTED, ReviewAction.REOPEN, CourseStatus.DRAFT),
    ],
)
def test_transition_allowed_returns_next_status(
    current: CourseStatus, action: ReviewAction, expected: CourseStatus
) -> None:
    # Arrange
    # (parámetros de la transición)

    # Act
    result = transition(current, action)

    # Assert
    assert result == expected


@pytest.mark.parametrize(
    ("current", "action"),
    [
        (CourseStatus.PUBLISHED, ReviewAction.SUBMIT),
        (CourseStatus.PUBLISHED, ReviewAction.APPROVE),
        (CourseStatus.PUBLISHED, ReviewAction.REJECT),
        (CourseStatus.PUBLISHED, ReviewAction.REOPEN),
        (CourseStatus.DRAFT, ReviewAction.APPROVE),
        (CourseStatus.DRAFT, ReviewAction.REJECT),
        (CourseStatus.IN_REVIEW, ReviewAction.SUBMIT),
        (CourseStatus.IN_REVIEW, ReviewAction.REOPEN),
        (CourseStatus.REJECTED, ReviewAction.APPROVE),
    ],
)
def test_can_transition_disallowed_returns_false(
    current: CourseStatus, action: ReviewAction
) -> None:
    # Arrange
    # (parámetros de la transición)

    # Act
    result = can_transition(current, action)

    # Assert
    assert result is False


def test_transition_disallowed_raises_invalid_transition_error() -> None:
    # Arrange
    current = CourseStatus.PUBLISHED
    action = ReviewAction.REOPEN

    # Act / Assert
    with pytest.raises(InvalidTransitionError) as error:
        transition(current, action)

    assert error.value.code == "INVALID_STATUS_TRANSITION"
