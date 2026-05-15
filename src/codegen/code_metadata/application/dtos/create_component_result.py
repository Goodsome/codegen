from pydantic import BaseModel


class CreateComponentResult(BaseModel):
    component_id: str
