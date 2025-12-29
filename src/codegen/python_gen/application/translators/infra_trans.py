from codegen.python_gen.domain.value_objects.function_spec import FunctionSpec
from typing import List

from codegen.domain_definition.domain.value_objects.meta_implementation import (
    MetaImplementation,
)
from codegen.domain_definition.domain.value_objects.meta_infrastructure import (
    MetaInfrastructure,
)
from codegen.domain_definition.domain.value_objects.meta_infrastructure_adapter import (
    MetaInfrastructureAdapter,
)
from codegen.python_gen.domain.value_objects.class_spec import ClassSpec
from codegen.python_gen.domain.value_objects.module_spec import ModuleSpec
from codegen.python_gen.domain.value_objects.package_spec import PackageSpec
from .base import BaseTranslator


class InfraTranslator(BaseTranslator):

    def translate_infrastructure(
        self,
        infrastructure: MetaInfrastructure,
        ports_class_specs: dict[str, ClassSpec],
    ) -> PackageSpec:
        pkg_adapters = self.translate_adapters(infrastructure.adapters)
        pkg_acl = self.translate_acl(infrastructure.acl, ports_class_specs)
        return PackageSpec.create(
            name="infrastructure",
            sub_packages=[pkg_adapters, pkg_acl],
        )

    def translate_adapter(self, adapter: MetaInfrastructureAdapter) -> ClassSpec:
        return ClassSpec(
            name=adapter.name,
            description=adapter.description,
            inheritance=[adapter.implements],
        )

    def translate_acl(
        self,
        acl: list[MetaImplementation],
        ports_class_specs: dict[str, ClassSpec],
    ) -> PackageSpec:
        modules = [self.translate_implementation(i, ports_class_specs) for i in acl]
        return PackageSpec.create(
            name="acl",
            modules=modules,
        )

    def translate_implementation(
        self,
        implementation: MetaImplementation,
        ports_class_specs: dict[str, ClassSpec],
    ) -> ModuleSpec:
        if implementation.implements not in ports_class_specs:
            raise ValueError(
                f"Could not find port class spec for {implementation.implements}"
            )
        port_cls = ports_class_specs[implementation.implements]
        methods = [self.remove_abstract_method(f) for f in port_cls.methods]
        main_cls = ClassSpec(
            name=implementation.name,
            description=implementation.description,
            inheritance=[implementation.implements],
            attributes=port_cls.attributes,
            methods=methods,
        )
        return ModuleSpec.create(
            name=implementation.name,
            classes=[main_cls],
        )

    def remove_abstract_method(self, function_spec: FunctionSpec) -> FunctionSpec:
        decorators = [d for d in function_spec.decorators if d != "abstractmethod"]
        return FunctionSpec.create(
            name=function_spec.name,
            decorators=decorators,
            parameters=function_spec.parameters,
            suite=function_spec.suite,
            return_annotation=function_spec.return_annotation,
            function_type=function_spec.function_type,
        )

    def translate_adapters(
        self, adapters: List[MetaInfrastructureAdapter]
    ) -> PackageSpec:
        modules: List[ModuleSpec] = []
        for adapter in adapters:
            class_spec = self.translate_adapter(adapter)
            module_spec = ModuleSpec.create(
                name=adapter.name,
                classes=[class_spec],
            )
            modules.append(module_spec)
        return PackageSpec.create(
            name="adapters",
            modules=modules,
        )
