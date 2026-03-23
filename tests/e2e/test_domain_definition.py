
import pytest
from codegen.entrypoints.cli.application import app
from pathlib import Path

import shutil

def test_domain_definition_generation(cli_runner, monkeypatch, tmp_path):
    """
    Scenario: Domain Definition Generation
    Given: A valid blueprint with Aggregate, Entity, Value Object, and Enum
    When: Running 'codegen build'
    Then: The domain artifacts are generated correctly.
    """
    base_dir = tmp_path / "domain_def"
    base_dir.mkdir()

    # Copy blueprint
    fixture_dir = Path(__file__).parent / "fixtures" / "domain_definition"
    source_blueprint = fixture_dir / "codegen.yaml"
    if not source_blueprint.exists():
        pytest.fail(f"Blueprint not found at {source_blueprint}")
    
    shutil.copy(source_blueprint, base_dir / "codegen.yaml")

    # Switch to the working directory
    monkeypatch.chdir(base_dir)

    # Run the build command
    result = cli_runner.invoke(app, ["build"])

    if result.exit_code != 0:
        print(result.stdout)

    assert result.exit_code == 0
    assert "Build Finished" in result.stdout or "SUCCESS" in result.stdout

    project_root = base_dir
    
    # We need to find the project slug. 
    # Validating based on what typically happens. 
    # If project name is "DomainDefinitionTest", likely "domain_definition_test"
    project_slug = "domain_definition_test"
    context_slug = "sales"
    
    sales_context = project_root / "src" / project_slug / context_slug
    assert sales_context.exists(), f"Context directory not found at {sales_context}. Content of src: {[p.name for p in (project_root / 'src').iterdir()] if (project_root / 'src').exists() else 'src not found'}"

    # Check Aggregate: Order
    order_file = sales_context / "domain" / "aggregates" / "order.py"
    assert order_file.exists()
    content = order_file.read_text()
    assert "class Order" in content
    assert "order_id: str" in content
    assert "total_amount: float" in content
    assert "def add_item(self, product_id: str, quantity: int) -> None:" in content

    # Check Entity: Product
    product_file = sales_context / "domain" / "entities" / "product.py"
    assert product_file.exists()
    content = product_file.read_text()
    assert "class Product" in content
    assert "product_id: str" in content
    assert "name: str" in content
    assert "price: float" in content

    # Check Value Object: Address
    address_file = sales_context / "domain" / "value_objects" / "address.py"
    assert address_file.exists()
    content = address_file.read_text()
    assert "class Address" in content
    assert "street: str" in content
    assert "city: str" in content
    assert "zip_code: str" in content

    # Check Enum: OrderStatus
    # Enums location: domain/enums.py
    enum_file = sales_context / "domain" / "enums.py"
    assert enum_file.exists()
    content = enum_file.read_text()
    assert "class OrderStatus" in content
    assert "PENDING" in content
    assert "SHIPPED" in content
    assert "DELIVERED" in content
