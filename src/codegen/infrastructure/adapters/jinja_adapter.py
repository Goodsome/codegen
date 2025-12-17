from pathlib import Path
from typing import Any, Dict
from jinja2 import Environment, FileSystemLoader, StrictUndefined
from codegen.domain.ports.template_port import TemplatePort

class JinjaTemplateAdapter(TemplatePort):
    def __init__(self, template_dir: Path):
        self.env = Environment(
            loader=FileSystemLoader(str(template_dir)),
            autoescape=False,
            undefined=StrictUndefined,
            keep_trailing_newline=True,
        )

    def render(self, template_name: str, context: Dict[str, Any]) -> str:
        template = self.env.get_template(template_name)
        return template.render(**context)