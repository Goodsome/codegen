from dataclasses import dataclass
from dataclasses import field

from codegen.domain_definition.domain.value_objects.blueprint import Blueprint
from codegen.domain_definition.domain.value_objects.bounded_context import (
    BoundedContext,
)
from codegen.python_gen.application.translators import DomainTranslator, InfraTranslator
from codegen.python_gen.application.translators.app_trans import AppTranslator
from codegen.python_gen.domain.value_objects.class_spec import ClassSpec
from codegen.python_gen.domain.value_objects.package_spec import PackageSpec


@dataclass
class BlueprintTranslator:
    domain_translator: DomainTranslator = field(default_factory=DomainTranslator)
    app_translator: AppTranslator = field(default_factory=AppTranslator)
    infra_translator: InfraTranslator = field(default_factory=InfraTranslator)

    def translate_context(self, context: BoundedContext) -> PackageSpec:
        pkg_application = self.app_translator.translate_application(context.application)
        pkg_domain = self.domain_translator.translate_domain(context.domain)
        class_specs: dict[str, ClassSpec] = {}
        self._collect_class_specs_in_ports(class_specs, pkg_domain)
        self._collect_class_specs_in_ports(class_specs, pkg_application)
        pkg_infrastructure = self.infra_translator.translate_infrastructure(
            context.infrastructure,
            class_specs,
        )
        sub_packages = [pkg_domain, pkg_application, pkg_infrastructure]
        return PackageSpec.create(
            name=context.name,
            sub_packages=sub_packages,
        )

    def translate_blueprint(self, blueprint: Blueprint) -> PackageSpec:
        sub_packages = [self.translate_context(ctx) for ctx in blueprint.contexts]
        return PackageSpec.create(
            name="codegen",
            sub_packages=sub_packages,
        )

    def _collect_class_specs_in_ports(
        self, class_specs: dict[str, ClassSpec], package_spec: PackageSpec
    ) -> None:
        if package_spec.name == "ports":
            class_specs.update(package_spec.collect_class_spec())
        else:
            for pkg in package_spec.sub_packages:
                self._collect_class_specs_in_ports(class_specs, pkg)
