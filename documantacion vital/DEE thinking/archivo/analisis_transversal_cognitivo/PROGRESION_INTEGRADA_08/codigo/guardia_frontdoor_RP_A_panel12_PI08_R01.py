"""Fixed external transport/budget guard; all published RP scripts stay literal.

Each stage executes the ACTUAL manager/RP/driver using runpy. Only their exact
next subprocess launch is wrapped. No actor input, reader or feedback changes.
The driver guard checks deadline and fixed bounds before each material request.
"""
from pathlib import Path
from datetime import datetime,timezone
import argparse,hashlib,importlib.util,json,os,runpy,subprocess,sys
P=Path(__file__).resolve().parents[1];C=P.parents[2]/'DEE Cognitive 2.0';RP=C/'reproducibilidad';PY=C/'motor/python313/python.exe'
SELF=Path(__file__).resolve();DEST=P/'estados/RP_A_PANEL12_R01'
LIFE='ECI02_PI03_REPRO_PI04_PI05_PI07_PI08_ARP_PANEL12_01'
RID='pi08_a_panel12_regulado_T861426_R01';VARIANT='panel12_sin_c2c';BOUND=8684
RECIPE_SHA='54fd4318d8ac25d999c632876715ecd0799b23e7e291ea4c32b7e2b6b8782700'
LOG=P/'control/GUARDIA_DRIVER_RP_A_PANEL12_PI08_R01.json'
DEADLINE=datetime.fromisoformat('2026-11-10T18:38:46-06:00').astimezone(timezone.utc)
def require(ok,message):
 if not ok:raise ValueError(message)
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def record(value):
 temp=LOG.with_name(LOG.name+'.WRITING')
 with temp.open('w',encoding='utf8')as f:json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
 os.replace(temp,LOG)
def command_arguments():return['reproducir',RID,'--variante',VARIANT,'--vida',LIFE,'--destino',str(DEST),'--material']
def main(args):
 require(Path(sys.executable).resolve()==PY.resolve(),'Root official Python required')
 require(sha(RP/'recetas'/(RID+'.json'))==RECIPE_SHA,'Exact prospective recipe required')
 require(datetime.now(timezone.utc)<DEADLINE,'No new Native phase after research deadline')
 saved_run=subprocess.run
 def guarded_run(command,*pos,**kw):
  require(isinstance(command,(list,tuple)),'Only fixed list subprocess commands')
  expected=RP/('reproducir.py'if args.stage=='manager'else'ejecutar_diagnostico.py')
  positions=[i for i,x in enumerate(command)if str(x)==str(expected)]
  if positions:
   require(len(positions)==1 and Path(command[0]).resolve()==PY.resolve(),'Exact preserved RP subprocess expected')
   index=positions[0];rest=list(command[index+1:]);nextstage='rp'if args.stage=='manager'else'driver'
   require(rest==(command_arguments()if nextstage=='rp'else['--contexto',str(DEST/'CONTEXTO_EJECUCION.json')]),'Fixed RP/context arguments changed')
   command=[str(PY),'-I','-B','-X','utf8',str(SELF),'--stage',nextstage]
  else:
   require(args.stage=='rp'and str(RP/'importar_diagnostico.py')in list(map(str,command))and list(command)[-2:]==['--contexto',str(DEST/'CONTEXTO_EJECUCION.json')],'No additional process/provider in guarded frontdoor')
  return saved_run(command,*pos,**kw)
 if args.stage in('manager','rp'):
  subprocess.run=guarded_run
  script=C/'sistema/gestionar.py'if args.stage=='manager'else RP/'reproducir.py'
  sys.argv=[str(script)]+(['reproducibilidad']if args.stage=='manager'else[])+command_arguments()
  runpy.run_path(str(script),run_name='__main__');return
 context=read(DEST/'CONTEXTO_EJECUCION.json')
 require(context['life']==LIFE and context['recipe']==RID and context['variant']==VARIANT and context['recipe_sha256']==RECIPE_SHA,'One fixed imported diagnostic context')
 require(context['prefix_manifest_sha256']=='dfadc5037b804f3c6112263eb0af84f6215d53fd3cb138ae143676a56dfcc00c','Exact complete A prefix')
 steps=context['fixed_recipe']['variants'][VARIANT]['batches'][0]
 require(sum(s['max_ticks']for s in steps)==BOUND,'Fixed total Native bound')
 require(not LOG.exists(),'Previous guard log preserved; no automatic retry')
 spec=importlib.util.spec_from_file_location('propietario_diagnostico',RP/'propietario_diagnostico.py')
 service=importlib.util.module_from_spec(spec);sys.modules['propietario_diagnostico']=service;spec.loader.exec_module(service)
 original=service.Owner.material;index=0;last_tick=861426
 state={'schema':'DEE.PI08.A.RP.external_per_request_guard.R01','status':'RUNNING','actual_published_driver':str(RP/'ejecutar_diagnostico.py'),
  'published_driver_sha256':sha(RP/'ejecutar_diagnostico.py'),'guard_sha256':sha(SELF),'recipe_sha256':RECIPE_SHA,
  'Native_bound':BOUND,'deadline_utc':DEADLINE.isoformat(),'initial_tick':last_tick,'rows':[],
  'fixed_inputs_or_readers_modified':False,'expected_values_passed_to_actor':False}
 record(state)
 def material(owner,identifier,literal,*pos,**kw):
  nonlocal index,last_tick
  require(index<len(steps),'No extra material operation')
  step=steps[index]
  require(identifier==LIFE+'_'+step['label'],'Fresh exact fixed transport sequence only')
  require(datetime.now(timezone.utc)<DEADLINE,'Deadline reached before next material input; preserve and close')
  require(last_tick-861426+step['max_ticks']<=BOUND,'Next fixed Native allowance does not fit')
  expected=dict(step['literal']);binding=step.get('actual_integer_binding')
  if binding:expected[binding['field']]=literal.get(binding['field']);require(type(expected[binding['field']])is int,'No missing-number fallback')
  require(literal==expected and kw.get('feedback','omit')==step.get('feedback','omit')and kw.get('actuator','closed')==step.get('actuator','closed'),'Fixed payload/transport settings differ')
  value=original(owner,identifier,literal,*pos,**kw)
  before,after=value['before_tick'],value['after_tick']
  row={'label':step['label'],'id':identifier,'literal':literal,'before_tick':before,'after_tick':after,'max_ticks':step['max_ticks'],'actual_ticks':after-before,'deadline_checked_before':True}
  state['rows'].append(row);record(state)
  require(before==last_tick and 0<=after-before<=step['max_ticks']and after-861426<=BOUND,'Unexpected idle gap or Native bound exceeded; no retry/rewind')
  last_tick=after;index+=1
  return value
 service.Owner.material=material
 sys.argv=[str(RP/'ejecutar_diagnostico.py'),'--contexto',str(DEST/'CONTEXTO_EJECUCION.json')]
 try:runpy.run_path(str(RP/'ejecutar_diagnostico.py'),run_name='__main__')
 except SystemExit as exc:
  state.update(status='COMPLETED_DRIVER'if exc.code in(None,0)and index==len(steps)else'STOPPED_PRESERVED',exit_code=exc.code,completed_material_requests=index,final_tick=last_tick,new_Native_ticks=last_tick-861426);record(state);raise
 except BaseException as exc:
  state.update(status='STOPPED_PRESERVED',error=repr(exc),completed_material_requests=index,final_tick=last_tick,new_Native_ticks=last_tick-861426,automatic_retry=False);record(state);raise
if __name__=='__main__':
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--stage',choices=('manager','rp','driver'),required=True);main(parser.parse_args())
