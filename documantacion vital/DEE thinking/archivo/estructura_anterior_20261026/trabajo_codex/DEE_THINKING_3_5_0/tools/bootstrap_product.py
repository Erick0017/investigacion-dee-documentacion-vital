"""Idempotent source copy and primary case index; never edits the parents."""
import hashlib
import json
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PRODUCT = ROOT.parents[1]
IDENTITIES = {
    "product_3_0": (PRODUCT / "archivo/DEE_thinking_3_0_0_ENTREGA_FINAL_RESULTADOS.zip", "9b45a8d0b05258dba3989bdf6e63ed3fd7d1c01f199673da06259d0aad946937"),
    "wheel_3_0": (PRODUCT / "3.0/dee_thinking-3.0.0-cp313-cp313-win_amd64.whl", "9aa3a69bf1d542308912dbeee0b7c89199dafe295ce09533a2a394c8bc83c6db"),
    "science": (PRODUCT / "archivo/DEE_thinking_3_0_0_FRONTERAS_COGNITIVAS_MULTIRRAMA_01_RESULTADOS.zip", "f1f8b6b2f68517f003a21c2908adde49bf1194c7f5657b460563b91ad76f28f0"),
}


def digest(p):
    return hashlib.file_digest(p.open("rb"), "sha256").hexdigest()


def main():
    identities = {}
    for label, (p, expected) in IDENTITIES.items():
        actual = digest(p)
        if actual != expected:
            raise ValueError(f"Identity mismatch {label}: {actual}")
        identities[label] = {"path": str(p), "sha256": actual}
    marker = ROOT / "validation/INITIAL_PROVENANCE.json"
    if not marker.exists():
        with zipfile.ZipFile(IDENTITIES["product_3_0"][0]) as z:
            assert z.testzip() is None
            for e in z.infolist():
                if e.filename.startswith("source/") or e.filename in ("README.md", "PRODUCT_CONTRACT.json", "PROJECT_METADATA.json") or e.filename.startswith("docs/"):
                    target = ROOT / e.filename
                    if e.is_dir():
                        target.mkdir(parents=True, exist_ok=True)
                    else:
                        target.parent.mkdir(parents=True, exist_ok=True)
                        target.write_bytes(z.read(e))
        (ROOT / "validation").mkdir(exist_ok=True)
        kernel = ROOT / "source/src/kernel_v27.cpp"
        assert digest(kernel) == "fbd8190381ed76085f404e6578ff15fe185ab66cd48c67300d2abad61ddc7e31"
        marker.write_text(json.dumps({"parents": identities, "source_copied_byte_exact": True, "kernel_sha256": digest(kernel)}, indent=2), encoding="utf-8")
    with zipfile.ZipFile(IDENTITIES["science"][0]) as z:
        assert z.testzip() is None
        case_members = [n for n in z.namelist() if n.endswith("CASE_LEDGER.jsonl")]
        records = []
        for member in case_members:
            if "/attempt_" in member:
                continue
            lines = [json.loads(line) for line in z.read(member).decode("utf-8-sig").splitlines() if line.strip()]
            by_case = {}
            for row in lines:
                by_case.setdefault(row["case"], []).append(row)
            for case, rows in by_case.items():
                records.append({"ledger_member": member, "case": case, "original_events": rows, "final_status": rows[-1]["status"]})
        rejected = [r for r in records if r["final_status"] == "TECHNICAL_ERROR"]
        records = [r for r in records if r["final_status"] != "TECHNICAL_ERROR"]
        if len(records) != 289:
            raise ValueError(f"Expected 289 completed primary records, got {len(records)} from {case_members}")
        (ROOT / "validation/PRIMARY_CASE_INDEX.json").write_text(json.dumps({"science_sha256": identities["science"]["sha256"], "count": len(records), "records": records, "rejected_original_cases_not_counted": rejected}, indent=2), encoding="utf-8")
    print(json.dumps({"workspace": str(ROOT), "parents": identities, "indexed_records": len(records)}))


if __name__ == "__main__":
    main()
