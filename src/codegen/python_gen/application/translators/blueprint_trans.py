from dataclasses import field
from codegen.domain_definition.domain.value_objects.blueprint import Blueprint
from codegen.python_gen.domain.value_objects.package_spec import PackageSpec
from codegen.domain_definition.domain.value_objects.bounded_context import (
    BoundedContext,
)
from dataclasses import dataclass

from codegen.python_gen.application.translators import DomainTranslator, InfraTranslator
from codegen.python_gen.application.translators.app_trans import AppTranslator


@dataclass
class BlueprintTranslator:
    domain_translator: DomainTranslator = field(default_factory=DomainTranslator)
    app_translator: AppTranslator = field(default_factory=AppTranslator)
    infra_translator: InfraTranslator = field(default_factory=InfraTranslator)

    def translate_context(self, context: BoundedContext) -> PackageSpec:
        sub_packages = [
            self.domain_translator.translate_domain(context.domain),
            self.app_translator.translate_application(context.application),
            self.infra_translator.translate_infrastructure(context.infrastructure),
        ]
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
