# seeds/cli.py
import argparse
from pathlib import Path

from seeds.init_project import InitProjectCommand, ProjectInitializer
from seeds.generate_application_action import AppActionGenerator, GenerateAppActionSpec

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="codegen")
    sub = parser.add_subparsers(dest="command", required=True)

    # init
    init_p = sub.add_parser("init", help="Initialize DDD project structure")
    init_p.add_argument("-t", "--target", default=".", help="Target directory (default: current directory)")
    init_p.add_argument("--package", required=True, help="Business project's Python package name (e.g. myproj)")
    init_p.add_argument("--no-src", action="store_true", help="Do not use src layout")
    init_p.set_defaults(_handler="init")

    # gen
    gen_p = sub.add_parser("gen", help="Generate application actions (use_case/query)")
    gen_p.add_argument("kind", choices=("use_case", "query"), help="Generate a use_case or query")
    gen_p.add_argument("name", help="snake_case name, e.g. init_project")
    gen_p.add_argument("-t", "--target", default=".", help="Target project root directory (default: current directory)")
    gen_p.add_argument("--package", required=True, help="Business project's Python package name (e.g. myproj)")
    gen_p.add_argument("--no-src", action="store_true", help="Do not use src layout")
    gen_p.add_argument("--form", choices=("single", "package"), default="single", help="single file or package directory")
    gen_p.add_argument("--with-mapper", action="store_true", help="Generate optional mapper")
    gen_p.set_defaults(_handler="gen")

    return parser

def _calc_project_pkg_dir(target: str, package: str, use_src_layout: bool) -> Path:
    base = Path(target).resolve()
    return (base / "src" / package) if use_src_layout else (base / package)

def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args._handler == "init":
        cmd = InitProjectCommand(
            target_dir=Path(args.target),
            package_name=args.package,
            use_src_layout=not args.no_src,
        )
        ProjectInitializer().run(cmd)
        return 0

    if args._handler == "gen":
        project_pkg_dir = _calc_project_pkg_dir(args.target, args.package, use_src_layout=not args.no_src)

        spec = GenerateAppActionSpec(
            kind=args.kind,
            name_snake=args.name,
            form=args.form,
            with_mapper=args.with_mapper,
        )

        AppActionGenerator().generate(project_pkg_dir=project_pkg_dir, spec=spec)
        return 0

    return 1

if __name__ == "__main__":
    raise SystemExit(main())