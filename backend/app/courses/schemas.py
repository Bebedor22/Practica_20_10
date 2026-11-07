from pydantic import BaseModel, ConfigDict


class CourseCreate(BaseModel):
    title: str
    version: str
    year: int
    category: str
    theme: str
    url: str
    instructor: str
    has_quiz: bool = False
    requires_exam: bool = False
    extends_certificate: bool = False
    organization: str | None = None


class CourseUpdate(BaseModel):
    title: str | None = None
    version: str | None = None
    year: int | None = None
    category: str | None = None
    theme: str | None = None
    url: str | None = None
    instructor: str | None = None
    has_quiz: bool | None = None
    requires_exam: bool | None = None
    extends_certificate: bool | None = None
    organization: str | None = None


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
    status: str
    validated: bool
    user_id: int

    model_config = ConfigDict(from_attributes=True)
