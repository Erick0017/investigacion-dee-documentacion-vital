"""Fixed B-material-to-external-valve codec; no target/reference/private input.

Observe both declared buses once at the frozen critical+30 boundary. Exactly
one qualified load5 horizontal material carrier commands its signed unit step.
No signal/conflict makes no valve action. This is prepared external coupling,
not native A-context replacement or a closed-v27 communication claim.
"""

REVISION = "EO01.B_external_valve.codec.1"
BUS_MINUS = (12, 19, 9)
BUS_PLUS = (0, 19, 9)
SAMPLE_OFFSET = 30
LOAD = 5


def raw_fields(q):
    value = q["raw"]
    if not isinstance(value, str) or not value.isdecimal():
        raise ValueError("Exact decimal RAW required")
    raw = int(value)
    if not 0 <= raw < 2**64:
        raise ValueError("RAW outside uint64")
    def signed(k):
        v = (raw >> k) & 15
        return v - 16 if v & 8 else v
    return {"raw": value, "state": raw & 0xffffffff, "s_reg": (raw >> 32) & 65535,
            "semantic": (raw >> 60) & 15, "direction": [signed(k) for k in (48, 52, 56)]}


def decode_b_bus(minus, plus):
    readings = [{"sign": sign, "site": list(site), "fields": raw_fields(q)}
                for sign, site, q in ((-1, BUS_MINUS, minus), (1, BUS_PLUS, plus))]
    qualified = [q for q in readings if q["fields"]["state"] > 0 and q["fields"]["semantic"] == 1
                 and q["fields"]["s_reg"] == LOAD and q["fields"]["direction"] == [q["sign"], 0, 0]]
    command = qualified[0]["sign"] if len(qualified) == 1 else None
    return {"revision": REVISION, "readings": readings, "qualified_messages": len(qualified),
            "formed_valve_step": command, "reason": "unique_native_message" if command is not None else
            "conflicting_messages" if len(qualified) > 1 else "no_valid_message",
            "mechanical_mapping": "External calibration changes by exactly formed_valve_step, never toward a computed correct calibration"}
