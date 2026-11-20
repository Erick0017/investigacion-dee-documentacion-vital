"""Materialize archived exact source revisions from content-deduplicated blobs."""
from pathlib import Path
import argparse
import hashlib
import json


def sha(data):
    return hashlib.sha256(data).hexdigest()


def materialize(index_path, destination):
    index_path = Path(index_path).resolve()
    destination = Path(destination).resolve()
    index = json.loads(index_path.read_text(encoding="utf8"))
    count = 0
    for entry in index["members"]:
        relative = Path(entry["archive_relative_path"])
        if relative.is_absolute() or ".." in relative.parts:
            raise ValueError("Unsafe archived relative path")
        target = destination.joinpath(relative).resolve()
        if not target.is_relative_to(destination):
            raise ValueError("Output path outside the selected destination")
        blob = index_path.parent / "blobs" / entry["sha256"]
        data = blob.read_bytes()
        assert len(data) == entry["bytes"] and sha(data) == entry["sha256"]
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists() and target.read_bytes() != data:
            raise FileExistsError("Different existing code will not be overwritten: " + str(target))
        if not target.exists():
            target.write_bytes(data)
        count += 1
    return {"members_materialized_and_verified": count, "destination": str(destination),
            "new_native_ticks": 0, "executes_archived_code": False}


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--index", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    a = p.parse_args()
    print(json.dumps(materialize(a.index, a.out), ensure_ascii=False))
