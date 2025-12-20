import sys
import argparse
from pathlib import Path
import yaml

from codegen.application.use_cases.generate_code import (
    GenerateCodeHandler,
    GenerateCodeCommand,
)
from codegen.domain.services.scaffold_service import ScaffoldService

# Add src to path if needed to find codegen package
current_dir = Path(__file__).parent
if str(current_dir) not in sys.path:
    sys.path.append(str(current_dir))

from codegen.infrastructure.adapters.jinja_adapter import JinjaAdapter
from codegen.infrastructure.adapters.o_s_file_system import OSFileSystem
from codegen.domain.services.naming_service import NamingService
from codegen.domain.services.template_context_builder import TemplateContextBuilder

def main():
    parser = argparse.ArgumentParser(description="DDD Codegen CLI")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing files")
    parser.add_argument("--node", type=str, help="Specific node name to generate (placeholder for future)")
    args = parser.parse_args()

    if args.overwrite is None:
        args.overwrite = False

    # 1. Dependency Injection / Wiring
    config = {
        "template_root": current_dir / "codegen" / "templates",
        "output_root": current_dir.parent, # Root of project
        "encoding": "utf-8"
    }
    
    naming_svc = NamingService()
    scaffold_service = ScaffoldService()
    context_builder = TemplateContextBuilder()
    
    template_port = JinjaAdapter(config)
    fs_port = OSFileSystem(config)
    
    handler = GenerateCodeHandler(
        naming_service=naming_svc,
        scaffold_service=scaffold_service,
        template_context_builder=context_builder,
        template_port=template_port,
        file_system_port=fs_port
    )
    
    cmd = GenerateCodeCommand(
        overwrite=False,
        node=args.node
    )
    result = handler.execute(cmd)
    print(f"Generation Complete. {len(result.files_written)} files processed.")

if __name__ == "__main__":
    main()
