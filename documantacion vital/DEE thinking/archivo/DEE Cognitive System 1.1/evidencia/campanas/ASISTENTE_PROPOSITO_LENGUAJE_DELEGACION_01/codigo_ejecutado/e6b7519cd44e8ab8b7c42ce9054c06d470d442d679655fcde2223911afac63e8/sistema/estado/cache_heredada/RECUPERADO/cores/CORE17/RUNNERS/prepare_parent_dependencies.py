#!/usr/bin/env python3
"""Materialize hash-pinned CORE15/16 runner dependencies from canonical parent ZIPs.

The compact CORE17 package does not duplicate parent packages.  Run this once
after extracting CORE17, or pass --core-dir explicitly, before executing the
scientific runners that import parent apparatus modules.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import zipfile


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
REFERENCES = ROOT / "PARENT_CORE_REFERENCES.json"


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def locate_core_dir(explicit: str | None, parent_names: set[str]) -> Path:
    if explicit:
        candidates = [Path(explicit).resolve()]
    else:
        seeds = [ROOT, ROOT.parent, Path.cwd().resolve()]
        candidates = []
        seen: set[Path] = set()
        for seed in seeds:
            for candidate in (seed, *seed.parents):
                if candidate not in seen:
                    seen.add(candidate)
                    candidates.append(candidate)
    for candidate in candidates:
        if all((candidate / name).is_file() for name in parent_names):
            return candidate
    raise FileNotFoundError(
        "Canonical CORE01-16 directory not found. Pass --core-dir pointing to "
        "the directory that contains all official parent ZIPs."
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--core-dir", help="Directory containing official CORE01-16 ZIPs")
    parser.add_argument("--verify-only", action="store_true")
    args = parser.parse_args()

    refs = json.loads(REFERENCES.read_text(encoding="utf-8"))
    parents = {row["core"]: row for row in refs["parent_cores"]}
    names = {row["filename"] for row in parents.values()}
    core_dir = locate_core_dir(args.core_dir, names)

    verified_parents: dict[int, Path] = {}
    for core, row in parents.items():
        path = core_dir / row["filename"]
        observed = sha256_path(path)
        if observed != row["sha256"]:
            raise RuntimeError(f"CORE{core:02d} SHA mismatch: {observed}")
        verified_parents[core] = path

    materialized = []
    for item in refs["dependency_materialization"]:
        parent = verified_parents[item["core"]]
        with zipfile.ZipFile(parent, "r") as archive:
            data = archive.read(item["member"])
        observed = sha256_bytes(data)
        if observed != item["sha256"]:
            raise RuntimeError(f"Parent member SHA mismatch: {item['member']}")
        for target_name in item["targets"]:
            target = ROOT / target_name
            if target.exists():
                current = sha256_path(target)
                if current != observed:
                    raise RuntimeError(f"Existing dependency differs: {target}")
                action = "already_present"
            elif args.verify_only:
                action = "verified_available"
            else:
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(data)
                action = "materialized"
            materialized.append(
                {"target": target_name, "sha256": observed, "action": action}
            )

    print(
        json.dumps(
            {
                "canonical_core_dir": str(core_dir),
                "parent_zips_verified": len(verified_parents),
                "dependencies": materialized,
                "all_hashes_pass": True,
            },
            indent=2,
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
