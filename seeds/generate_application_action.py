# seeds/generate_application_action.py
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from jinja2 import Environment, FileSystemLoader, StrictUndefined

_SNAKE_RE = re.compile(r"^[a-z][a-z0-9_]*$")

def ensure_snake(name: str) -> str:
    if not _SNAKE_RE.match(name):
        raise ValueError(f"Expected snake_case like 'init_project', got: {name!r}")
    return name

def snake_to_pascal(s: str) -> str:
    s = ensure_snake(s)
    return "".join(w[:1].upper() + w[1:] for w in s.split("_"))

def ensure_init_py(d: Path) -> None:
    init_file = d / "__init__.py"
    if not init_file.exists():
        init_file.write_text("", encoding="utf-8")

def default_templates_dir() -> Path:
    # repo_root/seeds/... -> repo_root/src/codegen/templates
    repo_root = Path(__file__).resolve().parents[1]
    return repo_root / "src" / "codegen" / "templates"

Kind = Literal["use_case", "query"]
Form = Literal["single", "package"]

@dataclass(frozen=True)
class GenerateAppActionSpec:
    kind: Kind
    name_snake: str
    form: Form
    with_mapper: bool = False

class AppActionGenerator:
    def __init__(self, templates_dir: Path | None = None) -> None:
        templates_dir = templates_dir or default_templates_dir()

        self.env = Environment(
            loader=FileSystemLoader(str(templates_dir)),
            autoescape=False,
            undefined=StrictUndefined,
            keep_trailing_newline=True,
            lstrip_blocks=True,
            trim_blocks=True,
        )

    def generate(self, project_pkg_dir: Path, spec: GenerateAppActionSpec) -> Path:
        name_snake = ensure_snake(spec.name_snake)
        pascal = snake_to_pascal(name_snake)

        kind_dir = "use_cases" if spec.kind == "use_case" else "queries"
        kind_suffix = "Command" if spec.kind == "use_case" else "Query"
        kind_label = "UseCase" if spec.kind == "use_case" else "Query"
        kind_var = "command" if spec.kind == "use_case" else "query"

        base_dir = project_pkg_dir / "application" / kind_dir
        base_dir.mkdir(parents=True, exist_ok=True)
        ensure_init_py(base_dir)

        ctx = {
            "kind": kind_label,
            "name_snake": name_snake,
            "pascal": pascal,
            "kind_suffix": kind_suffix,
            "kind_var": kind_var,
            "with_mapper": spec.with_mapper,
        }

        if spec.form == "single":
            out = base_dir / f"{name_snake}.py"
            self._render("application_action/single.py.j2", ctx, out)
            return out

        pkg_dir = base_dir / name_snake
        pkg_dir.mkdir(parents=True, exist_ok=True)

        self._render("application_action/pkg_command.py.j2", ctx, pkg_dir / "command.py")
        self._render("application_action/pkg_result.py.j2", ctx, pkg_dir / "result.py")
        self._render("application_action/pkg_handler.py.j2", ctx, pkg_dir / "handler.py")
        if spec.with_mapper:
            self._render("application_action/pkg_mapper.py.j2", ctx, pkg_dir / "mapper.py")
        self._render("application_action/pkg___init__.py.j2", ctx, pkg_dir / "__init__.py")

        return pkg_dir

    def _render(self, template_name: str, ctx: dict, out: Path) -> None:
        tpl = self.env.get_template(template_name)
        out.write_text(tpl.render(**ctx), encoding="utf-8")