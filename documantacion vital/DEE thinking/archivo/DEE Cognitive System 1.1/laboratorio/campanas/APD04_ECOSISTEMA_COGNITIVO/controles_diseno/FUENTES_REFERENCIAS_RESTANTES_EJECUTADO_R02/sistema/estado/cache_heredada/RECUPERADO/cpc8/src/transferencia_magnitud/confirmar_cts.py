"""Four frozen CTS confirmation worlds; never repeat the completed pilot."""
from pathlib import Path
import argparse
import gc
import json
import sys
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'src'))
from transferencia_magnitud import run_cts


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    cfg = json.loads((ROOT / 'configuraciones/transferencia_magnitud/CTS_CONGELADO.json').read_text(encoding='utf-8'))
    for case in cfg['cases'][1:]:
        sys.argv = ['run_cts.py', '--case', case['id'], '--out', str(args.out / case['id'])]
        run_cts.main()
        gc.collect()


if __name__ == '__main__':
    main()
