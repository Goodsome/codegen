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
    ensure_package(shared_dir)

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


import argparse

def write_if_needed(file_path: Path, content: str, overwrite: bool):
    if file_path.exists() and not overwrite:
        print(f"Skipping: {file_path} (exists)")
        return
    file_path.write_text(content, encoding="utf-8")
    print(f"Generated: {file_path}")


def extract_all_types(type_strs: List[str]) -> set:
    import re
    types = set()
    for ts in type_strs:
        if ts is None: continue
        # Find all words: List[Blueprint] -> ['List', 'Blueprint']
        found = re.findall(r'\b\w+\b', ts)
        for f in found:
            types.add(f)
    return types


def resolve_imports(types_used: set, registry: dict, current_name: str, force_dataclass: bool = False) -> List[str]:
    imports = []
    typing_keywords = {"List", "Dict", "Optional", "Any", "Union"}
    used_typing = types_used.intersection(typing_keywords)
    
    if used_typing:
        imports.append(f"from typing import {', '.join(sorted(used_typing))}")
    
    if force_dataclass:
        imports.append("from dataclasses import dataclass")
    
    for t in types_used:
        if t != current_name and t in registry:
            imports.append(registry[t])
            
    return sorted(list(set(imports)))


def generate_aggregate(base_path: Path, agg: Aggregate, env: Environment, overwrite: bool, registry: dict):
    folder = base_path / "domain" / "aggregates"
    ensure_package(folder)
    file_path = folder / f"{to_snake(agg.name)}.py"

    types_used = extract_all_types([a.type for a in agg.attributes])
    # Add types from behaviors if needed, but currently they are just strings
    imports = resolve_imports(types_used, registry, agg.name)

    template = env.get_template("domain/aggregate.py.j2")
    content = template.render(
        name=agg.name,
        description=agg.description,
        attributes=agg.attributes,
        behaviors=agg.behaviors,
        imports=imports,
    )
    write_if_needed(file_path, content, overwrite)


def generate_value_object(base_path: Path, vo: ValueObject, env: Environment, overwrite: bool, registry: dict):
    folder = base_path / "domain" / "value_objects"
    ensure_package(folder)
    file_path = folder / f"{to_snake(vo.name)}.py"

    types_used = extract_all_types([a.type for a in vo.attributes])
    imports = resolve_imports(types_used, registry, vo.name)

    template = env.get_template("domain/value_object.py.j2")
    content = template.render(
        name=vo.name,
        description=vo.description,
        attributes=vo.attributes,
        imports=imports,
    )
    write_if_needed(file_path, content, overwrite)


def generate_port(base_path: Path, port: Port, env: Environment, overwrite: bool, registry: dict):
    folder = base_path / "domain" / "ports"
    ensure_package(folder)
    file_path = folder / f"{to_snake(port.name)}.py"

    types_used = set()
    for op in port.operations:
        types_used.update(extract_all_types([i.type for i in op.inputs]))
        types_used.update(extract_all_types([op.output_type]))

    imports = resolve_imports(types_used, registry, port.name)

    template = env.get_template("domain/port.py.j2")
    content = template.render(
        name=port.name,
        description=port.description,
        operations=port.operations,
        imports=imports,
    )
    write_if_needed(file_path, content, overwrite)


def generate_service(base_path: Path, svc: Service, env: Environment, overwrite: bool, registry: dict):
    folder = base_path / "domain" / "services"
    ensure_package(folder)
    file_path = folder / f"{to_snake(svc.name)}.py"

    types_used = set()
    for op in svc.operations:
        types_used.update(extract_all_types([i.type for i in op.inputs]))
        types_used.update(extract_all_types([op.output_type]))

    imports = resolve_imports(types_used, registry, svc.name)

    template = env.get_template("domain/service.py.j2")
    content = template.render(
        name=svc.name,
        description=svc.description,
        operations=svc.operations,
        imports=imports,
    )
    write_if_needed(file_path, content, overwrite)


def generate_use_case(base_path: Path, uc: UseCase, env: Environment, overwrite: bool, registry: dict):
    folder = base_path / "application" / "use_cases"
    ensure_package(folder)
    file_path = folder / f"{to_snake(uc.name)}.py"

    types_used = set()
    types_used.update(extract_all_types([a.type for a in uc.command.attributes]))
    types_used.update(extract_all_types([a.type for a in uc.result.attributes]))
    types_used.update(extract_all_types(uc.depends_on_services))
    types_used.update(extract_all_types(uc.depends_on_ports))
    
    imports = resolve_imports(types_used, registry, uc.name, force_dataclass=True)

    template = env.get_template("application/use_case.py.j2")
    content = template.render(
        name=uc.name,
        kind=uc.kind,
        description=uc.description,
        command=uc.command,
        result=uc.result,
        depends_on_services=uc.depends_on_services,
        depends_on_ports=uc.depends_on_ports,
        imports=imports,
    )
    write_if_needed(file_path, content, overwrite)


def generate_adapter(base_path: Path, adapter: Adapter, env: Environment, overwrite: bool, ports: List[Port] = None):
    folder = base_path / "infrastructure" / "adapters"
    ensure_package(folder)
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
    write_if_needed(file_path, content, overwrite)


def main():
    parser = argparse.ArgumentParser(description="DDD Bootstrapper CLI")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing files")
    parser.add_argument("--node", type=str, help="Specific node name to generate (e.g., Blueprint)")
    args = parser.parse_args()

    root = Path(__file__).parent.parent
    yaml_path = root / "codegen.yaml"

    if not yaml_path.exists():
        print(f"Error: {yaml_path} not found.")
        sys.exit(1)

    data = load_yaml(yaml_path)
    print(f"Loaded blueprint: {data['name']}")

    target_root = root / "src" / "codegen"
    env = get_jinja_env()

    # Pre-build Type Registry
    registry = {}
    all_contexts = []
    for ctx_data in data.get("contexts", []):
        ctx = parse_context(ctx_data)
        all_contexts.append(ctx)
        
        for agg in ctx.aggregates:
            registry[agg.name] = f"from codegen.domain.aggregates.{to_snake(agg.name)} import {agg.name}"
        for vo in ctx.value_objects:
            registry[vo.name] = f"from codegen.domain.value_objects.{to_snake(vo.name)} import {vo.name}"
        for port in ctx.ports:
            registry[port.name] = f"from codegen.domain.ports.{to_snake(port.name)} import {port.name}"
        for svc in ctx.services:
            registry[svc.name] = f"from codegen.domain.services.{to_snake(svc.name)} import {svc.name}"

    # Shared kernel
    if not args.node:
        generate_shared_kernel(target_root / "domain")

    # 2. Generate Contexts
    all_ports = [p for ctx in all_contexts for p in ctx.ports]
    
    for ctx in all_contexts:
        print(f"Generating context '{ctx.name}'...")

        for agg in ctx.aggregates:
            if not args.node or args.node == agg.name:
                generate_aggregate(target_root, agg, env, args.overwrite, registry)

        for vo in ctx.value_objects:
            if not args.node or args.node == vo.name:
                generate_value_object(target_root, vo, env, args.overwrite, registry)

        for svc in ctx.services:
            if not args.node or args.node == svc.name:
                generate_service(target_root, svc, env, args.overwrite, registry)

        for port in ctx.ports:
            if not args.node or args.node == port.name:
                generate_port(target_root, port, env, args.overwrite, registry)

        for uc in ctx.use_cases:
            if not args.node or args.node == uc.name:
                generate_use_case(target_root, uc, env, args.overwrite, registry)

    # 3. Generate Infrastructure
    shared = data.get("shared", {})
    infra = shared.get("infrastructure", {})
    for adapter_data in infra.get("adapters", []):
        adapter = Adapter(**adapter_data)
        if not args.node or args.node == adapter.name:
            generate_adapter(target_root, adapter, env, args.overwrite, all_ports)


if __name__ == "__main__":
    main()
