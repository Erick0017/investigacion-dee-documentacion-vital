"""Reconcile CPC5 saved primary measurements without running a DEE trajectory.

This is an auditor, not an organizational component. No expected value or
classification from here is supplied to a Runtime. JSON pointers identify the
original record. UInt64 RAW/clock values remain strings or integers.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1048576), b''):
            h.update(block)
    return h.hexdigest()


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def put(path, value):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding='utf-8')


def escaped(key):
    return str(key).replace('~', '~0').replace('/', '~1')


def walk_records(value, pointer=''):
    if isinstance(value, dict):
        if 'site' in value and ('raw' in value or 'RAW_hex' in value) and 'tick' in value:
            yield pointer, value
        else:
            for key, item in value.items():
                yield from walk_records(item, pointer + '/' + escaped(key))
    elif isinstance(value, list):
        for i, item in enumerate(value):
            yield from walk_records(item, pointer + '/' + str(i))


def final_tick(value):
    for name in ('final_state', 'final_physics', 'physics', 'physical', 'final', 'world'):
        part = value.get(name)
        if isinstance(part, dict) and isinstance(part.get('tick'), int):
            return part['tick']
    ticks = [row['tick'] for row in value.get('rows', []) if isinstance(row, dict) and isinstance(row.get('tick'), int)]
    return max(ticks) if ticks else None


def receipt_values(value):
    # Select the unique receipt table, not nested duplicates captured in traces.
    for key in ('receipts',):
        if isinstance(value.get(key), list):
            return value[key]
    for key in ('operative', 'operational', 'final'):
        parent = value.get(key, {})
        if isinstance(parent, dict) and isinstance(parent.get('receipts'), list):
            return parent['receipts']
    teaching = value.get('teaching', {})
    if isinstance(teaching, dict) and isinstance(teaching.get('actual_receipts'), list):
        return teaching['actual_receipts']
    return []


def receipts_summary(value):
    rows = receipt_values(value)
    return {'receipts': len(rows), 'statuses': dict(Counter(str(x.get('status', 'MISSING')) for x in rows)),
            'scope': 'Unique stored receipt table; rejected, absent and silent are not combined'}


def language_metrics(value):
    case = value['case']
    expected = case.get('event_directions', [])
    result = {}
    for cycle in sorted({r['cycle'] for r in value['readouts']}):
        rows = [r for r in value['readouts'] if r['cycle'] == cycle]
        matched = sum(bool(r['decoder_valid'] and r.get('slot', -1) in range(len(expected))
                           and r['decoded_direction'] == expected[r['slot']]) for r in rows)
        result[str(cycle)] = {'queries': len(rows), 'admitted': sum(bool(r['admitted']) for r in rows),
                             'decoded': sum(bool(r['decoder_valid']) for r in rows),
                             'match_experienced_direction': matched,
                             'directions': [r['decoded_direction'] for r in rows],
                             'ticks': [r['tick'] for r in rows],
                             'loads': [r['physical']['s_reg'] if r['physical']['active'] else None for r in rows]}
    lanes = []
    for lesson in value.get('lessons', []):
        rows = [r for r in value['readouts'] if r['form'] == lesson['form']]
        lanes.append({'form': lesson['form'], 'acquisition_experience_tick': lesson['tick'],
                      'physical_after': lesson.get('physical_after'),
                      'later_experiences_before_first_query': sum(x['tick'] > lesson['tick'] for x in value['lessons']),
                      'queries': [{'tick': r['tick'], 'cycle': r['cycle'], 'admitted': r['admitted'],
                                   'decoded_direction': r['decoded_direction'], 'valid': r['decoder_valid']} for r in rows]})
    return {'cycles': result, 'lanes': lanes, 'formula': 'sum(valid_decoder AND decoded_direction == actual experienced direction), grouped by cycle',
            'denominator': '8 fixed physical ports per cycle; cycles are repeated uses of one trajectory, not independent replicates',
            'scope': value.get('scope'), 'same_RUNTIME': value.get('same_RUNTIME'),
            'opaque_forms': len({r['form'] for r in value['readouts']}),
            'physical_direction_classes': len(set(expected)),
            'new_preparations': value.get('new_preparations'), 'operative_forks': value.get('operative_forks'),
            'host_RAW_writes_after_T0': value.get('host_RAW_writes_after_T0'),
            'host_clock_writes_after_T0': value.get('host_clock_writes_after_T0')}


def network_metrics(value):
    post = [r for r in value['readouts'] if r.get('phase') == 'post']
    case = value['case']
    groups = defaultdict(list)
    for row in post:
        groups[row['group']].append(row)
    return {'architecture': case['architecture'], 'top_level_declared': case.get('top_level'),
            'physical_group_lengths': case['chains'], 'resources': value.get('resources'),
            'observed_stage_loads': [r['center']['s_reg'] if r['center']['active'] else None for r in post],
            'observed_stage_directions': [r['center']['direction'] for r in post],
            'observed_stage_ticks': [r['tick'] for r in post],
            'ordered_observations': [{'stage': r['stage'], 'group': r['group'], 'tick': r['tick'],
                                      'load': r['center']['s_reg'] if r['center']['active'] else None,
                                      'direction': r['center']['direction']} for r in post],
            'group_terminal_loads': {str(k): max(v, key=lambda r: r['stage'])['center']['s_reg']
                                     if max(v, key=lambda r: r['stage'])['center']['active'] else None for k, v in groups.items()},
            'admission': receipts_summary(value), 'diagnostic_edits': value.get('diagnostic_edits', []),
            'formula': 'Post-encounter center.s_reg if active; absent remains null. No output is synthesized.',
            'scope': value.get('scope')}


def relative_metrics(value):
    rows = []
    for original in value.get('rows', []):
        row = {'tick': original['tick'], 'memories': {}}
        for name, memory in original.get('memories', {}).items():
            fields = memory.get('physical', memory)
            a, b = fields.get('A', {}), fields.get('B', {})
            valid = a.get('active', False) and b.get('active', False)
            row['memories'][name] = {'A': a.get('s_reg') if a.get('active') else None,
                                      'B': b.get('s_reg') if b.get('active') else None,
                                      'delta': a.get('s_reg', 0) - b.get('s_reg', 0) if valid else None,
                                      'available': valid,
                                      'expression': fields.get('expression', fields.get('comparator')),
                                      'reader': fields.get('reader')}
        for name in ('joint', 'joint_out'):
            if name in original:
                row[name] = original[name]
        rows.append(row)
    return {'longitudinal_panel': rows, 'admission': receipts_summary(value),
            'formula': 'delta=s_A-s_B only when both actual centers are active; otherwise null',
            'scope': value.get('scope'), 'host_raw_edits': value.get('host_raw_edits'),
            'host_clock_edits': value.get('host_clock_edits')}


def regulation_metrics(value):
    profiles = {}
    for bank, captures in value['captures'].items():
        # These are the two exact measured resources, not a global intelligence score.
        profiles[bank] = {'physical_captures': captures, 'stored_profile': value['profiles'][bank]}
    transition = []
    for row in value.get('trace', []):
        if row.get('tick') in (292, 293, 294) and 'pulse_gate' in row:
            transition.append({k: row[k] for k in ('tick', 'pulse_site', 'residual_site', 'pulse_gate', 'residual_gate')})
    return {'case': value['case'], 'profiles': profiles, 'external_utility': value['external_utility'],
            'formula': 'F=exact function carrier signature, R=exact resource signature; per bank utility=2*F+R; sum across declared banks',
            'source_preparation': value.get('source_preparation'), 'scope': value.get('scope'),
            'technical': value.get('technical'), 'admission': receipts_summary(value),
            'final_physics': value.get('final_state'),
            'selective_transition': transition, 'interventions': value.get('interventions', []),
            'verified_RAW_indices_changed': value.get('verified_RAW_indices_changed'),
            'verified_clock_indices_changed': value.get('verified_clock_indices_changed')}


def compound_metrics(value):
    grouped = defaultdict(list)
    case = value['case']
    for row in value['readouts']:
        actual = row.get('decoded_direction')
        expected = case.get('directions', {}).get(row['relation'])
        grouped[str(row['block'])].append({
            'relation': row['relation'], 'input_tick': row['input_tick'],
            'read_tick': row.get('read_tick', row['physical'].get('tick')),
            'receipt': row['receipt'], 'physical': row['physical'],
            'decoded_direction': actual,
            'matches_experienced_direction': actual is not None and actual == expected})
    native_outputs = []
    for row in value.get('native_windows', []):
        for name in ('native_first', 'native_joint', 'native_consequence'):
            record = row.get(name)
            if isinstance(record, dict) and record.get('active'):
                native_outputs.append({'kind': name, 'record': record})
    calls = value.get('calls', [])
    inputs_by_origin = Counter(c.get('origin', 'UNSPECIFIED') for c in calls)
    geometry = value.get('geometry', {})
    resources = {'N': geometry.get('N'), 'components': geometry.get('components'),
                 'prepared_material_sites': geometry.get('prepared_material_sites'),
                 'input_calls': len(calls), 'input_calls_by_origin': dict(inputs_by_origin),
                 'input_calls_by_operation': dict(Counter(c.get('operation', 'UNSPECIFIED') for c in calls)),
                 'training_calls': sum(inputs_by_origin[k] for k in ('CURRENT_DIRECTION_EVENT', 'OPAQUE_SIGNAL_EXPOSURE')),
                 'physical_backup_query_calls': inputs_by_origin['COMMON_QUERY_WITHOUT_REPORT'],
                 'shared_native_query_calls': inputs_by_origin['NATIVE_SHARED_READOUT_REQUEST'],
                 'fixed_environment_calls': inputs_by_origin['FIXED_EXTERNAL_ENVIRONMENTAL_OPPORTUNITY'],
                 'payload_sum': sum(c.get('payload', 0) for c in calls)}
    return {'architecture': case.get('architecture'), 'case': case, 'geometry': geometry, 'resources': resources,
            'blocks': {k: {'queries': len(v), 'admitted': sum(x['receipt']['status'] == 'applied' for x in v),
                           'physically_decoded': sum(x['decoded_direction'] is not None for x in v),
                           'matches_experienced_direction': sum(x['matches_experienced_direction'] for x in v),
                           'observations': v} for k, v in grouped.items()},
            'admission': receipts_summary(value), 'preparations': value.get('preparations'),
            'same_Runtime_between_lessons': value.get('same_Runtime_between_lessons'),
            'diagnostic_forks': value.get('diagnostic_forks'), 'interventions': value.get('interventions'),
            'native_active_output_records': native_outputs,
            'scope_discrepancy': {'primary_scope_retained_verbatim': value.get('scope'),
                                  'geometry_and_actual_calls': 'Four relations are acquired in primary and backup routes; P1/P2 reused through new physical experiences. Six components, sixteen training calls in the intact core-reuse preparation.',
                                  'reason': 'The old generic result.scope sentence says two redundant relations; actual case.scope, geometry.relations and input ledger specify four in the core-reuse extension.'} if geometry.get('core_reuse') else None,
            'scope': value.get('scope'),
            'formula': 'Per longitudinal block, count actual applied receipts, directional decodes and matches; do not replace invalid/occupied/silent with numeric zero.'}


def heterogeneous_metrics(value):
    normalized = dict(value)
    normalized['rows'] = [{'tick': r['tick'], 'memories': r['relative_cells']} for r in value['rows']]
    result = relative_metrics(normalized)
    result.update({'case': value['case'], 'architecture': value['case'].get('architecture'),
                   'geometry': value['geometry'], 'preparations': value.get('preparations'),
                   'physical_population_types': value['geometry'].get('types'),
                   'functional_components': value['geometry'].get('functional_components'),
                   'mobile_encounters': [{k: r[k] for k in ('tick', 'stage', 'phase', 'center')} for r in value.get('mobile_encounters', [])],
                   'host_RAW_clock_edits_after_T0': value.get('host_RAW_clock_edits_after_T0'),
                   'scope': value.get('scope')})
    return result


def bridge_metrics(value):
    rows = []
    for row in value['rows']:
        a, b = row['A'], row['B']
        valid = a.get('active', False) and b.get('active', False)
        rows.append({'tick': row['tick'], 'A': a, 'B': b,
                     'delta_recomputed': a['s_reg'] - b['s_reg'] if valid else None,
                     'reader': row['reader'], 'comparator': row['comparator'],
                     'nominal_mobile_segment': row.get('nominal_mobile_segment')})
    return {'case': value['case'], 'geometry': value['geometry'], 'panel': rows,
            'admission': receipts_summary(value), 'host_RAW_clock_writes_after_T0': value.get('host_RAW_clock_writes_after_T0'),
            'scope': value.get('scope'),
            'formula': 'Preserve actual centers, reader and comparator; delta only for active A/B. A nominal ballistic segment is not an ancestry certification after an unobserved transformation.'}


def compact_panel_record(record):
    if not isinstance(record, dict):
        return record
    return {k: record[k] for k in ('tick', 'raw', 'RAW_hex', 'clock', 'clock_u64', 'active', 's_reg', 'direction') if k in record}


def compact_review(value):
    """Avoid repeating the same full primary panels in three review files."""
    keep = ('case_id', 'source', 'source_sha256', 'architecture', 'case', 'scope', 'admission',
            'cycles', 'opaque_forms', 'physical_direction_classes', 'same_RUNTIME',
            'new_preparations', 'preparations', 'same_Runtime_between_lessons', 'diagnostic_forks',
            'physical_population_types', 'functional_components', 'formula', 'resources', 'geometry')
    out = {k: value[k] for k in keep if k in value}
    out['complete_calculations'] = {'file': 'CALCULOS.json', 'json_pointer': '/cases/' + escaped(value['case_id'])}
    if 'longitudinal_panel' in value:
        out['longitudinal_panel'] = []
        for row in value['longitudinal_panel']:
            out['longitudinal_panel'].append({'tick': row['tick'], 'memories': {
                k: {'A': m['A'], 'B': m['B'], 'delta': m['delta'], 'available': m['available'],
                    'expression': compact_panel_record(m['expression']), 'reader': compact_panel_record(m['reader'])}
                for k, m in row['memories'].items()}})
    if 'panel' in value:
        out['panel'] = [{'tick': r['tick'], 'delta': r['delta_recomputed'],
                         'reader': compact_panel_record(r['reader']),
                         'comparator': compact_panel_record(r['comparator'])} for r in value['panel']]
    if 'blocks' in value:
        out['blocks'] = {k: {n: v[n] for n in ('queries', 'admitted', 'physically_decoded', 'matches_experienced_direction')} for k, v in value['blocks'].items()}
        out['native_active_output_records'] = value['native_active_output_records']
    if 'mobile_encounters' in value:
        out['mobile_encounters'] = value['mobile_encounters']
    return out


def source_hash_coverage(root, index, originals):
    available = defaultdict(list)
    for path in root.rglob('*.py'):
        if '.venv' in path.parts:
            continue
        available[sha(path)].append(path.relative_to(root).as_posix())
    rows = []
    for item in index:
        source = root / item['source']
        original = originals[item['source']]
        declared = [(item['source'], k, original[k]) for k in ('source_sha256', 'code_sha256', 'runner_sha256') if k in original]
        config = source.parent / 'CONFIG.json'
        if config.exists():
            cfg = read(config)
            declared.extend((config.relative_to(root).as_posix(), k, cfg[k]) for k in ('source_sha256', 'code_sha256', 'runner_sha256') if k in cfg)
        hashes = [{'declared_at': file, 'field': key, 'sha256': value,
                   'matching_python_files': available.get(value, [])[:5],
                   'total_matching_python_files': len(available.get(value, []))} for file, key, value in declared]
        row = {'case_id': item['case_id'], 'recorded_source_identities': hashes,
               'all_recorded_source_hashes_resolve': all(bool(available.get(x[2])) for x in declared) if declared else None,
               'status': 'RECORDED_SOURCE_HASH_RESOLVED' if declared and all(available.get(x[2]) for x in declared)
                         else 'RECORDED_SOURCE_HASH_MISSING' if declared else 'SOURCE_HASH_NOT_RECORDED_IN_PRIMARY_OR_CASE_CONFIG'}
        item['source_identification'] = row
        rows.append(row)
    return {'cases_checked': len(rows), 'cases_with_source_identity': sum(bool(x['recorded_source_identities']) for x in rows),
            'cases_with_all_source_hashes_resolved': sum(x['all_recorded_source_hashes_resolve'] is True for x in rows),
            'missing_or_not_recorded': [x for x in rows if x['all_recorded_source_hashes_resolve'] is not True],
            'scope': 'Byte-identical Python source reachable in CPC5. Metadata hashes do not alone certify scientific equivalence; primary continuations and controls are separate.'}


def message_index(root, originals):
    """Declared routes plus exact endpoint observations, never invented ancestry."""
    output = []
    for file, value in originals.items():
        case_id = Path(file).parent.name
        recipe = value.get('recipe', {})
        if 'stages' in recipe and 'readouts' in value:
            stages = recipe['stages']
            posts = {r['stage']: (i, r) for i, r in enumerate(value['readouts']) if r.get('phase') == 'post'}
            pres = {r['stage']: (i, r) for i, r in enumerate(value.get('encounter_windows', [])) if r.get('phase') == 'pre'}
            for a, b in zip(stages, stages[1:]):
                if a['group'] != b['group'] or a['index'] not in posts or b['index'] not in posts:
                    continue
                ai, start = posts[a['index']]; bi, end = posts[b['index']]
                pre = pres.get(b['index'])
                output.append({'case_id': case_id, 'source': file,
                               'emitter': 'stage' + str(a['index']), 'receiver': 'stage' + str(b['index']),
                               'emission': start['center'], 'receiver_pre': pre[1]['center'] if pre else None,
                               'reception_and_encounter_post': end['center'],
                               'evidence_pointers': ['/readouts/' + str(ai) + '/center', '/readouts/' + str(bi) + '/center'] + (['/encounter_windows/' + str(pre[0])] if pre else []),
                               'declared_route': {'direction': a['outgoing'], 'ticks': end['tick'] - start['tick'], 'periodic_N': recipe.get('N')},
                               'coverage': 'Exact endpoints and pre/post encounter Moore windows. Intermediate free-flight path is predicted from recipe, not certified ancestry at every tick.',
                               'attribution': 'CANDIDATE_DECLARED_NATIVE_ROUTE_WITH_CONTRASTS; NOT_UNIQUE_GENEALOGY_FROM_PROXIMITY',
                               'controls': ['NET_C_R2_EDGE_REMOVE', 'NET_C_R2_EDGE_DIRECTION', 'NET_C_R2_EDGE_SHAM', 'NET_R2_NAIVE_SECOND', 'NET_R2_UNPAIRED_SECOND']})
        if 'native_windows' in value:
            # Only the declared contacts are linked. Endpoints can receive other
            # contributions; a matched coordinate does not assign a unique parent.
            events = []
            for i, row in enumerate(value['native_windows']):
                for name in ('native_first', 'native_joint', 'native_consequence'):
                    if isinstance(row.get(name), dict) and row[name].get('active'):
                        events.append((i, name, row[name]))
            n = value.get('geometry', {}).get('N')
            for first, second in zip(events, events[1:]):
                ai, an, a = first; bi, bn, b = second
                h = b['tick'] - a['tick']
                endpoint = [(a['site'][j] + h * a['direction'][j]) % n for j in range(3)] if n else None
                output.append({'case_id': case_id, 'source': file,
                               'emitter': an, 'receiver': bn,
                               'emission': a, 'reception_or_later_encounter': b,
                               'evidence_pointers': [f'/native_windows/{ai}/{an}', f'/native_windows/{bi}/{bn}'],
                               'declared_route': {'direction_from_observed_emission': a['direction'], 'ticks': h, 'periodic_N': n,
                                                  'freeflight_endpoint': endpoint, 'endpoint_equals_observed_site': endpoint == b['site']},
                               'coverage': 'Exact sampled endpoints; local transition_neighborhoods retained in primary. Unsampled transformations are not filled in. This row is a route hypothesis, not assignment of unique parentage.',
                               'attribution': 'DECLARED_CONTACT_SEQUENCE_PLUS_COUNTERFACTUALS_NOT_PROXIMITY_GENEALOGY',
                               'controls': ['CORE_LATE_MESSAGE_REMOVE147', 'CORE_LATE_MESSAGE_DIRECTION147', 'CORE_LATE_MESSAGE_SHAM147', 'CORE_K3_OPPOSITE', 'CORE_K3_UNPAIRED', 'CORE_K4_OPPOSITE', 'CORE_UNCOUPLED_MATCHED']})
        if value.get('schema', '').startswith('CPC5.heterogeneous_bridge'):
            rows = value['rows']
            emission = next(((i, r['nominal_mobile_segment']) for i, r in enumerate(rows) if r['tick'] == 3), None)
            reception = next(((i, r['reader']) for i, r in enumerate(rows) if r['tick'] == 5), None)
            response = next(((i, r['comparator']) for i, r in enumerate(rows) if r['tick'] == 7), None)
            if emission and reception:
                output.append({'case_id': case_id, 'source': file, 'emitter': 'acquired_mobile_relation', 'receiver': 'relative_reader',
                               'emission': emission[1], 'reception': reception[1], 'later_relative_expression': response[1] if response else None,
                               'evidence_pointers': [f'/rows/{emission[0]}/nominal_mobile_segment', f'/rows/{reception[0]}/reader'] + ([f'/rows/{response[0]}/comparator'] if response else []),
                               'coverage': 'Exact source/reader/comparator samples plus local_transition_windows. Nominal mobile sampling alone is not unique ancestry after transformation.',
                               'attribution': 'PHYSICAL_CROSS_FAMILY_ROUTE_WITH_HISTORY_AND_OFFPATH_CONTROLS',
                               'controls': ['BRIDGE_C01_BA', 'BRIDGE_C02_UNPAIRED', 'BRIDGE_C03_OFFPATH']})
    with (root / 'MENSAJES.jsonl').open('w', encoding='utf-8') as stream:
        for row in output:
            stream.write(json.dumps(row, ensure_ascii=False, separators=(',', ':')) + '\n')
    return {'message_rows': len(output), 'file': 'MENSAJES.jsonl',
            'scope': 'Measured endpoints and declared candidate routes; gaps and possible joint dependencies retained; not a count of independent communication demonstrations.'}


def write_guides(target, inventory, calculations):
    count = inventory['measurement_records']
    guide = f'''# CPC5: leer primero

Este directorio permite revisar las observaciones y los cálculos sin instalar el
motor ni reproducir primero todas las trayectorias. Contiene {count} registros
primarios `MEASUREMENTS.json` indexados; no equivalen a {count} réplicas independientes.

1. [LECTURA_PROVISIONAL.md](LECTURA_PROVISIONAL.md): mecanismo, evidencia,
   contraejemplos y alcance de la interpretación de este corte.
2. [INDICE_EVIDENCIA.json](INDICE_EVIDENCIA.json): inventario reconciliado, tipo de
   trayectoria, archivo primario, SHA-256 y tick final. Conserva los intentos técnicos.
3. [OBSERVACIONES.jsonl](OBSERVACIONES.jsonl): selección compacta de lecturas físicas
   originales. Cada fila conserva archivo y puntero JSON. RAW y clocks de 64 bits no
   se convierten a float. La selección no sustituye las vecindades completas del origen.
4. [CALCULOS.json](CALCULOS.json): cálculos por caso, fórmulas y denominadores.
5. [COMPARACION_ARQUITECTURAS.json](COMPARACION_ARQUITECTURAS.json): recursos,
   componentes, consultas, latencias y productos por ruta; no un ranking universal.
6. [RETENCION_Y_ACCESO.json](RETENCION_Y_ACCESO.json): panel longitudinal de cada
   individuo. Separa disponibilidad, admisión, expresión y uso.
7. [NSM65_EVIDENCIAS.json](NSM65_EVIDENCIAS.json): catálogo heredado y estado de las
   pruebas nuevas. Ocho señales físicas no se convierten por conteo en ocho conceptos.

Las rutas de evidencia son relativas a la raíz CPC5 extraída. Los `MEASUREMENTS`
contienen llamadas, recibos, RAW desempaquetado, clocks exactos, ventanas, capturas
y referencias a snapshots. Las configuraciones y fuentes exactas están junto al
caso o en `configuraciones/` y `src/`; los casos conservados no se sobrescriben.

Para recalcular esta revisión sin ejecutar física:

```powershell
python src/audit.py --root .
```

Para ejecutar y usar el demostrador consulte `../LEEME.md`. El auditor no es una
parte del ente: sus métricas se calculan después y no retroalimentan MAIN.

## Unidades y separación de planos

Un tick es evolución DEE; un segundo es tiempo de ordenador. Una consulta es una
interacción, a veces consumible; una preparación, una continuación y un fork se
cuentan por separado. Los ticks sucesivos de un mundo determinista no son nuevas
réplicas. `null`, rechazo, cero físico, silencio y error conservan valores distintos.

Datos: registros físicos exactos. Cálculos: fórmulas repetibles sobre esos registros.
Lectura provisional: explicación revisable de Codex, con alternativas y dominio.
No se emite un dictamen automático sobre mente, inteligencia ni límites universales.
'''
    (target / 'LEER_PRIMERO.md').write_text(guide, encoding='utf-8')
    baseline = [
        ('R1: cuatro etapas acopladas', 'NET_R1_SERIAL4'),
        ('R2: dos grupos de cuatro en ruta común', 'NET_R2_SERIAL8_TWO_COMPOUNDS'),
        ('R3: diez simples homogéneos', 'NET_R3_HOMOGENEOUS10'),
        ('R4: cuatro simples heterogéneos', 'NET_R4_HETEROGENEOUS4'),
        ('R5: un grupo de cuatro más cuatro simples', 'NET_R5_MIXED4PLUS4')]
    table = []
    for label, key in baseline:
        if key in calculations:
            v = calculations[key]; r = v['resources']
            terminal = ', '.join(str(x) for x in v['group_terminal_loads'].values())
            table.append(f"| {label} | {r['components']} | {r['training_input_calls']} / {r['query_input_calls']} | {r['native_ticks']} | {terminal} |")
    compounds = []
    selected_compound_rows = {'compound_D01', 'compound_D02', 'compound_reuse_D01',
                              'CORE_UNCOUPLED_MATCHED', 'CORE_K3_OPPOSITE', 'CORE_K3_UNPAIRED',
                              'CORE_K4_OPPOSITE', 'CORE_LATE_MESSAGE_REMOVE147', 'CORE_LATE_MESSAGE_DIRECTION147',
                              'CORE_LATE_MESSAGE_SHAM147', 'CORE_RESERVED_ORDER_QUERY7',
                              'CORE_RESERVED_CONTEXT_QUERY9', 'CORE_QUIET_RETENTION1008'}
    for key, value in calculations.items():
        if 'blocks' not in value or key not in selected_compound_rows:
            continue
        queries = sum(x['queries'] for x in value['blocks'].values())
        matches = sum(x['matches_experienced_direction'] for x in value['blocks'].values())
        admitted = sum(x['admitted'] for x in value['blocks'].values())
        native = '; '.join(f"t{x['record']['tick']}={x['record']['s_reg']}" for x in value['native_active_output_records'] if x['kind'] == 'native_consequence') or 'sin consecuencia activa en las ventanas'
        compounds.append(f"- `{key}`: {matches}/{queries} concordancias de respaldo; {admitted} admitidas. Consecuencias: {native}.")
    regulation_rows = []
    for key, value in calculations.items():
        if not key.startswith('REG_') or 'profiles' not in value:
            continue
        case = value.get('case', {}); context = case.get('C_history')
        profile = '; '.join(f"{b} F{p.get('stored_profile', p)['F']}/R{p.get('stored_profile', p)['R']}" for b, p in value['profiles'].items())
        regulation_rows.append(f"- `{key}`, C={context}: {profile}; utilidad {value['external_utility']}.")
    text = '''# CPC5: lectura provisional argumentada

## Capacidad y mecanismo observados

La adquisición por encuentros físicos produce relaciones móviles utilizables en
una ruta común, y una preparación con ocho interfaces conserva ocho
correspondencias direccionales mientras incorpora las restantes y las vuelve a
consultar. Ambas realizaciones evolucionan bajo DEE thinking 4.0.0 / v27 congelado.
La integración física finita y la retención renovable se miden por separado.
Las arquitecturas son hipótesis de organización: llamarlas compuestos no añade
propiedades que sus acoplamientos y controles no hayan expresado.

## Comparación arquitectónica con recursos visibles

R0 reproduce la red A/B/C/D congelada de CPC4. R1/R2 son rutas nativas de cuatro y
ocho relaciones; R3/R4 son grupos simples homogéneos/heterogéneos; R5 mezcla rutas
compuestas con simples dentro de un Runtime. El inventario por caso conserva
N, componentes, fuentes, entrenamiento, consultas y carga suministrada.

| Realización | Componentes | Entradas enseñanza / consulta | Horizonte | Carga final por ruta |
|---|---:|---:|---:|---|
''' + '\n'.join(table) + '''

La ruta de ocho etapas produce 25→39→55→73→93→115→139→165 con una consulta de 13.
Las ventanas identifican encuentros en t11,16,…,46. Esta composición es realizada
por portadores en el mismo Runtime, no por copiar resultados entre runtimes.
La suma aditiva es un cálculo de evaluación posterior, no un generador de respuestas.
La referencia homogénea con cuatro componentes comparte ocho entradas de
entrenamiento y carga total48; la ruta serial consume una consulta de13 y produce61,
mientras cuatro rutas simples consumen cuatro consultas de13 y producen25 cada una.
Es una diferencia entre profundidad de transformación y amplitud de respuestas;
no demuestra por sí sola superioridad general de un compuesto.

La comparación heterogénea reconstruye además dos memorias relativas y dos
relaciones móviles en un único N67. R4 mantiene las rutas móviles separadas
(25/27); R5 acopla sus dos etapas (25→39). Conservan los mismos cuatro tipos
funcionales, las cargas de entrenamiento y el presupuesto físico de consulta,
incluido un pulso de control fuera de la ruta acoplada. Las reservas de nuevos
valores producen36/42 frente a36→59. En ambas realizaciones se conservan las
relaciones relativas+1/-1 hasta520, mientras la expresión del comparador puede
coincidir: memoria diferencial y expresión no se sustituyen una por otra.
La coexistencia y el acoplamiento móvil están ejecutados; no se los presenta como
si toda la población heterogénea hubiese fusionado su conocimiento.

Un puente adicional sí conecta familias: la relación móvil formada por experiencia
con carga12 alcanza el lector relativo en5 y el comparador en6; en7, historias AB
y BA emiten direcciones+x y-x respectivamente ante esa misma entrada. La carga
del paquete no decide el signo desde Python. Desacoplar la experiencia móvil o
desplazar su ruta deja el comparador sin ese producto. Las reservas de cargas20
y26 conservan la distinción de dirección según la historia relativa. Es un uso
físico conjunto de acceso móvil e historia basal, con dominio N47 y horizonte20;
no una atribución automática de renovación indefinida a ese puente.

Los cortes dirigidos del producto formado tras la etapa3 conservan la primera
mitad 25,39,55,73 y alteran la segunda a20,22,24,26; el sham conserva165 final.
Otro corte diagnóstico sobre la relación de la siguiente etapa deja145 final.
No son la misma intervención. El receptor sin enseñanza en su segunda mitad
conserva73 sin añadir las nuevas relaciones. El desacoplamiento temporal produce
otro contexto y pierde productos posteriores. Las reservas cambian consultas,
historias y, cuando corresponde, retraso de la consulta: 17 produce169 final y
una historia distinta con consulta19 produce179. Son realizaciones distintas,
no ticks contados como réplicas.

## Conservación durante experiencias adicionales

`language_D01` adquiere L1…L8 mediante ocho experiencias separadas antes de sus
consultas. L1 se utiliza después de siete adquisiciones posteriores. Con un
codificador/decodificador fijo, las tres rondas contienen8/8 entradas admitidas y
8/8 direcciones acordes con la experiencia; la historia inversa invierte las
respuestas. Las dos reservas cambian historia, orden, carga de consulta y geometría
y conservan8/8 en cada ronda. Las 24 consultas de un mundo no son24 memorias ni24
réplicas. Ocho formas remiten a dos clases físicas direccionales en este aparato.

El emparejamiento no puede juzgarse sólo por la última ronda: sin señal durante
enseñanza hay0/8 decodificadas en la primera y8/8 en rondas posteriores; la propia
consulta puede encontrarse con historia ambiental residual. En el desacoplado
hay0/8 en la primera y direcciones posteriores opuestas al objetivo de la
experiencia. La consulta desplazada un tick pierde el acceso0/24 sin modificar
clocks desde el host. En señal sin acontecimiento, las24 consultas se rechazan por
ocupación. Son causas distintas: interacción de evaluación, fase y admisión.

El ensayo temporal de dos eventos opuestos conserva la dirección del evento
emparejado primero en la preparación de intervalo1. En la reserva de intervalo4,
la primera ronda da8/8, la segunda conserva admisión8/8 pero0/8 decodificadas y la
tercera rechaza8/8. La asociación temporal concreta es medible; no acredita una
relación abstracta ANTES con acceso indefinido.

La memoria relativa de referencia conserva delta1=+1 al adquirir delta2=-1 hasta
t520. La sonda tardía del segundo lector es rechazada por ocupación aunque los
centros y expresión existente persisten. El piloto relativo acoplado nuevo
conserva +1/-1 pero no obtiene un producto conjunto en sus puertos observados;
esa diferencia conservada no se cuenta como composición funcional conseguida.

## Trayectorias longitudinales compuestas guardadas

''' + '\n'.join(compounds) + '''

Cuando se utilizan copias redundantes de una relación, cada copia se adquiere por
experiencia y se contabiliza como recurso explícito. No se trasplanta una memoria
entrenada a MAIN ni se atribuye recuperación automática a una copia consumible.
Los productos conjuntos y sus consecuencias se distinguen de la consulta separada
de respaldos. Los primeros intentos con acceso fuera de fase se conservan.

## Regulación: fuente, estado adquirido y función

El contraflujo de referencia de CPC4 es una entrada externa programada cuya
consecuencia se realiza por v27. El nuevo grupo compara una fuente interna
semantic4 preparada antes deT0 y un pulso direccional adquirido por experiencias
neutrales. Esa separación identifica qué aportó el diseñador y qué depende de
historia. Un pulso aprendido no equivale por nombre a atención adaptativa.

''' + '\n'.join(regulation_rows) + '''

La primera cohorte C=-1 conserva utilidad5 sin regulador y con pulso aprendido,
inverso o desacoplado; no separa una ventaja funcional de esos tratamientos. La
fuente interna fija y su dirección inversa dan4, con otro reparto recurso/función.
La referencia Flat adversa de CPC4 usa C=+1: no se intercambian ambas cohortes para
fabricar una comparación. Los resultados nuevos, si figuran arriba, conservan ese
contexto y sus propios controles. La utilidad2F+R corresponde a paquetes exactos
en dos ventanas declaradas, no a un veredicto global del ente.

En la cohorte C=+1, el pulso adquirido por experiencias emparejadas restaura el
paquete funcional Flat (F1/R0), frente a F0/R1 sin pulso, con pulso de dirección
opuesta o con experiencias desacopladas. El efecto cambia por historia física,
con carga cero y sin un callback que decida cuándo borrar una celda. En el fork
causal t292, pulso y relay ocupan sitios contiguos: ambos centros tienen un vecino
activo, sin tetraedro y `rule_value=0`; la rama material elimina ambos en293.
No se trata del reducer que suma propuestas en un destino vacío. El corte RAW del
pulso en292 conserva clock y todos los demás sitios, deja avanzar el relay5 en293
y cambia la función posterior; sham y aumento de carga0→1 conservan el resultado.
Estos contrastes separan presencia/dirección de una explicación por energía extra.
Las reservas traducidas, cuando estén indexadas, se ejecutan con sus configuraciones
congeladas y sin mover individualmente el punto de intervención tras observarlas.
Es regulación por un estado direccional adquirido dentro de un diseño preparado;
la selección adaptativa según consecuencias previas sigue siendo otra pregunta.

## Lenguaje y escalas del conocimiento

El catálogo65 se conserva con su fuente. Las pruebas nuevas sostienen ocho
correspondencias opacas consultables con dos contenidos direccionales y
generalización limitada de emparejamiento temporal. El mapa de evidencia no las
convierte automáticamente en65 significados, YO/TÚ, negación general ni gramática.
Una consulta física devuelve materia y dirección; el renderer sólo presenta esa
lectura. Las relaciones consultadas por puertos fijos no prueban enrutamiento
aprendido hacia «quién sabe» una respuesta.

La escala componente expresa una relación; una ruta compuesta utiliza varias
relaciones físicamente; una red sólo dispone de la función transmitida cuando se
observa recepción y efecto. Los repertorios de mundos independientes no se suman
como una sola vida. La composición longitudinal con redundancia explicita qué
función permanece local y cuál participa en la respuesta común.

La extensión de reutilización del núcleo conserva el mismo MAIN de seis
componentes. P1/P2 adquieren K1/K2 y después reciben experiencias K3/K4 cuando
los productos anteriores dejan libres sus interfaces; sus respaldos se adquieren
separadamente. El producto común37 en83 utiliza un recurso ambiental7 y produce44
en88. Ese mismo portador encuentra la nueva relación de16 en145 y produce60,
encuentra la siguiente en217 y produce76; el nuevo recurso7 produce83 en222.
Las14 consultas de respaldo conservan las cuatro relaciones sin reenseñarlas
en la consulta. Son33 llamadas aplicadas:16 de enseñanza,14 sondas individuales,
una solicitud común y dos oportunidades ambientales. La integración ejecuta
cuatro contribuciones históricas sin copiar una salida desde Python.

Los controles y reservas de esa extensión figuran por caso en los paneles: corte
tardío del portador formado, cambio de dirección, sham, historia opuesta o
desacoplada, ruta no acoplada, nuevos orden/carga/geometría y retención quieta.
No se los suma como una única vida. La comparación distingue explícitamente el
coste de16 entradas de enseñanza en esta reutilización frente a12 en la
preparación anterior, que sólo duplicaba dos relaciones. Se conserva una
discrepancia textual del campo genérico `scope` de los primeros archivos: dice
«two redundantly acquired» aunque geometría, caso y libro de llamadas especifican
cuatro en la extensión. El dato primario no se reescribe; esta revisión lo aclara.

Con el mismo inventario de seis componentes, la configuración no acoplada conserva
las14 respuestas de respaldo, pero da51 en la consecuencia222 frente a83 en el
acoplado. La ventaja medida corresponde a esa transformación común, no a una
superioridad de retención. Invertir K3 o K4 mantiene su lectura histórica local y
cambia la consecuencia común a67. Desacoplar K3 suprime su primer uso e impide la
cadena completa; una consulta posterior termina adquiriendo una respuesta en ese
respaldo, por lo que no se la cuenta como retención previa.

En la reserva de orden K2→K1→K4→K3 y consulta7, los nuevos encuentros cambian de
sitio y tiempo:62 en150 y78 en212, con85 en la consecuencia222. La reserva con
consulta9 y K3 opuesta produce71 en222. El corte o giro del producto60 ya formado
en147 altera la cadena posterior; el sham conserva83. En el brazo de retención
quieta, después de338 no hay nuevas entradas hasta las cuatro consultas de1005;
las cuatro se admiten y expresan en1008. Estos horizontes y funciones se atribuyen
a sus individuos respectivos, sin concatenar cohortes como una sola vida.

## Revisión de lecturas previas y límites locales

Lectura previa: una sonda silenciosa indica memoria perdida. Evidencia: rechazo
ocupado y delta conservado. Lectura actual: acceso, memoria y expresión se separan.

Lectura previa: igual utilidad implica igual mecanismo. Evidencia: cortes con
bypass y diferentes perfiles F/R. Lectura actual: se conservan rutas alternativas
y el contenido físico de la consecuencia, no sólo una puntuación.

Lectura previa: sumar módulos aumenta conocimiento integrado. Evidencia: grupos
independientes requieren consultas propias y la ruta serial tiene otra latencia.
Lectura actual: acoplamiento, coste, retención y acceso deben compararse por tarea.

Quedan abiertas regulación seleccionada por consecuencias anteriores, consultas
autónomamente enrutadas, cambio de papeles comunicativos y adquisición acumulativa
del inventario semántico completo. Los pilotos localizan fallos de acceso o
acoplamiento del aparato, no un límite universal de v27. Los datos, controles y
reservas conservados permiten revisar cada atribución sin aceptar esta lectura.

## Recalcular y reproducir

`python src/audit.py --root .` recalcula los índices y paneles a partir de los
archivos primarios guardados; no ejecuta física. El ejecutor y demostrador del
paquete generan trayectorias. La validación técnica conserva backend, observación,
fork, cola pendiente y restauración en otro proceso; sus registros no se cuentan
como nuevos aprendizajes científicos. Los SHA-256 del índice verifican qué datos
se analizaron. Las vecindades completas se conservan en los primarios y los
snapshots permiten comprobar los intervalos indicados por cada caso.
'''
    (target / 'LECTURA_PROVISIONAL.md').write_text(text, encoding='utf-8')


def update_nsm(target, inventory, calculations):
    path = target / 'NSM65_EVIDENCIAS.json'
    if not path.exists():
        return
    value = read(path)
    entries = value.get('entries', [])
    if len(entries) != 65 or len({x['id'] for x in entries}) != 65:
        raise ValueError('The inherited NSM catalog must have exactly 65 distinct stable IDs')
    compound_rows = []
    for key, result in calculations.items():
        if 'blocks' not in result:
            continue
        compound_rows.append({'case_id': key, 'file': result['source'], 'sha256': result['source_sha256'],
                              'directions_experienced': result['case'].get('directions'),
                              'physical_geometry': result.get('geometry'), 'resources': result.get('resources'),
                              'scope_discrepancy': result.get('scope_discrepancy'),
                              'blocks': {k: {n: v[n] for n in ('queries', 'admitted', 'physically_decoded', 'matches_experienced_direction')} for k, v in result['blocks'].items()},
                              'native_outputs': result['native_active_output_records'],
                              'scope': result['scope']})
    value['schema'] = 'CPC5.NSM65.evidence.v2'
    value['compound_directional_functions'] = {
        'four_physically_separate_relations_attempted': ['K1', 'K2', 'K3', 'K4'],
        'content_classes': 2, 'physical_components': 6,
        'redundancy': 'Every declared primary/backup copy receives an actual experience. Earlier preparation duplicates K1/K2 only; the core-reuse extension duplicates all four while reusing P1/P2 for K3/K4. Backups are explicit resources, not trained-snapshot copies.',
        'cases': compound_rows,
        'semantic_counting': 'Four conditioned interfaces are not four distinct general NSM meanings. The existing eight-form component and the four-form compound are different individuals; their repertoires are not added.'}
    plans = {
        'participantes': {
            'test': 'Intercambiar físicamente emisor/destinatario con un tercer interlocutor, misma forma e interfaces fijas; reservar combinaciones de papeles.',
            'executed': 'Red A/B/C/D reproducida y transmisiones seriales nuevas; no se enseñaron referentes cambiantes YO/TÚ.',
            'cause': 'La identidad de emisor en los logs la conserva el observador; no constituye una relación deíctica adquirida.'},
        'identidad_estructura': {
            'test': 'Mismos soportes con historias distintas y soportes trasladados con firma funcional igual; consulta común que emita una distinción igual/otro/parte/tipo.',
            'executed': 'Contrastes físicos de historias y de arquitectura; igualdad calculada por el auditor.',
            'cause': 'No se construyó una respuesta nativa de identidad independiente del puerto o coordenada.'},
        'cantidad_comparacion': {
            'test': 'Presentar cantidades por encuentros físicos, igualar dosis y variar disposición; reservar cantidades y solicitar una comparación sin codificar el resultado.',
            'executed': 'Transformaciones aditivas de cascadas y variación de cargas de consulta; no palabras de cantidad ni comparador cardinal aprendido.',
            'cause': 'Una carga sumada no identifica por sí sola UNO/DOS/MÁS, tamaño o cuantificación.'},
        'valor_contextual': {
            'test': 'Enseñar señal y consecuencias actuales en dos contextos con utilidad invertida; evaluar señal sola y nuevo contexto conservando lector.',
            'executed': 'Paquetes F/R, costes y contraflujos medidos; la valoración2F+R es del evaluador.',
            'cause': 'No se devolvió utilidad como política ni se enseñó una asociación general BUENO/MALO al participante.'},
        'conocimiento_acceso': {
            'test': 'Igual lectura inicial con distinta accesibilidad; experiencia y sonda pertinente, sin leer el estado global desde el ente; separar ausencia de dato y certeza.',
            'executed': 'Memoria/expresión/admisión separadas y sondas comunes; diagnóstico de disponibilidad externo.',
            'cause': 'La clasificación del auditor no es una palabra o estado subjetivo adquirido por el ente.'},
        'accion_comunicacion': {
            'test': 'Contrastar emisión, recepción, acción y acontecimiento con información y dosis igualadas; enseñar forma después del acontecimiento y probar rol o situación reservada.',
            'executed': 'Portadores nativos combinan relaciones y producen consecuencias; cortes de producto y sham.',
            'cause': 'El mecanismo físico se midió; falta asociación específica y generalización de las expresiones HACER/PASAR/MOVER/DECIR.'},
        'tiempo': {
            'test': 'Variar acontecimientos e intervalos, mantener relación temporal, invertir orden y enseñar formas separadas; reservar intervalos y acontecimientos completos.',
            'executed': 'Tres ensayos de dos acontecimientos opuestos con intervalos1/4 y orden invertido.',
            'cause': 'Se midió emparejamiento temporal concreto; la reserva muestra deterioro de acceso después de la primera ronda.'},
        'espacio': {
            'test': 'Variar signo, traslación, marco y figura/fondo; enseñar y consultar la relación espacial sin elegir decoder según historia.',
            'executed': 'Direcciones±y adquiridas en8interfaces, reservas y compuesto de4relaciones; marco reticular fijo.',
            'cause': 'No se probaron cambios de marco ni todas las operaciones de una relación espacial general.'},
        'posibilidad_negacion_causalidad': {
            'test': 'Más de un contenido, ventana y ruta; enseñar presencia/ausencia o contingencia actual y consultar un contenido nuevo, sin usar timeout del host como detector nativo.',
            'executed': 'Omisiones, cortes, shams y diferencias de fase como controles instrumentados.',
            'cause': 'No se construyó detector nativo general de ausencia, posibilidad o explicación de causa para esas formas.'}}
    groups = {}
    def assign(group, ids):
        for identifier in ids.split():
            groups['NSM65.' + identifier] = group
    assign('participantes', 'I YOU SOMEONE SOMETHING PEOPLE BODY')
    assign('identidad_estructura', 'KINDS PARTS THIS THE_SAME OTHER BE_SOMEONE_SOMETHING IS_MINE LIKE_AS')
    assign('cantidad_comparacion', 'ONE TWO SOME ALL MUCH_MANY LITTLE_FEW BIG SMALL VERY MORE')
    assign('valor_contextual', 'GOOD BAD')
    assign('conocimiento_acceso', 'KNOW THINK WANT DONT_WANT FEEL SEE HEAR LIVE DIE')
    assign('accion_comunicacion', 'SAY WORDS TRUE DO HAPPEN MOVE')
    assign('tiempo', 'WHEN_TIME NOW BEFORE AFTER LONG_TIME SHORT_TIME FOR_SOME_TIME MOMENT')
    assign('espacio', 'BE_SOMEWHERE WHERE_PLACE HERE ABOVE BELOW NEAR FAR SIDE INSIDE TOUCH')
    assign('posibilidad_negacion_causalidad', 'THERE_IS NOT MAYBE CAN BECAUSE IF')
    for entry in entries:
        group = groups.get(entry['id'], 'identidad_estructura')
        entry['CPC5']['programa_relacional'] = {
            'familia': group, 'prueba_especifica_pendiente': plans[group]['test'],
            'cobertura_ejecutada': plans[group]['executed'], 'causa_local_del_alcance': plans[group]['cause'],
            'plan_no_equivale_a_prueba_ejecutada': True}
        if entry['id'] in ('NSM65.ABOVE', 'NSM65.BELOW'):
            entry['CPC5']['soporte_compuesto_nuevo'] = [x['case_id'] for x in compound_rows]
            entry['CPC5']['alcance_del_soporte_compuesto'] = 'Funciones direccionales±y y conservación de acceso con recursos explícitos; no significa que el texto humano ARRIBA/DEBAJO se enseñara en cada nuevo compuesto.'
    value['all_65_have_local_method_and_coverage'] = True
    value['generated_from_current_primary_index_count'] = inventory['measurement_records']
    put(path, value)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    root = args.root.resolve()
    target = root / 'revision'
    files = sorted((root / 'resultados').rglob('MEASUREMENTS.json'))
    index, calculations, observations, architecture, retention = [], {}, [], [], []
    original_records = {}
    categories = Counter()
    for path in files:
        value = read(path)
        relative = path.relative_to(root).as_posix()
        original_records[relative] = value
        case_key = path.parent.name
        if case_key in calculations:
            raise ValueError('Case folder names must be unique for review: ' + case_key)
        case = value.get('case', {})
        declared_id = case.get('id', case_key) if isinstance(case, dict) else case
        if relative.startswith('resultados/references/'):
            category = 'DIRECTED_PRIOR_REPRODUCTION_OR_DIAGNOSTIC'
        elif 'cycles' not in value and 'readouts' in value and 'case' in value and isinstance(case, dict) and 'chains' in case:
            category = 'NATIVE_COMMUNICATION_GRAPH'
        elif 'event_directions' in case and 'lessons' in value and 'readouts' in value and all('cycle' in r for r in value['readouts']):
            category = 'LONGITUDINAL_LEXICAL_COMPONENT'
        elif 'lessons' in value and 'readouts' in value and all('relation' in r and 'block' in r for r in value['readouts']):
            category = 'LONGITUDINAL_COMPOUND'
        elif 'rows' in value and value['rows'] and 'relative_cells' in value['rows'][0]:
            category = 'HETEROGENEOUS_POPULATION'
        elif 'rows' in value and value['rows'] and all(k in value['rows'][0] for k in ('A', 'B', 'reader', 'comparator')):
            category = 'MOBILE_RELATIVE_CROSS_FAMILY_BRIDGE'
        elif 'profiles' in value and 'source_preparation' in value and 'captures' in value:
            category = 'REGULATION_CONTRAST'
        elif 'memories' in value.get('final', {}) and 'rows' in value:
            category = 'RELATIVE_MEMORY_AND_COUPLING'
        else:
            category = 'NEW_MEASUREMENT_SCHEMA_REQUIRES_DOMAIN_REVIEW'
        categories[category] += 1
        result = {'source': relative, 'source_sha256': sha(path)}
        if category == 'NATIVE_COMMUNICATION_GRAPH':
            result.update(network_metrics(value))
            architecture.append({'case_id': case_key, **result})
        elif category == 'LONGITUDINAL_LEXICAL_COMPONENT':
            result.update(language_metrics(value))
            retention.append({'case_id': case_key, **result})
        elif category == 'REGULATION_CONTRAST':
            result.update(regulation_metrics(value))
        elif category == 'LONGITUDINAL_COMPOUND':
            result.update(compound_metrics(value))
            retention.append({'case_id': case_key, **result})
        elif category == 'HETEROGENEOUS_POPULATION':
            result.update(heterogeneous_metrics(value))
            retention.append({'case_id': case_key, **result})
        elif category == 'MOBILE_RELATIVE_CROSS_FAMILY_BRIDGE':
            result.update(bridge_metrics(value))
            retention.append({'case_id': case_key, **result})
        elif 'rows' in value and any('memories' in r for r in value['rows'] if isinstance(r, dict)):
            result.update(relative_metrics(value))
            retention.append({'case_id': case_key, **result})
        else:
            for key in ('scope', 'classification', 'profiles', 'external_utility', 'technical', 'calculations'):
                if key in value:
                    result[key] = value[key]
            result['admission'] = receipts_summary(value)
        calculations[case_key] = result
        # This small review set selects readout/capture centers and relational panels.
        # Full Moore windows and all trace frames remain in the primary source.
        selection = {k: value[k] for k in ('readouts', 'captures', 'rows', 'uses', 'native_windows') if k in value}
        if value.get('trace') and 'pulse_gate' in value['trace'][0]:
            selection['trace'] = value['trace'][:3]
        seen = set()
        for pointer, record in walk_records(selection):
            if '/Moore26_plus_center/' in pointer or '/local_windows/' in pointer:
                continue
            key = (record.get('tick'), tuple(record.get('site', [])), record.get('raw', record.get('RAW_hex')))
            if key in seen:
                continue
            seen.add(key)
            observations.append({'case_id': case_key, 'source': relative, 'json_pointer': pointer,
                                 'provenance': 'PASSIVE_PRIMARY_RECORD_SELECTION', 'measurement': record})
        index.append({'case_id': case_key, 'declared_case_id': declared_id, 'category': category,
                      'source': relative, 'sha256': sha(path), 'size_bytes': path.stat().st_size,
                      'tick_final': final_tick(value), 'elapsed_seconds_worker': value.get('elapsed_seconds'),
                      'stored_status': value.get('status', 'MEASUREMENTS_SAVED'),
                      'readout_records': len(value.get('readouts', [])), 'case': case,
                      'independent_replication_count_not_inferred': True})
    attempts = []
    for path in sorted((root / 'jobs').rglob('*.json')):
        try:
            value = read(path)
        except (ValueError, OSError):
            continue
        if isinstance(value, dict) and any(k in value for k in ('exit_code', 'returncode', 'status')):
            attempts.append({'file': path.relative_to(root).as_posix(), 'sha256': sha(path), 'record': value})
    for row in observations:
        original = original_records[row['source']]
        for token in row['json_pointer'].split('/')[1:]:
            key = token.replace('~1', '/').replace('~0', '~')
            original = original[int(key)] if isinstance(original, list) else original[key]
        if original != row['measurement']:
            raise AssertionError('Review selection differs from primary JSON pointer')
        for field in ('raw', 'RAW_hex', 'clock', 'clock_u64'):
            if field not in original:
                continue
            number = original[field]
            if isinstance(number, float) or isinstance(number, bool):
                raise AssertionError('UInt64 observation was converted to float/bool')
            integer = int(number, 16) if field == 'RAW_hex' else int(number)
            if not 0 <= integer <= 2**64 - 1:
                raise AssertionError('UInt64 observation out of range')
    inventory = {'schema': 'CPC5.review.primary_index.v1', 'generated_utc': datetime.now(timezone.utc).isoformat(),
                 'measurement_records': len(index), 'counts_by_category': dict(categories),
                 'primary_cases': index, 'technical_job_records': attempts,
                 'review_technical_checks': {'all_observation_JSON_pointers_match_primary_exactly': True,
                                              'RAW_clock_uint64_no_float_and_in_range': True,
                                              'case_folder_names_unique': True,
                                              'observations_checked': len(observations)},
                 'counting': 'One saved MEASUREMENTS per case path. Reproductions, diagnostic forks, queries and ticks remain distinct; a case is not automatically an independent replicate.',
                 'selection': 'OBSERVACIONES selects primary centers/readouts. Full contexts and checkpoints remain at indexed primary paths.'}
    inventory['source_hash_coverage'] = source_hash_coverage(root, index, original_records)
    inventory['communication_index'] = message_index(root, original_records)
    physical_comparisons = []
    def normalized_digest(value):
        return {'tick': value.get('tick'), 'RAW_sha256': value.get('raw_sha256', value.get('RAW_sha256')),
                'clock_sha256': value.get('clock_sha256')}
    for first, second in (('REG_CF_REFERENCE', 'REG_FLAT_LEARNED_PULSE'),
                           ('REG_CF_SHAM', 'REG_CF_REFERENCE'),
                           ('REG_CF_LOAD1', 'REG_CF_REFERENCE'),
                           ('REG_CF_REMOVE', 'REG_CF_REFERENCE')):
        if first in calculations and second in calculations:
            a, b = calculations[first], calculations[second]
            physical_comparisons.append({'first': first, 'second': second,
                                         'first_state': normalized_digest(a['final_physics']),
                                         'second_state': normalized_digest(b['final_physics']),
                                         'full_RAW_clock_tick_equal': normalized_digest(a['final_physics']) == normalized_digest(b['final_physics']),
                                         'kind': 'TECHNICAL_POSTHOC_STATE_COMPARISON',
                                         'not_an_independent_scientific_replication': True})
    put(target / 'INDICE_EVIDENCIA.json', inventory)
    put(target / 'CALCULOS.json', {'schema': 'CPC5.review.calculations.v1', 'cases': calculations,
                                  'technical_physical_state_comparisons': physical_comparisons,
                                  'all_calculations_external_after_trajectories': True,
                                  'universal_scientific_verdict': None})
    put(target / 'COMPARACION_ARQUITECTURAS.json', {
        'schema': 'CPC5.review.architectures.v1', 'native_graph_cases': architecture,
        'heterogeneous_population_cases': [compact_review({'case_id': k, **v}) for k, v in calculations.items() if 'physical_population_types' in v],
        'cross_family_bridge_cases': [compact_review({'case_id': k, **v}) for k, v in calculations.items() if 'panel' in v and 'delta_recomputed' in (v['panel'][0] if v['panel'] else {})],
        'longitudinal_compound_cases': [compact_review({'case_id': k, **v}) for k, v in calculations.items() if 'blocks' in v],
        'R0_reference_cases': [x['case_id'] for x in index if x['case_id'].startswith('ABCD_')],
        'comparison_domain': 'N67 finite physical mobile routes. Serial coupling and population fan-out differ in queries, stage latencies and transformations; not a universal ranking.',
        'resources_controlled_and_uncontrolled': 'Rows declare components, top level labels, inputs, payload sum, N and ticks. Equal component count does not equal identical task depth or per-group input count.',
        'consumable_or_renewable': 'Network graph readouts establish finite composition; renewable retained access is separately measured in lexical/relative and new longitudinal cases.'})
    put(target / 'RETENCION_Y_ACCESO.json', {'schema': 'CPC5.review.retention.v1', 'cases': [compact_review(v) for v in retention],
                                           'important_distinction': 'Retained relation, current expression, admitted probe and useful consequence are separate measurements. Repeated probes can change acquired state.'})
    with (target / 'OBSERVACIONES.jsonl').open('w', encoding='utf-8') as stream:
        for row in observations:
            stream.write(json.dumps(row, ensure_ascii=False, separators=(',', ':')) + '\n')
    write_guides(target, inventory, calculations)
    update_nsm(target, inventory, calculations)
    print(json.dumps({'measurement_records': len(index), 'categories': dict(categories),
                      'review_observations': len(observations), 'technical_job_records': len(attempts)}, ensure_ascii=False))


if __name__ == '__main__':
    main()
