from dataclasses import dataclass

from codegen.code_metadata.domain.aggregates.component import Component
from codegen.code_metadata.domain.identifiers.attribute_id import AttributeId
from codegen.code_metadata.domain.identifiers.component_id import ComponentId
from codegen.code_metadata.domain.value_objects.reference_target import ReferenceTarget
from codegen.shared.domain.enums import PythonBuiltinType


@dataclass
class ReferenceResolver:
    
    dependencies: dict[str, Component]
    id_map: dict[ComponentId, Component]
    
    def resolve_target(self, target: str, source_target: ReferenceTarget | None) -> ReferenceTarget:
        if source_target is None:
            return self.resolve_target_to_component_id(target=target)
        elif source_target.component_id:
            return self.resolve_target_to_attribute_id(target=target, component_id=source_target.component_id)
            
        raise NotImplementedError(f"Unsupported source target: {source_target}")

    def resolve_target_to_component_id(self, target: str) -> ReferenceTarget:
        if target in PythonBuiltinType._value2member_map_:
            return ReferenceTarget(builtin_type=PythonBuiltinType(target))
        elif target in self.dependencies:
            return ReferenceTarget(component_id=self.dependencies[target].id)
        raise ValueError(f"Unknown target: {target}")

    def resolve_target_to_attribute_id(self, target: str, component_id: ComponentId) -> ReferenceTarget:
        component = self.id_map[component_id]
        attribute = component.find_attribute(target)
        if attribute is None:
            raise ValueError(f"attribute `{target}` not found in component `{component_id}`")
        return ReferenceTarget(attribute_id=attribute.id)

    def resolve_reference_target(self, target: ReferenceTarget, source_target: ReferenceTarget | None) -> str:
        if target.component_id:
            return self.resolve_component_id(target.component_id)
        elif target.attribute_id and source_target and source_target.component_id:
            return self.resolve_attribute_id(source_target.component_id, target.attribute_id)

        raise ValueError(f"Unsupported target: {target}, {source_target}")

    def resolve_component_id(self, component_id: ComponentId) -> str:
        return self.id_map[component_id].name

    def resolve_attribute_id(self, component_id: ComponentId, attribute_id: AttributeId) -> str:
        component = self.id_map[component_id]
        attribute = component.find_attribute_by_id(attribute_id)
        if attribute is None:
            raise ValueError(f"attribute `{attribute_id}` not found in component `{component_id}`")
        return attribute.name