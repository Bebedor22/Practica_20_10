from pydantic import BaseModel, ConfigDict


class CourseRead(BaseModel):
    id: int
    title: str
    version: str
    year: int
    category: str
    theme: str
    url: str
    instructor: str
    has_quiz: bool
    requires_exam: bool
    extends_certificate: bool
    organization: str | None = None
    validated: bool
    user_id: int

    model_config = ConfigDict(from_attributes=True)
