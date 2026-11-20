#!/usr/bin/env python3
"""Schema-aware ingestion of claims from CORE01-CORE15, MASTER, and locked CORE16."""
from __future__ import annotations

import json
import re
import sys
import zipfile
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from core16x_common import ARCHIVE, BASELINE_SHA256, OFFICIAL, ROOT, append_ndjson, canonical_hash, sha256_file, update_state, utc, write_json


MAX_JSON_BYTES = 24 * 1024 * 1024
CLAIM_KEYS = {
    "claim_id", "canonical_claim_id", "claim", "statement", "predicate", "verdict",
    "disposition", "revalidation_status", "fresh_status", "claim_status", "claim_text",
}
CONTAINER_WORDS = ("claim", "gold", "assertion", "conclusion", "finding")
STATUS_FIELDS = ("status", "verdict", "classification", "result", "disposition", "fresh_status", "revalidation_status", "tier")
ID_FIELDS = ("claim_id", "canonical_claim_id", "id", "key", "contract_id", "name")
TEXT_FIELDS = ("claim", "claim_text", "statement", "title", "description", "predicate", "question", "finding")
MECHANISM_TERMS = {
    "transport": ("transport", "propagat", "carrier", "ballistic"),
    "destination_reduction": ("destination", "reducer", "proposal", "fiber"),
    "phase": ("phase", "oscillat", "period"),
    "history": ("history", "memory", "trace", "lineage"),
    "organization": ("organization", "persistent", "basin", "regeneration"),
    "coupling": ("coupl", "joint homeostasis", "bidirectional"),
    "interface": ("interface", "capture", "transmission", "guard"),
    "observer": ("observer", "detector", "readout", "shadow"),
    "environment": ("environment", "medium", "vacuum"),
    "matter_response": ("matter", "material", "inertia", "object"),
    "learning": ("learn", "plastic", "adaptive", "training"),
    "reinstantiation": ("reinstantiat", "reconstruct", "transfer"),
    "clock": ("clock", "causal order", "timing"),
    "geometry_topology": ("geometry", "topolog", "distance", "routing"),
    "ensemble_statistics": ("ensemble", "statistical", "distribution", "probability"),
    "relaxation_dissipation": ("relax", "dissipat", "contraction", "recovery"),
}


def source_label(name: str) -> str:
    if name.startswith("DEE_V27_MASTER"):
        return "MASTER_CORE01_14"
    match = re.match(r"(\d{2})_", name)
    return f"CORE{int(match.group(1)):02d}" if match else name


def compact(value, depth: int = 0):
    if depth > 3:
        return "<truncated-depth>"
    if isinstance(value, dict):
        out = {}
        for index, (key, item) in enumerate(value.items()):
            if index >= 30:
                out["<truncated-keys>"] = len(value) - 30
                break
            out[str(key)] = compact(item, depth + 1)
        return out
    if isinstance(value, list):
        if len(value) > 12:
            return [compact(item, depth + 1) for item in value[:12]] + [f"<truncated {len(value)-12} items>"]
        return [compact(item, depth + 1) for item in value]
    if isinstance(value, str) and len(value) > 800:
        return value[:800] + "<truncated>"
    return value


def text_blob(value) -> str:
    parts = []
    def visit(item, depth=0):
        if depth > 3 or len(parts) > 150:
            return
        if isinstance(item, dict):
            for key, sub in item.items():
                if str(key).lower() not in {"raw", "telemetry", "arrays", "trials"}:
                    visit(sub, depth + 1)
        elif isinstance(item, list):
            for sub in item[:30]:
                visit(sub, depth + 1)
        elif isinstance(item, (str, int, float, bool)):
            parts.append(str(item))
    visit(value)
    return " ".join(parts)


def status_of(record) -> str:
    if isinstance(record, dict):
        for field in STATUS_FIELDS:
            if field in record and not isinstance(record[field], (dict, list)):
                return str(record[field])
    return "UNSPECIFIED"


def id_of(record, fallback: str) -> str:
    if isinstance(record, dict):
        for field in ID_FIELDS:
            value = record.get(field)
            if isinstance(value, (str, int)) and str(value).strip():
                return str(value)
    return fallback


def statement_of(record) -> str:
    if isinstance(record, dict):
        for field in TEXT_FIELDS:
            value = record.get(field)
            if isinstance(value, str) and value.strip():
                return value[:1600]
    if isinstance(record, str):
        return record[:1600]
    return text_blob(record)[:1600]


def facets(record) -> dict:
    blob = text_blob(record).lower()
    status = status_of(record).lower()
    joined = f"{status} {blob}"
    bounded = any(term in joined for term in ("bounded_null", "bounded null", "bounded_negative", "bounded negative"))
    negative = bounded or any(term in joined for term in ("not_reproduced", "tested_null", "negative", " failed", "fail", "no evidence", "rejected"))
    superseded = any(term in joined for term in ("superseded", "obsolete", "replaced"))
    unresolved = any(term in joined for term in ("unresolved", "unknown", "open_front", "open front", "not_reconstructible", "prerequisite_missing"))
    fresh = any(term in joined for term in ("fresh_revalidated", "fresh-confirm", "fresh confirm", "holdout_confirmed", "revalidated_fresh"))
    exact = "exact_derived" in joined or "exact derived" in joined
    replay = "replay_only" in joined or "replay only" in joined
    historical = "historical_only" in joined or "original_only" in joined or "historical only" in joined
    positive_terms = ("pass", "positive", "confirmed", "promoted", "revalidated", "supported", "exact_derived", "holdout")
    positive = not negative and not superseded and any(term in joined for term in positive_terms)
    if superseded:
        polarity = "SUPERSEDED"
    elif bounded:
        polarity = "BOUNDED_NULL"
    elif negative:
        polarity = "NEGATIVE"
    elif unresolved:
        polarity = "UNRESOLVED"
    elif positive:
        polarity = "POSITIVE"
    elif historical:
        polarity = "HISTORICAL_ONLY"
    else:
        polarity = "UNCLASSIFIED"
    return {
        "polarity": polarity,
        "positive": positive,
        "negative": negative,
        "bounded_null": bounded,
        "fresh_revalidated": fresh,
        "exact_derived": exact,
        "replay_only": replay,
        "superseded": superseded,
        "unresolved": unresolved,
        "historical_only": historical,
    }


def mechanisms(record) -> list[str]:
    blob = text_blob(record).lower()
    return sorted(name for name, needles in MECHANISM_TERMS.items() if any(needle in blob for needle in needles))


def is_claim_mapping(item: dict, context: str) -> bool:
    lower_keys = {str(key).lower() for key in item}
    if lower_keys & CLAIM_KEYS:
        return True
    if any(word in context.lower() for word in CONTAINER_WORDS):
        return bool(lower_keys & (set(ID_FIELDS) | set(STATUS_FIELDS) | set(TEXT_FIELDS)))
    return False


def discover_claims(value, file_name: str):
    found = []
    containers = []
    seen_paths = set()

    def emit(item, path: str, index: str):
        token = f"{path}[{index}]"
        if token in seen_paths:
            return
        seen_paths.add(token)
        found.append((path, index, item))

    def walk(item, path: str, claim_context: bool = False, depth: int = 0):
        if depth > 18:
            return
        if isinstance(item, dict):
            if claim_context and is_claim_mapping(item, path):
                emit(item, path, "self")
            for key, child in item.items():
                key_s = str(key)
                child_path = f"{path}.{key_s}" if path else key_s
                keyed = any(word in key_s.lower() for word in CONTAINER_WORDS)
                if keyed and isinstance(child, (list, dict)):
                    containers.append({"path": child_path, "schema": type(child).__name__, "size": len(child)})
                if isinstance(child, list):
                    for idx, sub in enumerate(child):
                        if isinstance(sub, dict) and (keyed or is_claim_mapping(sub, child_path)):
                            emit(sub, child_path, str(idx))
                        elif keyed and isinstance(sub, str):
                            emit(sub, child_path, str(idx))
                        walk(sub, f"{child_path}[{idx}]", claim_context or keyed, depth + 1)
                elif isinstance(child, dict):
                    if keyed:
                        for subkey, sub in child.items():
                            if isinstance(sub, dict):
                                enriched = dict(sub)
                                enriched.setdefault("container_key", str(subkey))
                                emit(enriched, child_path, str(subkey))
                            elif isinstance(sub, str):
                                emit({"container_key": str(subkey), "claim": sub}, child_path, str(subkey))
                    walk(child, child_path, claim_context or keyed, depth + 1)
        elif isinstance(item, list):
            for idx, sub in enumerate(item):
                walk(sub, f"{path}[{idx}]", claim_context, depth + 1)

    root_context = any(word in Path(file_name).name.lower() for word in CONTAINER_WORDS)
    walk(value, "$", root_context)
    return found, containers


def archive_sources() -> list[Path]:
    numbered = sorted(path for path in ARCHIVE.glob("*.zip") if re.match(r"(0[1-9]|1[0-5])_", path.name))
    masters = sorted(ARCHIVE.glob("DEE_V27_MASTER_REVALIDATION_CORE01_TO_14_ANTI_OVERFIT_RESULTADOS.zip"))
    return numbered + masters + [OFFICIAL]


def main() -> None:
    if sha256_file(OFFICIAL) != BASELINE_SHA256:
        raise RuntimeError("Official CORE16 changed before ingestion; baseline protection triggered")
    normalized = []
    source_reports = []
    global_container_types = Counter()
    for archive_path in archive_sources():
        label = "CORE16_BASELINE" if archive_path == OFFICIAL else source_label(archive_path.name)
        source_claims = []
        candidate_files = []
        skipped_large = []
        parse_errors = []
        with zipfile.ZipFile(archive_path) as archive:
            infos = archive.infolist()
            for info in infos:
                if info.is_dir() or not info.filename.lower().endswith(".json"):
                    continue
                basename = Path(info.filename).name.lower()
                name_relevant = any(word in basename for word in ("claim", "gold", "ledger", "canonical", "contract", "result", "verdict", "status"))
                if info.file_size > MAX_JSON_BYTES and not name_relevant:
                    skipped_large.append({"file": info.filename, "bytes": info.file_size, "reason": "large_nonclaim_named_json"})
                    continue
                try:
                    value = json.loads(archive.read(info).decode("utf-8-sig"))
                except Exception as exc:
                    parse_errors.append({"file": info.filename, "error": f"{type(exc).__name__}: {exc}"})
                    continue
                found, containers = discover_claims(value, info.filename)
                if found or containers or name_relevant:
                    top_keys = list(value.keys())[:80] if isinstance(value, dict) else []
                    candidate_files.append({
                        "file": info.filename,
                        "bytes": info.file_size,
                        "top_level_type": type(value).__name__,
                        "top_level_keys": top_keys,
                        "claim_containers": containers,
                        "claims_discovered": len(found),
                    })
                for container in containers:
                    global_container_types[container["path"].split(".")[-1]] += 1
                for container_path, index, record in found:
                    fallback = f"{label}:{Path(info.filename).name}:{container_path}:{index}"
                    local_id = id_of(record, fallback)
                    fact = facets(record)
                    row = {
                        "uid": canonical_hash({"source": label, "file": info.filename, "container": container_path, "index": index, "id": local_id})[:24],
                        "source": label,
                        "archive": archive_path.name,
                        "file": info.filename,
                        "container": container_path,
                        "container_index": index,
                        "claim_id": local_id,
                        "statement": statement_of(record),
                        "reported_status": status_of(record),
                        "facets": fact,
                        "mechanisms": mechanisms(record),
                        "record_sha256": canonical_hash(record),
                        "record_excerpt": compact(record),
                    }
                    source_claims.append(row)
                    normalized.append(row)
        counter = Counter(row["facets"]["polarity"] for row in source_claims)
        facet_counts = {key: sum(1 for row in source_claims if row["facets"].get(key)) for key in (
            "positive", "negative", "bounded_null", "replay_only", "exact_derived", "fresh_revalidated", "superseded", "unresolved", "historical_only"
        )}
        source_reports.append({
            "source": label,
            "archive": archive_path.name,
            "archive_sha256": sha256_file(archive_path),
            "archive_members": len(infos),
            "files_located": candidate_files,
            "claim_structures_discovered": sorted({c["path"] for f in candidate_files for c in f["claim_containers"]}),
            "claims": len(source_claims),
            "polarity_counts": dict(sorted(counter.items())),
            "facet_counts_nonexclusive": facet_counts,
            "skipped_large_nonclaim_named_json": skipped_large,
            "json_parse_errors": parse_errors,
        })
    # Remove exact duplicate discoveries caused by nested claim context while preserving source provenance.
    unique = {}
    for row in normalized:
        dedup_key = (row["source"], row["file"], row["record_sha256"], row["claim_id"])
        unique.setdefault(dedup_key, row)
    claims = list(unique.values())
    by_source = Counter(row["source"] for row in claims)
    ingestion = {
        "schema": "CORE16X_FULL_PARENT_CLAIM_INGESTION_V1",
        "created_utc": utc(),
        "method": {
            "schema_aware": True,
            "containers_are_discovered_recursively": True,
            "recognized_examples": ["claims", "baseline_claims", "expansion_claims", "canonical_gold_claims", "claim-like dicts"],
            "classification_counts_are_nonexclusive_facets_except_polarity": True,
            "deduplication": "same source + file + record hash + claim id",
            "large_raw_json_policy": f"Non-claim-named JSON over {MAX_JSON_BYTES} bytes is inventoried as skipped raw telemetry; claim-named files are still parsed.",
        },
        "sources": source_reports,
        "source_count": len(source_reports),
        "claims_before_deduplication": len(normalized),
        "claims_after_deduplication": len(claims),
        "claims_by_source_after_deduplication": dict(sorted(by_source.items())),
        "container_path_terminal_frequencies": dict(global_container_types.most_common()),
        "coverage_pass": all(report["claims"] > 0 for report in source_reports),
        "coverage_failures": [report["source"] for report in source_reports if report["claims"] == 0],
        "normalized_claims": claims,
    }
    write_json(ROOT / "FULL_PARENT_CLAIM_INGESTION.json", ingestion)

    id_map = defaultdict(list)
    for row in claims:
        id_map[row["claim_id"]].append(row["uid"])
    edges = []
    for row in claims:
        edges.append({"from": row["uid"], "to": row["source"], "relation": "EVIDENCED_IN"})
        if len(id_map[row["claim_id"]]) > 1:
            for other in id_map[row["claim_id"]]:
                if other != row["uid"]:
                    edges.append({"from": row["uid"], "to": other, "relation": "SHARES_REPORTED_CLAIM_ID"})
        blob = text_blob(row["record_excerpt"])
        for relation, pattern in (("REFINES", r"REFINES[_ ]?(C\d+[A-Z]?\d+|CORE\d+)"), ("CONTRADICTS", r"CONTRADICTS[_ ]?(C\d+[A-Z]?\d+|CORE\d+)")):
            for target in re.findall(pattern, blob, flags=re.IGNORECASE):
                edges.append({"from": row["uid"], "to": target, "relation": relation})
    claim_graph = {
        "schema": "CORE01_16_COMPLETE_CLAIM_GRAPH_V1",
        "created_utc": utc(),
        "premise": "P0_FIXED",
        "source_nodes": sorted(by_source),
        "claim_nodes": [{k: row[k] for k in ("uid", "source", "claim_id", "statement", "reported_status", "facets", "mechanisms", "record_sha256")} for row in claims],
        "edges": edges,
        "claim_count": len(claims),
        "coverage_pass": ingestion["coverage_pass"],
    }
    write_json(ROOT / "CORE01_16_COMPLETE_CLAIM_GRAPH.json", claim_graph)

    mechanism_claims = defaultdict(list)
    cooccurrence = Counter()
    for row in claims:
        for mechanism in row["mechanisms"]:
            mechanism_claims[mechanism].append(row["uid"])
        for i, left in enumerate(row["mechanisms"]):
            for right in row["mechanisms"][i + 1:]:
                cooccurrence[(left, right)] += 1
    mechanism_graph = {
        "schema": "CORE01_16_COMPLETE_MECHANISM_GRAPH_V1",
        "created_utc": utc(),
        "nodes": [{"mechanism": name, "claim_count": len(uids), "claim_uids": uids} for name, uids in sorted(mechanism_claims.items())],
        "edges": [{"from": pair[0], "to": pair[1], "relation": "CO_OCCURS_IN_CLAIM", "claim_count": count} for pair, count in sorted(cooccurrence.items())],
        "unmapped_claim_count": sum(1 for row in claims if not row["mechanisms"]),
        "interpretation_rule": "Keyword grouping is an auditable retrieval index, not proof that mechanisms are identical.",
    }
    write_json(ROOT / "CORE01_16_COMPLETE_MECHANISM_GRAPH.json", mechanism_graph)

    append_ndjson(ROOT / "QUESTION_TREE.ndjson", {
        "question_id": "C16X-Q001",
        "parent_id": "C16X-Q000",
        "parent_result_hash": canonical_hash({"coverage_pass": ingestion["coverage_pass"], "counts": dict(by_source)}),
        "what_was_learned": f"Schema-aware ingestion found {len(claims)} deduplicated claim records across {len(source_reports)} sources.",
        "new_uncertainty": "Do the newly restored mechanism/claim families require splitting, merging, or adding effective levels beyond baseline E1/E2/E3?",
        "competing_interpretations": ["E1/E2/E3 remain sufficient", "history/functional mechanisms require a parallel level", "destination/phase mechanisms require split causal levels"],
        "why_next_experiment_matters": "Effective-level reconstruction is invalid until all restored claims are mapped to causal information requirements.",
        "status": "OPEN" if ingestion["coverage_pass"] else "BLOCKED_BY_COVERAGE",
    })
    append_ndjson(ROOT / "KERNEL_DIALOGUE.ndjson", {
        "question_id": "C16X-Q001",
        "raw_outcome": {"claims": len(claims), "sources": len(source_reports), "coverage_pass": ingestion["coverage_pass"], "failures": ingestion["coverage_failures"]},
        "mechanism_update": "The previous zero-parent-claim result was an ingestion artifact, not a scientific null.",
        "next_high_information_question": "Map restored claim mechanisms to state coordinates, observers, and predictive tasks before level selection.",
    })
    checkpoints = ["BASELINE_AUDIT", "FULL_PARENT_CLAIM_INGESTION"] if ingestion["coverage_pass"] else ["BASELINE_AUDIT"]
    update_state(
        status="PARENT_CLAIMS_INGESTED" if ingestion["coverage_pass"] else "PARENT_INGESTION_REQUIRES_REPAIR",
        current_phase="FULL_STATE_CAUSAL_AUDIT" if ingestion["coverage_pass"] else "PARENT_INGESTION_REPAIR",
        parent_claims_ingested=len(claims),
        parent_sources_ingested=len(source_reports),
        parent_claim_coverage_pass=ingestion["coverage_pass"],
        completed_checkpoints=checkpoints,
    )
    print(json.dumps({"sources": len(source_reports), "claims": len(claims), "coverage_pass": ingestion["coverage_pass"], "by_source": dict(sorted(by_source.items()))}, indent=2))


if __name__ == "__main__":
    main()

