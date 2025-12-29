from dataclasses import dataclass, field
from typing import List

from codegen.domain_definition.domain.value_objects.attribute import Attribute
from codegen.domain_definition.domain.value_objects.blueprint import Blueprint
from codegen.domain_definition.domain.value_objects.bounded_context import (
    BoundedContext,
)
from codegen.domain_definition.domain.value_objects.meta_aggregate import MetaAggregate
from codegen.domain_definition.domain.value_objects.meta_application import (
    MetaApplication,
)
from codegen.domain_definition.domain.value_objects.meta_domain import MetaDomain
from codegen.domain_definition.domain.value_objects.meta_implementation import (
    MetaImplementation,
)
from codegen.domain_definition.domain.value_objects.meta_infrastructure import (
    MetaInfrastructure,
)
from codegen.domain_definition.domain.value_objects.meta_infrastructure_adapter import (
    MetaInfrastructureAdapter,
)
from codegen.domain_definition.domain.value_objects.meta_port import MetaPort
from codegen.domain_definition.domain.value_objects.meta_service import MetaService
from codegen.domain_definition.domain.value_objects.meta_use_case import MetaUseCase
from codegen.domain_definition.domain.value_objects.meta_value_object import (
    MetaValueObject,
)
from codegen.domain_definition.domain.value_objects.method_spec import MethodSpec
from codegen.python_gen.domain.value_objects.class_spec import ClassSpec
from codegen.python_gen.domain.value_objects.function_spec import (
    FunctionSpec,
    FunctionType,
)
from codegen.python_gen.domain.value_objects.module_spec import ModuleSpec
from codegen.python_gen.domain.value_objects.package_spec import PackageSpec
from codegen.python_gen.application.ports.blueprint_mapper_port import (
    BlueprintMapperPort,
)
from codegen.python_gen.domain.value_objects.parameter_spec import ParameterSpec
from codegen.python_gen.domain.value_objects.type_annotation_spec import (
    TypeAnnotationSpec,
)


@dataclass
class BaseTranslator:

    def _translate_attribute(
        self, attribute: Attribute, in_pydantic_model: bool
    ) -> ParameterSpec:
        return ParameterSpec.create(
            name=attribute.name,
            annotation=attribute.type,
            optional=attribute.optional,
            in_pydantic_model=in_pydantic_model,
        )

    def _translate_attributes(
        self, attributes: List[Attribute], in_pydantic_model: bool = False
    ) -> List[ParameterSpec]:
        return [self._translate_attribute(a, in_pydantic_model) for a in attributes]

    def _translate_method(
        self, method_spec: MethodSpec, is_abstract: bool = False
    ) -> FunctionSpec:
        parameter_specs = self._translate_attributes(
            method_spec.inputs, in_pydantic_model=False
        )
        if is_abstract:
            decorators = ["abstractmethod"]
        else:
            decorators = []
        return FunctionSpec(
            name=method_spec.name,
            decorators=decorators,
            parameters=parameter_specs,
            return_annotation=TypeAnnotationSpec.parse(method_spec.output.type),
            function_type=FunctionType.INSTANCE_METHOD,
        )

    def _translate_methods(
        self, method_specs: List[MethodSpec], is_abstract: bool = False
    ) -> List[FunctionSpec]:
        return [self._translate_method(m, is_abstract) for m in method_specs]

    def translate_port(self, port: MetaPort) -> ClassSpec:
        methods = self._translate_methods(port.operations, is_abstract=True)
        return ClassSpec(
            name=port.name,
            inheritance=["ABC"],
            description=port.description,
            methods=methods,
        )

    def translate_ports(self, ports: List[MetaPort]) -> PackageSpec:
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


class AppTranslator(BaseTranslator):

    def translate_application(self, application: MetaApplication) -> PackageSpec:
        pkg_use_cases = self.translate_use_cases(application.use_cases)
        pkg_ports = self.translate_ports(application.ports)
        pkg_application = PackageSpec.create(
            name="application", sub_packages=[pkg_use_cases, pkg_ports]
        )
        return pkg_application

    def translate_use_case(self, use_case: MetaUseCase) -> List[ClassSpec]:
        result: List[ClassSpec] = []
        if use_case.kind == "command":
            command_name = f"{use_case.name}Command"
            command_class = ClassSpec(
                name=command_name,
                decorators=["dataclass(frozen=True)"],
                attributes=self._translate_attributes(use_case.command.attributes),
            )
            param = ParameterSpec(
                name="cmd",
                annotation=TypeAnnotationSpec.parse(command_name),
            )
            result.append(command_class)
        elif use_case.kind == "query":
            query_name = f"{use_case.name}Query"
            query_class = ClassSpec(
                name=query_name,
                decorators=["dataclass(frozen=True)"],
                attributes=self._translate_attributes(use_case.query.attributes),
            )
            param = ParameterSpec(
                name="query",
                annotation=TypeAnnotationSpec.parse(query_name),
            )
            result.append(query_class)
        else:
            raise ValueError(f"Unknown use case kind: {use_case.kind}")

        result_name = f"{use_case.name}Result"
        result_class = ClassSpec(
            name=f"{use_case.name}Result",
            decorators=["dataclass(frozen=True)"],
            attributes=self._translate_attributes(use_case.result.attributes),
        )
        result.append(result_class)

        use_case_class = ClassSpec(
            name=use_case.name,
            description=use_case.description,
            decorators=["dataclass"],
            attributes=self._translate_attributes(use_case.attributes),
            methods=[
                FunctionSpec(
                    name="execute",
                    parameters=[param],
                    return_annotation=TypeAnnotationSpec.parse(result_name),
                    function_type=FunctionType.INSTANCE_METHOD,
                )
            ],
        )
        result.append(use_case_class)
        return result

    def translate_use_cases(self, use_cases: List[MetaUseCase]) -> PackageSpec:
        modules: List[ModuleSpec] = []
        for use_case in use_cases:
            classes = self.translate_use_case(use_case)
            module_spec = ModuleSpec.create(
                name=use_case.name,
                classes=classes,
            )
            modules.append(module_spec)
        return PackageSpec.create(
            name="use_cases",
            modules=modules,
        )


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


@dataclass
class BlueprintPythonMapper(BlueprintMapperPort):
    """Maps a blueprint to a Python package."""

    domain_translator: DomainTranslator = field(default_factory=DomainTranslator)
    app_translator: AppTranslator = field(default_factory=AppTranslator)
    infra_translator: InfraTranslator = field(default_factory=InfraTranslator)

    def to_package_spec(self, blueprint: Blueprint) -> PackageSpec:
        sub_packages = [self.translate_context(ctx) for ctx in blueprint.contexts]
        return PackageSpec.create(
            name="codegen",
            sub_packages=sub_packages,
        )

    def to_blueprint(self, package_spec: PackageSpec) -> Blueprint: ...

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

    def _collect_class_specs_in_ports(
        self, class_specs: dict[str, ClassSpec], package_spec: PackageSpec
    ) -> None:
        if package_spec.name == "ports":
            class_specs.update(package_spec.collect_class_spec())
        else:
            for pkg in package_spec.sub_packages:
                self._collect_class_specs_in_ports(class_specs, pkg)
