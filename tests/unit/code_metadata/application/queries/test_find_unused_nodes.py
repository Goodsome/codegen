from unittest.mock import MagicMock

from codegen.code_metadata.domain.aggregates.code_node import ClassNode
from codegen.code_metadata.application.queries.find_unused_nodes import FindUnusedNodes
from codegen.code_metadata.domain.enums.code_node_kind import CodeNodeKind


class TestFindUnusedNodes:
    def test_execute_delegates_to_query_service(self) -> None:
        mock_service = MagicMock()
        expected = [
            ClassNode(fqn="codegen.foo.Bar", name="Bar"),
            ClassNode(fqn="codegen.baz.Qux", name="Qux"),
        ]
        mock_service.find_unused_nodes.return_value = expected

        handler = FindUnusedNodes(query_service=mock_service)
        result = handler.execute(CodeNodeKind.CLASS)

        mock_service.find_unused_nodes.assert_called_once_with(CodeNodeKind.CLASS)
        assert result == expected

    def test_execute_returns_empty_when_no_unused(self) -> None:
        mock_service = MagicMock()
        mock_service.find_unused_nodes.return_value = []

        handler = FindUnusedNodes(query_service=mock_service)
        result = handler.execute(CodeNodeKind.CLASS)

        assert result == []
