from dataclasses import dataclass

import os
from pathlib import Path
from typing import cast

import yaml

from codegen.domain_definition.domain.ports.blueprint_storage import (
    BlueprintStorage,
)
from codegen.domain_definition.domain.aggregates.blueprint import Blueprint

import logging

logger = logging.getLogger(__name__)


@dataclass
class YamlBlueprintStorage(BlueprintStorage):
    """Blueprint loader that reads from a YAML file."""

    config_path: Path

    def load(self) -> Blueprint | None:
        if not os.path.exists(self.config_path):
            return None

        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                data = cast(dict[str, object], yaml.safe_load(f))

            return Blueprint.model_validate(data)

        except Exception as e:
            logger.error(f"Error loading yaml spec: {e}")
            raise e

    def save(self, blueprint: Blueprint) -> None:
        yaml_path = self.config_path
        try:
            # 确保目录存在
            yaml_path.parent.mkdir(parents=True, exist_ok=True)
            cleaned_data = blueprint.model_dump(
                exclude_defaults=True,
                exclude_none=True,
                mode="json",
            )

            with open(yaml_path, "w", encoding="utf-8") as f:
                f.write("# yaml-language-server: $schema=./codegen.schema.json\n")
                yaml.safe_dump(
                    cleaned_data,
                    f,
                    sort_keys=True,
                    allow_unicode=True,
                    indent=2,
                    default_flow_style=False,
                )
        except Exception as e:
            logger.error(f"Error saving yaml spec: {e}")
            raise e
