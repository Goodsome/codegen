import os
from typing import cast, override

import yaml

from codegen.domain.aggregates.blueprint import Blueprint
from codegen.domain.ports.blueprint_loader_port import BlueprintLoaderPort


class YamlBlueprintLoader(BlueprintLoaderPort):

    def load(self, source: str) -> Blueprint | None:
        if not os.path.exists(source):
            return None

        try:
            with open(source, "r", encoding="utf-8") as f:
                data = cast(dict[str, object], yaml.safe_load(f))

            return Blueprint.model_validate(data)

        except Exception as e:
            # 在实际工程中，这里应该记录日志或抛出自定义异常
            print(f"Error loading yaml spec: {e}")
            raise e
