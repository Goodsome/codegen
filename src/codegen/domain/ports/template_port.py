from typing import Protocol, Any, Dict

class TemplatePort(Protocol):
    def render(self, template_name: str, context: Dict[str, Any]) -> str:
        """渲染模板，返回字符串内容"""
        ...