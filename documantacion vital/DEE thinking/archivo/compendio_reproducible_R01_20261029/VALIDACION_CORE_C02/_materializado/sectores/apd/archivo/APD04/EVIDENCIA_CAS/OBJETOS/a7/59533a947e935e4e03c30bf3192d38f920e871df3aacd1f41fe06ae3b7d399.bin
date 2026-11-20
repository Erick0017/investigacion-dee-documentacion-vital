"""Autopsia retrospectiva de reserva por guarda, SQLite RO immutable, cero Native."""
from array import array
from collections import Counter
import argparse
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import sqlite3
import struct
import zlib

LIFE = 'APD04_ACTUADOR_REAL_R02'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def dump(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x', encoding='utf8', newline='\n') as stream:
        json.dump(value, stream, ensure_ascii=False, sort_keys=True, indent=2)
        stream.write('\n')


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def read_source(folder, index, key):
    row = next(x for x in index['sources'] if x['id'] == key)
    encoded = (folder / row['export']).read_bytes()
    assert sha(encoded) == row['export_sha256']
    data = gzip.decompress(encoded)
    assert sha(data) == row['source_sha256'] and len(data) == row['source_bytes']
    return data


def recalc(folder):
    index = json.loads((folder / 'INDICE.json').read_bytes())
    db = json.loads(read_source(folder, index, 'SQLITE_ROWS'))
    observer = module('frozen_parser', folder / 'CODIGO/observador_snapshot.py')
    common = module('frozen_common', folder / 'CODIGO/exportar_reserva_prefijo_completado_n0_r01.py')
    plan, card, wrapper = db['plan'], db['VIDA'], db['wrapper']
    byid = {r['id']: r for r in db['requests']}
    completed_rows = [r for r in db['requests'] if r['id'].startswith('apd04_reserve_r01_') and r['status'] == 'completed']
    synthetic = b''.join((json.dumps({'kind': 'scheduled_material_result', 'requested_id': r['id'],
         'result': {'request': {'status': 'completed', 'result': r['result']}}}) + '\n').encode('utf8') for r in completed_rows)
    primary = common.primary_summary(synthetic, observer)
    all_inputs = {str(r['id']): r for p in primary for r in p['receipts']}
    events = [json.loads(line) for line in read_source(folder, index, 'JOURNAL').splitlines() if line]
    submissions = {row['event']['request_id'] for row in events if row.get('kind') == 'scheduled_material_before_submission'}
    journal_completed = {row['requested_id'] for row in events if row.get('kind') == 'scheduled_material_result'
                         and row['result']['request']['status'] == 'completed'}
    calendar = []
    for event in plan['events']:
        rid = event.get('request_id')
        if rid is None:
            continue
        row = byid.get(rid)
        calendar.append({'request_id': rid, 'at_seconds': event.get('at_seconds'), 'kind': event.get('kind'),
             'journal_before_submission': rid in submissions, 'journal_completed': rid in journal_completed,
             'database_status': row['status'] if row else None, 'database_seq': row['seq'] if row else None,
             'planned_but_not_submitted': row is None and rid not in submissions})
    raw_data = zlib.decompress((folder / 'CAMPOS/ULTIMO_RAW_U64_LE.zlib').read_bytes())
    raw = observer.qarray(raw_data)
    info = index['last_fields']
    assert sha(raw_data) == info['RAW_sha256'] and len(raw) == info['N']**3
    # All clocks were checked equal to tick in the original complete snapshot.
    clocks = array('Q', [info['tick']]) * len(raw)
    assert sha(observer.pbytes(clocks)) == info['clocks_sha256']
    metrics = common.metrics(raw, clocks, info['N'], info['tick'])
    assert metrics == info['metrics']
    context = json.loads(read_source(folder, index, 'LAST_CONTEXT'))
    mu = []
    for site in ([14, 14, 15], [16, 14, 15]):
        i = observer.index(site, info['N'])
        mu.append({'site': site, 'clock': str(clocks[i]), **observer.fields(raw[i])})
    reconciled = []
    receipt_byid = {str(r['id']): r for r in context['relevant_receipts']}
    status_codes = {'applied': 2, 'rejected_occupied': 5}
    for key, primary_receipt in all_inputs.items():
        native = receipt_byid[key]
        assert native['channels'] == primary_receipt['channels']
        assert native['requested_tick'] == primary_receipt['requested_tick']
        assert native['status'] == status_codes[primary_receipt['status']]
        reconciled.append(key)
    work = [row for p in primary for row in p['work_opportunities']]
    pending = [{'id': r['id'], 'status': r['status'], 'seq': r['seq'], 'payload_sha256': r.get('payload_sha'),
                'payload_exact': r['payload']} for r in db['requests'] if r['status'] in ('queued', 'processing', 'uncertain')]
    count = Counter(r.get('status') for r in all_inputs.values())
    return {'schema': 'APD04.reserve.guard_closure.archived_recalculation.N0.R01',
        'life': LIFE, 'status': 'HOST_GUARD_CLOSURE_UNCOMMITTED_FUTURE_PRESERVED_NOT_CONTINUABLE_CERTIFICATION',
        'wrapper_exit_code': wrapper['exit_code'], 'wrapper_wall_seconds': wrapper['actual_wall_seconds'],
        'wrapper_final_processes': wrapper['final_total_job']['job_active_processes'],
        'FIN_VENTANA_exists': db['FIN_VENTANA_exists'], 'driver_RESULTADO_exists': db['driver_RESULTADO_exists'],
        'scheduled_events_with_ID': len(calendar), 'journal_submission_attempts': sum(x['journal_before_submission'] for x in calendar),
        'database_submitted_events': sum(x['database_status'] is not None for x in calendar),
        'database_completed_events': sum(x['database_status'] == 'completed' for x in calendar),
        'journal_completed_events': sum(x['journal_completed'] for x in calendar),
        'late_completed_not_in_journal': [x['request_id'] for x in calendar if x['database_status'] == 'completed' and not x['journal_completed']],
        'not_submitted_events': sum(x['planned_but_not_submitted'] for x in calendar), 'calendar': calendar,
        'pending_transport': pending, 'UI_protocol': db['UI_protocol'], 'interrupted_marker': db['marker'],
        'last_committed_tick': card['physical']['tick'], 'last_snapshot_sha256': card['snapshot_sha256'],
        'work_counts': {'completed': len(work), 'formed': sum(x['RAW_choice'] is not None for x in work),
             'NULL': sum(x['RAW_choice'] is None for x in work), 'useful': sum(bool(x['effect'].get('useful')) for x in work)},
        'unique_native_inputs': len(all_inputs), 'native_input_statuses': dict(count),
        'primary_results': primary, 'last_global_fields': metrics, 'mu_numeric_A_B': mu,
        'external_B_minus_A_not_actor_answer': mu[1]['s_reg'] - mu[0]['s_reg'],
        'last_native_pending': context['pending_native_events'], 'interfaces': len(context['channels']),
        'committed_primary_receipts_reconciled': len(reconciled),
        'new_Native_ticks': 0, 'owners_started': 0, 'same_ID_rePUTs': 0,
        'limits': ['No normal continuation is certified: interrupted marker and any processing request remain preserved.',
          'Guard timeout and absent FIN are host/transaction facts, not death or memory destruction.',
          'RAW/clocks arrays and selected operational context are not a continuable complete snapshot.',
          'External reference difference is not Native access or recovered content.',
          'Missed events and requested but unfinished opportunities are not cognitive errors.']}


def export(root, out):
    system = root / 'sistema'
    ev = root / 'evidencia/campanas/APD04_ECOSISTEMA_COGNITIVO'
    run = ev / 'RESERVA60_REAL_R02_R01'
    card_path = system / 'estado/vidas' / LIFE / 'VIDA.json'
    marker_path = card_path.with_name('FUTURO_INTERRUMPIDO.json')
    protocol = system / 'estado/entrada_sencilla/vidas' / LIFE / 'PROTOCOLO.json'
    journal = system / 'estado/servicios_persistentes' / LIFE / 'cola.sqlite3'
    if any(journal.with_name(journal.name + suffix).exists() for suffix in ('-wal', '-shm')):
        raise ValueError('immutable SQLite requires settled DB with no WAL/SHM; no recovery or journal modification authorized')
    protected = [card_path, marker_path, protocol, journal, run / 'TRAYECTORIA/EVENTOS.jsonl']
    before = {str(p): sha(p.read_bytes()) for p in protected}
    with sqlite3.connect(journal.as_uri() + '?mode=ro&immutable=1', uri=True) as con:
        con.row_factory = sqlite3.Row
        schemas = {name: [dict(r) for r in con.execute('PRAGMA table_info(' + name + ')')] for name in ('requests', 'meta')}
        first = con.execute("SELECT MIN(seq) FROM requests WHERE id LIKE 'apd04_reserve_%'").fetchone()[0]
        rows = [dict(r) for r in con.execute('SELECT * FROM requests WHERE seq>=? ORDER BY seq', (first,))]
        meta = {r['key']: r['value'] for r in con.execute('SELECT key,value FROM meta')}
    frozen = json.loads((run / 'TRAYECTORIA/ANTES_DE_NATIVE.json').read_bytes())
    plan_member = next(x for x in frozen['sources'] if 'PLAN_RESERVA60' in x['copy'])
    plan_bytes = (run / 'TRAYECTORIA' / plan_member['copy']).read_bytes()
    assert sha(plan_bytes) == plan_member['sha256']
    card = json.loads(card_path.read_bytes())
    wrapper = json.loads((run / 'RESULTADO_SUPERVISION.json').read_bytes())
    export_db = {'schema': 'APD04.reserve.RO_immutable_SQLite.exact_text_rows.N0.R01',
        'connection': 'mode=ro&immutable=1', 'schemas': schemas, 'query': 'seq >= MIN(seq WHERE id LIKE apd04_reserve_%)',
        'requests': rows, 'meta': meta, 'plan': json.loads(plan_bytes), 'VIDA': card,
        'marker': json.loads(marker_path.read_bytes()), 'UI_protocol': json.loads(protocol.read_bytes()), 'wrapper': wrapper,
        'FIN_VENTANA_exists': (run / 'TRAYECTORIA/FIN_VENTANA.json').exists(),
        'driver_RESULTADO_exists': (run / 'TRAYECTORIA/RESULTADO.json').exists()}
    for row in rows:
        payload = json.dumps(json.loads(row['payload']), ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode('utf8')
        assert sha(payload) == row['payload_sha'], row['id']
    out.mkdir(parents=True, exist_ok=False)
    (out / 'CODIGO').mkdir()
    prior = root / 'laboratorio/campanas/APD04_ECOSISTEMA_COGNITIVO/cierre/exportar_reserva_prefijo_completado_n0_r01.py'
    observer_source = ev / 'ACTUADOR_R02_AUX_R01/CORRECCION_Y_DOSSIER_N0_R02/observador_causal_retrospectivo_01.py'
    shutil.copyfile(prior, out / 'CODIGO' / prior.name)
    shutil.copyfile(observer_source, out / 'CODIGO/observador_snapshot.py')
    shutil.copyfile(Path(__file__), out / 'CODIGO' / Path(__file__).name)
    observer = module('frozen_reserve_last_parser', out / 'CODIGO/observador_snapshot.py')
    common = module('frozen_reserve_common', out / 'CODIGO' / prior.name)
    sources = []
    def archive(key, locator, data, destination):
        encoded = gzip.compress(data, compresslevel=9, mtime=0)
        target = out / destination
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open('xb') as stream:
            stream.write(encoded)
        sources.append({'id': key, 'source': locator, 'source_bytes': len(data), 'source_sha256': sha(data),
                        'export': destination, 'exported_bytes': len(encoded), 'export_sha256': sha(encoded)})
    archive('SQLITE_ROWS', str(journal) + '#exact-selected-TEXT-rows', json.dumps(export_db, ensure_ascii=False, separators=(',', ':')).encode('utf8'), 'PRIMARIOS/SQLITE_FILAS_TEXTUALES.json.gz')
    for key, path in [('JOURNAL', run / 'TRAYECTORIA/EVENTOS.jsonl'), ('VIDA', card_path), ('MARKER', marker_path),
        ('UI', protocol), ('WRAPPER', run / 'RESULTADO_SUPERVISION.json'), ('CLASS8', run / 'MUESTRAS_TOTALES_CLASS8.jsonl'),
        ('BEFORE', run / 'ANTES_DEL_PROCESO.json'), ('NATIVE_BEFORE', run / 'TRAYECTORIA/ANTES_DE_NATIVE.json'),
        ('START', run / 'TRAYECTORIA/INICIO_VENTANA.json'), ('STDOUT', run / 'STDOUT.txt'), ('STDERR', run / 'STDERR.txt')]:
        archive(key, path.relative_to(root).as_posix(), path.read_bytes(), 'PRIMARIOS/' + key + '_' + path.name + '.gz')
    for row in frozen['sources']:
        path = run / 'TRAYECTORIA' / row['copy']
        data = path.read_bytes()
        assert sha(data) == row['sha256'] and len(data) == row['bytes']
        archive('CODE_' + row['copy'], path.relative_to(root).as_posix(), data, 'FUENTES_EJECUTADAS/' + path.name + '.gz')
    snapshot_path = system / card['snapshot']
    snapshot = observer.Snapshot(snapshot_path)
    assert snapshot.encoded_sha256 == card['snapshot_sha256'] and snapshot.tick == card['physical']['tick']
    raw_bytes, clock_bytes = observer.pbytes(snapshot.raw), observer.pbytes(snapshot.clocks)
    assert sha(raw_bytes) == card['physical']['RAW_sha256'] and sha(clock_bytes) == card['physical']['clocks_sha256']
    assert all(x == snapshot.tick for x in snapshot.clocks)
    relevant_ids = set()
    for row in rows:
        if row['status'] == 'completed' and row['result']:
            relevant_ids.update(common.receipt_map(json.loads(row['result'])))
    context = {'channels': snapshot.channels, 'pending_native_events': snapshot.pending,
        'metadata': snapshot.metadata, 'metadata_packets_hex': {key: value.hex() for key, value in snapshot.metadata_packets.items()},
        'paused': snapshot.paused, 'phase': snapshot.phase, 'next_event_id': snapshot.next_event_id,
        'next_sequence': snapshot.next_sequence,
        'all_full_receipts_count': len(snapshot.receipts),
        'relevant_receipts': [x for x in snapshot.receipts if str(x['id']) in relevant_ids]}
    archive('LAST_CONTEXT', card['snapshot'] + '#offline-context-extraction-not-a-snapshot',
            json.dumps(context, ensure_ascii=False, separators=(',', ':')).encode('utf8'), 'CONTEXTOS/ULTIMO_CONTEXTO.json.gz')
    (out / 'CAMPOS').mkdir()
    with (out / 'CAMPOS/ULTIMO_RAW_U64_LE.zlib').open('xb') as stream:
        stream.write(zlib.compress(raw_bytes, 9))
    after = {str(p): sha(p.read_bytes()) for p in protected}
    assert before == after, 'Closed data changed during N0 extraction'
    fields = {'N': snapshot.N, 'tick': snapshot.tick, 'RAW_sha256': sha(raw_bytes), 'clocks_sha256': sha(clock_bytes),
        'source_full_snapshot': card['snapshot'], 'source_full_snapshot_sha256': snapshot.encoded_sha256,
        'metrics': common.metrics(snapshot.raw, snapshot.clocks, snapshot.N, snapshot.tick),
        'clocks_lossless_recipe': 'Every uint64 equals tick; verified against every original clock and full SHA before exclusion',
        'FNV_checksum_verified': True, 'not_operational_snapshot': True}
    dump(out / 'INDICE.json', {'schema': 'APD04.reserve.host_guard_closed.export.N0.R01', 'sources': sources,
         'last_fields': fields, 'protected_before': before, 'protected_after': after,
         'full_SQLite_and_snapshots_remain_local': True, 'no_pending_cleared_or_replayed': True, 'new_Native_ticks': 0})
    result = recalc(out)
    dump(out / 'RECALCULO_CIERRE_RESERVA_N0.json', result)
    dump(out / 'PLAN_RECALCULO.json', {'jobs': [{'id': 'RESERVA_GUARD_CLOSED', 'base': '.',
        'script': 'CODIGO/' + Path(__file__).name, 'args': ['recalc', '--evidence', {'input': '.'}, '--out', '{output}'],
        'expected': 'RECALCULO_CIERRE_RESERVA_N0.json', 'comparison': 'bytes'}]})
    members = [{'file': p.relative_to(out).as_posix(), 'bytes': p.stat().st_size, 'sha256': sha(p.read_bytes())}
               for p in sorted(out.rglob('*')) if p.is_file()]
    dump(out / 'MANIFIESTO.json', {'members': members, 'new_Native_ticks': 0})
    print(json.dumps({key: result[key] for key in ('last_committed_tick', 'scheduled_events_with_ID',
        'journal_submission_attempts', 'database_submitted_events', 'database_completed_events', 'not_submitted_events',
        'work_counts', 'unique_native_inputs', 'native_input_statuses', 'pending_transport')}))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    subs = parser.add_subparsers(dest='operation', required=True)
    p = subs.add_parser('export'); p.add_argument('--root', required=True, type=Path); p.add_argument('--out', required=True, type=Path)
    p = subs.add_parser('recalc'); p.add_argument('--evidence', required=True, type=Path); p.add_argument('--out', required=True, type=Path)
    args = parser.parse_args()
    if args.operation == 'export':
        export(args.root.resolve(), args.out.resolve())
    else:
        dump(args.out, recalc(args.evidence.resolve()))
