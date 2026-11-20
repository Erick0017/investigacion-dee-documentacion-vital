"""SEM01 M1: fixed physical signal ports, acquired mobile direction, torus read.

Only the installed DEE thinking4/v27 performs transitions.  U/V are a fixed
outcome transduction: no signal-to-outcome correspondence is stored here.
The same signal port, load, direction, state and semantic are used for learning
and for later signal-only queries.  The N=67 return phase is prepared geometry,
not an acquired estimate of a period.  This module is experimental apparatus.
"""
from __future__ import annotations

from array import array
import hashlib

N = 67
HUBS = {"S1": (30, 30, 12), "S2": (30, 30, 44)}
SIGNAL_LOAD = 5
OUTCOME_LOAD = 11
SIGNAL_DIRECTION = (-1, 0, 0)
OUTCOME_DIRECTIONS = {"U": (1, 1, 0), "V": (1, -1, 0)}
DEFAULT_TRAINING_TICKS = {"S1": 0, "S2": 8}
CONFIG = {
    "method": "M1_FIXED_SIGNAL_TOROIDAL_MOBILE_MEMORY_V1",
    "dimension": N,
    "hubs": HUBS,
    "signal_load": SIGNAL_LOAD,
    "outcome_load": OUTCOME_LOAD,
    "signal_direction": SIGNAL_DIRECTION,
    "outcome_directions": OUTCOME_DIRECTIONS,
    "training_ticks": DEFAULT_TRAINING_TICKS,
    "training_flight": 3,
    "query_ticks": {"S1": 67, "S2": 75},
    "emission_ticks": {"S1": 70, "S2": 78},
    "readout_window": "exact prepared meeting boundary; pre/post samples retained",
    "decoder": {"-1,1,0": "U", "-1,-1,0": "V"},
    "scope": "Two finite mobile acquired relations in one Runtime; physical signal encoding is identical across phases. Period67 is prepared.",
}


def plus(q, direction, count=1, translation=(0, 0, 0)):
    return tuple((q[i] + direction[i] * count + translation[i]) % N for i in range(3))


def hub(signal, translation=(0, 0, 0)):
    if signal not in HUBS:
        raise ValueError("Signal identity must be S1 or S2")
    return plus(HUBS[signal], (0, 0, 0), translation=translation)


def interface(d, name, site, direction):
    item = d.InterfaceSpec()
    item.name = name
    channel = d.ChannelSpec()
    channel.name = name
    channel.injection_site = d.Coordinate(*site)
    channel.direction = d.Direction(*direction)
    channel.state = 1
    channel.semantic = 1
    channel.allow_experience = True
    channel.allow_probe = True
    item.channel = channel
    return item


def memory_interfaces(d, translation=(0, 0, 0)):
    ports = []
    for signal in HUBS:
        center = hub(signal, translation)
        ports.append(interface(d, "signal." + signal, plus(center, SIGNAL_DIRECTION, -3), SIGNAL_DIRECTION))
        for outcome, direction in OUTCOME_DIRECTIONS.items():
            ports.append(interface(d, "outcome." + signal + "." + outcome, plus(center, direction, -3), direction))
    return ports


def create_world(d, translation=(0, 0, 0), placements=(), extra_interfaces=()):
    if len(translation) != 3 or any(type(v) is not int for v in translation):
        raise ValueError("Integer translation triple required")
    recipe = d.OrganizationRecipe.research(N, list(placements), 0)
    recipe.execution = d.TickOptions(d.Backend.LAZY, 1)
    recipe.interfaces = memory_interfaces(d, translation) + list(extra_interfaces)
    return d.OrganizationalWorld.create(recipe)


def present_signal(world, signal, at_tick):
    if signal not in HUBS:
        raise ValueError("Signal identity must be S1 or S2")
    return world.submit("signal." + signal, SIGNAL_LOAD, at_tick)


def broadcast_outcome(world, outcome, at_tick):
    """Fixed broadcast of an actual U/V class, not selection by association map.

    The caller is the declared experience generator/current-outcome sensor.
    Both signal regions receive an identical outcome carrier.  Only a signal
    physically coinciding with that carrier can acquire the tested relation.
    """
    if outcome not in OUTCOME_DIRECTIONS:
        raise ValueError("Current physical outcome class must be U or V")
    return [world.submit("outcome." + signal + "." + outcome, OUTCOME_LOAD, at_tick) for signal in HUBS]


def receipt(rt, identity):
    value = rt.receipt(identity)
    if value is None:
        return {"id": identity, "missing": True}
    return {"id": value.id, "kind": str(value.kind), "status": str(value.status),
            "requested_tick": value.requested_tick, "effective_tick": value.effective_tick,
            "channels": list(value.channels), "reason": value.reason}


def physical(value):
    record = value.record
    return {"tick": value.tick, "site": [value.coordinate.x, value.coordinate.y, value.coordinate.z],
            "raw": value.raw, "clock": value.clock, "state": record.state,
            "semantic": record.semantic, "s_reg": record.s_reg,
            "direction": [record.dx, record.dy, record.dz],
            "active": record.state > 0 and record.semantic != 5}


def read_emission(world, signal, translation=(0, 0, 0)):
    sample = physical(world.runtime.observe(__import__("dee_thinking").Coordinate(*hub(signal, translation))))
    direction = tuple(sample["direction"])
    decoded = {(-1, 1, 0): "U", (-1, -1, 0): "V"}.get(direction) if sample["active"] else None
    return {"modality": "PASSIVE_FIXED_DIRECTION_DECODER", "signal": signal,
            "physical": sample, "anticipated_class": decoded,
            "available": decoded is not None,
            "scope": "Only diagonal signature with dx=-1 is the tested acquired readout; scalar load alone never supplies the class"}


def digest(world):
    rt = world.runtime
    return {"tick": rt.current_tick,
            "raw_sha256": hashlib.sha256(array("Q", rt.raw_copy()).tobytes()).hexdigest(),
            "clock_sha256": hashlib.sha256(array("Q", rt.clock_copy()).tobytes()).hexdigest()}
