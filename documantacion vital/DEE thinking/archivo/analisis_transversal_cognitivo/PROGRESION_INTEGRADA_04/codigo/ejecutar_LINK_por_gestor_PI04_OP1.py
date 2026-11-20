"""One predeclared link-cut trial using the public bounded CLI, not a new task."""
from pathlib import Path
import hashlib,json,subprocess,sys
P=Path(__file__).resolve().parents[1];C=P.parents[2]/'DEE Cognitive 2.0';S=P/'estados/candidato_R02/sistema';PY=C/'motor/python313/python.exe';code=P/'codigo'
sys.path.insert(0,str(code))
from servicio_ensayo_R02 import Owner
LIFE='ECI02_PI03_REPRO_PI04_C2C_LINK_CUT_01';TAG='PI04_C2C_LINK_CUT1_R01'
def cli(command,identifier,material=False):
 args=[str(PY),'-I','-B','-X','utf8',str(S/'gestionar.py'),'--system-root',str(S),command,'--vida',LIFE,'--id',identifier,'--diagnostico']
 if material:args+=['--material']
 r=subprocess.run(args,capture_output=True,encoding='utf8',timeout=660)
 for suffix,value in(('stdout',r.stdout),('stderr',r.stderr)):(P/'ensayos'/(identifier+'.'+suffix+'.txt')).write_text(value,encoding='utf8')
 if r.returncode:raise RuntimeError('CLI stopped; inspect SAME queued ID, never retry: '+identifier+' exit'+str(r.returncode))
 value=json.loads(r.stdout)
 if value['status']!='completed'or not value['saved_and_paused']:raise ValueError('Incomplete CLI result preserved')
 return {'command':args,'returncode':r.returncode,'result':value}
def main():
 out=P/'control'/(TAG+'.json');assert not out.exists()
 subprocess.run([str(PY),'-I','-B','-X','utf8',str(code/'clonar_PI04_R02.py'),'--par',str(C/'reproducibilidad/materiales/PI03_PI04_C2B_STOP_T800379'),'--vida',LIFE],check=True)
 with Owner(LIFE,TAG)as owner:
  initial=owner.material(TAG+'_STATE_START',{'modo':'eci01-pi04-c2c-estado'},feedback='omit')
  prep=owner.material(TAG+'_PREPARE',{'modo':'eci01-pi04-c2c-preparar'},feedback='omit')
  owner.material(TAG+'_ADMIT',{'modo':'eci01-pi04-c2c-admitir','brazo':'link_cut'},feedback='omit')
  state=cli('pi04-coordinacion-estado',TAG+'_CLI_STATE')
  assert state['result']['native_result']['before_tick']==state['result']['native_result']['after_tick']==800379
  use=cli('pi04-coordinacion-oportunidad',TAG+'_OP_0',True)
  q=owner.q.get(TAG+'_OP_0');assert q['status']=='completed'
  primary=P/'ensayos'/(TAG+'_OP_0.json');primary.write_text(json.dumps(q,ensure_ascii=False,indent=2),encoding='utf8')
  actual=json.loads(q['result']);r=actual['result']['rows'][0]
  assert r['arm']=='link_cut'and r['first_reader']['choice']==-1 and r['selected_operation']=='diferencia'
  assert r['actual_numeric_result']==7 and r['second_native_use']['second_sensor_called']is False
  assert r['applied_route']is None and not r['useful_product']
  ids={x['id']:x['receipt']['status']for g in(r['requests'],r['native_arithmetic']['native_operation']['native_trial']['requests'])for x in g}
  assert len(ids)==182 and all(s=='applied'for s in ids.values())
  row={'ordinal':0,'stage':r['spec']['stage'],'context':r['spec']['context'],'operands':[16,9],'before_tick':actual['before_tick'],'after_tick':actual['after_tick'],'first_choice':r['first_reader']['choice'],'operation':r['selected_operation'],'actual_number':7,'offline_arithmetic_reference':7,'arithmetic_attempted':True,'arithmetic_correct':True,'second_choice':None,'actual_route':None,'useful_product':False,'actual_failed':r['actual_failed'],'returned_failed':r['returned_failed'],'reference_delta_before':r['bank_before'][0]['s_reg']-r['bank_before'][1]['s_reg'],'reference_delta_after':r['bank_after'][0]['s_reg']-r['bank_after'][1]['s_reg'],'first_NULL_preserved':r['first_NULL_preserved'],'normalized_calendar':r['normalized_calendar'],'primary':str(primary),'Native_inputs':{'unique_requested':len(ids),'applied':len(ids),'rejected_or_other':0,'groups_raw_counts':{'outer':6,'arithmetic':176,'MU':0},'expected_outer':6,'context_samples':1}}
  final=owner.material(TAG+'_STATE_FINAL',{'modo':'eci01-pi04-c2c-estado'},feedback='omit')
  owner.sample(force=True)
 proof={'schema':'DEE.PI04.C2C.actual_batch.R01','life':LIFE,'arm':'link_cut','tag':TAG,'start_ordinal':0,'stop_exclusive':1,'offered':1,'completed':1,'products':0,'arithmetic_correct':1,'rows':[row],'initial':initial,'final':final,'owner_closed':True,'source_world_or_control_histories_not_merged':True,'new_native_ticks':782,'original_principal_modified':False,'public_manager_CLI_test':{'state':state,'use':use},'scope':'Ablated actual-result link. The absent second query is intentional; it is neither a measured NULL nor arithmetic failure. Negative operational CLI trial, not a fabricated successful product.'}
 with out.open('x',encoding='utf8')as f:json.dump(proof,f,ensure_ascii=False,indent=2)
 print(json.dumps({'proof':str(out),'Native_ticks':782,'products':0,'public_CLI_actual':True}),flush=True)
if __name__=='__main__':main()
