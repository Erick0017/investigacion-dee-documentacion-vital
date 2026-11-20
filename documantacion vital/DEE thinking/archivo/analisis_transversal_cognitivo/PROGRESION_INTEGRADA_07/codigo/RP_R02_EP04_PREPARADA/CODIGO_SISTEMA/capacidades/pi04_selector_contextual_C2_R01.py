"""PI04 C2 candidate sensory extension; NOT a verified capability.

Import is stdlib only. No world/session, process, state or experiment is created.
Native mutation occurs only in explicit functions called by the root owner.
The inherited PI03 banks, eligibility routes, zero convention and clocks are
never rewritten. A public exact scalar enters a prepared transient datum site.
Six fixed output classes are read, as in the existing MU.current instrument.
Compatibility with PI03 temporal credit MUST be tested before a held-out run.
"""
from __future__ import annotations

VERSION = "PI04.C2.contextual_transient_sensor.R01_CANDIDATE"
KEY = "DEE.Cognitive.PI04.contextual_transient_sensor.R01"
LIFE_KEY = "DEE.Cognitive.System.1.1.life.v1"
N = 67
ORIGIN = (19, 54, 5)
PREFIX = "PI04.C2.CURRENT.R01"
LIFE_PREFIX = "ECI02_PI03_REPRO_PI04_"
DATUM_OFFSET = (-1, 0, 1)
STOP_OFFSETS = tuple((3*x, 3, 3*z) for x in (-1, 0, 1) for z in (0, -1))
OUTPUT_OFFSETS = tuple((2*x, 2, 2*z) for x in (-1, 0, 1) for z in (0, -1))


def at(offset):
    return tuple((ORIGIN[k] + int(offset[k])) % N for k in range(3))


def geometry():
    """Fixed design, with no data value, target, answer or history arguments."""
    return {"N": N, "origin": list(ORIGIN), "datum_site": list(at(DATUM_OFFSET)),
            "stops": [list(at(p)) for p in STOP_OFFSETS],
            "outputs": [list(at(p)) for p in OUTPUT_OFFSETS],
            "query_payload": 0, "datum_relative_to_query": 3,
            "read_relative_to_query": 6,
            "scope": "Prepared sensory extension; not learned anatomy or verified coexistence."}


def _native():
    from dee_thinking import _native as d
    from dee_thinking.consolidated import exact_observation, exact_receipt
    from dee_thinking.persistence import decode_metadata, encode_metadata
    return d, exact_observation, exact_receipt, decode_metadata, encode_metadata


def _guard(a):
    d, exact_observation, exact_receipt, decode, encode = _native()
    if int(a.world.runtime.dimension) != N:
        raise ValueError("Only the inherited N67 is admitted; never resize/recreate")
    entries = dict(a.world.runtime.snapshot_metadata_entries)
    if LIFE_KEY not in entries:
        raise ValueError("Complete Cognitive identity metadata required")
    life = decode(entries[LIFE_KEY])["life_id"]
    if not life.startswith(LIFE_PREFIX):
        raise ValueError("Explicit root-owned PI04 clone only; principal/original rejected")
    return d, exact_observation, exact_receipt, decode, encode, entries, life


def preflight(a):
    """Passive current-site inspection; not a global future safety proof."""
    d, exact, _, _, _, entries, life = _guard(a)
    inert = int(d.pack_record(0, 0, 0, 0, 0, 4))
    def obs(p):
        return exact(a.world.runtime.observe(d.Coordinate(*p)))
    datum = obs(at(DATUM_OFFSET))
    stops = [{"site": list(at(p)), "physical": obs(at(p))} for p in STOP_OFFSETS]
    conflicts = [r for r in stops if int(r["physical"]["raw"]) not in (0, inert)]
    names = {PREFIX + ".datum"} | {PREFIX + ".stop." + str(j) for j in range(6)}
    reused = sorted(names.intersection(set(a.world.runtime.channel_names)))
    return {"version": VERSION, "life_id": life, "tick": int(a.tick),
            "datum": datum, "stops": stops, "conflicts": conflicts,
            "namespace_reused": reused, "already_prepared": KEY in entries,
            "eligible": int(datum["raw"]) == 0 and not conflicts and not reused and KEY not in entries,
            "scope": "RAW checked, including state=0. No cleaning, bank/clock edits or future guarantee."}


def _declare(world, d, name, site, direction, *, state=1, semantic=1):
    if name in set(world.runtime.channel_names):
        raise ValueError("Refuse reused new sensor channel: " + name)
    c = d.ChannelSpec(); c.name = name; c.injection_site = d.Coordinate(*site)
    c.direction = d.Direction(*direction); c.state = state; c.semantic = semantic
    c.allow_experience = True; c.allow_probe = False
    i = d.InterfaceSpec(); i.name = name; i.channel = c
    world.declare_interface(i)


def prepare(a):
    """Explicit legal birth of missing SEM4 output stops, not learned content.

    An existing identical SEM4 stop (e.g. the inherited OP3 zero-tail stop) is
    reused, never replaced. Any other RAW is an immediate preserved refusal.
    """
    d, exact, receipt, _, encode, _, life = _guard(a)
    check = preflight(a)
    if not check["eligible"]:
        raise ValueError("Unsafe sensory-extension preflight; preserve the current state: " + repr(check))
    inert = int(d.pack_record(0, 0, 0, 0, 0, 4)); requests = []
    tick = int(a.tick) + 2
    for j, row in enumerate(check["stops"]):
        if int(row["physical"]["raw"]) == inert:
            continue
        name = PREFIX + ".stop." + str(j)
        _declare(a.world, d, name, row["site"], (0, 0, 0), state=0, semantic=4)
        r = a.world.submit(name, 0, tick)
        requests.append({"id": int(r.id), "channel": name, "requested_tick": tick,
                         "payload": 0, "site": row["site"]})
    # No missing-data experience or reference placement is used as preparation.
    a.run_until(tick + 1)
    for r in requests:
        r["receipt"] = receipt(a.world.runtime.receipt(r["id"]))
    if any(r["receipt"]["status"] != "applied" for r in requests):
        raise ValueError("Incomplete sensor preparation; preserve failed future, no retry")
    _declare(a.world, d, PREFIX + ".datum", at(DATUM_OFFSET), (0, 0, 0))
    info = {"version": VERSION, "geometry": geometry(), "life_id": life,
            "prepared_tick": int(a.tick), "queries": 0,
            "classification": "External P0 sensor/termination preparation; no learned response installed"}
    a.world.runtime.set_snapshot_metadata(KEY, encode(info))
    return {"version": VERSION, "preflight": check, "requests": requests,
            "after_tick": int(a.tick), "geometry": geometry(), "verified_function": False}


def submit_datum(a, value, query_tick):
    """Identity scalar codec; no sign/threshold/correct-operation calculation."""
    d, _, _, decode, _, entries, _ = _guard(a)
    if KEY not in entries or decode(entries[KEY])["version"] != VERSION:
        raise ValueError("Explicit compatible prepared sensor required")
    if type(value) is not int or not 0 <= value <= 512:
        raise ValueError("One exact public scalar0..512 as MU.current; independent FI operands remain0..32")
    if type(query_tick) is not int or query_tick + 3 <= int(a.tick):
        raise ValueError("Future frozen query+3 admission boundary required")
    r = a.world.submit(PREFIX + ".datum", value, query_tick + 3)
    return {"id": int(r.id), "channel": PREFIX + ".datum", "payload": value,
            "requested_tick": query_tick + 3, "site": list(at(DATUM_OFFSET)),
            "codec": "Identity exact scalar; no action or expected result encoded"}


def read_fixed(a, query_tick):
    """All six fixed signatures at caller's frozen q+6, no data/history input.

    The caller supplies its already fixed boundary. This does not advance time,
    select a favourable window or turn NULL into an action.
    """
    d, exact, _, decode, _, entries, _ = _guard(a)
    if KEY not in entries or decode(entries[KEY])["version"] != VERSION:
        raise ValueError("Explicit compatible prepared sensor required")
    if type(query_tick) is not int or int(a.tick) != query_tick + 6:
        raise ValueError("Frozen q+6 only; no retrospective window search")
    observations = []; candidates = []
    for x in (-1, 0, 1):
        for z in (0, -1):
            site = at((2*x, 2, 2*z))
            o = exact(a.world.runtime.observe(d.Coordinate(*site)))
            observations.append({"site": list(site), "physical": o})
            if int(o["state"]) > 0 and int(o["semantic"]) == 1 and list(o["direction"]) == [x, 1, z]:
                candidates.append({"choice": x, "site": list(site), "direction": [x, 1, z]})
    return {"version": VERSION, "tick": int(a.tick), "observations": observations,
            "candidates": candidates, "choice": candidates[0]["choice"] if len(candidates) == 1 else None,
            "decoder": "All six fixed R2 direction/site classes; unique candidate only",
            "zero_is_not_NULL": True, "functional_validation_pending": True}


def self_check():
    """Static assertions only; no import of DEE or experiment."""
    assert len(STOP_OFFSETS) == len(set(STOP_OFFSETS)) == 6
    assert len(OUTPUT_OFFSETS) == len(set(OUTPUT_OFFSETS)) == 6
    assert at(DATUM_OFFSET) not in {at(p) for p in STOP_OFFSETS}
    assert at((0, 3, 0)) == (19, 57, 5)  # Existing OP3 support may be reused.
    assert all(0 <= v < N for p in [DATUM_OFFSET, *STOP_OFFSETS, *OUTPUT_OFFSETS] for v in at(p))
    return {"version": VERSION, "status": "STATIC_ONLY", "geometry": geometry(),
            "Native_imported": False, "Native_ticks": 0,
            "unverified": ["admission", "current-data sensitivity", "generic-credit coexistence", "useful selection"]}


if __name__ == "__main__":
    import argparse, json
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-check", action="store_true", required=True)
    parser.parse_args()
    print(json.dumps(self_check(), ensure_ascii=False, indent=2))
