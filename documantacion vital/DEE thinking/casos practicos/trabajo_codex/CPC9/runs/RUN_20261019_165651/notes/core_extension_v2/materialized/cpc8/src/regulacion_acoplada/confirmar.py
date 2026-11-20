"""Frozen factorial and reserves, each a distinct fresh native preparation."""
from pathlib import Path
import argparse
import gc
import json
import sys
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'src'))
from regulacion_acoplada import ejecutar


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', required=True, type=Path)
    args = parser.parse_args()
    config = json.loads((ROOT / 'configuraciones/regulacion_acoplada/FACTORIAL_CONGELADO.json').read_text(encoding='utf-8'))
    for case in config['cases']:
        sys.argv = ['ejecutar.py', '--case', case['id'], '--medium', str(case['medium']),
                    '--reference', str(case['reference']), '--objects', *map(str, case['objects']),
                    '--routing', case['routing'], '--out', str(args.out / case['id'])]
        ejecutar.main()
        gc.collect()


if __name__ == '__main__':
    main()
