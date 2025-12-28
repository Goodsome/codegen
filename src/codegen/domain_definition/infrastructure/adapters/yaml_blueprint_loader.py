import os
from pathlib import Path
from typing import cast, Any

import yaml

from codegen.domain_definition.domain.ports.blueprint_loader_port import (
    BlueprintLoaderPort,
)
from codegen.domain_definition.domain.value_objects.blueprint import Blueprint


class YamlBlueprintLoader(BlueprintLoaderPort):
    """Blueprint loader that reads from a YAML file."""

    def __init__(self, config: dict[str, Any]) -> None:
        project_root = config.get("project_root", ".")
        if isinstance(project_root, str):
            self.project_root = Path(project_root)
        elif isinstance(project_root, Path):
            self.project_root = project_root
        else:
            raise ValueError("Invalid project_root value")

    def load(self, source: str) -> Blueprint | None:
        yaml_path = self.project_root / source
        if not os.path.exists(yaml_path):
            return None

        try:
            with open(yaml_path, "r", encoding="utf-8") as f:
                data = cast(dict[str, object], yaml.safe_load(f))

            return Blueprint.model_validate(data)

        except Exception as e:
            # 在实际工程中，这里应该记录日志或抛出自定义异常
            print(f"Error loading yaml spec: {e}")
            raise e
