from pydantic import BaseModel


class ComponentDTO(BaseModel):
    type: str
    name: str
    description: str
    context: str
