#!/usr/bin/env python3
"""
Compute/verify per-directory SHA-256 manifests (SHA256SUMS.txt).

- Scans these top-level trees: evidence/, cases/, analysis/, mas_package/
- For each directory that contains regular files (non-hidden), maintains a manifest with lines:
    <sha256>  <filename>
- Only files directly in that directory are listed (not recursive per manifest).
- Hidden files (starting with .) and the manifest itself are ignored.

Usage:
  - Write/update manifests:    python3 scripts/compute_checksums.py
  - Verify manifests only:     python3 scripts/compute_checksums.py --check
"""
from __future__ import annotations

import argparse
import hashlib
import os
from pathlib import Path
import sys

TOPS = ("evidence", "cases", "analysis", "mas_package")
MANIFEST = "SHA256SUMS.txt"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def list_files_for_manifest(dirpath: Path) -> list[Path]:
    files = []
    for name in sorted(os.listdir(dirpath)):
        if name.startswith(".") or name == MANIFEST:
            continue
        p = dirpath / name
        if p.is_file():
            files.append(p)
    return files


def write_manifest(dirpath: Path) -> None:
    files = list_files_for_manifest(dirpath)
    if not files:
        # Remove empty manifest if present
        m = dirpath / MANIFEST
        if m.exists():
            m.unlink()
        return
    lines = []
    for p in files:
        digest = sha256_file(p)
        lines.append(f"{digest}  {p.name}")
    (dirpath / MANIFEST).write_text("\n".join(lines) + "\n", encoding="utf-8")


def verify_manifest(dirpath: Path) -> list[str]:
    problems: list[str] = []
    manifest = dirpath / MANIFEST
    files = list_files_for_manifest(dirpath)
    names = {p.name for p in files}

    recorded: dict[str, str] = {}
    if not manifest.exists():
        if files:
            problems.append(f"Missing {MANIFEST} in {dirpath}")
        return problems

    for line in manifest.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            digest, fname = line.split(None, 1)
        except ValueError:
            problems.append(f"Malformed line in {manifest}: {line}")
            continue
        fname = fname.strip().lstrip("*").lstrip("./")
        recorded[fname] = digest

    # Check for extras/missing
    missing = sorted(n for n in recorded.keys() if n not in names)
    extra = sorted(n for n in names if n not in recorded.keys())
    if missing:
        problems.append(f"Manifest lists missing files in {dirpath}: {missing}")
    if extra:
        problems.append(f"Files present but not listed in manifest for {dirpath}: {extra}")

    # Check digests
    for p in files:
        want = recorded.get(p.name)
        if not want:
            continue
        have = sha256_file(p)
        if have != want:
            problems.append(f"Checksum mismatch in {dirpath}/{p.name}: manifest={want} actual={have}")

    return problems


def main() -> int:
    ap = argparse.ArgumentParser(description="Compute/verify per-directory SHA256SUMS.txt")
    ap.add_argument("--check", action="store_true", help="Verify manifests; do not modify")
    args = ap.parse_args()

    repo = Path(__file__).resolve().parents[1]
    failed = False

    for top in TOPS:
        root = repo / top
        if not root.exists():
            continue
        for dirpath, dirnames, filenames in os.walk(root):
            d = Path(dirpath)
            # Skip dot-directories
            if d.name.startswith("."):
                continue
            # If there are regular files (non-hidden, excluding manifest), manage/verify manifest
            has_regular = any(
                (d / f).is_file() and (not f.startswith(".")) and f != MANIFEST
                for f in filenames
            )
            if not has_regular:
                # Also remove manifest if present but no files to track
                if not args.check:
                    m = d / MANIFEST
                    if m.exists():
                        m.unlink()
                continue

            if args.check:
                problems = verify_manifest(d)
                if problems:
                    failed = True
                    rel = d.relative_to(repo)
                    print(f"[checksum] Issues in {rel}:")
                    for msg in problems:
                        print(f"  - {msg}")
            else:
                write_manifest(d)

    if args.check and failed:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
