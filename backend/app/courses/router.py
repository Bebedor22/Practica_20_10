from fastapi import APIRouter, Query

from app.courses.schemas import CourseRead
from app.shared.pagination import Page

router = APIRouter(prefix="/courses", tags=["courses"])


@router.get("", response_model=Page[CourseRead])
def list_courses(
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=50),
) -> Page[CourseRead]:
    return Page.create(items=[], total=0, page=page, limit=limit)
