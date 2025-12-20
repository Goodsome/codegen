import yaml
from pathlib import Path
from codegen.domain.aggregates.blueprint import Blueprint


def test_blueprint():
    yaml_path = Path("../codegen.yaml")

    with open(yaml_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    bp = Blueprint.model_validate(data)
    print(bp)
