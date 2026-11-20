"""Root-only selected B public manager use; default plan, no imports of DEE.

Actual exterior gestionar.py enqueues fixed FI20/6, alfa, B opportunity30.
The existing owner is sole Native writer. No last C2C use, resend, rewind,
automatic rollback or state repair. A remains unchanged and recoverable.
"""
from pathlib import Path
from datetime import datetime, timezone
from collections import Counter
import argparse, hashlib, importlib.util, json, os, time

P=Path(__file__).resolve().parents[1];C=P.parents[2]/'DEE Cognitive 2.0';S=C/'sistema';RP=C/'reproducibilidad';PY=C/'motor/python313/python.exe'
LIFE='ECI02_PI03_REPRO_PI04_PI05_PI07_PI08_B_REAL_01';A='ECI02_PI03_REPRO_PI04_PI05_PI07_RP_R03_PI08_A01';TAG='PI08_B_USO_PUBLICO_PRINCIPAL_R01';BOUND=3500
def require(ok,message):
 if not ok:raise ValueError(message)
def read(p):return json.loads(p.read_text('utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def put(p,v):
 with p.open('x',encoding='utf8')as f:json.dump(v,f,ensure_ascii=False,indent=2);f.write('\n')
def load(name,p):
 spec=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def direct(items):
 result={}
 for item in items:
  rid=item['id'];receipt=item['receipt'];require(type(rid)is int and receipt['id']==rid,'Current receipt ID mismatch')
  require(rid not in result or result[rid]==receipt,'Conflicting receipt alias');result[rid]=receipt
 return result

def main(args):
 output=P/'control'/(TAG+'.json');require(not output.exists(),'Existing public execution protected; never resubmit IDs')
 plan=[('FI20_6',{'modo':'eci01-balance','izquierda':20,'derecha':6},1300),
       ('alfa',{'modo':'memoria','operacion_memoria':'usar','contexto':'alfa'},512),
       ('B_OP30',{'modo':'eci01-pi08-b-episodio'},1300)]
 if not args.ejecutar:
  print(json.dumps({'mode':'PLAN_ONLY','life_id':LIFE,'public_literals':[r[1]for r in plan],
                    'finite_Native_bound':BOUND,'actual_manager_enqueue':True,'Native_executed':False}));return 0
 activefile=S/'estado/ACTIVO.json';active=read(activefile);profile=read(S/'contratos/PI08_B_USO_OPERATIVO_R01.json')
 require(active['life_id']==LIFE and profile['life_id']==LIFE and profile['status']=='COMMITTED'and profile['all_adoption_gates_met']is True,'Actually committed selected B required')
 cardfile=S/'estado/vidas'/LIFE/'VIDA.json';before=read(cardfile);initial=before['physical']['tick'];require(before['physical']['N']==67,'Inherited N67 required')
 for folder in(S/'estado/locks',):require(not folder.exists()or not any(folder.iterdir()),'Affected writer lock remains')
 require(not(cardfile.parent/'FUTURO_INTERRUMPIDO.json').exists()and not(RP/'EJECUCION_MATERIAL.lock').exists(),'Preserve unresolved material future')
 marker=P/'PI08_ROOT_NATIVE_WRITER.lock';require(not marker.exists(),'Sole-writer marker remains')
 budget=read(P/'REGISTRO_CAMPANA.json')['budget'];cutoff=datetime.fromisoformat(budget['new_experimental_uses_cutoff_local']).astimezone(timezone.utc)
 require(datetime.now(timezone.utc)<cutoff,'New material-use cutoff reached')
 acardfile=S/'estado/vidas'/A/'VIDA.json';acard=read(acardfile);require(acard['physical']['tick']==861426 and acard['snapshot_sha256']=='2eeef08e3bebac4e218178ed379fd99aa5fdeb03650c0454ad55c6534824c133','Protected A changed')
 protected=[acardfile,S/acard['snapshot']];protected_hash={str(f):sha(f)for f in protected}
 cards=list((P/'estados').glob('*/sistema/estado/vidas/*/VIDA.json'))+[cardfile,acardfile];seen=set();used=0
 for f in cards:
  card=read(f);require(card['life_id']not in seen,'Duplicate current world in Native ledger');seen.add(card['life_id']);origin=card.get('parent',{}).get('source_tick');require(type(origin)is int and card['physical']['tick']>=origin,'Current Native origin required');used+=card['physical']['tick']-origin
 require(used+BOUND<=budget['Native_ticks_all_branches'],'Fixed Native budget insufficient')
 put(marker,{'pid':os.getpid(),'life_id':LIFE,'kind':'SELECTED_B_PUBLIC_MANAGER_USE','finite_bound':BOUND})
 supervisor=load('PI08_B_selected_existing_owner',RP/'propietario_diagnostico.py');supervisor.configure(P,S,PY)
 owner=None;error=None;rows=[];ids=set();counts=Counter();commands=[];stopped=None

 def exterior(label,literal,limit):
  identifier=TAG+'_'+label;require(owner.q.get(identifier)is None,'Request ID already exists; never resend')
  payload={'operacion':'sesion','situaciones':[literal],'actuador':'closed','retorno':'real'}
  command=[str(PY),'-I','-B','-X','utf8',str(S/'gestionar.py'),'--system-root',str(S),
           'mente-unificada-pedir','--vida',LIFE,'--id',identifier,'--situaciones',json.dumps([literal],ensure_ascii=False),
           '--actuador','closed','--retorno','real','--esperar','0']
  stdout=P/'ensayos'/(identifier+'.CLI.stdout.txt');stderr=P/'ensayos'/(identifier+'.CLI.stderr.txt')
  with stdout.open('x',encoding='utf8')as out,stderr.open('x',encoding='utf8')as err:
   process,job,jobname=supervisor.pc.spawn_owned(command,cwd=str(P),stdout=out,stderr=err,memory_limit=536870912)
   deadline=time.monotonic()+60;timed_out=False
   while process.poll()is None or(process.poll()!=0 and supervisor.pc.job_resources(job).get('job_active_processes',0)):
    if time.monotonic()>deadline and not timed_out:
     timed_out=True
     timeoutfile=P/'control'/(identifier+'_CLI_HORIZON_PRESERVED.json')
     put(timeoutfile,{'pid':process.pid,'id':identifier,'command':command,'automatic_kill':False,'automatic_resend':False,
        'scope':'Transport CLI horizon exceeded; supervisor retains its job handle and waits for natural exit. No following material use is authorized.'})
     print(json.dumps({'transport_horizon_preserved':str(timeoutfile),'pid':process.pid,'automatic_kill':False}),flush=True)
    time.sleep(.05)
   admission=owner.q.get(identifier);resources=supervisor.pc.job_resources(job)
   command_record={'id':identifier,'command':command,'exit_code':process.returncode,'job_resources':resources,
      'stdout':str(stdout),'stderr':str(stderr),'job':jobname,'outer_memory_limit':536870912};commands.append(command_record)
   require(process.returncode==0 and admission is not None and json.loads(admission['payload'])==payload,
           'Exterior admission ambiguous/failed; inspect exact ID, never resend')
   # Successful CLI has exited, and this separate owner is still paused.
   # Only its CLI job handle is closed; it cannot own the persistent owner.
   supervisor.pc.close_job(job);command_record['successful_CLI_job_closed_explicitly']=True
   require(not timed_out,'CLI horizon was exceeded; exact queued ID preserved without re-enqueue or Native continuation')
  owner.control('reanudar');request=owner.wait(identifier);owner.control('pausar')
  primary=P/'ensayos'/(identifier+'.json');put(primary,request)
  require(request['status']=='completed'and request.get('result'),'Material future preserved; no following request')
  value=json.loads(request['result']);require(0<=value['after_tick']-value['before_tick']<=limit,'Prospective per-use bound exceeded')
  require(value['after_tick']-initial<=BOUND,'Prospective total bound exceeded')
  rows.append({'label':label,'literal':literal,'primary':str(primary),'primary_sha256':sha(primary),
               'transport_id':identifier,'before_tick':value['before_tick'],'after_tick':value['after_tick']})
  supervisor.append({'kind':'PUBLIC_MANAGER_MATERIAL','id':identifier,'life':LIFE,'run':owner.runid,
      'literal':literal,'status':request['status'],'record':str(primary.relative_to(P)),
      'before_tick':value['before_tick'],'after_tick':value['after_tick'],'sha256':sha(primary)})
  return value['result']['rows'][0]

 try:
  owner=supervisor.Owner(LIFE,TAG,system=S)
  with owner:
   state=owner.material(TAG+'_B_STATE_PRE',{'modo':'eci01-pi08-b-estado'},feedback='omit',actuator='closed')
   require(state['before_tick']==state['after_tick']==initial and state['result']['rows'][0]['progress']['ordinal']==30,'Exact current B next opportunity30 required')
   for label,literal,limit in plan:
    require(datetime.now(timezone.utc)<cutoff,'Cutoff between material uses')
    row=exterior(label,literal,limit)
    if label=='FI20_6':
     require('public_operands'in row and 'generic_return_failed'in row,'Public alias reached legacy route instead of fixed regulated access')
     observed,expected,items=row['early_physical_choice'],1,row['requests']
    elif label=='alfa':
     inner=row['result']['rows'][0];observed,expected,items=inner['reader']['formed_native_command'],-1,inner['requests']
    else:
     require(row['ordinal']==30,'Wrong B resource consumed');observed,expected,items=row['actual_failed'],False,row['requests']
    actual=direct(items);require(not ids.intersection(actual),'Inherited receipt counted as new input');ids.update(actual)
    statuses=Counter(r['status']for r in actual.values());counts.update(statuses)
    require(all(k=='applied'or k.startswith('rejected')for k in statuses),'Unresolved Native receipt; stop/preserve')
    correct=observed==expected and type(observed)is type(expected)
    rows[-1].update(observed=observed,expected_evaluator_only=expected,correct=correct,
       Native_inputs={'unique_requested':len(actual),'status_counts':dict(statuses)})
    if not correct:
     stopped={'label':label,'reason':'KNOWN_FUNCTIONAL_ERROR_OR_NULL_PRESERVED','no_more_material_requests':True};break
   owner.control('guardar')
 except Exception as exc:error={'type':type(exc).__name__,'message':str(exc),'automatic_retry':False}
 closed=bool(owner is not None and owner.proc is not None and owner.proc.poll()==0 and not(owner.q.get_meta('owner')or{}).get('running')and not owner.q.outstanding())
 current=read(cardfile);delta=current['physical']['tick']-initial;unchanged=protected_hash=={str(f):sha(f)for f in protected}
 criteria=bool(closed and error is None and stopped is None and len(rows)==3 and all(r.get('correct')for r in rows)and unchanged and 0<=delta<=BOUND)
 actual_binding={'life_id':LIFE,'N':current['physical']['N'],'tick':current['physical']['tick'],'snapshot_sha256':current['snapshot_sha256']}
 result={'schema':'DEE.PI08.B.selected_public_manager_use.R01','recorded_utc':datetime.now(timezone.utc).isoformat(),
    'life_id':LIFE,'principal_bindings':actual_binding,'physical':current['physical'],'initial_tick':initial,'final_tick':current['physical']['tick'],
    'snapshot_sha256':current['snapshot_sha256'],'current_record':current,'new_Native_ticks':delta,'finite_Native_bound':BOUND,
    'closed':closed,'owner_closed':closed,'pending_reconciled':closed,'criteria_met':criteria,'error':error,'preserved_stop':stopped,
    'all_planned_steps_executed':len(rows)==3,'rows':rows,'actual_exterior_manager_commands':commands,
    'Native_inputs':{'unique_requested':len(ids),'status_counts':dict(counts)},'A_unchanged':unchanged,'protected_A_hashes':protected_hash,
    'C2C_main_last_resource_not_consumed':True,'B_remaining_if_complete':1 if len(rows)==3 else None,
    'no_rewind_or_automatic_switch_to_A':True,'scope':'Selected public functional use, not new independent acquisition/causal generalization. Any switch back to A requires a separate explicit Root decision.'}
 put(output,result)
 if closed and marker.exists():marker.unlink()
 print(json.dumps({'proof':str(output),'sha256':sha(output),'criteria_met':criteria,'closed':closed,'final_tick':current['physical']['tick']}))
 return 0 if criteria else 2

if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--ejecutar',action='store_true');raise SystemExit(main(p.parse_args()))
