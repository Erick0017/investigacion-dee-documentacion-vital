"""JSONL transport for the published Gymnasium Pendulum-v1. No policy or DEE code.

Call with Python 3.11: python -I -B pendulum_worker.py --deps PATH
One request/response per line: info, reset(seed,g), step(torque), snapshot,
restore(snapshot), close. Snapshot contains physical state, RNG and wrapper state.
All hidden state in responses is auditor-only; only observation is sensor data.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import math
from pathlib import Path
import sys
import traceback


def safe(value):
    if hasattr(value, "tolist"):
        return safe(value.tolist())
    if hasattr(value, "item"):
        return safe(value.item())
    if isinstance(value, dict):
        return {str(k): safe(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [safe(v) for v in value]
    return value


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--deps", type=Path, default=Path(__file__).with_name("deps"))
    args = parser.parse_args()
    if args.deps.is_dir():
        sys.path.insert(0, str(args.deps.resolve()))
    import gymnasium as gym
    import numpy as np
    from gymnasium.envs.classic_control import pendulum

    source = Path(pendulum.__file__)
    identity = {
        "environment": "Pendulum-v1", "gymnasium": gym.__version__,
        "numpy": np.__version__, "python": sys.version,
        "source_path": str(source),
        "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
        "wrapper_contract": "TimeLimit<OrderEnforcing<PendulumEnv>>",
        "dt": 0.05, "torque_bounds": [-2.0, 2.0],
        "neutral_torque": 0.0, "max_episode_steps": 200,
    }
    env = None
    elapsed = 0
    gravity = 10.0

    def create(g):
        nonlocal env, elapsed, gravity
        if env is not None:
            env.close()
        gravity = float(g)
        if not math.isfinite(gravity) or gravity < 0 or gravity > 100:
            raise ValueError("gravity out of declared range [0,100]")
        env = gym.make("Pendulum-v1", g=gravity, disable_env_checker=True)
        if env.unwrapped.dt != 0.05 or env.unwrapped.max_torque != 2.0 or env.unwrapped.max_speed != 8.0:
            raise ValueError("published Pendulum constants differ from frozen bridge contract")
        elapsed = 0

    def export():
        if env is None or env.unwrapped.state is None:
            raise ValueError("reset is required")
        base = env.unwrapped
        wrappers = []
        wrapper = env
        while wrapper is not base:
            name = type(wrapper).__name__
            if name not in {"TimeLimit", "OrderEnforcing"}:
                raise ValueError("unsupported wrapper: " + name)
            row = {"class": name}
            for key in ("_elapsed_steps", "_max_episode_steps", "_has_reset", "_disable_render_order_enforcing"):
                if key in wrapper.__dict__:
                    row[key] = safe(wrapper.__dict__[key])
            wrappers.append(row)
            wrapper = wrapper.env
        return {
            "schema": "gymnasium-pendulum-state-1", "identity": identity,
            "gravity_hex": gravity.hex(),
            "state_float64_hex": [float(x).hex() for x in base.state],
            "last_u_hex": None if base.last_u is None else float(base.last_u).hex(),
            "np_random_state": safe(base.np_random.bit_generator.state),
            "np_random_seed": safe(base.np_random_seed),
            "action_rng_state": safe(env.action_space.np_random.bit_generator.state),
            "observation_rng_state": safe(env.observation_space.np_random.bit_generator.state),
            "wrappers": wrappers, "elapsed": elapsed,
        }

    def restore(snapshot):
        nonlocal elapsed
        if snapshot["schema"] != "gymnasium-pendulum-state-1":
            raise ValueError("snapshot schema mismatch")
        for key in ("environment", "gymnasium", "numpy", "source_sha256"):
            if snapshot["identity"][key] != identity[key]:
                raise ValueError("dependency identity mismatch: " + key)
        create(float.fromhex(snapshot["gravity_hex"]))
        env.reset(seed=0)
        base = env.unwrapped
        base.state = np.array([float.fromhex(x) for x in snapshot["state_float64_hex"]], dtype=np.float64)
        base.last_u = None if snapshot["last_u_hex"] is None else float.fromhex(snapshot["last_u_hex"])
        base.np_random.bit_generator.state = snapshot["np_random_state"]
        base._np_random_seed = snapshot["np_random_seed"]
        env.action_space.np_random.bit_generator.state = snapshot["action_rng_state"]
        env.observation_space.np_random.bit_generator.state = snapshot["observation_rng_state"]
        wrapper = env
        for row in snapshot["wrappers"]:
            if type(wrapper).__name__ != row["class"]:
                raise ValueError("wrapper order mismatch")
            for key, value in row.items():
                if key != "class":
                    setattr(wrapper, key, value)
            wrapper = wrapper.env
        elapsed = int(snapshot["elapsed"])
        return safe(base._get_obs())

    for line in sys.stdin:
        request = None
        try:
            request = json.loads(line)
            op = request["op"]
            if op == "info":
                result = {"identity": identity}
            elif op == "reset":
                create(request.get("g", 10.0))
                observation, info = env.reset(seed=int(request["seed"]))
                result = {"observation": safe(observation), "info": safe(info), "elapsed": 0}
            elif op == "step":
                if env is None:
                    raise ValueError("reset or restore is required")
                if elapsed >= 200:
                    raise ValueError("episode truncated: explicit reset required; DEE memory must not reset")
                requested = float(request["torque"])
                if not math.isfinite(requested):
                    raise ValueError("non-finite torque")
                applied = max(-2.0, min(2.0, requested))
                observation, reward, terminated, truncated, info = env.step(np.array([applied], dtype=np.float32))
                elapsed += 1
                result = {
                    "observation": safe(observation), "reward": float(reward),
                    "terminated": bool(terminated), "truncated": bool(truncated),
                    "requested_torque": requested, "applied_torque": applied,
                    "torque_saturated": requested != applied, "elapsed": elapsed,
                    "simulated_seconds": elapsed * env.unwrapped.dt,
                    "info": safe(info),
                }
            elif op == "snapshot":
                result = {"snapshot": export()}
            elif op == "restore":
                result = {"observation": restore(request["snapshot"]), "elapsed": elapsed}
            elif op == "close":
                if env is not None:
                    env.close()
                print(json.dumps({"ok": True, "op": op}), flush=True)
                return
            else:
                raise ValueError("unknown operation")
            print(json.dumps({"ok": True, "op": op, **result}, ensure_ascii=False, allow_nan=False), flush=True)
        except Exception as exc:
            print(json.dumps({"ok": False, "op": None if request is None else request.get("op"),
                              "error": type(exc).__name__ + ": " + str(exc)}, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
