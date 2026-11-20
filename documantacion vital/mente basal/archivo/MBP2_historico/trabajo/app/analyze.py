from __future__ import annotations

"""Offline scientific analysis for Mente Basal Persistente 2.

This program never opens a worker command queue and never writes inside a
world.  It reads immutable checkpoints/history, executes diagnostic forks in
memory and publishes only the campaign-level analysis and report.
"""

import argparse
import collections
import datetime as dtm
import hashlib
import json
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Iterator


APP_DIR = Path(__file__).resolve().parent
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

import mbp2


SCHEMA = "mbp2.final-analysis.v1"
CONDITIONS = ("A", "B", "C")
CONTACT_PREDICTIONS = {
    16: {"before_tick": 15, "before_load": 11, "before_direction": [1, 0, 0],
         "after_load": 13, "after_direction": [1, 1, 0], "environment": "E1"},
    80: {"before_tick": 79, "before_load": 13, "before_direction": [1, 1, 0],
         "after_load": 16, "after_direction": [1, 0, 0], "environment": "E2"},
}
TICK_PATTERN = re.compile(r"(?:^|[_-])(?:t|tick_?)(\d+)(?:[_\-.]|$)", re.IGNORECASE)


@dataclass(frozen=True)
class Cut:
    condition: str
    checkpoint: Path
    tick: int
    role: str
    source: str
    world_root: Path
    descriptor: Path | None = None


def utc_now() -> str:
    return dtm.datetime.now(dtm.timezone.utc).isoformat(timespec="milliseconds")


def atomic_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(text, encoding="utf-8", newline="\n")
    os.replace(temporary, path)


def atomic_json(path: Path, value: Any) -> None:
    atomic_text(path, json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n")


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def safe_resolve(root: Path, value: str | Path, bases: Iterable[Path] = ()) -> Path | None:
    candidate = Path(value)
    attempts = [candidate] if candidate.is_absolute() else [base / candidate for base in (root, *bases)]
    for attempt in attempts:
        resolved = attempt.resolve()
        if resolved.exists():
            return resolved
    return None


def iter_path_strings(value: Any) -> Iterator[str]:
    if isinstance(value, str):
        lowered = value.lower()
        if lowered.endswith((".deetsnap", ".deetsnap.json")) or (
                lowered.endswith(".json") and "cut_" in lowered):
            yield value
    elif isinstance(value, list):
        for item in value:
            yield from iter_path_strings(item)
    elif isinstance(value, dict):
        for item in value.values():
            yield from iter_path_strings(item)


def find_world_root(path: Path, campaign_root: Path) -> Path:
    for parent in (path.parent, *path.parents):
        if (parent / "world" / "checkpoints").exists() and (parent / "history").exists():
            return parent
        if parent == campaign_root:
            break
    # Descriptor paths live below <world>/history/collections.
    if "history" in path.parts:
        parts = list(path.parts)
        index = len(parts) - 1 - parts[::-1].index("history")
        return Path(*parts[:index])
    return path.parent


def condition_for_world(world_root: Path, checkpoint: Path | None = None) -> str:
    instance = world_root / "world" / "instance.json"
    if instance.exists():
        value = str(load_json(instance).get("condition", "")).upper()
        if value in CONDITIONS:
            return value
    config = world_root / "config" / "habitat.json"
    if config.exists():
        value = str(load_json(config).get("condition", "")).upper()
        if value in CONDITIONS:
            return value
    upper_parts = [part.upper() for part in world_root.parts]
    for condition in CONDITIONS:
        if any(part == condition or part.startswith(f"MBP2-{condition}-") for part in upper_parts):
            return condition
    if checkpoint is not None:
        runtime = mbp2.dee.Runtime.load_snapshot(str(checkpoint))
        value = mbp2.condition_from_runtime(runtime)
        if value in CONDITIONS:
            return value
    raise RuntimeError(f"cannot determine A/B/C condition for {world_root}")


def tick_from_path(path: Path) -> int | None:
    for candidate in (path.name, path.stem):
        match = TICK_PATTERN.search(candidate)
        if match:
            return int(match.group(1))
    return None


def role_from_name(path: Path, tick: int, explicit: str | None = None) -> str:
    if explicit:
        normalized = explicit.lower()
        if any(word in normalized for word in ("initial", "x0", "seed")):
            return "initial"
        if any(word in normalized for word in ("final", "stop", "2h")):
            return "final"
        if any(word in normalized for word in ("intermediate", "common", "1h", "mid")):
            return "intermediate"
    lowered = path.name.lower()
    if tick == 0 or "x0_" in lowered or "seeded_t0" in lowered:
        return "initial"
    if any(word in lowered for word in ("final", "stop", "2h")):
        return "final"
    return "intermediate"


def descriptor_cut(descriptor_path: Path, campaign_root: Path) -> Cut:
    descriptor = load_json(descriptor_path)
    if descriptor.get("schema") != "mente-basal.collection.v1":
        raise RuntimeError(f"unsupported descriptor schema: {descriptor_path}")
    world_root = find_world_root(descriptor_path, campaign_root)
    checkpoint = safe_resolve(campaign_root, descriptor["end_checkpoint"], (world_root,))
    if checkpoint is None:
        raise FileNotFoundError(descriptor["end_checkpoint"])
    tick = int(descriptor["end_tick"])
    role = "final" if bool(descriptor.get("stop_after")) else role_from_name(
        descriptor_path, tick, str(descriptor.get("request_id", "")))
    return Cut(condition_for_world(world_root, checkpoint), checkpoint, tick, role,
               "collection_descriptor", world_root, descriptor_path)


def checkpoint_cut(checkpoint: Path, campaign_root: Path, source: str = "checkpoint") -> Cut:
    world_root = find_world_root(checkpoint, campaign_root)
    tick = tick_from_path(checkpoint)
    if tick is None:
        runtime = mbp2.dee.Runtime.load_snapshot(str(checkpoint))
        tick = int(runtime.current_tick)
    return Cut(condition_for_world(world_root, checkpoint), checkpoint, tick,
               role_from_name(checkpoint, tick), source, world_root)


def discover_cuts(campaign_root: Path, cuts_json: Path | None) -> list[Cut]:
    descriptors: set[Path] = set()
    checkpoints: set[Path] = set()
    explicit_paths: list[Path] = []
    if cuts_json is not None:
        payload = load_json(cuts_json)
        for text in iter_path_strings(payload):
            resolved = safe_resolve(campaign_root, text, (cuts_json.parent,))
            if resolved is not None:
                explicit_paths.append(resolved)
    worlds_root = campaign_root / "worlds"
    if worlds_root.exists():
        descriptors.update(worlds_root.glob("*/history/collections/cut_*_t*.json"))
        checkpoints.update(worlds_root.glob("*/world/checkpoints/*.deetsnap"))
    for path in explicit_paths:
        if path.name.lower().endswith(".deetsnap"):
            checkpoints.add(path)
        elif path.suffix.lower() == ".json":
            try:
                payload = load_json(path)
            except (OSError, json.JSONDecodeError):
                continue
            if isinstance(payload, dict) and payload.get("schema") == "mente-basal.collection.v1":
                descriptors.add(path)
            elif path.name.lower().endswith(".deetsnap.json"):
                sibling = path.with_suffix("")
                if sibling.exists():
                    checkpoints.add(sibling)

    cuts: list[Cut] = []
    errors: list[str] = []
    for descriptor in sorted(descriptors):
        try:
            cuts.append(descriptor_cut(descriptor, campaign_root))
        except Exception as error:  # preserve other valid worlds
            errors.append(f"{descriptor}: {error}")
    for checkpoint in sorted(checkpoints):
        try:
            cuts.append(checkpoint_cut(checkpoint, campaign_root))
        except Exception as error:
            errors.append(f"{checkpoint}: {error}")
    if not cuts:
        detail = "; ".join(errors[:8])
        raise RuntimeError(f"no usable A/B/C checkpoints found{': ' + detail if detail else ''}")

    # One physical checkpoint can be referenced by a descriptor and by the
    # checkpoint directory.  Prefer the descriptor because it freezes the cut.
    deduplicated: dict[tuple[str, int, str], Cut] = {}
    for cut in cuts:
        key = (cut.condition, cut.tick, str(cut.checkpoint.resolve()))
        previous = deduplicated.get(key)
        if previous is None or (previous.descriptor is None and cut.descriptor is not None):
            deduplicated[key] = cut
    return list(deduplicated.values())


def select_scientific_cuts(cuts: list[Cut]) -> list[Cut]:
    selected: list[Cut] = []
    for condition in CONDITIONS:
        group = sorted((cut for cut in cuts if cut.condition == condition), key=lambda item: item.tick)
        if not group:
            continue
        by_tick: dict[int, Cut] = {}
        for cut in group:
            old = by_tick.get(cut.tick)
            score = (cut.descriptor is not None, "common_tick" in cut.checkpoint.name,
                     "x0_" in cut.checkpoint.name.lower())
            old_score = ((old.descriptor is not None), "common_tick" in old.checkpoint.name,
                         "x0_" in old.checkpoint.name.lower()) if old else None
            if old is None or score > old_score:
                by_tick[cut.tick] = cut
        ordered = [by_tick[tick] for tick in sorted(by_tick)]
        initial = ordered[0]
        final = ordered[-1]
        selected.append(Cut(condition, initial.checkpoint, initial.tick, "initial",
                            initial.source, initial.world_root, initial.descriptor))
        for cut in ordered[1:-1]:
            name = cut.checkpoint.name.lower()
            if ("common_tick" in name or cut.tick in (16, 64, 80, 144, 300) or
                    cut.descriptor is not None):
                selected.append(Cut(condition, cut.checkpoint, cut.tick, "intermediate",
                                    cut.source, cut.world_root, cut.descriptor))
        if final.checkpoint != initial.checkpoint:
            selected.append(Cut(condition, final.checkpoint, final.tick, "final",
                                final.source, final.world_root, final.descriptor))
    return selected


def nonzero_distributions(raw: list[int]) -> dict[str, Any]:
    semantic: collections.Counter[str] = collections.Counter()
    directions: collections.Counter[str] = collections.Counter()
    loads: list[int] = []
    states: list[int] = []
    for value in raw:
        if int(value) == 0:
            continue
        record = mbp2.dee.decode_record(int(value))
        semantic[str(int(record.semantic))] += 1
        directions[f"{int(record.dx)},{int(record.dy)},{int(record.dz)}"] += 1
        loads.append(int(record.s_reg))
        states.append(int(record.state))
    return {
        "raw_nonzero": len(loads),
        "semantic_histogram": dict(sorted(semantic.items())),
        "direction_histogram": dict(sorted(directions.items())),
        "s_reg": {
            "sum": sum(loads), "min": min(loads) if loads else None,
            "max": max(loads) if loads else None, "nonzero_count": sum(load != 0 for load in loads),
        },
        "occupied_count_from_records": sum(state > 0 for state in states),
    }


def receipt_summary(runtime: Any) -> dict[str, Any]:
    values = list(runtime.receipts)
    histogram: collections.Counter[str] = collections.Counter(str(item.status) for item in values)
    return {"total": len(values), "status_histogram": dict(sorted(histogram.items()))}


def query_diagnostic(runtime: Any, condition: str, tick: int,
                     located: dict[str, Any]) -> dict[str, Any]:
    if located.get("ambiguous") or not located.get("site") or not located.get("observation"):
        return {"executed": False, "reason": "primary lineage ambiguous or absent"}
    parent_raw = runtime.raw_copy()
    parent_clock = runtime.clock_copy()
    site = tuple(int(value) for value in located["site"])
    observation = located["observation"]
    current_direction = tuple(int(value) for value in observation["direction"])
    target = mbp2.plus(site, current_direction, 4)
    query_direction = (0, 1, 0)
    source = mbp2.plus(target, query_direction, -4)
    with_query = runtime.fork()
    without_query = runtime.fork()
    channel = mbp2.dee.ChannelSpec()
    channel.name = f"analysis.query.{condition}.t{tick}"
    channel.injection_site = mbp2.base.coordinate(source)
    channel.state = 1
    channel.direction = mbp2.base.direction(query_direction)
    channel.semantic = 1
    channel.allow_experience = True
    channel.allow_probe = False
    with_query.register_channel(channel)
    receipt = with_query.experience(channel.name, tick, 7)
    with_query.advance(4)
    without_query.advance(4)
    query_observation = mbp2.observe_site(with_query, target)
    no_query_observation = mbp2.observe_site(without_query, target)
    final_receipt = with_query.receipt(receipt.id)
    return {
        "executed": True,
        "mode": "diagnostic forks; never returned to A/B/C",
        "source": list(source), "target": list(target), "load": 7,
        "direction": list(query_direction),
        "receipt": {
            "id": int(final_receipt.id), "status": str(final_receipt.status),
            "requested_tick": int(final_receipt.requested_tick),
            "effective_tick": (None if final_receipt.effective_tick is None
                               else int(final_receipt.effective_tick)),
            "reason": str(final_receipt.reason),
        },
        "history_plus_query": query_observation,
        "same_history_without_query": no_query_observation,
        "query_delta_s_reg": int(query_observation["s_reg"]) - int(no_query_observation["s_reg"]),
        "parent_checkpoint_unmodified": (
            parent_raw == runtime.raw_copy() and parent_clock == runtime.clock_copy() and
            int(runtime.current_tick) == tick),
    }


def analyze_cut(cut: Cut) -> dict[str, Any]:
    runtime = mbp2.dee.Runtime.load_snapshot(str(cut.checkpoint))
    tick = int(runtime.current_tick)
    if tick != cut.tick:
        raise RuntimeError(f"checkpoint tick mismatch for {cut.checkpoint}: {tick} != {cut.tick}")
    metrics = runtime.metrics()
    raw = runtime.raw_copy()
    clocks = runtime.clock_copy()
    located = mbp2.locate_primary(runtime, cut.condition, tick)
    companion_site = mbp2.plus(mbp2.geometry().companion_site, mbp2.BASE_DIRECTION, tick)
    sidecar = cut.checkpoint.with_suffix(cut.checkpoint.suffix + ".json")
    return {
        "condition": cut.condition, "role": cut.role, "tick": tick,
        "checkpoint": str(cut.checkpoint), "checkpoint_bytes": cut.checkpoint.stat().st_size,
        "checkpoint_sha256": sha256(cut.checkpoint),
        "checkpoint_sidecar": str(sidecar) if sidecar.exists() else None,
        "descriptor": str(cut.descriptor) if cut.descriptor else None,
        "source": cut.source,
        "metrics": {
            "raw_support": int(metrics.raw_support), "occupied": int(metrics.occupied),
            "s_reg_sum": int(metrics.s_reg_sum),
            "backend": str(runtime.execution_options.backend),
            "threads": int(runtime.execution_options.threads),
        },
        "global": {
            **nonzero_distributions(raw),
            "clock": {
                "site_count": len(clocks), "min": min(clocks) if clocks else None,
                "max": max(clocks) if clocks else None,
                "all_equal_tick": all(int(value) == tick for value in clocks),
            },
        },
        "receipts": receipt_summary(runtime),
        "lineage": located,
        "companion": {"site": list(companion_site),
                      "observation": mbp2.observe_site(runtime, companion_site)},
        "history_query_diagnostic": query_diagnostic(runtime, cut.condition, tick, located),
        "evidence_class": {
            "checkpoint_state": "observed directly from immutable snapshot",
            "query": "new diagnostic execution on isolated forks",
            "causal_interpretation": "requires A/B/C and contact-log contrasts",
        },
    }


def iter_history_events(world_root: Path) -> Iterator[tuple[Path, dict[str, Any]]]:
    directory = world_root / "history" / "segments"
    if not directory.exists():
        return
    for path in sorted(directory.glob("*.jsonl")):
        with path.open("r", encoding="utf-8") as stream:
            for line_number, line in enumerate(stream, 1):
                if not line.strip():
                    continue
                try:
                    event = json.loads(line)
                except json.JSONDecodeError as error:
                    raise RuntimeError(f"invalid JSONL {path}:{line_number}: {error}") from error
                yield path, event


def contact_summary(world_root: Path, condition: str) -> dict[str, Any]:
    observations: dict[int, dict[str, Any]] = {}
    external_inputs = 0
    advances = {"calls": 0, "ticks": 0, "overflows": 0, "genesis": 0}
    files: set[str] = set()
    for path, event in iter_history_events(world_root):
        files.add(str(path))
        event_type = event.get("type")
        if event_type == "input_scheduled":
            external_inputs += 1
        elif event_type == "advance":
            advances["calls"] += 1
            advances["ticks"] += int(event.get("count", 0))
            advances["overflows"] += int(event.get("overflows", 0))
            advances["genesis"] += int(event.get("genesis", 0))
        elif event_type == "scientific_observation":
            tick = int(event.get("tick", -1))
            primary = event.get("readings", {}).get("primary_prediction", {}).get("observed")
            if isinstance(primary, dict):
                observations[tick] = primary

    evidence: list[dict[str, Any]] = []
    executed = 0
    for after_tick, prediction in CONTACT_PREDICTIONS.items():
        before = observations.get(int(prediction["before_tick"]))
        after = observations.get(after_tick)
        matched = bool(
            condition == "B" and before and after and
            int(before.get("s_reg", -1)) == prediction["before_load"] and
            before.get("direction") == prediction["before_direction"] and
            int(after.get("s_reg", -1)) == prediction["after_load"] and
            after.get("direction") == prediction["after_direction"]
        )
        if matched:
            executed += 1
        evidence.append({
            "environment": prediction["environment"], "after_tick": after_tick,
            "before": before, "after": after, "executed_match": matched,
            "status": ("observed_contact_transition" if matched else
                       "control_or_not_observed_in_log"),
        })
    control_observations_present = all(tick in observations for tick in (16, 80))
    control_retained = control_observations_present and all(
        observations.get(tick, {}).get("s_reg") == 11 and
        observations.get(tick, {}).get("direction") == [1, 0, 0]
        for tick in (16, 80)
    )
    return {
        "condition": condition, "history_files": sorted(files),
        "external_inputs_after_t0_logged": external_inputs,
        "advance_events": advances,
        "contacts_executed_from_frozen_transition_evidence": executed,
        "contact_evidence": evidence,
        "control_lineage_retained_where_observed": control_retained,
        "coverage_note": "counts only predeclared t15→16 and t79→80 transitions present in scientific logs",
    }


def common_age_comparisons(cuts: list[dict[str, Any]]) -> dict[str, Any]:
    by_condition_tick: dict[str, dict[int, dict[str, Any]]] = {condition: {} for condition in CONDITIONS}
    for cut in cuts:
        by_condition_tick[cut["condition"]][int(cut["tick"])] = cut
    sets = [set(by_condition_tick[condition]) for condition in CONDITIONS]
    common_ticks = sorted(set.intersection(*sets)) if all(sets) else []
    rows: list[dict[str, Any]] = []
    for tick in common_ticks:
        states = {condition: by_condition_tick[condition][tick] for condition in CONDITIONS}
        loads: dict[str, int | None] = {}
        query_loads: dict[str, int | None] = {}
        for condition, state in states.items():
            lineage = state["lineage"]
            observation = lineage.get("observation") if isinstance(lineage, dict) else None
            loads[condition] = int(observation["s_reg"]) if observation else None
            query = state["history_query_diagnostic"]
            qobs = query.get("history_plus_query") if query.get("executed") else None
            query_loads[condition] = int(qobs["s_reg"]) if qobs else None
        rows.append({
            "tick": tick, "primary_loads": loads, "query_output_loads": query_loads,
            "contrasts": {
                "B_minus_C_primary": (None if loads["B"] is None or loads["C"] is None
                                      else loads["B"] - loads["C"]),
                "B_minus_C_query": (None if query_loads["B"] is None or query_loads["C"] is None
                                    else query_loads["B"] - query_loads["C"]),
                "A_minus_C_primary": (None if loads["A"] is None or loads["C"] is None
                                      else loads["A"] - loads["C"]),
            },
            "comparison_scope": "exact same DEE tick; no wall-time-to-tick conversion",
        })
    final_ticks = {
        condition: max(by_condition_tick[condition]) if by_condition_tick[condition] else None
        for condition in CONDITIONS
    }
    return {
        "exact_common_ticks": common_ticks,
        "rows": rows,
        "latest_exact_common_tick": max(common_ticks) if common_ticks else None,
        "final_ticks_by_condition": final_ticks,
        "final_endpoints_exactly_age_matched": (
            all(final_ticks[condition] is not None for condition in CONDITIONS) and
            len({final_ticks[condition] for condition in CONDITIONS}) == 1),
        "limit": ("Los endpoints finales se informan por separado cuando sus ticks difieren; "
                  "el analizador no retrodata un checkpoint posterior ni equipara tiempo de pared "
                  "con edad DEE."),
    }


def markdown_report(result: dict[str, Any]) -> str:
    lines = [
        "# Mente Basal Persistente 2 — informe integrado A/B/C",
        "",
        f"Campaña: `{result['campaign_id']}`. Producto: DEE thinking 2.2.0; kernel DEE v27 congelado.",
        "Este informe fue calculado fuera de los workers, desde checkpoints y segmentos conservados.",
        "",
        "## Preparación y pregunta",
        "",
        "A contiene la díada basal sin inventario ambiental adicional. B contiene dos portadores "
        "genéricos: el encuentro E1 cambia la ruta y hace accesible E2. C conserva el inventario de B, "
        "pero separa E1 en z; E2 queda presente y no es accesible sin el primer encuentro. Ningún mundo "
        "recibe entradas del host después de t0 por diseño.",
        "",
        "La comparación principal B–C pregunta por contacto/contingencia con inventario inicial "
        "comparable. No es un control de orden con igual dosis efectiva: B puede recibir dos encuentros "
        "y C ninguno.",
        "",
        "## Evidencia observada",
        "",
    ]
    for condition in CONDITIONS:
        contact = result["contact_logs"].get(condition)
        if not contact:
            lines.append(f"- {condition}: mundo o historia no disponible.")
            continue
        final_tick = result["common_age_comparison"]["final_ticks_by_condition"].get(condition)
        lines.append(
            f"- {condition}: {contact['contacts_executed_from_frozen_transition_evidence']} "
            f"encuentros predeclarados confirmados por el log; {contact['external_inputs_after_t0_logged']} "
            f"entradas externas registradas; endpoint analizado T{final_tick}."
        )
    lines.extend(["", "## Comparaciones a edad DEE común", ""])
    rows = result["common_age_comparison"]["rows"]
    if rows:
        lines.extend([
            "| Tick | carga A | carga B | carga C | B−C | query A | query B | query C |",
            "|---:|---:|---:|---:|---:|---:|---:|---:|",
        ])
        for row in rows:
            loads, queries = row["primary_loads"], row["query_output_loads"]
            lines.append(
                f"| {row['tick']} | {loads['A']} | {loads['B']} | {loads['C']} | "
                f"{row['contrasts']['B_minus_C_primary']} | {queries['A']} | {queries['B']} | {queries['C']} |"
            )
    else:
        lines.append("No hubo un tick exacto representado por checkpoints en A, B y C.")
    lines.extend([
        "",
        result["common_age_comparison"]["limit"],
        "",
        "## Diagnóstico history ± query",
        "",
        "Cada consulta se ejecutó en un fork aislado del checkpoint. La rama sin consulta avanzó la "
        "misma cantidad. Ningún estado diagnóstico volvió a A, B o C. Una diferencia de salida conserva "
        "el contenido físico disponible; por sí sola no demuestra aprendizaje general.",
        "",
        "## Separación epistemológica",
        "",
        "- **Observado:** RAW/clocks/métricas en snapshots, observaciones predeclaradas y entradas del log.",
        "- **Ejecutado en diagnóstico:** ramas history+query y history sin query desde los cortes.",
        "- **Reconstruido por replay:** no se atribuye replay tick a tick salvo que figure explícitamente "
        "en los artefactos de campaña; este analizador no inventa ticks de contacto ausentes del log.",
        "- **Hipótesis:** que la diferencia B–C constituye adquisición ambiental acotada requiere que "
        "los contactos, retención y uso se sostengan conjuntamente bajo los controles.",
        "- **No ensayado:** réplica estadística, aprendizaje universal, igual dosis con orden alternativo, "
        "autoenseñanza, continuidad indefinida y transferencia fuera de la consulta declarada.",
        "",
        "## Límite de interpretación",
        "",
        "A/B/C son condiciones, no réplicas independientes. El ambiente fue preparado con una "
        "contingencia física, aunque no contenía una respuesta de evaluación. El resultado máximo "
        "compatible con este análisis es una modificación histórica finita, retenida y funcionalmente "
        "accesible dentro del aparato; no un dictamen global de inteligencia o consciencia.",
        "",
    ])
    return "\n".join(lines)


def campaign_id(campaign_root: Path) -> str:
    for candidate in (campaign_root / "campaign.json", campaign_root / "config" / "campaign.json",
                      campaign_root / "campaign_state.json"):
        if candidate.exists():
            value = load_json(candidate)
            for key in ("campaign_id", "id"):
                if value.get(key):
                    return str(value[key])
    worlds_root = campaign_root / "worlds"
    if worlds_root.exists():
        for instance in sorted(worlds_root.glob("*/world/instance.json")):
            value = load_json(instance)
            if value.get("campaign_id"):
                return str(value["campaign_id"])
    return campaign_root.name


def main() -> int:
    parser = argparse.ArgumentParser(description="Offline final A/B/C analysis for MBP2")
    parser.add_argument("--campaign-root", type=Path, required=True)
    parser.add_argument("--cuts-json", type=Path)
    args = parser.parse_args()
    root = args.campaign_root.resolve()
    if not root.exists():
        parser.error(f"campaign root does not exist: {root}")
    cuts_json = args.cuts_json.resolve() if args.cuts_json else None
    if cuts_json is not None and not cuts_json.exists():
        parser.error(f"cuts JSON does not exist: {cuts_json}")

    discovered = discover_cuts(root, cuts_json)
    selected = select_scientific_cuts(discovered)
    analyzed = [analyze_cut(cut) for cut in sorted(selected,
                                                   key=lambda item: (item.condition, item.tick, item.role))]
    world_roots: dict[str, Path] = {}
    for cut in selected:
        world_roots.setdefault(cut.condition, cut.world_root)
    contacts = {condition: contact_summary(world_root, condition)
                for condition, world_root in sorted(world_roots.items())}
    result = {
        "schema": SCHEMA, "created_utc": utc_now(), "campaign_id": campaign_id(root),
        "campaign_root": str(root), "cuts_json": str(cuts_json) if cuts_json else None,
        "product": "DEE thinking 2.2.0", "kernel": "DEE v27",
        "discovered_cut_count": len(discovered), "selected_cut_count": len(selected),
        "selected_cuts": analyzed,
        "contact_logs": contacts,
        "common_age_comparison": common_age_comparisons(analyzed),
        "evidence_boundaries": {
            "observed": "immutable checkpoint contents and recorded history events",
            "diagnostic": "history±query forks executed now and never returned to the worlds",
            "replay": "not claimed unless a supplied campaign artifact records it",
            "hypothesis": "B contact chain can explain retained B−C differences",
            "not_tested": ["independent replication", "equal-dose alternative ordering",
                           "unbounded retention", "general intelligence", "consciousness"],
        },
    }
    analysis_path = root / "analysis" / "FINAL_ANALYSIS.json"
    report_path = root / "docs" / "INFORME_INTEGRADO.md"
    atomic_json(analysis_path, result)
    atomic_text(report_path, markdown_report(result))
    print(json.dumps({"analysis": str(analysis_path), "report": str(report_path),
                      "cuts": len(analyzed),
                      "common_ticks": result["common_age_comparison"]["exact_common_ticks"]},
                     ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
