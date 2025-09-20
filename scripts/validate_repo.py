#!/usr/bin/env python3
"""
Repository validator for Accountability Ledger.

Checks:
- Case folder naming: cases/{entity}-{slug}, each part: [a-z0-9-]+
- Timeline filenames: timeline/YYYY-MM-DD-{slug}.md
  - YAML front matter contains: date, actors, claims
  - date ISO 8601, matches filename date prefix
- Checksum manifests (SHA256SUMS.txt):
  - For each directory under tracked roots that has regular files, a manifest exists
  - Every file listed and digests match; no extras/unlisted files

Usage:
  python3 scripts/validate_repo.py
"""
from __future__ import annotations

import hashlib
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Tuple, List
import argparse

TOPS = ("evidence", "cases", "timeline", "analysis", "mas_package")
MANIFEST = "SHA256SUMS.txt"
CASE_DIR_RE = re.compile(r"^[a-z0-9-]+-[a-z0-9-]+$")
TIMELINE_FILE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}-[a-z0-9-]+\.md$")


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def parse_front_matter(text: str) -> Tuple[Dict, str]:
    """
    Minimal YAML front matter parser.
    Supports simple scalars "key: value" and simple lists using hyphen:
      key:
        - item1
        - item2
    Returns (dict, body_without_front_matter)
    """
    if not text.startswith("---"):
        return {}, text
    lines = text.splitlines()
    if len(lines) < 3:
        return {}, text
    # Find closing '---'
    end_idx = None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end_idx = i
            break
    if end_idx is None:
        return {}, text

    fm_lines = lines[1:end_idx]
    body = "\n".join(lines[end_idx + 1:]).lstrip("\n")

    data = {}
    current_key = None
    for raw in fm_lines:
        line = raw.rstrip("\n")
        if not line.strip():
            continue
        if not line.startswith((" ", "\t")) and ":" in line:
            # New key
            k, v = line.split(":", 1)
            k = k.strip()
            v = v.strip()
            if v == "":
                # Expect a list or nested block
                data[k] = []
                current_key = k
            else:
                data[k] = v
                current_key = None
        else:
            # Indented list item
            s = line.strip()
            if s.startswith("- "):
                if current_key is None:
                    continue
                data[current_key].append(s[2:].strip())
    return data, body


def validate_cases(repo: Path) -> List[str]:
    errors: List[str] = []
    root = repo / "cases"
    if not root.exists():
        return errors
    for p in root.iterdir():
        if p.is_dir() and not CASE_DIR_RE.match(p.name):
            errors.append(f"Invalid case folder name: {p.relative_to(repo)} (expected [a-z0-9-]+-[a-z0-9-]+)")
    return errors


def validate_timeline(repo: Path) -> List[str]:
    errors: List[str] = []
    root = repo / "timeline"
    if not root.exists():
        return errors
    for p in root.iterdir():
        if p.is_file():
            if not TIMELINE_FILE_RE.match(p.name):
                errors.append(f"Invalid timeline filename: {p.name} (expected YYYY-MM-DD-{{slug}}.md)")
                continue
            text = p.read_text(encoding="utf-8")
            data, _ = parse_front_matter(text)
            # date
            date = data.get("date", "")
            if not date:
                errors.append(f"Missing 'date' in front matter: {p.name}")
            else:
                fn_date = p.name[:10]
                if not date.startswith(fn_date):
                    errors.append(f"Timeline date mismatch in {p.name}: front matter '{date}' vs filename prefix '{fn_date}'")
                try:
                    # Accept Z suffix
                    if "T" in date:
                        datetime.fromisoformat(date.replace("Z", "+00:00"))
                    else:
                        # Allow YYYY-MM-DD only
                        datetime.fromisoformat(date)
                except Exception:
                    errors.append(f"Invalid ISO 8601 date in {p.name}: '{date}'")
            # actors
            if "actors" not in data:
                errors.append(f"Missing 'actors' in front matter: {p.name}")
            # claims
            if "claims" not in data:
                errors.append(f"Missing 'claims' in front matter: {p.name}")
    return errors


def list_regular_files(dirpath: Path) -> List[str]:
    names: List[str] = []
    for name in os.listdir(dirpath):
        if name == MANIFEST or name.startswith("."):
            continue
        p = dirpath / name
        if p.is_file():
            names.append(name)
    return sorted(names)


def read_manifest(dirpath: Path) -> Dict[str, str]:
    m = dirpath / MANIFEST
    mapping: Dict[str, str] = {}
    if not m.exists():
        return mapping
    for line in m.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            digest, fname = line.split(None, 1)
        except ValueError:
            continue
        fname = fname.strip().lstrip("*").lstrip("./")
        mapping[fname] = digest
    return mapping


def validate_manifests(repo: Path) -> List[str]:
    errors: List[str] = []
    for top in TOPS:
        root = repo / top
        if not root.exists():
            continue
        for dirpath, dirnames, filenames in os.walk(root):
            d = Path(dirpath)
            if d.name.startswith("."):
                continue
            files = list_regular_files(d)
            if not files:
                # Directory has no regular files; having a manifest is optional but if present, ensure it's empty
                continue
            recorded = read_manifest(d)
            mpath = d / MANIFEST
            if not mpath.exists():
                errors.append(f"Missing {MANIFEST} in {d.relative_to(repo)}")
                continue
            # extras and missing
            missing = sorted([n for n in recorded.keys() if n not in files])
            extra = sorted([n for n in files if n not in recorded.keys()])
            if missing:
                errors.append(f"Manifest lists missing files in {d.relative_to(repo)}: {missing}")
            if extra:
                errors.append(f"Files present but not listed in manifest for {d.relative_to(repo)}: {extra}")
            # hash mismatches
            for name in files:
                want = recorded.get(name)
                if not want:
                    continue
                have = sha256_file(d / name)
                if have != want:
                    errors.append(f"Checksum mismatch in {d.relative_to(repo)}/{name}: manifest={want} actual={have}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate repository structure and (optionally) checksum manifests"
    )
    parser.add_argument(
        "--with-checksums",
        action="store_true",
        help="Also validate SHA256SUMS.txt manifests"
    )
    args = parser.parse_args()

    repo = Path(__file__).resolve().parents[1]
    errors: List[str] = []
    errors.extend(validate_cases(repo))
    errors.extend(validate_timeline(repo))
    if args.with_checksums:
        errors.extend(validate_manifests(repo))

    if errors:
        print("Repository validation failed:")
        for e in errors:
            print(f" - {e}")
        return 1
    print("Repository validation passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
