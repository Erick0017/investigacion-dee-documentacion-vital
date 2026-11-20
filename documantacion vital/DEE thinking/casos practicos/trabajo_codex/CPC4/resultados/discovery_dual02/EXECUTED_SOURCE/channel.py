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
LEXICAL_HUBS = {"W1": (30, 30, 36), "W2": (30, 30, 52)}
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
    lexical = {name: moved(site, (0, 0, 0), translation=translation)
               for name, site in LEXICAL_HUBS.items()}
    for name, center in lexical.items():
        # Neutral physical forms; no name->function correspondence is placed.
        # Same signal interface is used when acquiring and later querying.
        ports.append(interface(d, "lex." + name + ".signal", moved(center, SIGNAL, -3), SIGNAL))
        for sign, label in ((1, "plus"), (-1, "minus")):
            direction = (1, sign, 0)
            ports.append(interface(d, "lex." + name + ".outcome." + label, moved(center, direction, -3), direction))
            inverse = (-1, sign, 0)
            ports.append(interface(d, "lex." + name + ".inverse." + label, moved(center, inverse, -3), inverse))
    bank = bank_spec(centers["B"])
    for suffix, source, direction in (("resource", "resource_source", RESOURCE),
                                      ("supply", "supply_source", (0, 1, 0)),
                                      ("U", "U_source", U), ("V", "V_source", V)):
        ports.append(interface(d, "use." + suffix, bank[source], direction))
    ports.append(interface(d, "use.reference_action", centers["B"], ACTION))
    recipe = d.OrganizationRecipe.research(N, [], 0)
    recipe.interfaces = ports
    recipe.execution = d.TickOptions(d.Backend.LAZY, 1)
    return d.OrganizationalWorld.create(recipe), {"centers": centers, "bank": bank,
                                                "lexical_hubs": lexical, "translation": list(translation)}


def lexical_signal(world, form, tick, payload=5):
    if form not in LEXICAL_HUBS or payload not in (5, 7):
        raise ValueError("Declared physical form and bounded payload required")
    return world.submit("lex." + form + ".signal", payload, tick)


def lexical_outcome_broadcast(world, sign, tick, payload=11):
    """Explicit external transduction, identical report to both form regions.

    Caller must obtain sign from the actual current physical consequence,
    not a requested target, a decoded prediction or a stored pairing map.
    """
    if sign not in (-1, 1) or payload != 11:
        raise ValueError("Published fixed physical outcome code required")
    label = "plus" if sign == 1 else "minus"
    return [world.submit("lex." + form + ".outcome." + label, payload, tick)
            for form in LEXICAL_HUBS]


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


def oriented_bank(emitter, orientation, prefix, emission_tick):
    """Mirror-related useful routes, with equal physical resource inventory."""
    if orientation not in (-1, 1):
        raise ValueError("Orientation must be+1 or-1")
    action = (-1, orientation, 1)
    supply = (0, orientation, 0)
    event_u = (0, -orientation, 0)
    event_v = (0, -orientation, 1)
    h = moved(emitter, action, 4)
    intercept = moved(h, supply, 4)
    return {"prefix": prefix, "orientation": orientation,
            "emitter": tuple(emitter), "action": action, "resource_direction": RESOURCE,
            "supply_direction": supply, "U_direction": event_u, "V_direction": event_v,
            "cost_meeting": h, "interception": intercept,
            "resource_source": moved(h, RESOURCE, -4),
            "resource_receiver": moved(h, RESOURCE, 3),
            "supply_source": moved(h, supply, -6),
            "function_receiver": moved(h, supply, 2),
            "U_source": moved(intercept, event_u, -7),
            "V_source": moved(intercept, event_v, -7),
            "emission_tick": emission_tick, "resource_read_tick": emission_tick + 7,
            "function_read_tick": emission_tick + 14}


def prepare_dual(d, translation=(0, 0, 0), extra_interfaces=(), backend=None, receiver_basis="z"):
    """A sender and one distributed receiver B with two fixed physical regions.

    Bminus uses a different x and phase. Placing it at(30,8,12) would cause
    opposite vertical B memories to collide at70 before communication; that
    invalid geometry was rejected algebraically, not retuned from a holdout.
    """
    if receiver_basis not in ("y","z"):
        raise ValueError("Receiver basis must be explicitly y or z")
    centers = {"A": moved(A, (0, 0, 0), translation=translation),
               "Bplus": moved((30, 32, 12), (0, 0, 0), translation=translation),
               "Bminus": moved((24, 2, 12), (0, 0, 0), translation=translation)}
    ports = []
    for name, center in centers.items():
        ports.append(interface(d, name + ".signal", moved(center, SIGNAL, -3), SIGNAL))
        for sign, label in ((1, "plus"), (-1, "minus")):
            direction = (1,0,sign) if name!="A" and receiver_basis=="z" else (1,sign,0)
            ports.append(interface(d, name + ".outcome." + label, moved(center, direction, -3), direction))
        query=(0,1 if name=="Bplus" else -1,0) if name!="A" and receiver_basis=="z" else QUERY
        suffix=".query_y" if name!="A" and receiver_basis=="z" else ".query_z"
        ports.append(interface(d, name + suffix, moved(center, query, -3), query))
    lexical = {name: moved(site, (0, 0, 0), translation=translation)
               for name, site in LEXICAL_HUBS.items()}
    for name, center in lexical.items():
        ports.append(interface(d, "lex." + name + ".signal", moved(center, SIGNAL, -3), SIGNAL))
        for sign, label in ((1, "plus"), (-1, "minus")):
            direction = (1, sign, 0)
            ports.append(interface(d, "lex." + name + ".outcome." + label, moved(center, direction, -3), direction))
            inverse = (-1, sign, 0)
            ports.append(interface(d, "lex." + name + ".inverse." + label, moved(center, inverse, -3), inverse))
    banks = {"plus": oriented_bank(centers["Bplus"], 1, "use.plus", 149),
             "minus": oriented_bank(centers["Bminus"], -1, "use.minus", 155)}
    for bank in banks.values():
        for suffix, key, direction in (("resource", "resource_source", RESOURCE),
                                      ("supply", "supply_source", bank["supply_direction"]),
                                      ("U", "U_source", bank["U_direction"]),
                                      ("V", "V_source", bank["V_direction"])):
            ports.append(interface(d, bank["prefix"] + "." + suffix, bank[key], direction))
        ports.append(interface(d, bank["prefix"] + ".reference_action", bank["emitter"], bank["action"]))
        ports.append(interface(d, bank["prefix"] + ".reference_action_out", moved(bank["emitter"], bank["action"]), bank["action"]))
    ports.append(interface(d, "instrument.sham", moved((50,60,60),(0,0,0),translation=translation), (1,0,0)))
    recipe = d.OrganizationRecipe.research(N, [], 0)
    recipe.interfaces = ports + list(extra_interfaces)
    recipe.execution = d.TickOptions(backend or d.Backend.LAZY, 1)
    world = d.OrganizationalWorld.create(recipe)
    spec = {"recipe": "cpc4.dual_directional_channel.v2_z_receiver" if receiver_basis=="z" else "cpc4.dual_directional_channel.v1_y_receiver", "N": N,
            "centers": centers, "banks": banks, "lexical_hubs": lexical,
            "receiver_basis":receiver_basis,
            "B_query_channels":{core:core+(".query_y" if receiver_basis=="z" else ".query_z") for core in ("Bplus","Bminus")},
            "translation": list(translation), "A_acquisition": 0,
            "B_acquisition": {"Bplus":12,"Bminus":18},
            "A_query":67,"A_emission":70,
            "contacts":{"Bplus":82,"Bminus":88},
            "B_queries":{"Bplus":146,"Bminus":152},
            "B_responses":{"Bplus":149,"Bminus":155},
            "sham_source":moved((50,60,60),(0,0,0),translation=translation),
            "final_tick":169,
            "scope":"One sender A and one distributed finite receiver B; mobile physical cores, not two fully renewable basal bodies"}
    return world, spec


def describe_dual(translation=(0, 0, 0),receiver_basis="z"):
    """Inert published geometry, for views/continuation; never creates a world."""
    centers={"A":moved(A,(0,0,0),translation=translation),
             "Bplus":moved((30,32,12),(0,0,0),translation=translation),
             "Bminus":moved((24,2,12),(0,0,0),translation=translation)}
    if receiver_basis not in ("y","z"):raise ValueError("Explicit receiver basis required")
    return {"recipe":"cpc4.dual_directional_channel.v2_z_receiver" if receiver_basis=="z" else "cpc4.dual_directional_channel.v1_y_receiver","N":N,"centers":centers,
            "receiver_basis":receiver_basis,
            "B_query_channels":{core:core+(".query_y" if receiver_basis=="z" else ".query_z") for core in ("Bplus","Bminus")},
            "banks":{"plus":oriented_bank(centers["Bplus"],1,"use.plus",149),
                     "minus":oriented_bank(centers["Bminus"],-1,"use.minus",155)},
            "lexical_hubs":{name:moved(site,(0,0,0),translation=translation) for name,site in LEXICAL_HUBS.items()},
            "translation":list(translation),"A_acquisition":0,
            "B_acquisition":{"Bplus":12,"Bminus":18},"A_query":67,"A_emission":70,
            "contacts":{"Bplus":82,"Bminus":88},"B_queries":{"Bplus":146,"Bminus":152},
            "B_responses":{"Bplus":149,"Bminus":155},"final_tick":169,
            "sham_source":moved((50,60,60),(0,0,0),translation=translation),
            "scope":"One sender A and one distributed finite receiver B; mobile physical cores, not two fully renewable basal bodies"}


def acquire_dual(world, core, sign, tick, signal_load=5, outcome_load=11, signal_delay=0):
    if core not in ("A", "Bplus", "Bminus") or sign not in (-1, 1):
        raise ValueError("Declared distributed core and directional outcome required")
    world.run_until(tick)
    if signal_delay not in (0,1):
        raise ValueError("Only paired or explicitly one-tick-unpaired acquisition is declared")
    return [world.submit(core + ".signal", signal_load, tick+signal_delay),
            world.submit(core + ".outcome." + ("plus" if sign == 1 else "minus"), outcome_load, tick)]


def dual_resources(world, bank):
    tick = bank["emission_tick"]
    return [world.submit(bank["prefix"] + ".resource", 3, tick),
            world.submit(bank["prefix"] + ".supply", 7, tick + 6)]


def evaluate_oriented_bank(bank, resource, function):
    optional = bool(resource["active"] and resource["s_reg"] == 3 and resource["direction"] == list(RESOURCE))
    primary = bool(function["active"] and function["s_reg"] == 7 and function["direction"] == list(bank["supply_direction"]))
    return {"primary_delivery": primary, "optional_delivery": optional,
            "profile": [int(primary), int(optional)], "external_utility": 2 * int(primary) + int(optional)}


def cut_dual_message(world, spec):
    import dee_thinking as d
    site = spec["centers"]["A"]
    value = observe(world, site)
    if world.runtime.current_tick != 70 or not value["active"] or value["s_reg"] != 21 or value["direction"] not in ([-1,1,0],[-1,-1,0]):
        raise ValueError("The actual learned A message is not present; no cut fabricated")
    before_raw = world.runtime.raw_copy()
    before_clock = world.runtime.clock_copy()
    before_receipts = [receipt(world, r.id) for r in world.runtime.receipts]
    edit = d.ResearchStateEdit()
    edit.coordinate = d.Coordinate(*site)
    edit.raw = 0
    edit.label = "CPC4_DUAL_LATE_MESSAGE_CUT"
    child = world.diagnostic_fork([edit], True)
    changed = [i for i,(left,right) in enumerate(zip(before_raw,child.runtime.raw_copy())) if left != right]
    assert changed == [(site[0]*N+site[1])*N+site[2]]
    assert child.runtime.clock_copy() == before_clock
    assert [receipt(child,r.id) for r in child.runtime.receipts] == before_receipts
    assert world.runtime.raw_copy() == before_raw and world.runtime.clock_copy() == before_clock
    return child,{"operation":"EXPLICIT_DIAGNOSTIC_FORK_RAW_REMOVAL","tick":70,"site":list(site),
                  "pre":value,"raw_sites_changed":1,"clock_sites_changed":0,"parent_unchanged":True}


def diagnostic_record_edit(world,site,label,raw=None,direction=None,expected_load=None):
    """Explicit complete-state fork, with fieldwise verification of the edit."""
    import dee_thinking as d
    before=observe(world,site)
    if not before["active"] or expected_load is not None and before["s_reg"]!=expected_load:
        raise ValueError("Declared actual diagnostic component not present")
    if raw is not None and direction is not None:
        raise ValueError("One diagnostic edit specification required")
    if direction is not None:
        if d.pack_record(before["state"],before["s_reg"],*before["direction"],before["semantic"])!=before["raw"]:
            raise ValueError("Packing does not reproduce the actual RAW; reserved bits must not be lost")
        new_raw=d.pack_record(before["state"],before["s_reg"],*direction,before["semantic"])
    else:new_raw=raw
    if new_raw is None:raise ValueError("Explicit RAW or direction required")
    parent_raw=world.runtime.raw_copy();parent_clocks=world.runtime.clock_copy()
    old_receipts=[receipt(world,r.id) for r in world.runtime.receipts]
    edit=d.ResearchStateEdit();edit.coordinate=d.Coordinate(*site);edit.raw=new_raw;edit.label=label
    child=world.diagnostic_fork([edit],True)
    changed=[i for i,(a,b) in enumerate(zip(parent_raw,child.runtime.raw_copy())) if a!=b]
    expected_index=(site[0]*N+site[1])*N+site[2]
    assert changed==([expected_index] if new_raw!=before["raw"] else [])
    assert child.runtime.clock_copy()==parent_clocks
    assert [receipt(child,r.id) for r in child.runtime.receipts]==old_receipts
    assert world.runtime.raw_copy()==parent_raw and world.runtime.clock_copy()==parent_clocks
    after=observe(child,site)
    changed_fields=[key for key in ("state","semantic","s_reg","direction") if before[key]!=after[key]]
    return child,{"operation":"EXPLICIT_DIAGNOSTIC_FORK","label":label,"tick":world.runtime.current_tick,
                  "site":list(site),"pre":before,"post":after,"raw_sites_changed":len(changed),
                  "clock_sites_changed":0,"changed_record_fields":changed_fields,"parent_unchanged":True}


def moore_context(world,site):
    values=[]
    for dx in (-1,0,1):
        for dy in (-1,0,1):
            for dz in (-1,0,1):
                if (dx,dy,dz)==(0,0,0):continue
                sample=observe(world,moved(site,(dx,dy,dz)))
                values.append({"offset":[dx,dy,dz],"sample":sample})
    return values
