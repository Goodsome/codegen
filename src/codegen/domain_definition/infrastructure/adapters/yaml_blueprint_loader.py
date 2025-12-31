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
        config_path = config["config_path"]
        if isinstance(config_path, str):
            self.config_path = Path(config_path)
        elif isinstance(config_path, Path):
            self.config_path = config_path
        else:
            raise ValueError("Invalid config_path value")

    def load(self, source: str) -> Blueprint | None:
        if not os.path.exists(self.config_path):
            return None

        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                data = cast(dict[str, object], yaml.safe_load(f))

            return Blueprint.model_validate(data)

        except Exception as e:
            # 在实际工程中，这里应该记录日志或抛出自定义异常
            print(f"Error loading yaml spec: {e}")
            raise e
