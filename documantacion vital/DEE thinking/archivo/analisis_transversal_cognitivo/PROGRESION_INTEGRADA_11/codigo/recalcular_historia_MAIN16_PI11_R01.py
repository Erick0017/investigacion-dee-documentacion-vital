"""Passive history/use localizers from sixteen CLOSED PI11 witnesses.

Documents all Q1 changes and all adjacent changed choices, not only successful
examples. A local history gate does not establish exclusive real contingency.
"""
from pathlib import Path
import argparse,hashlib,json
def need(ok,why):
    if not ok:raise ValueError(why)
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def analyze(root):
    root=Path(root).resolve(strict=True);closure=read(root/'CIERRE_DOCUMENTAL.json');need(closure.get('closed_for_documentary_read')is True,'Closed witness export declaration required')
    rows=[]
    for n in range(16):
        file=root/('episodio_%04d.json'%n);v=read(file);one=v['first_stage'];raw=one['register']['actual_observation'];resource=v['resource']
        rows.append({'ordinal':n,'life_id':v['life_id'],'before_tick':v['before_tick'],'after_tick':v['after_tick'],
            'query_tick':one['reader']['tick'],'query_phase782':one['reader']['tick']%782,'sample_STATE':raw['state'],'sample_direction':raw['direction'],
            'mode':v['offer']['environment']['mode'],'q1_choice':one['reader']['choice'],'q2_choice':v['second_stage']['reader']['choice'],
            'q1_before':v['Q1_references_before']['A_minus_B'],'q1_after':v['references_after']['q1']['A_minus_B'],
            'returned_failed':v['returned_failed'],'actual_failed':v['actual_failed'],'useful':resource['attributed_useful'],
            'fresh_FI':v['second_stage']['refresh_FI'],'certificate_valid':resource['certificate_valid'],
            'witness':file.name,'witness_sha256':sha(file)})
    need(len({r['life_id']for r in rows})==1,'One continuous history only')
    pairs=[]
    for a,b in zip(rows,rows[1:]):
        if a['q1_choice']==b['q1_choice']:continue
        pair={'previous_ordinal':a['ordinal'],'later_ordinal':b['ordinal'],
              'same_Native_STATE':a['sample_STATE']==b['sample_STATE'],'same_preview_direction':a['sample_direction']==b['sample_direction'],
              'same_query_phase782':a['query_phase782']==b['query_phase782'],'same_environment_mode':a['mode']==b['mode'],
              'previous_Q1_reference_changed':a['q1_before']!=a['q1_after'],'reference_carried_forward':a['q1_after']==b['q1_before'],
              'previous_choice':a['q1_choice'],'later_choice':b['q1_choice'],'later_useful':b['useful']}
        pair['strict_local_history_and_use_witness']=all(pair[k]for k in('same_Native_STATE','same_preview_direction','same_query_phase782','same_environment_mode','previous_Q1_reference_changed','reference_carried_forward','later_useful'))
        pairs.append(pair)
    return {'schema':'DEE.PI11.closed_MAIN16_history_localizers.R01','Native_executed':False,'new_Native_ticks':0,
            'life_id':rows[0]['life_id'],'opportunities':16,'all_rows':rows,'all_adjacent_changed_choice_pairs':pairs,
            'all_Q1_reference_changes':[r for r in rows if r['q1_before']!=r['q1_after']],
            'reference_changes_after_nonfailure_also_preserved':[r for r in rows if r['q1_before']!=r['q1_after']and not r['returned_failed']],
            'history_local_use_gate_observed':any(p['strict_local_history_and_use_witness']for p in pairs),
            'limitations':['Native STATE/preview/fixed phase and codec are comparable, not the entire global landscape.',
                'This is documentary analysis of one history. Contingency specificity requires actual controls; no real>yoked claim is made.',
                'Prepared environmental certificate and fixed Q2 continuation map are not Native learned memory or a discovered plan.',
                'All original changes after nonfailure are retained; the bank is not explained as a host-written negative-value table.']}
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',required=True);p.add_argument('--salida',type=Path,required=True);a=p.parse_args();need(not a.salida.exists(),'Never overwrite an analysis');v=analyze(a.root)
    with a.salida.open('x',encoding='utf8')as f:json.dump(v,f,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps({'history_local_use_gate_observed':v['history_local_use_gate_observed'],'all_Q1_reference_changes':len(v['all_Q1_reference_changes']),'strict_local_pairs':[p for p in v['all_adjacent_changed_choice_pairs']if p['strict_local_history_and_use_witness']],'Native_executed':False}))
