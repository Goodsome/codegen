from pydantic import BaseModel
from codegen.domain_definition.domain.aggregates.blueprint import Blueprint


class LoadBlueprintResult(BaseModel):
    blueprint: Blueprint
