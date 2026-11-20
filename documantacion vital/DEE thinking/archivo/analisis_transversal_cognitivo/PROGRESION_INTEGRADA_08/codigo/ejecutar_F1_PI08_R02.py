"""Root-only F1 first/next runner. Default plan, no Native imports.

One complete POST4 import; structural identity fork advances zero ticks; only
the separate RAW-cut fork continues. Previously actual intact OP4/5 is reused.
No actor modification, force, source reset, promotion, retry or principal edit.
"""
from pathlib import Path
from datetime import datetime,timezone
from collections import Counter
import argparse,hashlib,importlib.util,json,os,runpy
P=Path(__file__).resolve().parents[1];H=P/'codigo';C=P.parents[2]/'DEE Cognitive 2.0';RP=C/'reproducibilidad';PY=C/'motor/python313/python.exe'
LIFE='ECI02_PI03_REPRO_PI04_PI05_PI07_PI08_F1_CUT_01'

def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def require(b,t):
    if not b:raise ValueError(t)
def receipt_counts(requests):
    seen={};aliases=0
    for row in requests:
        i=row['id'];r=row['receipt'];require(type(i)is int and r['id']==i,'Current Native receipt identity mismatch')
        if i in seen:require(seen[i]==r,'Contradictory Native alias');aliases+=1
        seen[i]=r
    return seen,aliases

def main(a):
    prep=read(P/'control/SISTEMA_F1_PI08_R02_PREPARADO.json');S=Path(prep['system']);directory=Path(prep['directory'])
    require(S.resolve().is_relative_to((P/'estados/F1_CUT_R02').resolve()) and S.name=='sistema','Exact F1 diagnostic system')
    protocol_path=S/'capacidades/PROTOCOLO_F1_DIAGONAL_PI08_R02.json';protocol=read(protocol_path)
    require(protocol['status']=='SEALED_FOR_OPTIONAL_F1_NATIVE' and sha(protocol_path)==prep['sealed_protocol_sha256'],'Prospective protocol changed')
    require(protocol['world_slots_one_import_plus_two_forks']==3 and protocol['maximum_Native_ticks_total']==2600,'Fixed budget changed')
    steps=[{'label':'estado_pre','literal':{'modo':'eci01-pi08-f1-estado'},'max_ticks':0},
      {'label':'OP4','literal':{'modo':'eci01-pi08-f1-diagonal','arm':'raw_cut','stage':'first'},'max_ticks':1300},
      {'label':'OP5','literal':{'modo':'eci01-pi08-f1-diagonal','arm':'raw_cut','stage':'next'},'max_ticks':1300},
      {'label':'estado_final','literal':{'modo':'eci01-pi08-f1-estado'},'max_ticks':0}]
    if not a.ejecutar:
        print(json.dumps({'mode':'PLAN_ONLY_NO_NATIVE','life_id':LIFE,'system':str(S),'steps':steps,
          'world_slots':3,'maximum_Native_ticks':2600,'identity_sham_future_ticks':0,
          'new_intact_future':False,'intact_reference_primaries':protocol['source_reference_primaries']},ensure_ascii=False,indent=2));return
    require(not(S/'estado/ACTIVO.json').exists(),'No selected diagnostic principal')
    imp=read(P/'control/IMPORTACION_F1_PI08_R02.json')
    require(imp['status']=='IMPORTED_CLOSED_NO_NATIVE_TICKS' and imp['exit_code']==0 and imp['successful_import_job_closed_before_supplement'],'Complete import and directory supplement must precede Owner')
    require(imp['directory_transport_supplement']['complete'] if 'complete' in imp['directory_transport_supplement'] else imp['directory_transport_supplement'] is not None,'Declared empty directories required')
    card_path=S/'estado/vidas'/LIFE/'VIDA.json';card=read(card_path)
    require(card['physical']==protocol['source_physical'] or all(card['physical'][k]==v for k,v in protocol['source_physical'].items()),'Fresh complete POST4 physical source')
    require(card['parent']['source_tick']==849645,'No substitute initial life')
    require(not(S/'estado/vidas'/LIFE/'FUTURO_INTERRUMPIDO.json').exists(),'Preserve interrupted future; no retry')
    require(not(S/'estado/locks').exists() or not any((S/'estado/locks').iterdir()),'Inspect remaining owner lock, never erase')
    budget=read(P/'REGISTRO_CAMPANA.json')['budget'];cutoff=datetime.fromisoformat(budget['new_experimental_uses_cutoff_local']).astimezone(timezone.utc)
    # Reuse the existing pure accounting function, not its B actor/main entry.
    accounting=runpy.run_path(str(H/'ejecutar_B_PI08_R01.py'),run_name='PI08_pure_budget_accounting')
    ticks_before,worlds=accounting['native_ledger']()
    require(ticks_before+2600<=budget['Native_ticks_all_branches'],'F1 finite tick reserve unavailable')
    require(len(worlds)+2<=budget['diagnostic_worlds_all_new'],'Two extra internal Runtime forks do not fit world budget')
    require(datetime.now(timezone.utc)<cutoff,'Science cutoff reached')
    active=C/'sistema/estado/ACTIVO.json';selected=read(active)['life_id'];main_card=C/'sistema/estado/vidas'/selected/'VIDA.json';main_record=read(main_card)
    protected_paths=[active,main_card,C/'sistema'/main_record['snapshot']];protected={str(q):sha(q) for q in protected_paths}
    proof=P/'control/PI08_F1_CUT_R02.json';marker=P/'PI08_ROOT_NATIVE_WRITER.lock'
    require(not proof.exists() and not marker.exists() and not(RP/'EJECUCION_MATERIAL.lock').exists(),'Fresh exact run, one Root writer only')
    with marker.open('x',encoding='utf-8') as f:json.dump({'pid':os.getpid(),'life_id':LIFE,'scope':'F1_DIAGNOSTIC_NOT_LEARNED','world_slots_reserved':3,'finite_Native_bound':2600},f)
    spec=importlib.util.spec_from_file_location('PI08_F1_owned_driver',RP/'propietario_diagnostico.py');driver=importlib.util.module_from_spec(spec);spec.loader.exec_module(driver);driver.configure(P,S,PY)
    owner=None;error=None;rows=[];intervals=[];new_ids=set();statuses=Counter();forks=0;finalstate=None
    try:
        owner=driver.Owner(LIFE,'PI08_F1_CUT_R02')
        with owner:
            for step in steps:
                require(datetime.now(timezone.utc)<cutoff,'Deadline before next fixed F1 operation')
                require(sha(protocol_path)==prep['sealed_protocol_sha256'],'Prospective protocol changed during run')
                identifier='PI08_F1_CUT_R02_'+step['label']
                value=owner.material(identifier,step['literal'],feedback='real',actuator='closed',allow_failure=True)
                require('before_tick'in value and 'after_tick'in value and 0<=value['after_tick']-value['before_tick']<=step['max_ticks'],'Unknown outcome or actual finite bound exceeded; no retry')
                primary=P/'ensayos'/(identifier+'.json')
                intervals.append({'label':step['label'],'before_tick':value['before_tick'],'after_tick':value['after_tick'],'primary':str(primary),'sha256':sha(primary)})
                row=value['result']['rows'][0]
                if step['max_ticks']==0:
                    if step['label']=='estado_pre':require(row['state'] is None,'Fresh F1 state required')
                    else:finalstate=row['state']
                    continue
                original=row['original_result'];unique,aliases=receipt_counts(original['requests'])
                require(not new_ids.intersection(unique),'Historical Native receipt counted again')
                new_ids.update(unique);statuses.update(r['status'] for r in unique.values())
                require(all(r['status']=='applied'or r['status'].startswith('rejected') for r in unique.values()),'Ambiguous Native input; preserve and stop')
                forks+=row['additional_Native_Runtime_forks'];rows.append(row)
            require(finalstate['completed_operations']==2 and finalstate['pending'] is None,'F1 future incomplete')
            owner.control('guardar')
    except Exception as exc:error={'type':type(exc).__name__,'message':str(exc),'automatic_retry':False}
    closed=bool(owner is not None and owner.proc is not None and owner.proc.poll()==0 and not(owner.q.get_meta('owner')or{}).get('running'))
    after=read(card_path);protected_after={str(q):sha(q) for q in protected_paths}
    if protected_after!=protected:error={'type':'PROTECTED_PRINCIPAL_CHANGED','automatic_retry':False}
    out={'schema':'DEE.PI08.F1.actual_diagnostic_continuation.R02','at':datetime.now(timezone.utc).isoformat(),'life_id':LIFE,
      'status':'CLOSED_TWO_OPERATIONS'if closed and error is None and len(rows)==2 else'STOPPED_PRESERVED',
      'closed':closed,'error':error,'initial_tick':849645,'final_tick':after['physical']['tick'],
      'new_Native_ticks':after['physical']['tick']-849645,'maximum_Native_ticks':2600,
      'world_slots_reserved':3,'actual_imported_worlds':1,'actual_additional_Runtime_forks':forks,
      'identity_sham_Native_future_ticks':0,'new_intact_future_executed':False,
      'Native_inputs':{'unique_requested':len(new_ids),'status_counts':dict(statuses)},'rows':rows,'intervals':intervals,
      'final_state':finalstate,'protected_before':protected,'protected_after':protected_after,
      'intact_reference_primaries':protocol['source_reference_primaries'],
      'scope':'External post-formation RAW cut after same-cut structural identity check; intact Native future reused from previous actual execution. No acquired repair, independent organism, principal change or adoption.'}
    with proof.open('x',encoding='utf-8') as f:json.dump(out,f,ensure_ascii=False,indent=2);f.write('\n')
    if closed and marker.exists():marker.unlink()
    print(json.dumps({'proof':str(proof),'sha256':sha(proof),'status':out['status'],'error':error,'actual_Runtime_forks':forks},ensure_ascii=False))
    if error:raise SystemExit(1)

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--ejecutar',action='store_true');main(ap.parse_args())
