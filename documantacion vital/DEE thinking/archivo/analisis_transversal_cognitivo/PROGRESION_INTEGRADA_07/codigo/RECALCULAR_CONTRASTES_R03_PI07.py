"""Passive R03 comparisons and explicitly noncausal action references."""
from pathlib import Path
from collections import Counter
import argparse, hashlib, importlib.util, json
P = Path(__file__).resolve().parents[1]

def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--salida',type=Path,required=True);args=ap.parse_args()
    if args.salida.exists(): raise FileExistsError(args.salida)
    spec=importlib.util.spec_from_file_location('PI07_documentary_decoder',P/'codigo/RECALCULAR_PRIMARIOS_PI07.py')
    dec=importlib.util.module_from_spec(spec);spec.loader.exec_module(dec)
    sets={'real':['PI07_ADQUISICION4_R03.json','PI07_RESERVA_A_R03.json','PI07_CAMBIO_RES_B_R03.json'],
          'constant_nonfailure':['PI07_NOFAIL12_R03.json'],'yoked':['PI07_YOKED12_R03.json'],
          'restoration':['PI07_RESTAURACION_12_13_R03.json'],
          'after_reopen':['PI07_POST_REAPERTURA_14_15_R03.json'],
          'sensor_cut':['PI07_CORTE_SENSOR_04_05_R03.json'],
          'actuator_cut':['PI07_CORTE_ACTUADOR_04_05_R03.json']}
    arms={};proofs={};missing=[];global_captures=[]
    for label,names in sets.items():
        if any(not(P/'control'/name).exists()for name in names):missing.append(label);continue
        result=[];sources=[]
        for name in names:
            path=P/'control'/name;proof=read(path)
            if not(proof['closed']and proof['status']=='CLOSED'and proof['full_plan_completed']):
                raise ValueError('Known complete closed cases required, not a favorable partial: '+name)
            sources.append({'file':name,'sha256':sha(path),'initial_tick':proof['initial_tick'],
                            'final_tick':proof['final_tick'],'Native_ticks':proof['new_ticks']})
            for item in proof['outcomes']:
                path=P/'ensayos'/Path(item['primary']).name
                if sha(path)!=item['primary_sha256']:raise ValueError('Published primary SHA differs')
                _,rows=dec.decoded_result(read(path))
                for r in rows:
                    if 'FI'not in r:continue
                    if r['version']!='DEE.PI07.acquired_regulation.perpendicular_environment.R03':
                        raise ValueError('This comparison is only the predeclared R03 environment')
                    early=dec.early_choice(r['FI']['legacy_result']['early_observation'])
                    late=dec.late_FI_choice(r['FI']['legacy_result']['original_result']['native_trial']['reader'])
                    choice=dec.early_choice(r['reader']['observation'])
                    if early!=r['FI']['early_physical_choice']or late!=r['FI']['old_q6_choice']or choice!=r['reader']['choice']:
                        raise ValueError('Physical RAW decoder disagrees')
                    msg=r['message'];obs=dec.observation(msg['observation']);required=msg['required_payload']
                    delivered=(required is not None and dec.request_status(msg['request'])=='applied'
                               and obs['state']>0 and obs['semantic']==1 and obs['direction']==[1,0,0]
                               and obs['s_reg']==required)
                    failed=late!=1 or(required is not None and not delivered)
                    if failed is not r['actual_failed']or delivered is not msg['delivered_exact']:
                        raise ValueError('Actual utility differs from the frozen physical outcome')
                    direct,aliases=dec.receipts(r['requests']);counts=Counter(z['status']for z in direct.values())
                    if any(k!='applied'and not k.startswith('rejected')for k in counts):raise ValueError('Unknown/pending Native receipt')
                    before=r['reference_before'];after=r['return_frames'][-1]
                    for z in before:dec.observation(z)
                    for frame in r['return_frames']:
                        for key in('A','B','hub'):dec.observation(frame[key])
                    record={'ordinal':r['ordinal'],'stage':r['environment_spec']['stage'],
                            'actual_sensor_state':r['sensor']['actual_state_datum'],
                            'submitted_sensor_state':r['sensor']['submitted_state_datum'],
                            'Native_choice':choice,'canonical_motor':r['actual_motor'],
                            'pulse_scheduled':r['pulse_scheduled'],'pulse_applied':r['pulse_applied'],
                            'FI_q4':early,'FI_q6':late,'message_required':required is not None,
                            'message_payload':required,'message_delivered':delivered,'actual_failed':failed,
                            'returned_failed':r['returned_failed'],'calendar':r['calendar'],'FI_calendar':r['FI']['calendar'],
                            'delta_before':before[0]['s_reg']-before[1]['s_reg'],
                            'delta_after':after['A']['s_reg']-after['B']['s_reg'],
                            'unique_requested':len(direct),'status_counts':dict(counts),
                            'aliases_not_new_events':aliases,'source_primary':path.name,'primary_sha256':sha(path)}
                    result.append(record)
                    cap=r.get('external_global_capture')
                    if cap:global_captures.append({'arm':label,'ordinal':r['ordinal'],'primary':path.name,**cap,
                                                  'scope':'Only capture metadata/index hash read here; no global buffers reconstructed by this script.'})
        result.sort(key=lambda z:z['ordinal']);proofs[label]=sources
        arms[label]={'rows':result,'opportunities':len(result),
                     'FI_correct':sum(z['FI_q6']==1 for z in result),
                     'complete':sum(not z['actual_failed']for z in result),
                     'messages_offered':sum(z['message_required']for z in result),
                     'messages_delivered':sum(z['message_delivered']for z in result if z['message_required']),
                     'pulse_scheduled':sum(z['pulse_scheduled']for z in result),
                     'pulse_applied':sum(z['pulse_applied']for z in result),
                     'unique_requested':sum(z['unique_requested']for z in result),
                     'applied':sum(z['status_counts'].get('applied',0)for z in result),
                     'rejected':sum(n for z in result for status,n in z['status_counts'].items()if status.startswith('rejected')),
                     'Native_ticks':sum(v['Native_ticks']for v in sources)}
    real=arms['real']['rows'];checks=[]
    if [r['ordinal']for r in real]!=list(range(12)):raise ValueError('Exact real source12 required')
    for label in('constant_nonfailure','yoked'):
        other=arms[label]['rows']
        if [r['ordinal']for r in other]!=list(range(12)):raise ValueError('Exact matched control12 required')
        checks.append({'arm':label,'check':'same12TC_and_FI_calendars','passed':all(a['calendar']==b['calendar']and a['FI_calendar']==b['FI_calendar']for a,b in zip(real,other))})
        checks.append({'arm':label,'check':'same12actual_sensor_states','passed':all(a['actual_sensor_state']==b['actual_sensor_state']for a,b in zip(real,other))})
    yoke=arms['yoked']['rows'];expected=[real[(i+5)%12]['actual_failed']for i in range(12)]
    checks.append({'arm':'yoked','check':'fixed_source_plus5_and_same_boolean_dose',
                   'passed':[r['returned_failed']for r in yoke]==expected and Counter(expected)==Counter(r['actual_failed']for r in real)})
    mismatch=[{'ordinal':r['ordinal'],'actual_failed':r['actual_failed'],'returned_failed':r['returned_failed']}
              for r in yoke if r['actual_failed']!=r['returned_failed']]
    for label in('sensor_cut','actuator_cut'):
        if label in arms:
            for row in arms[label]['rows']:
                same=real[row['ordinal']]
                checks.append({'arm':label,'ordinal':row['ordinal'],'check':'same_age_query_FI_calendar',
                               'passed':row['calendar']==same['calendar']and row['FI_calendar']==same['FI_calendar']})
    # Descriptive action-trace references added after the data at Root's
    # request. They have no simulated/counterfactual environmental utility.
    observed=[r['canonical_motor']for r in real]
    refs={'always_pulse':[1]*12,'never_pulse':[-1]*12,
          'fixed_current_information_rule':[1 if r['actual_sensor_state']==1 else -1 for r in real]}
    for initial in(-1,1):
        action=initial;pred=[]
        for r in real:
            pred.append(action)
            if r['actual_failed']:action=-action
        refs['global_stay_success_switch_failure_initial_'+str(initial)]=pred
    policy={0:-1,1:1};pred=[]
    for r in real:
        state=r['actual_sensor_state'];policy.setdefault(state,-1);pred.append(policy[state])
        if r['actual_failed']:policy[state]=-policy[state]
    refs['contextual_stay_switch_declared_initial_policy']=pred
    reference_report={key:{'predicted_actions':values,'agreement_with_recorded_real_actions':sum(a==b for a,b in zip(values,observed)),
                           'opportunities':12,'counterfactual_FI_products_messages':None}
                      for key,values in refs.items()}
    output={'schema':'DEE.PI07.R03.matched_control_and_retention.passive.v1','new_Native_ticks':0,
            'source_proofs':proofs,'arms':arms,'checks':checks,'all_comparability_checks_passed':all(v['passed']for v in checks),
            'yoked_actual_return_mismatches':mismatch,'global_capture_descriptors_only':global_captures,
            'action_trace_references':reference_report,
            'reference_scope':'Descriptive post-hoc action agreement on the same recorded physical information and actual real feedback. Reference actions were not materially executed: no counterfactual FI accuracy, message count, product count or performance superiority is invented. The contextual two-entry stay/switch reference can explain this short action trace; this is not evidence of a general strategy beyond it.',
            'causal_scope':'Three paired branches share a complete acquired prefix. Initial protection reuses R02policy and a prepared P0tool; true new outcome at8changes later Native selection at10. Their admitted doses differ as actual consequences of selection and conflicts. Link cuts intentionally change physical information or omit an actuator input, not a perfect isodose semantic sham.',
            'missing_cases_not_executed_or_not_closed':missing,
            'legacy_conservation':'The old API panel5/6failed and remains failed. No adoption is authorized by this positive local functional contrast; new access/conservation has its own versioned protocol.'}
    args.salida.write_text(json.dumps(output,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'output':str(args.salida),'sha256':sha(args.salida),'comparability':output['all_comparability_checks_passed'],
                      'arms':{k:{z:v[z]for z in('opportunities','FI_correct','complete','messages_offered','messages_delivered','unique_requested','applied','rejected')}for k,v in arms.items()},
                      'reference_action_agreement':{k:v['agreement_with_recorded_real_actions']for k,v in reference_report.items()},
                      'missing':missing},ensure_ascii=False))

if __name__=='__main__':main()
