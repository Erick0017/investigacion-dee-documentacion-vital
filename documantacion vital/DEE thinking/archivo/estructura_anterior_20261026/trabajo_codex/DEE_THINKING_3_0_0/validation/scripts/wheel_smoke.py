from __future__ import annotations

import pathlib
import tempfile

import dee_thinking as dee


origin = pathlib.Path(dee.__file__).resolve()
assert dee.__version__ == "3.0.0"
assert dee.kernel_identity()["kernel_version"] == 27
assert "site-packages" in str(origin).casefold()
assert all(
    hasattr(dee, name)
    for name in (
        "BasalWorld",
        "BasalConfig",
        "PassiveTracker",
        "inspect_write_gate",
        "compare_diagnostic_fork",
    )
)

world = dee.create_relational_world(dee.BasalHistory.AB)
assert world.runtime.current_tick == 32
assert world.observe().delta == 0
world.advance(1)
assert world.observe().delta == 1

with tempfile.TemporaryDirectory() as temporary:
    snapshot = pathlib.Path(temporary) / "user-roundtrip.deetsnap"
    world.save_snapshot(str(snapshot))
    restored = dee.BasalWorld.load_snapshot(str(snapshot))
    world.advance(8)
    restored.advance(8)
    assert world.runtime.raw_copy() == restored.runtime.raw_copy()
    assert world.runtime.clock_copy() == restored.runtime.clock_copy()

contextual = dee.create_contextual_world()
tracked = contextual.fork()
b_site = dee.TrackedSite()
b_site.id = "B"
b_site.site = tracked.ports.b
tracker = dee.PassiveTracker([b_site], 4)
tracker.capture(tracked.runtime)
tracked.advance(1)
tracker.capture(tracked.runtime)
assert len(tracker.frames) == 2

contextual.advance(131)
gate = dee.inspect_write_gate(contextual.runtime, contextual.ports.b, True)
assert gate.local_clock == 391
assert gate.n_active == 6
assert gate.ordinary_increment_condition
parent_raw = contextual.runtime.raw_copy()
parent_clock = contextual.runtime.clock_copy()
edit = dee.ResearchStateEdit()
edit.coordinate = contextual.ports.b
edit.clock = 392
edit.label = "external_user.phase_miss"
comparison = dee.compare_diagnostic_fork(contextual, [edit], 1, True)
assert comparison.parent_unchanged
assert contextual.runtime.raw_copy() == parent_raw
assert contextual.runtime.clock_copy() == parent_clock

print("dee_thinking_version=3.0.0")
print("kernel_version=27")
print("module_origin_site_packages=true")
print("basal_api=true")
print("documented_roundtrip=true")
print("contextual_gate=true")
print("passive_tracker=true")
print("diagnostic_parent_unchanged=true")
