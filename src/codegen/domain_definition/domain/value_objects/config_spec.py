from pydantic import Field
from codegen.shared.domain.value_objects.pascal_string import PascalString
from codegen.shared.models import ValueObject
from codegen.domain_definition.domain.value_objects.config_field_spec import ConfigFieldSpec


class ConfigSpec(ValueObject):
    """Specification for a configuration object (AppSettings or ContextSettings)."""

    class_name: PascalString | None = Field(default=None)
    env_prefix: str = Field(default="")
    env_file: str | None = Field(default=None)
    fields: list[ConfigFieldSpec] = Field(default_factory=list)
