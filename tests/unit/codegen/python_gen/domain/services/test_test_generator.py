import pytest
from codegen.domain_definition.domain.value_objects.bounded_context import BoundedContext
from codegen.domain_definition.domain.value_objects.use_case_spec import UseCaseSpec
from codegen.domain_definition.domain.value_objects.aggregate_spec import AggregateSpec
from codegen.domain_definition.domain.value_objects.test_config import TestConfig
from codegen.domain_definition.domain.enums import TestMockStrategy, UseCaseKind
from codegen.domain_definition.domain.value_objects.attribute_spec import AttributeSpec
from codegen.domain_definition.domain.value_objects.data_contract_spec import DataContractSpec
from codegen.python_gen.domain.services.test_generator import TestGenerator


def test_to_test_module_spec_use_case_pytest_strategy():
    # Arrange
    generator = TestGenerator()
    
    # 1. Setup TestConfig
    test_config = TestConfig(enabled=True, strategy=TestMockStrategy.PYTEST)
    
    # x. Context
    context = BoundedContext.create(
        name="Identity",
        description="Auth and User management",
        domain=None,
        application=None,
        infrastructure=None,
        test_config=test_config
    )
    
    # 2. Setup UseCaseSpec
    # Dependency: UserRepository (Port)
    repo_dep = AttributeSpec(name="user_repo", type="UserRepository")
    
    # Command: CreateUserCommand
    command_attr = AttributeSpec(name="username", type="str")
    command = DataContractSpec(name="CreateUserCommand", attributes=[command_attr])
    
    use_case = UseCaseSpec.create(
        name="CreateUser",
        kind=UseCaseKind.COMMAND,
        dependencies=[repo_dep],
        description="Creates a new user",
        command=command,
        query=None,
        result=None
    )
    
    # Act
    module_spec = generator.to_test_module_spec(
        context=context,
        use_case=use_case,
        aggregate=None
    )
    
    # Assert
    assert module_spec is not None
    assert module_spec.name == "test_create_user"
    
    # Check imports
    import_modules = [imp.module for imp in module_spec.imports]
    assert "__root__" in import_modules
    assert "typing" in import_modules
    
    # Check for the test function
    test_func = next((f for f in module_spec.functions if f.name == "test_create_user_success"), None)
    assert test_func is not None
    assert "mocker" in [p.name for p in test_func.parameters]
    
    # Check body for key keywords
    body = test_func.suite
    assert "CreateUser" in body
    assert "UserRepository" in body
    assert "mocker.Mock" in body or "create_autospec" in body
    assert "execute" in body

def test_to_test_module_spec_aggregate_pytest_strategy():
    # Arrange
    generator = TestGenerator()
    test_config = TestConfig(enabled=True, strategy=TestMockStrategy.PYTEST)
    context = BoundedContext.create(
        name="Identity",
        description="",
        domain=None,
        application=None,
        infrastructure=None,
        test_config=test_config
    )
    
    aggregate = AggregateSpec(
        name="User",
        attributes=[AttributeSpec(name="id", type="UUID"), AttributeSpec(name="username", type="str")],
        behaviors=[]
    )
    
    # Act
    module_spec = generator.to_test_module_spec(
        context=context,
        use_case=None,
        aggregate=aggregate
    )
    
    # Assert
    assert module_spec is not None
    assert module_spec.name == "test_user"
    
    test_func = next((f for f in module_spec.functions if f.name == "test_user_creation"), None)
    assert test_func is not None
    assert "User" in test_func.suite
