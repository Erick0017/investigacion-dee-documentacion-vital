"""Terminal focal-control SQLite inspection, mode=ro; no DEE imports or requests."""
import argparse
import hashlib
import json
from pathlib import Path
import sqlite3

ROOT = Path(__file__).resolve().parents[1]
PREFIX = "ECI02_PI03_REPRO_PI04_PI05_PI07_PI10_RBX01_C02_"


def digest(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def inspect(role):
    if role not in ("MEMPAIR", "MEMCTRL"):
        raise ValueError("Only the two explicit closed focal controls")
    result_path = ROOT / f"evidencia/CONTROL_{role}_R01/RESULTADO.json"
    result = json.loads(result_path.read_bytes())
    if result.get("owner_closed") is not True or result.get("life_id") != PREFIX + role:
        raise ValueError("Terminal exact-life result with closed owner required")
    destination = ROOT / "native" / role
    db = destination / "sistema/estado/servicios_persistentes" / (PREFIX + role) / "cola.sqlite3"
    wal = Path(str(db) + "-wal")
    if wal.exists() and wal.stat().st_size:
        raise ValueError("Nonempty WAL: closed standalone queue not established")
    before = digest(db)
    connection = sqlite3.connect(db.resolve().as_uri() + "?mode=ro", uri=True)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA query_only=ON")
    connection.execute("BEGIN")
    tables = [r[0] for r in connection.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")]
    schema = {name: [dict(r) for r in connection.execute('PRAGMA table_info("' + name.replace('"', '""') + '")')]
              for name in tables if not name.startswith("sqlite_")}
    relevant = {}
    for name, fields in schema.items():
        columns = {r["name"] for r in fields}
        if {"seq", "id", "status"} <= columns:
            safe = '"' + name.replace('"', '""') + '"'
            selected = [key for key in ("seq", "id", "status", "is_control", "arrived_utc", "started_utc", "finished_utc") if key in columns]
            focal = [dict(r) for r in connection.execute("SELECT " + ",".join(selected) + " FROM " + safe + " WHERE id LIKE ? ORDER BY seq", ("C02_FOCAL_FOCAL_" + role + "_%",))]
            counts = [dict(r) for r in connection.execute("SELECT status,count(*) AS count FROM " + safe + " GROUP BY status ORDER BY status")]
            relevant[name] = {"focal_requests": focal, "all_historical_status_counts": counts,
                              "count_scope": "Historical inherited rows are not new C02 events; only exact focal-ID rows above are campaign requests."}
    connection.rollback(); connection.close()
    after = digest(db)
    if before != after:
        raise RuntimeError("Closed queue changed during inspection")
    report = {"schema": "DEE.RBX01.C02.closed_focal_queue.inspection.R01", "life_id": PREFIX + role,
              "mode": "SQLite mode=ro/query_only transaction, no Native code, no requests", "queue_path": str(db.relative_to(ROOT)),
              "queue_bytes": db.stat().st_size, "queue_sha256_before": before, "queue_sha256_after": after,
              "nonempty_WAL_present": False, "SQLite_schema": schema, "requests": relevant,
              "result_path": str(result_path.relative_to(ROOT)), "result_sha256": digest(result_path)}
    target = ROOT / f"analisis/CONTROL_{role}_RECALCULO_R01/COLA_TERMINAL.json"
    with target.open("x", encoding="utf-8") as stream:
        stream.write(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"output": str(target.relative_to(ROOT)), "queue_stable": before == after,
                      "tables": list(schema), "focal_counts": {key: len(v["focal_requests"]) for key, v in relevant.items()}}, ensure_ascii=False))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("role", choices=("MEMPAIR", "MEMCTRL"))
    inspect(parser.parse_args().role)
