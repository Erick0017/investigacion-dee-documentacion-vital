"""Freeze the literal non-D panel interval and source0 beside the closed D export.

Pure documentary copy. No DEE, SQLite, Owner, Native or world import.
"""
from pathlib import Path
import hashlib
import json

P = Path(__file__).resolve().parents[1]
D = P / 'control/D_FINAL_PORTABLE_R04'

def require(ok, why):
    if not ok:
        raise ValueError(why)

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def read(path):
    return json.loads(Path(path).read_text('utf-8-sig'))

def member(source, relative):
    source = Path(source).resolve(strict=True)
    require(source.is_relative_to(P.resolve()) and source.is_file() and not source.is_symlink(), 'Literal PI09 regular source only')
    data = source.read_bytes()
    target = D / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    require(not target.exists(), 'New final documentary member only')
    target.write_bytes(data)
    require(target.read_bytes() == data, 'Literal copy changed')
    return {'file': relative, 'bytes': len(data), 'sha256': sha(target), 'source_reference_for_packager_only': str(source)}

def main():
    original = D / 'INDICE_D_PI09_R02.json'
    index = read(original)
    require(index['schema'] == 'DEE.PI09.D.portable_primary_index.R02', 'Frozen base index')
    for group in ('closures', 'plans', 'primaries', 'witnesses', 'products'):
        for item in index[group]:
            target = D / item['file']
            require(target.stat().st_size == item['bytes'] and sha(target) == item['sha256'], 'Frozen D member mismatch')
    proof_path = P / 'control/PI09_PANEL_POST_D12_R03.json'
    proof = read(proof_path)
    life = 'ECI02_PI03_REPRO_PI04_PI05_PI07_PI09_DISCOVERY_01'
    require(proof['schema'] == 'DEE.PI09.actual.finite_owner_plan.R03' and proof['closed'] is True and proof['error'] is None, 'Actual closed panel only')
    require(proof['life_id'] == life and (proof['initial_tick'], proof['final_tick'], proof['new_Native_ticks']) == (917679, 920520, 2841), 'Exact same-life panel interval')
    require(len(proof['records']) == 13, 'Habitat pause plus historical panel12')
    plan = Path(proof['plan'])
    require(sha(plan) == proof['plan_sha256'], 'Pinned panel plan changed')
    interleaved = {'kind': 'closed_legacy_panel12', 'arm': 'real', 'life_id': life,
                   'initial_tick': 917679, 'final_tick': 920520, 'new_Native_ticks': 2841,
                   'not_D_opportunities_or_D_learning': True,
                   'closure': member(proof_path, 'INTERVALOS_NO_D/' + proof_path.name),
                   'plan': member(plan, 'INTERVALOS_NO_D/' + plan.name), 'primaries': []}
    for record in proof['records']:
        source = Path(record['primary'])
        require(sha(source) == record['sha256'], 'Actual panel primary changed')
        interleaved['primaries'].append(member(source, 'PRIMARIOS_NO_D/real/' + source.name))
    zero = P / 'control/REAPERTURA_SOURCE_D_PI09_R01.json'
    require(sha(zero) == '8a5e26f5a767358f39f44219b17dcce3a4dbb859059674e3d8f631f5571d25b5', 'Actual Source0 proof changed')
    index['schema'] = 'DEE.PI09.D.portable_primary_index.R04'
    index['base_literal_index'] = {'file': original.name, 'bytes': original.stat().st_size, 'sha256': sha(original)}
    index['interleaved_non_D'] = [interleaved]
    index['source_zero_reopening'] = member(zero, 'CONTROLES/' + zero.name)
    index['evaluation_ordinals'] = list(range(6))
    index['real_future_ordinals_recorded'] = [6]
    index['source_world_needed_for_recalculation'] = False
    output = D / 'INDICE_D_PI09_R04.json'
    require(not output.exists(), 'Final index is append-only')
    output.write_text(json.dumps(index, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    result = {'schema': 'DEE.PI09.D.final_literal_export_ready.R04', 'MOVE_READY': True,
              'index': str(output), 'index_sha256': sha(output),
              'D_primaries': len(index['primaries']), 'witnesses': len(index['witnesses']),
              'products': len(index['products']), 'non_D_panel_primaries': 13,
              'Native_executed': False, 'DEE_imported': False,
              'all_source_witness_and_product_bytes_copied_and_verified': True,
              'source_world_needed_for_future_recalculation': False}
    proof_out = P / 'control/EXPORTACION_FINAL_D_MOVE_READY_PI09_R04.json'
    require(not proof_out.exists(), 'New move-ready witness only')
    proof_out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({**result, 'proof_sha256': sha(proof_out)}, ensure_ascii=False))

if __name__ == '__main__':
    main()
