from pydantic import Field

from codegen.shared.models import ValueObject
from codegen.domain_definition.domain.value_objects.http_endpoint_spec import HttpEndpointSpec


class HttpInterfaceSpec(ValueObject):
    """HTTP 接口层规范"""

    endpoints: list[HttpEndpointSpec] = Field(default_factory=list)