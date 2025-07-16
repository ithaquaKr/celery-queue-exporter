from pydantic import BaseModel


class Task(BaseModel):
    name: str
    count: int


class Queue(BaseModel):
    name: str
    db: int
    length: int
