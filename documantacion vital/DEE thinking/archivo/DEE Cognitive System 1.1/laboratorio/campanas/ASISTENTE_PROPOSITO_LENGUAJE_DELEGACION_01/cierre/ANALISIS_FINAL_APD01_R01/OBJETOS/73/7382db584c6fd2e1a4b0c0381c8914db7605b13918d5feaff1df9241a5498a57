"""Auditor of actually executed HOST reference copies; standard library, zero ticks."""
import argparse,gzip,hashlib,json
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
def fields(v):
    if type(v)is not int and not(isinstance(v,str)and v.isascii()and v.isdecimal()):raise ValueError('Exact uint64 only')
    n=int(v)
    if not 0<=n<2**64:raise ValueError('uint64 out of range')
    return {'state':n&0xffffffff,'s_reg':(n>>32)&65535,'semantic':(n>>60)&15,'direction':[((n>>s)&15)-(16 if((n>>s)&15)>=8 else 0)for s in(48,52,56)]}
def read6(r):
    origin=r.get('origin',[15,45,15]);expected={tuple((origin[j]+[2*x,2,2*z][j])%67 for j in range(3)):[x,1,z]for x in(-1,0,1)for z in(0,-1)}
    if len(r['observations'])!=6 or{tuple(o['site'])for o in r['observations']}!=set(expected):raise ValueError('Changed frozen six gates')
    choices=[]
    for o in r['observations']:
        f=fields(o['raw']);di=expected[tuple(o['site'])]
        if f['state']and f['semantic']==1 and f['direction']==di:choices.append(di[0])
    return choices[0]if len(choices)==1 else None
def policy_next(policy,previous_action,previous_cost,initial):
    if policy=='always_native':return'native'
    if policy=='always_external':return'external'
    if policy!='stay_until_last_cost_exceeds_budget_then_alternate':raise ValueError('Unknown fixed reference')
    if previous_action is None:return initial
    return('external'if previous_action=='native'else'native')if previous_cost>2 else previous_action

def calculate(root):
    frozen=load(root/'ANTES_DEL_PRIMER_TICK.json');protocol=frozen['protocol'];summary=load(root/'RESULTADOS.json');issues=[];sources=[];raws=set();cases=[]
    def source(p):sources.append({'file':p.relative_to(root).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)})
    source(root/'ANTES_DEL_PRIMER_TICK.json');source(root/'RESULTADOS.json')
    for item in frozen['sources']:
        p=root/item['file'];source(p)
        if sha(p)!=item['sha256']or p.stat().st_size!=item['bytes']:issues.append('frozen_source:'+item['file'])
    for outcome in summary['outcomes']:
        if outcome.get('error')or outcome.get('not_executed'):
            cases.append({'domain':outcome['domain'],'policy':outcome['policy'],'technical_error_or_not_executed':outcome.get('error',outcome.get('not_executed')),'numeric_execution_scope':'Do not infer failure of DEE or numerical correctness from this technical/missing run'});continue
        domain=next(d for d in protocol['sources']if d['domain']==outcome['domain']);policy=outcome['policy'];folder=root/(domain['domain']+'__'+policy)
        p=folder/'01_RESULTADO_COMPLETO.json.gz';source(p);doc=load(p);v=doc['result'];requests={};checks=[];previous_action=None;previous_cost=None;readers=0
        for node in walk(v):
            if all(k in node for k in('raw','clock','state','s_reg','semantic','direction','site')):
                key=hashlib.sha256(json.dumps(node,sort_keys=True,separators=(',',':')).encode('utf8')).hexdigest()
                if key not in raws:
                    raws.add(key)
                    if any(node[k]!=x for k,x in fields(node['raw']).items()):issues.append(outcome['life']+':RAW:'+key)
                    if not 0<=int(node['clock'])<2**64:issues.append(outcome['life']+':clock')
            if isinstance(node.get('reader'),dict)and'choice'in node['reader']and'observations'in node['reader']:
                r=node['reader'];readers+=1
                if read6(r)!=r['choice']:issues.append(outcome['life']+':six_reader')
            if type(node.get('id'))is int and isinstance(node.get('receipt'),dict):
                receipt=node['receipt'];old=requests.get(node['id'])
                if receipt['id']!=node['id']:issues.append(outcome['life']+':receipt_id')
                if old is not None and old!=receipt:issues.append(outcome['life']+':inconsistent_receipt_views')
                requests[node['id']]=receipt
        for index,row in enumerate(v['rows']):
            expected_action=policy_next(policy,previous_action,previous_cost,domain['initial_adaptive_action']);action=row['host_reference_action'];info=row['policy_information_before_action'];actualchoice=read6(row['native_query']['reader'])
            if action!=expected_action or info!={'previous_action':previous_action,'previous_own_actual_cost':previous_cost,'initial_action':domain['initial_adaptive_action'],'budget':2}:issues.append(outcome['life']+':causal_policy_history')
            if actualchoice!=row['native_route_observed_but_not_used_for_reference_choice']:issues.append(outcome['life']+':native_query_record')
            if row['public_operands']!=domain['opportunities'][index]:issues.append(outcome['life']+':public_task')
            native=row['native_calculation'];external=row['external_calculator'];numeric=None
            if action=='native':
                if native is None or external is not None:issues.append(outcome['life']+':both_or_missing_implementations')
                else:
                    trial=native['native_trial'];at=trial['datum_tick']-2;frames=[f for f in trial['frames']if f['tick']==at]
                    if len(frames)!=1:raise ValueError('No frozen native numeric frame')
                    o=frames[0]['fields']['C'];f=fields(o['raw']);valid=o['site']==[12,17,18]and o['tick']==at and f['state']>0 and f['semantic']==1 and f['direction']==[1,-1,-1]
                    numeric=f['s_reg']if valid else None
                    if native['operation']!='suma'or native['numeric_reader']['numeric_result']!=numeric:issues.append(outcome['life']+':native_numeric_decoder')
                    components=trial['raw_components'];wanted=[0]*128;wanted[0],wanted[1]=row['public_operands']
                    if components!=wanted:issues.append(outcome['life']+':independent_operand_channels')
            elif external is None or native is not None:issues.append(outcome['life']+':both_or_missing_implementations')
            else:
                numeric=external['value']
                if external.get('not_a_DEE_operation')is not True:issues.append(outcome['life']+':external_attribution')
            # Expected sum is OFFLINE AUDITOR ONLY, never a policy, native input or corrective feedback.
            correct=None if numeric is None else numeric==sum(row['public_operands'])
            if numeric!=row['numeric_result']:issues.append(outcome['life']+':reported_numeric')
            artifact=row['artifact'];artifact_ok=False
            if artifact:
                p=folder/artifact['file'];source(p);data=p.read_bytes();artifact_ok=(data==str(numeric).encode('ascii')and len(data)==artifact['bytes']and sha(p)==artifact['sha256'])
                if not artifact_ok:issues.append(outcome['life']+':artifact_bytes')
            completed=artifact is not None
            if row['completed']!=completed:issues.append(outcome['life']+':completion')
            price=domain['prices'][action];cost=(price if completed else 5)if domain['missing_artifact_rule']=='fixed_deadline5'else price+(0 if completed else 4)
            returned=row['common_return'];k=returned['boundary_multiplier'];cost_inputs=[r for r in returned['requests']if r.get('port')=='APD.route.cost']
            if row['modelled_price']!=price or row['actual_modelled_cost']!=cost or returned['cost']!=cost or returned['mode']!='real' or k%2 or returned['query_tick']!=391*k-4 or returned['datum_tick']!=391*k-1:issues.append(outcome['life']+':published_consequence_law')
            if len(cost_inputs)!=(1 if cost>2 else 0)or any(r['payload']!=cost for r in cost_inputs):issues.append(outcome['life']+':fixed_common_return_port')
            checks.append({'opportunity':index,'action_selected_by_host_reference':action,'native_query_choice_ignored_for_this_reference':actualchoice,
                           'numeric_result_observed':numeric,'numeric_correct':correct,'artifact_bytes_verified':artifact_ok,
                           'actual_modelled_cost':cost,'reference_state_after':[fields(o['raw'])['s_reg']for o in row['references_after']]})
            previous_action=action;previous_cost=cost
        statuses={}
        for receipt in requests.values():statuses[receipt['status']]=statuses.get(receipt['status'],0)+1
        cases.append({'domain':domain['domain'],'policy':policy,'life':outcome['life'],'tasks':checks,'requested_native_events':len(requests),'native_statuses_at_capture':statuses,
                      'native_query_readers_checked':readers,'numeric_responses':sum(x['numeric_result_observed']is not None for x in checks),
                      'numeric_correct':sum(x['numeric_correct']is True for x in checks),'actual_artifacts':sum(x['artifact_bytes_verified']for x in checks),
                      'total_actual_modelled_cost':sum(x['actual_modelled_cost']for x in checks),'final':v['final'],
                      'classification':'OBSERVED_HOST_REFERENCE_NOT_DEE_POLICY_LEARNING'})
    return {'schema':'APD01.actual_host_reference_recalculation.v1','native_ticks':0,'sources':sources,'cases':cases,'issues':issues,'RAW_observations_checked':len(raws),
            'scope':'Native/external arithmetic and artifact/cost data were actually executed in explicit reference copies. Only choices of the DEE learner remain DEE choices; these reference choices were forced by declared host policies. Their real files/numerical correctness close the earlier conditional-reference gap, not a claim of learner competence, R2 or CPU/energy efficiency.'}

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--evidencia',type=Path,required=True);p.add_argument('--salida',type=Path,required=True);a=p.parse_args()
    if a.salida.exists():raise FileExistsError('Preserve earlier reference audit')
    r=calculate(a.evidencia);a.salida.write_text(json.dumps(r,ensure_ascii=False,sort_keys=True,indent=2)+'\n',encoding='utf8')
    print(json.dumps({'issues':r['issues'],'RAW_checked':r['RAW_observations_checked'],'cases':[{'domain':c['domain'],'policy':c['policy'],'cost':c.get('total_actual_modelled_cost'),'correct':c.get('numeric_correct')}for c in r['cases']]}))
    raise SystemExit(bool(r['issues']))
