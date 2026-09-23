from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def check_public_fixtures(repo_root: Path = ROOT) -> list[str]:
    fixture_root = repo_root / "fixtures" / "public"
    manifest_path = fixture_root / "manifest.json"
    if not manifest_path.exists():
        return ["fixtures/public/manifest.json is missing"]

    manifest = load_json(manifest_path)
    entries = manifest.get("fixtures", [])
    listed_paths: set[str] = set()
    errors: list[str] = []
    required = {
        "id",
        "path",
        "kind",
        "format_family",
        "source_repository",
        "source_path",
        "license",
        "license_path",
        "redistribution",
        "purpose",
    }

    ids: set[str] = set()
    for entry in entries:
        missing = sorted(required - set(entry))
        if missing:
            errors.append(f"fixture entry missing fields {missing}: {entry.get('id', '<unknown>')}")
            continue

        fixture_id = entry["id"]
        if fixture_id in ids:
            errors.append(f"duplicate fixture id: {fixture_id}")
        ids.add(fixture_id)

        relative = entry["path"]
        listed_paths.add(relative)
        if not (fixture_root / relative).is_file():
            errors.append(f"fixture file missing: fixtures/public/{relative}")

        license_path = repo_root / entry["license_path"]
        if not license_path.is_file():
            errors.append(f"fixture license file missing: {entry['license_path']}")

        if not isinstance(entry["purpose"], list) or not entry["purpose"]:
            errors.append(f"fixture purpose must be a non-empty list: {fixture_id}")

    ignored_names = {"README.md", "THIRD_PARTY_NOTICES.md", "manifest.json"}
    for path in fixture_root.rglob("*"):
        if not path.is_file() or "licenses" in path.parts or path.name in ignored_names:
            continue
        relative = path.relative_to(fixture_root).as_posix()
        if relative not in listed_paths:
            errors.append(f"public fixture is not listed in manifest: {relative}")

    return errors


def check_ome_fixture(repo_root: Path = ROOT) -> list[str]:
    fixture_root = repo_root / "fixtures" / "ome"
    errors: list[str] = []
    sidecars = sorted(fixture_root.glob("*.ome.json"))

    if not sidecars:
        return ["fixtures/ome must contain at least one .ome.json fixture sidecar"]

    for sidecar_path in sidecars:
        stem = sidecar_path.name.removesuffix(".ome.json")
        csv_path = sidecar_path.with_name(f"{stem}.csv")
        label = f"fixtures/ome/{stem}"

        if not csv_path.is_file():
            errors.append(f"{label}.csv is missing")
            continue

        sidecar = load_json(sidecar_path)
        if sidecar.get("ome_csv_version") != "0.1":
            errors.append(f"{label}.ome.json must declare ome_csv_version 0.1")

        with csv_path.open(newline="", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            if reader.fieldnames is None or not reader.fieldnames:
                errors.append(f"{label}.csv has no header")
                continue
            if reader.fieldnames[0] != "time_s":
                errors.append(f"{label}.csv first column must be time_s")

            rows = list(reader)
            if not rows:
                errors.append(f"{label}.csv must contain data rows")
                continue

            try:
                times = [float(row["time_s"]) for row in rows]
            except (TypeError, ValueError):
                errors.append(f"{label}.csv time_s values must be decimal numbers")
                continue

            if any(
                current <= previous for previous, current in zip(times, times[1:], strict=False)
            ):
                errors.append(f"{label}.csv time_s must be strictly increasing")

            channel_defs = sidecar.get("channels", {})
            csv_channels = set(reader.fieldnames[1:])
            if set(channel_defs) != csv_channels:
                errors.append(
                    f"{label} sidecar channel keys must exactly match non-time CSV columns "
                    f"(csv={sorted(csv_channels)}, sidecar={sorted(channel_defs)})"
                )

    return errors


def check_fixtures(repo_root: Path = ROOT) -> list[str]:
    return check_public_fixtures(repo_root) + check_ome_fixture(repo_root)


def main() -> int:
    errors = check_fixtures()
    if errors:
        print("Fixture check failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print("Fixture check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
