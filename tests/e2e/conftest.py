
import os
import shutil
import pytest
from pathlib import Path
from typer.testing import CliRunner

@pytest.fixture
def working_dir(tmp_path):
    """
    Creates a temporary working directory and ensures it's clean.
    Returns the Path object.
    """
    return tmp_path

@pytest.fixture
def simple_project_blueprint(working_dir):
    """
    Copies the simple_project/codegen.yaml to the working_dir.
    Returns the path to the copied codegen.yaml.
    """
    # Try to find the fixture relative to this file
    fixture_dir = Path(__file__).parent / "fixtures" / "simple_project"
    source = fixture_dir / "codegen.yaml"
    
    if not source.exists():
         # Fallback for manual run location or if __file__ is weird
        source = Path("tests/e2e/fixtures/simple_project/codegen.yaml").absolute()

    if not source.exists():
        pytest.fail(f"Fixture not found at {source}")

    dest = working_dir / "codegen.yaml"
    shutil.copy(source, dest)
    return dest

@pytest.fixture
def cli_runner():
    return CliRunner()

@pytest.fixture
def domain_definition_blueprint(working_dir):
    """
    Copies the domain_definition/codegen.yaml to the working_dir.
    Returns the path to the copied codegen.yaml.
    """
    # Try to find the fixture relative to this file
    fixture_dir = Path(__file__).parent / "fixtures" / "domain_definition"
    source = fixture_dir / "codegen.yaml"
    
    if not source.exists():
         # Fallback for manual run location or if __file__ is weird
        source = Path("tests/e2e/fixtures/domain_definition/codegen.yaml").absolute()

    if not source.exists():
        pytest.fail(f"Fixture not found at {source}")

    dest = working_dir / "codegen.yaml"
    shutil.copy(source, dest)
    return dest
