"""Exact saved-state observer comparison; no engine import or simulation."""
from pathlib import Path
import hashlib
import importlib.util
import json
import sqlite3

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
S = ROOT / 'sistema'


def digest(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()


def load(condition):
    life = 'APD05_GUI_OBS_' + condition + '_R01'
    folder = S / 'estado/servicios_persistentes' / life
    card = json.loads((S / 'estado/vidas' / life / 'VIDA.json').read_text(encoding='utf8'))
    spec = importlib.util.spec_from_file_location('forensic_' + condition, S / 'capacidades/observador_causal_retrospectivo_01.py')
    reader = importlib.util.module_from_spec(spec); spec.loader.exec_module(reader)
    snap = reader.Snapshot(S / card['snapshot'])
    q = sqlite3.connect('file:'+(folder/'cola.sqlite3').as_posix()+'?mode=ro',uri=True)
    q.row_factory = sqlite3.Row
    requests = [dict(r) for r in q.execute("select * from requests where id like 'apd05_obs_%' order by seq")]
    meta = {r[0]:json.loads(r[1]) for r in q.execute("select key,value from meta where key in ('genesis_observer','genesis_frame','owner')")}
    q.close()
    result = {'life_id':life,'snapshot':card['snapshot'],'snapshot_sha256':card['snapshot_sha256'],
        'summary':snap.summary(),'requests':requests,'observer':meta.get('genesis_observer'),
        'last_frame':meta.get('genesis_frame'),'owner':meta.get('owner'),
        'native_state':{'N':snap.N,'tick':snap.tick,'paused':snap.paused,'phase':snap.phase,
            'next_event_id':snap.next_event_id,'next_sequence':snap.next_sequence,
            'channels_sha256':digest(snap.channels),'pending_sha256':digest(snap.pending),
            'receipts_sha256':digest(snap.receipts)},
        'final_world_raw_sha256':hashlib.sha256(reader.pbytes(snap.raw)).hexdigest(),
        'final_world_clocks_sha256':hashlib.sha256(reader.pbytes(snap.clocks)).hexdigest()}
    native_ids = []
    for row in requests:
        data = json.loads(row['result']) if row.get('result') else None
        if data and row['id']=='apd05_obs_query_r01':
            body = data['result']['rows'][0]
            result['formed_native_command'] = body['reader']['formed_native_command']
            native_ids = body['requests']
    result['new_native_receipts'] = native_ids
    metrics = folder / 'RECURSOS_TRABAJADOR_R01.json'
    result['whole_worker_resources'] = json.loads(metrics.read_text(encoding='utf8')) if metrics.is_file() else None
    return result


def main():
    on,off = load('ON'),load('OFF')
    checks = {'same_N_tick':on['native_state']['N']==off['native_state']['N'] and on['native_state']['tick']==off['native_state']['tick'],
        'whole_RAW_equal':on['final_world_raw_sha256']==off['final_world_raw_sha256'],
        'whole_clocks_equal':on['final_world_clocks_sha256']==off['final_world_clocks_sha256'],
        'native_agenda_channels_counters_receipts_equal':on['native_state']==off['native_state'],
        'new_native_requests_exact_equal':on['new_native_receipts']==off['new_native_receipts'],
        'native_query_output_equal':on['formed_native_command']==off['formed_native_command'],
        'five_transport_ids_completed_each':len(on['requests'])==len(off['requests'])==5 and all(r['status']=='completed' for r in on['requests']+off['requests']),
        'observer_ON_captured_OFF_did_not':on['observer']['capture_count']>0 and off['observer']['capture_count']==0}
    result={'schema':'GENESIS.passive_observer.fixed_ticks.N0_comparison.R01','native_ticks_in_recalculation':0,
        'ON':on,'OFF':off,'checks':checks,
        'cost_limit':'ON whole worker CPU/RAM unavailable because post-closure report read was blocked by the audit fence. ON actual capture count/seconds remain in SQLite. OFF whole worker resources are available. No zero-cost claim or invented symmetric CPU comparison.',
        'scope':'Exact physical buffers, agenda and native receipts at fixed Native protocol ticks. Owner PID, imported identity and transport documentary epoch need not be byte-identical. This is not whole future causal identity and not an external wall-time-coupled simulator proof.',
        'ON_instrument_export_failure_preserved':'Read of PLAN_OBSERVADOR_ON_OFF_R01.json after Native protocol close was denied by existing access_guard; data recovered retrospectively from saved state/outbox/SQLite without new ticks.'}
    target=HERE/'RESULTADO_OBSERVADOR_ON_OFF_N0_R01.json'
    if target.exists(): raise FileExistsError('Do not overwrite saved result.')
    target.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8')
    print(json.dumps({'checks':checks,'tick':on['native_state']['tick'],'RAW':on['final_world_raw_sha256'],
        'clocks':on['final_world_clocks_sha256'],'capture_ON':on['observer'],'capture_OFF':off['observer']},ensure_ascii=False))


if __name__ == '__main__': main()
