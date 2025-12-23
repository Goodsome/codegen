from pathlib import Path

import pytest

from codegen.bootstrap import Container
from codegen.python_gen.domain.value_objects.class_spec import ClassSpec
from codegen.python_gen.domain.value_objects.import_spec import ImportSpec
from codegen.python_gen.domain.value_objects.module_spec import ModuleSpec
from codegen.python_gen.domain.value_objects.parameter_spec import ParameterSpec
from codegen.python_gen.domain.value_objects.type_annotation_spec import (
    TypeAnnotationSpec,
)


# 1. 定义一个 Fixture 来获取 Template 目录的路径
@pytest.fixture(scope="module")
def project_root() -> Path:
    current_test_dir: Path = Path(__file__).resolve().parent
    project_root: Path = current_test_dir.parents[2]
    return project_root


@pytest.fixture(scope="module")
def container(project_root: Path) -> Container:
    config = {
        "template_root": project_root / "src" / "codegen" / "python_gen" / "templates",
        "output_root": project_root / "target",
    }
    return Container(
        config=config,
    )


@pytest.fixture(scope="module")
def module_spec() -> ModuleSpec:
    path = "python_gen/domain/value_objects"
    imports = [
        ImportSpec(
            module="pydantic.fields",
            name="Field",
        ),
        ImportSpec(
            module="codegen.domain.shared.models",
            name="ValueObject",
        ),
        ImportSpec(
            module="codegen.python_gen.domain.value_objects.class_spec",
            name="ClassSpec",
        ),
        ImportSpec(
            module="codegen.python_gen.domain.value_objects.function_spec",
            name="FunctionSpec",
        ),
        ImportSpec(
            module="codegen.python_gen.domain.value_objects.import_spec",
            name="ImportSpec",
        ),
    ]
    class_spec = ClassSpec(
        name="ModuleSpec",
        decorators=[],
        inheritance=["ValueObject"],
        attributes=[
            ParameterSpec(name="path", annotation=TypeAnnotationSpec(name="str")),
            ParameterSpec(
                name="functions",
                annotation=TypeAnnotationSpec(name="list[FunctionSpec]"),
                default="Field(default_factory=list)",
            ),
            ParameterSpec(
                name="classes",
                annotation=TypeAnnotationSpec(name="list[ClassSpec]"),
                default="Field(default_factory=list)",
            ),
            ParameterSpec(
                name="imports",
                annotation=TypeAnnotationSpec(name="list[ImportSpec]"),
                default="Field(default_factory=list)",
            ),
        ],
        methods=[],
    )
    return ModuleSpec.create(
        directory=path,
        filename="module_spec.py",
        imports=imports,
        classes=[class_spec],
    )


def test_generate_module(container: Container, module_spec: ModuleSpec):
    from codegen.python_gen.application.use_cases.generate_module import (
        GenerateModuleCommand,
    )

    cmd = GenerateModuleCommand(module_spec=module_spec, overwrite=True)
    use_case = container.generate_module_use_case()
    result = use_case.execute(cmd)
    assert result.result == "success"
