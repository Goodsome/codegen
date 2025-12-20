
from codegen.domain.ports.file_system_port import FileSystemPort

from codegen.domain.ports.template_port import TemplatePort

from codegen.domain.services.naming_service import NamingService

from codegen.domain.services.scaffold_service import ScaffoldService

from codegen.domain.services.template_context_builder import TemplateContextBuilder

from dataclasses import dataclass

from typing import List



@dataclass(frozen=True)
class GenerateCodeCommand:
    """Command/Query for GenerateCode."""
    
    overwrite: bool  # 
    
    node: str  # 
    

@dataclass(frozen=True)
class GenerateCodeResult:
    """Result of GenerateCode."""
    
    files_written: List[str]  # 
    

@dataclass
class GenerateCodeHandler:
    """Handler for GenerateCode (command)."""

    
    naming_service: NamingService

    scaffold_service: ScaffoldService
    
    template_context_builder: TemplateContextBuilder
    
    template_port: TemplatePort
    
    file_system_port: FileSystemPort
    

    def execute(self, cmd: GenerateCodeCommand) -> GenerateCodeResult:
        import yaml
        from pathlib import Path
        from codegen.domain.aggregates.blueprint import Blueprint

        yaml_path = Path("codegen.yaml")
        if not yaml_path.exists():
            return GenerateCodeResult(files_written=[])

        with open(yaml_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        blueprint = Blueprint.model_validate(data)

        self.template_context_builder.build_registry(blueprint)

        written_files = []
        all_ports = [p for ctx in blueprint.contexts for p in ctx.ports]

        for ctx in blueprint.contexts:
            # 1. Aggregates
            for agg in ctx.aggregates:
                path = self.scaffold_service.get_component_path("aggregate", agg.name)
                tpl_ctx = self.template_context_builder.build_context(agg)
                content = self.template_port.render("domain/aggregate.j2", tpl_ctx)
                self.file_system_port.write_text(path, content)
                written_files.append(path)

            # 2. Value Objects
            for vo in ctx.value_objects:
                path = self.scaffold_service.get_component_path("value_object", vo.name)
                tpl_ctx = self.template_context_builder.build_context(vo)
                content = self.template_port.render("domain/value_object.j2", tpl_ctx)
                self.file_system_port.write_text(path, content)
                written_files.append(path)

            # 3. Services
            for svc in ctx.services:
                path = self.scaffold_service.get_component_path("service", svc.name)
                tpl_ctx = self.template_context_builder.build_context(svc)
                content = self.template_port.render("domain/service.j2", tpl_ctx)
                self.file_system_port.write_text(path, content)
                written_files.append(path)

            # 4. Ports
            for port in ctx.ports:
                path = self.scaffold_service.get_component_path("port", port.name)
                tpl_ctx = self.template_context_builder.build_context(port)
                content = self.template_port.render("domain/port.j2", tpl_ctx)
                self.file_system_port.write_text(path, content)
                written_files.append(path)

            # 5. Use Cases
            for uc in ctx.use_cases:
                path = self.scaffold_service.get_component_path("use_case", uc.name)
                tpl_ctx = self.template_context_builder.build_context(uc)
                content = self.template_port.render("application/use_case.j2", tpl_ctx)
                self.file_system_port.write_text(path, content)
                written_files.append(path)

        # 6. Infrastructure Adapters
        infra = data.get("shared", {}).get("infrastructure", {})
        for adapter_data in infra.get("adapters", []):
            # Special logic for adapters to find matching port operations
            port_ops = []
            for p in all_ports:
                if p.name == adapter_data["implements"]:
                    port_ops = p.operations
                    break

            path = self.scaffold_service.get_component_path("adapter", adapter_data["name"])
            tpl_ctx = {
                "name": adapter_data["name"],
                "description": adapter_data.get("description", ""),
                "implements": adapter_data["implements"],
                "implements_snake": self.naming_service.to_snake(adapter_data["implements"]),
                "config": adapter_data.get("config", {}),
                "operations": port_ops
            }
            content = self.template_port.render("infrastructure/adapter.j2", tpl_ctx)
            self.file_system_port.write_text(path, content)
            written_files.append(path)

        return GenerateCodeResult(files_written=written_files)
    