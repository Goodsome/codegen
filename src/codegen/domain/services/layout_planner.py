from typing import List
from codegen.domain.aggregates.blueprint import Blueprint
from codegen.domain.value_objects.layout_strategy import LayoutStrategy

class LayoutPlanner:
    """
    Plan output paths based on the selected layout strategy and blueprint.
    """
    
    def plan_paths(self, layout: LayoutStrategy, blueprint: Blueprint) -> List[str]:
        """
        Return a list of file paths that will be generated.
        """
        paths = []
        # Support only one layout strategy for now (Standard DDD)
        if layout.name != "standard":
            # Default to standard for now as we don't have other strategies
            pass

        for ctx in blueprint.contexts:
            ctx_snake = ctx.name.lower()
            # Shared Kernel
            paths.append(f"domain/shared/models.py")
            paths.append(f"domain/shared/events.py")
            
            for agg in ctx.aggregates:
                paths.append(f"domain/aggregates/{agg.name.lower()}.py")
            
            for vo in ctx.value_objects:
                paths.append(f"domain/value_objects/{vo.name.lower()}.py")
                
            for svc in ctx.services:
                paths.append(f"domain/services/{svc.name.lower()}.py")
                
            for port in ctx.ports:
                paths.append(f"domain/ports/{port.name.lower()}.py")
                
            for uc in ctx.use_cases:
                paths.append(f"application/use_cases/{uc.name.lower()}.py")

        return list(set(paths))
    
    def get_component_path(self, component_type: str, name: str) -> str:
        """Helper to get path for a specific component."""
        mapping = {
            "aggregate": f"domain/aggregates/{name.lower()}.py",
            "value_object": f"domain/value_objects/{name.lower()}.py",
            "service": f"domain/services/{name.lower()}.py",
            "port": f"domain/ports/{name.lower()}.py",
            "use_case": f"application/use_cases/{name.lower()}.py",
            "adapter": f"infrastructure/adapters/{name.lower()}.py"
        }
        return mapping.get(component_type, f"unknown/{name.lower()}.py")
    