"""Non-rendering R04 timing contract derived from the preserved R03 timeline.

No DEE import, synthesis, media alteration or output on import. This can be
reused by the R04 editorial driver; its only clock is the presentation frame.
"""
from fractions import Fraction
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
BASE = HERE.parent / "produccion_cientifica/R03"
FPS = 30
FRAMES = 12059
DURATION = Fraction(FRAMES, FPS)
PCM_RATE = 24000
SAMPLES_PER_FRAME = PCM_RATE // FPS
PCM_SAMPLES = FRAMES * SAMPLES_PER_FRAME
SCENES = (("s01", 711), ("s02", 1515), ("s03", 1092), ("s04", 1959),
          ("s05a", 744), ("s05b", 642), ("s05c", 774), ("s05d", 714),
          ("s06", 1137), ("s07", 1381), ("s08", 1390))


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def base_contract():
    """Read/validate existing edit data; do not re-plan or write the R03 edit."""
    path = BASE / "timeline_R03.json"
    timeline = json.loads(path.read_text(encoding="utf-8-sig"))
    assert timeline["fps"] == FPS
    assert tuple((s["id"], s["frames"]) for s in timeline["scenes"]) == SCENES
    assert sum(s["frames"] for s in timeline["scenes"]) == FRAMES
    assert abs(timeline["duration"] - float(DURATION)) < 1e-9
    at = 0
    scenes = []
    for scene in timeline["scenes"]:
        count = scene["frames"]
        assert abs(scene["start"] - at / FPS) < 1e-9
        assert abs(scene["end"] - (at + count) / FPS) < 1e-9
        scenes.append({"id": scene["id"], "start_frame": at,
                       "end_frame_exclusive": at + count, "frames": count,
                       "start_seconds": at / FPS, "end_seconds": (at + count) / FPS,
                       "start_PCM_sample": at * SAMPLES_PER_FRAME,
                       "end_PCM_sample_exclusive": (at + count) * SAMPLES_PER_FRAME})
        at += count
    return {"schema": "DEE.R04.preserved_edit_timing.v1", "native_ticks": 0,
            "fps": FPS, "frames": FRAMES, "duration_rational": str(DURATION),
            "duration_seconds": float(DURATION), "source_timeline": str(path),
            "source_timeline_sha256": sha(path), "base_scene_counts_preserved": True,
            "PCM": {"sample_rate": PCM_RATE, "samples_per_video_frame": SAMPLES_PER_FRAME,
                    "samples_in_continuous_voice": PCM_SAMPLES},
            "scenes": scenes,
            "permitted_voice_replacements": {"A": scenes[0], "B": scenes[2]},
            "scope": "Presentation timeline only; no simulation, inferred causality or learned capability"}


def locate_frame(frame):
    """Return scene and local time for an exact output frame, no resampling."""
    if type(frame) is not int or not 0 <= frame < FRAMES:
        raise ValueError("An output frame must be an integer in 0..12058")
    at = 0
    for name, count in SCENES:
        if frame < at + count:
            return name, frame - at, Fraction(frame - at, FPS)
        at += count
    raise AssertionError("Frozen frame schedule is incomplete")


def validate_probe(data, require_decoded_count=True):
    """Verify ffprobe output; this function does not launch or decode media."""
    streams = data["streams"]
    video = next(s for s in streams if s.get("codec_type") == "video" or "width" in s)
    audio = next(s for s in streams if s.get("codec_type") == "audio" or "sample_rate" in s)
    assert video["codec_name"] == "h264"
    assert (video["width"], video["height"]) == (1920, 1080)
    assert video["pix_fmt"] == "yuv420p"
    assert Fraction(video["r_frame_rate"]) == FPS and Fraction(video["avg_frame_rate"]) == FPS
    assert int(video["nb_frames"]) == FRAMES
    if require_decoded_count:
        assert int(video["nb_read_frames"]) == FRAMES
    assert abs(float(video["duration"]) - float(DURATION)) < 1e-6
    assert audio["codec_name"] == "aac" and int(audio["sample_rate"]) == 48000
    # One AAC frame of container padding is technical, never an extra picture.
    assert abs(float(audio["duration"]) - float(DURATION)) <= 1024 / 48000
    return {"video_frames": FRAMES, "video_duration_seconds": float(video["duration"]),
            "audio_duration_seconds": float(audio["duration"]), "fps": FPS,
            "dimensions": [1920, 1080], "no_added_presentation_frames": True}


if __name__ == "__main__":
    print(json.dumps(base_contract(), ensure_ascii=False, indent=2))
