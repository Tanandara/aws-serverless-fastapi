from uuid import UUID

from pydantic import BaseModel, Field


class CreateTaskRequest(BaseModel):
    title: str = Field(min_length=1, max_length=200)


class TaskResponse(BaseModel):
    id: UUID
    title: str
    completed: bool
