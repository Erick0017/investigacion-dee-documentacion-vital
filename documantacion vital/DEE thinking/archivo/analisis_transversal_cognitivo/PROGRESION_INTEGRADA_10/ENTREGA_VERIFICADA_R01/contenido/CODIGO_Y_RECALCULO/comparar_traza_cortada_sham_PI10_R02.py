"""Paired formed-trace contrast on the actual shared REAL2[0..3] prefix.

No Native execution or automatic credit. Checks archived RAW references,
first already-formed choice, own material receipts and subsequent resources.
Different global hashes after adding different SEM4 positions are expected.
"""
from pathlib import Path
import argparse,hashlib,importlib.util,json
H=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('primary',H/'recalcular_primarios_PI10_R03.py');a=importlib.util.module_from_spec(s);s.loader.exec_module(a)
t=importlib.util.spec_from_file_location('contact',H/'recalcular_contactos_TC_PI10_R02.py');c=importlib.util.module_from_spec(t);t.loader.exec_module(c)

def compare(index):
    value=a.read(index);root=index.parent;p=a.read(a.safe_file(root,value['protocol']['file']));groups={};raw={}
    for entry in value['episodes']:
        b=a.safe_file(root,entry['witness']['file']).read_bytes();a.need(a.sha(b)==entry['witness']['sha256'],'Exact immutable control witness')
        v=json.loads(b)
        if not v['operator_calibration']and v['trace_control']in('cut','sham'):
            role=v['trace_control'];r=a.project_episode(v,p);r['contact']=c.contacts(v,p);groups.setdefault(role,[]).append(r);raw[(role,r['ordinal'])]=v
    a.need(set(groups)=={'cut','sham'},'Both actually executed formed-trace controls')
    for role,rows in groups.items():
        rows.sort(key=lambda r:r['ordinal']);a.need([r['ordinal']for r in rows]==[4,5,6]and len({r['life_id']for r in rows})==1,'The whole prospectively fixed three-case continuation, not picked successful episodes')
    pairs=[]
    for cut,sham in zip(groups['cut'],groups['sham']):
        a.need(cut['ordinal']==sham['ordinal'],'Same actual opportunity ordinal')
        pairs.append({'ordinal':cut['ordinal'],'same_actual_STATE_bit':(cut['q1_STATE'],cut['actual_preview_bit'])==(sham['q1_STATE'],sham['actual_preview_bit']),
          'same_q1_q2_ticks':cut['query1_tick']==sham['query1_tick']and cut['query2_tick']==sham['query2_tick'],
          'q1_choices':[cut['q1_Native_choice'],sham['q1_Native_choice']],'q1_before':[cut['q1_before'],sham['q1_before']],
          'q1_after':[cut['q1_after'],sham['q1_after']],'physical_products':[cut['physical_delivered'],sham['physical_delivered']],
          'attributed_products':[cut['attributed_useful'],sham['attributed_useful']],
          'contact_deltas':[cut['contact']['change_during_recorded_return_window'],sham['contact']['change_during_recorded_return_window']]})
    first_c=groups['cut'][0];first_s=groups['sham'][0];first_same=first_c['q1_Native_choice']==first_s['q1_Native_choice']and first_c['q1_before']==first_s['q1_before']
    admission={}
    for role in('cut','sham'):
        v=raw[(role,4)];names={p['query_prefix']+'.'+role+'.'+str(n)for n in range(2)}
        requests=[r for r in v['requests']if r.get('requested_tick')==v['calendar']['first']['seed_tick']+2 and r.get('channel')in names and r.get('control_kind')==role and r.get('not_selected_by_actual_choice')is True]
        ids={r['id']:r for r in requests};admission[role]={'detected_barrier_requests':list(ids.values()),
          'barrier_installed_reported':v['barrier_installed'],'barrier_attempt_ordinal':v['barrier_attempt_ordinal'],
          'exact_all_two_applied':len(ids)==2 and all(r['receipt']['status']=='applied'for r in ids.values())}
    stable=all(r['FI_choice_old_q6']==1 and r['q2_before']==-1 and r['q2_after']==-1 for rows in groups.values()for r in rows)
    summaries={role:{'life_id':rows[0]['life_id'],'opportunities':3,'physical':sum(r['physical_delivered']for r in rows),
      'attributed':sum(r['attributed_useful']for r in rows),'q1_reference_changes':[r['q1_after']-r['q1_before']for r in rows],
      'q1_choices':[r['q1_Native_choice']for r in rows]}for role,rows in groups.items()}
    return {'schema':'DEE.PI10.formed_trace_cut_sham_comparison.R02','Native_executed':False,'DEE_imported':False,
      'source_index_sha256':a.sha(index.read_bytes()),'summaries':summaries,'pairs':pairs,'barrier_admission':admission,
      'formed_choice_same_before_first_barrier':first_same,'all_q2_and_FI_stable':stable,
      'selective_credit_interpretation_conditions':{'paired_first_choice':first_same,'matched_actual_samples_and_clocks':all(r['same_actual_STATE_bit']and r['same_q1_q2_ticks']for r in pairs),
        'actual_two_barriers_each_admitted':all(x['exact_all_two_applied']for x in admission.values()),'q2_FI_stability':stable},
      'qualification':'New cut/sham episodes4..6 only; copied earlier REAL2 experiences are shared history, not new independent trials. RAW preflight/sham-ray coverage is a separate bounded proof, not universal isolation. Observed carrier loads/directions are not unique particle lineage. This contrast does not establish truth-sensitive feedback, general agency or promotion.'}

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--indice',type=Path,required=True);p.add_argument('--salida',type=Path,required=True);args=p.parse_args();a.need(not args.salida.exists(),'No overwrite of an earlier causal conclusion')
    out=compare(args.indice)
    with args.salida.open('x',encoding='utf8')as f:json.dump(out,f,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps({'file':str(args.salida),'sha256':a.sha(args.salida.read_bytes()),'Native_executed':False}))
if __name__=='__main__':main()
