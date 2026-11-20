"""N0 analytical policies on frozen laws; they never control or learn for DEE."""
import argparse,gzip,hashlib,json
from pathlib import Path
def load(path):
    data=path.read_bytes();return json.loads(gzip.decompress(data)if path.suffix=='.gz'else data)
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def native_route(reader):
    result=[]
    for o in reader['observations']:
        raw=int(o['raw']);state=raw&0xffffffff;semantic=(raw>>60)&15
        v=[((raw>>k)&15)-(16 if((raw>>k)&15)>=8 else 0)for k in(48,52,56)]
        if state and semantic==1 and v[0]in(-1,0,1)and v[1:]==[1,0]:result.append(v[0])
    return result[0]if len(result)==1 else None
def public_laws_main(protocol):
    law=None;block=-1;rows=[]
    for event in protocol['events']:
        for situation in event['payload'].get('situaciones',[]):
            if situation.get('modo')=='apd02-ambiente':
                law=situation['configuracion'];block+=1
                if law['fallos']!=['none','none']or law['disponibilidad']!=[True,True]or law['demora']!=[0,0]or law['presupuesto']!=2:raise ValueError('This policy model only covers published two-correct-provider, zero-delay ABAB laws')
            elif situation.get('modo')=='apd02':
                if law is None:raise ValueError('No predeclared environment')
                rows.append({'opportunity':len(rows)+1,'event_id':event['id'],'block':block+1,'prices':law['precios'],'public_literal':situation['texto'],'public_operands':situation['operandos']})
    actual=[sum(r['block']==i+1 for r in rows)for i in range(block+1)]
    if actual!=protocol['frozen_block_opportunities']:raise ValueError('Block denominators differ from frozen protocol')
    return rows
def public_laws_aux(protocol):
    result=[];last=None;block=0
    for i,case in enumerate(protocol['cases']):
        if case['law']!=last:block+=1;last=case['law']
        result.append({'opportunity':i+1,'event_id':'OP'+str(i),'block':block,'prices':case['prices'],'public_literal':'suma','public_operands':case['operands']})
    if[sum(r['block']==i for r in result)for i in range(1,block+1)]!=[2,3,1,2]:raise ValueError('Not the frozen AUX law')
    return result
def metrics(rows):
    blocks=[]
    for block in sorted({r['block']for r in rows}):
        items=[r for r in rows if r['block']==block];good=next((i+1 for i,r in enumerate(items)if r['useful']),None)
        blocks.append({'block':block,'opportunities':len(items),'first_response_route':items[0]['route'],'first_response_useful':items[0]['useful'],'first_useful_local_opportunity':good,'first_useful_censored_after':len(items)if good is None else None,'failures_before_first_useful':sum(not r['useful']for r in items[:good-1])if good else sum(not r['useful']for r in items),'cost':sum(r['modelled_price']for r in items)})
    after_failure=[{'opportunity':r['opportunity'],'previous_opportunity':rows[i-1]['opportunity'],'same_block_as_failure':r['block']==rows[i-1]['block'],'useful':r['useful'],'route':r['route']}for i,r in enumerate(rows)if i and rows[i-1]['category']=='FAILURE']
    return{'requested':len(rows),'responded':sum(r['route']in('native','external')for r in rows),'useful':sum(r['useful']for r in rows),'not_useful':sum(not r['useful']for r in rows),'total_modelled_price':sum(r['modelled_price']for r in rows),'first_responses_by_block':blocks,'next_use_after_own_observed_failure':after_failure,'useful_next_after_failure':sum(r['useful']for r in after_failure),'next_after_failure_denominator':len(after_failure)}
def simulate(laws,policy):
    action='external';result=[]
    for law in laws:
        if policy=='always_native':action='native'
        elif policy=='always_external':action='external'
        elif policy=='private_oracle':action='native'if law['prices'][0]<=law['prices'][1]else'external'
        elif policy!='conventional_WSLS':raise ValueError(policy)
        price=law['prices'][0 if action=='native'else 1];category='SUCCESS'if price<=2 else'FAILURE'
        result.append({**law,'route':action,'modelled_price':price,'category':category,'useful':category=='SUCCESS','numeric_correct_observed':None,'numeric_correct_assumption_for_conditional_model':True})
        if policy=='conventional_WSLS'and category=='FAILURE':action='external'if action=='native'else'native'
    return{'kind':'analytical_counterfactual_external_policy_not_DEE_execution','policy':policy,'information':'private current two-route prices; unattainable participant oracle'if policy=='private_oracle'else'Constant route'if policy.startswith('always_')else'Initial external; only its OWN post-action simulated binary category causes alternation; no current hidden law or learner outcome enters the policy','rows':result,'metrics':metrics(result),'correctness_scope':'Correct-provider assumption of this cost-only counterfactual model, not new measured numeric executions or host CPU/ticks/RAM.'}
def observed_row(law,value,choice,quality,committed):
    route='native'if choice==-1 else'external'if choice in(0,1)else None
    if route!=committed['selected_procedure']:raise ValueError('Native route and committed sole provider disagree')
    price=committed['price'];expected_price=law['prices'][0 if route=='native'else 1]if route else 0
    if price!=expected_price:raise ValueError('Actual charged price differs from its predeclared law')
    category='SUCCESS'if quality['feedback']['category']=='SUCCESS'else'FAILURE'
    return{**law,'route':route,'native_emission':choice,'neutral_0_is_material_external_not_plus_1':choice==0,'modelled_price':price,'category':category,'useful':bool(quality['task_success']),'numeric_correct_observed':quality['axes']['numeric_correct_for_original_request'],'completed_valid_artifact_observed':quality['completed_task'],'actual_effect_state':committed['state'],'only_return_to_DEE':category,'effect_commit_tick':value.get('committed_at',value.get('commit_before_verification',{})).get('tick')}
def calculate(evidence):
    issues=[];sources=[];studies={}
    def remember(p):sources.append({'file':p.relative_to(evidence).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)})
    for name in('AUX','MAIN'):
        folder=evidence/('AUXILIAR'if name=='AUX'else name);protocol_path=folder/'PROTOCOLO.json'
        if not protocol_path.is_file():continue
        protocol=load(protocol_path);remember(protocol_path);laws=public_laws_aux(protocol)if name=='AUX'else public_laws_main(protocol)
        policies=[simulate(laws,p)for p in('always_native','always_external','conventional_WSLS','private_oracle')];observed=[]
        if name=='AUX':
            for i,law in enumerate(laws):
                file=folder/('OP'+str(i))/'RESULTADO_COMPLETO.json.gz';v=load(file)['result'];remember(file);choice=native_route(v['use']['reader'])
                if choice!=v['native_choice']:raise ValueError('AUX decoded route mismatch')
                observed.append(observed_row(law,v,choice,v['quality'],v['committed_effect']))
        elif(folder/'REGISTROS_VENTANA.json.gz').is_file():
            records_file=folder/'REGISTROS_VENTANA.json.gz';summary_file=folder/'RESUMEN.json';summary=load(summary_file);remember(summary_file)
            if summary.get('error')or summary['owner_final'].get('running')or summary.get('pending')or summary.get('owner_returncode')!=0:raise ValueError('Only a closed successful owner sequence may be interpreted as the complete observed MAIN law')
            records=load(records_file)['records'];remember(records_file)
            for law in laws:
                key=protocol['prefix']+law['event_id']+'_parsed';entry=records[key]
                candidates=[r for r in entry['result']['rows']if r.get('kind')=='APD02_quality_request']
                if len(candidates)!=1:raise ValueError('Exactly one actual assistant result per declared task; no double counting rows and parsed cache')
                v=candidates[0];choice=native_route(v['route']['reader'])
                if choice!=v['native_route_command']:raise ValueError('MAIN decoded route mismatch')
                observed.append(observed_row(law,v,choice,v['quality'],v['committed_effect']))
        studies[name]={'frozen_laws':laws,'external_analytical_references':policies,'observed_learner':{'kind':'Actual closed DEE observations, not a benchmark policy controlling it','rows':observed,'metrics':metrics(observed)}if observed else None,'observed_learner_status':'closed evidence included'if observed else'not supplied: do not infer learner result from prospective policy model','assumptions':'Two available correct providers with no injected fault/delay for this cost-only comparison; unexecuted alternative correctness is conditional, not empirical. The private oracle violates participant information by definition.'}
    return{'schema':'APD02.R04.separate_analytical_references.v1','studies':studies,'sources':sources,'issues':issues,'native_ticks':0,'external_effects_executed_by_this_recalculation':0,'scope':'No Runtime, actor source change or host policy controlling E1. Laws and evaluation are auditor-side only. Prices are simulated environmental quantities, never electricity, CPU time, ticks, memory use or native thermodynamics. Controls omit/sham/desync are excluded from the task denominator.'}
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--evidencia',type=Path,required=True);p.add_argument('--salida',type=Path,required=True);a=p.parse_args()
    if a.salida.resolve().is_relative_to(a.evidencia.resolve())or a.salida.exists():raise ValueError('New output outside immutable evidence tree')
    r=calculate(a.evidencia);a.salida.parent.mkdir(parents=True,exist_ok=True);a.salida.write_text(json.dumps(r,ensure_ascii=False,sort_keys=True,indent=2)+'\n',encoding='utf8')
    print(json.dumps({k:{'policies':{p['policy']:p['metrics']['total_modelled_price']for p in v['external_analytical_references']},'learner':v['observed_learner']['metrics']if v['observed_learner']else None}for k,v in r['studies'].items()},sort_keys=True));return 0
if __name__=='__main__':raise SystemExit(main())
