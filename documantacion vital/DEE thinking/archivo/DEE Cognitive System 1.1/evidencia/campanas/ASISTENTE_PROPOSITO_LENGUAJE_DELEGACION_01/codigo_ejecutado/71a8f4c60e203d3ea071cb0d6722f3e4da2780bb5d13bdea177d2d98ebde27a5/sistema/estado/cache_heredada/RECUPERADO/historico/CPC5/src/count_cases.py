"""Reconcile operational counts from saved primary records, never from ticks as replicas."""
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import ROOT,put


def main():
    index=json.loads((ROOT/'revision/INDICE_EVIDENCIA.json').read_text(encoding='utf-8'))
    rows=[]
    for entry in index['primary_cases']:
        value=json.loads((ROOT/entry['source']).read_text(encoding='utf-8'))
        restored=value.get('schema')=='CPC5.regulation.counterfactual.v1'
        initial=int(value['initial_physics']['tick']) if restored else 0
        final=entry['tick_final']
        edits=value.get('interventions',value.get('diagnostic_edits',[]))
        intact_fork=restored and value.get('modality')=='INTACT_REPLAY_FORK'
        calls=None;call_field=None
        for name in ('calls','inputs','input_calls','actual_input_calls','actual_calls'):
            if isinstance(value.get(name),list):calls=value[name];call_field=name;break
        receipts=value.get('receipts')
        if receipts is None and isinstance(value.get('operative'),dict):receipts=value['operative'].get('receipts')
        if receipts is None and isinstance(value.get('teaching'),dict):
            # SEM01 records cumulative receipt lists at teaching/use boundaries.
            # Deduplicate the native IDs, never count repeated readouts as inputs.
            identified={}
            for segment in [value['teaching'],*value.get('uses',[])]:
                for item in segment.get('actual_receipts',[]):identified[item['id']]=item
                candidate=segment.get('anticipation',{}).get('receipt')
                if candidate:identified[candidate['id']]=candidate
            if identified:receipts=[identified[k] for k in sorted(identified)]
            if calls is None and receipts is not None:
                calls=receipts;call_field='unique native receipt IDs across teaching/uses; not synthetic input payloads'
        # Receipt IDs in a restored fork are inherited, not new host calls.
        new_receipts=[] if restored else receipts
        probe_count=None if new_receipts is None else sum('probe' in str(r.get('kind','')).lower() for r in new_receipts)
        reference_replay=(entry['category']=='DIRECTED_PRIOR_REPRODUCTION_OR_DIAGNOSTIC' and not edits)
        rows.append({'case_id':entry['case_id'],'category':entry['category'],'primary_source':entry['source'],
                     'fresh_Runtime_preparation':not restored,'restored_checkpoint_continuation':restored,
                     'start_tick':initial,'final_tick':final,
                     'native_ticks_on_this_recorded_path':None if final is None else final-initial,
                     'diagnostic_fork_calls':len(edits),'intact_replay_fork_calls':int(intact_fork),
                     'directed_historical_reproduction':reference_replay,
                     'input_call_field':call_field,'logged_new_input_requests':None if calls is None else len(calls),
                     'new_API_probe_receipts':probe_count,
                     'receipt_status_counts':None if new_receipts is None else {status:sum(r.get('status')==status for r in new_receipts) for status in sorted({r.get('status') for r in new_receipts})},
                     'receipt_counter_scope':'Native API kind only; intended scientific queries can also be sent through submit and retain that different modality',
                     'new_input_request_count_missing':calls is None})
    metrics={'schema':'CPC5.review.operational_counts.v1','primary_records':len(rows),
             'fresh_Runtime_preparations':sum(x['fresh_Runtime_preparation'] for x in rows),
             'restored_checkpoint_continuations':sum(x['restored_checkpoint_continuation'] for x in rows),
             'diagnostic_fork_calls':sum(x['diagnostic_fork_calls'] for x in rows),
             'intact_replay_fork_calls':sum(x['intact_replay_fork_calls'] for x in rows),
             'directed_historical_reproductions':sum(x['directed_historical_reproduction'] for x in rows),
             'native_ticks_on_recorded_primary_paths':sum(x['native_ticks_on_this_recorded_path'] or 0 for x in rows),
             'known_new_input_requests':sum(x['logged_new_input_requests'] or 0 for x in rows),
             'input_request_count_coverage':sum(x['logged_new_input_requests'] is not None for x in rows),
             'known_new_API_probe_receipts':sum(x['new_API_probe_receipts'] or 0 for x in rows),
             'probe_receipt_count_coverage':sum(x['new_API_probe_receipts'] is not None for x in rows),
             'scope':['Fresh preparations can have identical deterministic histories; they are not automatically statistical replicas.',
                      'Forks created inside a fresh run are counted both as that preparation and as fork operations, not additional independent samples.',
                      'Recorded path ticks count work on that path, including re-executed control prefixes; they are not an effective sample size.',
                      'Independent technical replays, demonstrations, aborted attempts and clean extraction runs are excluded from these primary counts and retain their own job/result records.',
                      'Missing counts remain null; known totals are not claimed as complete when coverage is partial.'],
             'cases':rows}
    put(ROOT/'revision/CONTEOS_RECONCILIADOS.json',metrics)
    print(json.dumps({k:v for k,v in metrics.items() if k not in ('cases','scope')},ensure_ascii=False))


if __name__=='__main__':main()
