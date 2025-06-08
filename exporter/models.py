from pydantic import BaseModel


class Task(BaseModel):
    name: str
    count: int


class Queue(BaseModel):
    name: str
    db: str
    length: int


class RedisConnectionParams(BaseModel):
    host: str
    port: int
    db: str
    username: str
    password: str
