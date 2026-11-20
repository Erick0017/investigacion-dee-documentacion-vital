"""CPC4 finite native channel apparatus, immutable DEE thinking4/v27 only.

This is a preparation/experience protocol, not a second physics.  A learned
directional product travels from A to B.  B's own acquired relation changes
the encounter; a later common physical probe reads the resulting mobile
state.  The same native output enters a finite supplied consequence bank.
Names A/B denote finite mobile functional cores, not two complete basal bodies.

Geometry derives from SEM01's measured directional-memory and supplied-bank
mechanisms.  No SEM01 module, result, correspondence map or terminal fixture is
imported. All interfaces are installed before the first advance.
"""
from __future__ import annotations

from array import array
import hashlib

N = 67
A = (42, 20, 12)
B = (30, 32, 12)
WHEEL_SHA256 = "17c07745b9687d8686d132f055c39c149da1dde807e7246a67d457fe69df5623"
NATIVE_SHA256 = "20d7c764dbc22d1f110ba255f92073b4f64c744c91f6980335a4e08dd61fe066"
SIGNAL = (-1, 0, 0)
MESSAGE = (-1, 1, 0)
QUERY = (0, 0, 1)
ACTION = (-1, 1, 1)
RESOURCE = (1, 0, -1)
U = (0, -1, 0)
V = (0, -1, 1)


def moved(site, direction, count=1, translation=(0, 0, 0)):
    return tuple((site[i] + count * direction[i] + translation[i]) % N for i in range(3))


def interface(d, name, site, direction):
    ch = d.ChannelSpec()
    ch.name = name
    ch.injection_site = d.Coordinate(*site)
    ch.direction = d.Direction(*direction)
    ch.state = 1
    ch.semantic = 1
    ch.allow_experience = True
    ch.allow_probe = True
    result = d.InterfaceSpec()
    result.name = name
    result.channel = ch
    return result


def bank_spec(emitter):
    h = moved(emitter, ACTION, 4)
    interception = moved(h, (0, 1, 0), 4)
    return {"emitter": tuple(emitter), "cost_meeting": h,
            "interception": interception,
            "resource_source": moved(h, RESOURCE, -4),
            "resource_receiver": moved(h, RESOURCE, 3),
            "supply_source": moved(h, (0, 1, 0), -6),
            "function_receiver": moved(h, (0, 1, 0), 2),
            "U_source": moved(interception, U, -7),
            "V_source": moved(interception, V, -7),
            "resource_delay": 0, "supply_delay": 6,
            "resource_read": 7, "function_read": 14}


def prepare(d, translation=(0, 0, 0)):
    """One empty physical world; port declaration installs no learned matter."""
    if len(translation) != 3 or any(type(v) is not int for v in translation):
        raise ValueError("Integer translation triple required")
    ports = []
    centers = {"A": moved(A, (0, 0, 0), translation=translation),
               "B": moved(B, (0, 0, 0), translation=translation)}
    for name, center in centers.items():
        ports.append(interface(d, name + ".signal", moved(center, SIGNAL, -3), SIGNAL))
        for sign, label in ((1, "plus"), (-1, "minus")):
            direction = (1, sign, 0)
            ports.append(interface(d, name + ".outcome." + label, moved(center, direction, -3), direction))
        # Fixed phase-later interfaces are declared at T0, not per episode.
        ports.append(interface(d, name + ".query_z", moved(center, QUERY, -3), QUERY))
        ports.append(interface(d, name + ".reference_message", center, MESSAGE))
    bank = bank_spec(centers["B"])
    for suffix, source, direction in (("resource", "resource_source", RESOURCE),
                                      ("supply", "supply_source", (0, 1, 0)),
                                      ("U", "U_source", U), ("V", "V_source", V)):
        ports.append(interface(d, "use." + suffix, bank[source], direction))
    ports.append(interface(d, "use.reference_action", centers["B"], ACTION))
    recipe = d.OrganizationRecipe.research(N, [], 0)
    recipe.interfaces = ports
    recipe.execution = d.TickOptions(d.Backend.LAZY, 1)
    return d.OrganizationalWorld.create(recipe), {"centers": centers, "bank": bank, "translation": list(translation)}


def acquire(world, core, sign, tick, signal_load=5, outcome_load=11):
    if core not in ("A", "B") or sign not in (-1, 1):
        raise ValueError("Declared core and directional outcome required")
    world.run_until(tick)
    return [world.submit(core + ".signal", signal_load, tick),
            world.submit(core + ".outcome." + ("plus" if sign == 1 else "minus"), outcome_load, tick)]


def physical(sample):
    r = sample.record
    return {"tick": sample.tick, "site": [sample.coordinate.x, sample.coordinate.y, sample.coordinate.z],
            "raw": sample.raw, "clock": sample.clock, "state": r.state,
            "semantic": r.semantic, "s_reg": r.s_reg, "direction": [r.dx, r.dy, r.dz],
            "active": r.state > 0 and r.semantic != 5}


def observe(world, site):
    import dee_thinking as d
    return physical(world.runtime.observe(d.Coordinate(*site)))


def digest(world):
    return {"tick": world.runtime.current_tick,
            "raw_sha256": hashlib.sha256(array("Q", world.runtime.raw_copy()).tobytes()).hexdigest(),
            "clock_sha256": hashlib.sha256(array("Q", world.runtime.clock_copy()).tobytes()).hexdigest()}


def receipt(world, identity):
    r = world.runtime.receipt(identity)
    if r is None:
        return {"id": identity, "missing": True}
    return {"id": r.id, "kind": str(r.kind), "status": str(r.status),
            "requested_tick": r.requested_tick, "effective_tick": r.effective_tick,
            "channels": list(r.channels), "reason": r.reason}


def panel(world, spec, tick):
    # This passively samples known recipe sites, not a universal identity tracker.
    a, b = spec["centers"]["A"], spec["centers"]["B"]
    sites = {"A_hub": a, "B_hub": b}
    if 70 <= tick <= 82:
        sites["A_message_segment"] = moved(a, MESSAGE, tick - 70)
    if 82 <= tick <= 149:
        sites["B_plus_candidate"] = moved(b, (-1, 1, 0), tick - 82)
        sites["B_flat_candidate"] = moved(b, (-1, 0, 0), tick - 82)
    for name, site in spec["bank"].items():
        if isinstance(site, tuple) and len(site) == 3:
            sites["bank_" + name] = site
    return {"tick": world.runtime.current_tick,
            "samples": {name: observe(world, site) for name, site in sites.items()}}


def input_resources(world, emission_tick):
    return [world.submit("use.resource", 3, emission_tick),
            world.submit("use.supply", 7, emission_tick + 6)]


def evaluate_bank(resource, function):
    optional = bool(resource["active"] and resource["s_reg"] == 3 and resource["direction"] == list(RESOURCE))
    primary = bool(function["active"] and function["s_reg"] == 7 and function["direction"] == [0, 1, 0])
    return {"primary_delivery": primary, "optional_delivery": optional,
            "profile": [int(primary), int(optional)],
            "external_utility": 2 * int(primary) + int(optional),
            "scope": "External finite-task evaluation only, never supplied as an error or teacher"}


def cut_emitted_message(world, spec):
    """Explicit diagnostic complete fork, after A's native emission exists."""
    import dee_thinking as d
    site = spec["centers"]["A"]
    before = observe(world, site)
    if world.runtime.current_tick != 70 or not before["active"] or before["direction"] != list(MESSAGE):
        raise ValueError("Expected real A emission not present; no replacement is fabricated")
    parent_raw = world.runtime.raw_copy()
    parent_clock = world.runtime.clock_copy()
    edit = d.ResearchStateEdit()
    edit.coordinate = d.Coordinate(*site)
    edit.raw = 0
    edit.label = "CPC4_LATE_CHANNEL_CUT_AFTER_A_EMISSION"
    child = world.diagnostic_fork([edit], True)
    child_raw = child.runtime.raw_copy()
    changed = [i for i, (a, b) in enumerate(zip(parent_raw, child_raw)) if a != b]
    expected = (site[0] * N + site[1]) * N + site[2]
    assert changed == [expected]
    assert child.runtime.clock_copy() == parent_clock
    assert world.runtime.raw_copy() == parent_raw and world.runtime.clock_copy() == parent_clock
    return child, {"site": list(site), "tick": 70, "pre": before,
                   "raw_sites_changed": 1, "clock_sites_changed": 0,
                   "parent_unchanged": True, "operation": "EXPLICIT_DIAGNOSTIC_FORK_RAW_REMOVAL"}
