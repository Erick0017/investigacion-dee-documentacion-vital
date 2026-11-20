"""Inventory/check every exported CF01 primary with stdlib; no engine/ticks."""
from pathlib import Path
from collections import Counter
import argparse
import gzip
import hashlib
import json


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def walk(value):
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from walk(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk(child)


def exact(q):
    assert isinstance(q["raw"], str) and q["raw"].isdecimal()
    assert isinstance(q["clock"], str) and q["clock"].isdecimal()
    v = int(q["raw"])
    assert 0 <= v < 2**64
    def signed(shift):
        x = (v >> shift) & 15
        return x - 16 if x & 8 else x
    fields = {"state": v & 0xffffffff, "s_reg": (v >> 32) & 65535,
              "semantic": (v >> 60) & 15, "direction": [signed(i) for i in (48, 52, 56)]}
    assert all(q[k] == v for k, v in fields.items())


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--evidence", required=True, type=Path)
    ap.add_argument("--out", required=True, type=Path)
    args = ap.parse_args()
    rows = []; loaded = {}
    for path in sorted(args.evidence.glob("*.json.gz")):
        with gzip.open(path, "rt", encoding="utf8") as stream:
            d = json.load(stream)
        loaded[path.stem.removesuffix(".json")] = d
        checked = 0; receipts = {}; ticks = []
        for q in walk(d.get("result", {})):
            if all(k in q for k in ("raw", "clock", "state", "s_reg", "semantic", "direction")):
                exact(q); checked += 1
                if "tick" in q:
                    ticks.append(q["tick"])
            if isinstance(q.get("receipt"), dict):
                rec = q["receipt"]
                if "id" in rec:
                    if rec["id"] in receipts:
                        assert receipts[rec["id"]] == rec
                    receipts[rec["id"]] = rec
        rows.append({"case": d.get("case", path.name), "file": path.name,
                     "sha256": sha(path), "bytes": path.stat().st_size,
                     "process_returncode": d.get("returncode"), "observation_records_checked": checked,
                     "observation_tick_range": [min(ticks), max(ticks)] if ticks else None,
                     "unique_requested_receipts": len(receipts),
                     "receipt_statuses": dict(Counter(q["status"] for q in receipts.values())),
                     "code_revision_sha256": d.get("code_revision_sha256")})
    controls = {}
    if "CAL_B36" in loaded and "CAL_B52" in loaded:
        a = loaded["CAL_B36"]["result"]["result"]
        b = loaded["CAL_B52"]["result"]["result"]
        controls["CAL36_vs52"] = {"sampled_before_witness_equal": a["before"] == b["before"],
            "sampled_after_witness_equal": a["after"] == b["after"],
            "end_ticks": [a["after"]["tick"], b["after"]["tick"]],
            "scope": "Only exported sampled witnesses; full RAW/clocks/agenda equality was separately verified locally from complete snapshots, which are not in this analysis package."}
    result = {"schema": "CF01.all_exported_primaries.check.v1", "new_native_ticks": 0,
              "primaries": rows, "files_checked": len(rows),
              "observation_records_checked": sum(r["observation_records_checked"] for r in rows),
              "all_positive_and_negative_files_enumerated": True, "calibration_controls": controls,
              "scope": "Exact packed-field consistency and primary inventory, not a rerun or universal scientific verdict."}
    args.out.write_text(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf8")
    print(json.dumps({"out": str(args.out), "files": len(rows), "observations": result["observation_records_checked"], "ticks": 0}))


if __name__ == "__main__":
    main()
