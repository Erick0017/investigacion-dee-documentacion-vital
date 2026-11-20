"""Auditor-only aggregation. No values are fed back into a Runtime."""
import argparse,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from src.common import put,sha

def main():
    config=json.loads((ROOT/'configuraciones/EXPERIMENT_CONFIG.json').read_text(encoding='utf-8'));rows=[]
    for case in config['cases']:
        path=ROOT/'resultados/confirmacion'/case['id']/'MEASUREMENTS.json'
        if not path.exists():rows.append({'id':case['id'],'status':'MISSING'});continue
        x=json.loads(path.read_text(encoding='utf-8'));uses=x['uses'];receipts=x['teaching']['actual_receipts']+[r for u in uses for r in u['actual_receipts']]+[u['anticipation']['receipt'] for u in uses]
        statuses={}
        for receipt in receipts:statuses[receipt['status']]=statuses.get(receipt['status'],0)+1
        row={'id':case['id'],'type':case['type'],'mode':case.get('mode','paired'),'prediction_slots':len(uses),'resolved':sum(u['anticipation']['emission']['available'] for u in uses),
          'correct':sum(u['prediction_correct'] is True for u in uses),'incorrect':sum(u['prediction_correct'] is False for u in uses),'unresolved':sum(u['prediction_correct'] is None for u in uses),
          'signals':[u['signal'] for u in uses],'emission_ticks':[u['anticipation']['emission_tick'] for u in uses],
          'native_classes':[u['anticipation']['emission']['anticipated_class'] for u in uses],
          'native_directions':[u['anticipation']['emission']['physical']['direction'] for u in uses],
          'emission_loads':[u['anticipation']['emission']['physical']['s_reg'] for u in uses],
          'future_events':[u['generator_later_event'] for u in uses],
          'physical_function_resource_profiles':[u['evaluation']['profile'] for u in uses],
          'external_utility_total':sum(u['evaluation']['external_utility_for_this_task'] for u in uses),'actual_receipt_status_counts':statuses,
          'observed_teacher_classes':[e['present_sensor']['observed_class'] for e in x['teaching']['experiences']],
          'initial':x['initial'],'final':x['final'],'elapsed_seconds':x['elapsed_seconds'],'measurements':path.relative_to(ROOT).as_posix(),'sha256':sha(path),'status':'MEASURED'}
        rows.append(row)
    index={x['id']:x for x in rows}
    paired=[index[x] for x in ('A_future_UV','B_future_VU')]
    reserves=[x for x in rows if x['type']=='RESERVED_PHYSICAL_VARIANT']
    summary={'schema':1,'instrument':'DEE thinking4.0.0','frozen_config_sha256':sha(ROOT/'configuraciones/EXPERIMENT_CONFIG.json'),
      'case_records':len(rows),'case_records_are_not_independent_population_samples':True,'rows':rows,
      'shared_initial_raw_clock_across_histories':index['A_future_UV']['initial']==index['B_future_VU']['initial'],
      'shared_signal_and_decoder_across_histories':True,'paired_main':{'resolved':sum(x['resolved'] for x in paired),'correct':sum(x['correct'] for x in paired),'slots':sum(x['prediction_slots'] for x in paired),'utilities':[x['external_utility_total'] for x in paired]},
      'reserved':{'cases':len(reserves),'resolved':sum(x['resolved'] for x in reserves),'correct':sum(x['correct'] for x in reserves),'slots':sum(x['prediction_slots'] for x in reserves),'utilities':[x['external_utility_total'] for x in reserves]},
      'interpretive_scope':'Native acquired directional consequence class selects a prepared physical action route; the utility assignment of that route is not independently learned',
      'external_sensor':'Current function receiver is transduced by a fixed external presence/direction/payload classifier; U/V teaching generators do not inject a corrected learned relation',
      'original_records_retained':True}
    put(ROOT/'resultados/CONFIRMATORY_SUMMARY.json',summary)
    for row in rows:print(row['id'],row.get('native_classes'),row.get('physical_function_resource_profiles'),row.get('external_utility_total'),row.get('actual_receipt_status_counts'))
if __name__=='__main__':main()
