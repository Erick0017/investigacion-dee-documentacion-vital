"""N0 byte-conservation witness for the DCS relocation; never imports DEE.

Reads only. Baseline records relative paths, sizes and SHA-256. Compare accepts
the relocated root and reports every difference, including allowed-to-review
code/config changes; it never silently accepts a changed historical byte.
"""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path, PurePosixPath
import sys
import time


PAIR = "sistema/estado/fuentes_emparejadas/APD03_MAIN_T604825_R01/EXPORTACION_SERVICIO.json"
APD03_CARD = "sistema/estado/vidas/APD03_MAIN/VIDA.json"
SCRIPT_EXTENSIONS = {".py", ".ps1", ".bat", ".cmd", ".json", ".toml", ".ini", ".cfg", ".pth"}


def now():
    return datetime.now(timezone.utc).isoformat()


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def put_json(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        raise FileExistsError("Do not overwrite an existing conservation witness: " + str(path))
    with path.open("x", encoding="utf8", newline="\n") as stream:
        stream.write(json.dumps(data, ensure_ascii=False, indent=2) + "\n")


def digest(path):
    path = Path(path)
    before = path.stat()
    result = hashlib.sha256()
    size = 0
    with path.open("rb") as stream:
        while chunk := stream.read(4 * 1024 * 1024):
            result.update(chunk)
            size += len(chunk)
    after = path.stat()
    if (before.st_size, before.st_mtime_ns) != (after.st_size, after.st_mtime_ns):
        raise RuntimeError("File changed while read: " + str(path))
    return {"bytes": size, "sha256": result.hexdigest()}


def safe_relative(value):
    posix = PurePosixPath(value)
    if posix.is_absolute() or ".." in posix.parts or ":" in value or "\\" in value:
        raise ValueError("Unsafe recorded relative member: " + repr(value))
    return posix


def within(root, value):
    rel = safe_relative(value)
    path = root.joinpath(*rel.parts)
    if not path.resolve().is_relative_to(root):
        raise ValueError("Relative member resolves outside root: " + value)
    return path


def selected_snapshot(root, card):
    value = card["snapshot"]
    return "sistema/" + safe_relative(value).as_posix()


def baseline(root, out):
    started = time.monotonic()
    root = Path(root).resolve(strict=True)
    records = {}

    def add(relative, category, expected=None):
        relative = safe_relative(relative).as_posix()
        if relative not in records:
            records[relative] = {**digest(within(root, relative)), "categories": []}
        if category not in records[relative]["categories"]:
            records[relative]["categories"].append(category)
        actual = records[relative]
        if expected and (actual["sha256"] != expected["sha256"] or actual["bytes"] != expected["bytes"]):
            raise AssertionError("Existing expected member identity mismatch: " + relative)

    active_path = "sistema/estado/ACTIVO.json"
    active = read_json(within(root, active_path))
    active_card_path = "sistema/estado/vidas/" + active["life_id"] + "/VIDA.json"
    active_card = read_json(within(root, active_card_path))
    add(active_path, "PROTECTED_ACTIVE")
    add(active_card_path, "PROTECTED_ACTIVE")
    active_snapshot = selected_snapshot(root, active_card)
    add(active_snapshot, "PROTECTED_ACTIVE")
    if records[active_snapshot]["sha256"] != active["snapshot_sha256"]:
        raise AssertionError("ACTIVO snapshot identity does not match its recorded hash")

    life_count = 0
    for path in sorted((root / "sistema/estado/vidas").rglob("VIDA.json")):
        if path.is_file():
            add(path.relative_to(root).as_posix(), "ALL_ORIGINAL_LIFE_CARDS")
            life_count += 1
    print("Life cards hashed:", life_count, flush=True)

    system = root / "sistema"
    for path in sorted(system.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in SCRIPT_EXTENSIONS:
            continue
        relative_system = path.relative_to(system)
        if relative_system.parts[0] in {"estado", "runtime"} or "__pycache__" in relative_system.parts:
            continue
        add(path.relative_to(root).as_posix(), "EXECUTABLE_CODE_OR_CONFIGURATION")

    continuity_path = "CONTINUIDAD_APD03_AUTONOMIA_DESARROLLO_DEMOSTRACION.json"
    continuity = read_json(within(root, continuity_path))
    add(continuity_path, "CONTINUITY_DESCRIPTOR")
    add(continuity["manual"], "CURRENT_MASTER_WORD")
    if records[continuity["manual"]]["sha256"] != continuity["manual_sha256"]:
        raise AssertionError("Current Word does not match continuity reference")
    add("sistema/runtime/dee_thinking-4.5.0-cp313-cp313-win_amd64.whl", "OFFICIAL_WHEEL")

    card = read_json(within(root, APD03_CARD))
    add(APD03_CARD, "APD03_SELECTED_LIFE")
    apd03_snapshot = selected_snapshot(root, card)
    add(apd03_snapshot, "APD03_SELECTED_LIFE")
    if records[apd03_snapshot]["sha256"] != continuity["snapshot_sha256"]:
        raise AssertionError("APD03 selected snapshot differs from continuity")

    manifest_path = within(root, PAIR)
    manifest = read_json(manifest_path)
    add(PAIR, "APD03_COMPLETE_OPERATIONAL_PAIR")
    if records[PAIR]["sha256"] != continuity["operational_pair_sha256"]:
        raise AssertionError("APD03 paired manifest differs from continuity")
    pair_prefix = manifest_path.parent.relative_to(root)
    members = manifest["members"]
    for member in members:
        relative = (pair_prefix / safe_relative(member["file"])).as_posix()
        add(relative, "APD03_COMPLETE_OPERATIONAL_PAIR", expected=member)
    print("Complete APD03 pair members verified:", len(members), flush=True)

    counts = Counter(category for data in records.values() for category in data["categories"])
    report = {
        "schema": "DEE.reorganization.conservation_baseline.n0.v1",
        "created_utc": now(),
        "original_root": str(root),
        "N0": True,
        "DEE_imported": False,
        "native_ticks": 0,
        "scope": {
            "all_original_VIDA_json": life_count,
            "selected_physical_snapshots": [active_snapshot, apd03_snapshot],
            "all_complete_APD03_pair_members": len(members),
            "executable_code_configuration": "All selected extensions under sistema, excluding estado/runtime/__pycache__; unchanged official WHL separately included",
            "not_full_archive_hash": True,
            "omissions": ["Other native checkpoints", "Deep scientific telemetry and historical ZIPs", "Runtime dependency directories apart from the official WHL", "Non-VIDA history and other lives' service artifacts unless members of the selected APD03 pair"],
            "no_scientific_capacity_revalidation": True,
        },
        "protected_active": {"life": active["life_id"], "tick": active["tick"], "snapshot_sha256": active["snapshot_sha256"]},
        "selected_APD03": {"life": card["life_id"], "tick": card["physical"]["tick"], "snapshot_sha256": card["snapshot_sha256"], "paired_manifest_sha256": records[PAIR]["sha256"]},
        "files": records,
        "summary": {"unique_files": len(records), "unique_bytes_hashed": sum(x["bytes"] for x in records.values()), "category_counts": dict(counts), "elapsed_seconds": time.monotonic() - started},
    }
    put_json(out, report)
    print(json.dumps({"baseline": str(out), "summary": report["summary"], "native_ticks": 0}, ensure_ascii=False), flush=True)


def compare(root, baseline_path, out):
    started = time.monotonic()
    root = Path(root).resolve(strict=True)
    source = read_json(baseline_path)
    differences = []
    matched = 0
    for relative, expected in source["files"].items():
        path = within(root, relative)
        if not path.is_file():
            differences.append({"file": relative, "status": "MISSING", "categories": expected["categories"]})
            continue
        actual = digest(path)
        if actual["sha256"] == expected["sha256"] and actual["bytes"] == expected["bytes"]:
            matched += 1
        else:
            differences.append({"file": relative, "status": "CHANGED", "categories": expected["categories"], "before": {key: expected[key] for key in ("bytes", "sha256")}, "after": actual})
    immutable_changes = [item for item in differences if any(category != "EXECUTABLE_CODE_OR_CONFIGURATION" for category in item["categories"])]
    operational_changes = [item for item in differences if item not in immutable_changes]
    report = {
        "schema": "DEE.reorganization.conservation_comparison.n0.v1",
        "created_utc": now(), "root": str(root),
        "baseline": str(Path(baseline_path).resolve()),
        "baseline_identity": digest(baseline_path),
        "N0": True, "DEE_imported": False, "native_ticks": 0,
        "byte_conservation_complete": not differences,
        "immutable_historical_bytes_conserved": not immutable_changes,
        "matched": matched, "expected_files": len(source["files"]),
        "differences": differences,
        "immutable_changes_count": len(immutable_changes),
        "executable_config_changes_requiring_explicit_relocation_review": operational_changes,
        "scope": source["scope"],
        "elapsed_seconds": time.monotonic() - started,
        "interpretation": "A relocated code/config change is reported, not silently approved. Root must explain and test any necessary path adaptation. This witness proves selected file byte identity, not all-repository integrity nor native functionality.",
    }
    put_json(out, report)
    print(json.dumps({"report": str(out), "matched": matched, "differences": len(differences), "immutable_changes": len(immutable_changes), "native_ticks": 0}, ensure_ascii=False), flush=True)
    return 0 if not differences else 2


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("baseline", "compare"))
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--baseline", type=Path)
    args = parser.parse_args()
    if args.mode == "baseline":
        baseline(args.root, args.out)
        return 0
    if args.baseline is None:
        parser.error("compare requires --baseline")
    return compare(args.root, args.baseline, args.out)


if __name__ == "__main__":
    sys.exit(main())
