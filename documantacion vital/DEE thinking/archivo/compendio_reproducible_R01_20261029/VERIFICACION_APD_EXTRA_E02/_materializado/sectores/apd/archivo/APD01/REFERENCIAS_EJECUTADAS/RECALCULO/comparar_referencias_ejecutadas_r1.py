"""Observed policy cost/numeric comparison, not a new controller or DEE run."""
import argparse,gzip,hashlib,importlib.util,json
from pathlib import Path

def load(p):
    b=p.read_bytes();return json.loads(gzip.decompress(b)if p.suffix=='.gz'else b)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def walk(v):
    if isinstance(v,dict):
        yield v
        for x in v.values():yield from walk(x)
    elif isinstance(v,list):
        for x in v:yield from walk(x)

def calculate(root):
    script=Path(__file__).with_name('recalcular_referencias_ejecutadas_o2_r1.py');spec=importlib.util.spec_from_file_location('PURE_REFERENCE_RECORD_DECODER',script);decoder=importlib.util.module_from_spec(spec);spec.loader.exec_module(decoder)
    reference=load(root/'RECALCULO_REFERENCIAS_EJECUTADAS_R02.json');frozen=load(root/'ANTES_DEL_PRIMER_TICK.json');issues=list(reference['issues']);rows=[];sources=[]
    for name in('RECALCULO_REFERENCIAS_EJECUTADAS_R02.json','ANTES_DEL_PRIMER_TICK.json'):
        p=root/name;sources.append({'file':name,'bytes':p.stat().st_size,'sha256':sha(p)})
    for domain in frozen['protocol']['sources']:
        folder=root/'LEARNER_EXISTENTE'/domain['domain'];primary=folder/'RESULTADO_COMPLETO.json.gz';sources.append({'file':primary.relative_to(root).as_posix(),'bytes':primary.stat().st_size,'sha256':sha(primary)});data=load(primary)['result'];tasks=[];native_calls=0;external_calls=0;event_ids=set()
        for r in data['rows']:
            choice=decoder.read6(r['route']['reader']);native=r['native_calculation'];external=r['external_calculator'];numeric=None
            if native is not None:
                native_calls+=1;t=native['native_trial'];when=t['datum_tick']-2;fs=[f for f in t['frames']if f['tick']==when]
                if len(fs)!=1:raise ValueError('No historical fixed native gate')
                o=fs[0]['fields']['C'];f=decoder.fields(o['raw']);valid=o['site']==[12,17,18]and o['tick']==when and f['state']>0 and f['semantic']==1 and f['direction']==[1,-1,-1]
                numeric=f['s_reg']if valid else None
                if choice!=-1 or external is not None or numeric!=native['numeric_reader']['numeric_result']:issues.append('learner:native_decoder_or_route')
            elif external is not None:
                external_calls+=1;numeric=external['value']
                if choice not in(0,1):issues.append('learner:external_route')
            if numeric!=r['numeric_result']:issues.append('learner:reported_number')
            artifact=r['artifact'];verified=False
            if artifact:
                p=folder/artifact['file'];b=p.read_bytes();verified=(sha(p)==artifact['sha256']and len(b)==artifact['bytes']and b==str(numeric).encode('ascii'))
                sources.append({'file':p.relative_to(root).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)})
                if not verified:issues.append('learner:actual_artifact')
            cost=r['modelled_price']if domain['domain']=='INITIAL_N1_E5'else r['actual_modelled_cost']
            for node in walk(r):
                if type(node.get('id'))is int and isinstance(node.get('receipt'),dict):event_ids.add(node['id'])
            tasks.append({'actual_native_route':choice,'numeric_result':numeric,'numeric_correct':None if numeric is None else numeric==sum(r['operands']),'actual_artifact_bytes_verified':verified,'actual_modelled_cost':cost})
        rows.append({'domain':domain['domain'],'controller':'DEE_LEARNER_EXISTING_REUSED_NOT_REPEATED','life':'APD01_ROUTE_O2_R3_real'if domain['domain']=='INITIAL_N1_E5'else'APD01_ROUTE_O2_R3_REVERSE',
                     'actual_tasks':len(tasks),'numeric_responses':sum(t['numeric_result']is not None for t in tasks),'numeric_correct':sum(t['numeric_correct']is True for t in tasks),
                     'actual_artifacts':sum(t['actual_artifact_bytes_verified']for t in tasks),'cost':sum(t['actual_modelled_cost']for t in tasks),
                     'native_arithmetic_calls':native_calls,'external_calculator_calls':external_calls,'native_requests_in_task_blocks':len(event_ids),'tasks':tasks,
                     'retention_scope':'Original learner panel retained in its own earlier records; this comparison does not perform it again.'})
        for case in(c for c in reference['cases']if c['domain']==domain['domain']):
            label=case['domain']+'__'+case['policy'];p=root/label/'01_RESULTADO_COMPLETO.json.gz';doc=load(p)['result'];prefix_ok=all(doc['before'][key]==domain[target]for key,target in(('tick','parent_tick'),('RAW_sha256','parent_RAW_sha256'),('clocks_sha256','parent_clocks_sha256')))
            if not prefix_ok:issues.append('reference:matched_complete_physical_prefix:'+label)
            actual_rows=doc['rows'];n_calls=sum(r['native_calculation']is not None for r in actual_rows);e_calls=sum(r['external_calculator']is not None for r in actual_rows)
            forced_opposite=sum((r['host_reference_action']=='native')!=(r['native_route_observed_but_not_used_for_reference_choice']==-1)for r in actual_rows)
            rows.append({'domain':case['domain'],'controller':'DECLARED_HOST_REFERENCE__'+case['policy'],'life':case['life'],'actual_tasks':len(case['tasks']),
                         'numeric_responses':case['numeric_responses'],'numeric_correct':case['numeric_correct'],'actual_artifacts':case['actual_artifacts'],
                         'cost':case['total_actual_modelled_cost'],'native_arithmetic_calls':n_calls,'external_calculator_calls':e_calls,
                         'native_requests_in_task_blocks':case['requested_native_events'],'all_counted_native_statuses':case['native_statuses_at_capture'],
                         'host_action_differs_from_native_route_class':forced_opposite,'matched_starting_RAW_clocks_tick':prefix_ok,
                         'retention_scope':'Not revalidated by an old-memory panel in these reference branches; no whole-entity competence attributed.'})
    return {'schema':'APD01.observed_reference_vs_existing_learner.table.v1','native_ticks':0,'new_native_replay':False,'rows':rows,'sources':sources,'issues':issues,
            'coverage':{'initial_positive_prefix_reference_tasks':9,'actual_negative_prefix_reverse_reference_tasks':6,
                        'same_law_negative_prefix_references':'Remain analytical only; not newly executed by this15-task supplement'},
            'limits':['Only published modelled task price is compared; not CPU, memory, native energy or universal efficiency.',
                      'The generic O2 query/common-return family is retained. Native arithmetic adds176 actual physical requests per call; external arithmetic does not. Different actions legitimately produce different histories/calendars.',
                      'Reference controllers directly use their own prior post-action cost threshold bit. Their choices were HOST overrides; they are not E1 acquisitions, new independent DEE learners or generalR2.',
                      'The comparison reuses existing learner trajectories without repeating them; independent replicas or a distribution of seeds are not claimed.']}

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--evidencia',type=Path,required=True);p.add_argument('--salida',type=Path,required=True);a=p.parse_args()
    if a.salida.exists():raise FileExistsError('Preserve earlier comparison')
    r=calculate(a.evidencia);a.salida.write_text(json.dumps(r,ensure_ascii=False,sort_keys=True,indent=2)+'\n',encoding='utf8')
    print(json.dumps({'issues':r['issues'],'rows':[{k:x.get(k)for k in('domain','controller','cost','numeric_correct','actual_tasks','native_requests_in_task_blocks')}for x in r['rows']]}))
    raise SystemExit(bool(r['issues']))
