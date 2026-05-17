from pydantic import BaseModel


class GetDevProgressQuery(BaseModel):
    context: str
    component_type: str | None = None
    