from typing import List
from codegen.domain_definition.domain.value_objects.meta_aggregate import MetaAggregate
from codegen.domain_definition.domain.value_objects.meta_domain import MetaDomain
from codegen.domain_definition.domain.value_objects.meta_value_object import (
    MetaValueObject,
)
from codegen.domain_definition.domain.value_objects.meta_service import MetaService
from codegen.domain_definition.domain.value_objects.meta_domain_port import (
    MetaDomainPort,
)
from codegen.python_gen.domain.value_objects.class_spec import ClassSpec
from codegen.python_gen.domain.value_objects.module_spec import ModuleSpec
from codegen.python_gen.domain.value_objects.package_spec import PackageSpec
from .base import BaseTranslator


class DomainTranslator(BaseTranslator):

    def translate_domain(self, domain: MetaDomain) -> PackageSpec:
        sub_packages = [
            self.translate_aggregates(domain.aggregates),
            self.translate_value_objects(domain.value_objects),
            self.translate_services(domain.services),
            self.translate_ports(domain.ports),
        ]
        return PackageSpec.create(
            name="domain",
            sub_packages=sub_packages,
        )

    def translate_aggregate(self, aggregate: MetaAggregate) -> ClassSpec:
        attributes = self._translate_attributes(
            aggregate.attributes, in_pydantic_model=True
        )
        methods = self._translate_methods(aggregate.behaviors)
        return ClassSpec(
            name=aggregate.name,
            description=aggregate.description,
            inheritance=["AggregateRoot"],
            attributes=attributes,
            methods=methods,
        )

    def translate_value_object(self, vo: MetaValueObject) -> ClassSpec:
        attributes = self._translate_attributes(vo.attributes, in_pydantic_model=True)
        return ClassSpec(
            name=vo.name,
            description=vo.description,
            inheritance=["ValueObject"],
            attributes=attributes,
        )

    def translate_service(self, service: MetaService) -> ClassSpec:
        methods = self._translate_methods(service.operations)
        attributes = self._translate_attributes(service.attributes)
        return ClassSpec(
            name=service.name,
            description=service.description,
            decorators=["dataclass"],
            attributes=attributes,
            methods=methods,
        )

    def translate_port(self, port: MetaDomainPort) -> ClassSpec:
        methods = self._translate_methods(port.operations, is_abstract=True)
        return ClassSpec(
            name=port.name,
            inheritance=["ABC"],
            description=port.description,
            methods=methods,
        )

    def translate_aggregates(self, aggregates: List[MetaAggregate]) -> PackageSpec:
        modules = []
        for aggregate in aggregates:
            class_spec = self.translate_aggregate(aggregate)
            module_spec = ModuleSpec.create(
                name=aggregate.name,
                classes=[class_spec],
            )
            modules.append(module_spec)
        return PackageSpec.create(
            name="aggregates",
            modules=modules,
        )

    def translate_value_objects(
        self, value_objects: List[MetaValueObject]
    ) -> PackageSpec:
        modules = []
        for vo in value_objects:
            class_spec = self.translate_value_object(vo)
            module_spec = ModuleSpec.create(
                name=vo.name,
                classes=[class_spec],
            )
            modules.append(module_spec)
        return PackageSpec.create(
            name="value_objects",
            modules=modules,
        )

    def translate_services(self, services: List[MetaService]) -> PackageSpec:
        modules = []
        for service in services:
            class_spec = self.translate_service(service)
            module_spec = ModuleSpec.create(
                name=service.name,
                classes=[class_spec],
            )
            modules.append(module_spec)
        return PackageSpec.create(
            name="services",
            modules=modules,
        )

    def translate_ports(self, ports: List[MetaDomainPort]) -> PackageSpec:
        modules = []
        for port in ports:
            class_spec = self.translate_port(port)
            module_spec = ModuleSpec.create(
                name=port.name,
                classes=[class_spec],
            )
            modules.append(module_spec)
        return PackageSpec.create(
            name="ports",
            modules=modules,
        )
