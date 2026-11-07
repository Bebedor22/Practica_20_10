from uuid import uuid4

from sqlalchemy.orm import Session

from app.auth.models import User
from app.courses.repository import CourseRepository
from app.courses.rules import CourseStatus


def make_course_data(**overrides: object) -> dict[str, object]:
    unique = uuid4().hex[:10]
    data: dict[str, object] = {
        "title": f"Curso {unique}",
        "version": "2026.1",
        "year": 2025,
        "category": "Programación",
        "theme": "Python",
        "url": f"https://example.com/curso-{unique}",
        "instructor": "Ada Lovelace",
        "has_quiz": True,
        "requires_exam": False,
        "extends_certificate": True,
        "organization": "Universidad Ejemplo",
    }
    data.update(overrides)
    return data


def test_create_and_get_by_id_roundtrip(db_session: Session, user_factory) -> None:
    # Arrange
    user = user_factory()
    repository = CourseRepository(db_session)
    data = make_course_data()

    # Act
    created = repository.create(data, user_id=user.id)
    fetched = repository.get_by_id(created.id)

    # Assert
    assert fetched is not None
    assert fetched.id == created.id
    assert fetched.title == data["title"]
    assert fetched.url == data["url"]
    assert fetched.status == CourseStatus.IN_REVIEW.value
    assert fetched.validated is False


def test_create_with_published_status_returns_validated_course(
    db_session: Session, user_factory
) -> None:
    # Arrange
    user = user_factory()
    repository = CourseRepository(db_session)

    # Act
    course = repository.create(
        make_course_data(),
        user_id=user.id,
        status=CourseStatus.PUBLISHED,
    )

    # Assert
    assert course.status == CourseStatus.PUBLISHED.value
    assert course.validated is True


def test_list_page_one_size_two_returns_two_items(
    db_session: Session, user_factory
) -> None:
    # Arrange
    user = user_factory()
    repository = CourseRepository(db_session)
    for _ in range(5):
        repository.create(
            make_course_data(), user_id=user.id, status=CourseStatus.PUBLISHED
        )

    # Act
    items, total = repository.list(page=1, limit=2)

    # Assert
    assert len(items) == 2
    assert total == 5


def test_list_page_two_size_two_returns_next_items(
    db_session: Session, user_factory
) -> None:
    # Arrange
    user = user_factory()
    repository = CourseRepository(db_session)
    for _ in range(5):
        repository.create(
            make_course_data(), user_id=user.id, status=CourseStatus.PUBLISHED
        )

    # Act
    items, total = repository.list(page=2, limit=2)

    # Assert
    assert len(items) == 2
    assert total == 5


def test_list_page_three_size_two_returns_remaining_item(
    db_session: Session, user_factory
) -> None:
    # Arrange
    user = user_factory()
    repository = CourseRepository(db_session)
    for _ in range(5):
        repository.create(
            make_course_data(), user_id=user.id, status=CourseStatus.PUBLISHED
        )

    # Act
    items, total = repository.list(page=3, limit=2)

    # Assert
    assert len(items) == 1
    assert total == 5


def test_list_page_beyond_total_returns_empty_items(
    db_session: Session, user_factory
) -> None:
    # Arrange
    user = user_factory()
    repository = CourseRepository(db_session)
    repository.create(
        make_course_data(), user_id=user.id, status=CourseStatus.PUBLISHED
    )

    # Act
    items, total = repository.list(page=4, limit=2)

    # Assert
    assert items == []
    assert total == 1


def test_list_q_filter_matches_title_and_theme_case_insensitive(
    db_session: Session, user_factory
) -> None:
    # Arrange
    user = user_factory()
    repository = CourseRepository(db_session)
    repository.create(
        make_course_data(title="Curso de Python", theme="Backend"),
        user_id=user.id,
        status=CourseStatus.PUBLISHED,
    )
    repository.create(
        make_course_data(title="Curso de Java", theme="Python avanzado"),
        user_id=user.id,
        status=CourseStatus.PUBLISHED,
    )
    repository.create(
        make_course_data(title="Curso de Diseño", theme="UI/UX"),
        user_id=user.id,
        status=CourseStatus.PUBLISHED,
    )

    # Act
    items, total = repository.list(q="pYtHoN")

    # Assert
    assert total == 2
    assert {item.title for item in items} == {"Curso de Python", "Curso de Java"}


def test_list_category_filter_returns_only_matching_category(
    db_session: Session, user_factory
) -> None:
    # Arrange
    user = user_factory()
    repository = CourseRepository(db_session)
    repository.create(
        make_course_data(category="Programación"),
        user_id=user.id,
        status=CourseStatus.PUBLISHED,
    )
    repository.create(
        make_course_data(category="Programación"),
        user_id=user.id,
        status=CourseStatus.PUBLISHED,
    )
    repository.create(
        make_course_data(category="Diseño"),
        user_id=user.id,
        status=CourseStatus.PUBLISHED,
    )

    # Act
    items, total = repository.list(category="Programación")

    # Assert
    assert total == 2
    assert all(item.category == "Programación" for item in items)


def test_list_defaults_to_published_status_only(
    db_session: Session, user_factory
) -> None:
    # Arrange
    user = user_factory()
    repository = CourseRepository(db_session)
    published = repository.create(
        make_course_data(), user_id=user.id, status=CourseStatus.PUBLISHED
    )
    repository.create(
        make_course_data(), user_id=user.id, status=CourseStatus.IN_REVIEW
    )

    # Act
    items, total = repository.list()

    # Assert
    assert total == 1
    assert [item.id for item in items] == [published.id]


def test_list_explicit_status_returns_pending_courses(
    db_session: Session, user_factory
) -> None:
    # Arrange
    user = user_factory()
    repository = CourseRepository(db_session)
    repository.create(
        make_course_data(), user_id=user.id, status=CourseStatus.PUBLISHED
    )
    pending = repository.create(
        make_course_data(), user_id=user.id, status=CourseStatus.IN_REVIEW
    )

    # Act
    items, total = repository.list(status=CourseStatus.IN_REVIEW)

    # Assert
    assert total == 1
    assert [item.id for item in items] == [pending.id]


def test_update_partial_fields_keeps_other_values(
    db_session: Session, user_factory
) -> None:
    # Arrange
    user = user_factory()
    repository = CourseRepository(db_session)
    course = repository.create(make_course_data(), user_id=user.id)

    # Act
    updated = repository.update(course.id, {"title": "Título actualizado"})

    # Assert
    assert updated is not None
    assert updated.title == "Título actualizado"
    assert updated.theme == course.theme
    assert updated.version == course.version


def test_update_missing_course_returns_none(
    db_session: Session, user_factory
) -> None:
    # Arrange
    user_factory()
    repository = CourseRepository(db_session)

    # Act
    updated = repository.update(999999, {"title": "No existe"})

    # Assert
    assert updated is None


def test_delete_then_get_by_id_returns_none(
    db_session: Session, user_factory
) -> None:
    # Arrange
    user = user_factory()
    repository = CourseRepository(db_session)
    course = repository.create(make_course_data(), user_id=user.id)

    # Act
    deleted = repository.delete(course.id)
    fetched = repository.get_by_id(course.id)

    # Assert
    assert deleted is True
    assert fetched is None


def test_delete_missing_course_returns_false(
    db_session: Session, user_factory
) -> None:
    # Arrange
    user_factory()
    repository = CourseRepository(db_session)

    # Act
    deleted = repository.delete(999999)

    # Assert
    assert deleted is False


def test_url_exists_ignores_case_and_trailing_slash(
    db_session: Session, user_factory
) -> None:
    # Arrange
    user = user_factory()
    repository = CourseRepository(db_session)
    repository.create(
        make_course_data(url="https://Example.com/Curso-Python/"),
        user_id=user.id,
    )

    # Act
    exists_same = repository.url_exists("https://example.com/curso-python")
    exists_other = repository.url_exists("https://example.com/otro-curso")

    # Assert
    assert exists_same is True
    assert exists_other is False
