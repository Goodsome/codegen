import os
from pathlib import Path

# 配置：需要忽略的目录和文件后缀
IGNORE_DIRS = {'.git', '__pycache__', '.idea', '.vscode', 'venv', '.venv', 'build', 'dist', 'codegen.egg-info'}
INCLUDE_EXTENSIONS = {'.py', '.yaml', '.toml', '.json', '.j2', '.md'}

def merge_project_files(root_dir: str = ".", output_file: str = "project_context.txt"):
    root_path = Path(root_dir).resolve()

    with open(output_file, "w", encoding="utf-8") as outfile:
        # 写入文件头信息
        outfile.write(f"# Project Snapshot generated for AI Context\n")
        outfile.write(f"# Root: {root_path.name}\n\n")

        for file_path in root_path.rglob("*"):
            # 过滤目录和被忽略的文件夹
            if file_path.is_dir():
                continue

            # 检查是否在忽略目录中
            parts = file_path.relative_to(root_path).parts
            if any(part in IGNORE_DIRS for part in parts):
                continue

            # 过滤文件扩展名
            if file_path.suffix not in INCLUDE_EXTENSIONS:
                continue

            # 获取相对路径
            rel_path = file_path.relative_to(root_path)

            try:
                content = file_path.read_text(encoding="utf-8")
                # 写入分隔符和文件路径（这行最关键）
                outfile.write(f"\n{'='*20} File: {rel_path} {'='*20}\n")
                outfile.write(content)
                outfile.write("\n")
            except Exception as e:
                print(f"Skipping binary or unreadable file: {rel_path} ({e})")

    print(f"✅ 完成！所有代码已合并至: {output_file}")
    print(f"   文件大小: {os.path.getsize(output_file) / 1024:.2f} KB")

if __name__ == "__main__":
    merge_project_files()