"""Tests for InterfaceMapper HTTP import generation."""

import pytest
from codegen.orchestration.domain.services.interface_mapper import InterfaceMapper
from codegen.domain_definition.domain.value_objects.interface_spec import InterfaceSpec
from codegen.domain_definition.domain.value_objects.http_interface_spec import (
    HttpInterfaceSpec,
)
from codegen.domain_definition.domain.value_objects.http_endpoint_spec import (
    HttpEndpointSpec,
)
from codegen.domain_definition.domain.value_objects.use_case_spec import UseCaseSpec
from codegen.domain_definition.domain.enums import UseCaseKind


class TestInterfaceMapperHttpImports:
    """Test HTTP interface import statement generation."""

    @pytest.fixture
    def mapper(self):
        return InterfaceMapper()

    @pytest.fixture
    def use_cases(self):
        return [
            UseCaseSpec(name="CreateUser", kind=UseCaseKind.COMMAND),
        ]

    def test_no_manual_container_import(self, mapper, use_cases):
        """Container import should have full package path with project_name prefix."""
        http_spec = HttpInterfaceSpec(
            endpoints=[
                HttpEndpointSpec(
                    path="/users",
                    method="POST",
                    use_case="CreateUser",
                    description="Create a new user",
                ),
            ]
        )
        interfaces = InterfaceSpec(http=http_spec)

        pkg = mapper.to_package_spec(interfaces, "Shared", use_cases, project_name="my_project")
        http_pkg = pkg.sub_packages[0]
        endpoint_module = http_pkg.modules[0]

        # Container import should be present with full package path
        container_imports = [
            imp for imp in endpoint_module.imports
            if "Container" in str(imp.names)
        ]
        assert len(container_imports) == 1, "Should manually import Container"
        assert container_imports[0].module == "my_project.shared.container", \
            f"Expected 'my_project.shared.container', got '{container_imports[0].module}'"

    def test_no_manual_use_case_import(self, mapper, use_cases):
        """Should not manually add UseCase imports - let DependencyResolver handle it."""
        http_spec = HttpInterfaceSpec(
            endpoints=[
                HttpEndpointSpec(
                    path="/users",
                    method="POST",
                    use_case="CreateUser",
                    description="Create a new user",
                ),
            ]
        )
        interfaces = InterfaceSpec(http=http_spec)

        pkg = mapper.to_package_spec(interfaces, "Shared", use_cases, project_name="my_project")
        http_pkg = pkg.sub_packages[0]
        endpoint_module = http_pkg.modules[0]

        # Should not have manually added use_case imports
        use_case_imports = [
            imp for imp in endpoint_module.imports
            if "CreateUser" in str(imp.names) or "CreateUserCommand" in str(imp.names)
        ]
        assert len(use_case_imports) == 0, "Should not manually import UseCase classes"

    def test_only_external_dependencies_in_imports(self, mapper, use_cases):
        """Only external dependencies (like fastapi) and Container should be in manual imports."""
        http_spec = HttpInterfaceSpec(
            endpoints=[
                HttpEndpointSpec(
                    path="/users",
                    method="POST",
                    use_case="CreateUser",
                    description="Create a new user",
                ),
            ]
        )
        interfaces = InterfaceSpec(http=http_spec)

        pkg = mapper.to_package_spec(interfaces, "Shared", use_cases, project_name="my_project")
        http_pkg = pkg.sub_packages[0]
        endpoint_module = http_pkg.modules[0]

        # External dependencies and Container should be in imports
        # UseCase classes should be resolved by DependencyResolver
        allowed_modules = {"fastapi", "my_project.shared.container"}  # external + Container with project prefix
        for imp in endpoint_module.imports:
            assert imp.module in allowed_modules, (
                f"Import from '{imp.module}' should be resolved by DependencyResolver, "
                f"not manually added"
            )

    def test_function_has_correct_return_annotation(self, mapper, use_cases):
        """Function should have correct return annotation for DependencyResolver."""
        http_spec = HttpInterfaceSpec(
            endpoints=[
                HttpEndpointSpec(
                    path="/users",
                    method="POST",
                    use_case="CreateUser",
                    description="Create a new user",
                ),
            ]
        )
        interfaces = InterfaceSpec(http=http_spec)

        pkg = mapper.to_package_spec(interfaces, "Shared", use_cases, project_name="my_project")
        http_pkg = pkg.sub_packages[0]
        endpoint_module = http_pkg.modules[0]
        func = endpoint_module.functions[0]

        # Return annotation should reference CreateUserResult
        assert func.return_annotation.name == "CreateUserResult"

    def test_function_has_correct_parameter_type(self, mapper, use_cases):
        """Function parameter should have correct type for DependencyResolver."""
        http_spec = HttpInterfaceSpec(
            endpoints=[
                HttpEndpointSpec(
                    path="/users",
                    method="POST",
                    use_case="CreateUser",
                    description="Create a new user",
                ),
            ]
        )
        interfaces = InterfaceSpec(http=http_spec)

        pkg = mapper.to_package_spec(interfaces, "Shared", use_cases, project_name="my_project")
        http_pkg = pkg.sub_packages[0]
        endpoint_module = http_pkg.modules[0]
        func = endpoint_module.functions[0]

        # Parameter type should reference CreateUserCommand
        assert func.parameters[0].type_spec.name == "CreateUserCommand"