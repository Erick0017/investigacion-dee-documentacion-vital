"""Portable documentary recalculation of A's two actual selected public uses.

This is not a replay of the newly prepared full-A RP recipe. Sources are only
the preserved package primaries plus fixed stdlib parsers; no DEE/Native import.
"""
from pathlib import Path
import argparse, json, runpy, sys

def main(args):
    root = Path(args.root).resolve(strict=True); dest = Path(args.out_dir).resolve()
    if dest.exists() or dest.is_relative_to(root): raise ValueError('Fresh output outside the preserved analysis required')
    index = json.loads((root / '04_EVIDENCIAS/PRIMARIOS/INDICE_PRIMARIOS_PI08.json').read_text('utf-8-sig'))
    if len(index['primaries']) != 2 or index['products']: raise ValueError('Exactly the actual selected FI18/7 and alfa primary records')
    sys.path.insert(0, str(root))
    tool = runpy.run_path(str(root / 'RECALCULAR_PRIMARIOS_PI08.py'), run_name='PI08_actual_public_A_only')
    result = tool['recalculate'](root)
    ledger = result['current_direct_receipt_ledger']
    if not result['all_checks_passed'] or ledger['unique_current_Native_requests'] != 189 or ledger['status_counts'] != {'applied': 189}:
        raise ValueError('Actual selected-public documentary decoding/counts differ')
    result['reproduction_scope'] = 'Documentary recalculation of actual selected FI18/7+alfa at860622..861426. It does not execute or verify the newly prepared full-state RP recipe or future OP12.'
    result['Native_imports'] = 0; result['new_Native_ticks'] = 0
    dest.mkdir(parents=True)
    (dest / 'RECALCULO_A_PUBLICA_PI08.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf8')
    print(json.dumps({'output': str(dest), 'checks_passed': True, 'Native_inputs_recounted_from_recorded_primaries': 189,
                      'new_Native_ticks': 0, 'material_replay_executed': False}))

if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__); p.add_argument('--root', required=True); p.add_argument('--out-dir', required=True)
    main(p.parse_args())
