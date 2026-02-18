
import pytest
from codegen.entrypoints.cli.application import app
from pathlib import Path

def test_reproduce_reverse_issue(cli_runner, working_dir, simple_project_blueprint, monkeypatch):
    """
    Scenario: Reproduce codegen reverse failure
    Given: A valid simple project blueprint
    When: Running 'codegen build' then 'codegen reverse'
    Then: Both commands succeed.
    """
    # Verify blueprint exists
    assert simple_project_blueprint.exists()

    # Switch to the working directory
    monkeypatch.chdir(working_dir)

    # 1. Run the build command
    result = cli_runner.invoke(app, ["build"])
    assert result.exit_code == 0, f"Build failed: {result.stdout}"
    
    # 2. explicit check that files exist
    project_root = working_dir
    sales_dir = project_root / "src" / "simple_project" / "sales"
    assert sales_dir.exists()

    # Modify Order aggregate to have a method with default parameters
    order_file = sales_dir / "domain" / "aggregates" / "order.py"
    original_content = order_file.read_text()
    # Add a method to the class Order
    new_content = original_content.replace(
        "    total_amount: float",
        "    total_amount: float\n\n    def calculate_tax(self, rate: float = 0.1) -> float:\n        return self.total_amount * rate"
    )
    order_file.write_text(new_content)
    
    # 3. Run the reverse command
    # We need to specify where to reverse from. 
    # Assuming the default behavior tries to reverse the package in the current directory or specified by config.
    # The simple_project blueprint has name: SimpleProject.
    # We might need to adjust the command arguments based on how reverse works.
    # Usually it's `codegen reverse --output codegen_reversed.yaml`
    
    reverse_output = working_dir / "codegen_reversed.yaml"
    result_reverse = cli_runner.invoke(app, ["reverse", "--config", str(reverse_output)])
    
    assert result_reverse.exit_code == 0, f"Reverse failed: {result_reverse.stdout}"
    assert reverse_output.exists()
    
    content = reverse_output.read_text()
    assert "calculate_tax" in content
    # We expect the parameter 'rate' to be present.
    # Depending on how VariableSpec is serialized, it might show 'assignment: 0.1' or similar.
    assert "rate" in content 
    assert "0.1" in content
