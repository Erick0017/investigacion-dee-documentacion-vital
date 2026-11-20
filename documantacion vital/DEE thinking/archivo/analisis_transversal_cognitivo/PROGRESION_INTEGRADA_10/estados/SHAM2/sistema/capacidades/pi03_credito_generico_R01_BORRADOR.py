"""PI03 generic temporal-credit apparatus: draft, NOT experimentally verified.

Importing this module is pure Python. It does not import DEE, open a life,
advance a Runtime, or select a main. Native functions require an explicit owner
object supplied by the campaign executor. There is no command that executes a
life. The only CLI mode verifies static geometry/arithmetic.

The proposed prepared motor-efference codec is inverse: choice -1/+1 becomes
an eligibility carrier +X/-X. A delayed generic failure pulse +Z then makes
native DEMUX, not Python, route a zero-load contact to the opposite R06 bank.
The predicted reinforcement polarity MUST be calibrated before evaluation.
It must not be reinterpreted after reserved outcomes.
"""
from __future__ import annotations

import argparse
import json
from math import gcd

VERSION = "PI03.generic_temporal_credit.R01_REVIEWED_DRAFT"
N = 67
REF_PERIOD = 391
REF_DOUBLE_PERIOD = 782
DEFAULT_PREFIX = "PI03.TC.R01"
READER_OFFSETS = ((-2, 2, 0), (0, 2, 0), (2, 2, 0))


def at(origin, delta, n=N):
    return tuple((int(origin[k]) + int(delta[k])) % int(n) for k in range(3))


def frame_rows(origin, n=N):
    """Exact R06 unlearned geometry plus TWO proposed disposal absorbers.

    Every row is submitted through ordinary admitted interfaces. No placement,
    RAW write, clock reset, learned-reference transplant or T0 is used here.
    """
    frame = {(-1, -1, 0): (1, 0, 1), (1, -1, 0): (1, 0, 1)}
    for x in (-2, 2):
        for y in (-2, -1):
            for z in (-1, 0, 1):
                frame[(x, y, z)] = (1, 0, 4)
    for p in ((0, 1, 1), (0, 1, -1)):
        frame[p] = (1, 0, 4)
    for p in ((0, 0, 1), (-1, -3, 0), (1, -3, 0), (-1, -2, 1),
              (1, -2, 1), (2, 1, 2), (-2, 0, 0), (-3, 3, 0), (3, 3, 0)):
        frame[p] = (0, 0, 4)
    # A generic successful/nonpunishing outcome turns the carrier toward -Y.
    # It is consumed before circling again, away from both plastic references.
    for p in ((-2, -3, -2), (2, -3, -2)):
        frame[p] = (0, 0, 4)
    return [{"site": at(origin, p, n), "offset": p, "state": state,
             "payload": payload, "semantic": semantic, "direction": (0, 0, 0)}
            for p, (state, payload, semantic) in sorted(frame.items())]


def port_rows(origin, prefix=DEFAULT_PREFIX, n=N):
    e = (0, -1, -2)
    rows = {
        "copy.minus": (e, (1, 0, 0)),
        "copy.plus": (e, (-1, 0, 0)),
        # Both outcome interfaces are independent of the previous action.
        # A +Z failure pulse is injected one site below E, one tick before E.
        "outcome.failure": ((0, -1, -3), (0, 0, 1)),
        "outcome.nonfailure": ((0, 0, -2), (0, -1, 0)),
        "query": ((0, 0, -3), (0, 0, 1)),
        "support.plus": ((-2, 1, -2), (1, 0, 1)),
        "support.minus": ((2, 4, 0), (-1, -1, 0)),
    }
    return [{"name": prefix + "." + name, "suffix": name,
             "site": at(origin, pos, n), "direction": direction,
             "state": 1, "semantic": 1}
            for name, (pos, direction) in rows.items()]


def geometry_footprint(origin, n=N, halo=1):
    """Conservative passive preflight area; not a global future-influence proof.

    Includes the ENTIRE periodic eligibility row, both outcome source sites,
    first two routed steps, frame, fixed query/support paths and reader sites.
    A Moore halo detects local pre-existing fields, including state=0 RAW.
    """
    points = {tuple(r["site"]) for r in frame_rows(origin, n)}
    points.update(tuple(r["site"]) for r in port_rows(origin, n=n))
    points.update(at(origin, (x, -1, -2), n) for x in range(n))
    for sign in (-1, 1):
        points.update(at(origin, (sign * step, -1, -2 + step), n)
                      for step in (0, 1, 2))
        points.update(at(origin, (sign * step, -1 - step, -2), n)
                      for step in (0, 1, 2))
    # Existing R06's complete fixed query/support/read path coverage.
    ports = [((0, 0, -3), (0, 0, 1)),
             ((-2, 1, -2), (1, 0, 1)),
             ((2, 4, 0), (-1, -1, 0))]
    for start, direction in ports:
        for t in range(8):
            points.add(at(origin, tuple(start[k] + t * direction[k]
                                       for k in range(3)), n))
    points.update(at(origin, p, n) for p in READER_OFFSETS)
    if halo:
        points = {at(p, (dx, dy, dz), n) for p in points
                  for dx in range(-halo, halo + 1)
                  for dy in range(-halo, halo + 1)
                  for dz in range(-halo, halo + 1)}
    return sorted(points)


def preflight_from_lookup(origin, lookup, n=N, halo=1):
    """Read-only evaluator supplied with snapshot lookup or owner observation.

    Lookup returns decoded dictionaries including exact integer raw and clock.
    No fallback to state==0 and no clearing is permitted. It checks matching
    reference clock phase; late installation preserves the existing clocks.
    """
    observations = [lookup(site) for site in geometry_footprint(origin, n, halo)]
    conflicts = [{"site": tuple(o.get("site", ())), "raw": str(o["raw"])}
                 for o in observations if int(o["raw"]) != 0]
    refs = [lookup(at(origin, p, n)) for p in ((-1, -1, 0), (1, -1, 0))]
    clocks = [int(o["clock"]) for o in refs]
    phase_equal = clocks[0] % REF_DOUBLE_PERIOD == clocks[1] % REF_DOUBLE_PERIOD
    return {"origin": tuple(origin), "N": n, "halo": halo,
            "checked_sites": len(observations), "raw_conflicts": conflicts,
            "reference_clocks": [str(c) for c in clocks],
            "reference_phase_equal": phase_equal,
            "eligible": not conflicts and phase_equal,
            "scope": "Passive current-state clearance only; no guarantee against future external influence."}


def schedule_trial(now, reference_clock_now, delay_laps, query_lead=7, n=N):
    """Prepared phase calendar, not learned timing or retrospective credit.

    The motor is read one tick before seed_tick; its fixed efference is submitted
    to the next FUTURE boundary, never to an already observed current boundary.
    Generic outcome arrives at the hub after delay_laps full toroidal circuits.
    The next step contacts one bank at the odd-391 accretion gate. Runtime
    boundary admission precedes the next evolution: receipt/snapshot semantics
    must be inspected in calibration, without silently shifting the reader.
    """
    if int(delay_laps) < 1:
        raise ValueError("At least one lap is required: a generic outcome cannot be scheduled before its actual action")
    delay = int(delay_laps) * int(n)
    earliest_contact = int(now) + int(query_lead) + delay + 3
    offset = int(reference_clock_now) - int(now)
    residue = (REF_PERIOD - offset) % REF_DOUBLE_PERIOD
    contact = earliest_contact + (residue - earliest_contact) % REF_DOUBLE_PERIOD
    collision = contact - 1
    seed = collision - delay
    return {"query_tick": seed - int(query_lead), "query_read_tick": seed - 1,
            "seed_tick": seed, "outcome_injection_tick": collision - 1,
            "collision_tick": collision, "contact_tick": contact,
            "settled_after_tick": contact + 2,
            "delay_ticks": delay, "delay_laps": int(delay_laps),
            "action_to_collision_ticks": delay + 1,
            "motor_efference_delay_ticks": 1,
            "phase_rule": "Both reference clocks at contact are 391 modulo 782; calendar is prepared."}


def _native():
    from dee_thinking import _native as d
    from dee_thinking.consolidated import exact_observation, exact_receipt
    return d, exact_observation, exact_receipt


def _channel(world, name, site, direction, state=1, semantic=1):
    d, _, _ = _native()
    if name in set(world.runtime.channel_names):
        raise ValueError("Refusing a reused channel namespace: " + name)
    c = d.ChannelSpec()
    c.name = name
    c.injection_site = d.Coordinate(*site)
    c.direction = d.Direction(*direction)
    c.state = int(state)
    c.semantic = int(semantic)
    c.allow_experience = True
    c.allow_probe = False
    i = d.InterfaceSpec()
    i.name = name
    i.channel = c
    world.declare_interface(i)


def install_legal(owner, origin, *, prefix=DEFAULT_PREFIX, halo=1):
    """EXPLICIT NATIVE MUTATION, called only by the root Native executor.

    Requires an already loaded diagnostic/candidate owner. Caller's contract
    must reject the main and require an unused clone. No owner, life, file,
    selector, metadata persistence or main promotion is created here.
    """
    d, exact_observation, exact_receipt = _native()
    world = owner.world
    current_tick = int(owner.tick)
    def lookup(site):
        return dict(exact_observation(world.runtime.observe(d.Coordinate(*site))), site=site)
    check = preflight_from_lookup(origin, lookup, halo=halo)
    if not check["eligible"]:
        raise ValueError("Unsafe P0 installation preflight: " + json.dumps(check))
    names = {prefix + ".prepare." + str(k) for k in range(len(frame_rows(origin)))}
    names.update(r["name"] for r in port_rows(origin, prefix))
    if names.intersection(set(world.runtime.channel_names)):
        raise ValueError("Candidate namespace already exists; no reinstallation")
    arrival = current_tick + 2
    requests = []
    for k, row in enumerate(frame_rows(origin)):
        name = prefix + ".prepare." + str(k)
        _channel(world, name, row["site"], row["direction"], row["state"], row["semantic"])
        r = world.submit(name, int(row["payload"]), arrival)
        requests.append({"id": int(r.id), "channel": name, "site": row["site"],
                         "payload": row["payload"], "requested_tick": arrival})
    owner.run_until(arrival + 1)
    for row in requests:
        row["receipt"] = exact_receipt(world.runtime.receipt(row["id"]))
    ready = all(row["receipt"]["status"] == "applied" for row in requests)
    # Any incomplete admission preserves an adverse reached state. It never
    # resubmits or cleans the landscape to manufacture a successful install.
    if ready:
        for row in port_rows(origin, prefix):
            _channel(world, row["name"], row["site"], row["direction"])
    return {"version": VERSION, "kind": "external_P0_legal_installation",
            "preflight": check, "requests": requests, "tick_after": int(owner.tick),
            "origin": tuple(origin), "prefix": prefix, "ready": ready,
            "scope": "Prepared unlearned anatomy only; no acquisition or functional success inferred."}


def submit_query(world, tick, *, prefix=DEFAULT_PREFIX):
    """Same three zero-load material inputs for every query; not passive."""
    requests = []
    for suffix in ("query", "support.plus", "support.minus"):
        r = world.submit(prefix + "." + suffix, 0, int(tick))
        requests.append({"id": int(r.id), "channel": prefix + "." + suffix,
                         "payload": 0, "requested_tick": int(tick)})
    return requests


def read_fixed(world, origin):
    """Exact R06 fixed three-site reader; zero is distinct from NULL."""
    d, exact_observation, _ = _native()
    observations = []
    candidates = []
    for sign in (-1, 0, 1):
        site = at(origin, (2 * sign, 2, 0))
        o = exact_observation(world.runtime.observe(d.Coordinate(*site)))
        observations.append(dict(o, site=site))
        if int(o["state"]) > 0 and int(o["semantic"]) == 1 and list(o["direction"]) == [sign, 1, 0]:
            candidates.append({"choice": sign, "site": site})
    return {"tick": int(world.runtime.current_tick), "observations": observations,
            "candidates": candidates,
            "choice": candidates[0]["choice"] if len(candidates) == 1 else None,
            "reader": "R06 q+6; three fixed sites, active SEM1, fixed direction class"}


def submit_motor_copy(world, actual_choice, tick, *, prefix=DEFAULT_PREFIX):
    """Prepared motor efference at actiontime, NEVER called at consequence time.

    Reject NULL/zero. Mapping zero to a default action, if used, is a separate
    declared environment/actuator rule and must appear in all controls.
    """
    if type(actual_choice) is not int or actual_choice not in (-1, 1):
        raise ValueError("Only a real admitted binary motor action can have an efference copy")
    suffix = "copy.minus" if actual_choice == -1 else "copy.plus"
    r = world.submit(prefix + "." + suffix, 0, int(tick))
    return {"id": int(r.id), "channel": prefix + "." + suffix, "payload": 0,
            "requested_tick": int(tick), "actual_motor_choice": actual_choice,
            "codec": "Fixed inverse motor-efference direction; P0, no expected action consulted."}


def submit_generic_outcome(world, failed, injection_tick, *, prefix=DEFAULT_PREFIX):
    """NO actual_choice/route/history argument by design.

    The outcome law receives only whether the environment actually failed.
    It cannot select a bank or infer a prior action from this interface.
    """
    if type(failed) is not bool:
        raise TypeError("An actual environment consequence bool is required")
    suffix = "outcome.failure" if failed else "outcome.nonfailure"
    r = world.submit(prefix + "." + suffix, 0, int(injection_tick))
    return {"id": int(r.id), "channel": prefix + "." + suffix, "payload": 0,
            "requested_tick": int(injection_tick), "actual_environment_failed": failed,
            "codec": "Generic outcome; bank is selected only by native eligibility at the hub."}


def self_check():
    """Static algebra/geometry only: NOT a DEE reproduction or simulation."""
    origin = (33, 33, 33)
    frame = {tuple(r["offset"]): r for r in frame_rows(origin)}
    for sign in (-1, 1):
        assert (2 * sign, -1, 0) in frame
        assert frame[(2 * sign, -1, 0)]["semantic"] == 4
        assert frame[(2 * sign, -3, -2)]["semantic"] == 4
        contact = (sign, -1, -1)
        own = (sign, -1, 0)
        other = (-sign, -1, 0)
        assert max(abs(contact[k] - own[k]) for k in range(3)) == 1
        assert max(abs(contact[k] - other[k]) for k in range(3)) == 2
    assert gcd(N, REF_DOUBLE_PERIOD) == 1
    for clock in (0, 753346, 2**54 + 33):
        for laps in (1, 2, 3):
            row = schedule_trial(753346, clock, laps)
            assert (clock + row["contact_tick"] - 753346) % 782 == 391
            assert row["collision_tick"] - row["seed_tick"] == laps * 67
            assert row["query_read_tick"] + 1 == row["seed_tick"]
    return {"version": VERSION, "status": "static_checks_only",
            "frame_rows": len(frame_rows(origin)),
            "footprint_sites_halo1": len(geometry_footprint(origin)),
            "not_verified": ["Native admission", "late-clock accretion", "query polarity",
                             "eligibility survival", "generic outcome contact", "functional learning"]}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-check", action="store_true", required=True)
    parser.parse_args()
    print(json.dumps(self_check(), ensure_ascii=False, indent=2))
