from pydantic import BaseModel


class GenerateCodeCommand(BaseModel):
    component_id: str
    