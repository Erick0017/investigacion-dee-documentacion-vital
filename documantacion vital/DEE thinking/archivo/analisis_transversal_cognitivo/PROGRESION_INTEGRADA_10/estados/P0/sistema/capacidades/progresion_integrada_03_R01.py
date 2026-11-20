"""Draft opt-in PI03 calibration plugin for the EXISTING Genesis owner.

Import and literal validation use only the standard library. No owner, life,
Runtime, ACTIVO change or shell command is created by this module. Root must
seal PROTOCOLO_PI03_R01.json before any material dispatch. Native execution is
confined to an explicitly identified diagnostic life and its admitted owner.

Calibration valence is imposed by the researcher. It is NOT useful learning,
an environmental task, autonomy or a positive PI03 result by itself.
"""
from pathlib import Path
import hashlib
import importlib.util
import json
import os

VERSION = "PI03.existing_owner_temporal_credit.R01_DRAFT"
KEY = "DEE.Cognitive.PI03.generic_temporal_credit.R01"
SYSTEM_KEY = "DEE.Cognitive.System.1.1.life.v1"
FOLDER = "PI03_CREDITO_TEMPORAL_R01"
PROTOCOL = Path(__file__).with_name("PROTOCOLO_PI03_R01.json")
PREPARE = "eci01-pi03-preparar"
CALIBRATE = "eci01-pi03-calibrar"
STATE = "eci01-pi03-estado"
MODES = {PREPARE, CALIBRATE, STATE}
ARMS = {"paired_failure", "paired_nonfailure", "no_efference_failure", "unpaired_failure"}
_HELPER = None


def _hash(data):
    return hashlib.sha256(data).hexdigest()


def _helper():
    global _HELPER
    if _HELPER is None:
        file = Path(__file__).with_name("pi03_credito_generico_R01_BORRADOR.py")
        spec = importlib.util.spec_from_file_location("pi03_credito_generico_R01_draft", file)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        _HELPER = module
    return _HELPER


def protocol(*, executable=True):
    data = PROTOCOL.read_bytes()
    p = json.loads(data)
    required = {"schema", "status", "candidate", "origin", "prefix", "N",
                "diagnostic_life_prefix", "protected_life_ids", "calibration_delay_laps",
                "reserved_delay_laps", "zero_motor", "unpaired_shift_ticks",
                "max_ticks_per_calibration", "require_pi02_paused", "helper_sha256"}
    if set(p) != required:
        raise ValueError("Exact sealed protocol fields required; no target/answer/reader override")
    if p["schema"] != "PI03.generic_temporal_credit.protocol.v1" or p["N"] != 67:
        raise ValueError("Only the inherited N67 declared protocol")
    if executable and p["status"] != "SEALED_FOR_CALIBRATION":
        raise ValueError("Draft protocol is deliberately not executable; root must fix geometry and seal it")
    if p["diagnostic_life_prefix"] != "ECI02_PI03_":
        raise ValueError("Only the existing owner-compatible explicit PI03 diagnostic namespace")
    if executable and (not isinstance(p["origin"], list) or len(p["origin"]) != 3
                       or any(type(x) is not int or not 0 <= x < 67 for x in p["origin"])):
        raise ValueError("One fixed in-range geometry selected before calibration is required")
    if p["zero_motor"] not in (-1, 1) or type(p["zero_motor"]) is not int:
        raise ValueError("Fixed material-zero motor transduction must be -1 or +1; NULL never acts")
    if p["calibration_delay_laps"] != [1, 2] or p["reserved_delay_laps"] != [3, 4]:
        raise ValueError("Frozen development/reserve delay split only")
    if p["unpaired_shift_ticks"] != 1 or not p["require_pi02_paused"]:
        raise ValueError("This draft requires a one-tick unpairing and explicit inherited bridge pause")
    if type(p["max_ticks_per_calibration"]) is not int or not 1000 <= p["max_ticks_per_calibration"] <= 2000:
        raise ValueError("Finite Native horizon required")
    helper_file = Path(__file__).with_name("pi03_credito_generico_R01_BORRADOR.py")
    if executable and _hash(helper_file.read_bytes()) != p["helper_sha256"]:
        raise ValueError("Exact reviewed helper bytes differ from the sealed protocol")
    return p, _hash(data)


def validate_literal(row):
    mode = row.get("modo") if isinstance(row, dict) else None
    if mode in (PREPARE, STATE):
        if set(row) != {"modo"}:
            raise ValueError("Only modo; geometry and reader come from the sealed protocol")
        return
    if mode == CALIBRATE:
        if set(row) != {"modo", "condicion", "demora_periodos"}:
            raise ValueError("Exact calibration condition and delay only; no action or expected answer")
        if row["condicion"] not in ARMS or type(row["demora_periodos"]) is not int or row["demora_periodos"] not in (1, 2):
            raise ValueError("Four fixed calibration arms and development delay1/2 only")
        return
    raise ValueError("Unknown explicit PI03 operation")


def _decode(value):
    from dee_thinking.persistence import decode_metadata
    return decode_metadata(value)


def _save(a, value):
    from dee_thinking.persistence import encode_metadata
    a.world.runtime.set_snapshot_metadata(KEY, encode_metadata(value))


def _get(a):
    entries = dict(a.world.runtime.snapshot_metadata_entries)
    if KEY not in entries:
        raise ValueError("No explicitly installed PI03 anatomy; no implicit preparation")
    m = _decode(entries[KEY])
    if m["version"] != VERSION:
        raise ValueError("PI03 snapshot protocol version mismatch")
    return m


def _identity(a, p, directory=None):
    entries = dict(a.world.runtime.snapshot_metadata_entries)
    if SYSTEM_KEY not in entries:
        raise ValueError("Complete Cognitive life identity metadata required")
    identity = _decode(entries[SYSTEM_KEY])
    life = identity["life_id"]
    if not life.startswith(p["diagnostic_life_prefix"]) or life in p["protected_life_ids"]:
        raise ValueError("This draft rejects protected/main/non-diagnostic lives")
    if int(a.world.runtime.dimension) != p["N"]:
        raise ValueError("No N change or new world is admitted")
    if directory is not None and Path(directory).resolve().name != life:
        raise ValueError("Diagnostic work directory must identify this exact life")
    if directory is not None:
        # Existing service path: estado/servicios_locales/<life>. Never mutate
        # the currently selected global main even after a PI03 life is adopted.
        active_file = Path(directory).resolve().parents[1] / "ACTIVO.json"
        if active_file.is_file():
            selected = json.loads(active_file.read_text(encoding="utf-8-sig"))
            if selected.get("life_id", selected.get("preferred_life")) == life:
                raise ValueError("Material calibration refuses the currently selected main")
    inherited = "DEE.Cognitive.PI02.continuous_workbench.R04"
    if p["require_pi02_paused"] and inherited in entries and _decode(entries[inherited]).get("enabled"):
        raise ValueError("Pause the inherited PI02 bridge explicitly before diagnostic calibration; no silent withdrawal")
    return identity


def validate(a, row):
    validate_literal(row)
    if row["modo"] == STATE:
        return
    p, ph = protocol()
    _identity(a, p)
    entries = dict(a.world.runtime.snapshot_metadata_entries)
    if row["modo"] == PREPARE:
        if KEY in entries:
            raise ValueError("Already prepared; preserve history, never reinstall")
        return
    m = _get(a)
    if m["protocol_sha256"] != ph or not m.get("ready"):
        raise ValueError("Installed apparatus and sealed protocol do not match or are incomplete")
    if m.get("uncertain") or m.get("pending") or m.get("terminal_control"):
        raise ValueError("Unreconciled/terminal control future; no implicit retry or new eligibility")
    if m.get("calibration_arm") not in (None, row["condicion"]):
        raise ValueError("A control life cannot silently change its declared arm")


def _record(a, m, directory, event):
    home = Path(directory) / FOLDER
    home.mkdir(parents=True, exist_ok=True)
    event = {"index": m["log_count"], "tick": int(a.tick), **event}
    data = (json.dumps(event, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")
    with (home / "eventos.jsonl").open("ab") as out:
        out.write(data)
        out.flush()
        os.fsync(out.fileno())
    m["log_count"] += 1
    m["log_chain_sha256"] = _hash(bytes.fromhex(m["log_chain_sha256"]) + data)
    _save(a, m)


def _frame(a, p, label):
    from app.native_tools import observe, physical
    points = _helper().geometry_footprint(p["origin"], halo=1)
    observations = []
    for site in points:
        o = observe(a.world, site)
        # Full precision: no uint64 value passes through a float or JS number.
        o["raw"] = str(o["raw"])
        o["clock"] = str(o["clock"])
        observations.append(dict(o, site=site))
    return {"kind": "PASSIVE_FRAME", "label": label, "physical": physical(a.world, occupation=True),
            "observations": observations,
            "coverage": "Fixed apparatus/query footprint, full periodic eligibility row, Moore halo1; whole-world RAW/clocks hashes and occupation, not whole-world lineage tracking"}


def _receipts(a, requests):
    from dee_thinking.consolidated import exact_receipt
    return [dict(r, receipt=exact_receipt(a.world.runtime.receipt(r["id"]))) for r in requests]


def prepare(a, directory):
    p, ph = protocol()
    identity = _identity(a, p, directory)
    home = Path(directory) / FOLDER
    if home.exists():
        raise ValueError("An unmatched existing apparatus directory is preserved, never reused")
    start = int(a.tick)
    m = {"version": VERSION, "protocol_sha256": ph, "life_id": identity["life_id"],
         "prepared_tick": start, "origin": p["origin"], "prefix": p["prefix"],
         "ready": False, "uncertain": True, "pending": {"phase": "installing"},
         "calibration_arm": None, "calibrations": 0, "terminal_control": False,
         "log_count": 0, "log_chain_sha256": "00" * 32,
         "scope": "External protocol/progress only; no actor-accessible policy or historical solution table"}
    _save(a, m)
    _record(a, m, directory, {"kind": "PREPARATION_INTENT", "protocol": p, "identity": identity})
    result = _helper().install_legal(a, p["origin"], prefix=p["prefix"], halo=1)
    m["ready"] = result["ready"]
    m["uncertain"] = not result["ready"]
    m["pending"] = None if result["ready"] else {"phase": "incomplete_installation"}
    _record(a, m, directory, {"kind": "P0_LEGAL_PREPARATION", "result": result})
    _record(a, m, directory, _frame(a, p, "after_preparation"))
    return {"version": VERSION, "prepared": m["ready"], "before_tick": start,
            "after_tick": int(a.tick), "new_native_ticks": int(a.tick) - start,
            "result": result, "attribution": "Prepared anatomy only; not acquired capacity"}


def calibrate(a, row, directory):
    p, ph = protocol()
    _identity(a, p, directory)
    m = _get(a)
    helper = _helper()
    from app.native_tools import observe, physical
    start = int(a.tick)
    refs = [observe(a.world, helper.at(p["origin"], v)) for v in ((-1, -1, 0), (1, -1, 0))]
    if int(refs[0]["clock"]) % 782 != int(refs[1]["clock"]) % 782:
        raise ValueError("Reference phases diverged; no clock repair")
    calendar = helper.schedule_trial(start, int(refs[0]["clock"]), row["demora_periodos"])
    arm = row["condicion"]
    shift = p["unpaired_shift_ticks"] if arm == "unpaired_failure" else 0
    final_query_tick = calendar["contact_tick"] + 8
    final_read_tick = final_query_tick + 6
    if final_read_tick - start > p["max_ticks_per_calibration"]:
        raise ValueError("Frozen calibration exceeds finite Native horizon")
    m["calibration_arm"] = arm
    m["pending"] = {"phase": "planned", "calendar": calendar, "arm": arm,
                    "index": m["calibrations"], "note": "One pending material trial; no prior-action bank lookup at return"}
    m["uncertain"] = True
    _record(a, m, directory, {"kind": "CALIBRATION_INTENT", "calendar": calendar,
                            "arm": arm, "physical": physical(a.world, occupation=True)})
    requests = helper.submit_query(a.world, calendar["query_tick"], prefix=p["prefix"])
    m["pending"]["request_ids"] = [r["id"] for r in requests]
    _save(a, m)
    a.run_until(calendar["query_read_tick"])
    initial = helper.read_fixed(a.world, p["origin"])
    raw_choice = initial["choice"]
    # This is one FIXED actuator convention. NULL never receives a substitute.
    motor = p["zero_motor"] if raw_choice == 0 else raw_choice
    motor = motor if type(motor) is int and motor in (-1, 1) else None
    copy = None
    if arm != "no_efference_failure" and motor is not None:
        copy = helper.submit_motor_copy(a.world, motor, calendar["seed_tick"], prefix=p["prefix"])
        requests.append(copy)
    _record(a, m, directory, {"kind": "ACTUAL_QUERY_AND_FIXED_EFFERENCE", "initial_reader": initial,
                            "motor_after_fixed_codec": motor, "material_zero_codec_applied": raw_choice == 0,
                            "copy_request": copy,
                            "attribution": "Material zero->fixed default is P0; NULL does not act; calibration schedules opportunity"})
    # Deliberately no motor/route argument or lookup on this path. This outcome
    # is an imposed calibration condition, not a claimed useful task result.
    outcome = helper.submit_generic_outcome(a.world, arm != "paired_nonfailure",
                calendar["outcome_injection_tick"] + shift, prefix=p["prefix"])
    requests.append(outcome)
    m["pending"] = {"phase": "waiting_generic_outcome", "calendar": calendar,
                    "arm": arm, "request_ids": [r["id"] for r in requests],
                    "note": "No prior motor choice stored in the outcome progress capsule"}
    _save(a, m)
    frames = {calendar["seed_tick"] + 1: "efference_first_step",
              calendar["seed_tick"] + 33: "eligibility_half_lap",
              calendar["collision_tick"] - 2: "pre_outcome",
              calendar["collision_tick"] - 1: "outcome_boundary_before_admission",
              calendar["collision_tick"]: "hub_arrival",
              calendar["contact_tick"]: "reference_contact",
              calendar["contact_tick"] + 1: "reference_update_and_disposal",
              calendar["contact_tick"] + 2: "post_contact_context"}
    if row["demora_periodos"] == 2:
        frames[calendar["seed_tick"] + 67] = "eligibility_one_complete_lap"
    for tick, label in sorted(frames.items()):
        if tick < int(a.tick):
            raise ValueError("Frozen frame calendar would rewind; preserve reached state")
        a.run_until(tick)
        _record(a, m, directory, _frame(a, p, label))
    final_requests = helper.submit_query(a.world, final_query_tick, prefix=p["prefix"])
    requests.extend(final_requests)
    m["pending"]["request_ids"] = [r["id"] for r in requests]
    _save(a, m)
    a.run_until(final_read_tick)
    final = helper.read_fixed(a.world, p["origin"])
    receipts = _receipts(a, requests)
    result = {"version": VERSION, "kind": "imposed_valence_calibration", "arm": arm,
              "before_tick": start, "after_tick": int(a.tick), "new_native_ticks": int(a.tick) - start,
              "calendar": calendar, "initial_reader": initial, "final_reader": final,
              "motor_after_fixed_codec": motor, "requests": receipts,
              "physical_after": physical(a.world, occupation=True),
              "scope": "Mechanical Native calibration only. No external useful task or autonomous exploration was executed."}
    m["calibrations"] += 1
    m["terminal_control"] = arm in ("no_efference_failure", "unpaired_failure")
    # Unpaired/no-copy returns may leave native residual carriers; this draft
    # never erases them or silently makes another trial from the same future.
    admitted = all(r["receipt"]["status"] == "applied" for r in receipts)
    m["pending"] = None if admitted else {"phase": "rejected_inputs_preserved", "request_ids": [r["id"] for r in requests]}
    m["uncertain"] = not admitted
    _record(a, m, directory, {"kind": "CALIBRATION_COMPLETED", "result": result,
                            "terminal_control": m["terminal_control"]})
    return result


def state(a, directory=None):
    from app.native_tools import physical
    entries = dict(a.world.runtime.snapshot_metadata_entries)
    return {"version": VERSION, "admitted": KEY in entries,
            "progress": _get(a) if KEY in entries else None,
            "physical": physical(a.world, occupation=True), "new_native_ticks": 0,
            "scope": "Passive instrument/protocol state; no material query, life creation or automatic repair"}


def dispatch(a, row, *, directory=None, actuator="closed"):
    validate(a, row)
    if row["modo"] == STATE:
        return state(a, directory)
    if directory is None or actuator != "closed":
        raise ValueError("Explicit diagnostic operational directory and calibration actuator only")
    if row["modo"] == PREPARE:
        return prepare(a, directory)
    return calibrate(a, row, directory)


def uncertain(a):
    entries = dict(a.world.runtime.snapshot_metadata_entries)
    return KEY in entries and bool(_get(a).get("uncertain"))


def operational_dependencies(a, directory):
    entries = dict(a.world.runtime.snapshot_metadata_entries)
    if KEY not in entries:
        return {"version": VERSION, "admitted": False, "new_native_ticks": 0}
    m = _get(a)
    p, ph = protocol()
    _identity(a, p, directory)
    if m["protocol_sha256"] != ph:
        raise ValueError("Installed protocol differs from preserved source bytes")
    journal = Path(directory) / FOLDER / "eventos.jsonl"
    chain = "00" * 32
    count = 0
    with journal.open("rb") as rows:
        for line in rows:
            json.loads(line)
            chain = _hash(bytes.fromhex(chain) + line)
            count += 1
    if count != m["log_count"] or chain != m["log_chain_sha256"]:
        raise ValueError("PI03 progress/journal mismatch; preserve state and reconcile, never reset")
    return {"version": VERSION, "admitted": True, "protocol_sha256": ph,
            "journal": str(journal), "journal_bytes": journal.stat().st_size,
            "journal_sha256": _hash(journal.read_bytes()), "log_count": count,
            "pending": m["pending"], "uncertain": m["uncertain"],
            "scope": "Complete Runtime agenda/interfaces/receipts remain in the owner's full snapshot. SQLite/outbox/transport IDs stay under the existing PersistentService contract; this plugin never replaces or purges them."}
