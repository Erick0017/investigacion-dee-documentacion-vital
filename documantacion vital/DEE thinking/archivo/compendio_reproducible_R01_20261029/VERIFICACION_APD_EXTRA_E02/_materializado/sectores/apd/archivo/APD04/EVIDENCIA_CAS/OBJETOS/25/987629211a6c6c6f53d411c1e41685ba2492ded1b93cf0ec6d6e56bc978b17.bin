"""Extrae únicamente primarios APD04 ya cerrados para un borrador acotado.

No Native, no vida activa, no lecturas de SQLite vivo, ni edición S/Word/Full.
La selección es explícita: no añade resultados que sigan en ejecución.
"""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path


def digest(data):
    return hashlib.sha256(data).hexdigest()


def dump(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x', encoding='utf8', newline='\n') as stream:
        json.dump(value, stream, ensure_ascii=False, sort_keys=True, indent=2)
        stream.write('\n')


def main(root, out):
    root, out = root.resolve(), out.resolve()
    lab = root / 'laboratorio/campanas/APD04_ECOSISTEMA_COGNITIVO'
    ev = root / 'evidencia/campanas/APD04_ECOSISTEMA_COGNITIVO'
    if not out.is_relative_to(lab) and not out.is_relative_to(ev):
        raise ValueError('Write only a new LAB/EV draft directory')
    out.mkdir(parents=True, exist_ok=False)
    sources = []

    def record(path, role):
        data = path.read_bytes()
        row = {'id': f'S{len(sources):04d}', 'source': path.relative_to(root).as_posix(),
               'sha256': digest(data), 'bytes': len(data), 'role': role}
        sources.append(row)
        return json.loads(data), row

    helper = lab / 'controles_diseno/recalcular_exportar_controles_apd04_n0_r01.py'
    helper_bytes = helper.read_bytes()
    frozen = out / 'FUENTE_CALCULO_ARCHIVADO.py'
    frozen.write_bytes(helper_bytes)
    sources.append({'id': 'HELPER', 'source': helper.relative_to(root).as_posix(),
                    'sha256': digest(helper_bytes), 'bytes': len(helper_bytes), 'role': 'exact_N0_RAW_decoder_used'})
    spec = importlib.util.spec_from_file_location('closed_apd04_decoder', frozen)
    decoder = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(decoder)
    groups = ['CONTROLES_LEXICO_REFERENCIA_AUX_R01', 'CONTROLES_DOCENTE_B_AUX_R01',
              'CONTROLES_REFERENCIAS_RESTANTES_AUX_R02']
    branches = []
    all_checks = []
    for group in groups:
        for closure in sorted((ev / group).glob('*/CIERRE.json')):
            c, csource = record(closure, 'closed_or_preserved_instrumental_branch_closure')
            label, branch = c['label'], closure.parent
            continuation = None
            # R04 is explicit, not selected by greatest timestamp or silently
            # substituted for the failed original REF_OMIT.
            r04 = branch / 'CONTINUACION_MISMA_VIDA_R04/CIERRE_CONTINUACION.json'
            if r04.is_file():
                continuation, rsource = record(r04, 'declared_same_life_R04_continuation')
                if continuation.get('error') or continuation.get('source_changed') or not continuation.get('continued_same_world_id'):
                    raise ValueError('Not a closed R04 continuation')
            rows, receipt_map = [], {}
            primary_paths = sorted(branch.glob('[0-9][0-9]_*.json'))
            if continuation:
                primary_paths += sorted(r04.parent.glob('[0-9][0-9]_*.json'))
            for primary in primary_paths:
                value, source = record(primary, 'exact_primary_response_before_RAW_recalculation')
                scanned = decoder.scan(value)
                checks = scanned.pop('checks')
                all_checks.extend({'source_id': source['id'], **check} for check in checks)
                rows.append({'event': primary.relative_to(branch).as_posix(), 'source_id': source['id'],
                             'source_sha256': source['sha256'], 'metrics': scanned})
                for receipt in scanned['receipts']:
                    key = str(receipt['receipt']['id'])
                    old = receipt_map.get(key)
                    if old is None or old['receipt'].get('status') in ('scheduled', 'pending', 'admitted'):
                        receipt_map[key] = receipt
            statuses = {}
            for receipt in receipt_map.values():
                status = receipt['receipt'].get('status')
                statuses[status] = statuses.get(status, 0) + 1
            branches.append({'label': label, 'life': c['life'], 'kind': c['kind'], 'condition': c['condition'],
                 'initial_tick': c['initial_tick'], 'final_tick_original': c['final_tick'],
                 'prefix_snapshot_sha256': c['prefix_snapshot_sha256'],
                 'original_error': c.get('error'), 'original_source_changed': c.get('source_changed'),
                 'closure_source_id': csource['id'], 'same_life_R04': continuation,
                 'lexical': [{'event': r['event'], 'source_id': r['source_id'], **x} for r in rows for x in r['metrics']['lexical']],
                 'numeric': [{'event': r['event'], 'source_id': r['source_id'], **x} for r in rows for x in r['metrics']['primitives']],
                 'references': [{'event': r['event'], 'source_id': r['source_id'], **x} for r in rows for x in r['metrics']['references']],
                 'unique_exported_physical_request_IDs_in_branch': len(receipt_map), 'receipt_statuses': statuses,
                 'receipt_scope': 'Only exported physical receipt IDs, deduplicated within branch. Shared prefix is not another independent learner.',
                 'events': rows})
    fixed = {
        'MAIN_PREFIX_RECALC': 'RECALCULO_MAIN_CERRADO_PREFIJO_Y_ADVERSO_R01/RECALCULO_COMPACTO.json',
        'MAIN_AUTOPSY': 'DIAGNOSTICO_SUPERVISION_MAIN_R01/RECALCULO_N0.json',
        'MAIN_ADVERSE_DRIVER': 'MAIN_CONTENIDO_Y_CARGA_R01/TRAYECTORIA/RESULTADO.json',
        'MAIN_ADVERSE_WRAPPER': 'MAIN_CONTENIDO_Y_CARGA_R01/RESULTADO_SUPERVISION.json',
        'CONTINUABLE90S_DRIVER': 'CONTINUABLE_OPERATIVO_R01/TRAYECTORIA/RESULTADO.json',
        'CONTINUABLE90S_WRAPPER': 'CONTINUABLE_OPERATIVO_R01/RESULTADO_SUPERVISION.json',
        'FORK_N0': 'FORK_CONTINUABLE_R01/FORK_COMPLETO_Y_UI_REGISTRADA.json'
    }
    fixed_values = {}
    for key, relative in fixed.items():
        path = ev / relative
        if path.is_file():
            value, source = record(path, key)
            fixed_values[key] = {'source_id': source['id'], 'value': value}
        else:
            fixed_values[key] = {'source_id': None, 'status': 'NOT_READ_NOT_FOUND_AT_EXPLICIT_PATH', 'locator': relative}
    if any(not x['ok'] for x in all_checks):
        raise ValueError('RAW recalculation disagrees; preserve partial fixture and investigate')
    for source in sources:
        if digest((root / source['source']).read_bytes()) != source['sha256']:
            raise ValueError('A supposedly closed source changed during N0 read')
    dump(out / 'DATOS_CERRADOS_Y_HASHES.json', {
        'schema': 'APD04.closed_prefix_draft.primary_analysis.N0.R01', 'status': 'DRAFT_NOT_FINAL_CUT',
        'sources': sources, 'branches': branches, 'fixed_closed_results': fixed_values,
        'RAW_checks': all_checks, 'RAW_check_count': len(all_checks), 'RAW_issues': [], 'new_native_ticks': 0,
        'scope': 'Closed named prefix and original AUX controls only. Not later reserve, Full, final promotion, or an account of independent learners.'})
    print(json.dumps({'out': str(out), 'sources_read': len(sources), 'branches': len(branches),
                      'RAW_checks': len(all_checks), 'new_native_ticks': 0, 'status': 'DRAFT_NOT_FINAL_CUT'}, ensure_ascii=False))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    main(args.root, args.out)
