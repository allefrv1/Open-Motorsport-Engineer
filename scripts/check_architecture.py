from __future__ import annotations

import ast
import sys
import tomllib
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def imported_modules(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    modules: set[str] = set()

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            modules.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            if node.level:
                continue
            if node.module:
                modules.add(node.module)
                if node.module == "ome":
                    modules.update(f"ome.{alias.name}" for alias in node.names)
    return modules


def matches_forbidden(module: str, forbidden: str) -> bool:
    return module == forbidden or module.startswith(f"{forbidden}.")


def module_layer(module: str) -> str | None:
    parts = module.split(".")
    if len(parts) >= 2 and parts[0] == "ome":
        return parts[1]
    return None


def detect_cycles(graph: dict[str, set[str]]) -> list[str]:
    visiting: set[str] = set()
    visited: set[str] = set()
    stack: list[str] = []
    cycles: list[str] = []

    def visit(node: str) -> None:
        if node in visited:
            return
        if node in visiting:
            start = stack.index(node)
            cycle = stack[start:] + [node]
            cycles.append(" -> ".join(cycle))
            return

        visiting.add(node)
        stack.append(node)
        for neighbor in sorted(graph.get(node, set())):
            visit(neighbor)
        stack.pop()
        visiting.remove(node)
        visited.add(node)

    for node in sorted(graph):
        visit(node)
    return sorted(set(cycles))


def check_architecture(repo_root: Path = ROOT) -> list[str]:
    config_path = repo_root / "architecture.toml"
    if not config_path.exists():
        return ["architecture.toml is missing"]

    config = tomllib.loads(config_path.read_text(encoding="utf-8"))
    source_root = repo_root / config["architecture"]["root"]
    if not source_root.exists():
        return [f"architecture root does not exist: {source_root.relative_to(repo_root)}"]

    layers = config.get("layers", {})
    layer_by_path = {settings["path"]: name for name, settings in layers.items()}
    graph: dict[str, set[str]] = defaultdict(set)
    errors: list[str] = []

    for path in sorted(source_root.rglob("*.py")):
        relative = path.relative_to(source_root)
        if not relative.parts:
            continue
        source_layer_path = relative.parts[0]
        source_layer = layer_by_path.get(source_layer_path, source_layer_path)
        imports = imported_modules(path)

        settings = layers.get(source_layer, {})
        for imported in sorted(imports):
            for forbidden in settings.get("forbid", []):
                if matches_forbidden(imported, forbidden):
                    errors.append(
                        f"{path.relative_to(repo_root)}: {source_layer} may not import {imported}"
                    )

            target_layer = module_layer(imported)
            if target_layer and target_layer != source_layer:
                graph[source_layer].add(target_layer)

    for cycle in detect_cycles(graph):
        errors.append(f"architecture dependency cycle: {cycle}")

    return errors


def main() -> int:
    errors = check_architecture()
    if errors:
        print("Architecture check failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print("Architecture check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
