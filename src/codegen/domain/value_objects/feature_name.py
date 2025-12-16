import re
from dataclasses import dataclass

@dataclass(frozen=True)
class FeatureName:
    """
    Value Object: 代表一个功能的名称。
    保证内部永远持有合法的 snake_case，并能提供 PascalCase。
    """
    value: str

    def __post_init__(self):
        # 验证逻辑 (原 ensure_snake)
        if not re.match(r"^[a-z][a-z0-9_]*$", self.value):
            raise ValueError(f"Feature name must be snake_case, got: {self.value!r}")

    @property
    def snake_case(self) -> str:
        return self.value

    @property
    def pascal_case(self) -> str:
        # 转换逻辑 (原 snake_to_pascal)
        return "".join(w[:1].upper() + w[1:] for w in self.value.split("_"))

    def __str__(self):
        return self.value