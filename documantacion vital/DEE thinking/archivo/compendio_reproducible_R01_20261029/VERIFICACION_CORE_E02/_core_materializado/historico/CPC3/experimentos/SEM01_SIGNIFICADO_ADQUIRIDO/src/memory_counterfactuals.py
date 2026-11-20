"""Explicit selective diagnostic forks for SEM01; never an operational reader.

Every intervention starts from a caller-supplied complete native World.  Native
diagnostic_fork preserves Runtime queues, receipts, channels and World metadata.
The host may know the history solely to locate the intended diagnostic target.
The predictive decoder does not import or call this module.
"""
from __future__ import annotations

from array import array
import hashlib

try:
    from . import memory
except ImportError:
    import memory


def _sha(values):
    return hashlib.sha256(array("Q", values).tobytes()).hexdigest()


def mobile_memory_site(signal, acquired_tick, current_tick, direction_y, translation=(0, 0, 0)):
    if direction_y not in (-1, 1) or current_tick < acquired_tick:
        raise ValueError("Diagnostic target is outside a verified vertical-memory segment")
    return memory.plus(memory.hub(signal, translation), (0, direction_y, 0), current_tick - acquired_tick)


def remove_one_record(world, site, label, expected_direction=None, expected_load=None):
    import dee_thinking as d
    site = tuple(site)
    if len(site) != 3 or any(type(x) is not int or not 0 <= x < memory.N for x in site):
        raise ValueError("A single concrete N67 site must be supplied")
    before = memory.physical(world.runtime.observe(d.Coordinate(*site)))
    if not before["active"]:
        raise ValueError("The declared diagnostic target does not contain an active record")
    if expected_direction is not None and before["direction"] != list(expected_direction):
        raise ValueError("The actual direction differs from the verified diagnostic segment")
    if expected_load is not None and before["s_reg"] != expected_load:
        raise ValueError("The actual load differs from the declared diagnostic record")
    parent_raw = world.runtime.raw_copy()
    parent_clocks = world.runtime.clock_copy()
    parent_receipts = [memory.receipt(world.runtime, r.id) for r in world.runtime.receipts]
    edit = d.ResearchStateEdit()
    edit.coordinate = d.Coordinate(*site)
    edit.raw = 0
    edit.label = label
    # clock is intentionally unset, not assigned zero or reassigned to its old value.
    branch = world.diagnostic_fork([edit], True)
    child_raw = branch.runtime.raw_copy()
    child_clocks = branch.runtime.clock_copy()
    changed = [i for i, (a, b) in enumerate(zip(parent_raw, child_raw)) if a != b]
    expected_index = (site[0] * memory.N + site[1]) * memory.N + site[2]
    assert changed == [expected_index]
    assert child_clocks == parent_clocks
    assert branch.runtime.current_tick == world.runtime.current_tick
    assert [memory.receipt(branch.runtime, r.id) for r in branch.runtime.receipts] == parent_receipts
    assert world.runtime.raw_copy() == parent_raw
    assert world.runtime.clock_copy() == parent_clocks
    after = memory.physical(branch.runtime.observe(d.Coordinate(*site)))
    return branch, {
        "modality": "DIAGNOSTIC_FORK",
        "label": label,
        "tick": world.runtime.current_tick,
        "site": list(site),
        "before": before,
        "after": after,
        "changed_raw_sites": [list(site)],
        "raw_field_edited": True,
        "clock_field_edited": False,
        "clocks_sha256_parent_and_branch": _sha(parent_clocks),
        "parent_raw_sha256": _sha(parent_raw),
        "branch_raw_sha256": _sha(child_raw),
        "receipts_preserved": True,
        "parent_unchanged_at_fork": True,
        "native_external_operations": list(branch.external_operations),
        "scope": "One externally removed record in a complete diagnostic clone; no intervention is merged into the operational MAIN",
    }


def present_reference_action(world, channel, at_tick, payload=21):
    """Explicit direct-actuator input control, never attributed to the memory.

    The named reference-action channel must already exist before T0. This helper
    cannot declare a new channel, reset a clock or install a learned state.
    """
    if channel not in world.runtime.channel_names:
        raise ValueError("Direct actuator control requires its predeclared interface")
    value = world.submit(channel, payload, at_tick)
    return {"modality": "EXPERIENCE_PROTOCOL_DIRECT_ACTUATOR_CONTROL",
            "operation": "submit", "channel": channel, "tick": at_tick,
            "payload": payload, "receipt_id": value.id,
            "scope": "External direct action challenge checks actuator availability; it is not an acquired or autonomous action"}
