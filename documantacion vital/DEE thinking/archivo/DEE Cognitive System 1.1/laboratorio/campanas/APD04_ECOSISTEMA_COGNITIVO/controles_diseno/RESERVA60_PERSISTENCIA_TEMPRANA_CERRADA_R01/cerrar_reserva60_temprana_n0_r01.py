"""Close only the identity/provenance of Root-approved literal reserve. N0 only."""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
EV = ROOT / 'evidencia/campanas/APD04_ECOSISTEMA_COGNITIVO'
S = ROOT / 'sistema'
OLD = HERE / 'PROPUESTA_RESERVA60_PERSISTENCIA_TEMPRANA_N0_R01'
OUT = HERE / 'RESERVA60_PERSISTENCIA_TEMPRANA_CERRADA_R01'
BUNDLE = HERE / 'EJECUTOR_TRES_VISTAS_REAL_POST10_N0_R02'
LIFE = 'APD04_PERSISTENCIA_TEMPRANA_RESERVA_R01'


def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p): return json.loads(p.read_bytes())
def emit(p, v):
    with p.open('x', encoding='utf8', newline='\n') as f:
        json.dump(v, f, ensure_ascii=False, indent=2)
        f.write('\n')


def main():
    if OUT.exists(): raise FileExistsError('Preserve every executed or closed revision')
    source = OLD / 'PLAN_RESERVA60_PERSISTENCIA_TEMPRANA_DRAFT_R01.json'
    if sha(source) != '17ddc1244df56c07a49417b807eb6f1444556ffc3b830d89db973516cce87d71':
        raise ValueError('Root-approved exact agenda changed')
    proofpath = EV / 'PERSISTENCIA_TEMPRANA_IMPORTACION_N0_R01/IMPORTACION_N0.json'
    proof = read(proofpath)
    cardpath = S / 'estado/vidas' / LIFE / 'VIDA.json'
    card = read(cardpath)
    if card != proof['record']: raise ValueError('Actual imported child changed before closure')
    expected = '57daa4513cff94cb048bd1a34e84aba71e41e0200eed32cd88700a75aea38de6'
    if card['snapshot_sha256'] != expected or card['physical']['tick'] != 639374:
        raise ValueError('Wrong actual imported identity')
    if sha(S / card['snapshot']) != expected: raise ValueError('Snapshot bytes changed')
    if (not proof['RAW_clocks_channels_pending_receipts_equal'] or not proof['SQLite_requests_equal']
            or proof['new_native_ticks'] != 0 or proof['Runtime_owner_started']
            or proof['protocol']['pending_material'] is not None):
        raise ValueError('Import proof does not match declared N0 full continuity')
    old = read(source)
    p = copy.deepcopy(old)
    p.update(status='CLOSED_FOR_EXECUTION', initial_snapshot_sha256=expected, initial_tick=639374,
        candidate_genealogy={'kind': 'EXACT_FULL_SAFE_FORK_N0', 'life': LIFE,
            'parent': card['parent'], 'import_record': str(proofpath), 'import_sha256': sha(proofpath),
            'new_native_ticks_before_reserve': 0, 'not_a_late_view_repair': True})
    if p['events'] != old['events'] or p['after_window_pending'] != old['after_window_pending']:
        raise ValueError('Closure changed literal agenda')
    spec = importlib.util.spec_from_file_location('existing_R04_validator_only', BUNDLE / 'ejecutar_plan_apd04_r04.py')
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    mod.validate_plan(p)
    frozen = {rel: sha(ROOT / rel) for rel in p['freeze_source_paths']}
    required = {
        'sistema/app/protocolo_apd04.py': 'f66989c3d9fb6779029d6ba626f4c366633d4f9d97006ae5e42f910dac3f0fe5',
        'sistema/capacidades/ecosistema_apd04.py': '6e829bc1ec7c5920613878718068b5b158d99993cec56fafa7c79e3ba5a31013',
        'sistema/app/usar_dee.py': 'a63e4a9fba9b675c9beac7a4fabfc11c852b36aa508d00ba257052f87451e594'}
    if any(frozen[k] != v for k, v in required.items()): raise ValueError('Root source freeze changed')
    OUT.mkdir()
    emit(OUT / 'PLAN_RESERVA60_PERSISTENCIA_TEMPRANA_CERRADO_R01.json', p)
    for name in ('ejecutar_plan_apd04_r04.py', 'supervisar_plan_apd04_r04.py'):
        shutil.copy2(BUNDLE / name, OUT / name)
    for rel in p['freeze_source_paths']:
        dest = OUT / 'FUENTES_CONGELADAS' / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / rel, dest)
    shutil.copy2(proofpath, OUT / 'IMPORTACION_N0_ORIGINAL.json')
    shutil.copy2(Path(__file__), OUT / Path(__file__).name)
    emit(OUT / 'CIERRE_PROSPECTIVO_N0.json', {
        'Native_ticks': 0, 'owner_started': False,
        'Root_GO': 'ROOT GO RESERVA60 TEMPRANA; exact approved draft17ddc124 identity-only closure',
        'original_draft_SHA': sha(source), 'current_card_SHA': sha(cardpath),
        'current_snapshot_SHA': expected, 'current_tick': 639374,
        'agenda_and_criteria_identical_to_approved_draft': True,
        'freeze_sources': frozen, 'global_max_owners': 2,
        'no_favorable_future_substitution_or_restart': True,
        'minimum3600_local4500_hard4800_close300': True,
        'Root_absolute_deadline_unchanged': p['deadline_utc'],
        'one_existing_OMIT_owner_coexists': True,
    })
    emit(OUT / 'MANIFIESTO.json', {'self_hash_excluded': True, 'members': [
        {'file': q.relative_to(OUT).as_posix(), 'bytes': q.stat().st_size, 'sha256': sha(q)}
        for q in sorted(OUT.rglob('*')) if q.is_file()]})
    print(json.dumps({'out': str(OUT), 'manifest_SHA': sha(OUT / 'MANIFIESTO.json'),
        'plan_SHA': sha(OUT / 'PLAN_RESERVA60_PERSISTENCIA_TEMPRANA_CERRADO_R01.json'), 'Native_ticks': 0}))


if __name__ == '__main__': main()
