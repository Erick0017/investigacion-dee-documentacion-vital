from __future__ import annotations

import argparse
import html
import json
import sys
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description="Passive Mente Basal local panel")
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    root = args.root.resolve()
    sys.path.insert(0, str(root / "app"))
    import habitat

    paths = habitat.root_paths(root)
    status = habitat.load_json(paths["status"])
    latest_relative = paths["latest"].read_text(encoding="utf-8").strip()
    checkpoint = root / latest_relative
    runtime = habitat.dee.Runtime.load_snapshot(str(checkpoint))
    g = habitat.geometry()
    sites = {
        "response1": g.response1,
        "revision1": g.revision1,
        "response2": g.response2,
        "revision2": g.revision2,
        "response3": g.response3,
        "context_hub": g.aux_hub_context,
        "initial_material_hub": g.aux_hub_initial,
    }
    spatial = {name: habitat.observe_site(runtime, site) for name, site in sites.items()}
    recent: list[dict[str, object]] = []
    controller = habitat.load_json(paths["controller"])
    active = habitat.active_segment(paths, controller)
    if active.exists():
        lines = active.read_text(encoding="utf-8").splitlines()[-30:]
        recent = [json.loads(line) for line in lines if line.strip()]
    payload = {
        "schema": "mente-basal.panel.v1",
        "observation_mode": "passive snapshot load",
        "world_id": status["world_id"],
        "session_id": status["session_id"],
        "status_tick": status["tick"],
        "checkpoint_tick": int(runtime.current_tick),
        "checkpoint": latest_relative,
        "field": "DEE record fields (RAW, clock, state, s_reg, direction, semantic)",
        "region": "fixed declared functional sites",
        "aggregation": "none; one voxel per declared site",
        "operational_status": status,
        "spatial_view": spatial,
        "timeline_tail": recent,
        "interpretation_guard": (
            "Activity and change are shown separately from any learned function; "
            "this passive panel does not establish learning."
        ),
    }
    json_output = (args.output or (paths["analysis"] / "panel_latest.html")).with_suffix(".json")
    html_output = args.output or (paths["analysis"] / "panel_latest.html")
    habitat.atomic_json(json_output, payload)

    rows = []
    for name, record in spatial.items():
        rows.append(
            "<tr><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td>"
            "<td>{}</td><td>{}</td><td>{}</td></tr>".format(
                html.escape(name), html.escape(str(record["site"])), record["raw"],
                record["clock"], record["state"], record["s_reg"],
                html.escape(str(record["direction"])), record["semantic"],
            )
        )
    timeline_rows = []
    for event in recent:
        timeline_rows.append(
            "<tr><td>{}</td><td>{}</td><td><pre>{}</pre></td></tr>".format(
                html.escape(str(event.get("tick", ""))),
                html.escape(str(event.get("type", ""))),
                html.escape(json.dumps(event, ensure_ascii=False, sort_keys=True)),
            )
        )
    document = """<!doctype html><meta charset=\"utf-8\"><title>Mente Basal panel</title>
<style>body{font:14px system-ui;margin:2rem;color:#17202a}table{border-collapse:collapse;width:100%%;margin:1rem 0}th,td{border:1px solid #ccd1d1;padding:.45rem;text-align:left;vertical-align:top}pre{white-space:pre-wrap;margin:0}.guard{padding:.8rem;background:#fff4d6}</style>
<h1>Mente Basal — panel local pasivo</h1>
<p><b>Mundo:</b> %s &nbsp; <b>Sesión:</b> %s</p>
<p><b>Tick de estado:</b> %s &nbsp; <b>Tick del checkpoint:</b> %s &nbsp; <b>Worker:</b> %s</p>
<p><b>Campo:</b> RAW, clock, state, s_reg, dirección y semantic. <b>Región:</b> sitios funcionales fijos declarados. <b>Agregación:</b> ninguna.</p>
<p class=\"guard\">Actividad, cambio, memoria candidata y aprendizaje contrastado no son equivalentes. Este panel no decide aprendizaje.</p>
<h2>Vista espacial declarada</h2><table><tr><th>Sitio</th><th>Coordenada</th><th>RAW</th><th>clock</th><th>state</th><th>s_reg</th><th>dirección</th><th>semantic</th></tr>%s</table>
<h2>Línea temporal reciente</h2><table><tr><th>Tick</th><th>Tipo</th><th>Registro</th></tr>%s</table>
""" % (
        html.escape(str(payload["world_id"])), html.escape(str(payload["session_id"])),
        payload["status_tick"], payload["checkpoint_tick"],
        html.escape(str(status["state"])), "".join(rows), "".join(timeline_rows),
    )
    habitat.atomic_text(html_output, document)
    print(json.dumps({"html": str(html_output), "json": str(json_output),
                      "checkpoint_tick": int(runtime.current_tick)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
