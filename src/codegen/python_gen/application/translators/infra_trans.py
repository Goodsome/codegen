from typing import List

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
        self, infrastructure: MetaInfrastructure
    ) -> PackageSpec:
        sub_package = self.translate_adapters(infrastructure.adapters)
        return PackageSpec.create(
            name="infrastructure",
            sub_packages=[sub_package],
        )

    def translate_adapter(self, adapter: MetaInfrastructureAdapter) -> ClassSpec:
        return ClassSpec(
            name=adapter.name,
            description=adapter.description,
            inheritance=[adapter.implements],
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
