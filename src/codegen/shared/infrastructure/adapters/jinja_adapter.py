from pathlib import Path
from typing import Dict, Any

from jinja2 import Environment, FileSystemLoader

from codegen.shared.domain.ports.template_port import TemplatePort


class JinjaAdapter(TemplatePort):
    """
    Jinja-based template rendering adapter.
    """

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.template_root = Path(config.get("template_root", "src/codegen/templates"))
        self.autoescape = config.get("autoescape", False)

        self.env = Environment(
            loader=FileSystemLoader(self.template_root), autoescape=self.autoescape
        )
        self.env.filters["repr"] = repr

    def render(self, template_path: str, context: Dict[str, Any]) -> str:
        """
        Renders a template with the given context.
        """
        template = self.env.get_template(template_path)
        return template.render(**context)
