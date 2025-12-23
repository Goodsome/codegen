from codegen.domain.value_objects.meta_application import MetaApplication
from codegen.domain.value_objects.bounded_context import BoundedContext
from codegen.domain.value_objects.meta_domain import MetaDomain
from codegen.domain.value_objects.meta_aggregate import MetaAggregate
from codegen.domain.value_objects.meta_value_object import MetaValueObject
from codegen.domain.value_objects.meta_service import MetaService
from codegen.domain.value_objects.meta_domain_port import MetaDomainPort
from codegen.domain.value_objects.meta_use_case import MetaUseCase
from codegen.domain.value_objects.attribute import Attribute
from codegen.domain.value_objects.meta_infrastructure import MetaInfrastructure
from codegen.domain.value_objects.meta_infrastructure_adapter import (
    MetaInfrastructureAdapter,
)
from codegen.domain.value_objects.method_spec import MethodSpec
from codegen.python_gen.domain.value_objects.class_spec import ClassSpec
from codegen.domain.aggregates.blueprint import Blueprint
from codegen.python_gen.domain.value_objects.function_spec import FunctionSpec
from codegen.python_gen.domain.value_objects.module_spec import ModuleSpec
from codegen.python_gen.domain.aggregates.package_spec import PackageSpec
from codegen.python_gen.domain.value_objects.parameter_spec import ParameterSpec
from codegen.python_gen.domain.value_objects.type_annotation_spec import (
    TypeAnnotationSpec,
)


def _translate_attribute(attribute: Attribute) -> ParameterSpec:
    return ParameterSpec(
        name=attribute.name,
        annotation=TypeAnnotationSpec(name=attribute.type),
        default=attribute.default,
    )


def _translate_attributes(attributes: list[Attribute]) -> list[ParameterSpec]:
    return [_translate_attribute(a) for a in attributes]


def _translate_method(method_spec: MethodSpec) -> FunctionSpec:
    parameter_specs = _translate_attributes(method_spec.inputs)
    return FunctionSpec(
        name=method_spec.name,
        parameters=parameter_specs,
        return_annotation=TypeAnnotationSpec(name=method_spec.output.type),
    )


def _translate_methods(method_specs: list[MethodSpec]) -> list[FunctionSpec]:
    return [_translate_method(m) for m in method_specs]


def _translate_aggregate(aggregate: MetaAggregate) -> ClassSpec:
    attributes = _translate_attributes(aggregate.attributes)
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
    attributes = _translate_attributes(vo.attributes)
    return ClassSpec(
        name=vo.name,
        description=vo.description,
        inheritance=["ValueObject"],
        attributes=attributes,
    )


def _translate_service(service: MetaService) -> ClassSpec:
    methods = _translate_methods(service.operations)
    return ClassSpec(
        name=service.name,
        description=service.description,
        methods=methods,
    )


def _translate_port(port: MetaDomainPort) -> ClassSpec:
    methods = _translate_methods(port.operations)
    return ClassSpec(
        name=port.name,
        description=port.description,
        methods=methods,
    )


def _translate_use_case(use_case: MetaUseCase) -> list[ClassSpec]:
    command_name = f"{use_case.name}Command"
    command_class = ClassSpec(
        name=command_name,
        decorators=["dataclass"],
        attributes=_translate_attributes(use_case.command.attributes),
    )

    result_name = f"{use_case.name}Result"
    result_class = ClassSpec(
        name=f"{use_case.name}Result",
        decorators=["dataclass"],
        attributes=_translate_attributes(use_case.result.attributes),
    )

    use_case_class = ClassSpec(
        name=use_case.name,
        description=use_case.description,
        methods=[
            FunctionSpec(
                name="execute",
                parameters=[
                    ParameterSpec(
                        name="cmd",
                        annotation=TypeAnnotationSpec(name=command_name),
                    )
                ],
                return_annotation=TypeAnnotationSpec(name=result_name),
            )
        ],
    )
    return [command_class, result_class, use_case_class]


def _translate_adapter(adapter: MetaInfrastructureAdapter) -> ClassSpec:
    return ClassSpec(
        name=adapter.name,
        description=adapter.description,
        inheritance=[adapter.implements],
    )


def _translate_domain_aggregates(
    ctx_name: str, aggregates: list[MetaAggregate]
) -> list[ModuleSpec]:
    modules = []
    path = f"{ctx_name}/domain/aggregates"
    for aggregate in aggregates:
        class_spec = _translate_aggregate(aggregate)
        module_spec = ModuleSpec.create(
            directory=path,
            filename=aggregate.name,
            classes=[class_spec],
        )
        modules.append(module_spec)
    return modules


def _translate_domain_value_objects(
    ctx_name: str, value_objects: list[MetaValueObject]
) -> list[ModuleSpec]:
    modules = []
    path = f"{ctx_name}/domain/value_objects"
    for vo in value_objects:
        class_spec = _translate_value_object(vo)
        module_spec = ModuleSpec.create(
            directory=path,
            filename=vo.name,
            classes=[class_spec],
        )
        modules.append(module_spec)
    return modules


def _translate_domain_services(
    ctx_name: str, services: list[MetaService]
) -> list[ModuleSpec]:
    modules = []
    path = f"{ctx_name}/domain/services"
    for service in services:
        class_spec = _translate_service(service)
        module_spec = ModuleSpec.create(
            directory=path,
            filename=service.name,
            classes=[class_spec],
        )
        modules.append(module_spec)
    return modules


def _translate_domain_ports(
    ctx_name: str, ports: list[MetaDomainPort]
) -> list[ModuleSpec]:
    modules = []
    path = f"{ctx_name}/domain/ports"
    for port in ports:
        class_spec = _translate_port(port)
        module_spec = ModuleSpec.create(
            directory=path,
            filename=port.name,
            classes=[class_spec],
        )
        modules.append(module_spec)
    return modules


def _translate_domain(ctx_name: str, domain: MetaDomain) -> list[ModuleSpec]:
    modules: list[ModuleSpec] = []
    modules += _translate_domain_aggregates(ctx_name, domain.aggregates)
    modules += _translate_domain_value_objects(ctx_name, domain.value_objects)
    modules += _translate_domain_services(ctx_name, domain.services)
    modules += _translate_domain_ports(ctx_name, domain.ports)
    return modules


def _translate_application(
    ctx_name: str, application: MetaApplication
) -> list[ModuleSpec]:
    modules: list[ModuleSpec] = []
    path = f"{ctx_name}/application/use_cases"
    for use_case in application.use_cases:
        classes = _translate_use_case(use_case)
        module_spec = ModuleSpec.create(
            directory=path,
            filename=use_case.name,
            classes=classes,
        )
        modules.append(module_spec)
    return modules


def _translate_infrastructure(
    ctx_name: str, infrastructure: MetaInfrastructure
) -> list[ModuleSpec]:
    modules: list[ModuleSpec] = []
    path = f"{ctx_name}/infrastructure/adapters"
    for adapter in infrastructure.adapters:
        class_spec = _translate_adapter(adapter)
        module_spec = ModuleSpec.create(
            directory=path,
            filename=adapter.name,
            classes=[class_spec],
        )
        modules.append(module_spec)
    return modules


def _translate_context(ctx: BoundedContext) -> list[ModuleSpec]:
    modules = []
    modules += _translate_domain(ctx.name, ctx.domain)
    modules += _translate_application(ctx.name, ctx.application)
    modules += _translate_infrastructure(ctx.name, ctx.infrastructure)
    return modules


class BlueprintToPackageSpecTranslator:

    @staticmethod
    def execute(blueprint: Blueprint) -> PackageSpec:
        module_specs = []
        for ctx in blueprint.contexts:
            module_specs += _translate_context(ctx)
        return PackageSpec(
            path="",
            modules=module_specs,
        )
