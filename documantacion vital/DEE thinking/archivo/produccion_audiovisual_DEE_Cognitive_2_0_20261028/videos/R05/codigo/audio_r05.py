"""Local R05 em_alex narration, literal bilingual captions and 360-second mix.

Uses the approved R04/R03 model and runner read-only. Does not write the root's
REGISTRO_PRODUCCION_R05.json. Technical asset provenance is an importable Python
object in audio/provenance_r05.py; no extra administrative JSON is produced.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import pprint
import re
import subprocess
import sys
import tempfile
import textwrap
import time
import wave
import xml.etree.ElementTree as ET
import zipfile

R05 = Path(__file__).resolve().parents[1]
VIDEOS = R05.parent
R03 = VIDEOS / "produccion_cientifica/R03"
VOICE_SOURCE = VIDEOS / "produccion_cientifica/voz"
TTS_SCRIPT = R03 / "sintetizar_voz_r03.py"
PROMPT = Path(r"C:\Users\Erik\.codex\codex-remote-attachments\01a0921e-4727-7f93-8ad0-0b605c9afe96\C362B742-5108-465C-AEE3-EF62F1A50C55\1-PROMPT_CODEX_DEE_VIDEO_R05_MUNDO_3D_Y_CAPACIDADES.docx")
PROVENANCE = R05 / "audio/provenance_r05.py"
TESTS = next(p for p in R05.parents if p.name == "tests")
FF = TESTS / "_dee20_trabajo/presentacion_clara/herramientas/ffmpeg.exe"
MUSIC = R03 / "voz/ambiente_R03.wav"
ALIAS = Path(tempfile.gettempdir()) / "dee_r03_voice_312cdd7b"


def install_write_boundary():
    """Keep all Python-mediated writes inside this new production directory."""
    allowed = R05.resolve()
    def check(path):
        if isinstance(path, (str, bytes, os.PathLike)):
            resolved = Path(os.fsdecode(path)).resolve()
            if not resolved.is_relative_to(allowed):
                raise PermissionError("R05 writes cannot leave the new directory: " + str(resolved))
    def audit(event, args):
        if event == "open":
            path, mode, flags = args
            write = (isinstance(mode, str) and any(c in mode for c in "wax+"))
            write = write or bool(flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC | os.O_APPEND))
            if write:
                check(path)
        elif event in ("os.mkdir", "os.remove", "os.rmdir"):
            check(args[0])
        elif event in ("os.rename", "os.replace"):
            check(args[0]); check(args[1])
        elif event == "socket.connect":
            raise PermissionError("R05 audio is offline; network connections are not permitted")
    sys.addaudithook(audit)


def sha(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(4 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def read_provenance():
    if not PROVENANCE.exists():
        return {"attempts": [], "selected": {}}
    spec = importlib.util.spec_from_file_location("_r05_provenance_only", PROVENANCE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.PROVENANCE


def save_provenance(value):
    PROVENANCE.parent.mkdir(parents=True, exist_ok=True)
    temporary = PROVENANCE.with_suffix(".pending.py")
    temporary.write_text("# Technical audio asset provenance; root owns the production register.\nPROVENANCE = "
                         + pprint.pformat(value, width=120, sort_dicts=False) + "\n", encoding="utf8")
    temporary.replace(PROVENANCE)


def literal_scenes():
    with zipfile.ZipFile(PROMPT) as archive:
        root = ET.fromstring(archive.read("word/document.xml"))
    ns = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
    paras = ["".join(p.itertext()) for p in root.findall("./w:body/w:p", ns)]
    scenes = []
    for i, text in enumerate(paras):
        match = re.match(r"^(S\d{2})\s*\|\s*(\d\d):(\d\d)[–-](\d\d):(\d\d)\s*\|", text)
        if not match:
            continue
        identifier, a, b, c, d = match.groups()
        assert paras[i + 2] == "Locución literal en español"
        assert paras[i + 4] == "Traducción inglesa para subtitular"
        scenes.append({"id": identifier, "title": paras[i + 1], "start": int(a) * 60 + int(b),
                       "end": int(c) * 60 + int(d), "es": paras[i + 3], "en": paras[i + 5]})
    assert [x["id"] for x in scenes] == [f"S{i:02d}" for i in range(1, 16)]
    assert scenes[0]["start"] == 0 and scenes[-1]["end"] == 360
    assert all(a["end"] == b["start"] for a, b in zip(scenes, scenes[1:]))
    assert all(" ".join(x[lang].split()) == x[lang] for x in scenes for lang in ("es", "en"))
    return scenes


def runtime_alias_readonly():
    if not ALIAS.is_junction() or ALIAS.resolve() != VOICE_SOURCE.resolve():
        raise RuntimeError("The approved pre-existing runtime alias is absent or has another target; no link is created")
    return ALIAS


def setup():
    # Preserve the exact already-authorized short alias before moving TEMP.
    runtime_alias_readonly()
    temp = R05 / "audio/tmp"
    temp.mkdir(parents=True, exist_ok=True)
    for key in ("TMP", "TEMP", "TMPDIR"):
        os.environ[key] = str(temp)
    tempfile.tempdir = str(temp)
    os.environ.update(HF_HUB_OFFLINE="1", TRANSFORMERS_OFFLINE="1", DO_NOT_TRACK="1")
    sys.dont_write_bytecode = True
    spec = importlib.util.spec_from_file_location("_r05_approved_tts_runner", TTS_SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.W = R05
    module.OUT = R05 / "audio/tomas"
    module.runtime_alias = runtime_alias_readonly
    module.OUT.mkdir(parents=True, exist_ok=True)
    np, sf, synth, assets, runner, alias = module.setup()
    assert module.PARAMS["voice"] == "em_alex" and module.PARAMS["language"] == "es-419"
    return module, np, sf, synth, assets, runner


def synthesize(ids, initial_speed, auto_fit):
    scenes = literal_scenes()
    selected_scenes = [s for s in scenes if not ids or s["id"] in ids]
    if ids and set(ids) != {s["id"] for s in selected_scenes}:
        raise ValueError("Unknown scene ID")
    module, np, sf, synth, assets, runner = setup()
    baseline = deepcopy(module.PARAMS)
    provenance = read_provenance()
    provenance.update({"prompt": str(PROMPT), "prompt_sha256": sha(PROMPT), "literal_scenes": scenes,
                       "approved_voice": baseline, "approved_runner": str(TTS_SCRIPT),
                       "approved_runner_sha256": sha(TTS_SCRIPT), "assets": assets, "runner_files": runner,
                       "model_execution": "Local CPUExecutionProvider only; no uploads or installations",
                       "existing_alias_read_only": str(ALIAS), "new_DEE_ticks": 0,
                       "no_time_stretch": True, "no_phoneme_trim": True,
                       "human_auditory_review": "Not performed; technical metrics are not listening"})
    existing = {row["id"]: row for row in provenance.get("attempts", [])}
    for scene in selected_scenes:
        prior_id = provenance["selected"].get(scene["id"])
        if prior_id and existing[prior_id]["fit_margin_seconds"] >= 0:
            assert sha(R05 / existing[prior_id]["file"]) == existing[prior_id]["wav_sha256"]
            print("SELECTED_CACHE_VERIFIED", scene["id"], prior_id, flush=True)
            continue
        speed = initial_speed
        for attempt in range(6):
            identifier = scene["id"] + "_rate" + f"{speed:.3f}".replace(".", "")
            module.PARAMS = deepcopy(baseline)
            module.PARAMS["speed"] = speed
            request = {"id": identifier, "es": scene["es"], "en": scene["en"]}
            row = module.synthesize(request, np, sf, synth, assets, runner, existing)
            row["scene_id"] = scene["id"]
            row["scene_window"] = [scene["start"], scene["end"]]
            row["fit_margin_seconds"] = scene["end"] - scene["start"] - row["duration"]
            existing[identifier] = row
            provenance["attempts"] = list(existing.values())
            # Each take already contains 0.60s trailing silence and the next
            # has 0.35s leading silence. Exact sample-domain window fit is the
            # required boundary; an extra arbitrary margin is unnecessary.
            fit = row["fit_margin_seconds"] >= 0
            if fit:
                provenance["selected"][scene["id"]] = identifier
            save_provenance(provenance)
            print("VOICE", json.dumps({"scene": scene["id"], "speed": speed, "seconds": row["duration"],
                                       "window": scene["end"] - scene["start"], "fit": fit,
                                       "margin": row["fit_margin_seconds"], "host_seconds": row["host_seconds"],
                                       "WPM": row["spoken_words_per_minute"]}), flush=True)
            if fit or not auto_fit:
                break
            available_speech = scene["end"] - scene["start"] - baseline["leading_silence_seconds"] - baseline["trailing_silence_seconds"] - .30
            speed = round(speed * row["speech_block_seconds"] / available_speech * 1.012, 3)
            if speed > 1.35:
                raise RuntimeError("Natural origin pacing would exceed the declared conservative ceiling: " + str(speed))
        if auto_fit and scene["id"] not in provenance["selected"]:
            raise RuntimeError("Scene did not fit after six complete origin regenerations: " + scene["id"])
    for filename, expected in module.EXPECTED_ASSETS.items():
        assert sha(VOICE_SOURCE / filename) == expected
    print("SELECTED", json.dumps(provenance["selected"], sort_keys=True), flush=True)


def sentence_split(text):
    parts = re.split(r"(?<=[.!?])\s+(?=[A-ZÁÉÍÓÚÜ¿¡])", text)
    assert " ".join(parts) == text
    return parts


def chunks(text, width=82):
    """Literal word-preserving chunks; prefer semantic punctuation boundaries."""
    result = []
    remaining = text
    while len(remaining) > width or len(textwrap.wrap(remaining, width=43, break_long_words=False, break_on_hyphens=False)) > 2:
        prefix = remaining[:width + 1]
        cuts = [m.end() for m in re.finditer(r"[,;:]", prefix) if m.end() >= width * .45]
        cut = cuts[-1] if cuts else prefix.rfind(" ")
        assert cut > 0
        while len(textwrap.wrap(remaining[:cut].strip(), width=43, break_long_words=False, break_on_hyphens=False)) > 2:
            cut = remaining[:cut].rfind(" ")
            assert cut > 0
        result.append(remaining[:cut].strip())
        remaining = remaining[cut:].strip()
    if remaining:
        result.append(remaining)
    if len(result) > 1 and len(result[-1]) < 20:
        pair = result[-2] + " " + result[-1]
        wrapped = textwrap.wrap(pair, width=43, break_long_words=False, break_on_hyphens=False)
        if len(wrapped) <= 2:
            result[-2:] = [pair]
        else:
            cuts = [m.start() for m in re.finditer(" ", pair)]
            cut = min(cuts, key=lambda x: abs(x - len(pair) / 2))
            result[-2:] = [pair[:cut], pair[cut + 1:]]
    assert " ".join(result) == text
    return result


def timecode(seconds):
    ms = round(seconds * 1000)
    h, ms = divmod(ms, 3600000); m, ms = divmod(ms, 60000); s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def caption_rows(scenes, selected, write=True):
    captions = {"es": [], "en": []}
    for scene in scenes:
        row = selected[scene["id"]]
        spanish = sentence_split(scene["es"])
        english = sentence_split(scene["en"])
        marks = row["sentences"]
        if len(spanish) != len(english) or len(spanish) != len(marks):
            raise ValueError("Bilingual sentence pairing differs: " + scene["id"])
        for index, (es, en, mark) in enumerate(zip(spanish, english, marks)):
            if mark["start"] is None or mark["end"] is None:
                raise ValueError("Unresolved model sentence timestamp: " + scene["id"])
            start = scene["start"] + mark["start"]
            # Retain the subtitle slightly beyond the spoken sentence, within
            # the following sentence onset / complete scene boundary.
            following = marks[index + 1]["start"] if index + 1 < len(marks) else row["duration"] - .15
            end = scene["start"] + min(following - .04, mark["end"] + .22)
            if end <= start:
                raise ValueError("Nonpositive caption interval")
            for lang, sentence in (("es", es), ("en", en)):
                parts = chunks(sentence)
                total = sum(len(p) for p in parts)
                cursor = start
                for j, part in enumerate(parts):
                    stop = end if j == len(parts) - 1 else cursor + (end - start) * len(part) / total
                    wrapped = textwrap.wrap(part, width=43, break_long_words=False, break_on_hyphens=False)
                    if len(wrapped) > 2:
                        raise ValueError("Caption exceeds two lines: " + part)
                    captions[lang].append({"scene": scene["id"], "start": round(cursor, 3), "end": round(stop, 3),
                                           "text": "\n".join(wrapped), "literal": part,
                                           "sentence": index, "timing": "model sentence boundaries; proportional clause allocation for readable bilingual chunks"})
                    cursor = stop
        for lang in ("es", "en"):
            restored = " ".join(c["literal"] for c in captions[lang] if c["scene"] == scene["id"])
            assert restored == scene[lang], (scene["id"], lang)
    for lang, rows in captions.items():
        assert all(0 <= r["start"] < r["end"] <= 360 for r in rows)
        assert all(a["end"] <= b["start"] for a, b in zip(rows, rows[1:]))
        for row in rows:
            row["characters_per_second"] = round(len(row["literal"]) / (row["end"] - row["start"]), 3)
        target = R05 / ("R05_" + lang.upper() + ".srt")
        text = "\n\n".join(str(i) + "\n" + timecode(row["start"]) + " --> " + timecode(row["end"]) + "\n" + row["text"]
                           for i, row in enumerate(rows, 1)) + "\n"
        if write:
            target.write_text(text, encoding="utf-8-sig")
    return captions


def ffmpeg(arguments):
    result = subprocess.run([str(FF), "-hide_banner", "-nostdin", "-threads", "3"] + arguments,
                            capture_output=True, text=True, encoding="utf8", errors="replace", check=True)
    return result


def norm_json(stderr):
    return json.loads(re.findall(r'\{\s*"input_i".*?\}', stderr, re.S)[-1])


def assemble():
    provenance = read_provenance()
    scenes = literal_scenes()
    attempts = {r["id"]: r for r in provenance["attempts"]}
    selected = {scene["id"]: attempts[provenance["selected"][scene["id"]]] for scene in scenes}
    for filename, metadata in provenance["assets"].items():
        assert sha(VOICE_SOURCE / filename) == metadata["sha256"]
    for filename, expected in provenance["runner_files"].items():
        assert sha(VOICE_SOURCE / "pydeps/kokoro_onnx" / filename) == expected
    # The stock runner dependencies are read-only here as well; no synthesis.
    sys.path.insert(0, str(runtime_alias_readonly() / "pydeps"))
    import numpy as np
    import soundfile as sf
    samples = np.zeros(360 * 24000, dtype=np.float32)
    for scene in scenes:
        row = selected[scene["id"]]
        source = R05 / row["file"]
        assert sha(source) == row["wav_sha256"] and row["fit_margin_seconds"] >= 0
        with source.open("rb") as stream:
            data, sr = sf.read(stream, dtype="float32")
        assert sr == 24000 and len(data) == row["total_samples"]
        start = scene["start"] * sr
        assert start + len(data) <= scene["end"] * sr
        samples[start:start + len(data)] = data
    raw_voice = R05 / "audio/locucion_R05_24k.wav"
    with raw_voice.open("wb") as stream:
        sf.write(stream, samples, 24000, subtype="PCM_24", format="WAV")
    with wave.open(str(raw_voice), "rb") as master:
        for scene in scenes:
            row = selected[scene["id"]]
            with wave.open(str(R05 / row["file"]), "rb") as original:
                original_pcm = original.readframes(original.getnframes())
            master.setpos(scene["start"] * 24000)
            assert master.readframes(row["total_samples"]) == original_pcm
    captions = caption_rows(scenes, selected)
    voice48 = R05 / "audio/locucion_R05_48k.wav"
    music48 = R05 / "audio/ambiente_R05_48k.wav"
    mix48 = R05 / "audio/mezcla_R05_48k.wav"
    ffmpeg(["-n", "-i", str(raw_voice), "-ar", "48000", "-ac", "2", "-c:a", "pcm_s24le", str(voice48)])
    music_hash = sha(MUSIC)
    ffmpeg(["-n", "-i", str(MUSIC), "-af", "atrim=end_sample=17280000,afade=t=out:st=358:d=2", "-ar", "48000", "-ac", "2", "-c:a", "pcm_s24le", str(music48)])
    inputs = ["-filter_complex_threads", "2", "-i", str(voice48), "-i", str(music48)]
    base = "[0:a][1:a]amix=inputs=2:normalize=0,"
    measure = ffmpeg(inputs + ["-filter_complex", base + "loudnorm=I=-16:TP=-1.5:LRA=9:print_format=json[a]", "-map", "[a]", "-f", "null", "NUL"])
    measured = norm_json(measure.stderr)
    normalizer = ("loudnorm=I=-16:TP=-1.5:LRA=9:measured_I=" + measured["input_i"]
                  + ":measured_TP=" + measured["input_tp"] + ":measured_LRA=" + measured["input_lra"]
                  + ":measured_thresh=" + measured["input_thresh"] + ":offset=" + measured["target_offset"]
                  + ":linear=true:print_format=json")
    final = ffmpeg(inputs + ["-n", "-filter_complex", base + normalizer + ",aresample=48000,atrim=end_sample=17280000[a]",
                            "-map", "[a]", "-ar", "48000", "-ac", "2", "-c:a", "pcm_s24le", str(mix48)])
    assert sha(MUSIC) == music_hash
    import audioop
    integer_peaks = {}
    for target in (voice48, music48, mix48):
        with wave.open(str(target), "rb") as stream:
            assert stream.getframerate() == 48000 and stream.getnchannels() == 2
            assert stream.getsampwidth() == 3 and stream.getnframes() == 17280000
            peak = 0
            for block in iter(lambda: stream.readframes(1000000), b""):
                peak = max(peak, audioop.max(block, 3))
            assert peak < (2 ** 23 - 1)
            integer_peaks[str(target.relative_to(R05))] = peak
    provenance["captions"] = captions
    provenance["assembly_helper_sha256"] = sha(__file__)
    provenance["original_voice_assets_reverified_unchanged"] = True
    provenance["cost"] = {"all_unique_complete_takes": len(attempts),
                          "all_take_generation_host_seconds": sum(r["host_seconds"] for r in attempts.values()),
                          "selected_take_generation_host_seconds": sum(r["host_seconds"] for r in selected.values()),
                          "selected_origin_speeds": {s["id"]: selected[s["id"]]["recipe"]["parameters"]["speed"] for s in scenes},
                          "scope": "Measured synthesis host time, not an energy, cloud, financial or human-listening metric"}
    provenance["master"] = {"duration_seconds": 360, "sample_frames_48k": 17280000,
                            "complete_voice_waveforms_retained": True, "voice_stretch_or_phoneme_trim": False,
                            "each_selected_take_PCM_exact_in_24k_master": True,
                            "PCM24_integer_peaks": integer_peaks, "integer_clipping_observed": False,
                            "files": {str(t.relative_to(R05)): {"bytes": t.stat().st_size, "sha256": sha(t)}
                                      for t in (raw_voice, voice48, music48, mix48, R05 / "R05_EN.srt", R05 / "R05_ES.srt")},
                            "music_source": str(MUSIC), "music_source_sha256": music_hash,
                            "music_provenance": "Original procedural ambient from approved R03/R04; reused first360s with music-only endfade; no third-party media",
                            "ffmpeg": str(FF), "ffmpeg_sha256": sha(FF),
                            "first_pass_loudness": measured, "final_loudness": norm_json(final.stderr),
                            "subtitle_sync_scope": "Model phoneme-derived sentence starts; readable clauses allocated within paired literal sentence windows. No independent ASR or human listening claimed."}
    save_provenance(provenance)
    print("MASTER", json.dumps(provenance["master"], ensure_ascii=False), flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--describe", action="store_true")
    group.add_argument("--synthesize", action="store_true")
    group.add_argument("--assemble", action="store_true")
    parser.add_argument("--ids", nargs="*")
    parser.add_argument("--speed", type=float, default=.84)
    parser.add_argument("--auto-fit", action="store_true")
    args = parser.parse_args()
    if args.describe:
        print(json.dumps({"scenes": [{"id": s["id"], "seconds": s["end"] - s["start"], "words": len(s["es"].split())} for s in literal_scenes()],
                          "voice": "Kokoro ONNX0.6.1 em_alex es-419", "runtime_alias": str(ALIAS), "new_DEE_ticks": 0}, ensure_ascii=False)); return
    install_write_boundary()
    if not .60 <= args.speed <= 1.35:
        parser.error("Origin speed must stay between 0.60 and 1.35")
    if args.synthesize:
        synthesize(args.ids, args.speed, args.auto_fit)
    else:
        assemble()


if __name__ == "__main__":
    main()
