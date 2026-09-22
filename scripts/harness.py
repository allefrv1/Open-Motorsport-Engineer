from __future__ import annotations

import argparse
import platform
import subprocess
import sys
from collections.abc import Sequence
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

EXPECTED_PYTHON = "3.13.15"
EXPECTED_UV = "0.12.17"
EXPECTED_NODE = "v24.21.0"
EXPECTED_PNPM = "11.27.1"
RUFF_VERSION = "0.16.8"
TY_VERSION = "0.0.82"


class HarnessError(RuntimeError):
    pass


def run(command: Sequence[str], *, cwd: Path = ROOT) -> None:
    printable = " ".join(command)
    print(f"\n> {printable}", flush=True)
    completed = subprocess.run(command, cwd=cwd, check=False)
    if completed.returncode != 0:
        raise HarnessError(f"command failed with exit code {completed.returncode}: {printable}")


def capture(command: Sequence[str], *, cwd: Path = ROOT) -> str:
    completed = subprocess.run(
        command,
        cwd=cwd,
        check=False,
        capture_output=True,
        text=True,
    )
    if completed.returncode != 0:
        raise HarnessError(
            f"command failed with exit code {completed.returncode}: {' '.join(command)}"
        )
    return completed.stdout.strip()


def check_environment() -> None:
    observed = {
        "python": platform.python_version(),
        "uv": capture(["uv", "--version"]).removeprefix("uv "),
        "node": capture(["node", "--version"]),
        "pnpm": capture(["pnpm", "--version"]),
    }
    expected = {
        "python": EXPECTED_PYTHON,
        "uv": EXPECTED_UV,
        "node": EXPECTED_NODE,
        "pnpm": EXPECTED_PNPM,
    }
    mismatches = [
        f"{name}: expected {expected[name]}, got {observed[name]}"
        for name in expected
        if observed[name] != expected[name]
    ]
    if mismatches:
        raise HarnessError("toolchain mismatch:\n- " + "\n- ".join(mismatches))
    print("Toolchain versions are correct.")


def ruff(*args: str) -> None:
    run(["uvx", "--from", f"ruff=={RUFF_VERSION}", "ruff", *args])


def ty(*args: str) -> None:
    run(["uvx", "--from", f"ty=={TY_VERSION}", "ty", *args])


def command_format() -> None:
    ruff("check", "--fix", ".")
    ruff("format", ".")


def command_lint() -> None:
    ruff("format", "--check", ".")
    ruff("check", ".")


def command_type() -> None:
    ty("check", "backend/src", "scripts")


def command_test() -> None:
    run([sys.executable, "-m", "unittest", "discover", "-s", "tests", "-p", "test_*.py", "-v"])
    run(["pnpm", "--dir", "frontend", "test"])


def command_docs() -> None:
    run([sys.executable, "scripts/check_docs.py"])


def command_arch() -> None:
    run([sys.executable, "scripts/check_architecture.py"])


def command_fixtures() -> None:
    run([sys.executable, "scripts/check_fixtures.py"])


def command_verify() -> None:
    check_environment()
    run(["uv", "lock", "--check"])
    command_lint()
    command_type()
    command_test()
    command_docs()
    command_arch()
    command_fixtures()
    print("\nOME harness verification passed.")


def main() -> int:
    parser = argparse.ArgumentParser(description="OME canonical engineering harness")
    parser.add_argument(
        "command",
        choices=["format", "lint", "type", "test", "docs", "arch", "fixtures", "verify", "env"],
    )
    args = parser.parse_args()

    commands = {
        "format": command_format,
        "lint": command_lint,
        "type": command_type,
        "test": command_test,
        "docs": command_docs,
        "arch": command_arch,
        "fixtures": command_fixtures,
        "verify": command_verify,
        "env": check_environment,
    }

    try:
        commands[args.command]()
    except HarnessError as exc:
        print(f"\nHARNESS FAILURE: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
