from app.auth.models import User
from app.courses.models import Course
from app.db.base import Base
from app.db.session import engine
from app.roadmaps.models import Roadmap


def init_db() -> None:
    Base.metadata.create_all(
        engine,
        tables=[User.__table__, Course.__table__, Roadmap.__table__],
    )
