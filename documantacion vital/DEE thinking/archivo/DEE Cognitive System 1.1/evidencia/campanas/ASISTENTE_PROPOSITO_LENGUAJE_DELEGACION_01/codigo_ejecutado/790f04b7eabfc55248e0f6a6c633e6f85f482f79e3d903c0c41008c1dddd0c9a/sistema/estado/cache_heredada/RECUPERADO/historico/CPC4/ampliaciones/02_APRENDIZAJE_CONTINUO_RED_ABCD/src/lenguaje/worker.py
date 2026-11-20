"""One supervised lexical continuation or fresh network+language realization."""
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))


def main():
    parser = argparse.ArgumentParser(); parser.add_argument("--case", required=True)
    parser.add_argument("--output", required=True); parser.add_argument("--parent")
    args = parser.parse_args(); case = json.loads(Path(args.case).read_text(encoding="utf-8"))
    from red.session_v3 import NetworkSession
    from lenguaje.protocol import run
    if args.parent:
        session = NetworkSession.load(args.parent)
    else:
        session = NetworkSession.create(case.get("network", {"roles": True}), tuple(case.get("translation", [0, 0, 0])))
        session.run_until(431)
    _, result = run(session, case, Path(args.output))
    print(json.dumps({"id": case.get("id"), "readouts": result["readouts"]}, ensure_ascii=False))


if __name__ == "__main__": main()
