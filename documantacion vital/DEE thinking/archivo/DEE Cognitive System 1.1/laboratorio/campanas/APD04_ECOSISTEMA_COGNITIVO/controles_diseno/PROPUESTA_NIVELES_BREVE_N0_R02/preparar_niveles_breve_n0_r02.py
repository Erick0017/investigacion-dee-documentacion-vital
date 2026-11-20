"""N0 shorter calendar requested prospectively by Root. Never runs Native."""
import argparse
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
BASE_SHA = '85e977f5cab4011f204d86bb660830f536b4e90dd70c474fea24399e3d6bae95'


def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def load(name, p):
    s = importlib.util.spec_from_file_location(name, p); m = importlib.util.module_from_spec(s); s.loader.exec_module(m); return m
def dump(p, v):
    with p.open('x', encoding='utf8', newline='\n') as f: json.dump(v, f, ensure_ascii=False, indent=2); f.write('\n')


def main():
    ap = argparse.ArgumentParser(description=__doc__); ap.add_argument('--out', type=Path, required=True); a = ap.parse_args()
    if a.out.exists(): raise FileExistsError('Preserve prior proposal')
    bp = HERE / 'proponer_niveles_igual_oportunidad_apd04_n0_r01.py'
    if sha(bp) != BASE_SHA: raise ValueError('Original600second DRAFT generator changed')
    b = load('immutable600second_proposal_only', bp)
    proto = load('N0_literals_only', ROOT / 'sistema/app/protocolo_apd04.py')
    ui = load('N0_parser_only', ROOT / 'sistema/app/usar_dee.py')
    driver = load('N0_schema_only', ROOT / 'laboratorio/campanas/APD04_ECOSISTEMA_COGNITIVO/ejecucion/ejecutar_plan_apd04_r03.py')
    a.out.mkdir(); proofs = []
    for n in (2, 5, 10, 20):
        p = b.plan(n); original = copy.deepcopy(p); life = 'APD04_NIVELES_BREVE_N' + str(n) + '_R02'
        p['life'] = p['world_id'] = life
        p.update(duration_seconds=180, supervision_wall_limit_seconds=480)
        times = {15: 5, 90: 30, 165: 55, 240: 80, 315: 105, 400: 130, 420: 140, 440: 150, 460: 160, 500: 175}
        for e in p['events']:
            e['at_seconds'] = times.get(e['at_seconds'], e['at_seconds'])
            if 'request_id' in e: e['request_id'] = e['request_id'].replace('apd04_igual_op_', 'apd04_breve_').replace('_r01_', '_r02_')
        p['prospective_revision'] = 'APD04.equal_opportunity.short_calendar.R02'
        p['not_a_closed_plan'] = True
        p['short_window_limit'] = '5opportunities are scheduled, not guaranteed completed inside180s; record late/omitted/inflight IDs and never refill missing opportunities or change the calendar after outcomes. Outer480s uses existing supervisor.'
        test = copy.deepcopy(p); test.update(status='CLOSED_FOR_EXECUTION', initial_snapshot_sha256='0' * 64, initial_tick=639374)
        driver.validate_plan(test)
        for e in p['events']:
            if e['kind'] == 'material':
                for r in e['situations']: proto.validate_literal(r)
            elif e['kind'] == 'command': ui.literal_rows(ui.command_parser().parse_args(e['argv']))
        dump(a.out / ('PLAN_BREVE_N' + str(n) + '_DRAFT_R02.json'), p)
        proofs.append({'N_sources': n, 'Native_N_unchanged': 67, 'life_proposed_not_created': life,
                       'work_offsets_seconds': [e['at_seconds'] for e in p['events'] if e['kind'] == 'material' and e['situations'][0]['modo'] == 'apd04-vivir'],
                       'old4_offsets_seconds': [e['at_seconds'] for e in p['events'] if e['kind'] == 'material' and e['situations'][0]['modo'] == 'apd04-palabra'],
                       'duration_seconds': 180, 'outer_guard_seconds': 480, 'static_literals_validated': True,
                       'source_original600plan_values_preserved_in_R01': True})
    source_hashes = [{'source': name, 'sha256_at_N0': sha(ROOT / name)} for name in b.SOURCES]
    dump(a.out / 'REVISION_BREVE_PREGO_N0_R02.json', {'schema': 'APD04.four_levels.short_DRAFT.N0.R02',
        'status': 'DRAFT_NO_ROOT_NATIVE_GO', 'Native_ticks': 0, 'lives_created': 0, 'proofs': proofs,
        'base600_generator_sha256': BASE_SHA, 'source_hashes_at_N0_not_a_future_freeze': source_hashes,
        'parent': {'full_pair': b.PARENT + '/EXPORTACION_SERVICIO.json', 'snapshot_sha256': b.PARENT_SHA, 'tick': 639374},
        'unchanged': ['R03sensor independent_balanced', 'R02codec', 'goal0/classifica/load7,3', 'mut0=18/1=24',
                      'append-only additional sources seed40520', 'literal inherited caches/cursor/bin preserved',
                      'old4 words suma/resta/compara/recuerda', 'existing driver/protocol/supervisor'],
        'limits': ['Four branches share one historical prefix and are not four independently trained learners.',
                   'N20 receives at most its first5circular slots; no simultaneous20-value input claim.',
                   'Physical work dose may differ after Native tool choices; opportunity count is the fixed budget.',
                   '180swindow may leave fewer than5completed opportunities. Report the common actually executed prefix and all rejections/pending/omissions without treating them as zero correct.',
                   'N2state check is an administrative slot, not a physical sham. Actual phases and clocks must be recorded.',
                   'Actual fork encoded SHA/genealogy/pending state remain unset until Root imports and closes each real candidate.']})
    shutil.copy2(Path(__file__), a.out / Path(__file__).name)
    dump(a.out / 'MANIFIESTO.json', {'members': [{'file': p.name, 'bytes': p.stat().st_size, 'sha256': sha(p)} for p in sorted(a.out.iterdir()) if p.is_file()], 'self_hash_excluded': True})
    print(json.dumps({'out': str(a.out), 'drafts': 4, 'Native_ticks': 0, 'duration_each': 180, 'outer_each': 480}))


if __name__ == '__main__': main()
