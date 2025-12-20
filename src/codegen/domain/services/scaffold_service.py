from dataclasses import dataclass
from pathlib import Path

from codegen.domain.aggregates.blueprint import Blueprint
from codegen.domain.services.naming_service import NamingService
from codegen.domain.services.template_context_builder import TemplateContextBuilder

from codegen.domain.value_objects.render_task import RenderTask


@dataclass
class ScaffoldService:
    """
    Converts the Blueprint into a flat list of render tasks.
    """

    naming_service: NamingService = NamingService()
    template_context_builder: TemplateContextBuilder = TemplateContextBuilder()

    def plan_generation(self, blueprint: Blueprint) -> list[RenderTask]:
        self.template_context_builder.build_registry(blueprint)
        render_tasks: list[RenderTask] = []
        all_ports = [p for ctx in blueprint.contexts for p in ctx.domain.ports]
        for ctx in blueprint.contexts:
            # 1. Aggregates
            for agg in ctx.domain.aggregates:
                path = self.get_component_path("aggregate", agg.name)
                tpl_ctx = self.template_context_builder.build_context(agg)
                render_tasks.append(
                    RenderTask(
                        target_path=path,
                        template_name="domain/aggregate.j2",
                        context_data=tpl_ctx,
                    )
                )

            # 2. Value Objects
            for vo in ctx.domain.value_objects:
                path = self.get_component_path("value_object", vo.name)
                tpl_ctx = self.template_context_builder.build_context(vo)
                render_tasks.append(
                    RenderTask(
                        target_path=path,
                        template_name="domain/value_object.j2",
                        context_data=tpl_ctx,
                    )
                )

            # 3. Services
            for svc in ctx.domain.services:
                path = self.get_component_path("service", svc.name)
                tpl_ctx = self.template_context_builder.build_context(svc)
                render_tasks.append(
                    RenderTask(
                        target_path=path,
                        template_name="domain/service.j2",
                        context_data=tpl_ctx,
                    )
                )

            # 4. Ports
            for port in ctx.domain.ports:
                path = self.get_component_path("port", port.name)
                tpl_ctx = self.template_context_builder.build_context(port)
                render_tasks.append(
                    RenderTask(
                        target_path=path,
                        template_name="domain/port.j2",
                        context_data=tpl_ctx,
                    )
                )

            # 5. Use Cases
            for uc in ctx.application.use_cases:
                path = self.get_component_path("use_case", uc.name)
                tpl_ctx = self.template_context_builder.build_context(uc)
                render_tasks.append(
                    RenderTask(
                        target_path=path,
                        template_name="application/use_case.j2",
                        context_data=tpl_ctx,
                    )
                )

            # 6. Infrastructure Adapters
            for infra_adapter in ctx.infrastructure.adapters:
                path = self.get_component_path("adapter", infra_adapter.name)
                adapter_data = infra_adapter
                port_ops = []
                for p in all_ports:
                    if p.name == adapter_data.implements:
                        port_ops = p.operations
                        break
                tpl_ctx = {
                    "name": adapter_data.name,
                    "description": adapter_data.description,
                    "implements": adapter_data.implements,
                    "implements_snake": self.naming_service.to_snake(
                        adapter_data.implements
                    ),
                    "config": adapter_data.config,
                    "operations": port_ops,
                }
                render_tasks.append(
                    RenderTask(
                        target_path=path,
                        template_name="infrastructure/adapter.j2",
                        context_data=tpl_ctx,
                    )
                )

        return render_tasks

    def plan_paths(self, blueprint: Blueprint) -> list[Path]:
        """
        Return a list of file paths that will be generated.
        """
        paths = []

        for ctx in blueprint.contexts:
            # Shared Kernel
            paths.append(f"domain/shared/models.py")
            paths.append(f"domain/shared/events.py")

            for agg in ctx.domain.aggregates:
                paths.append(f"domain/aggregates/{agg.name.lower()}.py")

            for vo in ctx.domain.value_objects:
                paths.append(f"domain/value_objects/{vo.name.lower()}.py")

            for svc in ctx.domain.services:
                paths.append(f"domain/services/{svc.name.lower()}.py")

            for port in ctx.domain.ports:
                paths.append(f"domain/ports/{port.name.lower()}.py")

            for uc in ctx.use_cases:
                paths.append(f"application/use_cases/{uc.name.lower()}.py")

        return list(set(paths))

    def get_component_path(self, component_type: str, name: str) -> str:
        """
        get path for a specific component
        """
        mapping = {
            "aggregate": f"domain/aggregates/{name.lower()}.py",
            "value_object": f"domain/value_objects/{name.lower()}.py",
            "service": f"domain/services/{name.lower()}.py",
            "port": f"domain/ports/{name.lower()}.py",
            "use_case": f"application/use_cases/{name.lower()}.py",
            "adapter": f"infrastructure/adapters/{name.lower()}.py",
        }
        return mapping.get(component_type, f"unknown/{name.lower()}.py")
