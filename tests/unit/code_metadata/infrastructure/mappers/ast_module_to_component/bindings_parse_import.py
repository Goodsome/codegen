import ast

import pytest
from dataclasses import dataclass
from typing import Self

from codegen.code_metadata.application.dtos.imported_component import ImportedComponent
from codegen.code_metadata.infrastructure.mappers.ast_module_to_component import (
    AstModuleToComponent,
)


@dataclass
class ParseImportBindings:
    _last_step_type: str | None = None
    _node: ast.ImportFrom | None = None
    _result: list[ImportedComponent] | None = None

    def given(self: Self, semantic_text: str) -> Self:
        self._last_step_type = "given"
        match semantic_text:
            case str(s) if "不以 codegen" in s:
                self._node = self._make_import_from("pydantic", ["BaseModel"])
            case str(s) if "别名" in s:
                self._node = self._make_import_from(
                    "case_converter", ["NamingString"], asnames=["SnakeString"]
                )
            case str(s) if "多个名字" in s:
                self._node = self._make_import_from(
                    "case_converter", ["NamingString", "SnakeString", "PascalString"]
                )
            case str(s) if "codegen" in s:
                self._node = self._make_import_from(
                    "codegen.shared.domain.value_objects.snake_string",
                    ["SnakeString"],
                )
            case _:
                raise NotImplementedError(f"未实现的 given 语义: {semantic_text}")
        return self

    def arrange_done(self: Self) -> Self:
        return self

    def when(self: Self, semantic_text: str) -> Self:
        self._last_step_type = "when"
        match semantic_text:
            case str(s) if "parse_import" in s:
                assert self._node is not None, "必须先在 given 中设置测试节点"
                sut = self._make_sut()
                self._result = sut.parse_import(self._node)
            case _:
                raise NotImplementedError(f"未实现的 when 语义: {semantic_text}")
        return self

    def then(self: Self, semantic_text: str) -> Self:
        self._last_step_type = "then"
        match semantic_text:
            case str(s) if (
                "context" in s
                and "codegen" in s
                and "多个" not in s
                and "原始" not in s
            ):
                assert self._result is not None, "必须先调用 when"
                assert self._result == [
                    ImportedComponent(
                        context="shared",
                        component="SnakeString",
                    )
                ]
            case str(s) if "完整模块路径" in s and "codegen" not in s:
                assert self._result is not None, "必须先调用 when"
                assert self._result == [
                    ImportedComponent(context="pydantic", component="BaseModel")
                ]
            case str(s) if "多个" in s:
                assert self._result is not None, "必须先调用 when"
                assert len(self._result) == 3
                assert self._result == [
                    ImportedComponent(
                        context="case_converter", component="NamingString"
                    ),
                    ImportedComponent(
                        context="case_converter", component="SnakeString"
                    ),
                    ImportedComponent(
                        context="case_converter", component="PascalString"
                    ),
                ]
            case str(s) if "原始名" in s:
                assert self._result is not None, "必须先调用 when"
                assert self._result == [
                    ImportedComponent(
                        context="case_converter", component="NamingString"
                    )
                ]
            case _:
                raise NotImplementedError(f"未实现的 then 语义: {semantic_text}")
        return self

    def and_(self: Self, semantic_text: str) -> Self:
        if not self._last_step_type:
            raise RuntimeError("Cannot use 'and/but' before any Given/When/Then step.")
        if self._last_step_type == "given":
            return self.given(semantic_text)
        if self._last_step_type == "when":
            return self.when(semantic_text)
        if self._last_step_type == "then":
            return self.then(semantic_text)
        raise RuntimeError(f"Unexpected last step type: {self._last_step_type}")

    def but(self: Self, semantic_text: str) -> Self:
        if not self._last_step_type:
            raise RuntimeError("Cannot use 'and/but' before any Given/When/Then step.")
        if self._last_step_type == "given":
            return self.given(semantic_text)
        if self._last_step_type == "when":
            return self.when(semantic_text)
        if self._last_step_type == "then":
            return self.then(semantic_text)
        raise RuntimeError(f"Unexpected last step type: {self._last_step_type}")

    @staticmethod
    def _make_sut() -> AstModuleToComponent:
        """Create a system-under-test instance with a no-op class mapper."""
        from unittest.mock import MagicMock

        return AstModuleToComponent(ast_class_to_component=MagicMock())

    @staticmethod
    def _make_import_from(
        module: str,
        names: list[str],
        asnames: list[str] | None = None,
    ) -> ast.ImportFrom:
        """Construct an ast.ImportFrom node from declarative parameters."""
        aliases: list[ast.alias] = []
        for i, name in enumerate(names):
            asname = asnames[i] if asnames and i < len(asnames) else None
            aliases.append(ast.alias(name=name, asname=asname))
        return ast.ImportFrom(module=module, names=aliases, level=0)


@pytest.fixture
def parse_import_bindings() -> ParseImportBindings:
    return ParseImportBindings()
