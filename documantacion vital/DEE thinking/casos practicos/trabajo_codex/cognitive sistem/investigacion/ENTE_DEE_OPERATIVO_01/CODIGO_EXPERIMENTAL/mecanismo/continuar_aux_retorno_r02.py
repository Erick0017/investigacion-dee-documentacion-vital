"""One common new opportunity on an existing auxiliary, never a reset/fork."""
from pathlib import Path
from datetime import datetime, timezone
import argparse
import gzip
import hashlib
import importlib.util
import json
import time

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("eo01_frozen_aux_r02", HERE / "retorno_posterior_aux_r02.py")
FROZEN = importlib.util.module_from_spec(SPEC); SPEC.loader.exec_module(FROZEN)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--system", required=True, type=Path)
    p.add_argument("--life", required=True)
    p.add_argument("--public", default="7,16")
    p.add_argument("--reference", type=int, default=9)
    p.add_argument("--out", required=True, type=Path)
    a = p.parse_args()
    if not a.life.startswith("EO01_AUX_") or a.out.exists():
        raise ValueError("Existing auxiliary life/new evidence filename required")
    if datetime.now(timezone.utc) >= datetime.fromisoformat(FROZEN.DEADLINE):
        raise TimeoutError("Original fixed budget exhausted")
    public = tuple(map(int, a.public.split(",")))
    FROZEN.configure(a.system)
    from app.lives import Store
    store = Store(a.system)
    prior = store.record(a.life)
    started = datetime.now(timezone.utc).isoformat(); clock = time.monotonic()
    result = store.mutate(a.life, "EO01_AUX_R02_COMMON_NEW_USE", lambda adapter: FROZEN.episode(adapter, system=a.system, mode="normal", public=public, environment_reference=a.reference),
                          details={"raw_public": public, "same_future_protocol_for_all_histories": True,
                                   "frozen_aux_source_sha256": hashlib.sha256((HERE / "retorno_posterior_aux_r02.py").read_bytes()).hexdigest()})
    d = {"case": a.out.stem.removesuffix(".json"), "started_utc": started, "elapsed_seconds": time.monotonic()-clock,
         "source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
         "frozen_episode_source_sha256": hashlib.sha256((HERE / "retorno_posterior_aux_r02.py").read_bytes()).hexdigest(),
         "previous_checkpoint_record": prior, "result": result,
         "interpretation": "First new common opportunity after different result histories; plasticity is still active and later fields may change during this very use."}
    a.out.parent.mkdir(parents=True, exist_ok=True)
    with gzip.open(a.out, "wt", encoding="utf8", compresslevel=6) as stream:
        json.dump(d, stream, ensure_ascii=False, allow_nan=False)
    row = result["result"]
    print(json.dumps({"life": a.life, "tick": result["INSTRUMENTO"]["tick"], "environment": row["environment"],
                      "before_own": [q["s_reg"] for q in row["before"]["own"]],
                      "after_own": [q["s_reg"] for q in row["after"]["own"]],
                      "receipts": {q["receipt"]["status"]: sum(x["receipt"]["status"] == q["receipt"]["status"] for x in row["requests"]) for q in row["requests"]}}, ensure_ascii=False))


if __name__ == "__main__":
    main()
