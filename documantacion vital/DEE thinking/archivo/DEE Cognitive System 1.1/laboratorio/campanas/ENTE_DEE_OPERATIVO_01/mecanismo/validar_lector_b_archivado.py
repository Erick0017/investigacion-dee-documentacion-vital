"""Read-only validation of the prospective external valve codec from archives."""
from pathlib import Path
import argparse
import gzip
import hashlib
import importlib.util
import json

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("eo_fixed_b_valve_codec", HERE / "lector_valvula_b_01.py")
CODEC = importlib.util.module_from_spec(SPEC); SPEC.loader.exec_module(CODEC)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path):
    with gzip.open(path, "rt", encoding="utf8") as f:
        return json.load(f)


def decode(points):
    return CODEC.decode_b_bus(points["minus"][6], points["plus"][6])


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--evidence", required=True, type=Path); p.add_argument("--out", required=True, type=Path)
    args = p.parse_args()
    source = args.evidence / "EO01_SOC_AUX_REPEAT.json.gz"
    repeated = load(source); message_rows = []
    for block in repeated["blocks"]:
        critical = block["private_input"]["row"]["critical_tick"]
        points = {f["tick"]: f["message_waypoints"] for f in block["passive_waypoints"]}
        selected = decode(points[critical + CODEC.SAMPLE_OFFSET])
        message_rows.append({"block": block["index"], "critical": critical, "sample_tick": critical + CODEC.SAMPLE_OFFSET,
                             "fixed_decoder": selected,
                             "neighboring_samples": [{"tick": t, "decoded": decode(points[t])} for t in range(critical+27, critical+33)]})
    assert [q["fixed_decoder"]["formed_valve_step"] for q in message_rows] == [-1, 1]
    assert all(q["decoded"]["formed_valve_step"] is None for b in message_rows for q in b["neighboring_samples"] if q["tick"] != b["sample_tick"])
    backgrounds = []
    for name in ("EO01_SOC_AUX_52", "EO01_SOC_AUX_50", "EO01_SOC_AUX_36"):
        path = args.evidence / (name + ".json.gz"); d = load(path)
        frames = d["blocks"][0]["private_input"]["frames"]
        readings = [decode(f["message_waypoints"]) for f in frames]
        assert all(q["formed_valve_step"] is None for q in readings)
        backgrounds.append({"case": name, "source": str(path), "sha256": sha(path), "bytes": path.stat().st_size,
                            "both_bus_samples": len(readings), "qualified_valve_actions": 0,
                            "scope": "No B reader in this earlier same-parent80tick window; not a matched-age no-query intervention at the later message epoch."})
    result = {"schema": "EO01.B_valve_codec.archived_validation.v1", "new_native_ticks": 0,
              "codec_source": {"path": str(HERE / "lector_valvula_b_01.py"), "sha256": sha(HERE / "lector_valvula_b_01.py")},
              "formed_messages_source": {"path": str(source), "bytes": source.stat().st_size, "sha256": sha(source)},
              "two_native_message_samples": message_rows, "background_windows": backgrounds,
              "prospective_control": {"postformed_cut": "SEM4 minus-bus blocker at critical+19, after B output+15; the same bus is read at+30 and SEM4 never qualifies as a message.",
                                      "sham": "Identical SEM4 dose at plus bus, same boundary, while a negative message is expected under the predeclared test.",
                                      "actuator_annulment": "Decode B normally but annul only its external valve step, leaving native transport intact.",
                                      "no_corrective_value": "Codec accepts only two bus RAW values; neither environment calibration, private observation, desired next action nor utility is an argument."},
              "scope": "Archived codec calibration, not execution or validation of the new coupled task. New inputs/reserves and later A actions remain prospective. External valve action is assisted environmental cooperation, not repaired v27 context reception."}
    args.out.write_text(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf8")
    print(json.dumps({"out": str(args.out), "sha256": sha(args.out), "native_ticks": 0,
                      "message_steps": [-1,1], "background_double_bus_samples": sum(q["both_bus_samples"] for q in backgrounds),
                      "codec_sha256": result["codec_source"]["sha256"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
