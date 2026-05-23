from pydantic import BaseModel


class ImportDto(BaseModel):
    module: str
    names: list[str]