from codegen.python_gen.application.use_cases.generate_schem_json import (
    GenerateSchemaJsonUseCase,
    GenerateSchemaJsonCommand,
)
from codegen.shared.infrastructure.adapters.os_file_system import OSFileSystem


def main():
    from pathlib import Path

    cwd = Path.cwd()
    config = {
        "output_root": cwd,
    }
    file_system_port = OSFileSystem(config=config)
    use_case = GenerateSchemaJsonUseCase(file_system_port=file_system_port)
    cmd = GenerateSchemaJsonCommand()
    use_case.execute(cmd)


if __name__ == "__main__":
    main()
