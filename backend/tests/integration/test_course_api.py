from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.auth.models import User
from app.auth.security import create_access_token
from app.courses.repository import CourseRepository
from app.courses.rules import CourseStatus
from tests.integration.test_course_repository import make_course_data


def auth_headers(user: User) -> dict[str, str]:
    token = create_access_token(user.id, role=user.role)
    return {"Authorization": f"Bearer {token}"}


def create_pending_course(
    db_session: Session,
    user: User,
    **overrides: object,
) -> int:
    repository = CourseRepository(db_session)
    course = repository.create(
        make_course_data(**overrides),
        user_id=user.id,
        status=CourseStatus.IN_REVIEW,
    )
    return course.id


def create_published_course(
    db_session: Session,
    user: User,
    **overrides: object,
) -> int:
    repository = CourseRepository(db_session)
    course = repository.create(
        make_course_data(**overrides),
        user_id=user.id,
        status=CourseStatus.PUBLISHED,
    )
    return course.id


def test_list_courses_returns_only_published_courses(
    client: TestClient, db_session: Session, user_factory
) -> None:
    # Arrange
    author = user_factory()
    create_published_course(db_session, author, title="Curso publicado")
    create_pending_course(db_session, author, title="Curso pendiente")

    # Act
    response = client.get("/courses")

    # Assert
    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 1
    assert [item["title"] for item in body["items"]] == ["Curso publicado"]
    assert body["items"][0]["validated"] is True


def test_list_courses_q_and_category_filters(
    client: TestClient, db_session: Session, user_factory
) -> None:
    # Arrange
    author = user_factory()
    create_published_course(
        db_session,
        author,
        title="Python desde cero",
        category="Programación",
        theme="Backend",
    )
    create_published_course(
        db_session,
        author,
        title="Diseño de interfaces",
        category="Diseño",
        theme="UI/UX",
    )

    # Act
    by_query = client.get("/courses", params={"q": "pYtHoN"})
    by_category = client.get(
        "/courses", params={"category": "Programación"}
    )

    # Assert
    assert by_query.json()["total"] == 1
    assert by_query.json()["items"][0]["title"] == "Python desde cero"
    assert by_category.json()["total"] == 1
    assert by_category.json()["items"][0]["category"] == "Programación"


def test_get_published_course_returns_detail(
    client: TestClient, db_session: Session, user_factory
) -> None:
    # Arrange
    author = user_factory()
    course_id = create_published_course(db_session, author)

    # Act
    response = client.get(f"/courses/{course_id}")

    # Assert
    assert response.status_code == 200
    assert response.json()["id"] == course_id
    assert response.json()["status"] == CourseStatus.PUBLISHED.value


def test_get_pending_course_returns_not_found(
    client: TestClient, db_session: Session, user_factory
) -> None:
    # Arrange
    author = user_factory()
    course_id = create_pending_course(db_session, author)

    # Act
    response = client.get(f"/courses/{course_id}")

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"]["code"] == "COURSE_NOT_FOUND"


def test_get_missing_course_returns_not_found(client: TestClient) -> None:
    # Act
    response = client.get("/courses/999999")

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"]["code"] == "COURSE_NOT_FOUND"


def test_create_course_without_token_returns_unauthorized(
    client: TestClient,
) -> None:
    # Act
    response = client.post("/courses", json=make_course_data())

    # Assert
    assert response.status_code == 401
    assert response.json()["detail"]["code"] == "AUTH_001"


def test_create_course_returns_pending_course_for_authenticated_user(
    client: TestClient, user_factory
) -> None:
    # Arrange
    user = user_factory()
    payload = make_course_data()

    # Act
    response = client.post(
        "/courses", json=payload, headers=auth_headers(user)
    )

    # Assert
    assert response.status_code == 201
    body = response.json()
    assert body["status"] == CourseStatus.IN_REVIEW.value
    assert body["validated"] is False
    assert body["user_id"] == user.id
    assert body["title"] == payload["title"]


def test_create_course_invalid_year_returns_rule_violation(
    client: TestClient, user_factory
) -> None:
    # Arrange
    user = user_factory()
    payload = make_course_data(year=1999)

    # Act
    response = client.post(
        "/courses", json=payload, headers=auth_headers(user)
    )

    # Assert
    assert response.status_code == 422
    details = response.json()["detail"]["details"]
    assert [detail["code"] for detail in details] == ["YEAR_BEFORE_2000"]


def test_create_course_duplicate_url_returns_rule_violation(
    client: TestClient, db_session: Session, user_factory
) -> None:
    # Arrange
    author = user_factory()
    existing_id = create_published_course(db_session, author)
    existing = CourseRepository(db_session).get_by_id(existing_id)
    assert existing is not None
    payload = make_course_data(url=existing.url)

    # Act
    response = client.post(
        "/courses", json=payload, headers=auth_headers(author)
    )

    # Assert
    assert response.status_code == 422
    details = response.json()["detail"]["details"]
    assert [detail["code"] for detail in details] == ["URL_DUPLICATE"]


def test_validate_course_without_token_returns_unauthorized(
    client: TestClient, db_session: Session, user_factory
) -> None:
    # Arrange
    author = user_factory()
    course_id = create_pending_course(db_session, author)

    # Act
    response = client.put(f"/courses/{course_id}/validate", json={})

    # Assert
    assert response.status_code == 401


def test_validate_course_as_regular_user_returns_forbidden(
    client: TestClient, db_session: Session, user_factory
) -> None:
    # Arrange
    author = user_factory()
    regular_user = user_factory()
    course_id = create_pending_course(db_session, author)

    # Act
    response = client.put(
        f"/courses/{course_id}/validate",
        json={"approved": True},
        headers=auth_headers(regular_user),
    )

    # Assert
    assert response.status_code == 403
    assert response.json()["detail"]["code"] == "ROLE_NOT_ALLOWED"


def test_validate_own_course_returns_forbidden(
    client: TestClient, db_session: Session, user_factory
) -> None:
    # Arrange
    instructor = user_factory(role="instructor")
    course_id = create_pending_course(db_session, instructor)

    # Act
    response = client.put(
        f"/courses/{course_id}/validate",
        json={"approved": True},
        headers=auth_headers(instructor),
    )

    # Assert
    assert response.status_code == 403
    assert response.json()["detail"]["code"] == "SELF_VALIDATION_FORBIDDEN"


def test_instructor_can_approve_pending_course(
    client: TestClient, db_session: Session, user_factory
) -> None:
    # Arrange
    author = user_factory()
    instructor = user_factory(role="instructor")
    course_id = create_pending_course(db_session, author)

    # Act
    response = client.put(
        f"/courses/{course_id}/validate",
        json={"approved": True},
        headers=auth_headers(instructor),
    )

    # Assert
    assert response.status_code == 200
    assert response.json()["status"] == CourseStatus.PUBLISHED.value
    assert response.json()["validated"] is True


def test_admin_can_reject_pending_course(
    client: TestClient, db_session: Session, user_factory
) -> None:
    # Arrange
    author = user_factory()
    admin = user_factory(role="admin")
    course_id = create_pending_course(db_session, author)

    # Act
    response = client.put(
        f"/courses/{course_id}/validate",
        json={"approved": False},
        headers=auth_headers(admin),
    )

    # Assert
    assert response.status_code == 200
    assert response.json()["status"] == CourseStatus.REJECTED.value
    assert response.json()["validated"] is False


def test_validate_published_course_returns_bad_request(
    client: TestClient, db_session: Session, user_factory
) -> None:
    # Arrange
    author = user_factory()
    instructor = user_factory(role="instructor")
    course_id = create_published_course(db_session, author)

    # Act
    response = client.put(
        f"/courses/{course_id}/validate",
        json={"approved": True},
        headers=auth_headers(instructor),
    )

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"]["code"] == "COURSE_NOT_IN_REVIEW"


def test_validate_missing_course_returns_not_found(
    client: TestClient, user_factory
) -> None:
    # Arrange
    instructor = user_factory(role="instructor")

    # Act
    response = client.put(
        "/courses/999999/validate",
        json={"approved": True},
        headers=auth_headers(instructor),
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"]["code"] == "COURSE_NOT_FOUND"
