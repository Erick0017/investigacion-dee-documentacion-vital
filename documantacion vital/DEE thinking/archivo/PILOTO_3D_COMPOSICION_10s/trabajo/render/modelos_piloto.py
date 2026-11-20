"""Recorded CPC9 cuts for the 10s pilot; no DEE or physical interpolation.

API:
    stage_model(205), stage_model(206), stage_model(210)
    blend_model(205, 206, alpha)
    admission_model()  # Receipt/empty editorial marker only, no invented RAW.
    test_model()       # One large first-encounter closeup for the sole test PNG.
"""
from pathlib import Path
from functools import lru_cache
from copy import deepcopy
import hashlib
import json
import math
from renderer_r05 import camera_for_bounds, PALETTE

HERE = Path(__file__).resolve().parent
SOURCE_PATH = HERE.parents[1] / "subtrabajo/evidencia/COMPOSICION_CPC9_DATOS.json"
SOURCE_SHA256 = "b981d8d2378188097d21c54ce14ae22706b2011f813bd58facf72d0ca0d1eb09"
FIRST_BOUNDS = [[18.65, 6.65, 12.65], [20.65, 8.65, 14.65]]
FINAL_BOUNDS = [[23, 11, 17], [25, 13, 19]]
GLYPH_RADIUS = 0.32  # Editorial glyph, measured positions remain unaltered.


@lru_cache(maxsize=1)
def data():
    raw = SOURCE_PATH.read_bytes()
    actual = hashlib.sha256(raw).hexdigest()
    if actual != SOURCE_SHA256:
        raise ValueError(f"Pilot evidence changed: {actual}")
    return json.loads(raw)


def _stage(tick):
    if tick not in (205, 206, 210):
        raise ValueError("Only the three retained material cuts 205/206/210 are admitted")
    return deepcopy(next(row for row in data()["stages"] if row["tick"] == tick))


def _base(bounds):
    return {
        "camera": camera_for_bounds(bounds, azimuth=-35, elevation=25, fill=.86),
        "bounds": deepcopy(bounds),
        "grid": False,
        "spatial_grid": {"step": 1, "plane_z": bounds[0][2], "opacity": .12},
        "ground": {"z": bounds[0][2]-.10, "color": "#102531", "opacity": .64},
        "particles": [], "labels": [], "screen_labels": [],
        "paths": [], "arrows": [],
        "provenance": {"representation": "Etapas"},
        "new_DEE_ticks": 0,
        "trajectory_interpolation": False,
    }


def _particle(point, tick, index, opacity=1):
    if tick == 205:
        color = (PALETTE["input"], PALETTE["teaching"])[index]
    else:
        color = PALETTE["history"] if tick == 206 else PALETTE["output"]
    return {
        "position": deepcopy(point["site"]),
        "radius": GLYPH_RADIUS,
        "shape": "sphere",
        "color": color,
        "opacity": opacity,
        "source_tick": tick,
        "source_point": deepcopy(point),
        "visual_role": "recorded-site glyph, not a continuously tracked individual",
    }


def stage_model(tick):
    """Material observations remain at their exact recorded coordinates."""
    row = _stage(tick)
    bounds = FINAL_BOUNDS if tick == 210 else FIRST_BOUNDS
    m = _base(bounds)
    nonzero = [p for p in row["points"] if str(p["raw"]) != "0"]
    m["particles"] = [_particle(p, tick, i) for i, p in enumerate(nonzero)]
    m["observed_points"] = deepcopy(row["points"])  # Preserve retained zero RAW too.
    m["N"], m["tick"] = row["N"], tick
    m["evidence_bindings"] = [{
        "extraction_path": str(SOURCE_PATH), "extraction_sha256": SOURCE_SHA256,
        "extraction_pointer": "/stages/" + str(data()["stages"].index(next(x for x in data()["stages"] if x["tick"] == tick))),
        **deepcopy(row["source"]),
        "life": data()["life"], "N": row["N"], "tick": tick,
        "coverage": row["coverage"],
    }]
    m["representation_scope"] = "Retained stage; no unobserved path or cell identity is asserted."
    return m


def blend_model(before_tick, after_tick, alpha):
    """Opacity is an editorial dissolve between cuts, never physical movement."""
    if (before_tick, after_tick) != (205, 206):
        raise ValueError("Only the local 205→206 dissolve is prepared; 206→210 must be a declared cut")
    alpha = float(alpha)
    if not math.isfinite(alpha) or not 0 <= alpha <= 1:
        raise ValueError("alpha must be finite in [0,1]")
    before, after = stage_model(before_tick), stage_model(after_tick)
    m = deepcopy(after)
    m["particles"] = []
    for source, opacity in ((before, 1-alpha), (after, alpha)):
        for particle in source["particles"]:
            p = deepcopy(particle)
            p["opacity"] = opacity
            m["particles"].append(p)
    m["layers"] = [
        {"tick": before_tick, "opacity": 1-alpha, "observed_points": before["observed_points"]},
        {"tick": after_tick, "opacity": alpha, "observed_points": after["observed_points"]},
    ]
    m["evidence_bindings"] = before["evidence_bindings"] + after["evidence_bindings"]
    m["representation_scope"] = "Editorial overlap of separate recorded cuts, not a simultaneous physical state."
    return m


def admission_model():
    """Prepared port marker plus a real receipt; no unobserved T207 carrier."""
    entry = deepcopy(data()["common_use_resource7"])
    m = _base([[23, 13.8, 17], [25, 16.2, 19]])
    # No particles are created here. This outline is a prepared interface annotation.
    m["highlights"] = [{
        "position": [24, 15, 18], "radius": .38,
        "color": PALETTE["teaching"], "opacity": .72,
        "annotation": "Prepared port only; no RAW observed at T207",
    }]
    m["input_admission_evidence"] = entry
    m["source_case"] = {"life": data()["life"], "N": data()["N"]}
    m["representation_scope"] = "Receipt-only admission annotation; no material trajectory or T207 RAW inferred."
    return m


def test_model():
    """Single-frame closeup of the first encounter, with no future T210 glyph."""
    m = blend_model(205, 206, .45)
    m["test_only"] = True
    return m

