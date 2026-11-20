"""External fixed RP budget guard; actual manager/RP/driver stay literal.

Wrap only their exact subprocess launch and Owner.material admission. No
reader, literal, Native action, feedback or expected response is changed.
"""
from pathlib import Path
from datetime import datetime,timezone
import argparse,hashlib,importlib.util,json,os,runpy,subprocess,sys
P=Path(__file__).resolve().parents[1];C=P.parents[2]/'DEE Cognitive 2.0';RP=C/'reproducibilidad';PY=C/'motor/python313/python.exe';SELF=Path(__file__).resolve()
DEST=P/'estados/RP_FAMILIA_R04_R01';LIFE='ECI02_PI03_REPRO_PI04_PI05_PI07_PI09_RPF_20261111A';RID='pi09_consulta_native12_familia_desde_C_R04';VARIANT='native12'
RECIPE_SHA='8054297bdd57e1203a0e2f5b8e89261ba43f5c6f0e15e38ec65cafc8e088f052';INITIAL=884835;STEP_BOUND=2280;BOUND=12*STEP_BOUND
LOG=P/'control/GUARDIA_DRIVER_RP_FAMILIA_PI09_R04.json';LEDGER=P/'codigo/ledger_PI09_misma_identidad_R01.py';LEDGER_SHA='bb1f326aa981ba00b9a6e3417700cca31d92a0d28a6e8a5ad601042bf2a26260'
def need(ok,msg):
 if not ok:raise ValueError(msg)
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def record(value):
 temp=LOG.with_name(LOG.name+'.WRITING')
 with temp.open('w',encoding='utf8')as f:json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
 os.replace(temp,LOG)
def command_arguments():return ['reproducir',RID,'--variante',VARIANT,'--vida',LIFE,'--destino',str(DEST),'--material']
def load_ledger():
 need(sha(LEDGER)==LEDGER_SHA,'Changed same-identity ledger')
 sp=importlib.util.spec_from_file_location('PI09_cold12_guard_ledger',LEDGER);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);return m
def allowance(step):return STEP_BOUND if step['literal']['modo']=='eci01-pi09-episodio'else 0
def main(a):
 need(Path(sys.executable).resolve()==PY.resolve(),'Root official Python required')
 need(sha(RP/'recetas'/(RID+'.json'))==RECIPE_SHA,'Exact registered prospective recipe required')
 budget=read(P/'REGISTRO_CAMPANA.json')['budget'];deadline=datetime.fromisoformat(budget['new_experimental_uses_cutoff_local']).astimezone(timezone.utc)
 need(datetime.now(timezone.utc)<deadline,'Research cutoff reached; no new material input')
 saved_run=subprocess.run
 def guarded_run(command,*pos,**kw):
  need(isinstance(command,(list,tuple)),'Only explicit list commands')
  expected=RP/('reproducir.py'if a.stage=='manager'else'ejecutar_diagnostico.py');positions=[i for i,v in enumerate(command)if str(v)==str(expected)]
  if positions:
   need(len(positions)==1 and Path(command[0]).resolve()==PY.resolve(),'Exact existing RP subprocess required');index=positions[0];rest=list(command[index+1:]);nextstage='rp'if a.stage=='manager'else'driver'
   need(rest==(command_arguments()if nextstage=='rp'else['--contexto',str(DEST/'CONTEXTO_EJECUCION.json')]),'RP/context literal arguments changed')
   command=[str(PY),'-I','-B','-X','utf8',str(SELF),'--stage',nextstage]
  else:need(a.stage=='rp'and str(RP/'importar_diagnostico.py')in list(map(str,command))and list(command)[-2:]==['--contexto',str(DEST/'CONTEXTO_EJECUCION.json')],'No additional process/provider in fixed RP guard')
  return saved_run(command,*pos,**kw)
 if a.stage in('manager','rp'):
  subprocess.run=guarded_run;script=C/'sistema/gestionar.py'if a.stage=='manager'else RP/'reproducir.py';sys.argv=[str(script)]+(['reproducibilidad']if a.stage=='manager'else[])+command_arguments();runpy.run_path(str(script),run_name='__main__');return
 context=read(DEST/'CONTEXTO_EJECUCION.json')
 need(context['life']==LIFE and context['recipe']==RID and context['variant']==VARIANT and context['recipe_sha256']==RECIPE_SHA and context['prefix_manifest_sha256']=='08a8e65deb2071b7653bc0ab95f3d55b8038191a4f585c6803f6d81c16e8182f','Fixed complete C-prefix context required')
 steps=context['fixed_recipe']['variants'][VARIANT]['batches'][0];need(len(steps)==14 and sum(allowance(s)for s in steps)==BOUND and not LOG.exists(),'Fixed PREPARE/12EP/STATE sequence and fresh guard output required')
 sp=importlib.util.spec_from_file_location('propietario_diagnostico',RP/'propietario_diagnostico.py');service=importlib.util.module_from_spec(sp);sys.modules['propietario_diagnostico']=service;sp.loader.exec_module(service);original=service.Owner.material
 ledger=load_ledger();index=0;last_tick=INITIAL
 state={'schema':'DEE.PI09.RP.family_external_per_request_guard.R04','status':'RUNNING','guard_sha256':sha(SELF),'published_driver':str(RP/'ejecutar_diagnostico.py'),'published_driver_sha256':sha(RP/'ejecutar_diagnostico.py'),'recipe_sha256':RECIPE_SHA,'Native_bound':BOUND,'per_episode_bound':STEP_BOUND,'initial_tick':INITIAL,'deadline_utc':deadline.isoformat(),'rows':[],'actor_literals_or_readers_modified':False,'expected_values_passed_to_actor':False};record(state)
 def material(owner,identifier,literal,*pos,**kw):
  nonlocal index,last_tick
  need(index<len(steps),'No extra material operation');step=steps[index];need(identifier==LIFE+'_'+step['label']and literal==step['literal'],'Exact fresh fixed transport/literal sequence required')
  need(kw.get('feedback','omit')==step.get('feedback','omit')and kw.get('actuator','closed')==step.get('actuator','closed'),'Fixed feedback/actuator settings changed')
  need(datetime.now(timezone.utc)<deadline,'Deadline reached before next material input; preserve/close')
  stock=ledger.ledger();own=stock['worlds'].get(LIFE,{});counted=own.get('ticks',0);known=last_tick-INITIAL;total=stock['ticks']-counted+max(counted,known);remaining=sum(allowance(s)for s in steps[index:])
  need(stock['world_count']<=budget['diagnostic_worlds_all_new']and total+remaining<=budget['Native_ticks_all_branches'],'All-branch saved/known ticks plus remaining conservative bound do not fit')
  value=original(owner,identifier,literal,*pos,**kw);before,after=value['before_tick'],value['after_tick'];limit=allowance(step)
  state['rows'].append({'label':step['label'],'id':identifier,'literal':literal,'before_tick':before,'after_tick':after,'actual_ticks':after-before,'max_ticks':limit,'global_known_ticks_before':total,'remaining_conservative_bound_before':remaining,'worlds_before':stock['world_count'],'deadline_checked_before':True});record(state)
  need(before==last_tick and 0<=after-before<=limit and after-INITIAL<=BOUND,'Unexpected gap/bound exceeded; actual future preserved, never repeat')
  last_tick=after;index+=1;return value
 service.Owner.material=material;sys.argv=[str(RP/'ejecutar_diagnostico.py'),'--contexto',str(DEST/'CONTEXTO_EJECUCION.json')]
 try:runpy.run_path(str(RP/'ejecutar_diagnostico.py'),run_name='__main__')
 except SystemExit as exc:
  state.update(status='COMPLETED_DRIVER'if exc.code in(None,0)and index==len(steps)else'STOPPED_PRESERVED',exit_code=exc.code,completed_material_requests=index,final_tick=last_tick,new_Native_ticks=last_tick-INITIAL);record(state);raise
 except BaseException as exc:
  state.update(status='STOPPED_PRESERVED',error=repr(exc),completed_material_requests=index,final_tick=last_tick,new_Native_ticks=last_tick-INITIAL,automatic_retry=False);record(state);raise
if __name__=='__main__':
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--stage',choices=('manager','rp','driver'),required=True);main(ap.parse_args())
