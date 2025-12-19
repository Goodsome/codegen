import sys
import argparse
from pathlib import Path
import yaml

# Add src to path if needed to find codegen package
current_dir = Path(__file__).parent
if str(current_dir) not in sys.path:
    sys.path.append(str(current_dir))

from codegen.infrastructure.adapters.jinja_adapter import JinjaAdapter
from codegen.infrastructure.adapters.o_s_file_system import OSFileSystem
from codegen.domain.services.naming_service import NamingService
from codegen.domain.services.layout_planner import LayoutPlanner
from codegen.domain.services.template_context_builder import TemplateContextBuilder
from codegen.application.use_cases.init_project import InitProjectHandler, InitProjectCommand
from codegen.application.use_cases.generate_action import GenerateActionHandler, GenerateActionCommand

def main():
    parser = argparse.ArgumentParser(description="DDD Codegen CLI")
    parser.add_argument("--init", action="store_true", help="Initialize project structure (Shared Kernel)")
    parser.add_argument("--generate", action="store_true", help="Generate code from codegen.yaml")
    parser.add_argument("--node", type=str, help="Specific node name to generate (placeholder for future)")
    args = parser.parse_args()

    # Default to generate if nothing specified
    if not args.init and not args.generate:
        args.generate = True

    # 1. Dependency Injection / Wiring
    config = {
        "template_root": current_dir / "codegen" / "templates",
        "output_root": current_dir.parent, # Root of project
        "encoding": "utf-8"
    }
    
    naming_svc = NamingService()
    layout_planner = LayoutPlanner()
    context_builder = TemplateContextBuilder()
    
    template_port = JinjaAdapter(config)
    fs_port = OSFileSystem(config)
    
    if args.init:
        handler = InitProjectHandler(
            naming_service=naming_svc,
            template_port=template_port,
            file_system_port=fs_port
        )
        
        cmd = InitProjectCommand(
            project_name="Codegen",
            template_root=str(config["template_root"]),
            output_root=str(config["output_root"])
        )
        result = handler.execute(cmd)
        print(f"Init Result: {result.message}")

    if args.generate:
        handler = GenerateActionHandler(
            naming_service=naming_svc,
            layout_planner=layout_planner,
            template_context_builder=context_builder,
            template_port=template_port,
            file_system_port=fs_port
        )
        
        cmd = GenerateActionCommand(
            feature_name=None, 
            code_form=None,
            output_root=str(config["output_root"])
        )
        result = handler.execute(cmd)
        print(f"Generation Complete. {len(result.files_written)} files processed.")

if __name__ == "__main__":
    main()
