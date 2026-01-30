from codegen.domain_definition.domain.value_objects.service_spec import ServiceSpec
from codegen.domain_definition.domain.value_objects.use_case_spec import UseCaseSpec
from codegen.domain_definition.domain.value_objects.port_spec import PortSpec
from codegen.shared.models import ValueObject
from pydantic import Field


class ApplicationSpec(ValueObject):
    """Specification of an application to be generated."""

    use_cases: list[UseCaseSpec] = Field(default_factory=list)
    ports: list[PortSpec] = Field(default_factory=list)
    services: list[ServiceSpec] = Field(default_factory=list)

    def add_use_case(self, use_case: UseCaseSpec) -> "ApplicationSpec":
        if any(uc.name == use_case.name for uc in self.use_cases):
            raise ValueError(f"Use Case '{use_case.name}' already exists.")
        return self.model_copy(update={"use_cases": self.use_cases + [use_case]})

    def update_use_case(self, use_case: UseCaseSpec) -> "ApplicationSpec":
        if not any(uc.name == use_case.name for uc in self.use_cases):
            raise ValueError(f"Use Case '{use_case.name}' not found.")
        new_list = [
            use_case if uc.name == use_case.name else uc for uc in self.use_cases
        ]
        return self.model_copy(update={"use_cases": new_list})

    def delete_use_case(self, name: str) -> "ApplicationSpec":
        new_list = [uc for uc in self.use_cases if str(uc.name) != name]
        if len(new_list) == len(self.use_cases):
            raise ValueError(f"Use Case '{name}' not found.")
        return self.model_copy(update={"use_cases": new_list})

    def add_port(self, port: PortSpec) -> "ApplicationSpec":
        if any(p.name == port.name for p in self.ports):
            raise ValueError(f"Port '{port.name}' already exists.")
        return self.model_copy(update={"ports": self.ports + [port]})

    def update_port(self, port: PortSpec) -> "ApplicationSpec":
        if not any(p.name == port.name for p in self.ports):
            raise ValueError(f"Port '{port.name}' not found.")
        new_list = [port if p.name == port.name else p for p in self.ports]
        return self.model_copy(update={"ports": new_list})

    def delete_port(self, name: str) -> "ApplicationSpec":
        new_list = [p for p in self.ports if str(p.name) != name]
        if len(new_list) == len(self.ports):
            raise ValueError(f"Port '{name}' not found.")
        return self.model_copy(update={"ports": new_list})
