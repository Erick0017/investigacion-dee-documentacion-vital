"""Small isolated regression for collection packaging.

This test never opens or starts the production lineage.  It constructs a
synthetic immutable cut, packages it, extracts it, and verifies canonical
restart files, manifests, cache exclusion, integrity, and no-overwrite
publication semantics.
"""

from __future__ import annotations

import hashlib
import json
import shutil
import sys
import tempfile
import zipfile
from pathlib import Path


HABITAT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HABITAT_ROOT))

from app import habitat  # noqa: E402


def put(path: Path, content: bytes | str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(content, bytes):
        path.write_bytes(content)
    else:
        path.write_text(content, encoding="utf-8")


def main(output: Path) -> int:
    checks: dict[str, bool] = {}
    with tempfile.TemporaryDirectory(prefix="mente-basal-package-test-") as temporary:
        root = Path(temporary) / "habitat"
        start = "world/checkpoints/start.deetsnap"
        end = "world/checkpoints/end.deetsnap"
        segment = "history/segments/segment_000_t0_t9.jsonl"
        telemetry = "history/telemetry/telemetry_000_t0_t9.csv"
        controller_cut = "history/collections/cut_UNIT_controller.json"
        status_cut = "history/collections/cut_UNIT_status.json"
        latest_cut = "history/collections/cut_UNIT_latest_checkpoint.txt"
        descriptor_relative = "history/collections/cut_UNIT_t9.json"

        put(root / start, b"synthetic-start")
        put(root / (start + ".json"), "{}\n")
        put(root / end, b"synthetic-end")
        put(root / (end + ".json"), "{}\n")
        put(root / segment, '{"type":"segment_closed","tick":9}\n')
        put(root / telemetry, "utc,tick\nnow,9\n")
        controller = {"last_checkpoint": end, "last_checkpoint_tick": 9,
                      "current_tick": 9, "segment_index": 1,
                      "segment_start_tick": 9}
        put(root / controller_cut, json.dumps(controller))
        put(root / status_cut, json.dumps({"state": "CUT_NOT_RUNNING", "tick": 9}))
        put(root / latest_cut, end + "\n")
        put(root / "world/instance.json", json.dumps({"x0": start}))
        put(root / "app/synthetic.py", "VALUE = 1\n")
        put(root / "app/__pycache__/leak.pyc", b"cache")
        put(root / "tools/synthetic.ps1", "# synthetic\n")
        put(root / "config/habitat.json", "{}\n")
        put(root / "docs/README.md", "synthetic\n")
        put(root / "analysis/result.json", "{}\n")
        put(root / "validation/result.json", "{}\n")
        put(root / "docs/old.zip", b"must not be nested")
        wheel_name = "dee_thinking-2.2.0-cp313-cp313-win_amd64.whl"
        wheel_source = HABITAT_ROOT / "baseline" / wheel_name
        wheel_target = root / "baseline" / wheel_name
        wheel_target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(wheel_source, wheel_target)
        put(root / "baseline/python_site/leak.txt", "must not be packaged\n")

        immutable = [end, end + ".json", segment, telemetry,
                     controller_cut, status_cut, latest_cut]
        descriptor = {
            "schema": "mente-basal.collection.v1", "request_id": "UNIT",
            "world_id": "SYNTHETIC", "session_id": "SESSION-TEST",
            "start_tick": 0, "end_tick": 9,
            "start_checkpoint": start, "end_checkpoint": end,
            "history_segment": segment, "telemetry_segment": telemetry,
            "controller_snapshot": controller_cut,
            "status_snapshot": status_cut,
            "latest_pointer_snapshot": latest_cut,
            "immutable_files": immutable,
        }
        descriptor_path = root / descriptor_relative
        put(descriptor_path, json.dumps(descriptor))
        package_path = Path(temporary) / "cut.zip"
        result = habitat.package_collection(root, descriptor_path, package_path,
                                            first_session=True)
        prefix = "MENTE_BASAL_HABITAT_PERSISTENTE_SESION_001"
        with zipfile.ZipFile(package_path) as archive:
            checks["testzip"] = archive.testzip() is None
            names = set(archive.namelist())
            checks["canonical_controller"] = f"{prefix}/world/controller.json" in names
            checks["canonical_status"] = f"{prefix}/world/status.json" in names
            checks["canonical_latest"] = f"{prefix}/world/latest_checkpoint.txt" in names
            checks["start_and_end"] = all(
                f"{prefix}/{name}" in names for name in (start, start + ".json",
                                                          end, end + ".json"))
            checks["no_runtime_or_cache"] = not any(
                "python_site/" in name or "__pycache__/" in name or
                name.lower().endswith("old.zip") for name in names)
            manifest = json.loads(archive.read(f"{prefix}/MANIFEST.json"))
            checks["manifest_hashes"] = all(
                hashlib.sha256(archive.read(f"{prefix}/{entry['path']}")).hexdigest() ==
                entry["sha256"] for entry in manifest["files"])
        extract = Path(temporary) / "extract"
        with zipfile.ZipFile(package_path) as archive:
            archive.extractall(extract)
        extracted = extract / prefix
        checks["clean_extract_canonical_state"] = (
            json.loads((extracted / "world/controller.json").read_text(encoding="utf-8")) ==
            controller and
            (extracted / "world/latest_checkpoint.txt").read_text(encoding="utf-8").strip() ==
            end)
        refused = False
        try:
            habitat.package_collection(root, descriptor_path, package_path,
                                       first_session=True)
        except RuntimeError as error:
            refused = "overwrite" in str(error)
        checks["refuses_overwrite"] = refused
        checks["reported_identity"] = (
            result["sha256"] == hashlib.sha256(package_path.read_bytes()).hexdigest())

    report = {
        "schema": "mente-basal.package-regression.v1",
        "checks": checks,
        "all_passed": all(checks.values()),
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0 if report["all_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main(Path(sys.argv[1])))
