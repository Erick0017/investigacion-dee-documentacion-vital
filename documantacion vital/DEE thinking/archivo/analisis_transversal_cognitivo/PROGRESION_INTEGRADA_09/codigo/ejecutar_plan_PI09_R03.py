"""Root-only bounded owner driver. A sealed finite JSON plan, no DEE imports here."""
from pathlib import Path
from datetime import datetime, timezone
import argparse, copy, hashlib, importlib.util, json, os, re
P=Path(__file__).resolve().parents[1];C=P.parents[2]/'DEE Cognitive 2.0';RP=C/'reproducibilidad';PY=C/'motor/python313/python.exe'
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def require(ok,msg):
 if not ok:raise ValueError(msg)
def ledger():
 file=P/'codigo/ledger_PI09_misma_identidad_R01.py'
 require(sha(file)=='bb1f326aa981ba00b9a6e3417700cca31d92a0d28a6e8a5ad601042bf2a26260','Exact same-ID ledger')
 sp=importlib.util.spec_from_file_location('PI09_panel_final_ledger',file);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);v=m.ledger()
 return v['ticks'],v['worlds']

def main(args):
 planpath=args.plan.resolve(strict=True);plan=read(planpath);system=Path(plan['system']).resolve(strict=True);life=plan['life_id'];tag=plan['tag'];steps=plan['steps']
 require(re.fullmatch(r'PI09_[A-Za-z0-9_]{1,65}',tag),'Fixed short unique operation tag')
 require(system.name=='sistema' and system.parent.parent==(P/'estados').resolve(),'Explicit isolated PI09 system only')
 require(not(system/'estado/ACTIVO.json').exists(),'Never run experiment on selected principal')
 require(steps and all(type(s['max_ticks'])is int and s['max_ticks']>=0 for s in steps),'Finite bound every step')
 bound=sum(s['max_ticks']for s in steps)
 if not args.ejecutar:
  print(json.dumps({'mode':'PLAN_NO_NATIVE','life':life,'steps':len(steps),'finite_bound':bound,'plan_sha256':sha(planpath)},ensure_ascii=False));return
 budget=read(P/'REGISTRO_CAMPANA.json')['budget'];cutoff=datetime.fromisoformat(budget['new_experimental_uses_cutoff_local']).astimezone(timezone.utc)
 require(datetime.now(timezone.utc)<cutoff,'Prospective experimental cutoff')
 used,worlds=ledger();require(used+bound<=budget['Native_ticks_all_branches'] and len(worlds)<=budget['diagnostic_worlds_all_new'],'Campaign ticks/world budget insufficient')
 require(sum(f.stat().st_size for f in P.rglob('*')if f.is_file())+budget['closure_storage_reserved_bytes']<budget['additional_logical_bytes_including_delivery'],'Storage budget reserved')
 cardpath=system/'estado/vidas'/life/'VIDA.json';card=read(cardpath)
 require(card['physical']['tick']==plan['initial_tick'],'Stale plan, never restore/retry silently')
 require(not(cardpath.parent/'FUTURO_INTERRUMPIDO.json').exists(),'Preserve interrupted future')
 require(not(system/'estado/locks').exists()or not any((system/'estado/locks').iterdir()),'Owner lock remains; inspect')
 marker=P/'PI09_ROOT_NATIVE_WRITER.lock';proof=P/'control'/(tag+'.json')
 require(not marker.exists()and not proof.exists()and not(RP/'EJECUCION_MATERIAL.lock').exists(),'Existing Root/RP writer or proof; no reuse')
 active=C/'sistema/estado/ACTIVO.json';acard=C/'sistema/estado/vidas'/read(active)['life_id']/'VIDA.json'
 protected=[active,acard,C/'sistema'/read(acard)['snapshot']];before={str(p):sha(p)for p in protected}
 pins={str(Path(k).resolve(strict=True)):v for k,v in plan.get('pins',{}).items()};pins[str(planpath)]=sha(planpath)
 require(all(sha(Path(k))==v for k,v in pins.items()),'Prospective code/protocol pin mismatch')
 marker.write_text(json.dumps({'pid':os.getpid(),'life':life,'tag':tag,'bound':bound}),'utf8')
 spec=importlib.util.spec_from_file_location('PI09_owned_driver',RP/'propietario_diagnostico.py');driver=importlib.util.module_from_spec(spec);spec.loader.exec_module(driver);driver.configure(P,system,PY)
 owner=None;error=None;records=[];by_label={};initial=card['physical']['tick'];cursor=initial
 clock=None
 if any(s.get('clock_alignment')for s in steps):
  helper=P/'codigo/pi09_aritmetica_temporal_P0_R01.py'
  require(sha(helper)=='ebff5dbe0d3b85000a33b7f789a72688e7c24c0151076558a01e32a803824656','Frozen clock-only helper changed')
  sp=importlib.util.spec_from_file_location('PI09_pure_clock_alignment',helper);clock=importlib.util.module_from_spec(sp);sp.loader.exec_module(clock)
 try:
  owner=driver.Owner(life,tag)
  with owner:
   for i,s in enumerate(steps):
    require(datetime.now(timezone.utc)<cutoff,'Cutoff before next operation')
    require(all(sha(Path(k))==v for k,v in pins.items()),'Sealed code/plan changed')
    identifier=tag+'_%03d'%i;literal=copy.deepcopy(s['literal']);alignment=None
    if s.get('clock_alignment'):
     require(s['clock_alignment']is True and literal.get('modo')=='eci01-pi09-aritmetica-temporal','Fixed clock-only arithmetic challenge')
     wait=clock.challenge_wait(cursor,True);require(0<=wait<=145,'Bounded legal challenge wait')
     literal['espera_previa']=wait
     alignment={'source_actual_tick':cursor,'legal_wait_ticks':wait,'unchanged_nominal_query':clock.query(cursor+wait,True),'expected_values_or_outcomes_used':False}
     require(alignment['unchanged_nominal_query']%67==19,'Frozen clock challenge failed')
    binding=s.get('actual_integer_binding')
    if binding:
     actual=by_label[binding['from_step']]['actual'];require(type(actual)is int,'NULL/noninteger previous actual result cannot be transported');literal[binding['field']]=actual
    result=owner.material(identifier,literal,feedback=s.get('feedback','real'),actuator=s.get('actuator','closed'),allow_failure=True)
    require('before_tick'in result and'after_tick'in result,'Missing complete transport result; SAME ID preserved')
    require(result['before_tick']==cursor,'Unexpected idle/material advance; preserve actual future')
    delta=result['after_tick']-result['before_tick'];require(0<=delta<=s['max_ticks'],'Per-operation Native horizon exceeded');cursor=result['after_tick']
    primary=P/'ensayos'/(identifier+'.json')
    rec={'index':i,'id':identifier,'label':s.get('label',str(i)),'literal':literal,'before_tick':result['before_tick'],'after_tick':result['after_tick'],'ticks':delta,'primary':str(primary),'sha256':sha(primary),'rows':result['result']['rows'],'clock_alignment':alignment}
    if s.get('read_path'):
     actual=result
     for key in s['read_path']:actual=actual[key]
     rec.update(actual=actual,expected=s.get('expected'),correct=actual==s['expected'] if 'expected'in s else None)
    records.append(rec);by_label[rec['label']]=rec
    require(result.get('status','completed')not in ('failed_preserved','uncertain','rejected_invalid'),'Preserved failed operation')
   owner.control('guardar')
 except BaseException as exc:error={'type':type(exc).__name__,'message':str(exc),'automatic_retry':False}
 closed=bool(owner is not None and owner.proc is not None and owner.proc.poll()==0 and not(owner.q.get_meta('owner')or{}).get('running'))
 after={str(p):sha(p)for p in protected}
 if before!=after:error={'type':'PRINCIPAL_CHANGED','automatic_retry':False}
 final=read(cardpath);output={'schema':'DEE.PI09.actual.finite_owner_plan.R03','status':'CLOSED_FINITE_PHASE'if closed and error is None else'STOPPED_PRESERVED','life_id':life,'tag':tag,'plan':str(planpath),'plan_sha256':sha(planpath),'initial_tick':initial,'final_tick':final['physical']['tick'],'new_Native_ticks':final['physical']['tick']-initial,'finite_bound':bound,'closed':closed,'error':error,'records':records,'protected_before':before,'protected_after':after,'ledger_before':{'ticks':used,'worlds':worlds},'no_adoption':True}
 with proof.open('x',encoding='utf8')as f:json.dump(output,f,ensure_ascii=False,indent=2);f.write('\n')
 if closed and marker.exists():marker.unlink()
 print(json.dumps({'proof':str(proof),'status':output['status'],'error':error,'ticks':output['new_Native_ticks'],'final_tick':output['final_tick'],'operations':len(records)},ensure_ascii=False))
 if error:raise SystemExit(1)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--plan',type=Path,required=True);p.add_argument('--ejecutar',action='store_true');main(p.parse_args())
