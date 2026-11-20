"""Technical transport/persistence tests only: no DEE participant or learning."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from datetime import datetime, timezone


class Client:
    def __init__(self, worker, deps):
        self.command = [sys.executable, "-I", "-B", "-u", str(worker), "--deps", str(deps)]
        self.process = subprocess.Popen(self.command, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                        stderr=subprocess.PIPE, text=True, encoding="utf-8")

    def request(self, op, **values):
        self.process.stdin.write(json.dumps({"op": op, **values}, allow_nan=False) + "\n")
        self.process.stdin.flush()
        line = self.process.stdout.readline()
        if not line:
            raise RuntimeError("worker exited: " + self.process.stderr.read())
        return json.loads(line)

    def close(self):
        if self.process.poll() is None:
            self.request("close")
            self.process.wait(timeout=10)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--deps", type=Path, default=Path(__file__).with_name("deps"))
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    worker = Path(__file__).with_name("pendulum_worker.py")
    first, second = Client(worker, args.deps), Client(worker, args.deps)
    report = {"kind": "EXTERNAL_WORKER_TECHNICAL_TEST_NOT_E1", "utc": datetime.now(timezone.utc).isoformat(),
              "worker_sha256": hashlib.sha256(worker.read_bytes()).hexdigest(), "checks": {}}
    try:
        info = first.request("info")
        report["identity"] = info
        assert info["ok"]
        reset = first.request("reset", seed=71001)
        assert reset["ok"]
        report["reset"] = reset
        prefix = [first.request("step", torque=x) for x in [0.0, 2.0, -2.0, 0.5, 0.0]]
        assert all(x["ok"] for x in prefix)
        snapshot = first.request("snapshot")["snapshot"]
        restored = second.request("restore", snapshot=snapshot)
        assert restored["ok"]
        restored_snapshot = second.request("snapshot")["snapshot"]
        assert restored_snapshot == snapshot
        report["checks"]["snapshot_full_wrapper_rng_exact"] = True
        future_a, future_b = [], []
        for action in [2.0, 0.0, -2.0, -0.5, 0.0, 2.0, 0.0, -2.0]:
            future_a.append(first.request("step", torque=action))
            future_b.append(second.request("step", torque=action))
        assert future_a == future_b
        assert first.request("snapshot") == second.request("snapshot")
        report["checks"]["cross_process_eight_step_exact_continuation"] = True
        report["prefix"] = prefix
        report["snapshot"] = snapshot
        report["same_future"] = future_a
        assert first.request("step", torque=3.0)["torque_saturated"]
        report["checks"]["saturation_reported"] = True
        for _ in range(200 - 14):
            terminal = first.request("step", torque=0.0)
        assert terminal["ok"] and terminal["truncated"] and not terminal["terminated"]
        denied = first.request("step", torque=0.0)
        assert not denied["ok"]
        report["checks"]["explicit_reset_after_step_200"] = True
        report["terminal"] = terminal
        report["post_truncation_rejection"] = denied
        zero_g = second.request("reset", seed=71001, g=0.0)
        zero_g_next = second.request("step", torque=0.0)
        normal_g = first.request("reset", seed=71001, g=10.0)
        normal_g_next = first.request("step", torque=0.0)
        assert zero_g["observation"] == normal_g["observation"]
        assert zero_g_next["observation"] != normal_g_next["observation"]
        report["checks"]["published_gravity_parameter_affects_physics"] = True
        report["gravity_contrast"] = {"g0": zero_g_next, "g10": normal_g_next}
        report["interpretation"] = "JSONL, gravity and exact persistence are tested; no E1 action, control competence or learning is claimed."
    finally:
        first.close()
        second.close()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(args.output), "checks": report["checks"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
