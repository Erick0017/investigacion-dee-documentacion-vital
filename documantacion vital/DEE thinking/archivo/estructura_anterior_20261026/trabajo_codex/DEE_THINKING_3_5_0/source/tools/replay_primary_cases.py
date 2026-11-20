"""Engineering regression from immutable primary fixtures, not product execution.

Run separately with the installed 3.0 and 3.5 interpreters. Checkpoint fixtures
are read one at a time; reconstructed initial preparations actually evolve.
The public library neither imports this adapter nor accesses the fixture ZIP.
"""
import argparse
from array import array
import gc
import hashlib
import importlib
import json
from pathlib import Path
import sys
import tempfile
import time
import traceback
import zipfile

import dee_thinking as dt

SCIENCE_SHA = "f1f8b6b2f68517f003a21c2908adde49bf1194c7f5657b460563b91ad76f28f0"
SECTION = "02_REPERTORIO_NATIVO_Y_CIERRES"


def sha(p):
    with Path(p).open("rb") as f:
        return hashlib.file_digest(f, "sha256").hexdigest()


def write(p, value):
    p = Path(p); p.parent.mkdir(parents=True, exist_ok=True)
    q = p.with_suffix(p.suffix + ".partial")
    q.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")
    q.replace(p)


def identity(rt):
    return {"tick": rt.current_tick, "dimension": rt.dimension,
            "raw_sha256": hashlib.sha256(array("Q", rt.raw_copy()).tobytes()).hexdigest(),
            "clock_sha256": hashlib.sha256(array("Q", rt.clock_copy()).tobytes()).hexdigest()}


def receipted(rt):
    return [{"id": r.id, "kind": str(r.kind), "status": str(r.status),
             "requested_tick": r.requested_tick, "effective_tick": r.effective_tick,
             "channels": r.channels, "reason": r.reason} for r in rt.receipts]


class Fixtures:
    def __init__(self, archive, scratch):
        self.z = zipfile.ZipFile(archive); self.scratch = Path(scratch)
        self.members = set(self.z.namelist())

    def json(self, member):
        return json.loads(self.z.read(member).decode("utf-8-sig"))

    def runtime(self, member, expected=None):
        member = member.replace("\\", "/")
        b = self.z.read(member)
        if expected is not None and hashlib.sha256(b).hexdigest() != expected:
            raise AssertionError("fixture identity " + member)
        p = self.scratch / "selected_fixture.deetsnap"
        p.write_bytes(b)
        rt = dt.Runtime.load_snapshot(str(p))
        p.unlink()  # Only the explicitly selected temporary copy, not evidence.
        return rt

    def compare(self, rt, entry, prefix=""):
        member = prefix + entry["path"]
        ref = self.runtime(member, entry["sha256"])
        left, right = identity(ref), identity(rt)
        check = {"label": entry["label"], "member": member,
                 "source_snapshot_sha256": entry["sha256"], "reference": left,
                 "reconstructed": right, "physical_equal": left == right,
                 "receipts_equal": receipted(ref) == receipted(rt),
                 "channel_names_equal": ref.channel_names == rt.channel_names,
                 "pause_equal": ref.paused == rt.paused,
                 "protocol_phase_equal": ref.protocol_phase == rt.protocol_phase}
        assert all(check[k] for k in ("physical_equal", "receipts_equal", "channel_names_equal", "pause_equal", "protocol_phase_equal")), check
        del ref
        return check

    def extract_instrumentation(self, target):
        # Exact original modules and small metadata, never every checkpoint.
        for n in sorted(self.members):
            if n.endswith(".py") and (n.startswith("RUNNER/") or n.startswith(SECTION + "/RUNNER/")):
                p = target / n; p.parent.mkdir(parents=True, exist_ok=True); p.write_bytes(self.z.read(n))
        for n in ("CAMPAIGN_CONFIG.json", SECTION + "/EXPERIMENT_CONFIG.json", SECTION + "/PARENT_MEMBERS.json"):
            p = target / n; p.parent.mkdir(parents=True, exist_ok=True); p.write_bytes(self.z.read(n))

    def records(self):
        out = []
        for ledger in ("CASE_LEDGER.jsonl", SECTION + "/CASE_LEDGER.jsonl"):
            by_id = {}
            for line in self.z.read(ledger).decode("utf-8-sig").splitlines():
                if line.strip():
                    row = json.loads(line)
                    if "case" in row: by_id.setdefault(row["case"], []).append(row)
            for case, events in by_id.items():
                if events[-1]["status"] == "TECHNICAL_ERROR": continue
                specs = [e["spec"] for e in events if "spec" in e]
                if not specs:
                    # Four post-emission controls are individually frozen in their case files.
                    specs = [self.json("BRANCHES/" + case + "/CASE_CONFIG.json")]
                spec = specs[-1]
                new = ledger.startswith(SECTION)
                location = ("COMBINATIONS/" if spec.get("combination") else "BRANCHES/")
                if new: location += spec["front"] + "/" + spec["id"]
                else: location += spec["case"] if spec.get("combination") else case
                prefix = SECTION + "/" if new else ""
                original = self.json(prefix + location + "/MEASUREMENTS.json")
                out.append({"case": case, "new": new, "spec": spec, "original": original,
                            "location": prefix + location, "prefix": prefix})
        assert len(out) == 289, len(out)
        return out


def old_context(base, fixtures, record, root):
    class ComparedCase(base.Case):
        def __init__(self):
            super().__init__(root, record["spec"]); self.comparisons = []
        def cp(self, rt, label):
            entry = next(e for e in record["original"]["checkpoints"] if e["label"] == label)
            self.comparisons.append(fixtures.compare(rt, entry))
            self.checkpoints.append(entry)
    return ComparedCase()


def extension_context(base, fixtures, record, root):
    class ComparedContext(base.Context):
        def __init__(self):
            super().__init__(root, record["spec"], None); self.comparisons = []
        def to(self, rt, tick):
            if tick < rt.current_tick: raise ValueError("backwards regression")
            rt.run_until(tick)
        def cp(self, rt, label):
            entry = next(e for e in record["original"]["checkpoints"] if e["label"] == label)
            self.comparisons.append(fixtures.compare(rt, entry, SECTION + "/"))
            self.checkpoints.append(entry); return entry
        def parent_bytes(self, member):
            entry = next(e for e in fixtures.json(SECTION + "/PARENT_MEMBERS.json")["members"] if e["name"] == member)
            b = fixtures.z.read(member); assert hashlib.sha256(b).hexdigest() == entry["sha256"]
            self.parent_sources.append({"member": member, "sha256": entry["sha256"]}); return b
        def parent_runtime(self, member):
            b = self.parent_bytes(member)
            return self.track(fixtures.runtime(member, hashlib.sha256(b).hexdigest()))
        def cut_runtime(self, front, case, label="MAIN_FINAL"):
            m = fixtures.json(SECTION + "/BRANCHES/" + front + "/" + case + "/MEASUREMENTS.json")
            e = next(e for e in m["checkpoints"] if e["label"] == label)
            self.parent_sources.append({"extension_case": front + "/" + case, "label": label, "sha256": e["sha256"]})
            return self.track(fixtures.runtime(SECTION + "/" + e["path"], e["sha256"]))
    return ComparedContext()


def late_replay(ctx, fixtures, spec, obs, branches, apparatus):
    s = spec["spec"]; arm = s["arm"]
    full = fixtures.runtime(s["reference_t13"], s["reference_sha256"])
    rt = ctx.track(fixtures.runtime(s["parent_t8"], s["parent_sha256"]))
    action, env = tuple(s["cut_site"]), tuple(s["copy_environment_site"])
    ctx.cp(rt, "AFTER_NATIVE_ACTION"); edits = []
    if arm != "intact_followup":
        rt, e = apparatus.edited(rt, action, 0, label="late_action_remove"); ctx.track(rt); edits.append(e)
    ctx.to(rt, 45); ctx.cp(rt, "PRE_ENV_REPLAY")
    equalbody = {name: branches.response(rt, q) == branches.response(full, q) for name, q in (("A", (14,15,15)), ("B", (16,15,15)))}
    if arm in ("action_cut_open_replay", "action_cut_identical_copy"):
        raw = full.observe(obs.c(env)).raw if arm == "action_cut_open_replay" else rt.observe(obs.c(env)).raw
        rt, e = apparatus.edited(rt, env, raw, label="external_environmental_replay" if arm == "action_cut_open_replay" else "identical_copy_sham")
        ctx.track(rt); edits.append(e); ctx.cp(rt, "POST_ENV_REPLAY")
    sites = {"A":(14,15,15),"B":(16,15,15),"comparator":(15,15,15),"action":action,"environment":env,"return":(19,19,19),"reader":(15,16,15)}
    rows = []
    for rel in (13,14,17,18,20,26,50,100,131,132,170):
        ctx.to(rt,32+rel)
        rows.append({"relative_tick":rel,"sites":{k:branches.response(rt,q) for k,q in sites.items()},"gateA":obs.gate(rt,(14,15,15)),"gateB":obs.gate(rt,(16,15,15))})
    ctx.cp(rt,"FINAL")
    return {"context_rows": rows, "phi": [[rows[-1]["sites"][k]["s_reg"],rows[-1]["sites"][k]["direction"]] for k in ("A","B","comparator","reader")],
            "interventions": edits, "matched_A_B_before_replay": equalbody}


def check_subset(left, right, name):
    assert len(left) == len(right), name + " length"
    for a, b in zip(left, right):
        assert all(k in b and b[k] == v for k, v in a.items()), (name, a, b)


def run(args):
    archive = Path(args.science).resolve(); out = Path(args.output).resolve()
    out.mkdir(parents=True, exist_ok=True)
    assert sha(archive) == SCIENCE_SHA
    binary = Path(importlib.import_module("dee_thinking._native").__file__)
    tool_sha = sha(__file__); binary_sha = sha(binary)
    with tempfile.TemporaryDirectory(prefix="dt35-primary-") as scratch:
        fixtures = Fixtures(archive, scratch); extracted = Path(scratch) / "instruments"
        fixtures.extract_instrumentation(extracted)
        module_dir = extracted / (SECTION + "/RUNNER" if args.suite == "extension" else "RUNNER")
        sys.path.insert(0, str(module_dir))
        base = importlib.import_module("run_extension_02" if args.suite == "extension" else "run_multibranch")
        handlers = importlib.import_module("frontiers" if args.suite == "extension" else "branches")
        obs = importlib.import_module("observations"); apparatus = importlib.import_module("apparatus")
        work = Path(scratch) / "regression"
        work.mkdir()
        if args.suite == "extension":
            write(work / "EXPERIMENT_CONFIG.json", fixtures.json(SECTION + "/EXPERIMENT_CONFIG.json"))
        records = [r for r in fixtures.records() if r["new"] == (args.suite == "extension")]
        count = 0
        for record in records:
            if args.case and args.case != record["case"]: continue
            report_path = out / (record["case"].replace("/", "__") + ".json")
            if report_path.exists() and not args.retry:
                prior = json.loads(report_path.read_text(encoding="utf-8"))
                if prior.get("status") == "PASS" and prior.get("science_sha256") == SCIENCE_SHA and prior.get("native_binary_sha256") == binary_sha:
                    print("SKIP_VERIFIED", record["case"], flush=True); continue
            spec = record["spec"]; original = record["original"]; started = time.perf_counter()
            report = {"case": record["case"], "source_member": record["location"] + "/MEASUREMENTS.json",
                      "science_sha256": SCIENCE_SHA, "adapter_sha256": tool_sha, "version": dt.__version__,
                      "native_binary_sha256": binary_sha, "fixture_only_not_runtime_dependency": True}
            if report_path.exists():
                previous = json.loads(report_path.read_text(encoding="utf-8"))
                report["previous_attempts"] = previous.get("previous_attempts", []) + [{k: v for k, v in previous.items() if k != "previous_attempts"}]
            ctx = None
            try:
                if args.suite == "extension":
                    ctx = extension_context(base, fixtures, record, work)
                    result = handlers.HANDLERS[spec["handler"]](ctx, spec["parameters"])
                else:
                    ctx = old_context(base, fixtures, record, work)
                    result = late_replay(ctx, fixtures, spec, obs, handlers, apparatus) if spec["kind"] == "late_contingency_replay" else handlers.HANDLERS[spec["kind"]](ctx, spec["spec"])
                assert result.get("phi") == original.get("phi"), "functional panel differs"
                assert len(ctx.comparisons) == len(original["checkpoints"]), "checkpoint coverage differs"
                if args.suite == "extension":
                    check_subset(original["external_calls"], ctx.inputs, "recorded calls")
                    assert original["diagnostic_writes"] == ctx.edits, "diagnostic writes differ"
                    source_ops = fixtures.json(record["location"] + f"/attempt_{original['attempt']:03d}/OPERATIONS.json")
                    expected = [{"tick": r["tick"], "events": r["events"]} for r in source_ops["receipts_by_runtime"]]
                    actual = [{"tick": r.current_tick, "events": receipted(r)} for r, _ in ctx.runtimes.values()]
                    if expected != actual:
                        report["receipt_difference"] = {"expected":expected,"actual":actual}
                        # The historical P03 replay used an unregistered read-only
                        # T54 reference; the later helper registers it. Preserve
                        # both inventories, rather than inventing an extra run.
                        if record["case"] == "P03/late_action_open_replay" and len(actual)==len(expected)+1:
                            reference_only = actual[2]
                            assert reference_only == {"tick":86,"events":[]}, "auxiliary reference changed"
                            actual = actual[:2]+actual[3:]
                            report["historical_instrumentation_difference"] = "Later cut_runtime registers read-only T54 reference; excluded from paired execution receipt comparison, retained above"
                    assert expected == actual, "receipt histories differ"
                    if "query_order" in original: assert result["query_order"] == original["query_order"], "query order differs"
                    report["recorded_calls_receipts_edits_equal"] = True
                report.update({"status": "PASS", "comparisons": ctx.comparisons, "panel_equal": True,
                               "execution_type": "SOURCE_DEPENDENCY_ONLY" if spec.get("handler") == "missing_historical" else "REREAD_RECALCULATED" if spec.get("handler") == "reread" else "PHYSICAL_REPLAY",
                               "ticks_evolved": sum(r.current_tick - t for r,t,*_ in ctx.runtimes.values())})
            except Exception as error:
                report.update({"status": "FAIL", "error": str(error), "traceback": traceback.format_exc(),
                               "comparisons": [] if ctx is None else ctx.comparisons})
            report["seconds"] = time.perf_counter() - started
            write(report_path, report); print(report["status"], record["case"], round(report["seconds"], 3), report.get("error", ""), flush=True)
            del ctx; gc.collect(); count += 1
            if args.limit and count >= args.limit: break
        reports = [json.loads(p.read_text(encoding="utf-8")) for p in out.glob("*.json") if p.name != "SUMMARY.json"]
        summary = {"suite": args.suite, "version": dt.__version__, "science_sha256": SCIENCE_SHA,
                   "source_records": len(records), "completed_reports": len(reports), "passed": sum(r["status"] == "PASS" for r in reports),
                   "failed": [r["case"] for r in reports if r["status"] != "PASS"],
                   "physical_replays": sum(r.get("execution_type") == "PHYSICAL_REPLAY" for r in reports),
                   "rereads": sum(r.get("execution_type") == "REREAD_RECALCULATED" for r in reports),
                   "not_executed_source_unrecovered": [r["case"] for r in reports if r.get("execution_type") == "SOURCE_DEPENDENCY_ONLY"],
                   "checkpoint_comparisons": sum(len(r.get("comparisons", [])) for r in reports)}
        write(out / "SUMMARY.json", summary)
        print(json.dumps(summary), flush=True)
        return 1 if summary["failed"] else 0


if __name__ == "__main__":
    p = argparse.ArgumentParser(); p.add_argument("--science", required=True); p.add_argument("--output", required=True)
    p.add_argument("--suite", choices=["inherited", "extension"], required=True); p.add_argument("--case"); p.add_argument("--limit", type=int); p.add_argument("--retry", action="store_true")
    raise SystemExit(run(p.parse_args()))
