"""Root-only passive final protection check. Default only prints the plan.

No DEE/app imports, owners, restoration or state writes. --verificar requires
the actual final writer-closure proof and writes only a fresh PI09 control JSON.
The initial register did not record python.exe's hash: its present hash is
reported without inventing historical equality.
"""
from pathlib import Path
from datetime import datetime, timezone
import argparse, hashlib, json

P = Path(__file__).resolve().parents[1]
R = P.parents[2]
C = R / 'DEE Cognitive 2.0'
A = 'ECI02_PI03_REPRO_PI04_PI05_PI07_RP_R03_PI08_A01'
REGISTER = P / 'REGISTRO_CAMPANA.json'
BASELINES = {
    'A_card': ('DEE Cognitive 2.0/sistema/estado/vidas/' + A + '/VIDA.json', 156910,
               '50ec14550436f5e86892c1b0b4edc3493d6c54c92e548c60d7b899807c7f3966'),
    'A_snapshot': ('DEE Cognitive 2.0/sistema/estado/checkpoints/' + A + '.T861426.f71dba6bdace.deetsnap.gz', 2067145,
                   '2eeef08e3bebac4e218178ed379fd99aa5fdeb03650c0454ad55c6534824c133'),
    'WHL': ('DEE Cognitive 2.0/sistema/runtime/dee_thinking-4.5.0-cp313-cp313-win_amd64.whl', 1022834,
            '09e191d259fd15d321ea11b587f8cc02c12c7adfe81b7b96ca2dbebb1fb12d0c'),
    'PYD': ('DEE Cognitive 2.0/motor/python313/site-packages/dee_thinking/_native.cp313-win_amd64.pyd', 2639872,
            '17f827341530f66816ec146af085b00a5f7b3d34d645bcd407f1279e8ac6c50d'),
    'kernel_source': ('4.5/DEE_thinking_4_5_0/source/src/kernel_v27.cpp', 31596,
                      'fbd8190381ed76085f404e6578ff15fe185ab66cd48c67300d2abad61ddc7e31'),
}

def need(ok, message):
    if not ok:
        raise ValueError(message)

def read(path):
    return json.loads(Path(path).read_text('utf-8-sig'))

def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()

def regular(path):
    path = Path(path).absolute()
    for item in (path, *path.parents):
        if item.exists():
            need(not item.is_symlink() and not (getattr(item.lstat(), 'st_file_attributes', 0) & 1024),
                 'Reparse/symlink refused: ' + str(item))
        if item == R:
            break
    return path

def pointer(value, text):
    need(text.startswith('/'), 'Explicit closure JSON pointer required')
    for part in text[1:].split('/'):
        part = part.replace('~1', '/').replace('~0', '~')
        value = value[int(part)] if isinstance(value, list) else value[part]
    return value

def plan():
    return {
        'schema': 'DEE.PI09.final_passive_protection.plan.v1',
        'mode': 'READ_ONLY_PLAN_NO_CURRENT_STATE_HASHING',
        'baselines': {key: {'path': str(R / row[0]), 'bytes': row[1], 'sha256': row[2]}
                      for key, row in BASELINES.items()},
        'python': {'path': str(C / 'motor/python313/python.exe'),
                   'initial_hash_in_PI09_register': False,
                   'historical_equality_not_asserted': True},
        'legitimate_changes_not_compared_to_A_selection': [
            'ACTIVO/selection', 'project/continuity/catalogue', 'published Manual/Compendium'],
        'requires_actual_final_writer_closure': True,
        'Native_executed': False,
    }

def verify(args):
    need(args.cierre is not None and args.cierre_sha256 is not None and args.salida is not None,
         'Actual closed proof/hash and fresh output are required')
    closed = regular(args.cierre).resolve(strict=True)
    out = regular(args.salida).resolve()
    need(closed.is_relative_to((P / 'control').resolve()) and out.is_relative_to((P / 'control').resolve())
         and not out.exists(), 'Closure and fresh output only under PI09/control')
    need(sha(closed) == args.cierre_sha256, 'Actual writer-closure proof changed')
    value = pointer(read(closed), args.cierre_puntero)
    need(type(value) is bool and value is True, 'Actual scoped writers are not closed')
    register_before = sha(REGISTER)
    register = read(REGISTER)
    rows = []
    for label, (relative, size, digest) in BASELINES.items():
        file = regular(R / relative).resolve(strict=True)
        original = register['protected_before'].get(str(file))
        need(original is not None and original['bytes'] == size and original['sha256'] == digest,
             'Initial register binding differs: ' + label)
        current_sha = sha(file)
        rows.append({'label': label, 'path': str(file), 'initial_bytes': size,
                     'initial_sha256': digest, 'actual_bytes': file.stat().st_size,
                     'actual_sha256': current_sha,
                     'unchanged': file.stat().st_size == size and current_sha == digest})
    card = read(R / BASELINES['A_card'][0])
    a_semantics = (card.get('life_id') == A and card.get('physical', {}).get('N') == 67
                   and card.get('physical', {}).get('tick') == 861426
                   and card.get('snapshot_sha256') == BASELINES['A_snapshot'][2])
    python = regular(C / 'motor/python313/python.exe').resolve(strict=True)
    python_row = {'path': str(python), 'actual_bytes': python.stat().st_size,
                  'actual_sha256': sha(python), 'initial_hash_available': False,
                  'equals_initial': None,
                  'scope': 'Present executable only. No initial python.exe hash was preserved in the PI09 register.'}
    need(sha(REGISTER) == register_before and sha(closed) == args.cierre_sha256,
         'Register/closure changed during passive verification')
    result = {'schema': 'DEE.PI09.final_passive_protection.actual.v1',
              'recorded_utc': datetime.now(timezone.utc).isoformat(),
              'initial_register': {'path': str(REGISTER), 'sha256_at_verification': register_before},
              'actual_writer_closure': {'path': str(closed), 'sha256': args.cierre_sha256,
                                        'pointer': args.cierre_puntero},
              'checks': rows, 'A861426_card_semantics_match': a_semantics,
              'python': python_row,
              'required_five_hashes_unchanged': all(row['unchanged'] for row in rows),
              'overall_required_protection': all(row['unchanged'] for row in rows) and a_semantics,
              'global_operational_state_equality_not_claimed': True,
              'Native_executed': False, 'DEE_imports': 0, 'worlds_opened': 0,
              'operational_files_written': 0}
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open('x', encoding='utf8') as stream:
        json.dump(result, stream, ensure_ascii=False, indent=2)
        stream.write('\n')
    print(json.dumps({'proof': str(out), 'sha256': sha(out),
                      'overall_required_protection': result['overall_required_protection'],
                      'python_historical_comparison': 'UNAVAILABLE_NOT_INVENTED', 'Native_executed': False}))
    return 0 if result['overall_required_protection'] else 2

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--verificar', action='store_true')
    parser.add_argument('--cierre', type=Path)
    parser.add_argument('--cierre-sha256')
    parser.add_argument('--cierre-puntero', default='/all_scoped_Native_writers_closed')
    parser.add_argument('--salida', type=Path)
    args = parser.parse_args()
    if not args.verificar:
        print(json.dumps(plan(), ensure_ascii=False, indent=2))
        return 0
    return verify(args)

if __name__ == '__main__':
    raise SystemExit(main())
