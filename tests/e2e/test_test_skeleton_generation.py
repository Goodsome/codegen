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


def test_build_generates_test_skeletons_with_flag(cli_runner, monkeypatch, tmp_path):
    """
    Scenario: Build with --generate-tests generates test skeletons.
    Given: A valid blueprint with Aggregate and Service behaviors.
    When: Running 'codegen build --generate-tests'.
    Then: test_*.py and cases_*.py are generated in tests/unit/.
    """
    base_dir = _setup_blueprint(tmp_path)
    monkeypatch.chdir(base_dir)

    result = cli_runner.invoke(app, ["build", "--generate-tests"])

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
    # 应为具名导入，不应使用 import *
    assert "import *" not in test_content, "cases import 不应使用 import *"
    assert "TEST_CASES_ADD_ITEM" in test_content

    # Verify cases file content
    cases_content = cases_order.read_text()
    assert "TEST_CASES_ADD_ITEM" in cases_content

    # Verify use_case test skeletons generated under application/use_cases/
    uc_dir = tests_dir / "sales" / "application" / "use_cases"
    assert uc_dir.exists(), f"application/use_cases/ not found under tests/unit/sales/"

    test_create_order = uc_dir / "test_create_order.py"
    cases_create_order = uc_dir / "cases_create_order.py"
    assert test_create_order.exists(), "test_create_order.py not generated"
    assert cases_create_order.exists(), "cases_create_order.py not generated"

    uc_content = test_create_order.read_text()
    assert "class TestCreateOrder" in uc_content
    assert "def test_execute" in uc_content
    assert "TEST_CASES_EXECUTE" in uc_content
    assert "import *" not in uc_content, "use_case test cases import 不应使用 import *"

    cases_uc_content = cases_create_order.read_text()
    assert "TEST_CASES_EXECUTE" in cases_uc_content

    # Verify import pytest is BEFORE the class definition
    import_line = test_content.index("import pytest")
    class_line = test_content.index("class TestOrder")
    assert import_line < class_line, "import pytest should appear before class definition"

    # Verify cases import is BEFORE the class definition
    cases_import_line = test_content.index("from .cases_order import")
    assert cases_import_line < class_line, (
        "cases import should appear before class definition"
    )


def test_build_default_skips_tests(cli_runner, monkeypatch, tmp_path):
    """
    Scenario: Default build (without --generate-tests) does NOT generate test skeletons.
    """
    base_dir = _setup_blueprint(tmp_path)
    monkeypatch.chdir(base_dir)

    result = cli_runner.invoke(app, ["build"])

    assert result.exit_code == 0

    # tests/ directory should NOT exist
    tests_dir = base_dir / "tests"
    assert not tests_dir.exists(), (
        f"tests/ should not be created by default. "
        f"Found: {list(tests_dir.iterdir()) if tests_dir.exists() else 'N/A'}"
    )


def test_cases_files_are_not_overwritten(cli_runner, monkeypatch, tmp_path):
    """
    Scenario: Running build twice does NOT overwrite cases_*.py files.
    """
    base_dir = _setup_blueprint(tmp_path)
    monkeypatch.chdir(base_dir)

    # First build with test generation
    result1 = cli_runner.invoke(app, ["build", "--generate-tests"])
    assert result1.exit_code == 0

    # Write custom test data in the cases file
    agg_dir = base_dir / "tests" / "unit" / "sales" / "domain" / "aggregates"
    cases_file = agg_dir / "cases_order.py"
    assert cases_file.exists(), "cases_order.py not generated on first build"

    # Add custom test case data
    custom_content = 'TEST_CASES_ADD_ITEM = [("custom_product", 5, None)]\n'
    cases_file.write_text(custom_content)

    # Second build — should NOT overwrite cases file
    result2 = cli_runner.invoke(app, ["build", "--generate-tests"])
    assert result2.exit_code == 0

    preserved_content = cases_file.read_text()
    assert "custom_product" in preserved_content, (
        "cases_order.py was overwritten! Content after second build: "
        + preserved_content
    )


def test_cases_files_support_incremental_update(cli_runner, monkeypatch, tmp_path):
    """
    Scenario: Adding a new behavior and rebuilding adds new TEST_CASES variable
              without losing hand-edited data in the existing case.
    Given: A blueprint with Order.add_item behavior.
    When: First build creates cases_order.py with TEST_CASES_ADD_ITEM.
          User writes custom data into TEST_CASES_ADD_ITEM.
          Blueprint adds Order.remove_item behavior.
          Second build runs.
    Then: cases_order.py now has BOTH TEST_CASES_ADD_ITEM (preserved) AND
          TEST_CASES_REMOVE_ITEM (newly added).
    """
    import yaml

    base_dir = _setup_blueprint(tmp_path)
    monkeypatch.chdir(base_dir)

    # First build: only add_item
    result1 = cli_runner.invoke(app, ["build", "--generate-tests"])
    assert result1.exit_code == 0, result1.stdout

    agg_dir = base_dir / "tests" / "unit" / "sales" / "domain" / "aggregates"
    cases_file = agg_dir / "cases_order.py"
    assert cases_file.exists()

    # User writes custom test data
    cases_file.write_text(
        'TEST_CASES_ADD_ITEM: list = [("prod_1", 2, None)]\n'
    )

    # Add remove_item behavior to blueprint
    blueprint_file = base_dir / "codegen.yaml"
    with blueprint_file.open() as f:
        blueprint = yaml.safe_load(f)

    for ctx in blueprint["contexts"]:
        if ctx.get("name") == "Sales":
            order_agg = next(
                a for a in ctx["domain"]["aggregates"] if a["name"] == "Order"
            )
            order_agg["behaviors"].append({
                "name": "remove_item",
                "inputs": [{"name": "product_id", "type": "str"}],
                "output": {"type": "None"},
            })

    with blueprint_file.open("w") as f:
        yaml.dump(blueprint, f)

    # Second build: should add TEST_CASES_REMOVE_ITEM without losing custom data
    result2 = cli_runner.invoke(app, ["build", "--generate-tests"])
    assert result2.exit_code == 0, result2.stdout

    updated_content = cases_file.read_text()
    assert "TEST_CASES_ADD_ITEM" in updated_content, (
        "TEST_CASES_ADD_ITEM 应被保留"
    )
    assert "prod_1" in updated_content, (
        "用户自定义的测试数据应被保留"
    )
    assert "TEST_CASES_REMOVE_ITEM" in updated_content, (
        "新增 behavior 对应的 TEST_CASES_REMOVE_ITEM 应被自动添加"
    )
