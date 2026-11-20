"""PI08 portable documentary recalculation. Stdlib, frozen files, zero Native.

Existing PI07 mechanical decoders are preserved literally in heredado/. New
material contracts must be added explicitly; unknown rows never become PASS.
An absent signature remains NULL; material zero remains zero.
"""
from pathlib import Path
from collections import defaultdict
import argparse
import json
import runpy
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from auditoria_documental_PI08 import (actual_life, body, canonical, checked,
    count_request_ledger, digest, direct_requests, interval_union, local,
    read_json, receipt_map)

INDEX = '04_EVIDENCIAS/PRIMARIOS/INDICE_PRIMARIOS_PI08.json'
LEGACY = HERE / 'heredado' / 'RECALCULAR_PRIMARIOS_PI07_LITERAL.py'
LEGACY_SHA256 = 'bbc81b6c01ca455ed961ae3cb53f29a6650374676ddc31df5f55af9a8a8b3470'
KNOWN_EPISODES = {
    'DEE.PI07.physical_state_selective_regulation.R01',
    'DEE.PI07.acquired_regulation.environment.R02',
    'DEE.PI07.acquired_regulation.perpendicular_environment.R03',
}
KNOWN_ACCESS = {'DEE.PI07.fixed_regulated_FI_access.R01_PREPARED'}


def material_kind(row):
    if all(k in row for k in ('reference_before', 'return_frames', 'FI', 'sensor', 'message', 'requests')):
        return 'regulation_episode'
    if all(k in row for k in ('FI', 'public_operands', 'generic_return_failed', 'sensor', 'return_frames')):
        return 'regulated_FI_access'
    if all(k in row for k in ('first_reader', 'native_arithmetic', 'second_native_use',
                              'actual_effect', 'native_input_summary')):
        return 'C2C'
    if ('numeric_result' in row and 'native_operation' in row and 'numeric_reader' in row):
        return 'numeric'
    if 'formed_native_command' in row.get('reader', {}) and isinstance(row['reader'].get('panel'), list):
        return 'association'
    return None


def leaf_rows(row, source):
    """Only known envelopes; do not walk operational_dependencies/history."""
    inner = row.get('original_result')
    if isinstance(inner, dict) and material_kind(inner) is not None:
        yield inner, source+'/original_result', True
    elif ('result' in row and isinstance(row['result'], dict)
          and isinstance(row['result'].get('rows'), list)):
        for i, value in enumerate(row['result']['rows']):
            yield from leaf_rows(value, source+'/result/row'+str(i))
    else:
        yield row, source, False


def adapter_contracts(root, index):
    """Future aliases require a frozen explicit audit contract, not inference."""
    result = {}
    for entry in index.get('mechanical_adapters', []):
        _, data = checked(root, entry)
        obj = read_json(data)
        if (obj.get('schema') != 'DEE.PI08.documentary_mechanical_alias.v1'
                or obj.get('status') != 'APPROVED_FOR_PASSIVE_RECALCULATION'
                or obj.get('canonical_PI07_version') not in KNOWN_EPISODES
                or not isinstance(obj.get('actual_version'), str)
                or len(obj.get('actor_sha256', '')) != 64
                or len(obj.get('protocol_sha256', '')) != 64):
            raise ValueError('Unapproved or malformed mechanical alias contract')
        if obj['actual_version'] in result:
            raise ValueError('Duplicate version alias')
        result[obj['actual_version']] = obj
    return result


def recalculate(root, index_name=INDEX):
    root = Path(root).resolve(strict=True)
    raw_index = local(root, index_name).read_bytes()
    index = read_json(raw_index)
    if index.get('schema') != 'DEE.PI08.portable_primary_index.v1':
        raise ValueError('Exact PI08 portable index schema required')
    code = LEGACY.read_bytes()
    if digest(code) != LEGACY_SHA256:
        raise ValueError('Preserved mechanical decoder literal changed')
    legacy = runpy.run_path(str(LEGACY), run_name='pi08_frozen_documentary_decoder')
    aliases = adapter_contracts(root, index)
    products = {}
    for entry in index.get('products', []):
        _, data = checked(root, entry)
        products[digest(data)] = data
    seen = set()
    episodes, inherited, chains, checks = [], [], [], []
    failures, omissions, wrappers, receipt_rows, intervals = [], [], [], [], []
    mismatch = []
    evidence_modes = defaultdict(int)
    primary_count = 0
    for entry in index.get('primaries', []):
        file = entry['file']
        if file.casefold() in seen:
            raise ValueError('Duplicate/case-aliased indexed primary')
        seen.add(file.casefold())
        _, data = checked(root, entry)
        primary_count += 1
        obj = read_json(data)
        envelope, rows = body(obj)
        evidence_modes[entry.get('modality', 'DOCUMENTARY_RECALCULATION_OF_RECORDED_EXECUTION')] += 1
        if not rows:
            failures.append({'source': file, 'transport_status': obj.get('status'),
                'recorded_error': obj.get('error'), 'complete_material_rows': 0,
                'scope': 'Frozen primary retained; no missing behavior, tick or success invented.'})
        for ordinal, outer in enumerate(rows):
            for row, source, wrapped in leaf_rows(outer, file+'#row'+str(ordinal)):
                if wrapped:
                    wrappers.append({'source': source, 'counted_once': True})
                kind = material_kind(row)
                if kind is None:
                    omissions.append({'source': source, 'version': row.get('version'),
                        'material_contract_unrecognized': any(k in row for k in ('requests', 'Native_inputs', 'native_input_summary')),
                        'coverage': 'BYTES_AND_HASH_ONLY',
                        'reason': 'No implemented scientific decoder for this row; no functional PASS inferred.'})
                    continue
                current_checks = []
                try:
                    life = actual_life(envelope, row, entry)
                    copy = row
                    actual_version = row.get('version')
                    alias = aliases.get(actual_version)
                    if kind == 'regulation_episode':
                        if actual_version not in KNOWN_EPISODES:
                            if alias is None:
                                raise ValueError('New material version needs explicit mechanical adapter')
                            if (entry.get('actor_sha256') != alias['actor_sha256']
                                    or entry.get('protocol_sha256') != alias['protocol_sha256']):
                                raise ValueError('New version does not match its fixed source/protocol provenance')
                            copy = dict(row, version=alias['canonical_PI07_version'])
                        value = legacy['inspect_episode'](copy, source, products, current_checks)
                        value['version'] = actual_version
                        value['passive_adapter'] = None if alias is None else alias['actual_version']
                        if life is not None:
                            value['life_id'] = life
                        episodes.append(value)
                    elif kind == 'regulated_FI_access':
                        if actual_version not in KNOWN_ACCESS:
                            raise ValueError('New FI access version needs an implemented fixed contract')
                        value = legacy['inspect_regulated_access'](row, source, current_checks)
                        episodes.append(value)
                    elif kind == 'C2C':
                        value = legacy['inspect_C2C'](row, source, products, current_checks)
                        value.update({'life_id': life, 'version': actual_version})
                        chains.append(value)
                    else:
                        values = legacy['inspect_inherited_witness'](row, source, current_checks)
                        if len(values) != 1:
                            raise ValueError('Expected one complete inherited scientific witness')
                        value = values[0]
                        value.update({'life_id': life, 'version': actual_version})
                        inherited.append(value)
                    current, stats = receipt_map(direct_requests(row, kind))
                    # Preserve direct current operation windows; neither IDs nor
                    # old nested dependency receipts establish extra events.
                    world = entry.get('world_key', life)
                    receipt_rows.append({'source': source, 'world_key': world,
                                         'requests': direct_requests(row, kind)})
                    before, after = row.get('before_tick'), row.get('after_tick')
                    if type(before) is int and type(after) is int:
                        intervals.append({'source': source, 'world_key': world,
                                          'before_tick': before, 'after_tick': after})
                    checks.extend(current_checks)
                    checks.append({'source': source, 'check': 'actual_current_direct_receipts_deduplicated',
                                   'passed': True, 'dose': stats})
                except (KeyError, TypeError, ValueError, IndexError) as exc:
                    checks.extend(current_checks)
                    mismatch.append({'source': source, 'kind': kind,
                                     'error_type': type(exc).__name__, 'error': str(exc),
                                     'scope': 'Documentary discrepancy preserved, not repaired or relabelled.'})
    groups = defaultdict(list)
    for row in episodes:
        groups[(row.get('life_id'), row.get('version'))].append(row)
    summaries = {}
    for (life, version), selected in groups.items():
        selected.sort(key=lambda r: r['ordinal'])
        if len({r['ordinal'] for r in selected}) != len(selected):
            mismatch.append({'source': str(life)+'|'+str(version), 'kind': 'duplicate_opportunity',
                             'error': 'Same life/version/local ordinal appears twice; no silent de-duplication.'})
        summaries[str(life)+'|'+str(version)] = {
            'life_id': life, 'version': version, 'included_opportunities': len(selected),
            'stages': legacy['stage_counts'](selected),
            'scope': 'A new version-local ordinal is not a reset of the physical history. '
                     'Paired futures are not independent individuals.'}
    windows = defaultdict(list)
    for row in intervals:
        if row['world_key']:
            windows[row['world_key']].append((row['before_tick'], row['after_tick']))
    ledger = count_request_ledger(receipt_rows)
    tick_coverage = {world: interval_union(w) for world, w in sorted(windows.items())}
    unsupported = [r for r in omissions if r['material_contract_unrecognized']]
    passed = bool(checks) and not mismatch and not unsupported and all(c['passed'] for c in checks)
    return {'schema': 'DEE.PI08.portable_primary_recalculation.v1',
        'status': 'IMPLEMENTED_DOCUMENTARY_CHECKS_MATCHED' if passed else 'INCOMPLETE_OR_MISMATCH_PRESERVED',
        'all_checks_passed': passed, 'new_Native_ticks': 0, 'DEE_imports': 0,
        'index_sha256': digest(raw_index), 'literal_legacy_decoder_sha256': digest(code),
        'indexed_primaries': primary_count, 'indexed_product_files': len(index.get('products', [])),
        'episodes_recalculated': len(episodes), 'groups': summaries, 'episodes': episodes,
        'inherited_function_witnesses_recalculated_separately': inherited,
        'C2C_chain_witnesses_recalculated_separately': chains,
        'current_direct_receipt_ledger': ledger, 'recorded_material_tick_windows': tick_coverage,
        'recorded_tick_window_coverage_is_full_campaign_ledger': False,
        'evidence_modalities_as_indexed_not_new_executions': dict(evidence_modes),
        'external_observation_wrappers_not_double_counted': wrappers,
        'checks': checks, 'documentary_mismatches': mismatch,
        'rows_hash_verified_not_recalculated': omissions,
        'no_complete_rows_or_technical_errors': failures,
        'scope': 'Frozen-record documentary recalculation only. No Native acquisition/replay, '
                 'new experiment, readmission, recovery, promotion or broad observer-passivity claim. '
                 'All source_reference fields are provenance only and never opened.'}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--raiz', type=Path, required=True)
    ap.add_argument('--salida', type=Path, required=True)
    ap.add_argument('--indice', default=INDEX)
    a = ap.parse_args()
    if a.salida.exists():
        raise FileExistsError(a.salida)
    value = recalculate(a.raiz, a.indice)
    with a.salida.open('x', encoding='utf-8') as f:
        json.dump(value, f, ensure_ascii=False, indent=2)
        f.write('\n')
    print(json.dumps({'schema': value['schema'], 'status': value['status'],
                      'indexed_primaries': value['indexed_primaries'],
                      'episodes_recalculated': value['episodes_recalculated'],
                      'checks': len(value['checks']), 'all_checks_passed': value['all_checks_passed'],
                      'new_Native_ticks': 0, 'output_sha256': digest(a.salida.read_bytes())}, ensure_ascii=False))
    return 0 if value['all_checks_passed'] else 2


if __name__ == '__main__':
    raise SystemExit(main())
