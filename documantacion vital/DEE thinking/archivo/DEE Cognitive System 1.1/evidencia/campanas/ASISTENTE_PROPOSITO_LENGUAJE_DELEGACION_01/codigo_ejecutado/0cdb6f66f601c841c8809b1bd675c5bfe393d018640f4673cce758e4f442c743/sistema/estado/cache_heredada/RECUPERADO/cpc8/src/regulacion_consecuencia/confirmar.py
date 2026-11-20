"""Two literal current-medium histories, one frozen translated geometry."""
from pathlib import Path
import argparse
import gc
import json
import sys
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'src'))
from regulacion_consecuencia import run


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', required=True, type=Path)
    args = parser.parse_args()
    cases = json.loads((ROOT / 'configuraciones/regulacion_consecuencia/MCTS_V2_CONGELADO.json').read_text(encoding='utf-8'))['cases']
    for case in cases:
        sys.argv = ['run.py', '--case', case['id'], '--out', str(args.out / case['id'])]
        run.main()
        gc.collect()


if __name__ == '__main__':
    main()
