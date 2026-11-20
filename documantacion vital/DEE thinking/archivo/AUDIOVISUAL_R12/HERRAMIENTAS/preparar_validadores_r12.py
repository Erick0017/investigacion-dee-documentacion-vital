"""Transparent adaptation of the existing local R08 verifier; no media runs."""
from pathlib import Path
import ast
import hashlib
import json

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT.with_name("AUDIOVISUAL_R08") / "codigo/verificar_entrega_r08.py"
DEST = ROOT / "HERRAMIENTAS/validar_entrega.py"
ORIGINAL = ROOT / "HERRAMIENTAS/origen/verificar_entrega_r08_original.py"
EXPECTED = "24e87524144d04624a12d42c48a396b0eeed40599b78dad43fe07501ad53e532"


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    assert sha(SOURCE) == EXPECTED
    assert not DEST.exists() and not ORIGINAL.exists()
    ORIGINAL.parent.mkdir(parents=True, exist_ok=True)
    ORIGINAL.write_bytes(SOURCE.read_bytes())
    s = SOURCE.read_text(encoding="utf-8")
    old_doc = s[:s.index("from __future__")]
    s = s.replace(old_doc, '''"""Local R12 technical verifier, transparently adapted from the existing R08 code.

The original R12 toolkit was not recovered. This is not its validar_entrega.py.
Checks only a CLOSED390s export, exact packets, native-PNG creation link and full
strict audio/video decode with sample captures. No DEE or scene modules imported.
Does not certify scientific evidence, perception, listening or comprehension.
"""\n''', 1)
    s = s.replace('MANDATORY_SECONDS = [2, 8, 35, 55, 83, 110, 139, 171, 210, 238, 282, 306, 331, 350, 382]',
                  'MANDATORY_SECONDS = []  # R08-specific list is not imported into R12.')
    s = s.replace('self.duration = 126 if args.central126s else 390', 'self.duration = 390')
    s = s.replace('self.prefix = args.prefix or ("CENTRAL126_R08" if args.central126s else "FINAL_R08")', 'self.prefix = args.prefix or "FINAL_R12"')
    s = s.replace('self.folder = ROOT / "verificaciones" / self.prefix', 'self.folder = ROOT / "AUDITORIA" / self.prefix')
    s = s.replace('self.captures = ROOT / "qa/codificado" / self.prefix', 'self.captures = self.folder / "capturas"')
    s = s.replace('        if not self.video.is_file():', '''        args.report = args.report if args.report.is_absolute() else ROOT / args.report
        args.report = args.report.resolve()
        if ROOT not in args.report.parents:
            raise ValueError("--report must stay inside AUDIOVISUAL_R12")
        if args.report.exists():
            raise FileExistsError("Earlier requested report is preserved: " + str(args.report))
        if not self.video.is_file():''', 1)
    s = s.replace('"schema": "DEE.R08.delivery_verification.v1"', '"schema": "DEE.R12.LOCAL_DERIVED.delivery_verification.v1"')
    s = s.replace('"mode": "central126s" if args.central126s else "final390s"', '"mode": "final390s"')
    s = s.replace('            "visual_scope":', '''            "tool_origin": {"status": "LOCAL_DERIVATION_NOT_ORIGINAL_R12_TOOLKIT", "R08_source_sha256": "'''+EXPECTED+'''", "changes_manifest": "HERRAMIENTAS/ORIGEN_Y_CAMBIOS_VALIDADORES_R12.json"},
            "original_R12_toolkit_status": "NO EVALUADO: original package and validator were not recovered",
            "separate_review_states": {"scientific_evidence": "NO EVALUADO by this tool", "motion_perception": "NO EVALUADO by this tool", "voice_listening": "NO EVALUADO", "audience_comprehension": "NO EVALUADO", "transfer": "NO EVALUADO by this tool"},
            "visual_scope":''', 1)
    s = s.replace('(ROOT / "verificaciones").glob("RENDER_*.json")', '(ROOT / "AUDITORIA").glob("RENDER_*.json")')
    s = s.replace('Source PNG path outside R08:', 'Source PNG path outside R12:')
    s = s.replace('current = (row["scene_id"], row["shot_id"], row["raster_id"], row["source_data_hash"])',
                  'current = (row["scene_id"], row["shot_id"], row["raster_id"])  # Raster transitions, not editorial source hashes.')
    s = s.replace('        self.report["render_state_transitions"] = transitions',
                  '        self.report["render_state_transitions"] = transitions\n        self.report["transition_scope"] = "Rendered-raster transitions only. Source_data_hash may include editorial progress; neither transitions nor source hashes count DEE physical events."')
    s = s.replace('guion_fuente/SHOTLIST_R08.json', 'guion_fuente/SHOTLIST_R12_DERIVADO_DEL_DOCX.json')
    s = s.replace('audio/TIEMPOS_ANCLAS_R08.json', 'audio/TIEMPOS_ANCLAS_R12.json')
    s = s.replace('        schedule = load(schedule_path)["rows"]', '''        literal = load(shots_path)
        actual = load(schedule_path)
        schedule = actual["rows"]
        self.check("R12_derived_contract_14scenes_42shots", len(scenes)==14 and sum(len(s["shots"]) for s in scenes)==42 and literal.get("not_original_specification") is True, "14/42 explicit DOCX-derived contract", [len(scenes),sum(len(s["shots"]) for s in scenes),literal.get("not_original_specification")])
        self.check("R12_actual_schedule_42_all_fit", len(schedule)==42 and actual.get("all_fit") is True and not actual.get("violations"), "42 fitted voice anchors", [len(schedule),actual.get("all_fit"),actual.get("violations")])''', 1)
    s = s.replace('        for row in transitions or []:', '''        for shot in schedule:
            a,b=shot["first_visual_frame_30fps"],shot["end_visual_frame_exclusive_30fps"]
            add((a+b-1)//2, {"kind": "actual_shot_midpoint_sample_NOT_physical_event", "shot": shot["shot_id"]})
        for row in transitions or []:''', 1)
    s = s.replace('        target = self.folder / "RESULTADO.json"\n        save_new(target, self.report)',
                  '        target = self.args.report\n        target.parent.mkdir(parents=True, exist_ok=True)\n        save_new(target, self.report)')
    s = s.replace('parser.add_argument("--video", type=Path, required=True)', 'parser.add_argument("video", type=Path, help="Closed final MP4; never modified")\n    parser.add_argument("--report", type=Path, required=True, help="New report path inside AUDIOVISUAL_R12")')
    s = s.replace('    parser.add_argument("--central126s", action="store_true")\n', '')
    assert 'central126s' not in s
    ast.parse(s)
    DEST.write_text(s, encoding="utf-8")
    manifest = {"schema": "DEE.R12.validator_derivation.R01", "original_R12_toolkit": "NOT RECOVERED; NO EVALUADO; never represented as original",
        "source": {"path": str(SOURCE), "sha256": EXPECTED, "exact_preserved_copy": str(ORIGINAL.relative_to(ROOT)), "copy_sha256": sha(ORIGINAL)},
        "derived": {"path": str(DEST.relative_to(ROOT)), "sha256": sha(DEST)},
        "changes": ["Fixed390s/11700frames only; removed R08central mode and old mandatory sample times.",
            "Positional VIDEO plus --report, --render-proof, --prefix; all outputs under local AUDITORIA.",
            "Uses explicit R12DOCX derivative and actual14scene/42shot schedule; checks fitted status.",
            "Samples source-raster transitions, actual shot midpoints and neighbouring scene/shot/state boundaries. Editorial source_data_hash changes alone are not physical or raster events.",
            "Retains full exact packet cadence scan, H2641080p30/SAR/yuv420p/AAC48kstereo>=192kbps, all native PNG SHA/dimension checks, encoded-video-payload comparison and strict full decode.",
            "Scientific evidence, human motion/voice perception, comprehension, transfer and original-package validation explicitly remain outside technical scope."],
        "not_executed_on_final_media": True, "syntax_only_checked": True, "new_Native_ticks": 0}
    target=ROOT/"HERRAMIENTAS/ORIGEN_Y_CAMBIOS_VALIDADORES_R12.json"
    target.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"derived": str(DEST), "bytes": DEST.stat().st_size,"sha256":sha(DEST),"source_preserved":sha(ORIGINAL)==EXPECTED,"AST_valid":True,"not_executed_on_final_media":True}))


if __name__ == "__main__":
    main()
