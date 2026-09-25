from __future__ import annotations

import shutil
from pathlib import Path

from fastapi import UploadFile


def stage_single_csv_upload(
    root: Path,
    *,
    csv_upload: UploadFile,
    fallback: str = "telemetry.csv",
) -> Path:
    root.mkdir(parents=True, exist_ok=True)
    csv_name = _safe_csv_name(csv_upload.filename, fallback=fallback)
    csv_path = root / csv_name
    _copy_upload(csv_upload, csv_path)
    return csv_path


def stage_ome_csv_bundle(
    root: Path,
    *,
    lap_side: str,
    csv_upload: UploadFile,
    sidecar_upload: UploadFile,
) -> Path:
    directory = root / lap_side
    directory.mkdir(parents=True, exist_ok=False)

    csv_name = _safe_csv_name(csv_upload.filename, fallback=f"lap-{lap_side}.csv")
    csv_path = directory / csv_name
    sidecar_path = csv_path.with_suffix(".ome.json")

    _copy_upload(csv_upload, csv_path)
    _copy_upload(sidecar_upload, sidecar_path)

    return csv_path


def _safe_csv_name(filename: str | None, *, fallback: str) -> str:
    candidate = (filename or "").replace("\\", "/")
    basename = candidate.rsplit("/", 1)[-1].strip()

    if basename in {"", ".", ".."}:
        return fallback

    return basename


def _copy_upload(upload: UploadFile, destination: Path) -> None:
    upload.file.seek(0)
    with destination.open("wb") as target:
        shutil.copyfileobj(upload.file, target, length=1024 * 1024)
