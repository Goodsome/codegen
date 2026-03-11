from pydantic import Field

from codegen.shared.models import ValueObject


class HttpEndpointSpec(ValueObject):
    """HTTP Endpoint 规范"""

    path: str
    method: str
    use_case: str
    description: str = Field(default_factory=str)