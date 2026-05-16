from pydantic import BaseModel


class PageQuery[T](BaseModel):
    current: int = 1
    size: int = 10
    condition: T
    