from pydantic import BaseModel
from codegen.domain_definition.domain.aggregates.blueprint import Blueprint


class InitProjectResult(BaseModel):
    blueprint: Blueprint
