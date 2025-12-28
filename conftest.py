# conftest.py
import pytest
from pathlib import Path

from codegen.bootstrap import Container
from codegen.domain_definition.application.use_cases.load_blueprint import (
    LoadBlueprintCommand,
)
from codegen.domain_definition.domain.value_objects.blueprint import Blueprint


@pytest.fixture(scope="session")
def project_root() -> Path:
    """
    获取项目根目录的绝对路径。
    由于 conftest.py 位于根目录，其父级即为根。
    """
    return Path(__file__).parent.absolute()


@pytest.fixture(scope="session")
def default_container(project_root: Path) -> Container:
    """ """
    config = {
        "template_root": project_root / "src/codegen/python_gen/templates",
        "output_root": project_root / "src",
        "project_root": project_root,
        "encoding": "utf-8",
    }
    return Container(config=config)


@pytest.fixture(scope="session")
def local_blueprint(default_container: Container) -> Blueprint:
    use_case = default_container.load_blueprint_use_case()
    result = use_case.execute(LoadBlueprintCommand())
    return result.blueprint
