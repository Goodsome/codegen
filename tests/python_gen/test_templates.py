from codegen.python_gen.domain.value_objects.type_annotation_spec import (
    TypeAnnotationSpec,
)
from codegen.python_gen.domain.value_objects.parameter_spec import ParameterSpec
from codegen.python_gen.domain.value_objects.class_spec import ClassSpec
from codegen.python_gen.domain.value_objects.module_spec import ModuleSpec
import pytest
from pathlib import Path
from jinja2 import Environment, FileSystemLoader, Template


# 1. 定义一个 Fixture 来获取 Template 目录的路径
@pytest.fixture(scope="module")
def template_dir() -> Path:
    """
    动态计算 templates 目录的绝对路径。
    基于: tests/python_gen/test_templates.py
    目标: src/codegen/python_gen/templates
    """
    # 获取当前测试文件的目录 (tests/python_gen)
    current_test_dir: Path = Path(__file__).resolve().parent

    # 回溯到项目根目录 (假设 tests 和 src 同级)
    # tests/python_gen -> tests -> project_root
    project_root: Path = current_test_dir.parents[1]

    # 拼接目标路径
    target_dir: Path = project_root / "src" / "codegen" / "python_gen" / "templates"

    # 可以在这里加一个断言，确保路径真的存在，方便调试
    assert target_dir.exists(), f"Template directory not found at: {target_dir}"

    return target_dir


# 2. 定义一个 Fixture 来初始化 Jinja2 Environment (如果需要)
@pytest.fixture(scope="module")
def jinja_env(template_dir: Path) -> Environment:
    """
    初始化 Jinja2 环境，加载器指向正确的目录
    """
    return Environment(loader=FileSystemLoader(str(template_dir)))


@pytest.fixture(scope="module")
def module_spec() -> ModuleSpec:
    class_spec = ClassSpec(
        name="ModuleSpec",
        decorators=[],
        inheritance=["ValueObject"],
        attributes=[
            ParameterSpec(name="path", annotation=TypeAnnotationSpec(name="str")),
            ParameterSpec(
                name="functions",
                annotation=TypeAnnotationSpec(name="list[FunctionSpec]"),
            ),
            ParameterSpec(
                name="classes",
                annotation=TypeAnnotationSpec(name="list[ClassSpec]"),
            ),
            ParameterSpec(
                name="imports",
                annotation=TypeAnnotationSpec(name="list[ImportSpec]"),
            ),
        ],
        methods=[],
    )
    return ModuleSpec.create(
        name="module.py",
        classes=[class_spec],
    )


# 3. 编写测试用例
def test_class_template_exists(template_dir: Path) -> None:
    """
    测试: 验证 class.j2 文件是否存在
    """
    template_file: Path = template_dir / "class.j2"
    assert template_file.exists()
    assert template_file.is_file()


def test_render_module_template(
    jinja_env: Environment, module_spec: ModuleSpec
) -> None:
    template: Template = jinja_env.get_template("module.j2")
    context = {"module_spec": module_spec}
    rendered_content = template.render(context)
    print(rendered_content)
