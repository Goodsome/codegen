from pydantic import BaseModel


class UpsertComponentResult(BaseModel):
    component_id: str