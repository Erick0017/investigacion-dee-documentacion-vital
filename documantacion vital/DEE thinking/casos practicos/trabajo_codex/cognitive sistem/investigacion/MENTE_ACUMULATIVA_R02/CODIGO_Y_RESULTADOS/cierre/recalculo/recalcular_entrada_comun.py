"""Independent archived calculation for MA02 common-access R01/R03B.

Standard library only. Never imports DEE, loads a live world, or advances ticks.
Decode fixed gate observations without a token, teacher sign, or expected answer.
Only afterwards compare the answer to the earlier acquired physical sign.
"""
from __future__ import annotations

import argparse
from collections import Counter
import gzip
import hashlib
import json
from pathlib import Path


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def raw_fields(value: str | int) -> dict:
    n = int(value)
    if not 0 <= n < 2**64:
        raise ValueError("RAW outside exact uint64")
    def signed(x):
        return x - 16 if x >= 8 else x
    return {"state": n & 0xffffffff, "s_reg": (n >> 32) & 65535,
            "semantic": (n >> 60) & 15,
            "direction": [signed((n >> s) & 15) for s in (48, 52, 56)]}


def pure_z(observation: dict) -> int | None:
    p = raw_fields(observation["raw"])
    if p["state"] > 0 and p["semantic"] == 1 and p["direction"][:2] == [0, 0] and p["direction"][2] in (-1, 1):
        return p["direction"][2]
    return None


def decode(panel: list[dict], gate_sites: list[tuple], site_signs=None) -> dict:
    """No token/history/expected sign argument: all eight fixed sites required."""
    if sorted(tuple(o["site"]) for o in panel) != sorted(gate_sites):
        raise ValueError("Incomplete, duplicated, or changed fixed gate panel")
    found = [{"site": o["site"], "sign": pure_z(o),
              "s_reg": raw_fields(o["raw"])["s_reg"]}
             for o in panel if pure_z(o) is not None
             and (site_signs is None or pure_z(o)==site_signs[tuple(o['site'])])]
    return {"candidates": found, "decoded_sign": found[0]["sign"] if len(found) == 1 else None}


class Audit:
    def __init__(self, root):
        self.root = root
        self.sources = []
        self.issues = []
        self.observations = 0

    def load(self, name):
        data = (self.root / name).read_bytes()
        self.sources.append({"file": name, "bytes": len(data), "sha256": sha(data)})
        return json.loads(gzip.decompress(data) if name.endswith(".gz") else data)

    def check_observation(self, o, where):
        self.observations += 1
        fields = raw_fields(o["raw"])
        for key, value in fields.items():
            if o.get(key) != value:
                self.issues.append({"where": where, "field": key, "from_raw": value, "recorded": o.get(key)})
        clock = int(o["clock"])
        if not 0 <= clock < 2**64:
            self.issues.append({"where": where, "field": "clock", "issue": "outside uint64"})


def geometry(x):
    n = int(x["geometry"]["N"])
    origin = x["geometry"]["common_input"]
    vectors = x["geometry"]["token_directions"]
    def site(v, k, z=0):
        return tuple((origin[j] + k*v[j] + (z if j == 2 else 0)) % n for j in range(3))
    return n, origin, vectors, site


def receipt_summary(receipts):
    statuses = Counter(r["receipt"]["status"] for r in receipts)
    applied = statuses.get("applied", 0)
    rejected = sum(v for k, v in statuses.items() if k.startswith("rejected"))
    return {"requested": len(receipts), "applied": applied, "rejected": rejected,
            "pending_or_other": len(receipts)-applied-rejected, "statuses": dict(sorted(statuses.items()))}


def analyze_restoration(audit, name, inherited=None):
    x = audit.load(name)
    n, origin, vectors, site = geometry(x)
    gates = [site(v, 4, s) for v in vectors for s in (-1, 1)]
    histories = dict(inherited or {})
    results = []
    receipts = x["receipts"]
    ids = [r["id"] for r in receipts]
    if len(set(ids)) != len(ids):
        audit.issues.append({"file": name, "issue": "duplicate receipt IDs"})
    for r in receipts:
        rr = r["receipt"]
        if rr["id"] != r["id"] or rr["requested_tick"] != r["tick"]:
            audit.issues.append({"file": name, "issue": "receipt/request mismatch", "id": r["id"]})
        if rr["status"] == "applied" and rr["effective_tick"] != r["tick"]:
            audit.issues.append({"file": name, "issue": "unexpected delayed application", "id": r["id"]})
    teach_rows = []
    for index, row in enumerate(x["rows"]):
        if row["kind"] in ("teach", "revision"):
            audit.check_observation(row["hub"], name+":teach"+str(index))
            sign = pure_z(row["hub"])
            token = row.get("i", row.get("bank"))
            taught_sign = row.get("sign", row.get("new_signal"))
            # An unsuccessful revision must not redefine its own success target.
            # This value is only an auditor score, never an input to decode().
            histories[token] = taught_sign
            teach_rows.append({"kind":row["kind"], "token": token, "tick": row["tick"],
                               "physical_sign": sign, "teacher_sign_for_scoring_only":taught_sign,
                               "mode":row.get("mode"),
                               "s_reg": raw_fields(row["hub"]["raw"])["s_reg"]})
            if row["kind"] == "teach" and sign != taught_sign:
                audit.issues.append({"file": name, "issue": "teaching observation differs from teacher sign", "row": index})
            continue
        t = row["input_tick"]
        panel = row["fixed_panel"]
        for o in panel:
            audit.check_observation(o, name+":panel@"+str(t))
        decoded = decode(panel, gates, {site(v,4,s):s for v in vectors for s in(-1,1)})
        if row["read_tick"] != t+4 or any(o["tick"] != t+4 for o in panel):
            audit.issues.append({"file": name, "issue": "changed read window", "tick": t})
        if decoded["decoded_sign"] != row["decoded_sign"]:
            audit.issues.append({"file": name, "issue": "recorded decoder differs", "tick": t})
        recorded_candidates = [{"site": c["site"], "sign": c["sign"]} for c in decoded["candidates"]]
        if recorded_candidates != row["candidates"]:
            audit.issues.append({"file": name, "issue": "recorded candidates differ", "tick": t})
        frames = {}
        for frame in row["frames"]:
            frames[frame["tick"]] = {tuple(o["site"]): o for o in frame["sites"]}
            for o in frame["sites"]:
                audit.check_observation(o, name+":frame@"+str(frame["tick"]))
        if sorted(frames) != list(range(t, t+8)):
            audit.issues.append({"file": name, "issue": "missing frame", "tick": t})
        for o in panel:
            f = frames[t+4].get(tuple(o["site"]))
            if not f or (f["raw"], f["clock"]) != (o["raw"], o["clock"]):
                audit.issues.append({"file": name, "issue": "panel/frame mismatch", "tick": t})
        # Independent geometric witness. Its selected branch is the observed
        # physical output; the previously acquired sign is used for scoring only.
        witness = []
        if decoded["decoded_sign"] is not None:
            sign = decoded["decoded_sign"]
            out_site = tuple(decoded["candidates"][0]["site"])
            matches = [v for v in vectors if site(v, 4, sign) == out_site]
            if len(matches) == 1:
                v = matches[0]
                for dt, k, z in [(0, 3, -3), (1, 3, -2), (2, 3, -1),
                                  (3, 3, 0), (4, 4, 1), (5, 4, 2), (6, 3, 3), (7, 3, 4)]:
                    pos = site(v, k, z*sign)
                    o = frames[t+dt].get(pos)
                    witness.append({"offset": dt, "site": list(pos),
                                    "raw": o["raw"] if o else None,
                                    "clock": o["clock"] if o else None,
                                    **(raw_fields(o["raw"]) if o else {})})
        q_receipts = [r for r in receipts if t <= r["tick"] <= t+7]
        generic = [r for r in q_receipts if r["name"].startswith("generic.")]
        expected_per_sign = 3 if row["restoration"] else 1
        expected_generic = 2*expected_per_sign if row["markers"] else 0
        prepared = all(r["value"] == 7 for r in generic) and len(generic) == expected_generic
        signs_present = sorted(int(r["name"].rsplit(".", 1)[-1]) for r in generic)
        expected_signs = [-1]*expected_per_sign+[1]*expected_per_sign if row["markers"] else []
        prepared = prepared and signs_present == expected_signs
        if not prepared or any(r["name"].startswith("experience.") for r in q_receipts):
            audit.issues.append({"file": name, "issue": "query resources not symmetric/non-teaching", "tick": t})
        expected = histories.get(row["request_token"])
        answer = decoded["decoded_sign"]
        requested_route_match = (len(decoded["candidates"]) == 1 and
                                 tuple(decoded["candidates"][0]["site"]) == site(vectors[row["request_token"]],4,answer))
        results.append({"input_tick": t, "read_tick": t+4, "token_for_scoring_only": row["request_token"],
                        "request":row["request"], "markers":row["markers"], "restoration":row["restoration"],
                        "expected_sign_for_external_scoring": expected, **decoded,
                        "output_site_matches_requested_route_diagnostic_only":requested_route_match,
                        "correct": answer is not None and answer == expected,
                        "receipts": receipt_summary(q_receipts),
                        "symmetric_generic_resources": prepared,
                        "observed_excursion": witness})
    # Describe the actual observed load/direction sequence, without inventing
    # unique carrier identity from equal loads or asserting full causal coverage.
    excursions = []
    for q in results:
        w = q["observed_excursion"]
        physical = bool(len(w) == 8 and all("direction" in o for o in w))
        if physical:
            sign = q["decoded_sign"]
            # At q+3 nonzero XY, q+4 pure Z, q+5 inverse XY, q+6 pure Z.
            a, b, c, d = w[3], w[4], w[5], w[6]
            physical = (a["direction"][2] == sign and a["direction"][:2] != [0,0]
                        and b["direction"] == [0,0,sign]
                        and c["direction"][:2] == [-v for v in a["direction"][:2]]
                        and c["direction"][2] == sign and d["direction"] == [0,0,sign]
                        and [b["s_reg"]-a["s_reg"], c["s_reg"]-b["s_reg"], d["s_reg"]-c["s_reg"]] == [7,7,7]
                        and a["s_reg"]-w[0]["s_reg"] == 5)
        excursions.append({"tick": q["input_tick"], "observed_geometry_and_addends_match": physical})
    return {"file": name, "label": x["label"], "N": n, "origin": origin,
            "vectors": vectors, "fixed_gate_sites": [list(p) for p in gates],
            "teach_observations": teach_rows, "queries": results,
            "summary": {"observation_opportunities":len(results),
                        "requested_queries": sum(q["request"] for q in results),
                        "responded": sum(q["decoded_sign"] is not None for q in results),
                        "correct": sum(q["correct"] for q in results),
                        "incorrect": sum(q["decoded_sign"] is not None and not q["correct"] for q in results),
                        "abstentions_or_ambiguous": sum(q["decoded_sign"] is None for q in results),
                        **({"before_fourth_acquisition": sum(q["correct"] for q in results[:6]),
                            "after_fourth_acquisition": sum(q["correct"] for q in results[6:])} if inherited is None else {}),
                        "receipts": receipt_summary(receipts)},
            "new_receipts_after_parent": receipt_summary([r for r in receipts if r["tick"] > x["initial"]["tick"]]) if inherited is not None else receipt_summary(receipts),
            "excursion_witnesses": excursions,
            "rejected_inputs": [{k:r[k] for k in ("id","name","site","direction","value","tick","receipt")}
                                for r in receipts if r["receipt"]["status"].startswith("rejected")],
            "initial_snapshot_reference": {k:x["initial"][k] for k in ("bytes","sha256","tick","source_life") if k in x["initial"]},
            "final_snapshot_reference": {k:x["final"][k] for k in ("bytes","sha256")}}


def analyze_coincidence(audit, name):
    x = audit.load(name)
    _, _, vectors, site = geometry(x)
    gates = [site(v, 4, sign) for v in vectors for sign in (-1,1)]
    rows = []
    for frame in x["frames"]:
        for o in frame["sites"]:
            audit.check_observation(o, name+":frame@"+str(frame["tick"]))
        by_site = {tuple(o["site"]):o for o in frame["sites"]}
        rows.append({"tick":frame["tick"], **decode([by_site[p] for p in gates],gates,
                    {site(v,4,s):s for v in vectors for s in(-1,1)})})
    q = x["pre_query"]
    # R01 fixed protocol queries at T67; no sign-dependent window selection.
    return {"file":name,"factors_for_auditor_only":x["factors"],
            "reader_retrospective_not_reserved":True,
            "q_plus_4":next(r for r in rows if r["tick"] == 71),
            "all_observed_gate_frames":rows, "receipts":receipt_summary(x["receipts"])}


def calculate(root):
    audit = Audit(root)
    arms = [analyze_restoration(audit, "MA02_RESTAURACION_R03B_"+arm+".R02.json.gz")
            for arm in ("MAIN","OPPOSITE","NOGUARD")]
    screens = [analyze_coincidence(audit, "MA02_COINC_R01_"+arm+".traza.json.gz")
               for arm in ("PLUS","MINUS","NOMARK","NOQUERY","LATE")]
    inherited = {r["token"]:r["physical_sign"] for r in arms[0]["teach_observations"]}
    continuation = [analyze_restoration(audit, "MA02_R04_"+arm+".R04.json.gz", inherited)
                    for arm in ("MAIN","SINGLE_REV","REV_SHAM","QUERY_RESOURCE","NOQUERY","NOMARKERS","NORESTORE")]
    comparisons = {"opposite_history_flips_all_twelve_outputs":
                      all(a["decoded_sign"] == -b["decoded_sign"] for a,b in zip(arms[0]["queries"],arms[1]["queries"])),
                   "guard_removal_preserves_all_twelve_decoded_outputs":
                      all(a["decoded_sign"] == b["decoded_sign"] for a,b in zip(arms[0]["queries"],arms[2]["queries"])),
                   "guard_removal_changes_admission": arms[0]["summary"]["receipts"] != arms[2]["summary"]["receipts"]}
    return {"schema":"DEE.MA02.archived_common_access.v1", "new_dee_ticks":0,
            "method":"Exact uint64 RAW unpack, fixed eight-site pure-Z decoder at q+4; scoring later from historical teaching and intended revision. No engine import.",
            "sources":audit.sources, "restoration":arms, "R01_screen":screens,
            "R04_continuation":continuation,
            "comparisons":comparisons,"observations_checked":audit.observations,
            "issues":audit.issues,
            "scope_and_limits":[
                "These are three new-T0 N67 candidate lives, not continuations of inherited E1.",
                "Input token i selects a designed cue direction and matching six resource routes (P0 addressing); sign content comes from earlier physical teaching (P1).",
                "Decoder itself never takes token, teacher sign, or expected answer. The auditor uses token/history only after physical decoding to score correctness.",
                "Query emits six equal resources7, three per possible sign. It changes acquired carrier load; it is not passive observation.",
                "Eight-frame local witnesses support the stated excursion and restoration geometry; they do not prove globally unique carrier lineage or complete tick causal coverage.",
                "R01 missing-marker, missing-query and delayed-marker screens support timing-dependent conversion at the selected gate. This reader applied to R01 is retrospective exploratory analysis, not an independent reserve.",
                "R04 controls fork from the same full R03B MAIN T1012. Their summaries keep inherited cumulative receipts separate from newly submitted receipts after the parent.",
                "R04 single and sham revision can fail physically; their intended teaching sign remains the external scoring target, not redefined to match the failed output.",
                "NOGUARD preserves12/12 decoded answers throughT1012 but rejects12/92 material inputs. Guards prevent these conflicts in the matched tested window, not a demonstrated accuracy loss.",
                "No learned selection policy, P2/R2, semantic generality, social coordination, or environmental competence follows from this limited access result.",
                "Duplicate .json.gz and .R02.json.gz per arm are one experiment, never independent replications."]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--evidencia", type=Path, required=True)
    parser.add_argument("--salida", type=Path, required=True)
    args = parser.parse_args()
    result = calculate(args.evidencia)
    args.salida.parent.mkdir(parents=True,exist_ok=True)
    args.salida.write_text(json.dumps(result,ensure_ascii=False,sort_keys=True,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"outputs":str(args.salida),"issues":len(result["issues"]),
                      "observations_checked":result["observations_checked"],
                      "arms":[{"label":a["label"],**a["summary"]}for a in result["restoration"]]},ensure_ascii=False))
    return 1 if result["issues"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
