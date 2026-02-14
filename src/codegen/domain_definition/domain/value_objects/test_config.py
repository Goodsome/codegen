from codegen.domain_definition.domain.enums import TestMockStrategy
from codegen.shared.models import ValueObject
from pydantic import Field


class TestConfig(ValueObject):
    """Configuration for automated test generation."""
    
    __test__ = False

    enabled: bool = True
    strategy: TestMockStrategy = TestMockStrategy.PYTEST
    fixtures_path: str | None = None
