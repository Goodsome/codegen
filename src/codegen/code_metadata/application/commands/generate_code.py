from dataclasses import dataclass

from codegen.code_metadata.application.dtos.generate_code_command import (
    GenerateCodeCommand,
)
from codegen.code_metadata.application.dtos.generate_code_result import (
    GenerateCodeResult,
)
from codegen.code_metadata.application.ports.component_query_service import (
    ComponentQueryService,
)
from codegen.code_metadata.domain.identifiers.component_id import ComponentId
from codegen.code_metadata.domain.ports.code_generator import CodeGenerator
from codegen.code_metadata.domain.ports.component_repository import ComponentRepository
from codegen.code_metadata.domain.services.reference_resolver import ReferenceResolver
from codegen.shared.application.ports.unit_of_work import UnitOfWork


@dataclass
class GenerateCode:
    query_service: ComponentQueryService
    uow: UnitOfWork[ComponentRepository]
    generator: CodeGenerator

    def execute(self, cmd: GenerateCodeCommand) -> GenerateCodeResult:
        c_id = ComponentId.reconstitute(cmd.component_id)
        with self.uow:
            component = self.uow.repository.get(c_id)
            dep_components = self.uow.repository.find_by_ids(
                ids=component.get_dependencies()
            )
        code = self.generator.generate(
            component,
            resolver=ReferenceResolver(name_map=dep_components),
        )
        return GenerateCodeResult(code=code)
