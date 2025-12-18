from datetime import datetime
import yaml
import sys
from pathlib import Path
from dataclasses import dataclass
from typing import List, Any
from jinja2 import Environment, FileSystemLoader


# Simplified internal models for the bootstrapper
@dataclass
class Attribute:
    name: str
    type: str
    description: str = ""


@dataclass
class Aggregate:
    name: str
    description: str
    attributes: List[Attribute]
    behaviors: List[str]


@dataclass
class ValueObject:
    name: str
    description: str
    attributes: List[Attribute]


@dataclass
class Operation:
    name: str
    description: str
    inputs: List[Attribute]
    output_type: str


@dataclass
class Service:
    name: str
    description: str
    operations: List[Operation]


@dataclass
class Port:
    name: str
    description: str
    kind: str  # gateway | repository
    operations: List[Operation]


@dataclass
class Command:
    name: str
    attributes: List[Attribute]


@dataclass
class Result:
    name: str
    attributes: List[Attribute]


@dataclass
class UseCase:
    name: str
    kind: str  # command | query
    description: str
    command: Command
    result: Result
    depends_on_services: List[str]
    depends_on_ports: List[str]


@dataclass
class Adapter:
    name: str
    implements: str
    description: str
    config: dict


@dataclass
class BoundedContext:
    name: str
    aggregates: List[Aggregate]
    value_objects: List[ValueObject]
    services: List[Service]
    ports: List[Port]
    use_cases: List[UseCase]


def to_pascal(s: str) -> str:
    return "".join(word.capitalize() for word in s.split("_"))


def to_snake(s: str) -> str:
    import re

    return re.sub(r"(?<!^)(?=[A-Z])", "_", s).lower()


def ensure_package(dir_path: Path):
    dir_path.mkdir(parents=True, exist_ok=True)
    init_file = dir_path / "__init__.py"
    if not init_file.exists():
        init_file.write_text("", encoding="utf-8")


def render_to_file(env: Environment, template_name: str, dest: Path, ctx: dict):
    dest.parent.mkdir(parents=True, exist_ok=True)
    tpl = env.get_template(template_name)
    dest.write_text(tpl.render(**ctx), encoding="utf-8")
    print(f"Generated: {dest}")


def extract_base_type(type_str: str) -> str:
    """Extracts 'Attribute' from 'List[Attribute]' or returns 'Attribute'."""
    import re

    match = re.search(r"\[(\w+)]", type_str)
    if match:
        return match.group(1)
    return type_str


def load_yaml(path: Path) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def parse_operation(op_data: dict) -> Operation:
    inputs = [Attribute(**attr) for attr in op_data.get("inputs", [])]
    return Operation(
        name=op_data["name"],
        description=op_data.get("description", ""),
        inputs=inputs,
        output_type=op_data.get("output", {}).get("type", "None"),
    )


def parse_use_case(uc_data: dict) -> UseCase:
    cmd_data = uc_data.get("command", {"name": f"{uc_data['name']}Command", "attributes": []})
    res_data = uc_data.get("result", {"name": f"{uc_data['name']}Result", "attributes": []})
    
    command = Command(
        name=cmd_data["name"],
        attributes=[Attribute(**a) for a in cmd_data.get("attributes", [])]
    )
    result = Result(
        name=res_data["name"],
        attributes=[Attribute(**a) for a in res_data.get("attributes", [])]
    )
    
    depends_on = uc_data.get("depends_on", {})
    return UseCase(
        name=uc_data["name"],
        kind=uc_data.get("kind", "command"),
        description=uc_data.get("description", ""),
        command=command,
        result=result,
        depends_on_services=depends_on.get("services", []),
        depends_on_ports=depends_on.get("ports", []),
    )


def parse_context(data: dict) -> BoundedContext:
    domain = data.get("domain", {})
    app = data.get("application", {})

    aggregates = []
    for agg_data in domain.get("aggregates", []):
        attrs = [Attribute(**a) for a in agg_data.get("attributes", [])]
        behaviors = agg_data.get("behaviors", [])
        aggregates.append(
            Aggregate(
                name=agg_data["name"],
                description=agg_data.get("description", ""),
                attributes=attrs,
                behaviors=behaviors,
            )
        )

    value_objects = []
    for vo_data in domain.get("value_objects", []):
        attrs = [Attribute(**a) for a in vo_data.get("attributes", [])]
        value_objects.append(
            ValueObject(
                name=vo_data["name"],
                description=vo_data.get("description", ""),
                attributes=attrs,
            )
        )

    services = []
    for svc_data in domain.get("services", []):
        ops = [parse_operation(op) for op in svc_data.get("operations", [])]
        services.append(
            Service(
                name=svc_data["name"],
                description=svc_data.get("description", ""),
                operations=ops,
            )
        )

    ports = []
    for port_data in domain.get("ports", []):
        ops = [parse_operation(op) for op in port_data.get("operations", [])]
        ports.append(
            Port(
                name=port_data["name"],
                description=port_data.get("description", ""),
                kind=port_data.get("kind", "gateway"),
                operations=ops,
            )
        )

    use_cases = []
    for uc_data in app.get("use_cases", []):
        use_cases.append(parse_use_case(uc_data))

    return BoundedContext(
        name=data["name"],
        aggregates=aggregates,
        value_objects=value_objects,
        services=services,
        ports=ports,
        use_cases=use_cases,
    )


def generate_shared_kernel(root_path: Path):
    """Generates the shared kernel from templates."""
    shared_dir = root_path / "shared"
    shared_dir.mkdir(parents=True, exist_ok=True)

    # In a real scenario, use jinja2 to render. Here we simulate copying/rendering.
    # Assuming the templates are at src/codegen/templates/domain/shared
    # root_path is src/codegen/domain, so template_dir is src/codegen/templates/domain/shared
    template_dir = root_path.parent / "templates" / "domain" / "shared"

    files = ["models.py.j2", "events.py.j2"]
    for tpl_file in files:
        src = template_dir / tpl_file
        if not src.exists():
            print(f"Warning: Template {src} not found.")
            continue

        dest = shared_dir / tpl_file.replace(".j2", "")
        with open(src, "r", encoding="utf-8") as f:
            content = f.read()

        with open(dest, "w", encoding="utf-8") as f:
            f.write(content)

    print(f"Generated Shared Kernel at {shared_dir}")


def get_jinja_env():
    template_dir = Path(__file__).parent / "codegen" / "templates"
    env = Environment(loader=FileSystemLoader(template_dir))
    env.filters["snake"] = to_snake
    env.filters["pascal"] = to_pascal
    env.filters["repr"] = repr
    return env


def generate_aggregate(base_path: Path, agg: Aggregate, env: Environment, known_vos: List[str] = None):
    folder = base_path / "domain" / "aggregates"
    folder.mkdir(parents=True, exist_ok=True)
    file_path = folder / f"{to_snake(agg.name)}.py"

    imports = []
    typing_imports = set()
    typing_keywords = ["List", "Dict", "Optional", "Any", "Union"]

    for attr in agg.attributes:
        for keyword in typing_keywords:
            if keyword in attr.type:
                typing_imports.add(keyword)
        if known_vos:
            base_type = extract_base_type(attr.type)
            if base_type != agg.name and base_type in known_vos:
                import_path = f"codegen.domain.value_objects.{to_snake(base_type)}"
                imports.append(f"from {import_path} import {base_type}")

    if typing_imports:
        imports.append(f"from typing import {', '.join(sorted(typing_imports))}")
    imports = sorted(list(set(imports)))

    template = env.get_template("domain/aggregate.py.j2")
    content = template.render(
        name=agg.name,
        description=agg.description,
        attributes=agg.attributes,
        behaviors=agg.behaviors,
        imports=imports,
    )
    file_path.write_text(content, encoding="utf-8")
    print(f"Generated Aggregate: {file_path}")


def generate_value_object(base_path: Path, vo: ValueObject, env: Environment, known_vos: List[str] = None):
    folder = base_path / "domain" / "value_objects"
    folder.mkdir(parents=True, exist_ok=True)
    file_path = folder / f"{to_snake(vo.name)}.py"

    imports = []
    typing_imports = set()
    typing_keywords = ["List", "Dict", "Optional", "Any", "Union"]

    for attr in vo.attributes:
        for keyword in typing_keywords:
            if keyword in attr.type:
                typing_imports.add(keyword)
        if known_vos:
            base_type = extract_base_type(attr.type)
            if base_type != vo.name and base_type in known_vos:
                import_path = f"codegen.domain.value_objects.{to_snake(base_type)}"
                imports.append(f"from {import_path} import {base_type}")

    if typing_imports:
        imports.append(f"from typing import {', '.join(sorted(typing_imports))}")
    imports = sorted(list(set(imports)))

    template = env.get_template("domain/value_object.py.j2")
    content = template.render(
        name=vo.name,
        description=vo.description,
        attributes=vo.attributes,
        imports=imports,
    )
    file_path.write_text(content, encoding="utf-8")
    print(f"Generated ValueObject: {file_path}")


def generate_port(base_path: Path, port: Port, env: Environment):
    folder = base_path / "domain" / "ports"
    folder.mkdir(parents=True, exist_ok=True)
    file_path = folder / f"{to_snake(port.name)}.py"
    template = env.get_template("domain/port.py.j2")
    content = template.render(
        name=port.name,
        description=port.description,
        operations=port.operations,
    )
    file_path.write_text(content, encoding="utf-8")
    print(f"Generated Port: {file_path}")


def generate_service(base_path: Path, svc: Service, env: Environment):
    folder = base_path / "domain" / "services"
    folder.mkdir(parents=True, exist_ok=True)
    file_path = folder / f"{to_snake(svc.name)}.py"
    template = env.get_template("domain/service.py.j2")
    content = template.render(
        name=svc.name,
        description=svc.description,
        operations=svc.operations,
    )
    file_path.write_text(content, encoding="utf-8")
    print(f"Generated Domain Service: {file_path}")


def generate_use_case(base_path: Path, uc: UseCase, env: Environment):
    folder = base_path / "application" / "use_cases"
    folder.mkdir(parents=True, exist_ok=True)
    file_path = folder / f"{to_snake(uc.name)}.py"
    template = env.get_template("application_action/single.py.j2")
    content = template.render(
        name=uc.name,
        kind=uc.kind,
        description=uc.description,
        command=uc.command,
        result=uc.result,
        depends_on_services=uc.depends_on_services,
        depends_on_ports=uc.depends_on_ports,
    )
    file_path.write_text(content, encoding="utf-8")
    print(f"Generated UseCase: {file_path}")


def generate_adapter(base_path: Path, adapter: Adapter, env: Environment, ports: List[Port] = None):
    folder = base_path / "infrastructure" / "adapters"
    folder.mkdir(parents=True, exist_ok=True)
    file_path = folder / f"{to_snake(adapter.name)}.py"
    template = env.get_template("infrastructure/adapter.py.j2")
    
    operations = []
    if ports:
        for p in ports:
            if p.name == adapter.implements:
                operations = p.operations
                break

    content = template.render(
        name=adapter.name,
        description=adapter.description,
        implements=adapter.implements,
        implements_snake=to_snake(adapter.implements),
        config=adapter.config,
        operations=operations
    )
    file_path.write_text(content, encoding="utf-8")
    print(f"Generated Adapter: {file_path}")


def main():
    root = Path(__file__).parent.parent
    yaml_path = root / "codegen.yaml"

    if not yaml_path.exists():
        print(f"Error: {yaml_path} not found.")
        sys.exit(1)

    data = load_yaml(yaml_path)
    print(f"Loaded blueprint: {data['name']}")

    target_root = root / "src" / "codegen"
    env = get_jinja_env()

    # 1. Generate Shared Kernel
    generate_shared_kernel(target_root / "domain")

    all_ports = []
    
    # 2. Generate Contexts
    for ctx_data in data.get("contexts", []):
        ctx = parse_context(ctx_data)
        print(f"Generating context '{ctx.name}'...")

        known_vo_names = [vo.name for vo in ctx.value_objects]

        for agg in ctx.aggregates:
            generate_aggregate(target_root, agg, env, known_vo_names)

        for vo in ctx.value_objects:
            generate_value_object(target_root, vo, env, known_vo_names)

        for svc in ctx.services:
            generate_service(target_root, svc, env)

        for port in ctx.ports:
            generate_port(target_root, port, env)
            all_ports.append(port)

        for uc in ctx.use_cases:
            generate_use_case(target_root, uc, env)

    # 3. Generate Infrastructure (Adapters from shared or elsewhere)
    shared = data.get("shared", {})
    infra = shared.get("infrastructure", {})
    for adapter_data in infra.get("adapters", []):
        adapter = Adapter(**adapter_data)
        generate_adapter(target_root, adapter, env, all_ports)


if __name__ == "__main__":
    main()
