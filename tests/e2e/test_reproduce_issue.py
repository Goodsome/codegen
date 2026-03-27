
from codegen.entrypoints.cli.application import app

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
    # Note: reverse now outputs to codegen.yaml (fixed path)
    # First backup original codegen.yaml
    original_blueprint = working_dir / "codegen.yaml"
    original_blueprint_backup = working_dir / "codegen.yaml.bak"
    original_blueprint.rename(original_blueprint_backup)

    try:
        result_reverse = cli_runner.invoke(app, ["reverse"])

        assert result_reverse.exit_code == 0, f"Reverse failed: {result_reverse.stdout}"
        assert original_blueprint.exists()

        content = original_blueprint.read_text()
        assert "calculate_tax" in content
        # We expect the parameter 'rate' to be present.
        # Depending on how VariableSpec is serialized, it might show 'assignment: 0.1' or similar.
        assert "rate" in content
        assert "0.1" in content
    finally:
        # Restore original blueprint
        original_blueprint.unlink()
        original_blueprint_backup.rename(original_blueprint)
