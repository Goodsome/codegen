from pydantic import BaseModel


class GenerateBlueprintResult(BaseModel):
    result: str
