from pydantic import BaseModel


class ImportedComponent(BaseModel):
    context: str
    name: str
    type: str
    
    