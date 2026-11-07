from dataclasses import dataclass
from typing import Sequence

from app.courses.rules import CourseStatus


class RoadmapRuleError(ValueError):
    def __init__(self, code: str, message: str) -> None:
        self.code = code
        super().__init__(message)


@dataclass(frozen=True)
class RoadmapCourse:
    course_id: int
    position: int


@dataclass(frozen=True)
class CourseCandidate:
    course_id: int
    status: CourseStatus | str


def _reindex(courses: Sequence[RoadmapCourse]) -> list[RoadmapCourse]:
    return [
        RoadmapCourse(course_id=course.course_id, position=index)
        for index, course in enumerate(courses, start=1)
    ]


def _course_status(course: CourseCandidate) -> CourseStatus:
    if isinstance(course.status, CourseStatus):
        return course.status
    try:
        return CourseStatus(course.status)
    except ValueError as error:
        raise RoadmapRuleError(
            "COURSE_NOT_PUBLISHED",
            "Solo se pueden agregar cursos publicados al roadmap",
        ) from error


def add_course(
    current: Sequence[RoadmapCourse], course: CourseCandidate | None
) -> list[RoadmapCourse]:
    if course is None:
        raise RoadmapRuleError("COURSE_NOT_FOUND", "El curso no existe")

    if _course_status(course) is not CourseStatus.PUBLISHED:
        raise RoadmapRuleError(
            "COURSE_NOT_PUBLISHED",
            "Solo se pueden agregar cursos publicados al roadmap",
        )

    if any(item.course_id == course.course_id for item in current):
        raise RoadmapRuleError(
            "COURSE_ALREADY_IN_ROADMAP",
            "El curso ya está en el roadmap",
        )

    return _reindex([*current, RoadmapCourse(course.course_id, 0)])


def remove_course(
    current: Sequence[RoadmapCourse], course_id: int
) -> list[RoadmapCourse]:
    if not any(item.course_id == course_id for item in current):
        raise RoadmapRuleError(
            "COURSE_NOT_IN_ROADMAP",
            "El curso no está en el roadmap",
        )

    return _reindex([item for item in current if item.course_id != course_id])


def reorder_courses(
    current: Sequence[RoadmapCourse], ordered_course_ids: Sequence[int]
) -> list[RoadmapCourse]:
    current_ids = [item.course_id for item in current]
    ordered = list(ordered_course_ids)

    if (
        len(ordered) != len(current_ids)
        or len(set(ordered)) != len(ordered)
        or set(ordered) != set(current_ids)
    ):
        raise RoadmapRuleError(
            "INVALID_REORDER",
            "El nuevo orden debe incluir exactamente los cursos del roadmap",
        )

    return [
        RoadmapCourse(course_id=course_id, position=index)
        for index, course_id in enumerate(ordered, start=1)
    ]
