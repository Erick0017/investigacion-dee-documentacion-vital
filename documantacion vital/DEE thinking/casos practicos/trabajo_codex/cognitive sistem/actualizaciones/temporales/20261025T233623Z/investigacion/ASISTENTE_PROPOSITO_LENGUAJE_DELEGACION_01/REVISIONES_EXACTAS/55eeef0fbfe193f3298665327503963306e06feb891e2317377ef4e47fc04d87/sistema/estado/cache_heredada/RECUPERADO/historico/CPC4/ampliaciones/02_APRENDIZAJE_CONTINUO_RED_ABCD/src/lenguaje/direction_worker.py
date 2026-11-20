import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]; sys.path.insert(0, str(ROOT / "src"))


def main():
    p = argparse.ArgumentParser(); p.add_argument("--case", required=True); p.add_argument("--parent", required=True)
    p.add_argument("--output", required=True); a = p.parse_args()
    from red.session_v3 import NetworkSession
    from lenguaje.directions import run
    case = json.loads(Path(a.case).read_text(encoding="utf-8")); network = NetworkSession.load(a.parent)
    _, result = run(network, case, Path(a.output))
    print(json.dumps({"id": case["id"], "actual_source_signs": [x["observed_sign"] for x in result["experiences"]],
                      "readouts": result["readouts"], "old_retention": result["old_retention_panel"]}, ensure_ascii=False))


if __name__ == "__main__": main()
