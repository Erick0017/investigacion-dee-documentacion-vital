"""CAS install of the separately reviewed S2 merge; default read-only plan.

Only Root applies after its current Yoked owner closes. No Native import, owner
start, mode routing change, product edit, state copy or selector modification.
"""
from pathlib import Path
import argparse
import datetime
import hashlib
import json
import shutil

P = Path(__file__).resolve().parents[1]
S2 = P / 'estados/candidato_R02/sistema'
SRC = P / 'codigo/PUERTA_GESTOR_PI04_S2_OP2'


def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def regular(p, root):
    if not p.resolve().is_relative_to(root.resolve()): raise ValueError('Outside directed tree')
    for n in [p, *p.parents]:
        if n.is_symlink() or (n.exists() and getattr(n.lstat(), 'st_file_attributes', 0) & 0x400):
            raise ValueError('No linked/reparse files')
        if n == root: break


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--aplicar', action='store_true')
    ap.add_argument('--owner-closed-proof', type=Path)
    a = ap.parse_args()
    proposed = read(SRC / 'PROPUESTA_NO_APLICADA.json')
    actual = S2 / 'gestionar.py'
    regular(actual, S2)
    if sha(actual) != proposed['source_S2_sha256']: raise ValueError('Actual S2 CAS differs; never overwrite another source delta')
    for name, key in [('gestionar.py', 'manager_merged_sha256'), ('pi04_cliente_acotado.py', 'client_sha256')]:
        regular(SRC / name, SRC)
        if sha(SRC / name) != proposed[key]: raise ValueError('Reviewed proposal changed')
    client = S2 / 'app/pi04_cliente_acotado.py'
    if client.exists(): raise ValueError('An existing client must be preserved and reconciled, not overwritten')
    locks = list((S2 / 'estado/locks').glob('*.lock'))
    result = {'schema': 'PI04.manager_merge.installation.S2.OP2',
        'mode': 'APPLY' if a.aplicar else 'READ_ONLY_PLAN', 'source_manager_sha256': sha(actual),
        'reviewed_manager_sha256': proposed['manager_merged_sha256'], 'client_sha256': proposed['client_sha256'],
        'current_S2_locks': [str(p) for p in locks], 'Native_ticks': 0,
        'product_or_selectors_modified': False, 'Root_apply_requires_all_owners_closed': True}
    if not a.aplicar:
        print(json.dumps(result, ensure_ascii=False, indent=2)); return
    if locks: raise ValueError('S2 writer locks exist; no apply while a writer may be active')
    if a.owner_closed_proof is None: raise ValueError('Explicit Root closed-owner proof is required')
    closed_file = a.owner_closed_proof.resolve(strict=True)
    regular(closed_file, P / 'control')
    closed = read(closed_file)
    if closed.get('owner_closed') is not True:
        raise ValueError('Actual closed-owner witness is required; no guessed process closure')
    proof = P / 'control/PUERTA_GESTOR_INSTALADA_S2_OP2.json'
    backup = P / 'codigo/revisiones/ANTES_PUERTA_GESTOR_S2_OP2'
    if proof.exists() or backup.exists(): raise ValueError('Preserve prior attempt; never replay an ambiguous installation')
    # Every refusal above occurs before a first write.
    backup.mkdir(parents=True)
    shutil.copyfile(actual, backup / 'gestionar.py')
    if sha(backup / 'gestionar.py') != proposed['source_S2_sha256']: raise ValueError('Literal S2 backup verification failed')
    temp = actual.with_name(actual.name + '.PI04_S2_OP2_writing')
    with temp.open('xb') as f: f.write((SRC / 'gestionar.py').read_bytes())
    with client.open('xb') as f: f.write((SRC / 'pi04_cliente_acotado.py').read_bytes())
    temp.replace(actual)
    if sha(actual) != proposed['manager_merged_sha256'] or sha(client) != proposed['client_sha256']:
        raise ValueError('Installed code differs; preserve the attempt and backup')
    result.update(status='INSTALLED_ISOLATED_S2_ONLY_PENDING_ROOT_REAL_CLI_TEST',
        installed_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        previous_manager={'path': str(backup / 'gestionar.py'), 'sha256': sha(backup / 'gestionar.py')},
        closed_owner_proof={'path': str(closed_file), 'sha256': sha(closed_file)},
        manager_after_sha256=sha(actual), client_after_sha256=sha(client),
        scope='Exact S2 manager preserved; only bounded CLI door plus existing product OP4 forwarding correction. No Native routing changed.')
    with proof.open('x', encoding='utf8') as f: json.dump(result, f, ensure_ascii=False, indent=2); f.write('\n')
    print(json.dumps({'proof': str(proof), 'sha256': sha(proof), **result}, ensure_ascii=False, indent=2))


if __name__ == '__main__': main()
