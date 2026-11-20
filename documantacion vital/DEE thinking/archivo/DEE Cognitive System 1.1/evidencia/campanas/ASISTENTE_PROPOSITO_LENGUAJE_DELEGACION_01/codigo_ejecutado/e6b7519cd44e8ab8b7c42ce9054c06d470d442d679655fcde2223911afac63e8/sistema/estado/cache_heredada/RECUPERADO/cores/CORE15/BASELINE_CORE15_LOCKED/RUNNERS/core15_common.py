"""Shared, hash-pinned persistence and provenance helpers for CORE15."""
from __future__ import annotations

import hashlib
import json
import os
import re
import zipfile
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TESTS = ROOT.parent
ARCHIVE = TESTS / "EXPEDIENTE_EXPERIMENTOS_DEE" / "CORE"
MASTER_WORK = TESTS / "DEE_V27_MASTER_REVALIDATION_REBUILD_WORK"
CORE14_WORK = TESTS / "DEE_V27_CORE14_CAUSAL_ECOLOGY_REBUILD_WORK"
OFFICIAL_NAME = "15_DEE_V27_OBSERVER_SHADOW_MULTIPHYSICS_AND_FINAL_ROSETTA_RESULTADOS.zip"
CORE14_NAME = "14_DEE_V27_CAUSAL_ECOLOGY_ENVIRONMENT_MATTER_AND_MULTI_ROSETTA_RESULTADOS.zip"
MASTER_NAME = "DEE_V27_MASTER_REVALIDATION_CORE01_TO_14_ANTI_OVERFIT_RESULTADOS.zip"
EXPECTED = {
    "wheel": "69297e6f06761c8b2f65d24a3fd7a2f16a3f67595a7f9660739ab65f47abc939",
    "package": "7e2991b1fc8a053ee44ead6e177b129855ae9265dea68505a8e545f0c3fdf8b4",
    "kernel": "0b17ba32037935a255b0f2182a52137bceab424f7e09126b761076b63e42c6ff",
}
EXPECTED_CORE14 = "ad158c922da87e9696247f149c0302329981efb16050a1cbe020aa0260acb4c3"
EXPECTED_MASTER = "82e05c5bec3c9fd79c84b25cd36c4dc3741e09489a4b7978e2c0d0fb830edb6e"


def utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def canonical_hash(value: object) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def native(value):
    try:
        import numpy as np
        if isinstance(value, np.generic):
            return value.item()
        if isinstance(value, np.ndarray):
            return value.tolist()
    except ImportError:
        pass
    if isinstance(value, dict):
        return {str(k): native(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [native(v) for v in value]
    return value


def write_json(path: Path, value: object) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("w", encoding="utf-8", newline="\n") as stream:
        json.dump(native(value), stream, indent=2, sort_keys=True, ensure_ascii=False, allow_nan=False)
        stream.write("\n")
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(temporary, path)


def write_text(path: Path, value: str) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("w", encoding="utf-8", newline="\n") as stream:
        stream.write(value)
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(temporary, path)


def append_ndjson(path: Path, row: dict) -> None:
    prior = path.read_text(encoding="utf-8") if path.exists() else ""
    write_text(path, prior + json.dumps(native({"utc": utc(), **row}), separators=(",", ":"), ensure_ascii=False) + "\n")


def read_json(path: Path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def read_zip_json(path: Path, name: str):
    with zipfile.ZipFile(path) as archive:
        return json.loads(archive.read(name).decode("utf-8-sig"))


def verify_zip(path: Path) -> dict:
    with zipfile.ZipFile(path) as archive:
        names = set(archive.namelist())
        first_bad = archive.testzip()
        hash_files = sorted(
            (name for name in names if name.endswith("HASHES.sha256")),
            key=lambda name: (name.count("/"), len(name), name),
        )
        bad = []
        checked = 0
        if hash_files:
            prefix = hash_files[0][:-len("HASHES.sha256")]
            for line in archive.read(hash_files[0]).decode("utf-8-sig").splitlines():
                line = line.strip()
                if not line:
                    continue
                expected, relative = line.split(None, 1)
                member = prefix + relative.strip().lstrip("*")
                checked += 1
                if member not in names or hashlib.sha256(archive.read(member)).hexdigest() != expected.lower():
                    bad.append(relative.strip())
        return {
            "path": str(path),
            "sha256": sha(path),
            "size": path.stat().st_size,
            "zip_crc_pass": first_bad is None,
            "internal_hashes_checked": checked,
            "internal_hash_mismatches": bad,
            "state_present": any(name.endswith("STATE.json") for name in names),
            "manifest_present": any(name.endswith("MANIFEST.json") for name in names),
            "pass": first_bad is None and not bad,
        }


def kernel_paths() -> dict[str, Path]:
    extracted = TESTS / "DEE_CODEX_NATIVE_DISCOVERY_AND_CLOSURE_V1_WORK" / "ANALYSIS" / "binary_api" / "wheel_extracted" / "dee_universe_v27"
    return {
        "wheel": TESTS / "dee_universe_v27-27.0.0-cp313-cp313-win_amd64.whl",
        "package": extracted / "__init__.py",
        "kernel": extracted / "dee_kernel_v27.cp313-win_amd64.pyd",
    }


def kernel_hashes() -> dict[str, str]:
    return {name: sha(path) for name, path in kernel_paths().items()}


def audit_kernel(stage: str) -> dict:
    path = ROOT / "KERNEL_IMMUTABILITY_AUDIT.json"
    audit = read_json(path) if path.exists() else {"expected": EXPECTED, "checks": []}
    observed = kernel_hashes()
    row = {"stage": stage, "utc": utc(), "observed": observed, "pass": observed == EXPECTED}
    audit["checks"].append(row)
    audit["all_pass"] = all(item["pass"] for item in audit["checks"])
    write_json(path, audit)
    if not row["pass"]:
        raise RuntimeError(f"canonical kernel identity mismatch: {observed}")
    return row


def record_question(**row) -> None:
    append_ndjson(ROOT / "QUESTION_TREE.ndjson", row)


def record_dialogue(**row) -> None:
    append_ndjson(ROOT / "KERNEL_DIALOGUE.ndjson", row)


def experiment_key(question: str, mechanism: str, preparation: str, observer: str, intervention: str, region: str) -> str:
    return hashlib.sha256("|".join((question, mechanism, preparation, observer, intervention, region)).encode("utf-8")).hexdigest()


def scan_q_mentions(zip_path: Path, max_member_bytes: int = 2_000_000) -> dict[str, list[dict]]:
    out = {f"Q{i}": [] for i in range(5)}
    pattern = re.compile(r"(?<![A-Za-z0-9_])Q([0-4])(?![A-Za-z0-9_])", re.I)
    allowed = (".json", ".md", ".py", ".ndjson", ".txt", ".csv")
    with zipfile.ZipFile(zip_path) as archive:
        for info in archive.infolist():
            if info.file_size > max_member_bytes or not info.filename.lower().endswith(allowed):
                continue
            try:
                text = archive.read(info).decode("utf-8-sig", errors="replace")
            except Exception:
                continue
            for line_no, line in enumerate(text.splitlines(), 1):
                matches = sorted(set(f"Q{m}" for m in pattern.findall(line)))
                for label in matches:
                    if len(out[label]) < 80:
                        out[label].append({"file": info.filename, "line": line_no, "context": line.strip()[:600]})
    return out


def update_state(**fields) -> None:
    path = ROOT / "STATE.json"
    state = read_json(path) if path.exists() else {"status": "INITIALIZING", "started_utc": utc(), "completed_modules": []}
    state.update(native(fields))
    state["updated_utc"] = utc()
    write_json(path, state)
