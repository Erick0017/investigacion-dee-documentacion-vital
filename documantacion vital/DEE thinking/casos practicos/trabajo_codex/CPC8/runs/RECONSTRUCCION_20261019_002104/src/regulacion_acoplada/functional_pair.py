"""One new frozen operand separating intact/corrupted native responses."""
from pathlib import Path
import argparse
import gc
import json
import sys
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'src'))
from regulacion_acoplada import ejecutar, run_mcts


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    cfg = json.loads((ROOT / 'configuraciones/regulacion_acoplada/PAR_FUNCIONAL_CONGELADO.json').read_text(encoding='utf-8'))
    for case in cfg['cases']:
        sys.argv = ['runner', '--case', case['id'], '--medium', str(case['medium']), '--reference', str(case['reference']),
                    '--objects', *map(str, case['objects']), '--out', str(args.out / case['id'])]
        (ejecutar.main if case['family'] == 'AUX' else run_mcts.main)()
        gc.collect()


if __name__ == '__main__':
    main()
