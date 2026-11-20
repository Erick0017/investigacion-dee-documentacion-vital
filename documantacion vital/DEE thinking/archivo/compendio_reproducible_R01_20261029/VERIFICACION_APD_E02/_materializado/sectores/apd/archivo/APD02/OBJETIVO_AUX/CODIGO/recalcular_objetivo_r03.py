"""Portable exact primary auditor of native goal action/effects, zero ticks."""
import argparse,base64,gzip,hashlib,importlib.util,json
from pathlib import Path
HISTORY={'alfa':-1,'beta':-1,'gamma':1,'delta':-1,'epsilon':-1,'zeta':1,
    'suma':1,'diferencia':-1,'agrega':1,'resta':-1,'total':1,'quita':-1,'compara':1,'recuerda':-1}
def read(p):return json.loads(gzip.decompress(p.read_bytes())if p.suffix=='.gz'else p.read_bytes())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def fields(raw):
    if type(raw)is not int and not(type(raw)is str and raw.isdecimal()):raise ValueError('No floating/inexact RAW')
    n=int(raw)
    if not 0<=n<2**64:raise ValueError('Exact uint64 required')
    return {'state':n&0xffffffff,'semantic':(n>>60)&15,'s_reg':(n>>32)&65535,
        'direction':[((n>>s)&15)-(16 if((n>>s)&15)>=8 else 0)for s in(48,52,56)],'active':bool(n&0xffffffff)}
def walk(x):
    if isinstance(x,dict):
        yield x
        for v in x.values():yield from walk(v)
    elif isinstance(x,list):
        for v in x:yield from walk(v)
def choice(reader):
    candidates=[];expected={(23,15,53):-1,(25,15,53):0,(27,15,53):1}
    if {tuple(o['site'])for o in reader['observations']}!=set(expected):raise ValueError('Frozen three-gate selector differs')
    for o in reader['observations']:
        f=fields(o['raw']);x=expected[tuple(o['site'])]
        if f['state']and f['semantic']==1 and f['direction']==[x,1,0]:candidates.append(x)
    return candidates[0]if len(candidates)==1 else None
def word(reader):
    candidates=[]
    if len(reader['panel'])!=28:raise ValueError('Frozen28 lexical reader differs')
    for o in reader['panel']:
        f=fields(o['raw'])
        if f['state']and f['semantic']==1 and f['direction'][:2]==[0,0]and f['direction'][2]in(-1,1):candidates.append(f['direction'][2])
    return candidates[0]if len(candidates)==1 else None
def numeric(record):
    trial=record['native_trial'];tick=trial['datum_tick']-2
    candidates=[f['fields']['C']for f in trial['frames']if f['tick']==tick]
    if len(candidates)!=1:raise ValueError('Unique native numeric gate required')
    o=candidates[0];f=fields(o['raw'])
    valid=o['site']==[12,17,18]and f['state']and f['semantic']==1 and f['direction']==[1,-1,-1]
    return f['s_reg']-(32 if record['operation']=='diferencia'else 0)if valid else None
def main():
    p=argparse.ArgumentParser();p.add_argument('--evidence',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    if a.output.exists():raise FileExistsError('Preserve preceding reference')
    ev=a.evidence;spec=importlib.util.spec_from_file_location('post_goal_auditor',ev/'FUENTES/evaluador_calidad_apd02.py');q=importlib.util.module_from_spec(spec);spec.loader.exec_module(q)
    protocol=read(ev/'PROTOCOLO_CONGELADO.json');issues=[];cases=[];sources=[];RAW=0
    for case in protocol['cases']:
        name=case['case'];events=[];receipts={};prior=None;afterprefix=None;old=[];phases=[]
        for phase in('prefix','suffix'):
            path=ev/phase/name/'PRIMARIO.json.gz';r=read(path);sources.append({'path':str(path.relative_to(ev)).replace('\\','/'),'sha256':sha(path)})
            if r['error']:issues.append([name,phase,'Native case error',r['error']])
            for node in walk(r):
                if 'raw'in node and'site'in node:
                    f=fields(node['raw']);RAW+=1
                    if any(k in node and node[k]!=v for k,v in f.items()):issues.append([name,phase,'RAW decoded fields mismatch',node['site']])
                rr=node.get('receipt')
                if isinstance(rr,dict)and'id'in rr:
                    key=str(rr['id']);prev=receipts.get(key)
                    if prev is None or prev['status']=='scheduled':receipts[key]=rr
                    elif rr['status']!='scheduled'and prev!=rr:issues.append([name,key,'Terminal receipt changed'])
            if phase=='prefix':
                b=r['binding']
                if b['before_physical']!=b['after_physical']or b['pending_before']!=b['pending_after']:issues.append([name,'Binding changed physical state or agenda'])
                prior=r;afterprefix=r['environment_after']
            else:
                if r['initial']!=prior['final']or not r['pending_restored_exactly']or r['pid']==prior['pid']:issues.append([name,'Other-process complete state/world continuity failed'])
                old=[[v['form'],word(v['reader'])]for v in r['old_panel']]
                if any(s!=v['reader']['formed_native_command']for (_,s),v in zip(old,r['old_panel'])):issues.append([name,'Old lexical RAW mismatch'])
            result=r.get('goal_result');ops=result['result']['opportunities']if result else[]
            for o in ops:
                physical_choice=choice(o['native_selection']['reader']);sign=word(o['word']['reader']);effect=o['environment_effect']
                if physical_choice!=effect['physical_action_sign']or physical_choice!=o['native_selection']['reader']['choice']or sign!=effect['physical_operation_sign']:issues.append([name,'Physical sign/action mismatch'])
                action=None if physical_choice is None else'ACT'if physical_choice==-1 else'QUERY'
                if effect['selected_action']!=action:issues.append([name,'Actuator codec changed'])
                before=effect['public_before'];after=effect['public_after'];number=None;correct=None
                if action=='QUERY':
                    if after['second']!=case['operands'][1]or effect['native_provider_called']or o['native_numeric']or effect['feedback']!={'category':'FAILURE'}:issues.append([name,'QUERY concealed arithmetic/correction or failed raw revelation'])
                elif action=='ACT'and before['second']is not None and sign is not None:
                    if len(o['native_numeric'])!=1:issues.append([name,'ACT must call one native provider'])
                    else:
                        number=numeric(o['native_numeric'][0]);committed=effect['committed_effect'];public={'task_id':committed['task_id'],'text':case['text'],'operands':[before['left'],before['second']]}
                        if number!=committed['raw_provider_response']['value']or number!=committed['used_value']:issues.append([name,'File value differs from actual native gate'])
                        directory=path.parent/'step/world';report=q.evaluate_literal_committed(public,committed,sandbox_root=directory,
                            policy={'max_operand':32,'max_artifact_bytes':4096,'max_price':2,'max_delay_ticks':8,'resource_limits_required_for_success':True})
                        correct=report['task_success']
                        if {k:v for k,v in report.items()if k!='evaluation_resources'}!={k:v for k,v in effect['quality'].items()if k!='evaluation_resources'}:issues.append([name,'Post-action real artifact quality mismatch'])
                elif effect['native_provider_called']or o['native_numeric']:issues.append([name,'Incomplete/silent ACT used a substituted value'])
                if o['common_return']is not None and(o['common_return']['category']!=effect['feedback']['category']or o['common_return']['mode']!=case['feedback']):issues.append([name,'Return category/mode altered'])
                events.append({'phase':phase,'opportunity':o['opportunity'],'choice':physical_choice,'word_sign':sign,'action':action,
                    'public_before':before,'public_after':after,'effect':effect['environment_effect'],'native_numeric':number,'quality_success':correct,
                    'consequence_category':effect['feedback']['category']if effect['feedback']else None,'consequence_mode':o['mode'],
                    'query_tick':o['native_selection']['query_tick']})
            phases.append({'phase':phase,'pid':r['pid'],'tick_before':r['initial']['tick'],'tick_after':r['final']['tick']})
        final=r['environment_after'];artifacts=final['artifacts']
        for artifact in artifacts:
            data=base64.b64decode(artifact['content_base64'],validate=True)
            if len(data)!=artifact['bytes']or hashlib.sha256(data).hexdigest()!=artifact['sha256']:issues.append([name,'Portable goal artifact bytes/hash mismatch'])
        statuses={}
        for rec in receipts.values():statuses[rec['status']]=statuses.get(rec['status'],0)+1
        cases.append({'case':name,'phases':phases,'events':events,'prefix_environment':afterprefix,
            'completed':final['progress']['verified_file_goal_completed'],'opportunities_used':final['progress']['opportunities_used'],
            'old_panel':old,'old_signs_valid':sum(s in(-1,1)for _,s in old),'old_queries':len(old),
            'old_matches_declared_acquisition_history':sum(s==HISTORY[f]for f,s in old),
            'unique_native_requests':len(receipts),'admission':statuses,'artifacts':[{k:v for k,v in x.items()if k!='content_base64'}for x in artifacts]})
    by={c['case']:c for c in cases};first=by['hidden_real']['events'][1];second=by['hidden_omit']['events'][1]
    common={'public_observation_equal':first['public_before']==second['public_before'],'same_query_tick':first['query_tick']==second['query_tick'],
        'actual_real_action':first['action'],'actual_omit_action':second['action'],'different_actions':first['action']!=second['action']}
    if not common['public_observation_equal']or not common['same_query_tick']:issues.append(['Intended common second opportunity not comparable'])
    result={'schema':'APD02.native_goal.archive_audit.R03','new_ticks':0,'engine_imported':False,'RAW_observations_checked':RAW,
        'cases':cases,'common_second_opportunity':common,'issues':issues,'sources':sources,
        'limits':['One inherited AUX history, four deterministic branches, not independent training replications',
            'First QUERY and fixed action codec are not learned semantic detection of absent information',
            'R04 consequence modifies a later local action; no general planner/R2 or autonomous goal schedule',
            'Environment private b and file bytes are legitimate external operational state, not acquired native memory',
            'Native full snapshot plus goal state restored across two processes; no SQLite/service restart claim']}
    with a.output.open('x',encoding='utf8')as f:json.dump(result,f,ensure_ascii=False,indent=2)
    print(json.dumps({'cases':len(cases),'RAW':RAW,'issues':issues,'common':common,'results':[{'case':c['case'],'actions':[v['action']for v in c['events']],'completed':c['completed'],'old':c['old_signs_valid'],'inputs':c['admission']}for c in cases]},ensure_ascii=False))
    if issues:raise SystemExit(1)
if __name__=='__main__':main()
