"""Tests for InterfaceMapper HTTP interface generation."""

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


class TestInterfaceMapperHttpNaming:
    """Test HTTP interface file naming and import generation."""

    @pytest.fixture
    def mapper(self):
        return InterfaceMapper()

    @pytest.fixture
    def use_cases(self):
        return [
            UseCaseSpec(name="CreateUser", kind=UseCaseKind.COMMAND),
            UseCaseSpec(name="GetUser", kind=UseCaseKind.QUERY),
            UseCaseSpec(name="UpdateUser", kind=UseCaseKind.COMMAND),
            UseCaseSpec(name="DeleteUser", kind=UseCaseKind.COMMAND),
        ]

    # ============ Module Naming Tests ============

    def test_module_name_from_use_case_not_path(self, mapper, use_cases):
        """Module name should be derived from use_case, not HTTP path."""
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

        pkg = mapper.to_package_spec(interfaces, "Shared", use_cases)
        http_pkg = pkg.sub_packages[0]

        # Module name should be create_user (from CreateUser use case), not users (from path)
        assert len(http_pkg.modules) == 2  # 1 endpoint module + __init__
        assert http_pkg.modules[0].name == "create_user"

    def test_module_name_for_path_with_parameters(self, mapper, use_cases):
        """Module name should not contain path parameter placeholders."""
        http_spec = HttpInterfaceSpec(
            endpoints=[
                HttpEndpointSpec(
                    path="/users/{user_id}",
                    method="GET",
                    use_case="GetUser",
                    description="Get user by ID",
                ),
            ]
        )
        interfaces = InterfaceSpec(http=http_spec)

        pkg = mapper.to_package_spec(interfaces, "Shared", use_cases)
        http_pkg = pkg.sub_packages[0]

        # Module name should be get_user, NOT users_{user_id}
        assert http_pkg.modules[0].name == "get_user"

    def test_multiple_endpoints_same_path_different_use_cases(
        self, mapper, use_cases
    ):
        """Multiple endpoints with same path but different use cases get separate modules."""
        http_spec = HttpInterfaceSpec(
            endpoints=[
                HttpEndpointSpec(
                    path="/users/{user_id}",
                    method="GET",
                    use_case="GetUser",
                    description="Get user by ID",
                ),
                HttpEndpointSpec(
                    path="/users/{user_id}",
                    method="PUT",
                    use_case="UpdateUser",
                    description="Update user",
                ),
                HttpEndpointSpec(
                    path="/users/{user_id}",
                    method="DELETE",
                    use_case="DeleteUser",
                    description="Delete user",
                ),
            ]
        )
        interfaces = InterfaceSpec(http=http_spec)

        pkg = mapper.to_package_spec(interfaces, "Shared", use_cases)
        http_pkg = pkg.sub_packages[0]

        # Should have 3 endpoint modules + __init__
        assert len(http_pkg.modules) == 4
        module_names = [m.name for m in http_pkg.modules if m.name != "__init__"]
        assert set(module_names) == {"get_user", "update_user", "delete_user"}

    # ============ Function Naming Tests ============

    def test_function_name_from_use_case(self, mapper, use_cases):
        """Function name should be derived from use_case."""
        http_spec = HttpInterfaceSpec(
            endpoints=[
                HttpEndpointSpec(
                    path="/users/{user_id}",
                    method="GET",
                    use_case="GetUser",
                    description="Get user by ID",
                ),
            ]
        )
        interfaces = InterfaceSpec(http=http_spec)

        pkg = mapper.to_package_spec(interfaces, "Shared", use_cases)
        http_pkg = pkg.sub_packages[0]
        endpoint_module = http_pkg.modules[0]

        # Function name should be get_user
        assert endpoint_module.functions[0].name == "get_user"

    # ============ __init__.py Import Tests ============

    def test_init_module_valid_import_names(self, mapper, use_cases):
        """__init__.py should have valid Python import names (no curly braces)."""
        http_spec = HttpInterfaceSpec(
            endpoints=[
                HttpEndpointSpec(
                    path="/users/{user_id}",
                    method="GET",
                    use_case="GetUser",
                    description="Get user by ID",
                ),
            ]
        )
        interfaces = InterfaceSpec(http=http_spec)

        pkg = mapper.to_package_spec(interfaces, "Shared", use_cases)
        http_pkg = pkg.sub_packages[0]

        # Find __init__ module
        init_module = next(m for m in http_pkg.modules if m.name == "__init__")

        # Check imports don't contain invalid characters
        for imp in init_module.imports:
            if imp.module:
                assert "{" not in imp.module, f"Invalid '{{' in import module: {imp.module}"
                assert "}" not in imp.module, f"Invalid '}}' in import module: {imp.module}"

    def test_init_module_imports_use_correct_module_names(self, mapper, use_cases):
        """__init__.py should import from use_case-named modules."""
        http_spec = HttpInterfaceSpec(
            endpoints=[
                HttpEndpointSpec(
                    path="/users",
                    method="POST",
                    use_case="CreateUser",
                    description="Create a new user",
                ),
                HttpEndpointSpec(
                    path="/users/{user_id}",
                    method="GET",
                    use_case="GetUser",
                    description="Get user by ID",
                ),
            ]
        )
        interfaces = InterfaceSpec(http=http_spec)

        pkg = mapper.to_package_spec(interfaces, "Shared", use_cases)
        http_pkg = pkg.sub_packages[0]

        init_module = next(m for m in http_pkg.modules if m.name == "__init__")

        # Check imports reference correct module names
        import_modules = [
            imp.module for imp in init_module.imports if "interfaces.http" in imp.module
        ]
        assert "shared.interfaces.http.create_user" in import_modules
        assert "shared.interfaces.http.get_user" in import_modules

    # ============ Decorator Tests ============

    def test_decorator_preserves_original_path(self, mapper, use_cases):
        """HTTP decorator should preserve the original path with parameters."""
        http_spec = HttpInterfaceSpec(
            endpoints=[
                HttpEndpointSpec(
                    path="/users/{user_id}",
                    method="GET",
                    use_case="GetUser",
                    description="Get user by ID",
                ),
            ]
        )
        interfaces = InterfaceSpec(http=http_spec)

        pkg = mapper.to_package_spec(interfaces, "Shared", use_cases)
        http_pkg = pkg.sub_packages[0]
        endpoint_module = http_pkg.modules[0]

        # Decorator should have the original path
        decorators = endpoint_module.functions[0].decorators
        assert len(decorators) == 1
        assert '/users/{user_id}' in decorators[0]
        assert 'router.get' in decorators[0]