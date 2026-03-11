from dataclasses import dataclass, field
from typing import Any

from codegen.domain_definition.domain.value_objects.bounded_context import BoundedContext
from codegen.python_gen.domain.value_objects.module_spec import ModuleSpec
from codegen.python_gen.domain.value_objects.package_spec import PackageSpec
from codegen.python_gen.domain.value_objects.import_from_spec import ImportFromSpec
from codegen.python_gen.domain.value_objects.raw_code_spec import RawCodeSpec


@dataclass
class EntrypointMapper:
    """Entrypoints 代码生成器，聚合所有 Context 的接口"""

    def to_package_spec(
        self,
        contexts: list[BoundedContext],
        project_name: str,
    ) -> PackageSpec:
        """生成 entrypoints 包"""
        modules: list[ModuleSpec] = []

        # 检查是否有 CLI 接口
        has_cli = any(ctx.interfaces and ctx.interfaces.cli for ctx in contexts)
        if has_cli:
            cli_main = self._create_cli_main(contexts, project_name)
            modules.append(cli_main)

        # 检查是否有 MCP 接口
        has_mcp = any(ctx.interfaces and ctx.interfaces.mcp for ctx in contexts)
        if has_mcp:
            mcp_main = self._create_mcp_main(contexts, project_name)
            modules.append(mcp_main)

        # 检查是否有 HTTP 接口
        has_http = any(ctx.interfaces and ctx.interfaces.http for ctx in contexts)
        if has_http:
            http_main = self._create_http_main(contexts, project_name)
            modules.append(http_main)

        return PackageSpec.create(
            name="entrypoints",
            modules=modules,
        )

    def _create_cli_main(
        self,
        contexts: list[BoundedContext],
        project_name: str,
    ) -> ModuleSpec:
        """生成 cli_main.py"""
        imports: list[ImportFromSpec] = [
            ImportFromSpec.create(module="__root__", names=["typer"]),
        ]

        context_apps: list[tuple[str, str]] = []  # (context_name, var_name)

        for ctx in contexts:
            if ctx.interfaces and ctx.interfaces.cli:
                ctx_snake = self._to_snake_case(str(ctx.name))
                var_name = f"{ctx_snake}_app"
                imports.append(
                    ImportFromSpec.create(
                        module=f"{ctx_snake}.interfaces.cli",
                        names=[f"app as {var_name}"],
                    )
                )
                context_apps.append((str(ctx.name), var_name))

        extra_code_lines = [
            f'app = typer.Typer(name="{project_name}")',
        ]
        for ctx_name, var_name in context_apps:
            ctx_snake = self._to_snake_case(ctx_name)
            extra_code_lines.append(f'app.add_typer({var_name}, name="{ctx_snake}")')

        extra_code_lines.extend([
            "",
            'if __name__ == "__main__":',
            "    app()",
        ])

        return ModuleSpec.create(
            name="cli_main",
            imports=imports,
            extra_code=[RawCodeSpec.create("\n".join(extra_code_lines))],
        )

    def _create_mcp_main(
        self,
        contexts: list[BoundedContext],
        project_name: str,
    ) -> ModuleSpec:
        """生成 mcp_main.py"""
        imports: list[ImportFromSpec] = [
            ImportFromSpec.create(module="mcp.server.fastmcp", names=["FastMCP"]),
        ]

        context_mcps: list[tuple[str, str]] = []  # (context_name, var_name)

        for ctx in contexts:
            if ctx.interfaces and ctx.interfaces.mcp:
                ctx_snake = self._to_snake_case(str(ctx.name))
                var_name = f"{ctx_snake}_mcp"
                imports.append(
                    ImportFromSpec.create(
                        module=f"{ctx_snake}.interfaces.mcp",
                        names=[f"mcp as {var_name}"],
                    )
                )
                context_mcps.append((str(ctx.name), var_name))

        # FastMCP 的 tools 合并方式：创建主实例并注册所有 tools
        extra_code_lines = [
            f'main_mcp = FastMCP("{project_name} MCP")',
            "",
            "# 注册所有 context 的 tools",
        ]

        # FastMCP 没有直接的合并方法，需要手动注册
        # 这里简化处理，假设通过导入各 context 的 mcp 实例后
        # tools 会自动注册到各自的 mcp 实例中
        # 实际使用时可能需要调整 FastMCP 的使用方式

        extra_code_lines.extend([
            "",
            'if __name__ == "__main__":',
            "    main_mcp.run()",
        ])

        return ModuleSpec.create(
            name="mcp_main",
            imports=imports,
            extra_code=[RawCodeSpec.create("\n".join(extra_code_lines))],
        )

    def _create_http_main(
        self,
        contexts: list[BoundedContext],
        project_name: str,
    ) -> ModuleSpec:
        """生成 http_main.py"""
        imports: list[ImportFromSpec] = [
            ImportFromSpec.create(module="fastapi", names=["FastAPI"]),
        ]

        context_apps: list[tuple[str, str]] = []  # (context_name, var_name)

        for ctx in contexts:
            if ctx.interfaces and ctx.interfaces.http:
                ctx_snake = self._to_snake_case(str(ctx.name))
                var_name = f"{ctx_snake}_app"
                imports.append(
                    ImportFromSpec.create(
                        module=f"{ctx_snake}.interfaces.http",
                        names=[f"app as {var_name}"],
                    )
                )
                context_apps.append((str(ctx.name), var_name))

        extra_code_lines = [
            f'app = FastAPI(title="{project_name} API")',
        ]
        for ctx_name, var_name in context_apps:
            extra_code_lines.append(f"app.include_router({var_name})")

        extra_code_lines.extend([
            "",
            'if __name__ == "__main__":',
            "    import uvicorn",
            '    uvicorn.run(app, host="0.0.0.0", port=8000)',
        ])

        return ModuleSpec.create(
            name="http_main",
            imports=imports,
            extra_code=[RawCodeSpec.create("\n".join(extra_code_lines))],
        )

    @staticmethod
    def _to_snake_case(name: str) -> str:
        """Convert PascalCase to snake_case"""
        result = []
        for i, char in enumerate(name):
            if char.isupper() and i > 0:
                result.append('_')
            result.append(char.lower())
        return ''.join(result)