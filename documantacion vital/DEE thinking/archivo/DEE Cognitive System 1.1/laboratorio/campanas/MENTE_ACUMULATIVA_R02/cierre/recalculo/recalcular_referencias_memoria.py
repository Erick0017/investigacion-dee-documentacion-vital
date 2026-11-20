"""Offline interpretive references, never used by MA02 actor or environment.

One selected genealogy only: R03B_MAIN→R04_MAIN→MAIN→MAIN_5. Both references
receive current explicit context and earlier explicit teacher signs, not future
answers. Per-context last sign is a small external associative-memory model;
global last sign discards the context. This is not a resource-matched contest.
"""
import argparse
import importlib.util
import json
from pathlib import Path
spec=importlib.util.spec_from_file_location('common_archived',Path(__file__).with_name('recalcular_entrada_comun.py'))
c=importlib.util.module_from_spec(spec);spec.loader.exec_module(c)
T=['alfa','beta','gamma','delta','epsilon'];V=[(1,0,0),(0,1,0),(1,1,0),(-1,1,0),(1,-1,0)]
def site(v,k,z=0):return tuple((33+k*v[j]+(z if j==2 else 0))%67 for j in range(3))

def calculate(root,include_final05=False):
    a=c.Audit(root);events=[];compound=[];receipt_by_id={};worker_events=[]
    def capture(records,source):
        for q in records:
            r=q['receipt'];v={'id':q['id'],'channel':q.get('name',q.get('channel')),'site':q['site'],
                'direction':q['direction'],'value':q['value'],'tick':q['tick'],'status':r['status'],'effective_tick':r['effective_tick']}
            if q['id']in receipt_by_id and receipt_by_id[q['id']]!=v:a.issues.append({'source':source,'id':q['id'],'issue':'selected genealogy reuses receipt id with different data'})
            receipt_by_id[q['id']]=v
    for filename in('entrada_comun/MA02_RESTAURACION_R03B_MAIN.R02.json.gz','entrada_comun/MA02_R04_MAIN.R04.json.gz'):
        x=a.load(filename)
        capture(x['receipts'],filename)
        for row in x['rows']:
            if row['kind'] in('teach','revision'):
                i=row.get('i',row.get('bank'));sign=row.get('sign',row.get('new_signal'))
                events.append({'kind':'teacher','source':filename,'tick':row['tick'],'context':T[i],'explicit_teacher_sign':sign,'physical_hub_raw':row['hub']['raw']})
            else:
                panels=row['fixed_panel'];vectors=V[:4]
                answer=c.decode(panels,[site(v,4,s)for v in vectors for s in(-1,1)],{site(v,4,s):s for v in vectors for s in(-1,1)})
                events.append({'kind':'query','source':filename,'tick':row['read_tick'],'context':T[row['request_token']],'native_sign':answer['decoded_sign']})
    names=['04_PANEL_HEREDADO_MAIN','07_JOBS_MAIN','10_POSTJOBS_ANTERIORES_MAIN','12_CONTINUAR_OTRO_PROCESO_MAIN',
           '16_COMPOSICION_TRABAJO_MAIN','19_PRIMER_USO_TRAS_COMPOSICION_MAIN','20_READQUIRIR_EXPLICITO_MAIN',
           '21_PRIMER_USO_TRAS_READQUIRIR_MAIN','23_REABRIR_COMPUESTA_MAIN','28_ADQUIRIR_EPSILON_MAIN_5',
           '31_PANEL_MAIN_5','35_REABRIR_MAIN_5','37_TRANSFERIR_EPSILON_TRABAJO_MAIN_5','39_USO_5_TRAS_TRABAJO',
           '41_RESERVA_ORDEN_NUEVO','43_USO_REPETIDO_64','45_REABRIR_CORTE_5']
    if include_final05:names.extend(['46_PREPARAR_PENDIENTE_MAIN5','50_VERIFICAR_TRAS_CARGA_MAIN5','51_PANEL_FINAL_CINCO_MAIN5'])
    for name in names:
        filename=name+'.json.gz';x=a.load(filename)
        for row in x['result']['result']['rows']:
            capture(row['requests'],filename)
            if row.get('external'):
                capture(row['external']['return_requests'],filename)
                w=row['external'].get('worker_receipt')
                if w:worker_events.append({'source':filename,'native_tick':w['native_tick'],'worker':w['worker'],'accepted':w['accepted'],'transaction_completed':w['transaction_completed']})
            if row['kind'].startswith('explicit_'):
                teacher=[q for q in row['requests']if q['channel'].startswith('experience.')]
                admitted=any(q['receipt']['status']=='applied'for q in teacher)
                events.append({'kind':'teacher','source':filename,'tick':row['end_tick'],'context':row['context_signal'],
                    'explicit_teacher_sign':row['teaching_signal'],'teacher_admitted':admitted,'physical_hub_raw':row['hub']['raw']})
            elif row['kind']=='joint':
                compound.append({'source':filename,'tick':row['read_tick'],'recorded_native_sign':row['reader']['formed_native_command'],
                    'model_scored':False,'reason':'Not an addressed single-content query; compound consumption is not simulated by these external memory references.'})
            else:
                vectors=V[:5 if int(name[:2])>=31 else 4];panels=row['reader']['panel']
                answer=c.decode(panels,[site(v,4,s)for v in vectors for s in(-1,1)],{site(v,4,s):s for v in vectors for s in(-1,1)})
                if answer['decoded_sign']!=row['reader']['formed_native_command']:a.issues.append({'source':filename,'tick':row['read_tick'],'issue':'native decoder mismatch'})
                events.append({'kind':'query','source':filename,'tick':row['read_tick'],'context':row['context_signal'],'native_sign':answer['decoded_sign']})
    if include_final05:
        prep=a.load('25_PREPARAR_EPSILON_MAIN_5.json.gz');capture(prep['result']['result']['requests'],'25_PREPARAR_EPSILON_MAIN_5.json.gz')
    events.sort(key=lambda x:x['tick']);last_by_context={};last_global=None;rows=[]
    for event in events:
        if event['kind']=='teacher':
            if event.get('teacher_admitted',True):
                last_by_context[event['context']]=event['explicit_teacher_sign'];last_global=event['explicit_teacher_sign']
            continue
        addressed=last_by_context.get(event['context']);native=event['native_sign']
        rows.append({**event,'per_context_last_teacher':addressed,'global_last_teacher':last_global,
                     'recall_reference_target_is_prior_teacher_not_hidden_task_solution':True,
                     'native_agrees_with_prior_teacher':native is not None and native==addressed,
                     'global_bit_agrees_with_prior_teacher':last_global is not None and last_global==addressed})
    groups={}
    for row in rows:
        key=row['source'];g=groups.setdefault(key,{'query_events':0,'native_answered':0,'native_prior_teacher_matches':0,'global_bit_prior_teacher_matches':0})
        g['query_events']+=1;g['native_answered']+=row['native_sign']is not None;g['native_prior_teacher_matches']+=row['native_agrees_with_prior_teacher'];g['global_bit_prior_teacher_matches']+=row['global_bit_agrees_with_prior_teacher']
    result={'schema':'DEE.MA02.offline_memory_references.v1','new_dee_ticks':0,'models_ever_controlled_DEE':False,
            'sources':a.sources,'events':events,'query_comparisons':rows,'unscored_native_compositions':compound,
            'summary':{'query_events_one_genealogy':len(rows),'native_answered':sum(q['native_sign']is not None for q in rows),
                'native_prior_teacher_matches':sum(q['native_agrees_with_prior_teacher']for q in rows),
                'context_table_prior_teacher_matches':sum(q['per_context_last_teacher']is not None for q in rows),
                'global_bit_prior_teacher_matches':sum(q['global_bit_agrees_with_prior_teacher']for q in rows),
                'maximum_context_sign_entries':len(last_by_context),'final_reference_only_state':last_by_context},
            'by_source':groups,'issues':a.issues,
            'scope_and_limits':[
                'Both references only receive explicit teacher signs already presented and the current context; none receives a future target, modelled eligibility law or worker reward.',
                'By construction, a per-context last-teacher table retains every labelled association. Its perfect score against the same prior-teacher definition is an interpretive lower-complexity reference, not a new empirical discovery or predictive intelligence test.',
                'The global one-bit reference deliberately discards context. It is not a simulation or asserted equivalence of MA_MAIN_R9 or any other DEE architecture.',
                'The five entries characterize bounded association capacity, not five task policies, semantic meanings or general intelligence.',
                'References ignore native damage, transport cost, material queries and compound consumption. Their resources are not matched to DEE and cannot justify universal superiority claims.',
                'Only selected MAIN genealogy events are included. Opposite, omission, cut/sham and other fork results never enter its memory history.',
                'Repeated queries, including64uses, are dependent events in one life, not independent training replicates. All omissions of compound scoring are explicit.' ]}
    if include_final05:
        receipts=[receipt_by_id[k]for k in sorted(receipt_by_id)]
        contiguous=[q['id']for q in receipts]==list(range(1,len(receipts)+1))
        if not contiguous:a.issues.append({'issue':'selected lifetime receipt IDs not contiguous'})
        result['selected_genealogy_native_admissions']={'requested':len(receipts),'applied':sum(q['status']=='applied'for q in receipts),
            'rejected':sum(q['status'].startswith('rejected')for q in receipts),'pending_or_other':sum(q['status']!='applied'and not q['status'].startswith('rejected')for q in receipts),
            'ids_contiguous_from_one':contiguous,'records':receipts,
            'scope':'Single selected physical genealogy only; includes130 pre-service native requests,977 row requests,20 actual worker-return pulses and6 anatomical-extension inputs; excludes all diagnostic branches.'}
        result['selected_main_worker_events']=worker_events
        result['selected_main_worker_summary']={'executed':len(worker_events),'accepted':sum(w['accepted']for w in worker_events),'commits':sum(w['transaction_completed']for w in worker_events)}
        result['cut']='Selected MA02_MAIN_5 T11196 after pending-state save/reload; no original life advanced by this calculation.'
    return result

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--evidencia',type=Path,required=True);p.add_argument('--salida',type=Path,required=True)
    q=p.parse_args();x=calculate(q.evidencia);q.salida.parent.mkdir(parents=True,exist_ok=True)
    q.salida.write_text(json.dumps(x,ensure_ascii=False,sort_keys=True,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'issues':len(x['issues']),**x['summary']},ensure_ascii=False));return1=1 if x['issues']else 0;return return1
if __name__=='__main__':raise SystemExit(main())
