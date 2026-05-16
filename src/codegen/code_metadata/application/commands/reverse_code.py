from dataclasses import dataclass
from pathlib import Path

from codegen.code_metadata.application.commands.upsert_component import UpsertComponent
from codegen.code_metadata.application.dtos.reverse_code_command import (
    ReverseCodeCommand,
)
from codegen.code_metadata.application.dtos.reverse_code_result import ReverseCodeResult
from codegen.code_metadata.application.dtos.upsert_component_command import (
    UpsertComponentCommand,
)
from codegen.code_metadata.application.dtos.upsert_component_result import (
    UpsertComponentResult,
)
from codegen.code_metadata.application.ports.code_parser import CodeParser
from codegen.code_metadata.domain.enums import ComponentType
from codegen.code_metadata.domain.factories.component_policy_factory import (
    ComponentPolicyFactory,
)
from codegen.shared.domain.ports.file_system_port import FileSystemPort


@dataclass
class ReverseCode:
    parser: CodeParser
    upsert_component: UpsertComponent
    file_system_port: FileSystemPort
    component_policy_factory: ComponentPolicyFactory

    def execute(self, cmd: ReverseCodeCommand) -> ReverseCodeResult:
        component_type = ComponentType(cmd.component_type)
        policy = self.component_policy_factory.get_policy(component_type)
        target_path = cmd.context / policy.target_path
        component_ids: list[str] = []
        for file_path in self.file_system_port.list_directory_recursively(target_path):
            result = self._reverse_one_component(
                cmd.context, cmd.component_type, file_path
            )
            component_ids.append(result.component_id)
        return ReverseCodeResult(component_ids=component_ids)

    def _reverse_one_component(
        self,
        context: str,
        component_type: str,
        code_path: Path,
    ) -> UpsertComponentResult:
        pc = self.parser.parse(code_path)
        ucc = UpsertComponentCommand(
            type=component_type,
            context=context,
            name=pc.name,
            description=pc.description,
        )
        result = self.upsert_component.execute(cmd=ucc)
        return result
