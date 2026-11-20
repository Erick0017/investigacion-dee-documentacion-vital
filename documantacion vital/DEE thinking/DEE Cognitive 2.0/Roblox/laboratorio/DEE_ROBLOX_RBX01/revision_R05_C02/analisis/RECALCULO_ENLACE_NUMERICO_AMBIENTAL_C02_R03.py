"""Portable R03 recalculation of frozen environmental replays. No engine calls.

All source identities resolve through CONTROL/MANIFIESTO_SHA256.json inside the
explicit package. Historical absolute paths are opaque IDs, never opened.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
import ntpath
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[1]
MISSING = {"__audit_absent_key__": True}
MAX_INPUT_BYTES = 64_000_000


def reject_links(path):
    """Reject symlinks/junctions before resolution; never follow package escapes."""
    for item in (path, *path.parents):
        if item.is_symlink() or (item.exists() and getattr(item.lstat(), "st_file_attributes", 0) & 1024):
            raise ValueError("Linked/reparse path refused")


class PackageSources:
    def __init__(self, package_root):
        raw_root = Path(package_root).absolute(); reject_links(raw_root)
        self.root = raw_root.resolve(strict=True)
        if not self.root.is_dir():
            raise ValueError("Existing extracted package directory required")
        manifest_path = self.archive_path("CONTROL/MANIFIESTO_SHA256.json")
        raw = manifest_path.read_bytes()
        if len(raw) > MAX_INPUT_BYTES:
            raise ValueError("Manifest bound exceeded")
        manifest = json.loads(raw.decode("utf-8-sig"))
        if not isinstance(manifest, dict) or not isinstance(manifest.get("members"), list):
            raise ValueError("Manifest members[{source,archive,sha256}] required")
        self.manifest_sha256 = hashlib.sha256(raw).hexdigest()
        self.by_source = {}; self.by_archive = {}; self.reads = []
        for member in manifest["members"]:
            if not isinstance(member, dict):
                raise ValueError("Manifest member must be an object")
            source, archive, sha = member.get("source"), member.get("archive"), member.get("sha256")
            if not isinstance(source, str) or not source or not isinstance(sha, str) or not re.fullmatch(r"[0-9a-fA-F]{64}", sha):
                raise ValueError("Manifest source identity and SHA-256 required")
            self.archive_path(archive)
            item = {"source": source, "archive": archive, "sha256": sha.lower()}
            key = self.source_key(source)
            for mapping, identity in ((self.by_source, key), (self.by_archive, archive)):
                if identity in mapping and mapping[identity] != item:
                    raise ValueError("Ambiguous manifest source/archive mapping")
                mapping[identity] = item

    @staticmethod
    def source_key(value):
        # Windows historical identifiers normalize as strings only. Never Path(D:...).
        return ntpath.normcase(ntpath.normpath(value))

    def archive_path(self, archive):
        if not isinstance(archive, str) or not archive or "\\" in archive or ":" in archive:
            raise ValueError("Portable relative archive member required")
        path = PurePosixPath(archive)
        if path.is_absolute() or any(part in ("", ".", "..") for part in path.parts):
            raise ValueError("Unsafe archive member")
        candidate = self.root.joinpath(*path.parts)
        reject_links(candidate)
        resolved = candidate.resolve(strict=False)
        if not resolved.is_relative_to(self.root):
            raise ValueError("Archive member escapes package")
        return resolved

    def read_archive(self, archive, reference_sha256=None):
        member = self.by_archive.get(archive)
        if member is None:
            raise ValueError("Archive source is not covered by manifest: " + archive)
        path = self.archive_path(archive)
        before = path.read_bytes()
        if len(before) > MAX_INPUT_BYTES or path.read_bytes() != before:
            raise ValueError("Source bound exceeded or source changed during passive read")
        actual = hashlib.sha256(before).hexdigest()
        if actual != member["sha256"]:
            raise ValueError("Manifest SHA mismatch: " + archive)
        if reference_sha256 is not None and actual != str(reference_sha256).lower():
            raise ValueError("Historical provenance SHA mismatch: " + archive)
        self.reads.append({"archive": archive, "bytes": len(before), "sha256": actual,
                           "resolved_from_manifest": True, "original_source_opened": False})
        return before, path

    def verify_source(self, source_identifier, reference_sha256):
        if not isinstance(source_identifier, str):
            raise ValueError("Historical source identifier required")
        member = self.by_source.get(self.source_key(source_identifier))
        if member is None:
            raise ValueError("Historical source has no package mapping; no original-path fallback")
        raw, _ = self.read_archive(member["archive"], reference_sha256)
        return {"path": member["archive"], "original_source_identifier": source_identifier,
                "bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest(),
                "reference_sha256": reference_sha256, "matches": True,
                "resolution": "manifest source->archive; original absolute path never opened"}


def canon(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def differences(a, b, path=""):
    if type(a) is not type(b):
        return [{"path": path or "/", "left": a, "right": b}]
    if isinstance(a, dict):
        rows = []
        for key in sorted(set(a) | set(b)):
            at = path + "/" + key.replace("~", "~0").replace("/", "~1")
            if key not in a or key not in b:
                rows.append({"path": at, "left": a.get(key, MISSING), "right": b.get(key, MISSING)})
            else:
                rows.extend(differences(a[key], b[key], at))
        return rows
    if isinstance(a, list):
        rows = []
        for i in range(max(len(a), len(b))):
            at = path + "/" + str(i)
            if i >= len(a) or i >= len(b):
                rows.append({"path": at, "left": a[i] if i < len(a) else MISSING,
                             "right": b[i] if i < len(b) else MISSING})
            else:
                rows.extend(differences(a[i], b[i], at))
        return rows
    return [] if a == b else [{"path": path or "/", "left": a, "right": b}]


def load_arm(name, package):
    archive = f"evidencia/CONTROL_ENLACE_NUMERICO_{name}_R02/RESULTADO_AMBIENTAL_REPLAY_C02.json"
    before, path = package.read_archive(archive)
    data = json.loads(before)
    if path.read_bytes() != before:
        raise RuntimeError("Source changed during passive read")
    if data["NativeExecuted"] is not False or data["hostSelectedAllActions"] is not True:
        raise RuntimeError("Unexpected replay provenance")
    events = data["events"]
    start = [i for i, row in enumerate(events) if row["kind"] == "ENV_REPLAY_BEGIN"]
    if len(start) != 1:
        raise RuntimeError("One explicit replay segment required")
    new_events = events[start[0]:]
    action_rows = [r for r in new_events if r["kind"] == "ACTION_EXECUTED"]
    actions = [{k: r["data"]["action"].get(k) for k in
                ("name", "sourceActionId", "sourceNativeTick", "sourceNativeTicks", "NativeExecuted")}
               for r in action_rows]
    final = data["final"]; initial = data["initial"]
    deltas = {key: final[key] - initial[key] for key in
              ("resourceCount", "resourceUnits", "permissionStock", "queries", "tollSpent",
               "codeRejected", "collisions", "moves", "delivered", "worldTime", "nativeTick")}
    locks = [r["data"] for r in new_events if r["kind"] == "EVALUATOR_LOCK_CHECK"]
    controls = data["controls"]
    facts = {
        "condition": data["condition"], "schema": data["schema"],
        "source_file": archive, "bytes": len(before),
        "sha256": hashlib.sha256(before).hexdigest(), "NativeExecuted": data["NativeExecuted"],
        "NativeContinuationCheckpoint": data["NativeContinuationCheckpoint"],
        "hostSelectedAllActions": data["hostSelectedAllActions"],
        "sourceNativeLifeId": data["sourceNativeLifeId"], "sourceNativeTick": data["sourceNativeTick"],
        "archivedNativeCompletedCycles": data["archivedNativeCompletedCycles"],
        "environmentReplayCompletedCycles": data["environmentReplayCompletedCycles"],
        "new_event_count": len(new_events), "new_event_kinds": dict(Counter(r["kind"] for r in new_events)),
        "replayed_actions": actions, "deltas": deltas, "lock_checks": locks,
        "functionResults": data["functionResults"],
        "control_cycles": [{"cycle": r["cycle"], "queryResult": r["queryResult"],
                            "routeResult": r["routeResult"], "environmentalConsequence": r["environmentalConsequence"],
                            "NativeFeedbackSent": r["NativeFeedbackSent"]} for r in controls],
        "all_control_feedback_not_sent_to_Native": all(r["NativeFeedbackSent"] is False for r in controls),
        "initial_to_final_state_differences": differences(initial, final),
        "provenance": data["sourceProvenance"],
    }
    return data, facts


def recalculate(package_root, output):
    package = PackageSources(package_root)
    output = Path(output).absolute(); reject_links(output)
    output = output.resolve(strict=False)
    if output.exists():
        raise RuntimeError("New absent output directory required; no report overwrite")
    if not output.parent.is_dir():
        raise ValueError("Existing output parent required")
    intact, intact_facts = load_arm("INTACT", package)
    cut, cut_facts = load_arm("CUT_B", package)
    provenance = intact["sourceProvenance"]
    checks = []
    for file_key, sha_key in (("primary_path", "primary_sha256"), ("world_path", "world_sha256"),
                              ("world_final_path", "world_final_sha256")):
        checks.append(package.verify_source(provenance[file_key], provenance[sha_key]))
        # Validate both arms' locators, even when they differ. Preserve the
        # original same_source_provenance comparison as a scientific observable.
        if cut["sourceProvenance"][file_key] != provenance[file_key] or cut["sourceProvenance"][sha_key] != provenance[sha_key]:
            checks.append(package.verify_source(cut["sourceProvenance"][file_key], cut["sourceProvenance"][sha_key]))
    equal_initial = intact["initial"] == cut["initial"]
    equal_actions = intact_facts["replayed_actions"] == cut_facts["replayed_actions"]
    equal_costs = {key: intact_facts["deltas"][key] == cut_facts["deltas"][key]
                   for key in ("permissionStock", "queries", "tollSpent", "collisions", "moves", "worldTime", "nativeTick")}
    facts = {
        "schema": "DEE.RBX01.C02.environmental_numeric_link.passive_recalculation.R03",
        "inspection_utc": datetime.now(timezone.utc).isoformat(),
        "mode": "Recalculation of frozen completed Studio environmental replays; no Native import, no simulation rerun",
        "arms": {"INTACT": intact_facts, "CUT_B": cut_facts},
        "paired_comparability": {"initial_state_exact_equal": equal_initial,
                                 "same_recorded_action_sequence": equal_actions,
                                 "equal_actual_cost_time_dose_deltas": equal_costs,
                                 "same_source_provenance": intact["sourceProvenance"] == cut["sourceProvenance"]},
        "cross_arm_initial_state_differences": differences(intact["initial"], cut["initial"]),
        "cross_arm_final_state_differences": differences(intact["final"], cut["final"]),
        "cross_arm_final_physical_differences": differences(intact["physical"], cut["physical"]),
        "source_hash_checks": checks,
        "portable_resolution": {"manifest": "CONTROL/MANIFIESTO_SHA256.json", "manifest_sha256": package.manifest_sha256,
                                "all_reads": package.reads, "original_absolute_sources_opened": False},
        "interpretation_supported": "Under this prepared Body/lock and the same recorded action sequence, transporting the recorded actual Native integer5 permits the resource contact/inventory effect. Cutting B preserves movement/query costs but prevents code acceptance and resource pickup. This isolates a necessary environmental numeric-result link for this recorded case.",
        "interpretation_not_supported": [
            "New Native learning, new Native decisions or Native response to the cut: NativeExecuted is false and no Native feedback was sent.",
            "A general policy comparison or independent replication: both arms replay the same archived trajectory.",
            "A coherent continuation checkpoint: archived Native remains at T950523/completed2 while environment reaches completed4.",
            "An energetic/metabolic resource or subjective pain claim.",
        ],
        "downstream_differences_expected": "After B is cut, lastFailure and later observations/consequences legitimately diverge. Equal exogenous conditions do not require forcing identical endogenous observations.",
        "subagent_native_ticks": 0,
    }
    output.mkdir()
    (output / "RECALCULO.json").write_text(json.dumps(facts, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    with (output / "TODAS_DIFERENCIAS_ESTADO.csv").open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=("comparison", "path", "left", "right")); writer.writeheader()
        groups = {"INTACT_initial_to_final": intact_facts["initial_to_final_state_differences"],
                  "CUT_B_initial_to_final": cut_facts["initial_to_final_state_differences"],
                  "cross_arm_initial": facts["cross_arm_initial_state_differences"],
                  "cross_arm_final": facts["cross_arm_final_state_differences"],
                  "cross_arm_final_physical": facts["cross_arm_final_physical_differences"]}
        for group, rows in groups.items():
            for row in rows:
                writer.writerow({"comparison": group, "path": row["path"],
                                 "left": canon(row["left"]), "right": canon(row["right"])})
    summary = {"output": str(output), "initial_equal": equal_initial,
                      "actions_equal": equal_actions, "equal_cost_deltas": equal_costs,
                      "INTACT": intact_facts["deltas"], "CUT_B": cut_facts["deltas"],
                      "final_S_differences": len(facts["cross_arm_final_state_differences"]),
                      "final_physical_differences": len(facts["cross_arm_final_physical_differences"]),
                      "provenance_hashes_match": all(r["matches"] for r in checks),
                      "original_absolute_sources_opened": False}
    print(json.dumps(summary, ensure_ascii=False))
    return facts


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--package-root", type=Path, default=ROOT, help="Extracted package containing CONTROL/MANIFIESTO_SHA256.json")
    parser.add_argument("--output", type=Path, required=True, help="New absent output directory; no overwrite")
    args = parser.parse_args()
    recalculate(args.package_root, args.output)


if __name__ == "__main__":
    main()
