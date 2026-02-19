
import pytest
from codegen.entrypoints.cli.application import app
from pathlib import Path

def test_reproduce_missing_type_error(cli_runner, working_dir, simple_project_blueprint, monkeypatch):
    """
    Scenario: Reproduce 'NoneType' object has no attribute 'name' error
    Given: A python class with an untyped attribute
    When: Running 'codegen reverse'
    Then: It should handle it gracefully (or fail with a clear error, but currently crashes).
    """
    # Verify blueprint exists
    assert simple_project_blueprint.exists()

    # Switch to the working directory
    monkeypatch.chdir(working_dir)

    # 1. Run the build command to get base structure
    result = cli_runner.invoke(app, ["build"])
    assert result.exit_code == 0
    
    # 2. Inject a file with an untyped attribute in a Value Object or similar
    # The traceback showed value_object_mapper -> module_spec_to_value_objects
    # So let's add a Value Object with an untyped field.
    
    project_root = working_dir
    sales_domain_defs = project_root / "src" / "simple_project" / "sales" / "domain" / "value_objects" / "money.py"
    sales_domain_defs.parent.mkdir(parents=True, exist_ok=True)
    
    # Writing a class with an untyped attribute 'currency'
    sales_domain_defs.write_text("""
from dataclasses import dataclass

@dataclass(frozen=True)
class Money:
    amount: float
    currency = "USD"  # Untyped attribute
""")
    
    # 3. Run the reverse command
    reverse_output = working_dir / "codegen_reversed.yaml"
    result_reverse = cli_runner.invoke(app, ["reverse", "--config", str(reverse_output)])
    
    # Assert successful execution (once fixed)
    assert result_reverse.exit_code == 0, f"Reverse failed: {result_reverse.stdout}"
    assert reverse_output.exists()
