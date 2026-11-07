from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.auth.models import User
from app.courses.aportes import (
    Actor,
    AporteRuleError,
    CourseReview,
    resolve_validation,
    validate_aporte,
)
from app.courses.repository import CourseRepository
from app.courses.rules import (
    CourseStatus,
    CourseSubmission,
    RuleViolation,
)
from app.courses.schemas import CourseCreate, CourseRead, CourseValidateRequest
from app.db.session import get_db
from app.shared.pagination import Page

router = APIRouter(prefix="/courses", tags=["courses"])

FORBIDDEN_CODES = frozenset(
    {"ROLE_NOT_ALLOWED", "SELF_VALIDATION_FORBIDDEN"}
)


def _validation_detail(violations: list[RuleViolation]) -> dict[str, object]:
    return {
        "error": "validation failed",
        "details": [
            {
                "field": violation.field,
                "code": violation.code,
                "message": violation.message,
            }
            for violation in violations
        ],
    }


def _raise_validation_error(violations: list[RuleViolation]) -> None:
    raise HTTPException(
        status_code=422,
        detail=_validation_detail(violations),
    )


def _raise_aporte_error(error: AporteRuleError) -> None:
    if error.code in FORBIDDEN_CODES:
        raise HTTPException(
            status_code=403,
            detail={"error": "forbidden", "code": error.code},
        ) from error
    raise HTTPException(
        status_code=400,
        detail={"error": "validation failed", "code": error.code},
    ) from error


@router.get("", response_model=Page[CourseRead])
def list_courses(
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=50),
    q: str | None = Query(default=None, max_length=100),
    category: str | None = Query(default=None),
    db: Session = Depends(get_db),
) -> Page[CourseRead]:
    items, total = CourseRepository(db).list(
        page=page,
        limit=limit,
        q=q,
        category=category,
        status=CourseStatus.PUBLISHED,
    )
    return Page.create(
        items=[CourseRead.model_validate(course) for course in items],
        total=total,
        page=page,
        limit=limit,
    )


@router.get("/{course_id}", response_model=CourseRead)
def get_course(course_id: int, db: Session = Depends(get_db)) -> CourseRead:
    course = CourseRepository(db).get_by_id(course_id)
    if course is None or course.status != CourseStatus.PUBLISHED.value:
        raise HTTPException(
            status_code=404,
            detail={"error": "not found", "code": "COURSE_NOT_FOUND"},
        )
    return CourseRead.model_validate(course)


@router.post("", response_model=CourseRead, status_code=201)
def create_course(
    payload: CourseCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> CourseRead:
    repository = CourseRepository(db)
    submission = CourseSubmission(**payload.model_dump())
    violations = validate_aporte(
        submission,
        existing_urls=repository.all_urls(),
    )
    if violations:
        _raise_validation_error(violations)

    try:
        course = repository.create(
            payload.model_dump(),
            user_id=current_user.id,
            status=CourseStatus.IN_REVIEW,
        )
    except IntegrityError as error:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail={"error": "course already exists", "code": "URL_DUPLICATE"},
        ) from error
    return CourseRead.model_validate(course)


@router.put("/{course_id}/validate", response_model=CourseRead)
def validate_course(
    course_id: int,
    payload: CourseValidateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> CourseRead:
    repository = CourseRepository(db)
    course = repository.get_by_id(course_id)
    if course is None:
        raise HTTPException(
            status_code=404,
            detail={"error": "not found", "code": "COURSE_NOT_FOUND"},
        )

    try:
        new_status = resolve_validation(
            Actor(id=current_user.id, role=current_user.role),
            CourseReview(
                id=course.id,
                user_id=course.user_id,
                status=course.status,
            ),
            approved=payload.approved,
        )
    except AporteRuleError as error:
        _raise_aporte_error(error)

    updated = repository.update(course.id, {"status": new_status.value})
    if updated is None:
        raise HTTPException(
            status_code=404,
            detail={"error": "not found", "code": "COURSE_NOT_FOUND"},
        )
    return CourseRead.model_validate(updated)
