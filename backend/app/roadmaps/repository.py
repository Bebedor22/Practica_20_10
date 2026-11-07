from sqlalchemy import select
from sqlalchemy.orm import Session

from app.roadmaps.models import Roadmap
from app.roadmaps.rules import (
    CourseCandidate,
    RoadmapCourse,
    RoadmapRuleError,
    add_course,
    remove_course,
    reorder_courses,
)


class RoadmapRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def list_entries(self, user_id: int, name: str | None = None) -> list[Roadmap]:
        statement = select(Roadmap).where(Roadmap.user_id == user_id)
        if name is not None:
            statement = statement.where(Roadmap.name == name)
        statement = statement.order_by(Roadmap.name, Roadmap.position)
        return list(self.session.scalars(statement))

    def add_course(self, user_id: int, name: str, course_id: int) -> Roadmap:
        from app.courses.models import Course

        course = self.session.get(Course, course_id)
        user_entries = self.list_entries(user_id)
        if any(entry.course_id == course_id for entry in user_entries):
            raise RoadmapRuleError(
                "COURSE_ALREADY_IN_ROADMAP",
                "El curso ya está en el roadmap",
            )

        current = [
            RoadmapCourse(item.course_id, item.position)
            for item in user_entries
            if item.name == name
        ]
        candidate = (
            CourseCandidate(course_id=course.id, status=course.status)
            if course is not None
            else None
        )
        updated = add_course(current, candidate)

        entry = Roadmap(
            user_id=user_id,
            name=name,
            course_id=course_id,
            position=updated[-1].position,
        )
        self.session.add(entry)
        self.session.commit()
        self.session.refresh(entry)
        return entry

    def remove_course(self, user_id: int, name: str, course_id: int) -> None:
        entries = self.list_entries(user_id, name)
        current = [RoadmapCourse(item.course_id, item.position) for item in entries]
        updated = remove_course(current, course_id)
        positions = {item.course_id: item.position for item in updated}

        entry = next(item for item in entries if item.course_id == course_id)
        self.session.delete(entry)
        for item in entries:
            if item is entry:
                continue
            item.position = positions[item.course_id]
        self.session.commit()

    def reorder_courses(
        self, user_id: int, name: str, ordered_course_ids: list[int]
    ) -> list[Roadmap]:
        entries = self.list_entries(user_id, name)
        current = [RoadmapCourse(item.course_id, item.position) for item in entries]
        updated = reorder_courses(current, ordered_course_ids)
        positions = {item.course_id: item.position for item in updated}

        for entry in entries:
            entry.position = positions[entry.course_id]
        self.session.commit()

        return self.list_entries(user_id, name)
