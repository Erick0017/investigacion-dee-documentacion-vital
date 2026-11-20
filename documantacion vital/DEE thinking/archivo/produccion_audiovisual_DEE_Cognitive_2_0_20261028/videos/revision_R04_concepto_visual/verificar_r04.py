"""R04 final-media verification only. No DEE import or scientific execution.

Run only AFTER the final MP4, English SRT and edit timeline exist. The script
returns one JSON fragment for the canonical production register; it never
edits that register, the Manual, media, visual code or narration. Optional
--fragment writes that one fragment, refusing to replace an existing file.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
VIDEOS = HERE.parent
R03 = VIDEOS / "produccion_cientifica/R03"
WORKSPACE = next(p for p in HERE.parents if (p / "_dee20_trabajo").is_dir())
FF = WORKSPACE / "_dee20_trabajo/presentacion_clara/herramientas/ffmpeg.exe"
PROBE = WORKSPACE / "_dee20_trabajo/video_publico_definitivo/herramientas/ffprobe.exe"
sys.path.insert(0, str(HERE))
from contrato_tiempo_r04 import FPS, FRAMES, DURATION, validate_probe

ORIGINAL_HASHES = {
    "DEE_Cognitive_2_0_Inteligencia_Funcional_R03_1080p.mp4": "697a2b5c63c960cbc20bba90f7c403a9de7ee2ff5749c4f75a0611d2903c3726",
    "timeline_R03.json": "4a9f14bd91b9dc4cc40a38d76958edc9390af324dda22039b4fb2bc15eeefc85",
    "montaje_r03.py": "a2b82a72ba33a428014331b8758515112bc5336eaa302f9db9e7ea075c73af6f",
    "estilo_r03.py": "d8637244c42424d5d571e3a54994829a73f1bcccac529cda69d4163159260ec7",
    "app_visual_r03.py": "03f9e2703f7383d208b5980f9fd9b7d31ef238dd7586778276d60d5543b34cdd",
    "mecanismos_g07_g08.py": "b51312e458449d2d9728a9dbc588cd4e1810b98d3486bf16b5c3c091ccd7d45a",
    "agregacion_r03.py": "9523447af69f53d0d3a0ca12a447f84308609cb9a5ccbe55d4b5f789bb8e8026",
    "voz/locucion_continua_R03.wav": "00e3fd0fe311d15e0ace0aa67a80274adcea3afbfbd1a6a09f127b49ba493954",
    "voz/ambiente_R03.wav": "1935a6162d8487471ce09b6135c222ab84d0ae4b9fdcf63aa0ddd1efd03edcd0",
}


def sha(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for block in iter(lambda: f.read(4 * 1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def timecode(value):
    h, m, rest = value.split(":")
    s, ms = rest.split(",")
    return int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000


def subtitles(path):
    content = path.read_text(encoding="utf-8-sig").replace("\r\n", "\n").strip()
    blocks = re.split(r"\n\s*\n", content)
    cues, problems = [], []
    prior_end = 0
    for index, block in enumerate(blocks, 1):
        lines = block.splitlines()
        if len(lines) < 3:
            raise ValueError("Incomplete SRT block " + str(index))
        number = int(lines[0])
        match = re.fullmatch(r"(\d{2}:\d{2}:\d{2},\d{3}) --> (\d{2}:\d{2}:\d{2},\d{3})", lines[1])
        if match is None:
            raise ValueError("Invalid SRT timestamp in block " + str(index))
        start, end = map(timecode, match.groups())
        text = lines[2:]
        if number != index or not 1 <= len(text) <= 2 or start < 0 or end <= start or end > float(DURATION) + .001:
            problems.append({"cue": number, "lines": len(text), "start": start, "end": end})
        if start < prior_end - .001:
            problems.append({"cue": number, "overlap_seconds": prior_end - start})
        cps = len(" ".join(text)) / (end - start)
        cues.append({"cue": number, "start": start, "end": end, "lines": text, "characters_per_second": cps})
        prior_end = end
    return {"file": str(path), "sha256": sha(path), "cues": len(cues),
            "maximum_lines": max(len(c["lines"]) for c in cues),
            "last_end": cues[-1]["end"], "structural_problems": problems,
            "max_characters_per_second": max(c["characters_per_second"] for c in cues),
            "fast_cues_above23cps": [c for c in cues if c["characters_per_second"] > 23],
            "timing_and_two_line_check_ok": not problems,
            "reading_speed_scope": "CPS is an editorial warning, not automatic certification of readability"}


def select_frames(timeline, extra=None):
    points = {}
    def add(n, label):
        n = max(0, min(FRAMES - 1, int(n)))
        points.setdefault(n, []).append(label)
    add(0, "first frame")
    add(FRAMES - 1, "last frame")
    for scene in timeline["scenes"]:
        start = round(scene["start"] * FPS)
        end = start + scene["frames"]
        if start:
            add(start - 1, "last frame before " + scene["id"])
            add(start, "first frame of " + scene["id"])
        for fraction in (.20, .50, .85):
            add(start + round((scene["frames"] - 1) * fraction), scene["id"] + " decisive sample " + str(fraction))
    s01 = next(s for s in timeline["scenes"] if s["id"] == "s01")
    for t in (7.966666667, 8, 14.966666667, 15, 18.966666667, 19):
        add(round((s01["start"] + t) * FPS), "opening shot boundary " + str(t))
    s04 = next(s for s in timeline["scenes"] if s["id"] == "s04")
    # The shot follows sentence-indexed G07 phases; use the actual edit marks.
    for j in (2, 3, 4, 5, 6, 7, 9):
        if j < len(s04["marks"]):
            add(round((s04["start"] + s04["marks"][j]["start"] + .25) * FPS), "G07 phase at sentence " + str(j))
    s08 = next(s for s in timeline["scenes"] if s["id"] == "s08")
    for t in (10.466666667, 10.5, 12.5, 14.5, 18.466666667, 18.5):
        add(round((s08["start"] + t) * FPS), "a26 prepared chain shot " + str(t))
    if extra:
        for row in extra:
            add(row["frame"], row["label"])
    return [{"frame": frame, "seconds": frame / FPS, "labels": labels} for frame, labels in sorted(points.items())]


def original_sources(extra_reference=None):
    expected = {str((R03 / name).resolve()): digest for name, digest in ORIGINAL_HASHES.items()}
    if extra_reference:
        root = json.loads(extra_reference.read_text(encoding="utf-8-sig"))
        def visit(v):
            if isinstance(v, dict):
                file = v.get("path", v.get("file"))
                digest = v.get("sha256")
                if isinstance(file, str) and isinstance(digest, str) and re.fullmatch(r"[0-9a-f]{64}", digest):
                    p = Path(file)
                    p = p if p.is_absolute() else extra_reference.parent / p
                    if p.resolve().is_relative_to(R03.resolve()):
                        expected[str(p.resolve())] = digest
                for w in v.values():
                    visit(w)
            elif isinstance(v, list):
                for w in v:
                    visit(w)
        visit(root)
    rows = []
    for name, digest in expected.items():
        p = Path(name)
        actual = sha(p) if p.is_file() else None
        rows.append({"file": name, "expected_sha256": digest, "actual_sha256": actual,
                     "unchanged": actual == digest})
    return rows


def verify(final, srt, timeline_path, *, qa_directory=None, source_reference=None, extra_shots=None, timeout=900):
    final = final.resolve(strict=True)
    srt = srt.resolve(strict=True)
    timeline_path = timeline_path.resolve(strict=True)
    timeline = json.loads(timeline_path.read_text(encoding="utf-8-sig"))
    assert timeline["fps"] == FPS and sum(s["frames"] for s in timeline["scenes"]) == FRAMES
    assert abs(timeline["duration"] - float(DURATION)) < 1e-9
    qa = qa_directory or HERE / "qa_final" / datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    qa = qa.resolve()
    if not qa.is_relative_to(HERE.resolve()) or qa.exists():
        raise ValueError("QA uses a new directory inside R04; prior checks are preserved")
    qa.mkdir(parents=True)
    logfile = qa / "technical_commands.log"
    report = {"schema": "DEE.R04.final_media_verification.v1", "started_utc": datetime.now(timezone.utc).isoformat(),
              "new_native_ticks": 0, "validator_file": str(Path(__file__)), "validator_sha256": sha(__file__),
              "final": {"file": str(final), "bytes": final.stat().st_size, "sha256": sha(final)},
              "timeline": {"file": str(timeline_path), "sha256": sha(timeline_path)},
              "QA_directory": str(qa), "checks": {}, "errors": [],
              "visual_review": "PNG files are evidence awaiting actual individual review; contact sheet alone is insufficient",
              "audio_listening": "No human or model listening is performed or certified by this technical script"}
    commands = []
    def run(label, binary, args):
        started = time.monotonic()
        done = subprocess.run([str(binary), *map(str, args)], capture_output=True, text=True,
                              encoding="utf8", errors="replace", timeout=timeout)
        commands.append({"label": label, "returncode": done.returncode,
                         "host_seconds": time.monotonic() - started})
        with logfile.open("a", encoding="utf8") as f:
            f.write("\n### " + label + "\n" + subprocess.list2cmdline([str(binary), *map(str, args)]) + "\n")
            f.write(done.stderr)
        if done.returncode:
            raise RuntimeError(label + " failed; full stderr preserved in " + str(logfile))
        return done
    def checked(label, callback):
        try:
            value = callback()
            report["checks"][label] = {"ok": True, "data": value}
        except Exception as error:
            report["checks"][label] = {"ok": False, "error": str(error), "type": type(error).__name__}
            report["errors"].append(label)
    def probe():
        done = run("probe_decoded_frames", PROBE, ["-v", "error", "-count_frames", "-show_entries",
                   "stream=codec_type,codec_name,width,height,pix_fmt,r_frame_rate,avg_frame_rate,time_base,nb_frames,nb_read_frames,duration,start_time,sample_rate,channels,sample_aspect_ratio,display_aspect_ratio",
                   "-show_entries", "format=duration,size", "-of", "json", final])
        data = json.loads(done.stdout)
        validation = validate_probe(data, require_decoded_count=True)
        audio = next(s for s in data["streams"] if s["codec_type"] == "audio")
        video = next(s for s in data["streams"] if s["codec_type"] == "video")
        assert audio["channels"] == 2
        assert video["sample_aspect_ratio"] == "1:1" and video["display_aspect_ratio"] == "16:9"
        assert abs(float(data["format"]["duration"]) - float(DURATION)) <= 1 / FPS
        return {"probe": data, "validation": validation}
    checked("probe", probe)
    def cfr():
        done = run("packet_presentation_cadence", PROBE, ["-v", "error", "-select_streams", "v:0", "-show_packets",
                   "-show_entries", "packet=pts,duration:stream=time_base", "-of", "json", final])
        data = json.loads(done.stdout)
        tb = Fraction(data["streams"][0]["time_base"])
        packets = data["packets"]
        assert len(packets) == FRAMES
        pts = sorted(int(p["pts"]) for p in packets)
        assert len(set(pts)) == FRAMES and pts[0] == 0
        assert all(Fraction(int(p["duration"])) * tb == Fraction(1, FPS) for p in packets)
        assert all(Fraction(b - a) * tb == Fraction(1, FPS) for a, b in zip(pts, pts[1:]))
        return {"packets": len(packets), "first_pts": pts[0], "last_pts": pts[-1], "time_base": str(tb),
                "every_presentation_interval_seconds": "1/30", "unique_timestamps": True}
    checked("CFR_exact_packet_timestamps", cfr)
    checked("strict_full_decode", lambda: {"exit_code": run("strict_full_decode", FF,
        ["-hide_banner", "-v", "error", "-nostdin", "-xerror", "-err_detect", "explode", "-i", final,
         "-map", "0:v:0", "-map", "0:a:0", "-f", "null", "NUL"]).returncode,
        "scope": "Full H264 and AAC decode with xerror and err_detect explode; no scientific execution"})
    def srt_check():
        value = subtitles(srt)
        if not value["timing_and_two_line_check_ok"]:
            raise ValueError(json.dumps(value["structural_problems"], ensure_ascii=False))
        return value
    checked("English_SRT", srt_check)
    def loudness():
        done = run("audio_loudness", FF, ["-hide_banner", "-nostdin", "-i", final, "-vn", "-af",
                   "loudnorm=I=-16:TP=-1.5:LRA=9:print_format=json", "-f", "null", "NUL"])
        values = re.findall(r'\{\s*"input_i".*?\}', done.stderr, re.S)
        if not values:
            raise ValueError("No loudness analysis returned")
        data = json.loads(values[-1])
        i, tp = float(data["input_i"]), float(data["input_tp"])
        assert i != float("-inf") and tp < 0, "Audio is silent or decoded true peaks reach/exceed 0 dBTP"
        return {"input_integrated_LUFS": i, "input_true_peak_dBTP": tp,
                "input_LRA_LU": float(data["input_lra"]), "analysis_only_final_not_modified": True,
                "level_warnings": ([] if -19 <= i <= -13 else ["Integrated loudness outside -19..-13LUFS"]),
                "listening_certified": False}
    checked("audio_loudness_and_peaks", loudness)
    def sample_peak():
        done = run("audio_sample_peaks", FF, ["-hide_banner", "-nostdin", "-i", final, "-vn", "-af", "volumedetect", "-f", "null", "NUL"])
        mean = re.search(r"mean_volume:\s*(-?[\d.]+) dB", done.stderr)
        maximum = re.search(r"max_volume:\s*(-?[\d.]+) dB", done.stderr)
        if not (mean and maximum):
            raise ValueError("No decoded sample-peak analysis returned")
        return {"mean_sample_level_dBFS": float(mean[1]), "max_sample_level_dBFS": float(maximum[1]),
                "scope": "Whole-stream measured levels, not a judgement about edits, pronunciation or naturalness"}
    checked("audio_sample_peaks", sample_peak)
    def images():
        extra = json.loads(extra_shots.read_text(encoding="utf8")) if extra_shots else None
        points = select_frames(timeline, extra)
        expression = "+".join("eq(n," + str(x["frame"]) + ")" for x in points)
        graph = "[0:v:0]select='" + expression + "',split=3[a][b][c];[a]null[full];[b]scale=960:540:flags=lanczos[mid];[c]scale=480:270:flags=lanczos[phone]"
        args = ["-hide_banner", "-v", "warning", "-nostdin", "-n", "-i", final, "-filter_complex", graph]
        for tag, name in (("full", "1080"), ("mid", "0540"), ("phone", "phone")):
            args += ["-map", "[" + tag + "]", "-fps_mode", "passthrough", "-start_number", "0",
                     "-compression_level", "4", "-f", "image2", qa / ("frame_" + name + "_%03d.png")]
        run("postencode_temporal_PNG_samples", FF, args)
        from PIL import Image
        entries = []
        for sequence, point in enumerate(points):
            files = []
            for suffix, size in (("1080", (1920, 1080)), ("0540", (960, 540)), ("phone", (480, 270))):
                path = qa / ("frame_" + suffix + "_" + f"{sequence:03d}" + ".png")
                with Image.open(path) as im:
                    assert im.size == size
                    im.verify()
                files.append({"file": str(path), "dimensions": list(size), "sha256": sha(path)})
            entries.append({**point, "PNG": files})
        return {"selected_frames": len(points), "scales_per_frame": 3, "frames": entries,
                "scope": "Actual encoded MP4 frames, not pre-render images. Every internal scene cut has last/first frame samples. No visual certification without inspecting the PNGs."}
    checked("postencode_temporal_images", images)
    def protected():
        rows = original_sources(source_reference)
        assert all(r["unchanged"] for r in rows), "A protected original is absent or differs"
        return rows
    checked("preserved_R03_originals", protected)
    checked("final_media_unchanged_during_validation", lambda: {"same_sha256": sha(final) == report["final"]["sha256"]})
    if not report["checks"]["final_media_unchanged_during_validation"].get("data", {}).get("same_sha256"):
        report["errors"].append("final_media_changed_during_validation")
    report["commands"] = commands
    report["command_log"] = str(logfile)
    report["command_log_sha256"] = sha(logfile)
    report["technical_checks_ok"] = not report["errors"]
    report["ended_utc"] = datetime.now(timezone.utc).isoformat()
    report["scope_limits"] = ["Technical decode/timing checks do not certify human comprehension or natural narration",
                              "Audio was measured; this script does not listen",
                              "No DEE simulation, original media mutation, Word edit or experimental evidence change"]
    return report


def main():
    p = argparse.ArgumentParser(__doc__)
    p.add_argument("final", type=Path)
    p.add_argument("--srt", type=Path, required=True)
    p.add_argument("--timeline", type=Path, default=HERE / "timeline_R04.json")
    p.add_argument("--qa-directory", type=Path)
    p.add_argument("--source-reference", type=Path)
    p.add_argument("--extra-shots", type=Path)
    p.add_argument("--timeout", type=int, default=900)
    p.add_argument("--fragment", type=Path)
    a = p.parse_args()
    if a.fragment and a.fragment.exists():
        raise FileExistsError("Existing verification fragment is preserved")
    report = verify(a.final, a.srt, a.timeline, qa_directory=a.qa_directory,
                    source_reference=a.source_reference, extra_shots=a.extra_shots, timeout=a.timeout)
    output = json.dumps(report, ensure_ascii=False, indent=2)
    if a.fragment:
        destination = a.fragment.resolve()
        if not destination.is_relative_to(HERE.resolve()):
            raise ValueError("The optional fragment must remain in R04")
        destination.write_text(output + "\n", encoding="utf8")
        print(json.dumps({"fragment": str(destination), "sha256": sha(destination), "technical_checks_ok": report["technical_checks_ok"]}))
    else:
        print(output)
    if not report["technical_checks_ok"]:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
