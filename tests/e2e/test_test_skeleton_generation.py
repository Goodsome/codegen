"""E2E test: Test skeleton generation with `codegen build`."""

import pytest
from codegen.entrypoints.cli.application import app
from pathlib import Path

import shutil


def _setup_blueprint(tmp_path, fixture_name="domain_definition"):
    """Copy blueprint fixture to a temp directory and return the base_dir."""
    base_dir = tmp_path / fixture_name
    base_dir.mkdir()
    fixture_dir = Path(__file__).parent / "fixtures" / fixture_name
    source_blueprint = fixture_dir / "codegen.yaml"
    if not source_blueprint.exists():
        pytest.fail(f"Blueprint not found at {source_blueprint}")
    shutil.copy(source_blueprint, base_dir / "codegen.yaml")
    return base_dir


def test_build_generates_test_skeletons_by_default(cli_runner, monkeypatch, tmp_path):
    """
    Scenario: Default build generates test skeletons.
    Given: A valid blueprint with Aggregate and Service behaviors.
    When: Running 'codegen build' (without --skip-tests).
    Then: test_*.py and cases_*.py are generated in tests/unit/.
    """
    base_dir = _setup_blueprint(tmp_path)
    monkeypatch.chdir(base_dir)

    result = cli_runner.invoke(app, ["build"])

    if result.exit_code != 0:
        print(result.stdout)
        if result.exception:
            import traceback
            traceback.print_exception(
                type(result.exception), result.exception,
                result.exception.__traceback__,
            )

    assert result.exit_code == 0, f"Build failed: {result.stdout}"

    # Verify test directory structure
    tests_dir = base_dir / "tests" / "unit"
    assert tests_dir.exists(), (
        f"tests/unit/ directory not created. Contents: {list(base_dir.iterdir())}"
    )

    # Check Sales context test files
    sales_test_dir = tests_dir / "sales" / "domain"
    assert sales_test_dir.exists(), "sales/domain/ not found in tests/unit/"

    # Check aggregates (Order has add_item behavior)
    agg_dir = sales_test_dir / "aggregates"
    assert agg_dir.exists(), f"aggregates/ not found in {sales_test_dir}"

    test_order = agg_dir / "test_order.py"
    cases_order = agg_dir / "cases_order.py"
    assert test_order.exists(), "test_order.py not generated"
    assert cases_order.exists(), "cases_order.py not generated"

    # Verify test file content
    test_content = test_order.read_text()
    assert "import pytest" in test_content
    assert "class TestOrder" in test_content
    assert "def test_add_item" in test_content
    assert "from .cases_order import" in test_content

    # Verify cases file content
    cases_content = cases_order.read_text()
    assert "TEST_CASES_ADD_ITEM" in cases_content

    # Verify import pytest is BEFORE the class definition
    import_line = test_content.index("import pytest")
    class_line = test_content.index("class TestOrder")
    assert import_line < class_line, "import pytest should appear before class definition"

    # Verify cases import is BEFORE the class definition
    cases_import_line = test_content.index("from .cases_order import")
    assert cases_import_line < class_line, (
        "cases import should appear before class definition"
    )


def test_build_skip_tests_flag(cli_runner, monkeypatch, tmp_path):
    """
    Scenario: Build with --skip-tests does NOT generate test skeletons.
    """
    base_dir = _setup_blueprint(tmp_path)
    monkeypatch.chdir(base_dir)

    result = cli_runner.invoke(app, ["build", "--skip-tests"])

    assert result.exit_code == 0

    # tests/ directory should NOT exist
    tests_dir = base_dir / "tests"
    assert not tests_dir.exists(), (
        f"tests/ should not be created with --skip-tests. "
        f"Found: {list(tests_dir.iterdir()) if tests_dir.exists() else 'N/A'}"
    )


def test_cases_files_are_not_overwritten(cli_runner, monkeypatch, tmp_path):
    """
    Scenario: Running build twice does NOT overwrite cases_*.py files.
    """
    base_dir = _setup_blueprint(tmp_path)
    monkeypatch.chdir(base_dir)

    # First build
    result1 = cli_runner.invoke(app, ["build"])
    assert result1.exit_code == 0

    # Write custom test data in the cases file
    agg_dir = base_dir / "tests" / "unit" / "sales" / "domain" / "aggregates"
    cases_file = agg_dir / "cases_order.py"
    assert cases_file.exists(), "cases_order.py not generated on first build"

    # Add custom test case data
    custom_content = 'TEST_CASES_ADD_ITEM = [("custom_product", 5, None)]\n'
    cases_file.write_text(custom_content)

    # Second build — should NOT overwrite cases file
    result2 = cli_runner.invoke(app, ["build"])
    assert result2.exit_code == 0

    preserved_content = cases_file.read_text()
    assert "custom_product" in preserved_content, (
        "cases_order.py was overwritten! Content after second build: "
        + preserved_content
    )
