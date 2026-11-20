"""Installed public API only. No laboratory imports, fixtures or oracles."""
import argparse
from pathlib import Path
import tempfile
import dee_thinking as d


def example(folder):
    w = d.create_organization("mobile_pair")
    for j, teacher in enumerate((7, 11)):
        w.submit(f"l{j}.cue", 5, 0)
        w.submit(f"l{j}.teacher", teacher, 0)
    w.run_until(6)
    separate = w.fork()
    for j in range(2): separate.probe(f"q{j}.query", 13, 6)
    separate.run_until(11)
    decoder = d.OutputDecoder()
    print("independent physical responses", [separate.decode(f"q{j}", "response", decoder).integer for j in range(2)])
    w.start_mobile_sequence("declared_queries", [13, 7, 17])
    w.run_until(13)
    snapshot = str(folder / "public_mid_protocol.deetsnap")
    w.save_snapshot(snapshot)
    restored = d.OrganizationalWorld.load_snapshot(snapshot)
    restored.run_until(21)
    print("continued protocol", [[o.record.s_reg for o in step.captured] for step in restored.protocols[0].steps])
    # A different physical family and a same-Runtime mobile/basal bridge.
    bridge = d.create_organization("mobile_basal")
    trace = d.TraceSession(); trace.sample_budget = 16
    trace.sites = {"comparator": bridge.view("body").spec.comparator}
    bridge.set_trace(trace); bridge.advance(6)
    print("bridge passive panel", bridge.view("body").observe().delta, bridge.observe("body", "comparator").record.s_reg)
    branch = bridge.fork()
    branch.probe("body.common_query", 7, branch.runtime.current_tick)
    branch.advance(3)
    print("fork physical probe", branch.observe("body", "comparator").record.dx)
    bridge.save_snapshot(str(folder / "public_bridge.deetsnap"))
    bridge.trace().export_trace(str(folder / "public_bridge.deetrace"))
    print("snapshots", folder)


if __name__ == "__main__":
    p = argparse.ArgumentParser(); p.add_argument("--output", type=Path)
    a = p.parse_args()
    if a.output:
        a.output.mkdir(parents=True, exist_ok=True); example(a.output)
    else:
        with tempfile.TemporaryDirectory(prefix="dee-public-") as temp: example(Path(temp))
