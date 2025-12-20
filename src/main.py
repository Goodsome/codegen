import argparse
import sys
from pathlib import Path

from codegen.application.use_cases.generate_code import (
    GenerateCodeHandler,
    GenerateCodeCommand,
)
from codegen.domain.services.scaffold_service import ScaffoldService
from codegen.infrastructure.adapters.yaml_blueprint_loader import YamlBlueprintLoader

current_dir = Path(__file__).parent
if str(current_dir) not in sys.path:
    sys.path.append(str(current_dir))

from codegen.infrastructure.adapters.jinja_adapter import JinjaAdapter
from codegen.infrastructure.adapters.o_s_file_system import OSFileSystem


def main():
    parser = argparse.ArgumentParser(description="DDD Codegen CLI")
    parser.add_argument(
        "--overwrite", action="store_true", help="Overwrite existing files"
    )
    parser.add_argument(
        "--node",
        type=str,
        help="Specific node name to generate (placeholder for future)",
    )
    args = parser.parse_args()

    if args.overwrite is None:
        args.overwrite = False

    # 1. Dependency Injection / Wiring
    config = {
        "template_root": current_dir / "codegen" / "templates",
        "output_root": current_dir.parent,  # Root of project
        "encoding": "utf-8",
    }

    scaffold_service = ScaffoldService()

    template_port = JinjaAdapter(config)
    fs_port = OSFileSystem(config)

    handler = GenerateCodeHandler(
        scaffold_service=scaffold_service,
        template_port=template_port,
        file_system_port=fs_port,
        blueprint_loader=YamlBlueprintLoader(),
    )

    cmd = GenerateCodeCommand(overwrite=False, node=args.node)
    result = handler.execute(cmd)
    print(f"Generation Complete. {len(result.files_written)} files processed.")


if __name__ == "__main__":
    main()
