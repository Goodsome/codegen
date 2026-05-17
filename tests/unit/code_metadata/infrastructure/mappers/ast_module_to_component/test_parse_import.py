from tests.unit.code_metadata.infrastructure.mappers.ast_module_to_component.bindings_parse_import import (
    ParseImportBindings,
    parse_import_bindings,
)

_ = parse_import_bindings


def test_internal_import_extraction(parse_import_bindings: ParseImportBindings) -> None:
    parse_import_bindings.given(
        "ast.ImportFrom 节点的 module 路径以 codegen 开头（如 codegen.shared.domain...）"
    ).arrange_done().when("调用 parse_import 解析该节点").then(
        "context 取 codegen 之后的完整模块路径（如 shared.domain.value_objects.snake_string），component 取 names 列表中的导入名"
    )


def test_external_import_extraction(parse_import_bindings: ParseImportBindings) -> None:
    parse_import_bindings.given(
        "ast.ImportFrom 节点的 module 路径不以 codegen 开头（如 pydantic, case_converter）"
    ).arrange_done().when("调用 parse_import 解析该节点").then(
        "context 取 from 之后的完整模块路径，component 取 names 列表中的导入名"
    )


def test_multiple_names_yield_multiple_components(
    parse_import_bindings: ParseImportBindings,
) -> None:
    parse_import_bindings.given(
        "ast.ImportFrom 节点的 names 列表包含多个名字"
    ).arrange_done().when("调用 parse_import 解析该节点").then(
        "返回多个 ImportedComponent，每个名字对应一个"
    )


def test_alias_uses_original_name(parse_import_bindings: ParseImportBindings) -> None:
    parse_import_bindings.given(
        "ast.ImportFrom 节点中某个 name 有别名（如 import OriginalName as Alias）"
    ).arrange_done().when("调用 parse_import 解析该节点").then(
        "ImportedComponent 的 component 字段使用原始名（OriginalName），而非别名"
    )
