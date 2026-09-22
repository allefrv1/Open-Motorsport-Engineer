from __future__ import annotations

import re
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
LINK_RE = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")
STATUS_RE = re.compile(r"^Status:\s*\*\*([^*]+)\*\*", re.MULTILINE)

REQUIREMENT_STATUSES = {"Proposed", "Accepted", "Implemented", "Deprecated"}
ADR_STATUSES = {"Proposed", "Accepted", "Superseded", "Deprecated", "Rejected"}


def markdown_target_exists(source: Path, raw_target: str, root: Path) -> bool:
    target = raw_target.strip().strip("<>")
    if not target or target.startswith(("#", "http://", "https://", "mailto:")):
        return True

    target = unquote(target.split("#", 1)[0])
    if not target:
        return True

    candidate = (root / target.lstrip("/")) if target.startswith("/") else (source.parent / target)
    return candidate.resolve().exists()


def file_status(path: Path) -> str | None:
    match = STATUS_RE.search(path.read_text(encoding="utf-8"))
    return match.group(1).strip() if match else None


def indexed_ids(index_path: Path) -> str:
    return index_path.read_text(encoding="utf-8")


def check_docs(repo_root: Path = ROOT) -> list[str]:
    errors: list[str] = []

    for path in sorted(repo_root.rglob("*.md")):
        if any(part in {".git", ".venv", "node_modules"} for part in path.parts):
            continue
        text = path.read_text(encoding="utf-8")
        for target in LINK_RE.findall(text):
            if not markdown_target_exists(path, target, repo_root):
                errors.append(f"{path.relative_to(repo_root)}: broken link -> {target}")

    requirements_dir = repo_root / "docs" / "requirements"
    requirement_index = indexed_ids(requirements_dir / "README.md")
    requirement_ids: set[str] = set()
    for path in sorted(requirements_dir.glob("REQ-*.md")):
        match = re.match(r"(REQ-\d{3})-", path.name)
        if not match:
            errors.append(f"{path.relative_to(repo_root)}: invalid requirement filename")
            continue
        req_id = match.group(1)
        if req_id in requirement_ids:
            errors.append(f"duplicate requirement ID: {req_id}")
        requirement_ids.add(req_id)
        status = file_status(path)
        if status not in REQUIREMENT_STATUSES:
            errors.append(f"{path.relative_to(repo_root)}: invalid requirement status {status!r}")
        if req_id not in requirement_index:
            errors.append(f"{path.relative_to(repo_root)}: missing from requirements index")

    adr_dir = repo_root / "docs" / "adr"
    adr_index = indexed_ids(adr_dir / "README.md")
    adr_ids: set[str] = set()
    for path in sorted(adr_dir.glob("[0-9][0-9][0-9][0-9]-*.md")):
        if path.name.startswith("0000-"):
            continue
        adr_id = path.name[:4]
        if adr_id in adr_ids:
            errors.append(f"duplicate ADR ID: {adr_id}")
        adr_ids.add(adr_id)
        status = file_status(path)
        if status not in ADR_STATUSES:
            errors.append(f"{path.relative_to(repo_root)}: invalid ADR status {status!r}")
        if adr_id not in adr_index:
            errors.append(f"{path.relative_to(repo_root)}: missing from ADR index")

    for path in sorted((repo_root / "docs" / "plans" / "active").glob("*.md")):
        if file_status(path) != "Active":
            errors.append(
                f"{path.relative_to(repo_root)}: active plan must have Status: **Active**"
            )

    for path in sorted((repo_root / "docs" / "plans" / "completed").glob("*.md")):
        if file_status(path) != "Completed":
            errors.append(
                f"{path.relative_to(repo_root)}: completed plan must have Status: **Completed**"
            )

    return errors


def main() -> int:
    errors = check_docs()
    if errors:
        print("Documentation check failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print("Documentation check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
