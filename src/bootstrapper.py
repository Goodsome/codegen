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
class BoundedContext:
    name: str
    aggregates: List[Aggregate]
    value_objects: List[ValueObject]

def to_pascal(s: str) -> str:
    return "".join(word.capitalize() for word in s.split("_"))

def to_snake(s: str) -> str:
    import re
    return re.sub(r'(?<!^)(?=[A-Z])', '_', s).lower()

def extract_base_type(type_str: str) -> str:
    """Extracts 'Attribute' from 'List[Attribute]' or returns 'Attribute'."""
    import re
    match = re.search(r'\[(\w+)\]', type_str)
    if match:
        return match.group(1)
    return type_str

def load_yaml(path: Path) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def parse_context(data: dict) -> BoundedContext:
    aggregates = []
    for agg_data in data.get("aggregates", []):
        attrs = [Attribute(**a) for a in agg_data.get("attributes", [])]
        behaviors = agg_data.get("behaviors", [])
        aggregates.append(Aggregate(
            name=agg_data["name"], 
            description=agg_data.get("description", ""), 
            attributes=attrs,
            behaviors=behaviors
        ))
    
    value_objects = []
    for vo_data in data.get("value_objects", []):
        attrs = [Attribute(**a) for a in vo_data.get("attributes", [])]
        value_objects.append(ValueObject(
            name=vo_data["name"],
            description=vo_data.get("description", ""),
            attributes=attrs
        ))
        
    return BoundedContext(name=data["name"], aggregates=aggregates, value_objects=value_objects)

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

def generate_aggregate(base_path: Path, agg: Aggregate, known_vos: List[str] = None):
    folder = base_path / "aggregates"
    folder.mkdir(parents=True, exist_ok=True)
    
    file_path = folder / f"{to_snake(agg.name)}.py"
    
    imports = []
    typing_imports = set()
    typing_keywords = ["List", "Dict", "Optional", "Any", "Union"]

    for attr in agg.attributes:
        # Check for typing keywords
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
    
    # Deduplicate imports
    imports = sorted(list(set(imports)))

    template_dir = Path(__file__).parent / "codegen" / "templates"
    env = Environment(loader=FileSystemLoader(template_dir))
    template = env.get_template("domain/aggregate.py.j2")
    
    content = template.render(
        name=agg.name,
        description=agg.description,
        attributes=agg.attributes,
        behaviors=agg.behaviors,
        imports=imports
    )

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Generated Aggregate: {file_path}")

def generate_value_object(base_path: Path, vo: ValueObject, known_vos: List[str] = None):
    folder = base_path / "value_objects"
    folder.mkdir(parents=True, exist_ok=True)
    
    file_path = folder / f"{to_snake(vo.name)}.py"
    
    imports = []
    typing_imports = set()
    typing_keywords = ["List", "Dict", "Optional", "Any", "Union"]

    for attr in vo.attributes:
        # Check for typing keywords
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
    
    # Deduplicate imports
    imports = sorted(list(set(imports)))

    template_dir = Path(__file__).parent / "codegen" / "templates"
    env = Environment(loader=FileSystemLoader(template_dir))
    template = env.get_template("domain/value_object.py.j2")
    
    content = template.render(
        name=vo.name,
        description=vo.description,
        attributes=vo.attributes,
        imports=imports
    )

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Generated ValueObject: {file_path}")

def main():
    root = Path(__file__).parent.parent
    yaml_path = root / "codegen.yaml"
    
    if not yaml_path.exists():
        print(f"Error: {yaml_path} not found.")
        sys.exit(1)
        
    data = load_yaml(yaml_path)
    print(f"Loaded blueprint: {data['name']}")
    
    target_root = root / "src" / "codegen" / "domain"
    
    # 1. Generate Shared Kernel
    generate_shared_kernel(target_root)
    
    for ctx_data in data.get("contexts", []):
        ctx = parse_context(ctx_data)
        ctx_root = target_root 
        
        print(f"Generating context '{ctx.name}' into {ctx_root}...")
        

        known_vo_names = [vo.name for vo in ctx.value_objects]

        for agg in ctx.aggregates:
            generate_aggregate(ctx_root, agg, known_vo_names)
            
        for vo in ctx.value_objects:
            generate_value_object(ctx_root, vo, known_vo_names)

if __name__ == "__main__":
    main()
