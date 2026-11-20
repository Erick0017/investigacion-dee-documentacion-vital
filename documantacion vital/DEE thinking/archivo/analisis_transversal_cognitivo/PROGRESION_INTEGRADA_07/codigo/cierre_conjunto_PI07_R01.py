"""Root-only finite final integration. Import/default never runs Native."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,hashlib,importlib.util,json,os,sys
P=Path(__file__).resolve().parents[1];S=P/'estados/candidato/sistema'
C=P.parents[2]/'DEE Cognitive 2.0'
LIFE='ECI02_PI03_REPRO_PI04_PI05_PI07_CAND_01'
MAIN='ECI02_PI03_REPRO_PI04_PI05_MAIN_01'
PLAN=P/'control/PLAN_CIERRE_CONJUNTO_PI07_R01.json'
RESULT=P/'control/CIERRE_CONJUNTO_MATERIAL_PI07_R01.json'

def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def req(ok,msg):
 if not ok:raise ValueError(msg)
def driver():
 spec=importlib.util.spec_from_file_location('closed_PI07_budget_reader',P/'codigo/ejecutar_plan_PI07_R01.py')
 mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);return mod
def row(value):return value['result']['rows'][0]
def write(p,v):
 with p.open('x',encoding='utf-8')as f:json.dump(v,f,ensure_ascii=False,indent=2);f.write('\n')

def seal():
 req(not PLAN.exists(),'Existing sealed final plan is immutable')
 previous=P/'control/C2C_CONSERVACION_VERIFICADA_PI07_R03.json'
 v=read(previous)
 req(v.get('closed')and v.get('material_success')and v.get('opportunities')==2 and v.get('products')==2,
     'Both actual old C2C offers28/29 must have succeeded before final supply')
 card=read(S/'estado/vidas'/LIFE/'VIDA.json');req(card['physical']['tick']==v['final_tick'],'A newer candidate exists; re-evaluate, no stale plan')
 panel=P/'control/PI07_PANEL_ACCESO_R02.json';pr=read(panel)
 req(pr['closed']and pr['criteria_met']and pr['correct']==pr['tested']==12,'Actual new conservation12 required')
 plan={'schema':'DEE.PI07.final_combined_material.fixed.v1','status':'SEALED_BEFORE_FINAL_USES',
  'registration_utc':datetime.now(timezone.utc).isoformat(),'life_id':LIFE,'initial_tick':v['final_tick'],
  'max_Native_ticks':2800,'source_proofs':[{'file':str(f),'sha256':sha(f)}for f in(previous,panel)],
  'dependencies':[{'file':str(f),'sha256':sha(f)}for f in(P/'codigo/PROTOCOLO_PI07_R03.json',P/'codigo/PROTOCOLO_PI07_C2C_34_R01.json',Path(__file__))],
  'phases':[{'label':'supply_and_C2C30','max_Native_ticks':1500,'steps':[
    {'label':'supply','literal':{'modo':'eci01-pi07-c2c-ampliar'},'max_Native_ticks':0},
    {'label':'C2C30','literal':{'modo':'eci01-pi04-c2c-oportunidad'},'max_Native_ticks':1500}]},
    {'label':'new_owner_after_close_R03_16','max_Native_ticks':1300,'steps':[
    {'label':'EP16','literal':{'modo':'eci01-pi07-r03-episodio'},'max_Native_ticks':1300}]}],
  'invariants':{'R03_start_ordinal':16,'R03_final_ordinal':17,'R03_remaining':1,'C2C_start_ordinal':30,
    'C2C_final_ordinal':31,'C2C_resources':34,'C2C_remaining':3,'no_reset':True},
  'scope':'Public environmental supply and two actual Native uses, separated by coherent close/reopen. Not a new learned sequence or an adoption approval. Every failed or uncertain future is preserved without retry.'}
 write(PLAN,plan);print(json.dumps({'plan':str(PLAN),'sha256':sha(PLAN),'initial_tick':plan['initial_tick'],'new_Native_ticks':0}));return 0

def execute():
 plan=read(PLAN);literal=PLAN.read_bytes()
 req(plan['schema']=='DEE.PI07.final_combined_material.fixed.v1'and plan['status']=='SEALED_BEFORE_FINAL_USES','Exact sealed plan required')
 for f in plan['source_proofs']+plan['dependencies']:req(sha(Path(f['file']))==f['sha256'],'Changed source/dependency')
 req(not RESULT.exists(),'Final proof/tag already used; no retry')
 d=driver();campaign=read(P/'REGISTRO_CAMPANA.json');ticks,lives=d.ledger()
 req(ticks+2800<=campaign['budget']['Native_ticks_all_branches']and len(lives)<=14,'Campaign finite resource bound')
 cutoff=datetime.fromisoformat(campaign['science_cutoff_local']).astimezone(timezone.utc)
 req(datetime.now(timezone.utc)<cutoff,'Science deadline reached')
 req(not(S/'estado/ACTIVO.json').exists(),'No principal in diagnostic store')
 req(not(C/'reproducibilidad/EJECUCION_MATERIAL.lock').exists(),'Another material RP owner')
 locks=S/'estado/locks';req(not locks.exists()or not any(locks.iterdir()),'Scoped Native owner remains')
 writer=P/'PI07_ROOT_NATIVE_WRITER.lock';req(not writer.exists(),'Another campaign writer')
 cardfile=S/'estado/vidas'/LIFE/'VIDA.json';card=read(cardfile)
 req(card['physical']['N']==67 and card['physical']['tick']==plan['initial_tick'],'Exact current candidate cut required')
 active=C/'sistema/estado/ACTIVO.json';maincard=C/'sistema/estado/vidas'/MAIN/'VIDA.json'
 protectedcard=read(maincard);req(read(active)['life_id']==MAIN and protectedcard['physical']['tick']==824911,'Protected principal advanced')
 critical=[active,maincard,C/'sistema'/protectedcard['snapshot']];protected={str(f):sha(f)for f in critical}
 write(writer,{'pid':os.getpid(),'life_id':LIFE,'plan_sha256':sha(PLAN)})
 rows=[];phases=[];error=None;owners=[];lasttick=plan['initial_tick']
 sys.path.insert(0,str(P/'codigo'));from servicio_ensayo_PI07 import Owner
 def call(owner,label,literal,max_ticks):
  req(datetime.now(timezone.utc)<cutoff,'Science cutoff between material uses')
  value=owner.material('PI07_CIERRE_CONJUNTO_'+label,literal,feedback='real',actuator='closed',allow_failure=True)
  primary=P/'ensayos'/('PI07_CIERRE_CONJUNTO_'+label+'.json')
  rec={'label':label,'primary':str(primary),'sha256':sha(primary),'before_tick':value.get('before_tick'),'after_tick':value.get('after_tick')};rows.append(rec)
  req('before_tick'in value and'after_tick'in value,'Incomplete transport future; preserve without retry')
  req(0<=value['after_tick']-value['before_tick']<=max_ticks,'Actual step exceeds finite Native bound')
  req(PLAN.read_bytes()==literal_plan,'Sealed plan changed')
  return value
 def states(owner,suffix,c2c_ordinal,r3_ordinal,resources):
  c=call(owner,'C2Cstate_'+suffix,{'modo':'eci01-pi04-c2c-estado'},0);cv=row(c)
  req(cv['progress']['ordinal']==cv['device']['ordinal']==c2c_ordinal and len(cv['device']['resources'])==resources,'C2C actual progress differs')
  req(not any(cv['device'].get(k)for k in('pending','feedback_pending','uncertain')),'C2C future pending')
  r=call(owner,'R03state_'+suffix,{'modo':'eci01-pi07-r03-estado'},0);rv=row(r)['progress']
  req(rv['ordinal']==r3_ordinal and not rv.get('pending')and not rv.get('uncertain'),'R03 actual progress differs')
  return cv,rv
 literal_plan=literal
 try:
  for i,phase in enumerate(plan['phases']):
   owner=Owner(LIFE,'PI07_CIERRE_CONJUNTO_FASE'+str(i));owners.append(owner)
   with owner:
    states(owner,'pre'+str(i),30 if i==0 else 31,16,30 if i==0 else 34)
    for step in phase['steps']:
     v=call(owner,step['label'],step['literal'],step['max_Native_ticks']);r=row(v)
     if step['label']=='supply':
      req(r['ready']and r['new_native_ticks']==0 and r['ordinal_before']==r['ordinal_after']==30 and r['resources_after']==34 and r['original_rows_products_rejections_preserved'],'Explicit append-only supply failed')
      req(r['Native_physical_before']==r['Native_physical_after'],'Supply changed Native causal state')
     elif step['label']=='C2C30':
      q=r['native_input_summary'];req(r['ordinal']==30 and q['rejected']==q['pending_or_other']==0 and q['all_terminal'],'C2C material inputs rejected/pending')
      req(r['useful_product']is True and type(r['actual_numeric_result'])is int,'C2C actual useful product absent')
      product=r['actual_effect']['product'];productpath=S/'estado/servicios_locales'/LIFE/'PI04_C2C_COORDINACION_R01/dispositivo'/product['path'];d.regular(productpath);data=productpath.read_bytes()
      req(len(data)==product['bytes']==64 and sha(productpath)==product['sha256']and int.from_bytes(data[:2],'little')==r['actual_numeric_result'],'Real C2C product not actual Native number')
     else:
      req(r['ordinal']==16 and r['reader']['choice']is not None,'R03 final selector NULL')
      req(r['FI']['early_physical_choice']==r['FI']['old_q6_choice']==1 and not r['actual_failed'],'R03 final actual useful protection failed')
      req(r['pulse_applied']is True,'Actual final R03 protection pulse required, not a favorable no-pulse phase')
      direct={x['id']:x['receipt']for x in r['requests']};req(all(x['status']=='applied'for x in direct.values()),'R03 material admission failed')
     lasttick=v['after_tick']
    states(owner,'post'+str(i),31,16 if i==0 else 17,34)
    owner.control('guardar')
   okay=owner.proc.poll()==0 and not(owner.q.get_meta('owner')or{}).get('running')
   phases.append({'phase':phase['label'],'owner_pid':owner.proc.pid,'owner_returncode':owner.proc.poll(),'closed':okay,'last_tick':read(cardfile)['physical']['tick']})
   req(okay,'Owner did not close coherently; no next writer')
  req(all(sha(f)==protected[str(f)]for f in critical),'Protected principal changed; never overwrite')
 except Exception as exc:error={'type':type(exc).__name__,'message':str(exc),'automatic_retry':False}
 final=read(cardfile);closed=all(o.proc is not None and o.proc.poll()==0 and not(o.q.get_meta('owner')or{}).get('running')for o in owners)
 proof={'schema':'DEE.PI07.final_combined_material.actual.v1','at_utc':datetime.now(timezone.utc).isoformat(),'life_id':LIFE,
  'status':'COMPLETED_FINAL_INTEGRATION'if error is None and closed else'FAILED_PRESERVED','closed':closed,'criteria_met':error is None and closed,
  'initial_tick':plan['initial_tick'],'final_tick':final['physical']['tick'],'new_Native_ticks':final['physical']['tick']-plan['initial_tick'],
  'plan':str(PLAN),'plan_sha256':sha(PLAN),'rows':rows,'owner_phases':phases,'error':error,
  'remaining_resources_if_pass':{'C2C':3,'R03':1}if error is None and closed else None,
  'protected_main_before':protected,'protected_main_after':{str(f):sha(f)for f in critical},
  'no_adoption_by_this_runner':True,'no_reset_or_memory_merge':True}
 write(RESULT,proof)
 if closed and read(writer)['pid']==os.getpid():writer.unlink()
 print(json.dumps({'proof':str(RESULT),'sha256':sha(RESULT),'status':proof['status'],'closed':closed,'final_tick':final['physical']['tick'],'error':error}));return 0 if proof['criteria_met']else 2

def main():
 parser=argparse.ArgumentParser();g=parser.add_mutually_exclusive_group();g.add_argument('--sellar',action='store_true');g.add_argument('--ejecutar',action='store_true');a=parser.parse_args()
 if a.sellar:return seal()
 if a.ejecutar:return execute()
 print(json.dumps({'Native_executed':False,'new_ticks':0,'plan':str(PLAN),'sequence':'supply0 + C2C30 <=1500, close/reopen, R03 EP16 <=1300','remaining_if_actual_pass':{'C2C':3,'R03':1}}));return 0

if __name__=='__main__':raise SystemExit(main())
