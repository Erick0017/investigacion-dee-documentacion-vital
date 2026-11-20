"""Read-only R05 MP4 checks; emit one detailed JSON object to stdout.

No DEE or scene imports. No video decoding, media writes or production-register
edits. The two complete audio streams are decoded solely to compare their PCM
sample SHA256. ffprobe nb_frames is container evidence, not a fresh video count.
Run only after both final exports have finished and root gives the signal.

The literal DOCX does not require ffprobe default0 for subtitle tracks. In MP4,
FFmpeg maps the tkhd enabled flag to that disposition. Apple requires one
enabled alternate subtitle even when display is off. Record actual flags;
require forced0 and exact extraction, without claiming a universal player state.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import re
import struct
import subprocess
import sys
import time


ROOT = Path(__file__).resolve().parents[1]
PREFIX = "DEE_Cognitive_2_0_R05_Mundo_y_Capacidades_1080p"
TESTS = next((p for p in ROOT.parents if (p / "_dee20_trabajo").is_dir()), None)
TOOL_BASE = TESTS / "_dee20_trabajo" if TESTS else None
DEFAULT_FFMPEG = TOOL_BASE / "presentacion_clara/herramientas/ffmpeg.exe" if TOOL_BASE else None
DEFAULT_FFPROBE = TOOL_BASE / "video_publico_definitivo/herramientas/ffprobe.exe" if TOOL_BASE else None


class ToolFailure(RuntimeError):
    def __init__(self, details):
        super().__init__(details.get("message", "External tool failed"))
        self.details = details


def sha_file(path):
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def signature(path):
    stat = path.stat()
    return {"bytes": stat.st_size, "mtime_ns": stat.st_mtime_ns}


def command(argv, timeout):
    """Capture child diagnostics; never send tool chatter to JSON stdout."""
    argv = [str(v) for v in argv]
    began = time.monotonic()
    try:
        proc = subprocess.run(
            argv, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
            stderr=subprocess.PIPE, timeout=timeout, check=False,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )
    except subprocess.TimeoutExpired as exc:
        raise ToolFailure({"command": argv, "message": "Tool timeout", "timeout_seconds": timeout,
                           "stderr_tail": (exc.stderr or b"").decode("utf-8", "replace")[-4096:]}) from exc
    except OSError as exc:
        raise ToolFailure({"command": argv, "message": str(exc), "exception": type(exc).__name__}) from exc
    details = {"command": argv, "returncode": proc.returncode,
               "host_seconds": round(time.monotonic() - began, 6),
               "stderr_tail": proc.stderr.decode("utf-8", "replace")[-4096:]}
    if proc.returncode:
        raise ToolFailure(dict(details, message="External tool returned nonzero"))
    return proc.stdout, details


def probe(path, ffprobe, timeout):
    raw, evidence = command([ffprobe, "-v", "error", "-show_streams", "-show_format", "-of", "json", path], timeout)
    try:
        data = json.loads(raw)
    except (ValueError, UnicodeDecodeError) as exc:
        raise ToolFailure(dict(evidence, message="ffprobe output is not valid JSON")) from exc
    return data, evidence


def top_level_boxes(path):
    """Read only ISO-BMFF top-level headers, including extended and zero sizes."""
    size = path.stat().st_size
    rows = []
    offset = 0
    with path.open("rb") as handle:
        while offset < size:
            if len(rows) >= 100000:
                raise ValueError("Too many top-level MP4 boxes")
            if size - offset < 8:
                raise ValueError(f"Incomplete top-level box header at byte{offset}")
            handle.seek(offset)
            raw = handle.read(8)
            box_size, kind = struct.unpack(">I4s", raw)
            header = 8
            if box_size == 1:
                raw = handle.read(8)
                if len(raw) != 8:
                    raise ValueError(f"Incomplete extended-size box at byte{offset}")
                box_size = struct.unpack(">Q", raw)[0]
                header = 16
            elif box_size == 0:
                box_size = size - offset
            if box_size < header or offset + box_size > size:
                raise ValueError(f"Invalid box bounds at byte{offset}: size={box_size}, file={size}")
            rows.append({"type": kind.decode("ascii", "replace"), "offset": offset,
                         "size": box_size, "header_bytes": header})
            offset += box_size
    return rows


def track_header_flags(path, top_boxes):
    """Record actual tkhd bits/track IDs/handler types; never change them."""
    moovs = [b for b in top_boxes if b["type"] == "moov"]
    if len(moovs) != 1:
        return []

    def children(handle, start, end):
        rows = []
        offset = start
        while offset < end:
            if end - offset < 8:
                raise ValueError(f"Incomplete nested MP4 header at byte{offset}")
            handle.seek(offset)
            box_size, kind = struct.unpack(">I4s", handle.read(8))
            header = 8
            if box_size == 1:
                raw = handle.read(8)
                if len(raw) != 8:
                    raise ValueError(f"Incomplete extended nested header at byte{offset}")
                box_size = struct.unpack(">Q", raw)[0]
                header = 16
            elif box_size == 0:
                box_size = end - offset
            if box_size < header or offset + box_size > end:
                raise ValueError(f"Invalid nested MP4 box bounds at byte{offset}")
            rows.append({"type": kind.decode("ascii", "replace"), "offset": offset,
                         "size": box_size, "header_bytes": header})
            offset += box_size
        return rows

    def inner(handle, box):
        return children(handle, box["offset"] + box["header_bytes"], box["offset"] + box["size"])

    result = []
    with path.open("rb") as handle:
        for track in [b for b in inner(handle, moovs[0]) if b["type"] == "trak"]:
            fields = inner(handle, track)
            tkhd = [b for b in fields if b["type"] == "tkhd"]
            mdia = [b for b in fields if b["type"] == "mdia"]
            if len(tkhd) != 1 or len(mdia) != 1:
                raise ValueError("Expected exactly one tkhd and mdia per track")
            header = tkhd[0]
            payload = header["offset"] + header["header_bytes"]
            handle.seek(payload)
            fullbox = handle.read(4)
            if len(fullbox) != 4 or fullbox[0] not in (0, 1):
                raise ValueError("Invalid or unsupported tkhd FullBox version")
            version = fullbox[0]
            flags = int.from_bytes(fullbox[1:4], "big")
            handle.seek(payload + (20 if version == 1 else 12))
            track_id = struct.unpack(">I", handle.read(4))[0]
            handlers = [b for b in inner(handle, mdia[0]) if b["type"] == "hdlr"]
            if len(handlers) != 1:
                raise ValueError("Expected exactly one mdia/hdlr per track")
            hdlr = handlers[0]
            handle.seek(hdlr["offset"] + hdlr["header_bytes"] + 8)
            handler_type = handle.read(4).decode("ascii", "replace")
            result.append({"track_id": track_id, "handler_type": handler_type,
                           "tkhd_offset": header["offset"], "tkhd_version": version,
                           "flags_24bit_hex": f"0x{flags:06x}",
                           "track_enabled_bit0": bool(flags & 1),
                           "track_in_movie_bit1": bool(flags & 2),
                           "track_in_preview_bit2": bool(flags & 4)})
    return result


def srt_ms(value):
    match = re.fullmatch(r"(\d+):(\d{2}):(\d{2}),(\d{3})", value.strip())
    if not match:
        raise ValueError("Invalid SRT timestamp: " + value)
    hours, minutes, seconds, millis = map(int, match.groups())
    if minutes >= 60 or seconds >= 60:
        raise ValueError("Invalid SRT minute/second range: " + value)
    return ((hours * 60 + minutes) * 60 + seconds) * 1000 + millis


def parse_srt(raw):
    text = raw.decode("utf-8-sig").replace("\r\n", "\n").replace("\r", "\n")
    result = []
    if not text.strip():
        raise ValueError("Empty subtitle extraction")
    for block in re.split(r"\n\s*\n", text.strip()):
        lines = block.splitlines()
        where = next((i for i, line in enumerate(lines) if "-->" in line), None)
        if where is None:
            raise ValueError("SRT block has no timestamp: " + block[:120])
        stamps = lines[where].split("-->")
        if len(stamps) != 2:
            raise ValueError("Malformed SRT timestamp pair")
        start, end = map(srt_ms, stamps)
        body = lines[where + 1:]
        if not body or not start < end:
            raise ValueError("Empty or nonpositive SRT cue")
        if result and start < result[-1]["end_ms"]:
            raise ValueError("Overlapping SRT cues")
        result.append({"start_ms": start, "end_ms": end,
                       "text": " ".join(" ".join(body).split()), "lines": body})
    return result


def subtitle_roundtrip(clean, stream, external, ffmpeg, timeout):
    raw, execution = command([
        ffmpeg, "-nostdin", "-hide_banner", "-v", "error", "-i", clean,
        "-map", "0:" + str(stream["index"]), "-vn", "-an", "-dn",
        "-c:s", "srt", "-f", "srt", "pipe:1",
    ], timeout)
    wanted = parse_srt(external.read_bytes())
    found = parse_srt(raw)
    differences = []
    for index, (a, b) in enumerate(zip(wanted, found), 1):
        if a["text"] != b["text"] or a["start_ms"] != b["start_ms"] or a["end_ms"] != b["end_ms"]:
            differences.append({"cue": index, "expected": a, "extracted": b,
                                "start_delta_ms": b["start_ms"] - a["start_ms"],
                                "end_delta_ms": b["end_ms"] - a["end_ms"]})
    if len(wanted) != len(found):
        differences.append({"kind": "cue_count", "expected": len(wanted), "extracted": len(found)})
    return {
        "ok": not differences, "external_path": str(external), "external_sha256": sha_file(external),
        "stream_index": stream["index"], "language": stream.get("tags", {}).get("language"),
        "expected_cues": len(wanted), "extracted_cues": len(found),
        "comparison": "Exact cue order, text after whitespace/linebreak normalization, and integer-millisecond starts/ends; tolerance0ms.",
        "linebreaks_equal": len(wanted) == len(found) and all(a["lines"] == b["lines"] for a, b in zip(wanted, found)),
        "differences": differences, "extracted_SRT_SHA256": hashlib.sha256(raw).hexdigest(),
        "execution": execution,
    }


def audio_sample_hash(path, ffmpeg, timeout):
    # hash muxer hashes PCM packet payloads, with no WAV/container header. AAC's
    # native float samples are kept as interleaved f32le. No resample/trim/filter.
    raw, execution = command([
        ffmpeg, "-nostdin", "-hide_banner", "-v", "error", "-i", path,
        "-map", "0:a:0", "-vn", "-sn", "-dn", "-c:a", "pcm_f32le",
        "-f", "hash", "-hash", "sha256", "pipe:1",
    ], timeout)
    match = re.fullmatch(rb"\s*SHA256=([0-9a-fA-F]{64})\s*", raw)
    if not match:
        raise ToolFailure(dict(execution, message="Unexpected decoded-audio hash output",
                               output_preview=raw.decode("utf-8", "replace")[:300]))
    return {"sha256_decoded_samples": match.group(1).decode("ascii").lower(),
            "representation": "interleaved pcm_f32le from the whole AAC stream; no header, resampling, gain, trimming or duration cap",
            "execution": execution}


def inspect_file(name, path, ffprobe, timeout, checks):
    data, execution = probe(path, ffprobe, timeout)
    streams = data.get("streams", [])
    video = [s for s in streams if s.get("codec_type") == "video"]
    audio = [s for s in streams if s.get("codec_type") == "audio"]
    subtitles = [s for s in streams if s.get("codec_type") == "subtitle"]

    def check(key, actual, expected):
        checks.append({"file": name, "check": key, "ok": actual == expected,
                       "expected": expected, "actual": actual})

    check("video_stream_count", len(video), 1)
    check("audio_stream_count", len(audio), 1)
    check("subtitle_stream_count", len(subtitles), 2 if name == "clean" else 0)
    check("total_stream_count", len(streams), 4 if name == "clean" else 2)
    if len(video) == 1:
        v = video[0]
        for key, expected in [("codec_name", "h264"), ("width", 1920), ("height", 1080),
                              ("pix_fmt", "yuv420p"), ("nb_frames", "10800")]:
            check("video_" + key, v.get(key), expected)
        for key in ["avg_frame_rate", "r_frame_rate"]:
            try:
                rate = str(Fraction(v.get(key, "0/1")))
            except (ValueError, ZeroDivisionError):
                rate = "invalid:" + str(v.get(key))
            check("video_" + key, rate, "30")
        try:
            duration = Fraction(v.get("duration", "-1"))
            duration_ok = abs(duration - 360) <= Fraction(1, 1000000)
        except (ValueError, ZeroDivisionError):
            duration_ok = False
        check("video_duration360_tolerance1microsecond", duration_ok, True)
    if len(audio) == 1:
        a = audio[0]
        for key, expected in [("codec_name", "aac"), ("sample_rate", "48000"),
                              ("channels", 2), ("channel_layout", "stereo")]:
            check("audio_" + key, a.get(key), expected)
        check("audio_language", a.get("tags", {}).get("language"), "spa")
        try:
            duration_ok = abs(Fraction(a.get("duration", "-1")) - 360) <= Fraction(1, 48000)
        except (ValueError, ZeroDivisionError):
            duration_ok = False
        check("audio_duration360_tolerance1sample", duration_ok, True)
    try:
        format_duration_ok = abs(Fraction(data.get("format", {}).get("duration", "-1")) - 360) <= Fraction(1, 1000000)
    except (ValueError, ZeroDivisionError):
        format_duration_ok = False
    check("container_duration360_tolerance1microsecond", format_duration_ok, True)
    if name == "clean":
        check("subtitle_languages", sorted(s.get("tags", {}).get("language", "") for s in subtitles), ["eng", "spa"])
        for s in subtitles:
            lang = s.get("tags", {}).get("language", "unknown")
            check("subtitle_" + lang + "_codec", s.get("codec_name"), "mov_text")
            check("subtitle_" + lang + "_forced", s.get("disposition", {}).get("forced"), 0)
    boxes = top_level_boxes(path)
    moov = [b for b in boxes if b["type"] == "moov"]
    mdat = [b for b in boxes if b["type"] == "mdat"]
    check("one_top_level_moov", len(moov), 1)
    check("has_top_level_mdat", bool(mdat), True)
    faststart = len(moov) == 1 and bool(mdat) and moov[0]["offset"] + moov[0]["size"] <= min(b["offset"] for b in mdat)
    check("faststart_complete_moov_before_first_mdat", bool(faststart), True)
    return {"path": str(path), "probe": data, "probe_execution": execution,
            "frame_count_evidence": "MP4 ffprobe nb_frames; no -count_frames and no video decoder run",
            "top_level_boxes": boxes, "faststart": bool(faststart),
            "track_headers": track_header_flags(path, boxes),
            "subtitle_dispositions_observed": [
                {"stream_index": s["index"], "track_id": s.get("id"),
                 "language": s.get("tags", {}).get("language"),
                 "disposition": s.get("disposition", {})} for s in subtitles
            ]}, subtitles


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--primary", type=Path, default=ROOT / (PREFIX + "_EN.mp4"))
    parser.add_argument("--clean", type=Path, default=ROOT / (PREFIX + "_LIMPIO.mp4"))
    parser.add_argument("--srt-en", type=Path, default=ROOT / "R05_EN.srt")
    parser.add_argument("--srt-es", type=Path, default=ROOT / "R05_ES.srt")
    parser.add_argument("--ffmpeg", type=Path, default=DEFAULT_FFMPEG)
    parser.add_argument("--ffprobe", type=Path, default=DEFAULT_FFPROBE)
    parser.add_argument("--timeout", type=int, default=180)
    parser.add_argument("--describe", action="store_true", help="Describe checks; do not open media or launch tools")
    args = parser.parse_args(argv)
    if args.describe:
        print(json.dumps({"mode": "description_only", "inputs": {k: str(getattr(args, k)) for k in ["primary", "clean", "srt_en", "srt_es", "ffmpeg", "ffprobe"]},
                          "scope": __doc__, "subtitle_time_tolerance_ms": 0,
                          "subtitle_default0_requirement": False,
                          "exit_codes": {"0": "all individual checks passed", "1": "verification mismatch or tool failure", "2": "missing/invalid inputs", "3": "unexpected internal error"}}, ensure_ascii=False))
        return 0
    if not 1 <= args.timeout <= 900:
        parser.error("--timeout must be in1..900 seconds")
    started = time.monotonic()
    report = {"schema": "DEE.video.R05.final_mp4_scope_checks.v1", "started_utc": datetime.now(timezone.utc).isoformat(),
              "ok": False, "new_DEE_ticks": 0, "video_full_decode_repeated": False,
              "scope": "ffprobe/container, MP4 faststart, clean subtitle metadata and SRT roundtrip, identical decoded audio samples; no visual or auditory semantic verdict",
              "files": {}, "checks": [], "errors": []}
    report["subtitle_policy"] = {
        "required": "Exactly two mov_text tracks, eng and spa, forced0, both exactly extractable against the external SRTs",
        "default0_required": False,
        "off_by_default_validated": False,
        "rationale": "The literal DOCX requires a clean selectable-subtitle copy, not ffprobe default0. FFmpeg maps tkhd enabled to default. Apple alternate-subtitle guidance requires one enabled track even when subtitle display is off. Actual default/tkhd bits are recorded, without modifying the compatible standard mux or asserting a universal player display preference.",
        "primary_sources": [
            "https://github.com/FFmpeg/FFmpeg/blob/n7.1/libavformat/movenc.c#L6856-L6903",
            "https://github.com/FFmpeg/FFmpeg/blob/n7.1/libavformat/mov.c#L5032-L5034",
            "https://developer.apple.com/documentation/quicktime-file-format/preparing_sound_and_subtitle_alternate_groups_for_use_with_apple_devices",
        ],
    }
    paths = {k: getattr(args, k).resolve() if getattr(args, k) is not None else None
             for k in ["primary", "clean", "srt_en", "srt_es", "ffmpeg", "ffprobe"]}
    missing = {k: str(p) if p else None for k, p in paths.items() if p is None or not p.is_file()}
    if missing:
        report.update(status="inputs_not_ready", missing_inputs=missing)
        print(json.dumps(report, ensure_ascii=False))
        return 2
    if paths["primary"] == paths["clean"]:
        report.update(status="invalid_inputs", errors=[{"message": "Primary and clean must be distinct files"}])
        print(json.dumps(report, ensure_ascii=False))
        return 2
    initial = {name: signature(paths[name]) for name in ["primary", "clean", "srt_en", "srt_es"]}
    report["tools"] = {name: {"path": str(paths[name]), "sha256": sha_file(paths[name])} for name in ["ffmpeg", "ffprobe"]}
    subtitle_streams = []
    for name in ["primary", "clean"]:
        try:
            info, substreams = inspect_file(name, paths[name], paths["ffprobe"], args.timeout, report["checks"])
            info["bytes"] = paths[name].stat().st_size
            info["sha256"] = sha_file(paths[name])
            report["files"][name] = info
            if name == "clean":
                subtitle_streams = substreams
        except ToolFailure as exc:
            report["errors"].append(dict(exc.details, phase="inspect_" + name))
        except (ValueError, OSError) as exc:
            report["errors"].append({"phase": "inspect_" + name, "message": str(exc), "exception": type(exc).__name__})
    report["subtitle_roundtrip"] = {}
    for language, input_name in [("eng", "srt_en"), ("spa", "srt_es")]:
        matches = [s for s in subtitle_streams if s.get("tags", {}).get("language") == language]
        if len(matches) != 1:
            report["errors"].append({"phase": "subtitle_roundtrip_" + language, "message": "Need exactly one matching language track", "count": len(matches)})
            continue
        try:
            result = subtitle_roundtrip(paths["clean"], matches[0], paths[input_name], paths["ffmpeg"], args.timeout)
            report["subtitle_roundtrip"][language] = result
            report["checks"].append({"check": "subtitle_roundtrip_" + language, "ok": result["ok"], "expected": "all ordered cues exact text and millisecond timing", "actual": {"expected_cues": result["expected_cues"], "extracted_cues": result["extracted_cues"], "differences": len(result["differences"])}})
        except ToolFailure as exc:
            report["errors"].append(dict(exc.details, phase="subtitle_roundtrip_" + language))
        except (ValueError, OSError, UnicodeDecodeError) as exc:
            report["errors"].append({"phase": "subtitle_roundtrip_" + language, "message": str(exc), "exception": type(exc).__name__})
    report["decoded_audio"] = {}
    for name in ["primary", "clean"]:
        try:
            report["decoded_audio"][name] = audio_sample_hash(paths[name], paths["ffmpeg"], args.timeout)
        except ToolFailure as exc:
            report["errors"].append(dict(exc.details, phase="audio_sample_hash_" + name))
    hashes = report["decoded_audio"]
    same = len(hashes) == 2 and hashes["primary"]["sha256_decoded_samples"] == hashes["clean"]["sha256_decoded_samples"]
    report["checks"].append({"check": "decoded_PCM_sample_SHA256_identical", "ok": bool(same), "expected": "two successfully decoded streams with identical PCM sample SHA256", "actual": {k: v["sha256_decoded_samples"] for k, v in hashes.items()}})
    for name, before in initial.items():
        try:
            after = signature(paths[name])
            report["checks"].append({"check": name + "_unchanged_during_verification", "ok": before == after, "expected": before, "actual": after})
        except OSError as exc:
            report["errors"].append({"phase": "final_input_signature", "file": name, "message": str(exc)})
    report["host_seconds"] = round(time.monotonic() - started, 6)
    report["ok"] = not report["errors"] and bool(report["checks"]) and all(row["ok"] for row in report["checks"])
    report["status"] = "verified_within_declared_scope" if report["ok"] else "verification_failed"
    report["failed_checks"] = [row for row in report["checks"] if not row["ok"]]
    print(json.dumps(report, ensure_ascii=False, allow_nan=False))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(json.dumps({"schema": "DEE.video.R05.final_mp4_scope_checks.v1", "ok": False,
                          "status": "unexpected_internal_error", "exception": type(exc).__name__,
                          "message": str(exc), "new_DEE_ticks": 0}, ensure_ascii=False))
        raise SystemExit(3)
