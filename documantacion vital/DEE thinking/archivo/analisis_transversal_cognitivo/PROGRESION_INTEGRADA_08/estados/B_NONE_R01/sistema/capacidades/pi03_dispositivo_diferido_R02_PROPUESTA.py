"""Pure external-device proposal for PI03, NOT a DEE policy or Native runner.

Two physical output commands select two bounded feeder conduits. Only one is
connected to the receiver during an exogenously fixed block. A real capsule
enters an inflight conduit at action time. At a fixed later deadline the device
either decompresses it into a useful product or keeps it in the rejected sink.
The actual result yields only a generic failure bool for the DEE return API.

This file never imports DEE, chooses a motor command, reads a Native state,
opens arbitrary user files, launches shell/network processes, or updates DEE.
No experiment or filesystem self-test is run on import or as a CLI.
"""
from pathlib import Path
import hashlib
import json
import os
import zlib

VERSION = "PI03.delayed_material_feeder.R02_PROPOSAL"


def sha(data):
    return hashlib.sha256(data).hexdigest()


def _atomic_json(path, data):
    # A bounded, fixed internal filename; never accept a participant path.
    path = Path(path)
    temp = path.with_name(path.name + ".pending")
    if temp.exists():
        raise ValueError("Uncertain previous environment write; never overwrite it")
    with temp.open("x", encoding="utf-8") as out:
        json.dump(data, out, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False)
        out.write("\n")
        out.flush()
        os.fsync(out.fileno())
    os.replace(temp, path)


class DelayedFeeder:
    """One pending bounded external action; journals are NOT agent memory.

    `blocks` is a frozen list of `{opportunities, connected_motor}`. It is an
    environment law, private from DEE, not a table consulted to choose actions.
    Reversal changes this law only between completed attempts. Unknown reversal
    cannot be anticipated from an identical observation: the first error after
    it is not scored as failure to predict an imperceptible change.
    """
    @classmethod
    def prepare(cls, directory, blocks, *, fixture_id="PI03.R02", payloads=None):
        home = Path(directory).resolve()
        if home.exists():
            raise ValueError("Explicit fresh external-device destination required")
        if not isinstance(blocks, list) or not 1 <= len(blocks) <= 8:
            raise ValueError("A finite frozen block law is required")
        for row in blocks:
            if set(row) != {"opportunities", "connected_motor"} or type(row["opportunities"]) is not int or not 1 <= row["opportunities"] <= 12 or type(row["connected_motor"]) is not int or row["connected_motor"] not in (-1, 1):
                raise ValueError("Exact bounded environment law; no expected response table")
        count = sum(row["opportunities"] for row in blocks)
        if payloads is not None and (not isinstance(payloads, list) or len(payloads) != count or any(not isinstance(v, bytes) or not 1 <= len(v) <= 256 for v in payloads)):
            raise ValueError("One actual bounded byte payload per opportunity")
        home.mkdir(parents=True, exist_ok=False)
        for folder in ("reservoir", "inflight_minus", "inflight_plus", "inflight_silence", "products", "rejected"):
            (home / folder).mkdir()
        capsules = []
        for i in range(count):
            # Fixture bytes are irrelevant to route selection. They never encode
            # the connected conduit or a motor answer. An optional real Native
            # result may supply bytes under a separately declared fixed codec.
            payload = payloads[i] if payloads is not None else hashlib.sha256((fixture_id + ":" + str(i)).encode("utf-8")).digest() * 2
            encoded = zlib.compress(payload, level=6)
            name = "%04d.zlib" % i
            (home / "reservoir" / name).write_bytes(encoded)
            capsules.append({"name": name, "compressed_bytes": len(encoded), "compressed_sha256": sha(encoded),
                             "decoded_bytes": len(payload), "decoded_sha256": sha(payload)})
        m = {"version": VERSION, "blocks": blocks, "capsules": capsules,
             "opportunity": 0, "pending": None, "feedback_pending": None, "uncertain": False,
             "products": [], "rejections": [], "events": 0,
             "scope": "External device and progress only, not a Native policy or actor-accessible memory"}
        _atomic_json(home / "ESTADO_DISPOSITIVO.json", m)
        return cls(home)

    def __init__(self, directory):
        self.home = Path(directory).resolve()
        self.statefile = self.home / "ESTADO_DISPOSITIVO.json"
        self.m = json.loads(self.statefile.read_text(encoding="utf-8"))
        if self.m["version"] != VERSION:
            raise ValueError("External device revision mismatch")

    def _save(self):
        _atomic_json(self.statefile, self.m)

    def _record(self, event):
        event = {"index": self.m["events"], **event}
        data = (json.dumps(event, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")
        with (self.home / "EVENTOS_DISPOSITIVO.jsonl").open("ab") as out:
            out.write(data)
            out.flush()
            os.fsync(out.fileno())
        self.m["events"] += 1
        self._save()
        return event

    def _connected(self, opportunity):
        end = 0
        for row in self.m["blocks"]:
            end += row["opportunities"]
            if opportunity < end:
                return row["connected_motor"]
        raise ValueError("Finite prepared opportunities exhausted")

    def begin(self, actual_motor, action_tick, ready_tick):
        """Apply the actual motor; never infer it from the environment law."""
        if actual_motor is not None and (type(actual_motor) is not int or actual_motor not in (-1, 1)):
            raise ValueError("Only an actual binary action or declared NULL")
        if type(action_tick) is not int or type(ready_tick) is not int or ready_tick <= action_tick:
            raise ValueError("A genuinely later external consequence deadline is required")
        if self.m["pending"] is not None or self.m["feedback_pending"] is not None or self.m["uncertain"]:
            raise ValueError("Only one pending device action; no silent retry")
        i = self.m["opportunity"]
        connected = self._connected(i)
        cap = self.m["capsules"][i]
        src = self.home / "reservoir" / cap["name"]
        if not src.is_file() or sha(src.read_bytes()) != cap["compressed_sha256"]:
            raise ValueError("Missing/altered actual resource; no synthetic replacement")
        folder = "inflight_minus" if actual_motor == -1 else "inflight_plus" if actual_motor == 1 else "inflight_silence"
        dst = self.home / folder / cap["name"]
        if dst.exists():
            raise ValueError("Existing prior conduit artifact; preserve and reconcile")
        # The conduit identity is the physical state of the external actuator,
        # not a record used by the DEE credit transducer to pick a bank.
        self.m["uncertain"] = True
        self.m["pending"] = {"index": i, "conduit": folder, "connected_motor_latched": connected,
                             "action_tick": action_tick, "ready_tick": ready_tick,
                             "capsule": cap, "phase": "before_conduit_move"}
        self._save()
        src.replace(dst)
        self.m["pending"]["phase"] = "inflight"
        self.m["uncertain"] = False
        return self._record({"kind": "ACTUATOR_APPLIED", "actual_motor": actual_motor,
                            "action_tick": action_tick, "ready_tick": ready_tick,
                            "conduit_file": str(dst), "opportunity": i,
                            "attribution": "Fixed physical action-to-conduit mapping; no returned bank selected"})

    def complete_due(self, tick):
        """Observe a real delayed product, return one generic failed bool.

        Call at the predeclared device deadline, before scheduling a FUTURE
        generic DEE input. The returned feedback capsule contains no route,
        motor or expected response. Audit files remain outside agent access.
        """
        pending = self.m["pending"]
        if pending is None or self.m["uncertain"] or pending["phase"] != "inflight":
            raise ValueError("One certain unfinished external action is required")
        if type(tick) is not int or tick != pending["ready_tick"]:
            raise ValueError("Fixed deadline missed; never adapt time to rescue a response")
        cap = pending["capsule"]
        src = self.home / pending["conduit"] / cap["name"]
        encoded = src.read_bytes()
        if sha(encoded) != cap["compressed_sha256"]:
            raise ValueError("Actual inflight resource changed; preserve uncertainty")
        connected_folder = "inflight_minus" if pending["connected_motor_latched"] == -1 else "inflight_plus"
        accepted = pending["conduit"] == connected_folder
        self.m["uncertain"] = True
        self._save()
        if accepted:
            product = zlib.decompress(encoded)
            if len(product) != cap["decoded_bytes"] or sha(product) != cap["decoded_sha256"]:
                raise ValueError("Real device output integrity failure; do not substitute expected bytes")
            dst = self.home / "products" / ("%04d.bin" % pending["index"])
            with dst.open("xb") as out:
                out.write(product)
                out.flush()
                os.fsync(out.fileno())
            # Preserve original encoded resource as consumed evidence; no delete.
            consumed = self.home / "products" / cap["name"]
            src.replace(consumed)
            result = {"index": pending["index"], "path": dst.relative_to(self.home).as_posix(), "bytes": len(product), "sha256": sha(product)}
            self.m["products"].append(result)
        else:
            dst = self.home / "rejected" / cap["name"]
            src.replace(dst)
            result = {"index": pending["index"], "path": dst.relative_to(self.home).as_posix(), "bytes": len(encoded), "sha256": sha(encoded)}
            self.m["rejections"].append(result)
        self.m["opportunity"] += 1
        self.m["pending"] = None
        self.m["uncertain"] = False
        feedback = {"failed": not accepted, "consequence_tick": tick,
                    "actual_product_bytes": result["bytes"] if accepted else 0,
                    "actual_product_sha256": result["sha256"] if accepted else None,
                    "native_request": None, "phase": "due_not_transduced",
                    "feedback_boundary": "Only failed is transduced to a generic DEE outcome; no route/action/bank field"}
        self.m["feedback_pending"] = feedback
        self._record({"kind": "DELAYED_CONSEQUENCE", "tick": tick, "failed": not accepted,
                      "actual_material_result": result,
                      "scope": "64-byte fixture is an external resource, not energy, food or thermodynamics"})
        return dict(feedback)

    def mark_feedback_scheduled(self, request_id, requested_tick):
        """Persist the EXACT already-created Native ID; never submit/retry it.

        The existing owner must checkpoint this state, Native agenda/receipts,
        SQLite transport and the device artifacts coherently. This helper is
        not a substitute for that transaction/continuation contract.
        """
        feedback = self.m["feedback_pending"]
        if self.m["uncertain"] or feedback is None or feedback["phase"] != "due_not_transduced" or feedback["native_request"] is not None:
            raise ValueError("No unique unscheduled generic outcome; never resubmit an ambiguous request")
        if type(request_id) is not int or request_id < 1 or type(requested_tick) is not int or requested_tick <= feedback["consequence_tick"]:
            raise ValueError("Exact positive receipt ID and a future Native boundary required")
        feedback["native_request"] = {"id": request_id, "requested_tick": requested_tick}
        feedback["phase"] = "scheduled_receipt_unreconciled"
        self._record({"kind": "GENERIC_FEEDBACK_SCHEDULED", "native_request": feedback["native_request"],
                      "scope": "Transport/progress only; no route lookup or retransmission"})

    def reconcile_feedback(self, exact_receipt):
        """Accept an existing exact receipt, no DEE import or new event."""
        feedback = self.m["feedback_pending"]
        if feedback is None or feedback["phase"] != "scheduled_receipt_unreconciled":
            raise ValueError("No unique pending generic Native receipt to reconcile")
        if exact_receipt.get("id") != feedback["native_request"]["id"]:
            raise ValueError("Receipt ID mismatch; preserve the uncertain future")
        status = exact_receipt.get("status")
        if status == "scheduled":
            return {"finished": False, "status": status, "new_native_ticks": 0}
        if status != "applied":
            self.m["uncertain"] = True
            feedback["phase"] = "rejected_feedback_preserved"
            feedback["receipt"] = exact_receipt
            self._record({"kind": "GENERIC_FEEDBACK_REJECTED", "receipt": exact_receipt})
            return {"finished": False, "status": status, "new_native_ticks": 0}
        self.m["feedback_pending"] = None
        self._record({"kind": "GENERIC_FEEDBACK_APPLIED", "receipt": exact_receipt})
        return {"finished": True, "status": status, "new_native_ticks": 0}
