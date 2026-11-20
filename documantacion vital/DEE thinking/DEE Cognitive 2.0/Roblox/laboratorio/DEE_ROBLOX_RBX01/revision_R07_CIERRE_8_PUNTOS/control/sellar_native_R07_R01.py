"""Freeze explicit R07 wrapper sources; stdlib only, zero DEE/Studio imports."""
from pathlib import Path
import ast, datetime, hashlib, json, time

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / 'control/CONGELADO_NATIVE_R07_R01.json'
BUNDLE = ('rbx07_native_v3.py', 'rbx07_identity_v3.py', 'rbx07_funciones_v3.py')
START, LAST, END = 1794841620, 1794859200, 1794863220

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

def main():
    if OUTPUT.exists() or not START <= time.time() < LAST:
        raise ValueError('Fresh prospective freeze required; do not overwrite')
    files = ['native/bundle/' + x for x in BUNDLE]
    files += ['native/' + x for x in ('adapter_v3.py', 'ledger_v3.py',
        'owner_support_v3.py', 'servicio_eventos_v3.py', 'preparar_par28_v3.py',
        'importar_par_v3.py', 'import0_v3.py')]
    rows = []
    for rel in files:
        path = ROOT / rel
        raw = path.read_bytes()
        if len(raw) > 150000:
            raise ValueError('Bounded explicit source required')
        ast.parse(raw.decode('utf-8-sig'), filename=rel)
        rows.append({'file': rel, 'bytes': len(raw), 'sha256': sha(raw)})
    value = {
        'schema': 'DEE.RBX07.prospective_native_freeze.R01', 'sealed': True,
        'utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'native_start_epoch': START, 'last_new_episode_epoch': LAST,
        'native_cutoff_epoch': END,
        'native_sources_sha256': {x: sha((ROOT/'native/bundle'/x).read_bytes()) for x in BUNDLE},
        'files': rows, 'Native_Studio_model_calls': 0,
        'scope': 'R07 wrappers only. Official v27/Thinking and R06 originals remain separate.',
        'source_tick': 991187, 'new_main_supply': 24, 'new_control_supply': 6,
        'load_protected_slots': 9, 'new_native_aggregate_max': 160000,
        'not_an_execution_or_scientific_approval': True,
    }
    raw = (json.dumps(value, ensure_ascii=False, indent=2)+'\n').encode('utf8')
    with OUTPUT.open('xb') as out:
        out.write(raw)
    print(json.dumps({'freeze': str(OUTPUT), 'bytes': len(raw), 'sha256': sha(raw),
                      'sources': len(rows), 'Native_executions': 0}, ensure_ascii=False))

if __name__ == '__main__':
    main()
