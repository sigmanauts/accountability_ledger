#!/usr/bin/env python3
"""
Scaffold a new case directory from the template.

Usage:
  python3 scripts/new_case.py --entity <entity-id> --slug <short-slug>
  or with env vars:
  ENTITY_ID=<entity-id> SLUG=<short-slug> python3 scripts/new_case.py

Creates:
  cases/<entity-id>-<short-slug>/
    README.md (from template with placeholders filled)
    evidence/
    notes/
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path
import os
import sys


def render_template(entity: str, slug: str, ts: str) -> str:
    tpl_path = Path("templates/case/README.md")
    if tpl_path.exists():
        tpl = tpl_path.read_text(encoding="utf-8")
        return (
            tpl.replace("<entity-id>", entity)
               .replace("<short-slug>", slug)
               .replace("<timestamp>", ts)
        )
    # Fallback minimal content
    return f"""# Case: {entity} - {slug}

- Entity ID: {entity}
- Slug: {slug}
- Created (UTC, ISO 8601): {ts}

## Summary
Short description of the case.

## Actors

## Timeline

## Sources
"""


def main() -> int:
    parser = argparse.ArgumentParser(description="Create a new case skeleton")
    parser.add_argument("--entity", required=False, help="Entity ID (lowercase, hyphenated)")
    parser.add_argument("--slug", required=False, help="Case slug (lowercase, hyphenated)")
    args = parser.parse_args()

    entity = args.entity or os.getenv("ENTITY_ID")
    slug = args.slug or os.getenv("SLUG")
    if not entity or not slug:
        print("Usage: new_case.py --entity <entity-id> --slug <short-slug> (or set ENTITY_ID and SLUG env vars)", file=sys.stderr)
        return 2

    case_dir = Path("cases") / f"{entity}-{slug}"
    case_dir.mkdir(parents=True, exist_ok=True)
    (case_dir / "evidence").mkdir(exist_ok=True)
    (case_dir / "notes").mkdir(exist_ok=True)

    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    readme = render_template(entity, slug, ts)
    (case_dir / "README.md").write_text(readme, encoding="utf-8")

    print(f"Created case at {case_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
