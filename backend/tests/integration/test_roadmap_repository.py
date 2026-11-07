import pytest
from sqlalchemy.orm import Session

from app.courses.repository import CourseRepository
from app.courses.rules import CourseStatus
from app.roadmaps.repository import RoadmapRepository
from app.roadmaps.rules import RoadmapRuleError
from tests.integration.test_course_repository import make_course_data


def create_course(
    session: Session,
    user_id: int,
    *,
    status: CourseStatus = CourseStatus.PUBLISHED,
    **overrides: object,
) -> int:
    repository = CourseRepository(session)
    course = repository.create(
        make_course_data(**overrides),
        user_id=user_id,
        status=status,
    )
    return course.id


def test_add_course_published_appends_with_next_position(
    db_session: Session, user_factory
) -> None:
    # Arrange
    user = user_factory()
    first_id = create_course(db_session, user.id)
    second_id = create_course(db_session, user.id)
    repository = RoadmapRepository(db_session)

    # Act
    first = repository.add_course(user.id, "Desarrollo Web", first_id)
    second = repository.add_course(user.id, "Desarrollo Web", second_id)

    # Assert
    assert first.position == 1
    assert second.position == 2


def test_add_course_duplicate_raises_course_already_in_roadmap(
    db_session: Session, user_factory
) -> None:
    # Arrange
    user = user_factory()
    course_id = create_course(db_session, user.id)
    repository = RoadmapRepository(db_session)
    repository.add_course(user.id, "Desarrollo Web", course_id)

    # Act / Assert
    with pytest.raises(RoadmapRuleError) as error:
        repository.add_course(user.id, "Desarrollo Web", course_id)

    assert error.value.code == "COURSE_ALREADY_IN_ROADMAP"


def test_add_course_unpublished_raises_course_not_published(
    db_session: Session, user_factory
) -> None:
    # Arrange
    user = user_factory()
    course_id = create_course(
        db_session, user.id, status=CourseStatus.IN_REVIEW
    )
    repository = RoadmapRepository(db_session)

    # Act / Assert
    with pytest.raises(RoadmapRuleError) as error:
        repository.add_course(user.id, "Desarrollo Web", course_id)

    assert error.value.code == "COURSE_NOT_PUBLISHED"


def test_add_course_missing_raises_course_not_found(
    db_session: Session, user_factory
) -> None:
    # Arrange
    user = user_factory()
    repository = RoadmapRepository(db_session)

    # Act / Assert
    with pytest.raises(RoadmapRuleError) as error:
        repository.add_course(user.id, "Desarrollo Web", 999999)

    assert error.value.code == "COURSE_NOT_FOUND"


def test_remove_course_reindexes_remaining_positions(
    db_session: Session, user_factory
) -> None:
    # Arrange
    user = user_factory()
    first_id = create_course(db_session, user.id)
    second_id = create_course(db_session, user.id)
    repository = RoadmapRepository(db_session)
    repository.add_course(user.id, "Desarrollo Web", first_id)
    repository.add_course(user.id, "Desarrollo Web", second_id)

    # Act
    repository.remove_course(user.id, "Desarrollo Web", first_id)
    entries = repository.list_entries(user.id, "Desarrollo Web")

    # Assert
    assert len(entries) == 1
    assert entries[0].course_id == second_id
    assert entries[0].position == 1


def test_reorder_courses_returns_new_order(
    db_session: Session, user_factory
) -> None:
    # Arrange
    user = user_factory()
    first_id = create_course(db_session, user.id)
    second_id = create_course(db_session, user.id)
    third_id = create_course(db_session, user.id)
    repository = RoadmapRepository(db_session)
    repository.add_course(user.id, "Desarrollo Web", first_id)
    repository.add_course(user.id, "Desarrollo Web", second_id)
    repository.add_course(user.id, "Desarrollo Web", third_id)

    # Act
    entries = repository.reorder_courses(
        user.id, "Desarrollo Web", [third_id, first_id, second_id]
    )

    # Assert
    assert [(entry.course_id, entry.position) for entry in entries] == [
        (third_id, 1),
        (first_id, 2),
        (second_id, 3),
    ]


def test_reorder_courses_invalid_permutation_raises_invalid_reorder(
    db_session: Session, user_factory
) -> None:
    # Arrange
    user = user_factory()
    first_id = create_course(db_session, user.id)
    second_id = create_course(db_session, user.id)
    repository = RoadmapRepository(db_session)
    repository.add_course(user.id, "Desarrollo Web", first_id)
    repository.add_course(user.id, "Desarrollo Web", second_id)

    # Act / Assert
    with pytest.raises(RoadmapRuleError) as error:
        repository.reorder_courses(user.id, "Desarrollo Web", [first_id])

    assert error.value.code == "INVALID_REORDER"
