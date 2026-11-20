"""Actual public-manager LIST/VERIFY only, after Root's completed registration.

No material command, DEE import, owner, life access/query or source mutation.
"""
from pathlib import Path
import datetime
import hashlib
import json
import subprocess
import sys

P = Path(__file__).resolve().parents[1]
C = P.parents[2] / 'DEE Cognitive 2.0'
S = C / 'sistema'
RP = C / 'reproducibilidad'
RID = 'pi04_c2c_adquisicion_20_R01'


def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    folder = P / 'control/RP_C2C_LISTAR_VERIFICAR_POSTREPLAY_R01'
    if folder.exists(): raise ValueError('Preserve an earlier operational read-only proof')
    active = read(S / 'estado/ACTIVO.json')
    cardfile = S / 'estado/vidas' / active['life_id'] / 'VIDA.json'; card = read(cardfile)
    recipefile = RP / 'recetas' / (RID + '.json'); recipe = read(recipefile)
    resources = read(RP / 'RECURSOS.json'); capsule = resources['code_capsules'][recipe['code_capsule_key']]
    capmanifest = C / capsule['product_relative'] / capsule.get('manifest', 'SISTEMA_CODIGO.json')
    watched = [S / 'estado/ACTIVO.json', cardfile, S / card['snapshot'], recipefile, capmanifest]
    before = {str(p): sha(p) for p in watched}
    folder.mkdir()
    executions = {}
    for mode, extra in [('listar', []), ('verificar', [RID])]:
        command = [sys.executable, '-I', '-B', '-X', 'utf8', str(S / 'gestionar.py'), 'reproducibilidad', mode, *extra]
        r = subprocess.run(command, capture_output=True, text=True, encoding='utf8', errors='strict', timeout=180,
            creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
        for suffix, text in [('stdout', r.stdout), ('stderr', r.stderr)]:
            (folder / (mode + '.' + suffix + '.txt')).write_text(text, encoding='utf8')
        if r.returncode: raise RuntimeError('Pure public command failed; preserve stdout/stderr, no material retry')
        executions[mode] = {'command': command, 'returncode': r.returncode, 'decoded': json.loads(r.stdout)}
    listing = executions['listar']['decoded']; verified = executions['verificar']['decoded']
    entry = next(r for r in listing['recipes'] if r['id'] == RID)
    actual = entry['actual_registered_verifications']
    if len(actual) != 1 or actual[0]['life'] != 'ECI02_PI03_REPRO_PI04_RP_COLD20_OP2' or actual[0]['actual_native_execution_completed'] is not True or actual[0]['fixed_local_criteria_met'] is not True:
        raise ValueError('The real registered cold20 evidence is absent or ambiguous')
    if len(verified) != 1 or verified[0]['recipe'] != RID or verified[0]['requirements_available'] is not True:
        raise ValueError('Actual preserved requirements verification did not pass')
    if verified[0]['actual_registered_verifications'] != actual:
        raise ValueError('List/verify disagree on actual registered evidence')
    after = {str(p): sha(p) for p in watched}
    if before != after: raise ValueError('A watched original or pinned recipe/capsule changed during the read')
    compact = {'schema': 'DEE.PI04.C2C.actual_public_RP_read_only.v1',
        'checked_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'commands': {k: {'command': v['command'], 'returncode': v['returncode']} for k, v in executions.items()},
        'new_Native_ticks': 0, 'material_commands_invoked': False,
        'route': 'First argument reproducibilidad: manager early stdlib forwarding, RP listar/verificar. No Store/Native execution path.',
        'recipe': RID, 'historical_recipe_verification_state': recipe['verification']['state'],
        'recipe_sha256_preserved': before[str(recipefile)], 'capsule_key': recipe['code_capsule_key'],
        'capsule_manifest_sha256_preserved': before[str(capmanifest)],
        'requirements_available': True,
        'requirement_checks': [{k:r[k] for k in ('kind', 'available_and_identity_checked')} for r in verified[0]['checks']],
        'actual_registered_verifications': actual, 'actual_verified_runs': 1,
        'source_active_life_observed_as_file': active['life_id'], 'source_active_tick_from_card': card['physical']['tick'],
        'watched_critical_before': before, 'watched_critical_after': after, 'watched_hashes_unchanged': True,
        'raw_command_outputs': [{'file': p.name, 'bytes': p.stat().st_size, 'sha256': sha(p)} for p in sorted(folder.glob('*.txt'))],
        'scope': 'Actual public list/verify execution of read-only modes. The actual Native cold replay was executed and registered by Root separately. No new reproduction, selection, promotion or recipe/capsule update here.'}
    proof = folder / 'COMPROBACION.json'
    with proof.open('x', encoding='utf8') as f: json.dump(compact, f, ensure_ascii=False, indent=2); f.write('\n')
    print(json.dumps({'proof': str(proof), 'sha256': sha(proof), 'actual_verified_runs':1,
        'requirements_available':True,'new_Native_ticks':0,'watched_unchanged':True}))


if __name__ == '__main__': main()
