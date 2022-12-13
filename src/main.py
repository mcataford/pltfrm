"""
PLTFRM

Quick tooling to manage docker-based multi-project environments.
---

`pltfrm` is a thin wrapper around repetitive calls to `docker-compose` and
aims to help with use cases where multiple projects living in different
locations are at play without having to `cd` from one place to another
constantly.

It is configuration-file drive such that you can easily integrate it
to your use case.
"""

import subprocess
import pathlib
import sys
import argparse
import typing
import json
import os

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
    parser = argparse.ArgumentParser(prog="pltfrm", description="Makes handling multi-docker-projects environments a bit easier.")

    parser.add_argument("-v", "--verbose", action="store_true", help="Extra output, including forwarded output from docker.")
    parser.add_argument("-a", "--all", action="store_true", help="Applies the command to all known projects.")
    parser.add_argument("--cwd", type=str, default=os.getenv("HOME", "."), help="Directory used as root when looking for configuration files.")

    subparsers = parser.add_subparsers(dest="command", required=True, help="Action to take.")

    parser_start = subparsers.add_parser("start", help="Starts target projects.")

    parser_start.add_argument("targets", nargs="*", help="Target projects to start.")
    parser_start.add_argument("-b", "--build", default=False, action="store_true", help="Build projects before starting.")

    parser_stop = subparsers.add_parser("stop", help="Stops running target projects.")

    parser_stop.add_argument("targets", nargs="*", help="Targets to stop.")

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
