"""Pure validation of CLOSED actual post12 panels and prospectively fixed gate.

No world, Runtime, SQLite, live process or target-based decoding. Numeric/FI
readers are reconstructed from actual RAW with frozen source/codecs; word and
context values use their declared original primary read_path. Zero != NULL.
"""
from pathlib import Path
import argparse,ast,hashlib,importlib.util,json
P=Path(__file__).resolve().parents[1];H=P/'codigo';C=P.parents[2]/'DEE Cognitive 2.0';GATE=P/'control/GATE_P0_ARITMETICA_PRE_NATIVE_PI09_R01.json';GATE_SHA='3c5e1de201241935750e008513fae0f24c6fa7346bf4f304858276c05c68f05d'
WORDS=('luma','nara','clasifica','suma','alfa','alfa_after','luma_after');SIGNED=('FIplus','FIminus','FIzero')
def need(ok,msg):
 if not ok:raise ValueError(msg)
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ref(p):return {'path':str(p),'sha256':sha(p)}
def at(value,path):
 for key in path:
  if isinstance(value,str):value=json.loads(value)
  value=value[key]
 return value
def RAW(o):
 need(all(type(o.get(k))is int for k in('state','s_reg','semantic','tick'))and isinstance(o.get('direction'),list)and len(o['direction'])==3 and all(type(x)is int for x in o['direction']),'Literal physical integer fields required; bool is not a Native integer')
 n=int(o['raw']);need(0<=n<2**64,'Actual uint64 RAW required');direction=[]
 for shift in(48,52,56):x=(n>>shift)&15;direction.append(x-16 if x&8 else x)
 fields={'state':n&0xffffffff,'s_reg':(n>>32)&65535,'semantic':n>>60,'direction':direction}
 need(all(o[k]==v for k,v in fields.items()),'RAW fields differ from literal record')
 return fields
def frozen_numeric():
 file=C/'sistema/capacidades/aritmetica_apd_01.py';text=file.read_text('utf-8-sig');tree=ast.parse(text);scope={}
 for node in tree.body:
  if isinstance(node,ast.Assign)and all(isinstance(t,ast.Name)for t in node.targets):
   try:value=ast.literal_eval(node.value)
   except(ValueError,TypeError):continue
   for target in node.targets:scope[target.id]=value
 function=next(n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name=='read_numeric');exec(compile(ast.Module(body=[function],type_ignores=[]),str(file)+':stdlib_reader_only','exec'),scope)
 return scope['read_numeric'],ref(file)
def load_clock():
 file=H/'pi09_aritmetica_temporal_P0_R01.py';need(sha(file)=='ebff5dbe0d3b85000a33b7f789a72688e7c24c0151076558a01e32a803824656','Frozen clock helper differs');sp=importlib.util.spec_from_file_location('PI09_pure_clock_panel_validation',file);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);return m
def phase(proof_path,plan_path,numeric,clock):
 proof=read(proof_path);plan=read(plan_path);need(proof.get('schema')=='DEE.PI09.actual.finite_owner_plan.R02'and proof.get('status')=='CLOSED_FINITE_PHASE'and proof.get('closed')is True and proof.get('error')is None,'Closed complete finite actual panel required')
 need(proof['life_id']==plan['life_id']and proof['plan_sha256']==sha(plan_path)and proof['initial_tick']==plan['initial_tick']==903603 and proof['finite_bound']==sum(s['max_ticks']for s in plan['steps']),'Actual plan/source/bound differs')
 need(len(proof['records'])==len(plan['steps'])==18 and proof['protected_before']==proof['protected_after'],'Exactly eighteen actual records and unchanged principal required')
 result=[];prior={};requests={};cursor=903603
 for index,(record,step)in enumerate(zip(proof['records'],plan['steps'])):
  need(record['index']==index and record['label']==step['label']and record['id']==plan['tag']+'_%03d'%index,'Fixed record sequence differs')
  literal=dict(step['literal'])
  if step.get('clock_alignment'):
   wait=clock.challenge_wait(cursor,True);literal['espera_previa']=wait;align=record['clock_alignment'];need(align['source_actual_tick']==cursor and align['legal_wait_ticks']==wait and align['unchanged_nominal_query']==clock.query(cursor+wait,True)and align['unchanged_nominal_query']%67==19 and align['expected_values_or_outcomes_used']is False,'Clock-only predeclared alignment differs')
  binding=step.get('actual_integer_binding')
  if binding:
   value=prior[binding['from_step']];need(type(value)is int,'A formed previous actual integer must be transported');literal[binding['field']]=value
  need(record['literal']==literal and record['before_tick']==cursor and record['ticks']==record['after_tick']-cursor and 0<=record['ticks']<=step['max_ticks'],'Actual literal/calendar/bound differs')
  file=Path(record['primary']).resolve(strict=True);need(file.parent==(P/'ensayos').resolve()and sha(file)==record['sha256'],'Actual primary hash/path differs')
  outer=read(file);need(outer['id']==record['id']and outer['status']=='completed','Primary is not the same completed request');value=json.loads(outer['result'])if isinstance(outer['result'],str)else outer['result'];payload=json.loads(outer['payload'])if isinstance(outer['payload'],str)else outer['payload']
  need(payload=={'operacion':'sesion','situaciones':[literal],'actuador':step.get('actuator','closed'),'retorno':step.get('feedback','real')},'Actual transport payload differs from fixed material input')
  need(value['before_tick']==cursor and value['after_tick']==record['after_tick'],'Primary physical boundaries differ');cursor=record['after_tick'];actual=at(value,step['read_path'])if step.get('read_path')else None
  raw_check=None;row=value['result']['rows'][0]
  if literal['modo']in('eci01-aritmetica-directa','eci01-pi09-aritmetica-temporal'):
   reader=row['numeric_reader'];RAW(reader['observation']);trial=row['native_operation']['native_trial'];decoded=numeric(trial,literal['operacion']);need(decoded==reader and decoded['numeric_result']==actual and type(decoded['numeric_result'])is type(actual),'Frozen RAW numeric decoding differs')
   need(row['literal_operator_request']==literal,'Numeric input differs from actual transported operands')
   if literal['modo']=='eci01-pi09-aritmetica-temporal':
    prediction=clock.forecast(value['before_tick'],literal['espera_previa'],literal['guardia_temporal'],True);need(row['forecast']==prediction and trial['query_tick']==prediction['query_tick']and row['P0_guard_paid_ticks']==prediction['guard_paid_ticks'],'Fixed P0 forecast/paid legal wait differs')
   raw_check={'kind':'exact_frozen_numeric_RAW_reader','raw':reader['observation']['raw'],'valid':reader['fixed_site_direction_valid'],'decoded':decoded['numeric_result'],'bias':decoded['representation_bias']}
  elif literal['modo']=='eci01-pi07-fi-regulada':
   old=row['FI']['legacy_result'];o=old['early_observation'];f=RAW(o);x,y,z=f['direction'];valid=f['state']>0 and f['semantic']==1 and x in(-1,0,1)and y==1 and z in(0,-1);decoded=x if valid else None
   need(o['site']==[15,15,15]and o['tick']==old['early_tick']==old['query_tick']+4 and decoded==actual and type(decoded)is type(actual),'Frozen earlyq4 FI RAW reader differs')
   raw_check={'kind':'exact_early_q4_FI_RAW_reader','raw':o['raw'],'valid':valid,'decoded':decoded}
  step_ids={}
  for path in step.get('receipt_paths',[]):
   items=at(value,path);need(isinstance(items,list),'Fixed direct receipt path must be list')
   for request in items:
    receipt=request['receipt'];rid=request['id'];need(type(rid)is int and receipt['id']==rid,'Native receipt identity differs')
    if rid in requests:need(requests[rid]==receipt,'Contradictory receipt aliases')
    requests[rid]=receipt;step_ids[rid]=receipt
  need(all(r['status']=='applied'or r['status'].startswith('rejected')for r in step_ids.values()),'Unknown/pending Native receipt cannot close conservation')
  correct=type(actual)is type(step.get('expected'))and actual==step.get('expected')if'read_path'in step else None
  if'read_path'in step:need(record.get('actual')==actual and type(record.get('actual'))is type(actual),'Driver response differs from literal primary');prior[step['label']]=actual
  result.append({'label':step['label'],'actual':actual,'expected_auditor_only':step.get('expected'),'correct':correct,'NULL_is_not_zero':True,'RAW_recheck':raw_check,'direct_Native_requested':len(step_ids),'direct_Native_applied':sum(r['status']=='applied'for r in step_ids.values()),'direct_Native_rejected':sum(r['status'].startswith('rejected')for r in step_ids.values()),'primary':ref(file),'ticks':record['ticks'],'clock_alignment':record['clock_alignment']})
 need(cursor==proof['final_tick']and proof['new_Native_ticks']==cursor-903603,'Final actual boundary differs')
 by={r['label']:r for r in result};return {'life_id':proof['life_id'],'closed':True,'proof':ref(proof_path),'plan':ref(plan_path),'initial_tick':903603,'final_tick':cursor,'new_Native_ticks':cursor-903603,'records':result,'published_correct':sum(by[k]['correct']is True for k in WORDS+SIGNED+('number13','number8')),'published_denominator':12,'words_context_correct':sum(by[k]['correct']is True for k in WORDS),'signed_FI_correct':sum(by[k]['correct']is True for k in SIGNED),'fresh_correct':sum(r['correct']is True for r in result if r['label'].startswith('CHALLENGE_')),'fresh_denominator':5,'arithmetic_causal_chain':{'first_actual':by['number13']['actual'],'second_actual':by['number8']['actual'],'second_input_is_first_actual':True,'not_two_independent_losses':True},'Native_receipts':{'unique_requested':len(requests),'applied':sum(r['status']=='applied'for r in requests.values()),'rejected':sum(r['status'].startswith('rejected')for r in requests.values())}}
def calculate(panel_path,discovery_path):
 need(sha(GATE)==GATE_SHA,'Prospective functional gate changed');gate=read(GATE)
 for item in[gate['protocol'],gate['source_seal'],*gate['plans']]:need(sha(Path(item['file']))==item['sha256'],'Prospective protocol/seal/plan changed')
 numeric,reader_ref=frozen_numeric();clock=load_clock();legacy=phase(panel_path,H/'PLAN_PANEL_P0_R01.json',numeric,clock);guard=phase(discovery_path,H/'PLAN_DISCOVERY_P0_R01.json',numeric,clock)
 fresh=guard['fresh_correct']==5;gain=guard['fresh_correct']-legacy['fresh_correct'];not_worse=guard['published_correct']>=legacy['published_correct'];core=guard['words_context_correct']==7 and guard['signed_FI_correct']==3
 return {'schema':'DEE.PI09.closed_panels_and_prospective_P0_gate.validation.R01','Native_executed':False,'DEE_imports':0,'closed':True,'error':None,'prospective_gate':ref(GATE),'numeric_reader_source':reader_ref,'legacy':legacy,'guard':guard,'P0_public_access_gate':{'satisfied':fresh and gain>=2 and not_worse,'fresh5of5':fresh,'absolute_gain':gain,'minimum_gain':2,'published_conservation_not_worse':not_worse},'minimum_previous_function_gate':{'satisfied':core,'learned_word_context7of7':guard['words_context_correct']==7,'signed_FI3of3':guard['signed_FI_correct']==3,'direct_arithmetic_partial_loss_is_separate_reported_chain':True},'approval':False,'adoption_not_performed':True,'scope':'Only actual closed primaries at frozen paths/readers. P0 access is engineering, not Native learned regulation. Native conditional-information gain and other adoption gates remain the separate C2 actual evaluation.'}
def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--panel',type=Path,required=True);ap.add_argument('--discovery',type=Path,required=True);ap.add_argument('--salida',type=Path,required=True);a=ap.parse_args();out=a.salida.resolve();need(out.is_relative_to((P/'control').resolve())and not out.exists(),'Fresh control output required');result=calculate(a.panel.resolve(strict=True),a.discovery.resolve(strict=True));out.parent.mkdir(parents=True,exist_ok=True)
 with out.open('x',encoding='utf8')as f:json.dump(result,f,ensure_ascii=False,indent=2);f.write('\n')
 print(json.dumps({'proof':str(out),'sha256':sha(out),'P0_gate':result['P0_public_access_gate'],'minimum_previous_function':result['minimum_previous_function_gate'],'Native_executed':False}))
if __name__=='__main__':main()
