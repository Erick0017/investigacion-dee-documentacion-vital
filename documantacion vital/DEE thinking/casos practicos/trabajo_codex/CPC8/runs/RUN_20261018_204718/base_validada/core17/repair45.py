"""CORE17 carrier-supported redundant repair, adapted to installed DEE4.5.

No legacy engine, archived output or target map is imported. Exact replay uses
explicit diagnostic input forks to retain historical input clocks. The optional
channel arm instead uses real Runtime input receipts and clock0. Both are separate
diagnostic cohorts, never the CPC8 E1 MAIN and never autonomous regeneration.
"""
from array import array
from pathlib import Path
import hashlib
import json

import dee_thinking as d

A = (1, 0, 0)
B = (0, 1, 0)
SENSOR = (-1, 0, 1)
NORMALIZER = (1, 0, -1)
PENALTY0 = (-1, 1, 0)
ACTION1 = (-1, 1, 1)


def add(q, direction, distance, n):
    return tuple((q[i] + distance * direction[i]) % n for i in range(3))


def neg(direction):
    return tuple(-v for v in direction)


def transform(value, permutation, signs):
    return tuple(signs[i] * value[permutation[i]] for i in range(3))


def pack(state, load, direction, semantic=1):
    return int(d.pack_record(state, load, *direction, semantic))


def record(runtime, q):
    o = runtime.observe(d.Coordinate(*q))
    if o.raw == 0:
        return None
    r = o.record
    return {"raw": str(o.raw), "clock": str(o.clock), "state": int(r.state),
            "sreg": int(r.s_reg), "direction": [r.dx, r.dy, r.dz], "semantic": int(r.semantic)}


def physical(runtime):
    raw = array("Q", runtime.raw_copy())
    clocks = array("Q", runtime.clock_copy())
    return {"tick": int(runtime.current_tick), "RAW_sha256": hashlib.sha256(raw.tobytes()).hexdigest(),
            "clocks_sha256": hashlib.sha256(clocks.tobytes()).hexdigest()}


def receipt(r):
    return {"id": str(r.id), "status": str(r.status), "requested_tick": str(r.requested_tick),
            "effective_tick": None if r.effective_tick is None else str(r.effective_tick),
            "channels": list(r.channels), "reason": r.reason}


class RepairWorld:
    def __init__(self, config):
        self.config = config
        self.n = config["n"]
        self.ledger = []
        self.channel_ids = []
        self.diagnostic_forks = 0
        n = self.n
        raw, clocks = [0] * n**3, [0] * n**3
        a = transform(A, config["permutation"], config["signs"])
        for j, q in enumerate((config["source1"], config["source2"])):
            index = d.linear_index(*q, n)
            raw[index] = pack(610000 + config["seed"] + j, 7 + j, a)
            clocks[index] = 710000 + config["seed"] + j
        self.runtime = d.Runtime.import_research_state(n, 0, raw, clocks)
        self.runtime.execution_options = d.TickOptions(d.Backend.LAZY, 1)

    def edit(self, rows, reason):
        before = physical(self.runtime)
        edits, log = [], []
        for q, raw, clock in rows:
            prior = self.runtime.observe(d.Coordinate(*q))
            e = d.ResearchStateEdit()
            e.coordinate = d.Coordinate(*q)
            e.raw = int(raw)
            e.clock = None if clock is None else int(clock)
            e.label = reason
            edits.append(e)
            log.append({"site": list(q), "RAW_before": str(prior.raw), "RAW_after": str(raw),
                        "clock_before": str(prior.clock), "clock_after": str(prior.clock if clock is None else clock)})
        child = self.runtime.diagnostic_fork(edits, True)
        assert physical(self.runtime) == before, "Diagnostic edit mutated parent"
        self.runtime = child
        self.diagnostic_forks += 1
        self.ledger.append({"kind": "DIAGNOSTIC_FORK", "reason": reason, "parent_physical": before,
                            "post_physical": physical(child), "parent_unchanged": True, "edits": log})

    def arrivals(self, arrivals):
        if not arrivals:
            return
        rows = []
        for target, direction, load, state, clock in arrivals:
            port = add(target, direction, -1, self.n)
            prior = self.runtime.observe(d.Coordinate(*port))
            if prior.raw:
                raise RuntimeError("Historical input port occupied: " + str(port))
            if self.config["input_mode"] == "exact_diagnostic":
                rows.append((port, pack(state, load, direction), clock))
            else:
                channel = d.ChannelSpec()
                channel.name = "legacy_input_" + str(len(self.channel_ids))
                channel.injection_site = d.Coordinate(*port)
                channel.state = state
                channel.direction = d.Direction(*direction)
                channel.semantic = 1
                self.runtime.register_channel(channel)
                r = self.runtime.experience(channel.name, self.runtime.current_tick, load)
                self.channel_ids.append(r.id)
                self.ledger.append({"kind": "EXPERIENCE_PROTOCOL", "original_clock": str(clock),
                                    "actual_input_clock": "0", "state": state, "payload": load,
                                    "direction": list(direction), "site": list(port), "receipt_scheduled": receipt(r)})
        if rows:
            self.edit(rows, "Historical external experience with exact legacy clock; diagnostic replay only")


def run_case(config, out):
    out = Path(out)
    out.mkdir(parents=True, exist_ok=False)
    world = RepairWorld(config)
    n, seed, mode = config["n"], config["seed"], config["mode"]
    p, signs = config["permutation"], config["signs"]
    a, b, sensor, normalizer, penalty0, action1 = [transform(v, p, signs) for v in (A, B, SENSOR, NORMALIZER, PENALTY0, ACTION1)]
    relay1, relay2 = [transform(v, p, signs) for v in ((1, -1, 1), (-1, -1, 1))]
    route1, route2 = [tuple(v[i] + b[i] for i in range(3)) for v in (relay1, relay2)]
    receiver = tuple(config["receiver"])
    sources = [tuple(config["source1"]), tuple(config["source2"])]
    learned, launch1, launch2 = 2*n, 3*n, 5*n
    arrival1, arrival2 = launch1 + config["d1"], launch2 + config["d2"]
    damage_tick, query_tick = arrival1 + 1, arrival2 + n
    windows, observations, snapshots = [], {}, []

    def checkpoint(label):
        rt = world.runtime
        path = out / (label + ".deetsnap")
        rt.save_snapshot(str(path))
        snapshots.append({"label": label, "path": path.name, "sha256": hashlib.sha256(path.read_bytes()).hexdigest(), "physical": physical(rt)})

    checkpoint("T0")
    first_arrival = second_arrival = backup_after_learning = None
    damaged = None
    for current in range(query_tick):
        assert world.runtime.current_tick == current
        t = current + 1
        inputs = []
        if t == n:
            inputs += [(source, sensor, 47+j, 720000+seed+j, 730000+seed+j) for j, source in enumerate(sources)]
        if t == learned:
            for j, source in enumerate(sources):
                inputs.append((source, normalizer, 53+j, 740000+seed+j, 750000+seed+j))
                if j == 0 or mode != "backup_untrained":
                    inputs.append((source, penalty0, 59+j, 760000+seed+j, 770000+seed+j))
        if t == launch1:
            inputs.append((sources[0], relay1, 61, 780000+seed, 790000+seed))
        if t == arrival1:
            inputs.append((receiver, neg(relay1), 71, 800000+seed, 810000+seed))
        if t == launch2 and mode != "no_backup":
            inputs.append((sources[1], relay2, 67, 820000+seed, 830000+seed))
        if t == launch2 + max(2, config["d2"]//2) and mode in ("path_cut", "offpath_cut"):
            target = add(sources[1], route2, max(2, config["d2"]//2), n)
            if mode == "offpath_cut":
                target = add(target, transform((0,0,5), p, signs), 1, n)
            inputs.append((target, neg(route2), 73, 840000+seed, 850000+seed))
        if t == arrival2 and mode != "receiver_none":
            converter = neg(relay2) if mode != "wrong_receiver" else neg(b)
            inputs.append((receiver, converter, 79, 860000+seed, 870000+seed))
        if t == query_tick:
            inputs.append((receiver, sensor, 101, 880000+seed, 890000+seed))
        world.arrivals(inputs)
        if t in (arrival1, arrival2, query_tick):
            windows.append({"phase": "BEFORE_NATIVE_TICK", "tick": current,
                            "receiver": record(world.runtime, receiver), "physical": physical(world.runtime)})
        world.runtime.advance(1)
        if t == learned:
            backup_after_learning = record(world.runtime, sources[1])
            if mode == "backup_direction_reset" and backup_after_learning:
                r = backup_after_learning
                world.edit([(sources[1], pack(r["state"],r["sreg"],a,r["semantic"]),None)], "Diagnostic backup learned-direction reset; clock preserved")
            elif mode == "no_backup":
                world.edit([(sources[1],0,0)], "Diagnostic removal of redundant learned source; explicit RAW/clock damage")
            checkpoint("T"+str(t)+"_learned")
        if t == arrival1:
            first_arrival = record(world.runtime, receiver)
            checkpoint("T"+str(t)+"_before_damage")
        if t == damage_tick:
            damaged = add(receiver, b, 1, n)
            before = record(world.runtime, damaged)
            world.edit([(damaged,0,0)], "Authorized finite diagnostic damage of first transferred policy; not E1 MAIN")
            observations["damage"] = {"tick":t,"site":list(damaged),"before":before,"after":record(world.runtime,damaged)}
            checkpoint("T"+str(t)+"_damaged")
        if t == arrival2:
            second_arrival = record(world.runtime, receiver)
            checkpoint("T"+str(t)+"_repair_arrival")
        if t in (arrival1, arrival2, query_tick):
            windows.append({"phase":"AFTER_NATIVE_TICK","tick":t,"receiver":record(world.runtime,receiver),"physical":physical(world.runtime)})
    query = record(world.runtime, receiver)
    checkpoint("T"+str(query_tick)+"_query")
    query_raw = world.runtime.raw_copy()
    query_xor = 0
    for value in query_raw:
        if value:
            query_xor ^= int(d.decode_record(value).state)
    final_at_query = {"support":sum(bool(value) for value in query_raw),
                      "sreg_total":sum(int(d.decode_record(value).s_reg) for value in query_raw if value),
                      "state_xor":query_xor,"physical":physical(world.runtime)}
    # Validation consumer only: save/load continuation has no teaching map.
    restored = d.Runtime.load_snapshot(str(out/snapshots[-1]["path"]))
    restored.execution_options = d.TickOptions(d.Backend.LAZY,1)
    assert physical(restored) == physical(world.runtime)
    restored.advance(1)
    world.runtime.advance(1)
    continuation_equal = physical(restored) == physical(world.runtime)
    assert continuation_equal
    raw = world.runtime.raw_copy()
    total = sum(int(d.decode_record(value).s_reg) for value in raw if value)
    sxor = 0
    for value in raw:
        if value:
            sxor ^= int(d.decode_record(value).state)
    result = {"schema":"CPC8.CORE17.repair45.case.v1","case_id":config["case_id"],"config":config,
        "modality":"DIAGNOSTIC_REPLAY" if config["input_mode"]=="exact_diagnostic" else "CHANNEL_EXPERIENCE_WITH_DIAGNOSTIC_DAMAGE",
        "no_E1_MAIN_relation":True,"input_clock_contract":"exact legacy clocks via explicit diagnostic forks" if config["input_mode"]=="exact_diagnostic" else "standard Runtime channel inputs use clock0; not physically identical legacy input contract",
        "first_arrival":first_arrival,"second_arrival":second_arrival,"backup_after_learning":backup_after_learning,
        "query":query,"events":observations,"local_windows":windows,"ledger":world.ledger,
        "final_at_query":final_at_query,
        "final_receipts":[receipt(world.runtime.receipt(i)) for i in world.channel_ids],"diagnostic_forks":world.diagnostic_forks,
        "snapshots":snapshots,"continuation_same_after_save_load":continuation_equal,
        "reconstructed_policy_at_arrival":second_arrival is not None and tuple(second_arrival["direction"])==b,
        "fresh_function_after_reconstruction":query is not None and tuple(query["direction"])==action1,
        "source1_depleted":record(world.runtime,sources[0]) is None,"source2_depleted":record(world.runtime,sources[1]) is None,
        "final_after_extra_validation_tick":{"support":sum(bool(x) for x in raw),"sreg_total":total,"state_xor":sxor,"physical":physical(world.runtime)},
        "scope":"Carrier-mediated reconstruction from an acquired redundant source; externally prepared resources/relay/converter and authorized damage, not autonomous local regeneration."}
    (out/"MEASUREMENTS.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    return result
