"""CF01's sole alternative preparation: one-tick first-turn supply delay.

This constructs a NEW T0 recipe derived from R9. It never loads, edits,
cleans or rearranges the fields of an existing learned life. The two generic
load5 supplies move one step upstream; their target heads and all other
anatomy remain fixed. Selection, input content and future actions are not
computed by this constructor.
"""
from capacidades.geometria_distribuida_mi02_r9 import unified_recipe as baseline
from capacidades.geometria_distribuida_mi02 import compile_geometry


def unified_recipe(control="intact"):
    _, g = baseline(control)
    n = g["N"]
    anchors = {tuple(q["site"]): (q["load"], tuple(q["direction"])) for q in g["anchors"]}
    opened = {tuple(q) for q in g["opened"]}
    pinned = {tuple(q) for q in g["pinned"]}
    modifications = []
    names = {"B.-1.first", "B.1.first"}
    selected = [q for q in g["prepared_sources"] if q["id"] in names]
    if len(selected) != 2:
        raise ValueError("Exact two R9 first-turn resources required")
    for source in selected:
        old = tuple(source["site"])
        direction = tuple(source["direction"])
        if source["distance"] != 3 or source["load"] != 5 or direction != (0, 1, 1):
            raise ValueError("Unchanged official R9 first-turn source contract required")
        if anchors.get(old) != (5, direction):
            raise ValueError("R9 first-turn source anchor differs")
        new = tuple((old[i] - direction[i]) % n for i in range(3))
        if new in anchors or new in pinned:
            raise ValueError("New upstream source collides with another prepared component")
        if old in pinned:
            raise ValueError("Original source unexpectedly pinned")
        anchors.pop(old)
        anchors[new] = (5, direction)
        opened.update((old, new))
        source["site"] = list(new)
        source["distance"] = 4
        source["CF01_prepared_delay_ticks"] = 1
        modifications.append({"source_id": source["id"], "old_origin": list(old),
                              "new_origin": list(new), "head_unchanged": source["head"],
                              "direction_unchanged": list(direction), "load_unchanged": 5,
                              "old_distance": 3, "new_distance": 4})
    g.update({"schema": "CF01.unified.r10", "base_protocol_schema": "MI02.unified.r9",
              "CF01_revision": "R10_ONLY_COMPLETE_ALTERNATIVE",
              "CF01_source_changes": modifications,
              "anchors": [{"site": list(p), "load": v[0], "direction": list(v[1])}
                          for p, v in sorted(anchors.items())],
              "opened": [list(p) for p in sorted(opened)],
              "pinned": [list(p) for p in sorted(pinned)],
              "CF01_hypothesis": "With the first-turn generic source delayed one geometric step, "
                  "an odd-tick B output caused by an even-boundary direct datum may meet the resource "
                  "at an empty head rather than die against its occupied phase. Actual delivery, "
                  "reference retention, query reuse and utility must be measured; no success is presumed.",
              "CF01_limits": "New T0 body; inherits mechanisms but no R9 learned state or biography. "
                  "Changing source parity may impair original private-message delivery. No new source "
                  "contains a private sign, remembered magnitude, answer, policy or target.",
              "new_preparation_not_repair_of_existing_life": True})
    return compile_geometry(n, opened, anchors, pinned), g
