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
from codegen.code_metadata.domain.policies import ComponentPolicy
from codegen.shared.domain.ports.file_system_port import FileSystemPort


@dataclass
class ReverseCode:
    parser: CodeParser
    upsert_component: UpsertComponent
    file_system_port: FileSystemPort
    component_policy_factory: ComponentPolicyFactory

    def execute(self, cmd: ReverseCodeCommand) -> ReverseCodeResult:
        policies: list[ComponentPolicy] = []
        if cmd.component_type:
            component_type = ComponentType(cmd.component_type)
            policies.append(self.component_policy_factory.get_policy(component_type))
        else:
            policies = self.component_policy_factory.get_policies()

        component_ids: list[str] = []
        for policy in policies:
            result = self._reverse_component(
                cmd.context,
                component_type=str(policy.component_type),
                policy=policy,
            )
            component_ids.extend(result)

        return ReverseCodeResult(component_ids=component_ids)

    def _reverse_component(
        self, context: str, component_type: str, policy: ComponentPolicy
    ) -> list[str]:
        target_path = f"src/codegen/{context}" / policy.target_path
        component_ids: list[str] = []
        for file_path in self.file_system_port.list_directory_recursively(
            target_path, pattern="*.py"
        ):
            if file_path.stem == "__init__":
                continue
            result = self._reverse_one_component(context, component_type, file_path)
            component_ids.append(result.component_id)
        return component_ids

    def _reverse_one_component(
        self,
        context: str,
        component_type: str,
        code_path: Path,
    ) -> UpsertComponentResult:
        code = self.file_system_port.read_file(code_path)
        file_name = code_path.stem
        pc = self.parser.parse(code, module_name=file_name)
        ucc = UpsertComponentCommand(
            type=component_type,
            context=context,
            name=pc.name,
            description=pc.description,
        )
        result = self.upsert_component.execute(cmd=ucc)
        return result
