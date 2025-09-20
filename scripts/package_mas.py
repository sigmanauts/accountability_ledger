#!/usr/bin/env python3
"""
Package a case folder into mas_package/<case>-<UTC timestamp>.zip with an embedded manifest.json.

Usage:
  python3 scripts/package_mas.py --case cases/<entity-id>-<slug>
"""
from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
import sys


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser(description="Package case materials for MAS submission")
    ap.add_argument("--case", required=True, help="Path to case folder (e.g., cases/acme-exchange-outage)")
    args = ap.parse_args()

    case_path = Path(args.case)
    if not case_path.exists() or not case_path.is_dir():
        print(f"Case path not found or not a directory: {case_path}", file=sys.stderr)
        return 2

    out_dir = Path("mas_package")
    out_dir.mkdir(exist_ok=True)

    ts_utc = datetime.now(timezone.utc)
    ts_compact = ts_utc.strftime("%Y%m%dT%H%M%SZ")
    out_zip = out_dir / f"{case_path.name}-{ts_compact}.zip"

    # Collect files
    files = [p for p in case_path.rglob("*") if p.is_file()]

    manifest = {
        "case": case_path.name,
        "created_at": ts_utc.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "files": []
    }

    with ZipFile(out_zip, "w", ZIP_DEFLATED) as zf:
        for p in files:
            rel = p.relative_to(case_path)
            arc = Path(case_path.name) / rel
            zf.write(p, arcname=str(arc))
            manifest["files"].append({
                "path": str(arc),
                "bytes": p.stat().st_size,
                "sha256": sha256_file(p)
            })
        zf.writestr("manifest.json", json.dumps(manifest, indent=2))

    print(f"Created MAS package: {out_zip}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
