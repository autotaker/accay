from __future__ import annotations

import argparse
from pathlib import Path

from accay.project import init_project, install_skills


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if not hasattr(args, "handler"):
        parser.print_help()
        return 2

    return args.handler(args)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="accay")
    parser.add_argument(
        "--root",
        type=Path,
        default=Path.cwd(),
        help="Repository root to operate on. Defaults to the current directory.",
    )

    subparsers = parser.add_subparsers(dest="command")

    init_parser = subparsers.add_parser("init", help="Create Accay config and directories.")
    init_parser.set_defaults(handler=_init)

    install_parser = subparsers.add_parser("install", help="Install Accay agent skills.")
    install_parser.set_defaults(handler=_install)

    validate_parser = subparsers.add_parser("validate", help="Validate Accay artifacts.")
    validate_parser.set_defaults(handler=_planned)

    regression_parser = subparsers.add_parser("regression", help="Run acceptance regression.")
    regression_parser.add_argument("--junit", action="append", default=[])
    regression_parser.set_defaults(handler=_planned)

    serve_parser = subparsers.add_parser("serve", help="Serve the local Accay dashboard.")
    serve_parser.set_defaults(handler=_planned)

    system_parser = subparsers.add_parser("system", help="System-level commands.")
    system_subparsers = system_parser.add_subparsers(dest="system_command")

    system_validate = system_subparsers.add_parser("validate")
    system_validate.set_defaults(handler=_planned)

    system_pack = system_subparsers.add_parser("pack")
    system_pack_subparsers = system_pack.add_subparsers(dest="pack_command")
    desk_debug = system_pack_subparsers.add_parser("desk-debug")
    desk_debug.add_argument("--scenario", required=True)
    desk_debug.set_defaults(handler=_planned)

    component_parser = subparsers.add_parser("component", help="Component-level commands.")
    component_subparsers = component_parser.add_subparsers(dest="component_command")

    component_validate = component_subparsers.add_parser("validate")
    component_validate.add_argument("component")
    component_validate.set_defaults(handler=_planned)

    component_regression = component_subparsers.add_parser("regression")
    component_regression.add_argument("component")
    component_regression.add_argument("--junit", action="append", default=[])
    component_regression.set_defaults(handler=_planned)

    component_pack = component_subparsers.add_parser("pack")
    component_pack_subparsers = component_pack.add_subparsers(dest="pack_command")
    review = component_pack_subparsers.add_parser("review")
    review.add_argument("component")
    review.add_argument("--case", required=True, dest="case_id")
    review.set_defaults(handler=_planned)

    return parser


def _init(args: argparse.Namespace) -> int:
    result = init_project(args.root)
    for path in result.created:
        print(f"created {path}")
    for path in result.existing:
        print(f"exists  {path}")
    return 0


def _install(args: argparse.Namespace) -> int:
    result = install_skills(args.root)
    for path in result.created:
        print(f"created {path}")
    for path in result.existing:
        print(f"exists  {path}")
    return 0


def _planned(args: argparse.Namespace) -> int:
    command = " ".join(part for part in vars(args).values() if isinstance(part, str))
    print(f"{command or 'command'} is planned for the MVP harness.")
    return 0
