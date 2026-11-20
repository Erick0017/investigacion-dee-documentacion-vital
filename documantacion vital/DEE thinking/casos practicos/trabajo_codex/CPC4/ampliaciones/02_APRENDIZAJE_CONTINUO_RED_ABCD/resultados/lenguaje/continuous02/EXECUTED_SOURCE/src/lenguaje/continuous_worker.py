"""Continue an actual1431 genealogy or execute one frozen fresh realization."""
import argparse
import json
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[2]; sys.path.insert(0, str(ROOT / "src"))


def main():
    p = argparse.ArgumentParser(); p.add_argument("--case", required=True); p.add_argument("--output", required=True)
    p.add_argument("--parent"); a = p.parse_args(); case = json.loads(Path(a.case).read_text(encoding="utf-8"))
    output = Path(a.output); output.mkdir(parents=True, exist_ok=True); started = time.monotonic()
    from red.session_v3 import NetworkSession
    from lenguaje.session import GroundedSession
    from lenguaje.protocol import put, digest, sha
    if a.parent:
        network = NetworkSession.load(a.parent)
    else:
        from red.curriculum_v3 import present_epoch
        # Fixed external experiences, not a choice made from an evaluation ID.
        conditions = {"roles": True, "A_history": 1, "B_history": 1, "C_history": -1, "D_history": 1, "event": "U"}
        network = NetworkSession.create(conditions, tuple(case["translation"])); network.run_until(431)
        network.save(output / "FRESH_AFTER_NETWORK431.deetsnap")
        for offset, context, event in ((500, 1, "U"), (1000, -1, "V")):
            present_epoch(network, {"roles": True, "A_history": 1, "B_history": 1,
                                    "C_history": context, "D_history": 1, "event": event}, offset)
            network.run_until(offset + 431); network.save(output / f"FRESH_AFTER_CURRICULUM{offset+431}.deetsnap")
    if network.world.runtime.current_tick != 1431: raise ValueError("Same network actual1431 required")
    initial = digest(network.world)
    language = GroundedSession.attach(network, tuple(case.get("word_order", ["L1", "L2"])),
                                      case.get("teaching", "paired"), case.get("second_episode", True))
    language.save(output / "BEFORE_NEW_FORMS1431.deetsnap")
    experiences = []
    for slot in range(2):
        experiences.append(language.teach_next()); language.save(output / f"AFTER_NEW_EXPERIENCE{slot+1}.deetsnap")
        put(output / "INCREMENTAL.json", {"experiences": experiences})
    reads = []
    for slot in range(2):
        language.save(output / f"BEFORE_QUERY_SLOT{slot+1}.deetsnap")
        mode = case.get("query_mode", "word")
        result = language.query_next_word(language.state["word_order"][slot]) if mode == "word" else language.name_next_profile(mode)
        reads.append(result); language.save(output / f"ACTUAL_READ{language.tick}.deetsnap")
        put(output / "INCREMENTAL.json", {"experiences": experiences, "readouts": reads})
    language.save(output / "MAIN_FINAL1529.deetsnap")
    result = {"case": case, "initial": initial, "final": digest(network.world), "experiences": experiences,
              "readouts": reads, "same_native_Runtime_in_process": True, "new_preparation": not bool(a.parent),
              "operative_forks": 0, "raw_clock_edits": [], "elapsed_seconds": time.monotonic()-started,
              "source_sha256": {n: sha(ROOT / n) for n in ("src/lenguaje/protocol.py", "src/lenguaje/session.py", "src/lenguaje/continuous_worker.py")}}
    put(output / "MEASUREMENTS.json", result)
    print(json.dumps({"id": case["id"], "profiles": [x["sensor"]["profile"] for x in experiences],
                      "readouts": reads}, ensure_ascii=False))


if __name__ == "__main__": main()
