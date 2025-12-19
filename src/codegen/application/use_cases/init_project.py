
from codegen.domain.ports.file_system_port import FileSystemPort

from codegen.domain.ports.template_port import TemplatePort

from codegen.domain.services.naming_service import NamingService

from dataclasses import dataclass


@dataclass(frozen=True)
class InitProjectCommand:
    """Command/Query for InitProject."""
    
    project_name: str  # 
    
    template_root: str  # 
    
    output_root: str  # 
    

@dataclass(frozen=True)
class InitProjectResult:
    """Result of InitProject."""
    
    message: str  # 
    

class InitProjectHandler:
    """Handler for InitProject (command)."""

    def __init__(self, naming_service: NamingService, template_port: TemplatePort, file_system_port: FileSystemPort):
        self.naming_service = naming_service
        self.template_port = template_port
        self.file_system_port = file_system_port

    def execute(self, cmd: InitProjectCommand) -> InitProjectResult:
        """Implement the use case logic."""
        # This handles the "Shared Kernel" generation logic
        from pathlib import Path
        
        # We assume templates are under cmd.template_root
        tpl_root = Path(cmd.template_root)
        shared_tpl_dir = tpl_root / "domain" / "shared"
        
        files = ["models.py.j2", "events.py.j2"]
        for tpl_file in files:
            src_path = shared_tpl_dir / tpl_file
            if not src_path.exists():
                print(f"Warning: Template {src_path} not found.")
                continue
                
            # Read from template root (JinjaAdapter usually handles rendering, 
            # but shared kernel might be simple file copy or use Jinja)
            # Bootstrapper was just reading and writing.
            content = src_path.read_text(encoding="utf-8")
            
            dest_path = f"domain/shared/{tpl_file.replace('.j2', '')}"
            self.file_system_port.write_text(dest_path, content)
            
        return InitProjectResult(message=f"Shared kernel initialized in {cmd.output_root}")