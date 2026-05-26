from dataclasses import dataclass, field
from typing import override
from codegen.code_metadata.domain.aggregates.component import ClassComponent
from codegen.code_metadata.domain.entities.attribute import Attribute
from codegen.code_metadata.domain.enums import ComponentType
from codegen.code_metadata.domain.enums.architecture_layer import ArchitectureLayer
from codegen.code_metadata.domain.identifiers.component_id import ComponentId
from codegen.code_metadata.domain.ports.component_collection import ComponentCollection


@dataclass
class MemoryComponentCollection(ComponentCollection):

    store: dict[tuple[str, str], ClassComponent]
    components: dict[ComponentId, ClassComponent]

    need_saves: dict[tuple[str, str], ClassComponent] = field(default_factory=dict)

    def update(self, component: ClassComponent) -> None:
        self.store[(component.context, component.name)] = component
        self.need_saves[(component.context, component.name)] = component
        self.components[component.id] = component

    @override
    def get_or_create_component(self, context: str, name: str) -> ClassComponent:
        component = self.store.get((context, name))
        if component:
            return component

        component = ClassComponent(
            id=ComponentId.create(),
            context=context,
            name=name,
            type=ComponentType.EXTERNAL,
            layer=ArchitectureLayer.UNKNOWN,
            description=""
        )
        self.update(component)
        return component

    @override
    def get_or_create_attribute(self, component_id: ComponentId, name: str) -> Attribute:
        component = self.components[component_id]
        attribute = component.find_attribute(name)
        if attribute:
            return attribute
        attribute = component.add_attribute(name)
        self.need_saves[(component.context, component.name)] = component
        return attribute