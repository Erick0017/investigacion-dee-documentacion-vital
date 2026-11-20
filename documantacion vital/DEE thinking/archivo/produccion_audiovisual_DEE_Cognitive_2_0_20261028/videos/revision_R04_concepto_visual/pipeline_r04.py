"""Isolated R04 editorial renderer/mux, reusing preserved R03 sources read-only.

No DEE imports, queries, teaching, scientific replay or original-media writes.
This module does nothing on import. Rendering and export require explicit CLI
actions; inspection/preview never launches the final render.

Visual hook, in visual_r04.py:
    render_frame(renderer, scene, local_frame, base) -> PIL.Image RGB 1920x1080
``base`` is the preserved R03 module. Do not call its plan/render/mux/export;
its read-only image_at/renderer and source drawing modules may be reused.
The hook receives exact local frame indices; no simulated clock advances.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import time
from fractions import Fraction

HERE = Path(__file__).resolve().parent
VIDEOS = HERE.parent
R03 = VIDEOS / "produccion_cientifica/R03"
WORKSPACE = next(p for p in HERE.parents if (p / "_dee20_trabajo").is_dir())
FFMPEG = WORKSPACE / "_dee20_trabajo/presentacion_clara/herramientas/ffmpeg.exe"
FFPROBE = WORKSPACE / "_dee20_trabajo/video_publico_definitivo/herramientas/ffprobe.exe"
sys.path.insert(0, str(HERE))
from contrato_tiempo_r04 import FPS, FRAMES, DURATION, SCENES, base_contract, validate_probe


def sha(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for block in iter(lambda: f.read(4 * 1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def local_output(path):
    p = Path(path).resolve()
    if not p.is_relative_to(HERE.resolve()):
        raise ValueError("Editorial intermediate files must stay inside the R04 workspace")
    p.parent.mkdir(parents=True, exist_ok=True)
    return p


def new_output(path, *, final=False):
    p = Path(path).resolve()
    allowed = VIDEOS.resolve() if final else HERE.resolve()
    if not p.is_relative_to(allowed):
        raise ValueError("Output must remain in the existing audiovisual directory")
    if p.exists():
        raise FileExistsError("Existing media are preserved: " + str(p))
    p.parent.mkdir(parents=True, exist_ok=True)
    return p


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    sys.modules[name] = m
    spec.loader.exec_module(m)
    return m


def load_base():
    # All imported R03 top-level statements define functions/read constants.
    # The R03 output functions are never called here or redirected to a new W.
    if str(R03) not in sys.path:
        sys.path.insert(0, str(R03))
    return module("r04_readonly_r03_base", R03 / "montaje_r03.py")


def load_timeline(path=None):
    path = Path(path) if path else HERE / "timeline_R04.json"
    if not path.is_file():
        if path != HERE / "timeline_R04.json":
            raise FileNotFoundError(path)
        path = R03 / "timeline_R03.json"
    d = json.loads(path.read_text(encoding="utf-8-sig"))
    expected = base_contract()
    assert d["fps"] == FPS
    assert tuple((s["id"], s["frames"]) for s in d["scenes"]) == SCENES
    for s, frozen in zip(d["scenes"], expected["scenes"]):
        assert abs(s["start"] - frozen["start_seconds"]) < 1e-9
        assert abs(s["end"] - frozen["end_seconds"]) < 1e-9
        assert abs(s["duration"] - s["frames"] / FPS) < 1e-9
    assert abs(d["duration"] - float(DURATION)) < 1e-9
    return d, path


def load_visual(path=None):
    path = Path(path) if path else HERE / "visual_r04.py"
    if not path.is_file():
        return None, None
    if not path.resolve().is_relative_to(HERE.resolve()):
        raise ValueError("The explicit R04 visual override must remain in its workspace")
    return module("r04_editorial_visual_override", path), path


def ensure_renderer_alias():
    """Recreate only the already-declared R02 DLL path alias if absent."""
    import tempfile
    alias = Path(tempfile.gettempdir()) / "DEE_R02_RENDER_PROD"
    target = VIDEOS / "produccion_cientifica"
    if alias.exists():
        if not alias.is_junction() or alias.resolve() != target.resolve():
            raise RuntimeError("An unrelated renderer alias is preserved: " + str(alias))
    else:
        q = lambda p: "'" + str(p).replace("'", "''") + "'"
        command = "New-Item -ItemType Junction -Path " + q(alias) + " -Target " + q(target) + " | Out-Null"
        subprocess.run(["powershell.exe", "-NoProfile", "-NonInteractive", "-Command", command],
                       capture_output=True, text=True, timeout=30, check=True)
        if not alias.is_junction() or alias.resolve() != target.resolve():
            raise RuntimeError("The renderer DLL alias was not confirmed")
    return alias


def image_at(renderer, scene, local_frame, base, visual=None):
    if type(local_frame) is not int or not 0 <= local_frame < scene["frames"]:
        raise ValueError("Local presentation frame outside its frozen scene")
    im = visual.render_frame(renderer, scene, local_frame, base) if visual else base.image_at(renderer, scene, local_frame / FPS)
    if im.size != (1920, 1080) or im.mode != "RGB":
        raise ValueError("The visual hook must return native 1920x1080 RGB, not a reduced frame")
    return im


def context(timeline=None, visual=None):
    plan, timeline_path = load_timeline(timeline)
    extension, extension_path = load_visual(visual)
    base = load_base()
    ensure_renderer_alias()
    renderer = base.renderer()
    return plan, timeline_path, extension, extension_path, base, renderer


def source_witness(timeline_path, visual_path):
    paths = [Path(__file__), HERE / "contrato_tiempo_r04.py", timeline_path,
             R03 / "montaje_r03.py", R03 / "estilo_r03.py", R03 / "app_visual_r03.py",
             R03 / "mecanismos_g07_g08.py", R03 / "agregacion_r03.py"]
    if visual_path:
        paths.append(visual_path)
    return [{"file": str(p), "bytes": p.stat().st_size, "sha256": sha(p)} for p in paths]


def render_scenes(ids=None, *, timeline=None, visual=None, preset="fast", crf=17, threads=3, ass=None):
    plan, tpath, ext, vpath, base, renderer = context(timeline, visual)
    outcomes = []
    ass = Path(ass).resolve(strict=True) if ass else None
    if ass and not ass.is_relative_to(HERE.resolve()):
        raise ValueError("Use R04 English ASS inside the isolated workspace")
    try:
        for scene in plan["scenes"]:
            if ids and scene["id"] not in ids:
                continue
            output = new_output(HERE / "escenas" / (scene["id"] + ".mp4"))
            logpath = local_output(HERE / "logs" / ("render_" + scene["id"] + ".log"))
            witnesses = source_witness(tpath, vpath)
            if ass:
                witnesses.append({"file": str(ass), "bytes": ass.stat().st_size, "sha256": sha(ass)})
            filters = "setsar=1"
            if ass:
                relative = ass.relative_to(HERE).as_posix().replace("'", "\\'").replace(":", "\\:")
                start_frame = round(scene["start"] * FPS)
                # The original ASS is global; restore scene-local timestamps
                # after subtitle rendering. This changes no presentation rate.
                filters = "setpts=PTS+" + str(start_frame) + "/(30*TB),ass='" + relative + "',setpts=PTS-STARTPTS,setsar=1"
            command = [str(FFMPEG), "-hide_banner", "-v", "warning", "-nostdin", "-n",
                       "-f", "rawvideo", "-pixel_format", "rgb24", "-video_size", "1920x1080",
                       "-framerate", "30", "-i", "pipe:0", "-an", "-c:v", "libx264",
                       "-threads", str(threads), "-preset", preset, "-crf", str(crf),
                       "-pix_fmt", "yuv420p", "-r", "30", "-fps_mode", "cfr",
                       "-frames:v", str(scene["frames"]), "-vf", filters, str(output)]
            started = time.monotonic()
            with logpath.open("xb") as log:
                proc = subprocess.Popen(command, stdin=subprocess.PIPE, stderr=log,
                                        creationflags=0x08000000 if os.name == "nt" else 0, cwd=HERE)
                try:
                    for frame in range(scene["frames"]):
                        proc.stdin.write(image_at(renderer, scene, frame, base, ext).tobytes())
                        if frame and frame % 600 == 0:
                            print(json.dumps({"rendering": scene["id"], "frame": frame, "total": scene["frames"]}), flush=True)
                    proc.stdin.close()
                    if proc.wait(timeout=180):
                        raise RuntimeError("Encoder failed; partial candidate retained: " + str(output))
                finally:
                    if proc.poll() is None:
                        proc.terminate()
                        proc.wait(timeout=30)
            for item in witnesses:
                if sha(item["file"]) != item["sha256"]:
                    raise RuntimeError("A source changed during a scene render; do not approve this candidate")
            outcome = {"scene": scene["id"], "frames": scene["frames"], "file": str(output),
                       "bytes": output.stat().st_size, "sha256": sha(output), "sources": witnesses,
                       "host_seconds": time.monotonic() - started, "native_ticks": 0,
                       "subtitles_burned_during_only_scene_encode": ass is not None,
                       "renderer_info": renderer.info}
            outcomes.append(outcome)
            print(json.dumps({"scene_finished": outcome}, ensure_ascii=False), flush=True)
    finally:
        renderer.close()
    return outcomes


def preview(scene_id, frame, output, *, timeline=None, visual=None):
    plan, _, ext, _, base, renderer = context(timeline, visual)
    try:
        scene = next(s for s in plan["scenes"] if s["id"] == scene_id)
        p = new_output(output)
        image_at(renderer, scene, frame, base, ext).save(p)
        return {"preview": str(p), "scene": scene_id, "local_frame": frame,
                "dimensions": [1920, 1080], "native_ticks": 0}
    finally:
        renderer.close()


def preview_many(ids=None, *, timeline=None, visual=None, frame_fraction=.5, suffix="sample"):
    """One renderer, one native-sized PNG per selected scene; no subtitles."""
    plan, tpath, ext, vpath, base, renderer = context(timeline, visual)
    results = []
    witnesses = source_witness(tpath, vpath)
    try:
        for scene in plan["scenes"]:
            if ids and scene["id"] not in ids:
                continue
            frame = min(scene["frames"] - 1, max(0, round(scene["frames"] * frame_fraction)))
            output = new_output(HERE / "previas" / (scene["id"] + "_" + suffix + ".png"))
            image_at(renderer, scene, frame, base, ext).save(output)
            results.append({"scene": scene["id"], "local_frame": frame, "file": str(output),
                            "dimensions": [1920, 1080], "native_ticks": 0})
    finally:
        renderer.close()
    for item in witnesses:
        if sha(item["file"]) != item["sha256"]:
            raise RuntimeError("A source changed while creating previews")
    return {"previews": results, "sources": witnesses, "subtitles_added": False}


def command_log(label, arguments, *, cwd=None):
    path = local_output(HERE / "logs" / (label + ".log"))
    if path.exists():
        raise FileExistsError("Prior execution log preserved; choose another declared candidate")
    with path.open("xb") as f:
        subprocess.run([str(FFMPEG), "-hide_banner", "-nostdin", *map(str, arguments)],
                       stdout=f, stderr=f, check=True, cwd=cwd,
                       creationflags=0x08000000 if os.name == "nt" else 0)
    return str(path)


def assemble(audio, output, *, timeline=None, final=False):
    """Join exact frame scenes and a PREPARED soundtrack; no voice regeneration."""
    plan, _ = load_timeline(timeline)
    output = new_output(output, final=final)
    audio = Path(audio).resolve(strict=True)
    concat = new_output(HERE / "concatenar_R04.txt")
    members = [HERE / "escenas" / (s["id"] + ".mp4") for s in plan["scenes"]]
    if not all(p.is_file() for p in members):
        raise FileNotFoundError("All eleven R04 scenes must be completed before assembly")
    concat.write_text("\n".join("file '" + p.as_posix().replace("'", "'\\''") + "'" for p in members) + "\n", encoding="utf8")
    log = command_log("assemble_R04", ["-n", "-f", "concat", "-safe", "0", "-i", concat,
                     "-i", audio, "-map", "0:v:0", "-map", "1:a:0", "-c:v", "copy",
                     "-bsf:v", "h264_metadata=sample_aspect_ratio=1/1", "-c:a", "aac",
                     "-b:a", "256k", "-ar", "48000", "-ac", "2", "-af", "atrim=end_sample=19294400,asetpts=PTS-STARTPTS",
                     "-frames:v", str(FRAMES), "-t", format(float(DURATION), ".12f"), "-movflags", "+faststart", output])
    return {"clean_master": str(output), "audio_source": str(audio), "audio_source_sha256": sha(audio),
            "frames": FRAMES, "sha256": sha(output), "bytes": output.stat().st_size, "log": log}


def export(clean, ass, output, *, crf=18, preset="medium", threads=5):
    """Explicit final encode only; this is never called by inspect/preview/render."""
    clean = Path(clean).resolve(strict=True)
    ass = Path(ass).resolve(strict=True)
    if not ass.is_relative_to(HERE.resolve()):
        raise ValueError("Use the new R04 ASS inside this workspace")
    output = new_output(output, final=True)
    relative = ass.relative_to(HERE).as_posix().replace("'", "\\'").replace(":", "\\:")
    log = command_log("export_R04", ["-n", "-i", clean, "-vf", "ass='" + relative + "',setsar=1",
                     "-map", "0:v:0", "-map", "0:a:0", "-c:v", "libx264", "-threads", str(threads),
                     "-preset", preset, "-crf", str(crf), "-profile:v", "high", "-pix_fmt", "yuv420p",
                     "-r", "30", "-fps_mode", "cfr", "-frames:v", str(FRAMES), "-c:a", "copy",
                     "-t", format(float(DURATION), ".12f"), "-movflags", "+faststart",
                     "-metadata", "title=DEE Cognitive 2.0 — Concepto y visual R04",
                     "-metadata", "artist=Ivan Erick Tlaltecatl Morales", output], cwd=HERE)
    return {"final": str(output), "frames": FRAMES, "sha256": sha(output), "bytes": output.stat().st_size,
            "clean_source_sha256": sha(clean), "ass_sha256": sha(ass), "log": log}


def probe(path, *, decode_count=True):
    command = [str(FFPROBE), "-v", "error"]
    if decode_count:
        command.append("-count_frames")
    command += ["-show_entries", "stream=codec_type,codec_name,width,height,pix_fmt,r_frame_rate,avg_frame_rate,nb_frames,nb_read_frames,duration,sample_rate,channels",
                "-show_entries", "format=duration,size", "-of", "json", str(Path(path).resolve(strict=True))]
    done = subprocess.run(command, check=True, capture_output=True, text=True, encoding="utf8")
    data = json.loads(done.stdout)
    return {"probe": data, "timing_validation": validate_probe(data, require_decoded_count=decode_count)}


def main():
    p = argparse.ArgumentParser(__doc__)
    p.add_argument("action", choices=("inspect", "preview", "render", "assemble", "export", "probe"))
    p.add_argument("--timeline", type=Path)
    p.add_argument("--visual", type=Path)
    p.add_argument("--ids", nargs="*")
    p.add_argument("--all", action="store_true", help="Preview all scenes in one renderer")
    p.add_argument("--fraction", type=float, default=.5, help="Position inside scenes for --ids/--all preview")
    p.add_argument("--suffix", default="sample")
    p.add_argument("--scene", default="s01")
    p.add_argument("--frame", type=int, default=0)
    p.add_argument("--out", type=Path)
    p.add_argument("--audio", type=Path)
    p.add_argument("--clean", type=Path)
    p.add_argument("--ass", type=Path)
    p.add_argument("--crf", type=int)
    p.add_argument("--preset")
    p.add_argument("--metadata-only", action="store_true")
    p.add_argument("--final", action="store_true", help="Allow assemble output in the audiovisual videos directory; no re-encode")
    a = p.parse_args()
    if a.action == "inspect":
        timeline, path = load_timeline(a.timeline)
        result = {"contract": base_contract(), "selected_timeline": str(path), "selected_timeline_sha256": sha(path),
                  "visual_hook": str(a.visual or HERE / "visual_r04.py"), "final_render_started": False,
                  "native_ticks": 0, "R03_unmodified_source": str(R03)}
    elif a.action == "preview":
        if a.ids or a.all:
            result = preview_many(None if a.all else a.ids, timeline=a.timeline, visual=a.visual,
                                  frame_fraction=a.fraction, suffix=a.suffix)
        else:
            result = preview(a.scene, a.frame, a.out or HERE / "previas" / f"{a.scene}_{a.frame:05d}.png", timeline=a.timeline, visual=a.visual)
    elif a.action == "render":
        result = render_scenes(a.ids, timeline=a.timeline, visual=a.visual, crf=a.crf if a.crf is not None else 17, preset=a.preset or "fast", ass=a.ass)
    elif a.action == "assemble":
        if not a.audio:
            p.error("--audio must be the prepared R04 soundtrack")
        result = assemble(a.audio, a.out or HERE / "montaje_limpio_R04.mp4", timeline=a.timeline, final=a.final)
    elif a.action == "export":
        if not a.ass:
            p.error("--ass must be the prepared R04 English subtitles")
        result = export(a.clean or HERE / "montaje_limpio_R04.mp4", a.ass,
                        a.out or VIDEOS / "DEE_Cognitive_2_0_Presentacion_R04_Concepto_y_Visual_1080p.mp4",
                        crf=a.crf if a.crf is not None else 18, preset=a.preset or "medium")
    else:
        if not a.out:
            p.error("probe reads --out PATH; it never overwrites that file")
        result = probe(a.out, decode_count=not a.metadata_only)
    print(json.dumps(result, ensure_ascii=False, indent=2), flush=True)


if __name__ == "__main__":
    main()
