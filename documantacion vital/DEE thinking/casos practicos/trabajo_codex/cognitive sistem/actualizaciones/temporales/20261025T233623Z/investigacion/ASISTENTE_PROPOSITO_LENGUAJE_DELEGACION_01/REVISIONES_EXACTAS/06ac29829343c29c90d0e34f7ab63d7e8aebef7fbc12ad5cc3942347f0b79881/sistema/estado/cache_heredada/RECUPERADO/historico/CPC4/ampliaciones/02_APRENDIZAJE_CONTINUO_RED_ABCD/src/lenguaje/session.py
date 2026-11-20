"""Inert linguistic view of an already experienced, persistent ABCD session.

Two finite lessons and two physical queries.  Textual aliases identify ports;
they never select an answer.  The resource sensor is an explicit external
transducer, while all stored relations and responses evolve under v27.
"""
from __future__ import annotations
import json
from pathlib import Path

from .protocol import (FORMS, observe, profile, teach, query_word, name_current_profile,
                       digest, until)

KEY = "cpc4.extension02.continuous_language.neutral.v2"


class GroundedSession:
    def __init__(self, network, state):
        self.network, self.state = network, state

    @classmethod
    def attach(cls, network, word_order=("L1", "L2"), teaching="paired", second_episode=True):
        """Attach does not install matter, change clocks, or recreate the body."""
        tick = network.world.runtime.current_tick
        if tick not in (431, 1431): raise ValueError("Validated post-experience boundary431 or1431 required")
        if network.world.runtime.snapshot_metadata(KEY): raise ValueError("A finite linguistic protocol already exists")
        if sorted(word_order) != ["L1", "L2"]: raise ValueError("Two declared form identities required")
        if teaching not in ("paired", "unpaired", "signal_omitted", "report_omitted"): raise ValueError("Unknown experience contract")
        if network.world.runtime.paused or any(str(x.status) == "scheduled" for x in network.world.runtime.receipts):
            raise ValueError("No paused state or unexplained pending input at language entry")
        state = {"version": 2, "base_tick": tick, "tick": tick, "stage": "UNTAUGHT",
                 "word_order": list(word_order), "teaching_mode": teaching,
                 "lesson_cursor": 0, "query_cursor": 0, "calls": [],
                 "forms": dict(FORMS), "external_episode_scheduled": False,
                 "second_episode_enabled": bool(second_episode),
                 "scope": "Only protocol progress and external form identity; no class map, target, cached output or utility"}
        result = cls(network, state); result._commit(); return result

    @property
    def world(self): return self.network.world

    @property
    def tick(self): return self.world.runtime.current_tick

    def _commit(self):
        self.state["tick"] = self.tick
        self.world.runtime.set_snapshot_metadata(KEY, json.dumps(self.state, separators=(",", ":")))

    def _check_live(self):
        if self.world.runtime.paused: raise ValueError("Paused linguistic MAIN; no progress or nominal emission invented")
        if self.tick != self.state["tick"]: raise ValueError("Native time changed outside this finite protocol view")
        if set(self.world.runtime.channel_names) != {x.name for x in self.world.interfaces}: raise ValueError("Channel/interface mismatch")

    def teach_next(self):
        self._check_live(); slot = self.state["lesson_cursor"]; base = self.state["base_tick"]
        if slot not in (0, 1) or self.state["query_cursor"]: raise ValueError("Only two pre-query lessons are declared")
        calls = self.state["calls"]
        if slot == 0:
            if self.tick != base: raise ValueError("First lesson requires its actual entry boundary")
            sensed = profile(self.world, self.network.spec["role"], base - 14)
        else:
            # New world opportunity is fixed and independent of an emitted action.
            if self.state["external_episode_scheduled"]: raise ValueError("Do not repeat the world episode")
            if self.state["second_episode_enabled"]:
                for channel, load, tick in (("world.resource", 3, base + 7), ("world.supply", 7, base + 13),
                                            ("world.U", 11, base + 8)):
                    rec = self.world.submit(channel, load, tick)
                    calls.append({"id": rec.id, "channel": channel, "load": load, "requested_tick": tick,
                                  "call_tick": self.tick, "modality": "EXPERIENCE_PROTOCOL"})
            self.state["external_episode_scheduled"] = True
            until(self.network, base + 28)
            sensed = profile(self.world, self.network.spec["bank"], base + 7)
        at = base + 28 * slot; form = self.state["word_order"][slot]
        result = teach(self.network, form, sensed, at, self.state["teaching_mode"], calls)
        # Undefined actual class is reported, not manufactured.  Advance the
        # empty interval so a missing experience is not a different hidden age.
        if self.tick < at + 3: until(self.network, at + 3)
        self.state["lesson_cursor"] += 1
        self.state["stage"] = "FIRST_EXPERIENCE" if slot == 0 else "READY_FOR_TWO_QUERIES"
        self._commit(); return result

    def query_next_word(self, form):
        self._check_query(form)
        tick = self.state["base_tick"] + (67, 95)[self.state["query_cursor"]]
        result = query_word(self.network, form, tick, self.state["calls"])
        self._after_query(); return result

    def name_next_profile(self, source):
        self._check_query()
        if source not in ("role", "second"): raise ValueError("Choose a declared current sensor, not an expected word")
        base = self.state["base_tick"]
        bank, emitted = (self.network.spec["role"], base - 14) if source == "role" else (self.network.spec["bank"], base + 7)
        tick = base + (67, 95)[self.state["query_cursor"]]
        result = name_current_profile(self.network, bank, emitted, tick, self.state["calls"])
        # Explicit new local observer: a rejected input at another region does
        # not erase this region's actual admitted26.  The original discovery
        # global decoder remains byte-exact and its conservative result kept.
        local = {}
        for lane, record in result["actual"].items():
            rr = [r for r in result["receipts"] if any(c.startswith("lex." + lane + ".") for c in r["channels"])]
            good = (len(rr) == 2 and all(r["status"] == "applied" for r in rr)
                    and result["sensor"]["class_sign"] is not None and record["active"]
                    and record["semantic"] == 1 and record["s_reg"] == 26
                    and record["direction"] in ([0, 1, 0], [0, -1, 0]))
            local[lane] = {"valid": bool(good), "form": FORMS[lane] if good else None, "receipts": rr, "physical": record}
        result["local_region_decoder"] = local
        result["locally_emitted_forms"] = [x["form"] for x in local.values() if x["valid"]]
        result["observer_revision"] = "Local Applied receipts required independently per region; frozen before new confirmation"
        self._after_query(); return result

    def _check_query(self, form=None):
        self._check_live()
        if self.state["lesson_cursor"] != 2 or self.state["query_cursor"] not in (0, 1):
            raise ValueError("Finite domain: two lessons followed by two queries; no unlimited renewal")
        if form is not None and form not in FORMS: raise ValueError("Unregistered physical form")

    def _after_query(self):
        self.state["query_cursor"] += 1
        self.state["stage"] = "FIRST_QUERY" if self.state["query_cursor"] == 1 else "COMPLETE_FINITE_DOMAIN"
        self._commit()

    def observe(self):
        self._check_live(); before = digest(self.world)
        panel = {lane: observe(self.world, p) for lane, p in self.network.spec["lexical_hubs"].items()}
        if digest(self.world) != before: raise RuntimeError("Passive observation changed physical MAIN")
        return {"tick": self.tick, "stage": self.state["stage"], "current_fields": panel,
                "modality": "PASSIVE_OBSERVATION", "next_queries_remaining": 2 - self.state["query_cursor"],
                "scope": "Actual current fields; no historical response is replayed"}

    def save(self, path):
        self._check_live(); self._commit(); return self.network.save(path)

    @classmethod
    def load(cls, path):
        from red.session_v3 import NetworkSession
        network = NetworkSession.load(path); text = network.world.runtime.snapshot_metadata(KEY)
        if not text or len(text) > 131072: raise ValueError("Missing finite linguistic continuity metadata")
        state = json.loads(text)
        if state.get("version") != 2 or state.get("base_tick") not in (431, 1431): raise ValueError("Unknown language schema")
        if state.get("tick") != network.world.runtime.current_tick or state.get("forms") != FORMS: raise ValueError("Altered time/form interface")
        if sorted(state.get("word_order", [])) != ["L1", "L2"]: raise ValueError("Altered form order")
        if type(state.get("lesson_cursor")) is not int or state["lesson_cursor"] not in (0, 1, 2): raise ValueError("Invalid lesson cursor")
        if type(state.get("query_cursor")) is not int or state["query_cursor"] not in (0, 1, 2): raise ValueError("Invalid query cursor")
        if state["query_cursor"] and state["lesson_cursor"] != 2: raise ValueError("Query before actual experience")
        expected_offsets = { (0,0): 0, (1,0): 3, (2,0): 31, (2,1): 70, (2,2): 98 }
        # Unpaired is a declared different protocol, whose lesson adds one tick.
        offset = expected_offsets.get((state["lesson_cursor"], state["query_cursor"]))
        if offset is None: raise ValueError("Unsupported phase")
        if state.get("teaching_mode") == "unpaired" and state["lesson_cursor"] and not state["query_cursor"]: offset += 1
        if state["tick"] != state["base_tick"] + offset: raise ValueError("Phase/tick mismatch")
        for call in state.get("calls", []):
            r = network.world.runtime.receipt(call["id"])
            if r is None or r.requested_tick != call["requested_tick"] or list(r.channels) != [call["channel"]]: raise ValueError("Lost/changed operative receipt")
        result = cls(network, state); result._check_live(); return result
