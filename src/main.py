"""
"""

import subprocess
import pathlib
import sys
import argparse
import typing
import json

Command = typing.Union[
    typing.Literal["start"],
    typing.Literal["stop"],
    typing.Literal["stop-all"],
    typing.Literal["build"],
]


class CommandLineArguments(typing.NamedTuple):
    """
    Sanitized command-line arguments. Values are piped
    in from the parser and normalized.
    """

    cwd: str
    command: Command
    targets: typing.List[str]
    build: bool
    apply_all: bool


def _run(
    args: typing.List[str], cwd: str, capture: bool = False
) -> subprocess.CompletedProcess:
    """
    Wrapper around subprocess.run that sets common parameters. Always returns
    the CompletedProcess object corresponding to what was executed.
    """
    return subprocess.run(
        args, cwd=cwd, check=True, encoding="utf8", capture_output=capture
    )


def get_argument_parser() -> argparse.ArgumentParser:
    """
    Prepares the argument parser.
    """
    parser = argparse.ArgumentParser()

    parser.add_argument("-v", "--verbose", action="store_true")
    parser.add_argument("-a", "--all", action="store_true")
    parser.add_argument("--cwd", type=str, default=".")

    subparsers = parser.add_subparsers(dest="command", required=True)

    parser_start = subparsers.add_parser("start")

    parser_start.add_argument("targets", nargs="*")
    parser_start.add_argument("-b", "--build", default=False, action="store_true")

    parser_stop = subparsers.add_parser("stop")

    parser_stop.add_argument("targets", nargs="*")

    return parser


def yellow(text: str) -> str:
    """Formats text with yellow colouring"""
    return f"\033[93m{text}\033[00m"


def green(text: str) -> str:
    """Formats text with green colouring"""
    return f"\033[92m{text}\033[00m"


def red(text: str) -> str:
    """Formats text with red colouring"""
    return f"\033[91m{text}\033[00m"


def start(args: CommandLineArguments, configuration):
    """
    Starts the projects referred to by the `projects` argument.

    If the `build` flag is truthy, the stack will be rebuilt before being
    started (the equivalent of using the --build flag on compose).
    """
    call_args = ["docker-compose", "up", "-d"]

    if args.build:
        call_args.append("--build")

    targets = configuration["projects"].keys() if args.apply_all else args.targets

    for project in targets:
        project_root = pathlib.Path(configuration["projects"][project])
        _run(call_args, str(project_root))
        print(green(f"Started {project}"))


def build(args: CommandLineArguments, configuration):
    """
    Builds the specific projects' images.
    """
    targets = configuration["projects"].keys() if args.apply_all else args.targets

    for target in targets:
        project_root = pathlib.Path(configuration["projects"][target])
        _run(["docker-compose", "build"], cwd=str(project_root))
        print(green(f"Built fresh {target}"))


def stop(args: CommandLineArguments, configuration):
    """
    Stops the given project if it's running.
    """
    targets = configuration["projects"].keys() if args.apply_all else args.targets

    for target in targets:
        project_root = pathlib.Path(configuration["projects"][target])

        out = _run(
            ["docker-compose", "ps"],
            capture=True,
            cwd=str(project_root),
        )

        ps_out = out.stdout.strip().split("\n")[2:]

        if not ps_out:
            print(yellow(f"{target} is not running."))
            continue

        _run(["docker-compose", "down"], cwd=str(project_root))
        print(green(f"{target} stopped."))


def main():
    """
    Main tool runtime.
    """
    parsed_args = get_argument_parser().parse_args(sys.argv[1:])

    config_path = (
        pathlib.Path(parsed_args.cwd)
        .joinpath(".config", "pltfrm", "pltfrm.json")
        .resolve()
    )

    if not config_path.exists():
        raise RuntimeError("Configuration file not found.")

    with open(
        config_path,
        "r",
        encoding="utf8",
    ) as configuration_file:
        configuration = json.loads(configuration_file.read())

    args = CommandLineArguments(
        command=parsed_args.command,
        targets=parsed_args.targets,
        build=parsed_args.build if hasattr(parsed_args, "build") else None,
        apply_all=parsed_args.all,
        cwd=parsed_args.cwd,
    )

    handlers = {
        "start": start,
        "stop": stop,
        "build": build,
    }

    handlers.get(args.command)(args, configuration)
