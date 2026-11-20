"""Keep R01 intact; emit S14 with intrinsic model pauses, speed1.0 unchanged."""
from pathlib import Path
import copy
import datetime as dt
import json
import sys

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "codigo"))
import audio_r12 as base


def main():
    p = json.loads(base.INDEX.read_text(encoding="utf-8"))
    assert len(p["selected"]) == 42
    previous = ROOT / "audio/revisiones/PROVENIENCIA_SINTESIS_R01.json"
    assert not previous.exists()
    previous.write_bytes(base.INDEX.read_bytes())
    base.write_boundary()
    module, np, sf, synth, assets, runner = base.setup()
    # Zero disables only the apparatus's added punctuation-gap extension.
    # The neural model's intrinsic pauses, phonemes and speed remain intact.
    module.PARAMS.update(sentence_pause=0.0, clause_pause=0.0, speed=1.0)
    existing = {r["id"]: r for r in p["takes"]}
    scene = next(s for s in base.source()["scenes"] if s["scene_id"] == "S14")
    changes = []
    for shot in scene["shots"]:
        sid = shot["shot_id"]
        before = existing[p["selected"][sid]]
        rid = sid + "_pausas_R02"
        row = module.synthesize({"id": rid, "es": shot["anchor_exact"]}, np, sf, synth, assets, runner, existing)
        row.update(scene_id="S14", shot_id=sid, window=[shot["start_s"], shot["end_s"]],
                   fit_margin_s=shot["duration_s"]-row["duration"],
                   status="GENERATED_LITERAL_WITH_INTRINSIC_MODEL_PAUSES", subtitle_chunks=base.align_chunks(module, synth, row))
        assert not any(c["start"] is None or c["end"] is None for c in row["subtitle_chunks"])
        existing[rid] = row
        p["selected"][sid] = rid
        changes.append({"shot_id": sid, "prior_take": before["id"], "selected_take": rid,
                        "prior_model_s": before["speech_block_seconds"], "selected_model_s": row["speech_block_seconds"],
                        "speed": 1.0, "intrinsic_neural_pauses_retained": True,
                        "additional_punctuation_pause_extension_disabled": True,
                        "no_phoneme_trim": True, "no_audio_time_stretch": True,
                        "literal_equal": before["es"] == row["es"]})
        p.update(takes=list(existing.values()), updated_utc=dt.datetime.now(dt.timezone.utc).isoformat())
        p["S14_pause_revision"] = {"source_code_sha256": base.sha(__file__), "previous_complete_index": str(previous.relative_to(ROOT)),
            "previous_complete_index_sha256": base.sha(previous), "changes": changes,
            "scope": "Only added punctuation-gap extension is disabled at synthesis; intrinsic model waveform and pauses are retained. All42R01WAVs remain intact."}
        base.atomic_json(base.INDEX, p)
        print(json.dumps(changes[-1]), flush=True)
    for filename, expected in module.EXPECTED_ASSETS.items():
        assert base.sha(base.VOICE_SOURCE/filename) == expected
    print(json.dumps({"selected42": len(p["selected"]), "complete_takes_preserved": len(existing),
        "S14_model_total_s": sum(existing[p["selected"][s["shot_id"]]]["speech_block_seconds"] for s in scene["shots"])}), flush=True)


if __name__ == "__main__":
    main()
