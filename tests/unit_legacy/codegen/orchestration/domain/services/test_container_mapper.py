import pytest

from codegen.domain_definition.domain.enums import UseCaseKind
from codegen.domain_definition.domain.value_objects.application_spec import (
    ApplicationSpec,
)
from codegen.domain_definition.domain.value_objects.attribute_spec import AttributeSpec
from codegen.domain_definition.domain.value_objects.bounded_context import (
    BoundedContext,
)
from codegen.domain_definition.domain.value_objects.container_spec import ContainerSpec
from codegen.domain_definition.domain.value_objects.port_binding import PortBinding
from codegen.domain_definition.domain.value_objects.use_case_spec import UseCaseSpec
from codegen.orchestration.domain.services.container_mapper import ContainerMapper
from codegen.python_gen.domain.enums import AssignmentFlavor
from codegen.python_gen.domain.value_objects.assignment_spec import AssignmentSpec


@pytest.fixture
def mapper() -> ContainerMapper:
    return ContainerMapper()


@pytest.fixture
def sample_context() -> BoundedContext:
    use_case = UseCaseSpec.create(
        name="CreateUserUseCase",
        kind=UseCaseKind.COMMAND,
        dependencies=[
            AttributeSpec.create(name="user_repository", type="UserRepository")
        ],
    )
    application = ApplicationSpec(use_cases=[use_case])

    container_spec = ContainerSpec(
        bindings=[
            PortBinding(port="UserRepository", implementation="PostgresUserRepository"),
            PortBinding(port="EmailService", implementation="SmtpEmailService"),
        ]
    )

    return BoundedContext.create(
        name="UserManagement",
        application=application,
        container=container_spec,
    )


def test_maps_container_bindings_to_providers(
    mapper: ContainerMapper, sample_context: BoundedContext
):
    class_spec = mapper.to_class_spec(sample_context.container, sample_context)

    mapper_vars = {attr.name: attr for attr in class_spec.attributes}

    # Should map the implementations into Factory assignments
    assert "postgres_user_repository" in mapper_vars
    repo_provider = mapper_vars["postgres_user_repository"]
    assert repo_provider.assignment.flavor == AssignmentFlavor.CALL
    assert repo_provider.assignment.call.callee == "Factory"
    assert (
        repo_provider.assignment.call.args[0].reference.name == "PostgresUserRepository"
    )

    assert "smtp_email_service" in mapper_vars
    email_provider = mapper_vars["smtp_email_service"]
    assert email_provider.assignment.flavor == AssignmentFlavor.CALL
    assert email_provider.assignment.call.callee == "Factory"
    assert email_provider.assignment.call.args[0].reference.name == "SmtpEmailService"


def test_maps_use_cases_to_providers(
    mapper: ContainerMapper, sample_context: BoundedContext
):
    class_spec = mapper.to_class_spec(sample_context.container, sample_context)

    mapper_vars = {attr.name: attr for attr in class_spec.attributes}

    # Should map use cases
    assert "create_user_use_case" in mapper_vars
    use_case_provider = mapper_vars["create_user_use_case"]

    assert use_case_provider.assignment.flavor == AssignmentFlavor.CALL
    assert use_case_provider.assignment.call.callee == "Factory"
    assert (
        use_case_provider.assignment.call.args[0].reference.name == "CreateUserUseCase"
    )

    # Make sure kwargs are populated properly according to dependencies
    kwargs = use_case_provider.assignment.call.kwargs
    assert "user_repository" in kwargs

    # The value of the kwarg should point to the provider
    arg_assignment = kwargs["user_repository"]
    assert arg_assignment.flavor == AssignmentFlavor.SYMBOL
    assert arg_assignment.reference.name == "postgres_user_repository"

