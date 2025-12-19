
from codegen.domain.ports.file_system_port import FileSystemPort

from codegen.domain.ports.template_port import TemplatePort

from codegen.domain.services.layout_planner import LayoutPlanner

from codegen.domain.services.naming_service import NamingService

from codegen.domain.services.template_context_builder import TemplateContextBuilder

from codegen.domain.value_objects.code_form import CodeForm

from codegen.domain.value_objects.feature_name import FeatureName

from dataclasses import dataclass

from typing import List


@dataclass(frozen=True)
class GenerateActionCommand:
    """Command/Query for GenerateAction."""
    
    feature_name: FeatureName  # 
    
    code_form: CodeForm  # 
    
    output_root: str  # 
    

@dataclass(frozen=True)
class GenerateActionResult:
    """Result of GenerateAction."""
    
    files_written: List[str]  # 
    

class GenerateActionHandler:
    """Handler for GenerateAction (command)."""

    def __init__(self, naming_service: NamingService, layout_planner: LayoutPlanner, template_context_builder: TemplateContextBuilder, template_port: TemplatePort, file_system_port: FileSystemPort):
        self.naming_service = naming_service
        self.layout_planner = layout_planner
        self.template_context_builder = template_context_builder
        self.template_port = template_port
        self.file_system_port = file_system_port

    def execute(self, cmd: GenerateActionCommand) -> GenerateActionResult:
        """Implement the use case logic."""
        # Note: In a real app, we might load the blueprint from a repository
        # For this migration, we assume the command or a service provides the raw data.
        # But wait, Blueprint is an aggregate. Let's assume we have it or can load it.
        
        # For simplicity in this migration, I'll add a 'blueprint' attribute to the handler 
        # or assume it's passed. Let's assume we load codegen.yaml within the handler for now
        # OR we can pass it in the command. 
        # Actually, let's look at the command. It has output_root.
        
        # I'll implement a simplified version of the bootstrapper loop here.
        import yaml
        from pathlib import Path
        from codegen.domain.aggregates.blueprint import Blueprint
        from codegen.domain.value_objects.layout_strategy import LayoutStrategy

        yaml_path = Path("codegen.yaml")
        if not yaml_path.exists():
            return GenerateActionResult(files_written=[])

        with open(yaml_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        blueprint = Blueprint()
        blueprint.load_from_dict(data)
        
        self.template_context_builder.build_registry(blueprint)
        layout = LayoutStrategy(name=blueprint.layout)
        
        written_files = []
        all_ports = [p for ctx in blueprint.contexts for p in ctx.ports]

        for ctx in blueprint.contexts:
            # 1. Aggregates
            for agg in ctx.aggregates:
                path = self.layout_planner.get_component_path("aggregate", agg.name)
                tpl_ctx = self.template_context_builder.build_context(agg)
                content = self.template_port.render("domain/aggregate.py.j2", tpl_ctx)
                self.file_system_port.write_text(path, content)
                written_files.append(path)

            # 2. Value Objects
            for vo in ctx.value_objects:
                path = self.layout_planner.get_component_path("value_object", vo.name)
                tpl_ctx = self.template_context_builder.build_context(vo)
                content = self.template_port.render("domain/value_object.py.j2", tpl_ctx)
                self.file_system_port.write_text(path, content)
                written_files.append(path)

            # 3. Services
            for svc in ctx.services:
                path = self.layout_planner.get_component_path("service", svc.name)
                tpl_ctx = self.template_context_builder.build_context(svc)
                content = self.template_port.render("domain/service.py.j2", tpl_ctx)
                self.file_system_port.write_text(path, content)
                written_files.append(path)

            # 4. Ports
            for port in ctx.ports:
                path = self.layout_planner.get_component_path("port", port.name)
                tpl_ctx = self.template_context_builder.build_context(port)
                content = self.template_port.render("domain/port.py.j2", tpl_ctx)
                self.file_system_port.write_text(path, content)
                written_files.append(path)

            # 5. Use Cases
            for uc in ctx.use_cases:
                path = self.layout_planner.get_component_path("use_case", uc.name)
                tpl_ctx = self.template_context_builder.build_context(uc)
                content = self.template_port.render("application/use_case.py.j2", tpl_ctx)
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
            
            path = self.layout_planner.get_component_path("adapter", adapter_data["name"])
            tpl_ctx = {
                "name": adapter_data["name"],
                "description": adapter_data.get("description", ""),
                "implements": adapter_data["implements"],
                "implements_snake": self.naming_service.to_snake(adapter_data["implements"]),
                "config": adapter_data.get("config", {}),
                "operations": port_ops
            }
            content = self.template_port.render("infrastructure/adapter.py.j2", tpl_ctx)
            self.file_system_port.write_text(path, content)
            written_files.append(path)

        return GenerateActionResult(files_written=written_files)