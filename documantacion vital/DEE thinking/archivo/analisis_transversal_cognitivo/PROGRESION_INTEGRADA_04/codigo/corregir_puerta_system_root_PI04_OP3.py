"""Transport-only early dispatch fix for the two PI04 manager commands.

Accept the existing same-system --system-root forms before Store imports.
Never changes a scientific module, frozen capsule, state, queue or selector.
"""
from pathlib import Path
import argparse
import ast
import datetime
import hashlib
import json
import subprocess
import sys

P = Path(__file__).resolve().parents[1]
S = P / 'estados/candidato_R02/sistema'
H = P / 'codigo'
OUT = H / 'PUERTA_GESTOR_PI04_SYSTEMROOT_OP3'
BASE_SHA = '811c3ed051034b03be7e219726e758d38b11746dfed8cebe17e53f06226d56af'


def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    ap = argparse.ArgumentParser(description=__doc__); ap.add_argument('--aplicar', action='store_true'); a = ap.parse_args()
    src = S / 'gestionar.py'
    if sha(src) != BASE_SHA: raise ValueError('Manager CAS changed; preserve before further edits')
    before = src.read_bytes(); s = before.decode('utf8').replace('\r\n', '\n')
    old = """# Fixed transport-only PI04 convenience door, before Store/Native imports.
if len(sys.argv)>1 and sys.argv[1]in('pi04-coordinacion-estado','pi04-coordinacion-oportunidad'):
    import importlib.util as _pi04_importlib
    _pi04_system=Path(__file__).resolve().parent
"""
    new = """# Fixed transport-only PI04 convenience door, before Store/Native imports.
# OP3: the existing manager's explicit same-system --system-root syntax must
# reach this early door too; otherwise argparse accepted it but main had no
# material dispatch branch. No request is redirected to another system.
_pi04_arguments=list(sys.argv[1:]); _pi04_requested_system=None
if len(_pi04_arguments)>=3 and _pi04_arguments[0]=='--system-root':
    _pi04_requested_system=_pi04_arguments[1]; _pi04_arguments=_pi04_arguments[2:]
elif len(_pi04_arguments)>=2 and _pi04_arguments[0].startswith('--system-root='):
    _pi04_requested_system=_pi04_arguments[0].split('=',1)[1]; _pi04_arguments=_pi04_arguments[1:]
if _pi04_arguments and _pi04_arguments[0]in('pi04-coordinacion-estado','pi04-coordinacion-oportunidad'):
    import importlib.util as _pi04_importlib
    _pi04_system=Path(__file__).resolve().parent
    if _pi04_requested_system is not None and Path(_pi04_requested_system).resolve(strict=True)!=_pi04_system:
        raise SystemExit('PI04 bounded queue command only accepts its own explicit system; no redirected owner or implicit selection')
"""
    if s.count(old) != 1: raise ValueError('Exact PI04 early-door locator changed')
    fixed = s.replace(old, new, 1)
    old_call = '    raise SystemExit(_pi04_client.cli(sys.argv[1:],system_root=_pi04_system))'
    new_call = '    raise SystemExit(_pi04_client.cli(_pi04_arguments,system_root=_pi04_system))'
    if fixed.count(old_call) != 1: raise ValueError('Exact CLI argument locator changed')
    fixed = fixed.replace(old_call, new_call, 1)
    ast.parse(fixed)
    assert fixed.replace(new, old, 1).replace(new_call, old_call, 1) == s
    if OUT.exists(): raise ValueError('Preserve an existing OP3 proposal/attempt')
    OUT.mkdir()
    (OUT / 'gestionar_ANTES_S2.py').write_bytes(before)
    (OUT / 'gestionar.py').write_text(fixed, encoding='utf8', newline='')
    # Real Python subprocesses, deliberately fake client and no app package:
    # falling through to Store would fail instead of silently passing a fake.
    fake = OUT / 'PRUEBA_FAKE_SIN_APP'
    (fake / 'app').mkdir(parents=True)
    (fake / 'gestionar.py').write_text(fixed, encoding='utf8', newline='')
    (fake / 'app/pi04_cliente_acotado.py').write_text(
        "import json\ndef cli(arguments,*,system_root):\n print(json.dumps({'FAKE_TRANSPORT_ONLY':True,'arguments':arguments,'system_root':str(system_root),'Native_ticks':0})); return 0\n", encoding='utf8')
    command = 'pi04-coordinacion-estado'
    tests = []
    for prefix in ([], ['--system-root', str(fake)], ['--system-root=' + str(fake)]):
        args = [sys.executable, '-I', '-B', '-X', 'utf8', str(fake / 'gestionar.py'), *prefix, command, '--vida', 'FAKE_ONLY']
        r = subprocess.run(args, capture_output=True, text=True, encoding='utf8', timeout=30)
        assert r.returncode == 0, r.stderr
        v = json.loads(r.stdout); assert v['arguments'] == [command, '--vida', 'FAKE_ONLY']
        tests.append({'argument_prefix': prefix, 'returncode': r.returncode, 'fake_result': v})
    r = subprocess.run([sys.executable, '-I', '-B', '-X', 'utf8', str(fake / 'gestionar.py'),
        '--system-root', str(OUT), command, '--vida', 'FAKE_ONLY'], capture_output=True, text=True, encoding='utf8', timeout=30)
    assert r.returncode != 0 and 'own explicit system' in r.stderr and not r.stdout
    locks = list((S / 'estado/locks').glob('*.lock'))
    proof = {'schema': 'PI04.manager.same_system_dispatch.OP3', 'Native_ticks': 0,
        'root_cause': 'Root invoked --system-root <sameS2> before the command. The early door inspected argv[1] only; parser accepted the added command, then legacy main rejected Command not implemented before queue admission.',
        'baseline_manager_sha256': BASE_SHA, 'new_manager_sha256': sha(OUT / 'gestionar.py'),
        'exact_reverse_patch_equals_prior_manager': True, 'fake_subprocess_tests': tests,
        'different_system_rejected_before_Store': True, 'current_S2_locks': [str(x) for x in locks],
        'frozen_RP_capsule_modified': False, 'scientific_modules_modified': False, 'product_modified': False,
        'scope': 'Transport argument routing only. Cold RP executes its pinned direct owner/runner, not this optional public manager door.',
        'installed': False}
    if a.aplicar:
        if locks: raise ValueError('A source S2 owner may be active; no manager edit')
        if src.read_bytes() != before: raise ValueError('CAS changed during pure tests')
        temp = src.with_name(src.name + '.PI04_OP3_writing')
        with temp.open('xb') as f: f.write((OUT / 'gestionar.py').read_bytes())
        temp.replace(src)
        assert sha(src) == proof['new_manager_sha256']
        proof['installed'] = True
        proof['installed_utc'] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    target = P / 'control/PUERTA_GESTOR_SYSTEMROOT_OP3.json'
    with target.open('x', encoding='utf8') as f: json.dump(proof, f, ensure_ascii=False, indent=2); f.write('\n')
    print(json.dumps({'proof': str(target), 'sha256': sha(target), 'installed': proof['installed'],
        'manager_sha256': proof['new_manager_sha256'], 'Native_ticks': 0}, ensure_ascii=False))


if __name__ == '__main__': main()
