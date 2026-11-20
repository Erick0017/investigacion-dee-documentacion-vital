"""Loader-only hardening of the frozen experimental linguistic facilitator.

No dynamics, recipes, teaching, query, decoder or historical result is changed.
The measured source remains byte-exact in continuous02/EXECUTED_SOURCE.  This
wrapper is for the public interactive view and rejects a foreign pending teacher
instead of allowing a later word-only query to be misattributed.
"""
from .session import GroundedSession as ExperimentalGroundedSession


class GroundedSession(ExperimentalGroundedSession):
    @classmethod
    def load(cls, path):
        result = super().load(path)
        state = result.state
        if any(str(x.status) == "scheduled" for x in result.world.runtime.receipts):
            raise ValueError("Unexpected pending input at a completed published language boundary")
        if state.get("teaching_mode") not in ("paired", "unpaired", "signal_omitted", "report_omitted"):
            raise ValueError("Unknown physical teaching mode")
        for key in ("second_episode_enabled", "external_episode_scheduled"):
            if type(state.get(key)) is not bool: raise ValueError("Boolean protocol flag required: " + key)
        expected = {(0,0): "UNTAUGHT", (1,0): "FIRST_EXPERIENCE", (2,0): "READY_FOR_TWO_QUERIES",
                    (2,1): "FIRST_QUERY", (2,2): "COMPLETE_FINITE_DOMAIN"}
        if state.get("stage") != expected[(state["lesson_cursor"], state["query_cursor"])]:
            raise ValueError("Neutral stage/cursor mismatch")
        calls = state.get("calls")
        if not isinstance(calls, list) or len(calls) > 64: raise ValueError("Bounded physical call history required")
        ids = []
        for call in calls:
            identifier, channel = call.get("id"), call.get("channel")
            if type(identifier) is not int or not isinstance(channel, str): raise ValueError("Malformed physical call")
            ids.append(identifier)
            if not (channel.startswith("lex.L") or channel in ("world.resource", "world.supply", "world.U")):
                raise ValueError("Unexpected linguistic protocol input")
            actual = result.world.runtime.receipt(identifier)
            expected_kind = "experience" if call.get("modality") == "EXPERIENCE_PROTOCOL" else "probe"
            if str(actual.kind) != expected_kind: raise ValueError("Physical receipt kind mismatch")
        if len(ids) != len(set(ids)): raise ValueError("Duplicate operative receipt identity")
        return result
