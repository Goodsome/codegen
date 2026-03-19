"""Tests for InterfaceMapper CLI interface generation with special characters in names."""

import pytest
from codegen.orchestration.domain.services.interface_mapper import InterfaceMapper
from codegen.domain_definition.domain.value_objects.interface_spec import InterfaceSpec
from codegen.domain_definition.domain.value_objects.cli_interface_spec import (
    CliInterfaceSpec,
)
from codegen.domain_definition.domain.value_objects.cli_command_spec import (
    CliCommandSpec,
)
from codegen.domain_definition.domain.value_objects.use_case_spec import UseCaseSpec
from codegen.domain_definition.domain.enums import UseCaseKind


class TestInterfaceMapperCliNaming:
    """Test CLI interface file naming and import generation with special characters."""

    @pytest.fixture
    def mapper(self):
        return InterfaceMapper()

    @pytest.fixture
    def use_cases(self):
        return [
            UseCaseSpec(name="CreateIssue", kind=UseCaseKind.COMMAND),
            UseCaseSpec(name="ListIssues", kind=UseCaseKind.QUERY),
        ]

    # ============ Space Handling Tests (G1 Bug) ============

    def test_cli_command_name_with_space_creates_valid_module_name(self, mapper, use_cases):
        """CLI command name with space should create valid Python module name."""
        cli_spec = CliInterfaceSpec(
            commands=[
                CliCommandSpec(
                    name="issue create",  # Contains space
                    use_case="CreateIssue",
                    description="Create a new issue",
                ),
            ]
        )
        interfaces = InterfaceSpec(cli=cli_spec)

        pkg = mapper.to_package_spec(interfaces, "IssueTracking", use_cases)
        cli_pkg = pkg.sub_packages[0]

        # Module name should be issue_create, NOT issue create
        module_names = [m.name for m in cli_pkg.modules]
        assert "issue_create" in module_names, f"Expected 'issue_create' in {module_names}"
        assert "issue create" not in module_names, "Module name should not contain space"

    def test_cli_command_name_with_space_creates_valid_function_name(self, mapper, use_cases):
        """CLI command name with space should create valid Python function name."""
        cli_spec = CliInterfaceSpec(
            commands=[
                CliCommandSpec(
                    name="issue create",
                    use_case="CreateIssue",
                    description="Create a new issue",
                ),
            ]
        )
        interfaces = InterfaceSpec(cli=cli_spec)

        pkg = mapper.to_package_spec(interfaces, "IssueTracking", use_cases)
        cli_pkg = pkg.sub_packages[0]

        # Find the command module (not __init__)
        cmd_module = next(m for m in cli_pkg.modules if m.name != "__init__")
        func = cmd_module.functions[0]

        # Function name should be issue_create
        assert func.name == "issue_create", f"Expected 'issue_create', got '{func.name}'"

    def test_cli_init_import_with_space_in_command_name(self, mapper, use_cases):
        """__init__.py should import from space-sanitized module names."""
        cli_spec = CliInterfaceSpec(
            commands=[
                CliCommandSpec(
                    name="issue create",  # Contains space
                    use_case="CreateIssue",
                    description="Create a new issue",
                ),
                CliCommandSpec(
                    name="issue list",  # Contains space
                    use_case="ListIssues",
                    description="List all issues",
                ),
            ]
        )
        interfaces = InterfaceSpec(cli=cli_spec)

        pkg = mapper.to_package_spec(interfaces, "IssueTracking", use_cases)
        cli_pkg = pkg.sub_packages[0]

        # Find __init__ module
        init_module = next(m for m in cli_pkg.modules if m.name == "__init__")

        # Check imports don't contain spaces
        for imp in init_module.imports:
            if imp.module and "interfaces.cli" in imp.module:
                assert " " not in imp.module, f"Space found in import module: {imp.module}"
                # Should use underscore instead
                assert "issue_create" in imp.module or "issue_list" in imp.module, \
                    f"Expected sanitized name in import: {imp.module}"

    def test_cli_init_import_names_sanitized(self, mapper, use_cases):
        """__init__.py imported names should be sanitized identifiers."""
        cli_spec = CliInterfaceSpec(
            commands=[
                CliCommandSpec(
                    name="issue create",
                    use_case="CreateIssue",
                    description="Create a new issue",
                ),
            ]
        )
        interfaces = InterfaceSpec(cli=cli_spec)

        pkg = mapper.to_package_spec(interfaces, "IssueTracking", use_cases)
        cli_pkg = pkg.sub_packages[0]

        init_module = next(m for m in cli_pkg.modules if m.name == "__init__")

        # Check imported names are valid Python identifiers
        for imp in init_module.imports:
            if imp.names:
                for imported_name in imp.names:
                    # imported_name is an ImportedName object with .name attribute
                    name = imported_name.name if hasattr(imported_name, 'name') else str(imported_name)
                    assert " " not in name, f"Space in imported name: {name}"
                    assert name.isidentifier(), f"Not a valid Python identifier: {name}"

    # ============ Hyphen Handling Tests (Existing behavior) ============

    def test_cli_command_name_with_hyphen_creates_valid_module_name(self, mapper, use_cases):
        """CLI command name with hyphen should create valid Python module name."""
        cli_spec = CliInterfaceSpec(
            commands=[
                CliCommandSpec(
                    name="issue-create",  # Contains hyphen
                    use_case="CreateIssue",
                    description="Create a new issue",
                ),
            ]
        )
        interfaces = InterfaceSpec(cli=cli_spec)

        pkg = mapper.to_package_spec(interfaces, "IssueTracking", use_cases)
        cli_pkg = pkg.sub_packages[0]

        # Module name should be issue_create
        module_names = [m.name for m in cli_pkg.modules]
        assert "issue_create" in module_names

    # ============ Mixed Special Characters Tests ============

    def test_cli_command_name_with_mixed_special_chars(self, mapper, use_cases):
        """CLI command name with spaces and hyphens should create valid identifier."""
        cli_spec = CliInterfaceSpec(
            commands=[
                CliCommandSpec(
                    name="issue create-new",  # Contains both space and hyphen
                    use_case="CreateIssue",
                    description="Create a new issue",
                ),
            ]
        )
        interfaces = InterfaceSpec(cli=cli_spec)

        pkg = mapper.to_package_spec(interfaces, "IssueTracking", use_cases)
        cli_pkg = pkg.sub_packages[0]

        cmd_module = next(m for m in cli_pkg.modules if m.name != "__init__")

        # Should be sanitized to issue_create_new
        assert cmd_module.name == "issue_create_new"
        assert cmd_module.functions[0].name == "issue_create_new"