from pydantic import BaseModel


class ImportDto(BaseModel):
    module: str | None
    level: int
    names: list[str]