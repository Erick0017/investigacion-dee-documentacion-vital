"""Recalculate EO01 auxiliary post-execution feedback trials, stdlib, zero ticks."""
from pathlib import Path
from collections import Counter
import argparse
import gzip
import hashlib
import json


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def walk(x):
    if isinstance(x, dict):
        yield x
        for q in x.values():
            yield from walk(q)
    elif isinstance(x, list):
        for q in x:
            yield from walk(q)


def exact(q):
    assert isinstance(q["raw"], str) and q["raw"].isdecimal()
    assert isinstance(q["clock"], str) and q["clock"].isdecimal()
    v = int(q["raw"]); assert 0 <= v < 2**64
    def signed(k):
        n = (v >> k) & 15
        return n - 16 if n & 8 else n
    fields = {"state": v & 0xffffffff, "s_reg": (v >> 32) & 65535,
              "semantic": (v >> 60) & 15, "direction": [signed(k) for k in (48, 52, 56)]}
    assert all(q[k] == value for k, value in fields.items())


def decode(n):
    c = n["plan"]["critical_tick"]; samples = []
    for tick in (c-16, c-15):
        f = next(q for q in n["frames"] if q["tick"] == tick)
        roles = [r for r in (-1,0,1) if f["contacts"][str(r)]["state"] > 0
                 and f["contacts"][str(r)]["semantic"] == 1
                 and f["contacts"][str(r)]["direction"] in ([r,-1,-1],[r,-1,0])]
        samples.append({"tick": tick, "material_roles": roles,
                        "command": (1 if roles[0] >= 0 else -1) if len(roles) == 1 else None,
                        "simultaneous_conflict": len(roles)>1})
    chosen = None if samples[-1]["simultaneous_conflict"] else next((q for q in reversed(samples) if q["command"] is not None),None)
    reason = "deadline_conflict" if samples[-1]["simultaneous_conflict"] else "no_native_output" if chosen is None else "current" if chosen["tick"]==c-15 else "fixed_hold_one_tick"
    return {"rule":"latest_unique_with_max_hold1tick.v1","samples":samples,"command":None if chosen is None else chosen["command"],
            "source_tick":None if chosen is None else chosen["tick"],"reason":reason}


def loads(w,key):
    return [q["s_reg"] for q in w[key]]


def inspect(path):
    with gzip.open(path,"rt",encoding="utf8") as f:
        d = json.load(f)
    n = d["result"]["result"]
    checked = 0
    for q in walk(n):
        if all(k in q for k in ("raw","clock","state","s_reg","semantic","direction")):
            exact(q); checked += 1
    reader = decode(n); assert reader == n["decoder"]
    env = n["environment"]
    chosen = next((q for q in reader["samples"] if q["tick"]==reader["source_tick"]),None)
    posture = None if chosen is None else chosen["material_roles"][0]
    assert posture == env["emitted_posture"]
    assert reader["command"] == env["emitted_command"]
    assert env["moved"] == (env["executed_command"] is not None)
    assert env["observed_closed_gate_contact"] == bool(env["moved"] and env["executed_command"] != env["available_gate_not_injected"])
    assert env["job_completed"] == bool(env["moved"] and env["executed_command"] == env["available_gate_not_injected"])
    assert n["plan"]["all_j0_sources_omitted"]
    u = n["plan"]["decision_deadline"]
    assert env["observation_tick"] == u
    assert all(int(q["name"].rsplit(".",2)[1]) > 0 for q in n["plan"]["supplies"])
    receipts = {}
    for request in n["requests"]:
        r = request["receipt"]
        assert r["id"] == request["id"] and r["requested_tick"] == request["tick"]
        if r["id"] in receipts:
            assert receipts[r["id"]] == r
        receipts[r["id"]] = r
        if ".tactile." in request["port"]:
            assert request["tick"] > env["observation_tick"]
    all_w = [n["before"],*n["frames"],n["after"]]
    before, after = loads(n["before"],"own"), loads(n["after"],"own")
    active_role = n["tactile_role_returned"]
    route = []
    if active_role is not None:
        expected = {0:([1,0,1],[-1,1,0],[0,0,-1]),
                    -1:([0,1,1],[1,0,0],[0,1,0]),
                    1:([0,1,1],[-1,0,0],[0,1,0])}[active_role]
        for j, direction in enumerate(expected,1):
            candidates = [f["return_heads"][str(active_role)][j] for f in n["frames"]
                          if f["tick"]>u and f["return_heads"][str(active_role)][j]["state"]>0
                          and f["return_heads"][str(active_role)][j]["direction"]==direction]
            route.append({"stage":j,"first_expected_direction_observation":candidates[0] if candidates else None,
                          "scope":"Observed compatible waypoint, not invented unique particle identity."})
    return {"case":path.name.removesuffix(".json.gz"),"source":str(path),"bytes":path.stat().st_size,"sha256":sha(path),
      "executed_source_sha256":d.get("source_sha256"),"frozen_episode_source_sha256":d.get("frozen_episode_source_sha256",d.get("source_sha256")),
      "revision":n["revision"],"initial_tick":n["before"]["tick"],"final_tick":n["after"]["tick"],"decoder":reader,
      "environment":env,"own_before":before,"own_after":after,"delta_before":before[0]-before[1],"delta_after":after[0]-after[1],
      "context_before":loads(n["before"],"context_A"),"context_after":loads(n["after"],"context_A"),
      "context_7_5_preserved_in_samples":all(loads(w,"context_A")==[7,5] for w in all_w),
      "B_private_61_19_preserved_in_samples":all(loads(w,"private_B")==[61,19] for w in all_w),
      "tactile_role_returned":active_role,"receipt_statuses":dict(Counter(r["status"] for r in receipts.values())),
      "requests":n["requests"],"compatible_return_waypoints":route,"exact_observations_checked":checked,
      "physical_endpoint":d["result"]["physical"]}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--evidence",required=True,type=Path);p.add_argument("--out",required=True,type=Path)
    a = p.parse_args()
    rows = [inspect(path) for path in sorted(a.evidence.glob("EO01_AUX_*.json.gz"))]
    result = {"schema":"EO01.auxiliary_real_result.recalculation.v1","new_native_ticks":0,"cases":rows,
      "files_checked":len(rows),"exact_observations_checked":sum(q["exact_observations_checked"]for q in rows),
      "limits":["Auxiliary lineages are forks of the same parent, not independent learners or MAIN experiences.",
                "Two sampled roles0/+ share the left command but retain distinct mechanical postures and return paths.",
                "R01 role0 received/transformed its tactile input yet did not change own relative fields. The R02 timing revision is external engineering, not learned route selection.",
                "First response in a common opportunity tests prior history; that opportunity's own feedback can then teach and change final fields.",
                "No old j0 feedback is submitted; downstream resources are fixed in every arm. The environment/codec does not calculate the desired next action or target memory."]}
    a.out.write_text(json.dumps(result,ensure_ascii=False,indent=2,allow_nan=False)+"\n",encoding="utf8")
    print(json.dumps({"out":str(a.out),"sha256":sha(a.out),"files":len(rows),"observations":result["exact_observations_checked"],
                      "rows":[{"case":q["case"],"command":q["environment"]["emitted_command"],"contact":q["environment"]["observed_closed_gate_contact"],"completed":q["environment"]["job_completed"],"delta":[q["delta_before"],q["delta_after"]],"receipts":q["receipt_statuses"]}for q in rows]},ensure_ascii=False))


if __name__ == "__main__":
    main()
