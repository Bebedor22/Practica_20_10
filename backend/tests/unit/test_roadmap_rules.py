import pytest

from app.courses.rules import CourseStatus
from app.roadmaps.rules import (
    CourseCandidate,
    RoadmapCourse,
    RoadmapRuleError,
    add_course,
    remove_course,
    reorder_courses,
)


def test_add_course_published_course_appends_at_end() -> None:
    # Arrange
    current = [RoadmapCourse(course_id=1, position=1)]
    course = CourseCandidate(course_id=2, status=CourseStatus.PUBLISHED)

    # Act
    result = add_course(current, course)

    # Assert
    assert result == [
        RoadmapCourse(course_id=1, position=1),
        RoadmapCourse(course_id=2, position=2),
    ]


def test_add_course_empty_roadmap_returns_position_one() -> None:
    # Arrange
    course = CourseCandidate(course_id=7, status=CourseStatus.PUBLISHED)

    # Act
    result = add_course([], course)

    # Assert
    assert result == [RoadmapCourse(course_id=7, position=1)]


def test_add_course_missing_course_raises_course_not_found() -> None:
    # Arrange
    current: list[RoadmapCourse] = []

    # Act / Assert
    with pytest.raises(RoadmapRuleError) as error:
        add_course(current, None)

    assert error.value.code == "COURSE_NOT_FOUND"


@pytest.mark.parametrize(
    "status",
    [
        CourseStatus.DRAFT,
        CourseStatus.IN_REVIEW,
        CourseStatus.REJECTED,
        "draft",
        "in_review",
        "rejected",
    ],
)
def test_add_course_unpublished_course_raises_course_not_published(
    status: CourseStatus | str,
) -> None:
    # Arrange
    course = CourseCandidate(course_id=2, status=status)

    # Act / Assert
    with pytest.raises(RoadmapRuleError) as error:
        add_course([], course)

    assert error.value.code == "COURSE_NOT_PUBLISHED"


def test_add_course_duplicate_raises_course_already_in_roadmap() -> None:
    # Arrange
    current = [RoadmapCourse(course_id=2, position=1)]
    course = CourseCandidate(course_id=2, status=CourseStatus.PUBLISHED)

    # Act / Assert
    with pytest.raises(RoadmapRuleError) as error:
        add_course(current, course)

    assert error.value.code == "COURSE_ALREADY_IN_ROADMAP"


def test_remove_course_existing_reindexes_positions() -> None:
    # Arrange
    current = [
        RoadmapCourse(course_id=1, position=1),
        RoadmapCourse(course_id=2, position=2),
        RoadmapCourse(course_id=3, position=3),
    ]

    # Act
    result = remove_course(current, course_id=2)

    # Assert
    assert result == [
        RoadmapCourse(course_id=1, position=1),
        RoadmapCourse(course_id=3, position=2),
    ]


def test_remove_course_missing_raises_course_not_in_roadmap() -> None:
    # Arrange
    current = [RoadmapCourse(course_id=1, position=1)]

    # Act / Assert
    with pytest.raises(RoadmapRuleError) as error:
        remove_course(current, course_id=99)

    assert error.value.code == "COURSE_NOT_IN_ROADMAP"


def test_reorder_courses_valid_returns_new_positions() -> None:
    # Arrange
    current = [
        RoadmapCourse(course_id=1, position=1),
        RoadmapCourse(course_id=2, position=2),
        RoadmapCourse(course_id=3, position=3),
    ]

    # Act
    result = reorder_courses(current, [3, 1, 2])

    # Assert
    assert result == [
        RoadmapCourse(course_id=3, position=1),
        RoadmapCourse(course_id=1, position=2),
        RoadmapCourse(course_id=2, position=3),
    ]


def test_reorder_courses_empty_roadmap_returns_empty_list() -> None:
    # Arrange
    current: list[RoadmapCourse] = []

    # Act
    result = reorder_courses(current, [])

    # Assert
    assert result == []


@pytest.mark.parametrize(
    "ordered_course_ids",
    [
        [1, 2],
        [1, 2, 3, 4],
        [1, 1, 2],
        [0, 1, 2],
    ],
)
def test_reorder_courses_invalid_permutation_raises_invalid_reorder(
    ordered_course_ids: list[int],
) -> None:
    # Arrange
    current = [
        RoadmapCourse(course_id=1, position=1),
        RoadmapCourse(course_id=2, position=2),
        RoadmapCourse(course_id=3, position=3),
    ]

    # Act / Assert
    with pytest.raises(RoadmapRuleError) as error:
        reorder_courses(current, ordered_course_ids)

    assert error.value.code == "INVALID_REORDER"
