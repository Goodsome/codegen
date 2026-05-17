from pydantic import BaseModel


class ImportedComponent(BaseModel):
    context: str
    component: str
    
    