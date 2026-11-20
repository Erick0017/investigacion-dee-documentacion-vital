"""Local R12 technical verifier, transparently adapted from the existing R08 code.

The original R12 toolkit was not recovered. This is not its validar_entrega.py.
Checks only a CLOSED390s export, exact packets, native-PNG creation link and full
strict audio/video decode with sample captures. No DEE or scene modules imported.
Does not certify scientific evidence, perception, listening or comprehension.
"""
from __future__ import annotations
import argparse
from collections import Counter
from datetime import datetime, timezone
from fractions import Fraction
import gzip
import hashlib
import json
from pathlib import Path
import re
import struct
import subprocess
import sys
import time
import zlib

ROOT = Path(__file__).resolve().parents[1]
TESTS = next(p for p in ROOT.parents if (p / "_dee20_trabajo").is_dir())
FF = TESTS / "_dee20_trabajo/presentacion_clara/herramientas/ffmpeg.exe"
PROBE = TESTS / "_dee20_trabajo/video_publico_definitivo/herramientas/ffprobe.exe"
MANDATORY_SECONDS = []  # R08-specific list is not imported into R12.


def sha(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(4 * 1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def canonical_hash(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True,
        separators=(",", ":")).encode()).hexdigest()


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def save_new(path, value):
    with Path(path).open("x", encoding="utf-8") as handle:
        json.dump(value, handle, ensure_ascii=False, indent=2, allow_nan=False)
        handle.write("\n")


def png_info(path):
    with Path(path).open("rb") as handle:
        header = handle.read(33)
    if len(header) != 33 or header[:8] != b"\x89PNG\r\n\x1a\n" or header[12:16] != b"IHDR":
        raise ValueError("Invalid PNG/IHDR: " + str(path))
    if struct.unpack(">I", header[8:12])[0] != 13 or zlib.crc32(header[12:29]) & 0xffffffff != struct.unpack(">I", header[29:33])[0]:
        raise ValueError("PNG IHDR CRC mismatch: " + str(path))
    width, height, depth, kind = struct.unpack(">IIBB", header[16:26])
    return {"width": width, "height": height, "bit_depth": depth, "color_type": kind,
            "bytes": Path(path).stat().st_size, "sha256": sha(path)}


def integer(value):
    if isinstance(value, bool) or not isinstance(value, (str, int)) or not re.fullmatch(r"-?\d+", str(value)):
        raise ValueError("Timestamp/size must be an exact integer: " + repr(value))
    return int(value)


class Verification:
    def __init__(self, args):
        self.args = args
        self.video = args.video.resolve()
        self.duration = 390
        self.frames = self.duration * 30
        self.prefix = args.prefix or "FINAL_R12"
        if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,79}", self.prefix) or self.prefix.upper() in {"CON", "NUL", "PRN", "AUX"}:
            raise ValueError("--prefix must be one safe directory-name component")
        self.folder = ROOT / "AUDITORIA" / self.prefix
        self.captures = self.folder / "capturas"
        if self.folder.exists() or self.captures.exists():
            raise FileExistsError("Existing verification/capture prefix is preserved: " + self.prefix)
        args.report = args.report if args.report.is_absolute() else ROOT / args.report
        args.report = args.report.resolve()
        if ROOT not in args.report.parents:
            raise ValueError("--report must stay inside AUDIOVISUAL_R12")
        if args.report.exists():
            raise FileExistsError("Earlier requested report is preserved: " + str(args.report))
        if not self.video.is_file():
            raise FileNotFoundError(self.video)
        self.folder.mkdir(parents=True, exist_ok=False)
        self.captures.mkdir(parents=True, exist_ok=False)
        self.initial_signature = self.signature(self.video)
        self.report = {"schema": "DEE.R12.LOCAL_DERIVED.delivery_verification.v1", "started_utc": datetime.now(timezone.utc).isoformat(),
            "video": str(self.video), "mode": "final390s",
            "expected": {"frames": self.frames, "duration_s": self.duration, "fps": 30, "width": 1920, "height": 1080,
                         "SAR": "1:1", "video": "h264/yuv420p", "audio": "AAC48kHzstereo>=192000bps"},
            "checks": [], "errors": [], "commands": [], "new_DEE_ticks": 0, "scene_modules_imported": False,
            "auditory_review_performed": False, "full_motion_visual_review_performed": False,
            "tool_origin": {"status": "LOCAL_DERIVATION_NOT_ORIGINAL_R12_TOOLKIT", "R08_source_sha256": "24e87524144d04624a12d42c48a396b0eeed40599b78dad43fe07501ad53e532", "changes_manifest": "HERRAMIENTAS/ORIGEN_Y_CAMBIOS_VALIDADORES_R12.json"},
            "original_R12_toolkit_status": "NO EVALUADO: original package and validator were not recovered",
            "separate_review_states": {"scientific_evidence": "NO EVALUADO by this tool", "motion_perception": "NO EVALUADO by this tool", "voice_listening": "NO EVALUADO", "audience_comprehension": "NO EVALUADO", "transfer": "NO EVALUADO by this tool"},
            "visual_scope": "Decoded captures and source-PNG checks only. A separate person/agent must inspect them; this script does not certify comprehension or naturalness."}

    @staticmethod
    def signature(path):
        st = path.stat()
        return {"bytes": st.st_size, "mtime_ns": st.st_mtime_ns}

    def check(self, name, ok, expected=None, actual=None):
        self.report["checks"].append({"check": name, "ok": bool(ok), "expected": expected, "actual": actual})

    def command(self, label, argv, timeout=None):
        out = self.folder / (label + ".stdout")
        err = self.folder / (label + ".stderr")
        argv = [str(x) for x in argv]
        row = {"label": label, "command": argv, "stdout": str(out), "stderr": str(err)}
        self.report["commands"].append(row)
        save_new(self.folder / (label + ".command.json"), row)
        start = time.monotonic()
        with out.open("xb") as stdout, err.open("xb") as stderr:
            try:
                p = subprocess.run(argv, stdin=subprocess.DEVNULL, stdout=stdout, stderr=stderr,
                    timeout=timeout or self.args.timeout, check=False,
                    creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
                row["returncode"] = p.returncode
            except (subprocess.TimeoutExpired, OSError) as exc:
                row.update(returncode=None, exception=type(exc).__name__, message=str(exc))
        row.update(host_seconds=round(time.monotonic() - start, 6),
            stdout_sha256=sha(out), stderr_sha256=sha(err), stdout_bytes=out.stat().st_size,
            stderr_bytes=err.stat().st_size)
        if row["returncode"] != 0:
            raise RuntimeError(label + " failed: " + json.dumps(row, ensure_ascii=False))
        return out

    def phase(self, name, action):
        try:
            return action()
        except Exception as exc:
            self.report["errors"].append({"phase": name, "exception": type(exc).__name__, "message": str(exc)})
            return None

    def metadata(self):
        self.report["tools"] = {"ffmpeg": {"path": str(FF), "sha256": sha(FF)},
                                "ffprobe": {"path": str(PROBE), "sha256": sha(PROBE)}}
        data = load(self.command("01_probe", [PROBE, "-v", "error", "-show_streams", "-show_format", "-of", "json", self.video]))
        self.report["probe"] = data
        videos = [s for s in data["streams"] if s["codec_type"] == "video"]
        audios = [s for s in data["streams"] if s["codec_type"] == "audio"]
        self.check("one_video_and_one_audio", len(videos) == len(audios) == 1, [1, 1], [len(videos), len(audios)])
        if len(videos) != 1 or len(audios) != 1:
            raise ValueError("Need exactly one video and one audio stream")
        self.v, self.a = videos[0], audios[0]
        for field, value in [("codec_name", "h264"), ("width", 1920), ("height", 1080), ("pix_fmt", "yuv420p"), ("sample_aspect_ratio", "1:1")]:
            self.check("video_" + field, self.v.get(field) == value, value, self.v.get(field))
        for field in ["avg_frame_rate", "r_frame_rate"]:
            self.check("video_" + field, Fraction(self.v[field]) == 30, "30/1", self.v[field])
        self.check("declared_video_frames", integer(self.v.get("nb_frames", "-1")) == self.frames, self.frames, self.v.get("nb_frames"))
        for name, value in [("video", self.v.get("duration")), ("audio", self.a.get("duration")), ("container", data["format"].get("duration"))]:
            self.check(name + "_duration", value is not None and abs(Fraction(value) - self.duration) <= Fraction(1, 30),
                       str(self.duration) + "s ±1/30s", value)
        for field, value in [("codec_name", "aac"), ("sample_rate", "48000"), ("channels", 2), ("channel_layout", "stereo")]:
            self.check("audio_" + field, self.a.get(field) == value, value, self.a.get(field))
        bitrate = integer(self.a.get("bit_rate", "0"))
        self.check("AAC_declared_bitrate_at_least192kbps", bitrate >= 192000, ">=192000", bitrate)
        self.report["video_identity"] = {"bytes": self.video.stat().st_size, "sha256": sha(self.video)}
        return data

    def packets(self):
        data = load(self.command("02_all_packets", [PROBE, "-v", "error", "-show_packets",
            "-show_entries", "packet=codec_type,stream_index,pts,dts,duration,size,pos,flags", "-of", "json", self.video]))
        packets = [p for p in data["packets"] if p.get("stream_index") == self.v["index"]]
        tb = Fraction(self.v["time_base"])
        step = Fraction(1, 30) / tb
        if step.denominator != 1 or step <= 0:
            raise ValueError("One30fps interval is not a positive integer in this timebase")
        step = int(step)
        values = [{key: integer(p[key]) for key in ["pts", "dts", "duration"]} for p in packets]
        pts = [x["pts"] for x in values]
        dts = [x["dts"] for x in values]
        ordered = sorted(pts)
        pts_bad = [{"sorted_index": i, "prior": a, "next": b} for i, (a, b) in enumerate(zip(ordered, ordered[1:]), 1) if b - a != step]
        dts_bad = [{"packet": i, "prior": a, "next": b} for i, (a, b) in enumerate(zip(dts, dts[1:]), 1) if b - a != step]
        durations_bad = [{"packet": i, "duration": x["duration"]} for i, x in enumerate(values) if x["duration"] != step]
        self.check("video_packet_count", len(values) == self.frames, self.frames, len(values))
        self.check("unique_sorted_video_PTS_exact_CFR", len(set(pts)) == self.frames and not pts_bad and bool(ordered) and ordered[0] == 0 and ordered[-1] == (self.frames - 1) * step,
                   {"unique": self.frames, "first_PTS": 0, "last_PTS": (self.frames - 1) * step, "delta": step},
                   {"unique": len(set(pts)), "first": ordered[0] if ordered else None, "last": ordered[-1] if ordered else None, "bad_intervals": pts_bad})
        self.check("packet_decode_order_DTS_exact_CFR", len(dts) == self.frames and not dts_bad, {"count": self.frames, "delta": step},
                   {"count": len(dts), "first": dts[0] if dts else None, "last": dts[-1] if dts else None, "bad_intervals": dts_bad})
        self.check("every_video_packet_duration_exact", not durations_bad and len(values) == self.frames, step, durations_bad)
        self.report["all_frame_timestamp_scan"] = {"time_base": str(tb), "integer_ticks_per_frame": step,
            "packets_checked": len(values), "raw_PTS_reorders_from_Bframes": sum(b < a for a, b in zip(pts, pts[1:])),
            "meaning": "All video packet PTS/DTS/durations checked as integers. Packets are in decode/DTS order; sortedPTS are in presentation order. Negative starting DTS is allowed codec delay, not a cadence failure."}
        audio_bytes = sum(integer(p["size"]) for p in data["packets"] if p.get("stream_index") == self.a["index"])
        self.report["audio_packet_payload_average_bps"] = str(Fraction(audio_bytes * 8, self.duration))

    def packet_hash(self, video, label):
        output = self.command(label, [FF, "-nostdin", "-hide_banner", "-v", "error", "-i", video,
            "-map", "0:v:0", "-an", "-sn", "-dn", "-c:v", "copy", "-f", "hash", "-hash", "sha256", "pipe:1"])
        match = re.fullmatch(r"\s*SHA256=([0-9a-fA-F]{64})\s*", output.read_text(encoding="utf-8"))
        if not match:
            raise ValueError("Unexpected encoded-packet hash output")
        return match.group(1).lower()

    def native_sources(self):
        final_packet_hash = self.packet_hash(self.video, "03_final_video_packet_hash")
        candidates = [self.args.render_proof.resolve()] if self.args.render_proof else sorted((ROOT / "AUDITORIA").glob("RENDER_*.json"))
        results = []
        selected = None
        for index, path in enumerate(candidates):
            proof = load(path)
            if proof.get("frames") != self.frames:
                continue
            visual = Path(proof["video"])
            row = {"proof": str(path), "proof_sha256": sha(path), "visual": str(visual)}
            if not visual.is_file():
                row["rejection"] = "Source visual MP4 is missing"
            elif sha(visual) != proof.get("sha256"):
                row["rejection"] = "Source visual MP4 SHA differs from creation proof"
            else:
                packet_hash = self.packet_hash(visual, "04_source_video_%03d_packet_hash" % index)
                row["encoded_video_payload_SHA256"] = packet_hash
                row["matches_delivered_video_payload"] = packet_hash == final_packet_hash
                if row["matches_delivered_video_payload"] and selected is None:
                    selected = (path, proof)
            results.append(row)
        self.report["source_proof_candidates"] = results
        self.check("delivered_video_matches_creation_proof_packets", selected is not None, "At least one complete render proof with exact matching encoded-video payload", bool(selected))
        if selected is None:
            raise ValueError("No matching RENDER_*.json/source visual video: native1080creation not verified")
        path, proof = selected
        self.proof = proof
        self.report["selected_render_proof"] = {"path": str(path), "sha256": sha(path), "encoded_video_payload_SHA256": final_packet_hash}
        self.check("creation_proof_dimensions_and_frames", [proof.get(k) for k in ["width", "height", "fps", "frames"]] == [1920, 1080, 30, self.frames],
                   [1920, 1080, 30, self.frames], [proof.get(k) for k in ["width", "height", "fps", "frames"]])
        command = proof.get("command", [])
        native_command = "-video_size" in command and command[command.index("-video_size") + 1] == "1920x1080" and "rawvideo" in command
        resize_filters = [x for x in command if re.search(r"(?:^|[,;])(?:scale|zscale|scale2ref)=", str(x))]
        self.check("creation_command_native1080_rawvideo_no_resize", native_command and not resize_filters,
                   "1920x1080rawvideo stdin, no scaling filter", {"native_rawvideo": native_command, "resize_filters": resize_filters})
        rasters = proof.get("all_native_rasters", {})
        self.check("creation_proof_native_raster_count", bool(rasters) and proof.get("native_rasters") == len(rasters), proof.get("native_rasters"), len(rasters))
        png_rows = []
        for key, row in rasters.items():
            png = Path(row["source_png"]).resolve()
            if ROOT not in png.parents:
                raise ValueError("Source PNG path outside R12: " + str(png))
            info = png_info(png)
            png_rows.append(dict(info, raster_id=key, path=str(png), declared_sha256=row["PNG_sha256"]))
        self.report["native_source_PNGs"] = png_rows
        bad = [x for x in png_rows if (x["width"], x["height"]) != (1920, 1080) or x["sha256"] != x["declared_sha256"]]
        self.check("all_native_source_PNG_dimensions_and_SHA", not bad and bool(png_rows), "Every creation PNG is1920x1080and byte-identical to its proof", bad)
        trace = Path(proof["frame_trace"])
        self.check("frame_trace_SHA", sha(trace) == proof["frame_trace_sha256"], proof["frame_trace_sha256"], sha(trace))
        transitions = []
        prior = None
        count = 0
        with gzip.open(trace, "rt", encoding="utf-8") as handle:
            for count, line in enumerate(handle, 1):
                row = json.loads(line)
                if row["frame"] != count - 1 or row["raster_id"] not in rasters:
                    raise ValueError("Frame trace is nonconsecutive or references an unknown native raster")
                current = (row["scene_id"], row["shot_id"], row["raster_id"])  # Raster transitions, not editorial source hashes.
                if current != prior:
                    transitions.append({"frame": row["frame"], "scene_id": row["scene_id"], "shot_id": row["shot_id"],
                                        "raster_id": row["raster_id"], "source_data_hash": row["source_data_hash"]})
                prior = current
        self.check("every_frame_has_native_raster_creation_record", count == self.frames, self.frames, count)
        self.report["render_state_transitions"] = transitions
        self.report["transition_scope"] = "Rendered-raster transitions only. Source_data_hash may include editorial progress; neither transitions nor source hashes count DEE physical events."
        self.report["native_resolution_proof_scope"] = "Creation PNG dimensions+SHA, full frame trace, raw1080creation command and exact encoded-video-payload link to deliveredMP4. Video dimensions alone were not used as proof of native rendering."
        return transitions

    def capture_plan(self, transitions):
        reasons = {}

        def add(frame, why):
            frame = int(frame)
            if 0 <= frame < self.frames:
                reasons.setdefault(frame, []).append(why)

        for sec in MANDATORY_SECONDS:
            add(sec * 30, {"kind": "DOCX_mandatory", "seconds": sec})
        shots_path = ROOT / "guion_fuente/SHOTLIST_R12_DERIVADO_DEL_DOCX.json"
        schedule_path = ROOT / "audio/TIEMPOS_ANCLAS_R12.json"
        scenes = load(shots_path)["scenes"]
        literal = load(shots_path)
        actual = load(schedule_path)
        schedule = actual["rows"]
        self.check("R12_derived_contract_14scenes_42shots", len(scenes)==14 and sum(len(s["shots"]) for s in scenes)==42 and literal.get("not_original_specification") is True, "14/42 explicit DOCX-derived contract", [len(scenes),sum(len(s["shots"]) for s in scenes),literal.get("not_original_specification")])
        self.check("R12_actual_schedule_42_all_fit", len(schedule)==42 and actual.get("all_fit") is True and not actual.get("violations"), "42 fitted voice anchors", [len(schedule),actual.get("all_fit"),actual.get("violations")])
        self.report["capture_schedule_sources"] = [{"path": str(p), "sha256": sha(p)} for p in [shots_path, schedule_path]]
        for scene in scenes:
            for boundary in [scene["start_s"], scene["end_s"]]:
                frame = round(boundary * 30)
                for delta in [-1, 0, 1]:
                    add(frame + delta, {"kind": "scene_boundary", "scene": scene["scene_id"], "boundary_s": boundary, "delta_frames": delta})
        for shot in schedule:
            frame = shot["first_visual_frame_30fps"]
            for delta in [-1, 0, 1]:
                add(frame + delta, {"kind": "actual_voice_shot_boundary", "shot": shot["shot_id"], "delta_frames": delta})
        for shot in schedule:
            a,b=shot["first_visual_frame_30fps"],shot["end_visual_frame_exclusive_30fps"]
            add((a+b-1)//2, {"kind": "actual_shot_midpoint_sample_NOT_physical_event", "shot": shot["shot_id"]})
        for row in transitions or []:
            # Every first rendered state is captured, including every first
            # qualified reader display. No Native tick is converted to seconds.
            for delta in [-1, 0, 1]:
                add(row["frame"] + delta, dict(kind="render_state_or_reader_transition", delta_frames=delta, **row))
        add(0, {"kind": "first_frame"})
        add(self.frames - 1, {"kind": "last_frame"})
        plan = [{"frame": frame, "presentation_seconds": str(Fraction(frame, 30)), "reasons": reasons[frame]}
                for frame in sorted(reasons)]
        self.report["capture_plan"] = plan
        self.report["reader_capture_method"] = "Capture every first rendered raster/source-data state and its neighbouringframes, plus every actual shot boundary. Thus retained reader-display transitions are included as a superset; these are montage frame indices, not guessed conversions of Native ticks."
        save_new(self.folder / "capture_plan.json", plan)
        return plan

    def decode_and_capture(self, plan):
        expression = "+".join("eq(n\\,%d)" % row["frame"] for row in plan)
        graph = "[0:v:0]split=2[vall][vsel];[vsel]select=" + expression + ",split=2[v1080][vm];[vm]format=rgb24,scale=360:-1:flags=lanczos[v360]"
        graph_path = self.folder / "decode_capture.ffgraph"
        with graph_path.open("x", encoding="utf-8") as handle:
            handle.write(graph + "\n")
        self.report["capture_filter"] = {"path": str(graph_path), "sha256": sha(graph_path)}
        output = self.command("05_strict_full_decode_and_captures", [FF,
            "-nostdin", "-hide_banner", "-v", "error", "-xerror", "-err_detect", "explode", "-nostats", "-n",
            "-threads", "2", "-i", self.video, "-filter_complex_threads", "1", "-filter_complex_script", graph_path, "-progress", "pipe:1",
            "-map", "[vall]", "-map", "0:a:0", "-c:v", "wrapped_avframe", "-fps_mode", "passthrough", "-f", "null", "-",
            "-map", "[v1080]", "-an", "-c:v", "png", "-pix_fmt", "rgb24", "-threads", "1", "-fps_mode", "passthrough", "-start_number", "0", self.captures / "1080_%05d.png",
            "-map", "[v360]", "-an", "-c:v", "png", "-pix_fmt", "rgb24", "-threads", "1", "-fps_mode", "passthrough", "-start_number", "0", self.captures / "360_%05d.png"], timeout=self.args.timeout)
        progress = output.read_text(encoding="utf-8", errors="replace")
        frames = re.findall(r"(?m)^frame=\s*(\d+)\s*$", progress)
        decoded = int(frames[-1]) if frames else None
        stderr = self.folder / "05_strict_full_decode_and_captures.stderr"
        self.check("strict_full_decode_reached_end", "progress=end" in progress, True, "progress=end" in progress)
        self.check("actual_decoded_video_frame_count", decoded == self.frames, self.frames, decoded)
        self.check("strict_full_decode_error_output_empty", not stderr.read_bytes().strip(), 0, stderr.stat().st_size)
        self.report["full_decode_scope"] = "Every video frame and the complete mapped audio stream decoded once with-xerror/-err_detect explode. The same decode produces the selected PNGs; no auditory evaluation or native reproduction is implied."
        full = sorted(self.captures.glob("1080_*.png"))
        mobile = sorted(self.captures.glob("360_*.png"))
        self.check("capture_counts", len(full) == len(mobile) == len(plan), [len(plan), len(plan)], [len(full), len(mobile)])
        rows = []
        for index, (a, b) in enumerate(zip(full, mobile)):
            ai, bi = png_info(a), png_info(b)
            row = {"index": index, **plan[index], "1080": dict(ai, path=str(a)), "360": dict(bi, path=str(b))}
            rows.append(row)
        bad = [x["index"] for x in rows if [x["1080"]["width"], x["1080"]["height"]] != [1920, 1080] or x["360"]["width"] != 360]
        self.check("capture_native_and_mobile_dimensions", not bad and len(rows) == len(plan), "1920x1080and360pxwide, no zoom for mobile preview", bad)
        self.report["decoded_captures"] = rows
        save_new(self.folder / "decoded_captures.json", rows)

    def run(self):
        began = time.monotonic()
        self.phase("metadata", self.metadata)
        if hasattr(self, "v"):
            self.phase("all_packet_timestamps", self.packets)
        transitions = self.phase("native_creation_sources", self.native_sources)
        plan = self.phase("capture_plan", lambda: self.capture_plan(transitions))
        if plan:
            self.phase("strict_decode_and_samples", lambda: self.decode_and_capture(plan))
        try:
            final_signature = self.signature(self.video)
            self.check("delivered_file_unchanged_during_verification", final_signature == self.initial_signature,
                       self.initial_signature, final_signature)
        except OSError as exc:
            self.report["errors"].append({"phase": "final_file_signature", "exception": type(exc).__name__, "message": str(exc)})
        self.report["host_seconds"] = round(time.monotonic() - began, 6)
        self.report["failed_checks"] = [c for c in self.report["checks"] if not c["ok"]]
        self.report["ok"] = not self.report["errors"] and not self.report["failed_checks"]
        self.report["status"] = "technical_scope_verified_visual_samples_require_review" if self.report["ok"] else "verification_failed"
        target = self.args.report
        target.parent.mkdir(parents=True, exist_ok=True)
        save_new(target, self.report)
        print(json.dumps({"ok": self.report["ok"], "status": self.report["status"], "report": str(target), "report_sha256": sha(target),
            "checks": len(self.report["checks"]), "failed_checks": self.report["failed_checks"], "errors": self.report["errors"],
            "decoded_capture_count": len(self.report.get("decoded_captures", [])), "expected_frames": self.frames,
            "new_DEE_ticks": 0, "auditory_review": False, "full_motion_visual_review": False}, ensure_ascii=False))
        return 0 if self.report["ok"] else 1


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("video", type=Path, help="Closed final MP4; never modified")
    parser.add_argument("--report", type=Path, required=True, help="New report path inside AUDIOVISUAL_R12")
    parser.add_argument("--prefix", help="Unique output-directory name; never overwrites an earlier run")
    parser.add_argument("--render-proof", type=Path, help="Optional explicit RENDER_Rxx.json; still must match encoded video payload")
    parser.add_argument("--timeout", type=int, default=900)
    args = parser.parse_args()
    if not 1 <= args.timeout <= 3600:
        parser.error("--timeout must be in1..3600seconds")
    try:
        return Verification(args).run()
    except (FileNotFoundError, FileExistsError, ValueError) as exc:
        print(json.dumps({"ok": False, "status": "inputs_or_prefix_not_ready", "exception": type(exc).__name__, "message": str(exc), "new_DEE_ticks": 0}, ensure_ascii=False))
        return 2


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(json.dumps({"ok": False, "status": "unexpected_internal_error", "exception": type(exc).__name__, "message": str(exc), "new_DEE_ticks": 0}, ensure_ascii=False))
        raise SystemExit(3)
