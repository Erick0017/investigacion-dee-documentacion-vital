"""Read-only saved-state/queue reconciliation witness; never loads a Runtime."""
from pathlib import Path
import hashlib
import importlib.util
import json
import sqlite3

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
S = ROOT / 'sistema'
LIFE = 'APD05_GUI_WALK_R01'


def main():
    spec = importlib.util.spec_from_file_location('snapshot_forensic', S / 'capacidades/observador_causal_retrospectivo_01.py')
    observer = importlib.util.module_from_spec(spec); spec.loader.exec_module(observer)
    card_path = S / 'estado/vidas' / LIFE / 'VIDA.json'
    card = json.loads(card_path.read_text(encoding='utf8'))
    native = observer.Snapshot(S / card['snapshot'])
    journal_path = card_path.with_name('HISTORIA.jsonl')
    journal = [json.loads(s) for s in journal_path.read_text(encoding='utf8').splitlines() if s]
    key = 'DEE.Cognitive.System.1.1.PERSISTENT_SERVICE.v1'
    protocol = json.loads(native.metadata[key])
    qpath = S / 'estado/servicios_persistentes' / LIFE / 'cola.sqlite3'
    con = sqlite3.connect('file:' + qpath.as_posix() + '?mode=ro', uri=True)
    con.row_factory = sqlite3.Row
    outstanding = [dict(r) for r in con.execute("select * from requests where status in ('queued','processing','uncertain') order by seq")]
    con.close()
    receipt = protocol.get('last_completed_receipt')
    outbox = qpath.parent / 'resultados' / (receipt['id'] + '.json') if receipt else None
    raw_sha = hashlib.sha256(observer.pbytes(native.raw)).hexdigest()
    clock_sha = hashlib.sha256(observer.pbytes(native.clocks)).hexdigest()
    pending_native = [json.loads(v) for k,v in native.metadata.items() if k.startswith(key + '.queue.') and not json.loads(v).get('empty')]
    checks = {
        'no_interrupted_future_marker': not card_path.with_name('FUTURO_INTERRUMPIDO.json').exists(),
        'snapshot_bytes_match_card': native.encoded_sha256 == card['snapshot_sha256'],
        'last_journal_matches_card': journal[-1]['snapshot_sha256'] == card['snapshot_sha256'],
        'native_protocol_tick_matches': protocol['native_tick_at_checkpoint'] == native.tick,
        'N_tick_RAW_clocks_match': native.N == card['physical']['N'] and native.tick == card['physical']['tick'] and raw_sha == card['physical']['RAW_sha256'] and clock_sha == card['physical']['clocks_sha256'],
        'last_receipt_outbox_exact': outbox.is_file() and hashlib.sha256(outbox.read_bytes()).hexdigest() == receipt['result_sha256'] if receipt else None,
        'no_processing_row_requiring_missing_receipt': not any(r['status'] in ('processing', 'uncertain') for r in outstanding) if receipt is None else True,
        'queue_payloads_exact': all(hashlib.sha256(r['payload'].encode()).hexdigest() == r['payload_sha'] for r in outstanding),
        'same_material_id_still_queued': any(r['id'] == 'apd05_gui_walk_pending_r01' and r['status'] == 'queued' for r in outstanding),
        'no_processing_or_uncertain': all(r['status'] == 'queued' for r in outstanding)
    }
    result = {'schema':'GENESIS.saved_cut_after_host_failure.N0.R01', 'native_ticks':0,
        'life_id':LIFE, 'snapshot_summary':native.summary(), 'record':card, 'protocol':protocol,
        'journal_last_two':journal[-2:], 'native_pending_slots':pending_native,
        'external_outstanding_queue':outstanding, 'checks':checks,
        'scope':'Whole raw/clocks, metadata, queue and any available receipt verified from saved bytes. No recovery or Native continuation claimed by this N0 calculation. The reopened idle epoch saved last_completed_receipt=null; no processing row needs it. Post-exit controls remain legitimate external queued inputs and are not deleted.'}
    output = HERE / 'VERIFICACION_CORTE_GUI_R02_N0_R01.json'
    if output.exists(): raise FileExistsError('Preserve prior result.')
    output.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8')
    print(json.dumps({'checks':checks,'tick':native.tick,'snapshot_sha256':card['snapshot_sha256'],'outstanding_ids':[r['id'] for r in outstanding]},ensure_ascii=False))


if __name__ == '__main__': main()
