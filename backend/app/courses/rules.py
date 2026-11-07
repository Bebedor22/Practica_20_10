from dataclasses import dataclass
from datetime import date
from enum import StrEnum
from typing import Iterable
from urllib.parse import urlparse

CATEGORIES = (
    "Programación",
    "Diseño",
    "Marketing",
    "Negocios",
    "Artes",
    "Ciencias",
    "Otros",
)

MIN_YEAR = 2000
MAX_TITLE_LENGTH = 200
MIN_TITLE_LENGTH = 3
MAX_VERSION_LENGTH = 50
MAX_THEME_LENGTH = 100
MIN_THEME_LENGTH = 2
MAX_URL_LENGTH = 500
MAX_INSTRUCTOR_LENGTH = 200
MIN_INSTRUCTOR_LENGTH = 2
MAX_ORGANIZATION_LENGTH = 200


class CourseStatus(StrEnum):
    DRAFT = "draft"
    IN_REVIEW = "in_review"
    PUBLISHED = "published"
    REJECTED = "rejected"


class ReviewAction(StrEnum):
    SUBMIT = "submit"
    APPROVE = "approve"
    REJECT = "reject"
    REOPEN = "reopen"


TRANSITIONS: dict[CourseStatus, dict[ReviewAction, CourseStatus]] = {
    CourseStatus.DRAFT: {ReviewAction.SUBMIT: CourseStatus.IN_REVIEW},
    CourseStatus.IN_REVIEW: {
        ReviewAction.APPROVE: CourseStatus.PUBLISHED,
        ReviewAction.REJECT: CourseStatus.REJECTED,
    },
    CourseStatus.REJECTED: {ReviewAction.REOPEN: CourseStatus.DRAFT},
    CourseStatus.PUBLISHED: {},
}


class InvalidTransitionError(ValueError):
    code = "INVALID_STATUS_TRANSITION"

    def __init__(self, current: CourseStatus, action: ReviewAction) -> None:
        self.current = current
        self.action = action
        super().__init__(
            f"Transición inválida: no se puede aplicar '{action}' a '{current}'"
        )


@dataclass(frozen=True)
class RuleViolation:
    field: str
    code: str
    message: str


@dataclass(frozen=True)
class CourseSubmission:
    title: str | None = None
    version: str | None = None
    year: int | None = None
    category: str | None = None
    theme: str | None = None
    url: str | None = None
    instructor: str | None = None
    has_quiz: bool = False
    requires_exam: bool = False
    extends_certificate: bool = False
    organization: str | None = None


def normalize_url(url: str) -> str:
    return url.strip().lower().rstrip("/")


def _is_valid_url(url: str) -> bool:
    if " " in url:
        return False
    parsed = urlparse(url)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def can_transition(current: CourseStatus, action: ReviewAction) -> bool:
    return action in TRANSITIONS.get(current, {})


def transition(current: CourseStatus, action: ReviewAction) -> CourseStatus:
    if not can_transition(current, action):
        raise InvalidTransitionError(current, action)
    return TRANSITIONS[current][action]


def validate_course_submission(
    submission: CourseSubmission,
    *,
    existing_urls: Iterable[str] = (),
    current_year: int | None = None,
) -> list[RuleViolation]:
    violations: list[RuleViolation] = []
    max_year = current_year if current_year is not None else date.today().year

    title = (submission.title or "").strip()
    if not title:
        violations.append(
            RuleViolation("title", "TITLE_REQUIRED", "El título es obligatorio")
        )
    elif len(title) < MIN_TITLE_LENGTH:
        violations.append(
            RuleViolation(
                "title",
                "TITLE_TOO_SHORT",
                f"El título debe tener al menos {MIN_TITLE_LENGTH} caracteres",
            )
        )
    elif len(title) > MAX_TITLE_LENGTH:
        violations.append(
            RuleViolation(
                "title",
                "TITLE_TOO_LONG",
                f"El título no puede superar {MAX_TITLE_LENGTH} caracteres",
            )
        )

    version = (submission.version or "").strip()
    if not version:
        violations.append(
            RuleViolation("version", "VERSION_REQUIRED", "La versión es obligatoria")
        )
    elif len(version) > MAX_VERSION_LENGTH:
        violations.append(
            RuleViolation(
                "version",
                "VERSION_TOO_LONG",
                f"La versión no puede superar {MAX_VERSION_LENGTH} caracteres",
            )
        )

    if submission.year is None:
        violations.append(
            RuleViolation("year", "YEAR_REQUIRED", "El año es obligatorio")
        )
    elif submission.year < MIN_YEAR:
        violations.append(
            RuleViolation(
                "year",
                "YEAR_BEFORE_2000",
                f"El año debe ser mayor o igual a {MIN_YEAR}",
            )
        )
    elif submission.year > max_year:
        violations.append(
            RuleViolation(
                "year",
                "YEAR_IN_FUTURE",
                f"El año no puede ser mayor a {max_year}",
            )
        )

    category = (submission.category or "").strip()
    if not category:
        violations.append(
            RuleViolation("category", "CATEGORY_REQUIRED", "La categoría es obligatoria")
        )
    elif category not in CATEGORIES:
        violations.append(
            RuleViolation(
                "category",
                "CATEGORY_INVALID",
                f"La categoría debe ser una de: {', '.join(CATEGORIES)}",
            )
        )

    theme = (submission.theme or "").strip()
    if not theme:
        violations.append(
            RuleViolation("theme", "THEME_REQUIRED", "El tema es obligatorio")
        )
    elif len(theme) < MIN_THEME_LENGTH:
        violations.append(
            RuleViolation(
                "theme",
                "THEME_TOO_SHORT",
                f"El tema debe tener al menos {MIN_THEME_LENGTH} caracteres",
            )
        )
    elif len(theme) > MAX_THEME_LENGTH:
        violations.append(
            RuleViolation(
                "theme",
                "THEME_TOO_LONG",
                f"El tema no puede superar {MAX_THEME_LENGTH} caracteres",
            )
        )

    url = (submission.url or "").strip()
    normalized_existing = {normalize_url(item) for item in existing_urls}
    if not url:
        violations.append(RuleViolation("url", "URL_REQUIRED", "La URL es obligatoria"))
    elif len(url) > MAX_URL_LENGTH:
        violations.append(
            RuleViolation(
                "url",
                "URL_TOO_LONG",
                f"La URL no puede superar {MAX_URL_LENGTH} caracteres",
            )
        )
    elif not _is_valid_url(url):
        violations.append(
            RuleViolation(
                "url",
                "URL_INVALID",
                "La URL debe ser válida y comenzar con http:// o https://",
            )
        )
    elif normalize_url(url) in normalized_existing:
        violations.append(
            RuleViolation("url", "URL_DUPLICATE", "Ya existe un curso con esa URL")
        )

    instructor = (submission.instructor or "").strip()
    if not instructor:
        violations.append(
            RuleViolation(
                "instructor", "INSTRUCTOR_REQUIRED", "El docente es obligatorio"
            )
        )
    elif len(instructor) < MIN_INSTRUCTOR_LENGTH:
        violations.append(
            RuleViolation(
                "instructor",
                "INSTRUCTOR_TOO_SHORT",
                f"El docente debe tener al menos {MIN_INSTRUCTOR_LENGTH} caracteres",
            )
        )
    elif len(instructor) > MAX_INSTRUCTOR_LENGTH:
        violations.append(
            RuleViolation(
                "instructor",
                "INSTRUCTOR_TOO_LONG",
                f"El docente no puede superar {MAX_INSTRUCTOR_LENGTH} caracteres",
            )
        )

    organization = (submission.organization or "").strip()
    if len(organization) > MAX_ORGANIZATION_LENGTH:
        violations.append(
            RuleViolation(
                "organization",
                "ORGANIZATION_TOO_LONG",
                f"La organización no puede superar {MAX_ORGANIZATION_LENGTH} caracteres",
            )
        )

    return violations
