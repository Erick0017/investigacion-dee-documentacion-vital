"""Complemento N0: todos los eventos, WAL/SHM y conciliación de resultados/snapshots."""
from collections import Counter
import argparse
import gzip
import hashlib
import json
from pathlib import Path
import shutil


def sha(data):
    return hashlib.sha256(data).hexdigest()


def dump(path, value):
    with path.open('x', encoding='utf8', newline='\n') as stream:
        json.dump(value, stream, ensure_ascii=False, sort_keys=True, indent=2)
        stream.write('\n')


def archived(folder, index, key):
    row = next(x for x in index['sources'] if x['id'] == key)
    data = gzip.decompress((folder / row['export']).read_bytes())
    assert sha(data) == row['source_sha256']
    return data


def recalc(folder):
    index = json.loads((folder / 'INDICE.json').read_bytes())
    db = json.loads(archived(folder, index, 'SQLITE_ROWS'))
    events = [json.loads(x) for x in archived(folder, index, 'JOURNAL').splitlines() if x]
    witness = json.loads((folder / 'CONCILIACION_Y_SIDECARS_RO_R02.json').read_bytes())
    total = db['plan']['events']
    before_rows = [x for x in events if x.get('kind') == 'scheduled_material_before_submission']
    completed = {x['id']: x for x in db['requests'] if x['status'] == 'completed' and x['id'].startswith('apd04_reserve_r01_')}
    card_ops = {x.get('transport_id'): x for x in db['VIDA']['operations']}
    comparisons = []
    for source in witness['completed_result_and_snapshot_checks']:
        rid = source['id']
        row, op = completed[rid], card_ops[rid]
        native = json.loads(row['result'])
        assert source['result_file_sha256'] == op['result_sha256'] and source['result_JSON_equal_DB_without_commit_wrapper']
        assert source['DB_only_fields'] == ['committed_snapshot']
        assert source['snapshot_sha256'] == native['committed_snapshot']['snapshot_sha256']
        assert source['snapshot_tick'] == native['after_tick']
        comparisons.append({'id': rid, 'snapshot_tick': source['snapshot_tick'],
             'result_file_sha256': source['result_file_sha256'], 'snapshot_sha256': source['snapshot_sha256'],
             'result_JSON_equal_DB_without_commit_wrapper': True, 'DB_only_fields': ['committed_snapshot']})
    assert len(comparisons) == len(completed)
    assert witness['sidecars_before'] == witness['sidecars_after']
    assert all(not x['exists'] for x in witness['sidecars_before'])
    without_id = []
    for i, event in enumerate(total):
        if not event.get('request_id'):
            matches = [x for x in events if x.get('kind') == 'scheduled_checkpoint' and x.get('tag') == event.get('tag')]
            without_id.append({'plan_index': i, 'event_exact': event, 'completed_journal_matches': len(matches),
                               'not_executed': len(matches) == 0})
    result = json.loads((folder / 'RECALCULO_CIERRE_RESERVA_N0.json').read_bytes())
    return {'schema': 'APD04.reserve.full_calendar_and_RO_reconciliation.N0.R03',
         'plan_events_all': len(total), 'material_events_with_request_ID': sum(bool(x.get('request_id')) for x in total),
         'events_without_ID': without_id, 'material_submission_attempts_recorded': len(before_rows),
         'material_events_completed': len(completed), 'completed_result_and_snapshot_reconciliation': comparisons,
         'late_completed_results_absent_from_driver_journal': result['late_completed_not_in_journal'],
         'WAL_SHM_before_after': witness['sidecars_before'], 'immutable_SQLite_valid_for_this_closed_cut': True,
         'work_opportunities_completed': result['work_counts']['completed'],
         'native_receipt_denominator': {'scope': 'Only seven completed work opportunities; two administrative completed events add zero Native inputs. The eighth processing opportunity has no committed result, so its possible Native activity is UNKNOWN, not zero.',
                                      'requested_IDs': result['unique_native_inputs'], 'statuses': result['native_input_statuses']},
         'pending_after_full_window_request': {'definition': db['plan']['after_window_pending'],
            'present_in_SQLite': any(x['id'] == db['plan']['after_window_pending']['request_id'] for x in db['requests']),
            'no_queued_continuation_claim': True},
         'no_FIN_or_driver_result': not db['FIN_VENTANA_exists'] and not db['driver_RESULTADO_exists'],
         'realized_complete_60minute_protocol': False, 'new_Native_ticks': 0,
         'scope': 'Exact archived schedule/DB/card/result/snapshot reconciliation; no owner/replay/repair or memory destruction inference.'}


def export(root, source, out):
    assert not out.exists()
    index = json.loads((source / 'INDICE.json').read_bytes())
    db = json.loads(archived(source, index, 'SQLITE_ROWS'))
    life = db['VIDA']['life_id']
    journal = root / 'sistema/estado/servicios_persistentes' / life / 'cola.sqlite3'
    def sidecars():
        return [{'suffix': suffix, 'exists': journal.with_name(journal.name + suffix).exists(),
                 'bytes': journal.with_name(journal.name + suffix).stat().st_size if journal.with_name(journal.name + suffix).exists() else 0}
                for suffix in ('-wal', '-shm')]
    before = sidecars()
    assert all(not x['exists'] for x in before), 'WAL/SHM present: use a separate DB+WAL copy, do not assert immutable completeness'
    journal_hash = sha(journal.read_bytes())
    checks = []
    operations = {x.get('transport_id'): x for x in db['VIDA']['operations']}
    service = journal.parent
    for row in db['requests']:
        if row['status'] != 'completed' or not row['id'].startswith('apd04_reserve_r01_'):
            continue
        op, native = operations[row['id']], json.loads(row['result'])
        result_path = service / op['result_file']
        result_bytes = result_path.read_bytes()
        snap = root / 'sistema' / native['committed_snapshot']['snapshot']
        checks.append({'id': row['id'], 'result_file': result_path.relative_to(root).as_posix(),
             'result_file_sha256': sha(result_bytes),
             'result_JSON_equal_DB_without_commit_wrapper': json.loads(result_bytes) == {k: v for k, v in native.items() if k != 'committed_snapshot'},
             'DB_only_fields': sorted(set(native) - set(json.loads(result_bytes))),
             'snapshot': snap.relative_to(root).as_posix(), 'snapshot_sha256': sha(snap.read_bytes()),
             'snapshot_tick': native['after_tick']})
    after = sidecars()
    assert before == after and sha(journal.read_bytes()) == journal_hash
    shutil.copytree(source, out)
    shutil.copyfile(Path(__file__), out / 'CODIGO' / Path(__file__).name)
    dump(out / 'CONCILIACION_Y_SIDECARS_RO_R02.json', {'sidecars_before': before, 'sidecars_after': after,
         'SQLite_sha256_unchanged': journal_hash, 'completed_result_and_snapshot_checks': checks,
         'original_DB_or_sidecars_modified': False, 'new_Native_ticks': 0})
    result = recalc(out)
    dump(out / 'RECALCULO_CALENDARIO_Y_CONCILIACION_R02.json', result)
    members = [{'file': p.relative_to(out).as_posix(), 'bytes': p.stat().st_size, 'sha256': sha(p.read_bytes())}
               for p in sorted(out.rglob('*')) if p.is_file()]
    dump(out / 'MANIFIESTO_R03.json', {'members': members, 'new_Native_ticks': 0, 'R01_R02_preserved_unchanged': True,
         'R02_failure': 'No physical discrepancy: standalone result file predates the administrative committed_snapshot envelope added in SQLite. R03 checks every core field and retains that wrapper separately; full original bytes and R02 failure stay preserved.'})
    print(json.dumps({k: result[k] for k in ('plan_events_all', 'material_events_with_request_ID', 'events_without_ID',
        'material_submission_attempts_recorded', 'material_events_completed', 'work_opportunities_completed')}))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='operation', required=True)
    p = sub.add_parser('export'); p.add_argument('--root', required=True, type=Path); p.add_argument('--source', required=True, type=Path); p.add_argument('--out', required=True, type=Path)
    p = sub.add_parser('recalc'); p.add_argument('--evidence', required=True, type=Path); p.add_argument('--out', required=True, type=Path)
    args = parser.parse_args()
    if args.operation == 'export':
        export(args.root, args.source, args.out)
    else:
        dump(args.out, recalc(args.evidence))
