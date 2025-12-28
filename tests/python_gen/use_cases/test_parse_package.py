from codegen.python_gen.application.use_cases.parse_package import ParsePackageQuery
from pathlib import Path

from codegen.bootstrap import Container


def test_parse_package(project_root: Path):
    config = {
        "template_root": project_root / "src/codegen/python_gen/templates",
        "output_root": project_root / "src",
        "encoding": "utf-8",
    }
    container = Container(config=config)
    use_case = container.parse_package_use_case()
    query = ParsePackageQuery(package_path=Path("codegen"))
    result = use_case.execute(query)
