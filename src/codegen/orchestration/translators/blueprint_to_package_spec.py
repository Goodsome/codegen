from codegen.domain_definition.domain.value_objects.meta_application import (
    MetaApplication,
)
from codegen.domain_definition.domain.value_objects.bounded_context import (
    BoundedContext,
)
from codegen.domain_definition.domain.value_objects.meta_domain import MetaDomain
from codegen.domain_definition.domain.value_objects.meta_aggregate import MetaAggregate
from codegen.domain_definition.domain.value_objects.meta_value_object import (
    MetaValueObject,
)
from codegen.domain_definition.domain.value_objects.meta_service import MetaService
from codegen.domain_definition.domain.value_objects.meta_domain_port import (
    MetaDomainPort,
)
from codegen.domain_definition.domain.value_objects.meta_use_case import MetaUseCase
from codegen.domain_definition.domain.value_objects.attribute import Attribute
from codegen.domain_definition.domain.value_objects.meta_infrastructure import (
    MetaInfrastructure,
)
from codegen.domain_definition.domain.value_objects.meta_infrastructure_adapter import (
    MetaInfrastructureAdapter,
)
from codegen.domain_definition.domain.value_objects.method_spec import MethodSpec
from codegen.domain_definition.domain.value_objects.blueprint import Blueprint
from codegen.python_gen.domain.value_objects.function_spec import (
    FunctionSpec,
    FunctionType,
)
from codegen.python_gen.domain.value_objects.class_spec import ClassSpec
from codegen.python_gen.domain.value_objects.module_spec import ModuleSpec
from codegen.python_gen.domain.value_objects.package_spec import PackageSpec
from codegen.python_gen.domain.value_objects.parameter_spec import ParameterSpec
from codegen.python_gen.domain.value_objects.type_annotation_spec import (
    TypeAnnotationSpec,
)


def _translate_attribute(
    attribute: Attribute, in_pydantic_model: bool
) -> ParameterSpec:
    return ParameterSpec.create(
        name=attribute.name,
        annotation=attribute.type,
        optional=attribute.optional,
        in_pydantic_model=in_pydantic_model,
    )


def _translate_attributes(
    attributes: list[Attribute], in_pydantic_model: bool = False
) -> list[ParameterSpec]:
    return [_translate_attribute(a, in_pydantic_model) for a in attributes]


def _translate_method(
    method_spec: MethodSpec, is_abstract: bool = False
) -> FunctionSpec:
    parameter_specs = _translate_attributes(method_spec.inputs, in_pydantic_model=False)
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
    method_specs: list[MethodSpec], is_abstract: bool = False
) -> list[FunctionSpec]:
    return [_translate_method(m, is_abstract) for m in method_specs]


def _translate_aggregate(aggregate: MetaAggregate) -> ClassSpec:
    attributes = _translate_attributes(aggregate.attributes, in_pydantic_model=True)
    methods = _translate_methods(aggregate.behaviors)
    class_spec = ClassSpec(
        name=aggregate.name,
        description=aggregate.description,
        inheritance=["AggregateRoot"],
        attributes=attributes,
        methods=methods,
    )
    return class_spec


def _translate_value_object(vo: MetaValueObject) -> ClassSpec:
    attributes = _translate_attributes(
        vo.attributes,
        in_pydantic_model=True,
    )
    return ClassSpec(
        name=vo.name,
        description=vo.description,
        inheritance=["ValueObject"],
        attributes=attributes,
    )


def _translate_service(service: MetaService) -> ClassSpec:
    methods = _translate_methods(service.operations)
    attributes = _translate_attributes(service.attributes)
    return ClassSpec(
        name=service.name,
        description=service.description,
        decorators=["dataclass"],
        attributes=attributes,
        methods=methods,
    )


def _translate_port(port: MetaDomainPort) -> ClassSpec:
    methods = _translate_methods(port.operations, is_abstract=True)
    return ClassSpec(
        name=port.name,
        inheritance=["ABC"],
        description=port.description,
        methods=methods,
    )


def _translate_use_case(use_case: MetaUseCase) -> list[ClassSpec]:
    result: list[ClassSpec] = []
    if use_case.kind == "command":
        command_name = f"{use_case.name}Command"
        command_class = ClassSpec(
            name=command_name,
            decorators=["dataclass(frozen=True)"],
            attributes=_translate_attributes(use_case.command.attributes),
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
            attributes=_translate_attributes(use_case.query.attributes),
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
        attributes=_translate_attributes(use_case.result.attributes),
    )
    result.append(result_class)

    use_case_class = ClassSpec(
        name=use_case.name,
        description=use_case.description,
        decorators=["dataclass"],
        attributes=_translate_attributes(use_case.attributes),
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


def _translate_adapter(adapter: MetaInfrastructureAdapter) -> ClassSpec:
    return ClassSpec(
        name=adapter.name,
        description=adapter.description,
        inheritance=[adapter.implements],
    )


def _translate_domain_aggregates(aggregates: list[MetaAggregate]) -> PackageSpec:
    modules = []
    for aggregate in aggregates:
        class_spec = _translate_aggregate(aggregate)
        module_spec = ModuleSpec.create(
            name=aggregate.name,
            classes=[class_spec],
        )
        modules.append(module_spec)
    return PackageSpec.create(
        name="aggregates",
        modules=modules,
    )


def _translate_domain_value_objects(
    value_objects: list[MetaValueObject],
) -> PackageSpec:
    modules = []
    for vo in value_objects:
        class_spec = _translate_value_object(vo)
        module_spec = ModuleSpec.create(
            name=vo.name,
            classes=[class_spec],
        )
        modules.append(module_spec)
    return PackageSpec.create(
        name="value_objects",
        modules=modules,
    )


def _translate_domain_services(services: list[MetaService]) -> PackageSpec:
    modules = []
    for service in services:
        class_spec = _translate_service(service)
        module_spec = ModuleSpec.create(
            name=service.name,
            classes=[class_spec],
        )
        modules.append(module_spec)
    return PackageSpec.create(
        name="services",
        modules=modules,
    )


def _translate_domain_ports(ports: list[MetaDomainPort]) -> PackageSpec:
    modules = []
    for port in ports:
        class_spec = _translate_port(port)
        module_spec = ModuleSpec.create(
            name=port.name,
            classes=[class_spec],
        )
        modules.append(module_spec)
    return PackageSpec.create(
        name="ports",
        modules=modules,
    )


def _translate_domain(domain: MetaDomain) -> PackageSpec:
    packages: list[PackageSpec] = [
        _translate_domain_aggregates(domain.aggregates),
        _translate_domain_value_objects(domain.value_objects),
        _translate_domain_services(domain.services),
        _translate_domain_ports(domain.ports),
    ]
    return PackageSpec.create(
        name="domain",
        sub_packages=packages,
    )


def _translate_application_use_cases(use_cases: list[MetaUseCase]) -> PackageSpec:
    modules: list[ModuleSpec] = []
    for use_case in use_cases:
        classes = _translate_use_case(use_case)
        module_spec = ModuleSpec.create(
            name=use_case.name,
            classes=classes,
        )
        modules.append(module_spec)
    return PackageSpec.create(
        name="use_cases",
        modules=modules,
    )


def _translate_application(application: MetaApplication) -> PackageSpec:
    packages: list[PackageSpec] = [
        _translate_application_use_cases(application.use_cases)
    ]
    return PackageSpec.create(
        name="application",
        sub_packages=packages,
    )


def _translate_infrastructure_adapters(
    adapters: list[MetaInfrastructureAdapter],
) -> PackageSpec:
    modules: list[ModuleSpec] = []
    for adapter in adapters:
        class_spec = _translate_adapter(adapter)
        module_spec = ModuleSpec.create(
            name=adapter.name,
            classes=[class_spec],
        )
        modules.append(module_spec)
    return PackageSpec.create(
        name="adapters",
        modules=modules,
    )


def _translate_infrastructure(infrastructure: MetaInfrastructure) -> PackageSpec:
    packages: list[PackageSpec] = [
        _translate_infrastructure_adapters(infrastructure.adapters)
    ]
    return PackageSpec.create(
        name="infrastructure",
        sub_packages=packages,
    )


def _translate_context(ctx: BoundedContext) -> PackageSpec:
    packages: list[PackageSpec] = [
        _translate_infrastructure(ctx.infrastructure),
        _translate_application(ctx.application),
        _translate_domain(ctx.domain),
    ]

    return PackageSpec.create(
        name=ctx.name,
        sub_packages=packages,
    )


class BlueprintToPackageSpecTranslator:

    @staticmethod
    def execute(blueprint: Blueprint) -> PackageSpec:
        package_specs: list[PackageSpec] = []
        for ctx in blueprint.contexts:
            package_specs.append(_translate_context(ctx))
        return PackageSpec.create(
            name="codegen",
            sub_packages=package_specs,
        )
