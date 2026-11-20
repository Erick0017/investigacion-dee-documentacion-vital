"""Execute only the frozen finite confirmation panel, one world at a time."""
from pathlib import Path
import argparse
import json
import sys
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'src'))
from transferencia_magnitud import ejecutar


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    config = json.loads((ROOT / 'configuraciones/transferencia_magnitud/CONFIRMACION_CONGELADA.json').read_text(encoding='utf-8'))
    rows = []
    for case in config['cases']:
        sys.argv = ['ejecutar.py', '--case', case['id'], '--value', str(case['value']), '--mode', case['mode'],
                    '--objects', *map(str, case['objects']), '--out', str(args.out / case['id'])]
        ejecutar.main()
        value = json.loads((args.out / case['id'] / 'MEASUREMENTS.json').read_text(encoding='utf-8'))
        rows.append({'case_id': case['id'], 'qualified': [row['qualified'] for row in value['readings']],
                     'reference': [row['reference']['s_reg'] for row in value['readings']],
                     'outputs': [row['output'] for row in value['readings']]})
        (args.out / 'CONFIRMATION_INCREMENTAL.json').write_text(json.dumps(rows, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'status': 'MEASURED', 'cases': rows}, ensure_ascii=False))


if __name__ == '__main__':
    main()
