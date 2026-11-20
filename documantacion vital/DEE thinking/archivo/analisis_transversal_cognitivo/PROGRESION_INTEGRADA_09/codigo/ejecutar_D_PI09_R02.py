"""ROOT ONLY: prepare a finite D2 plan; --ejecutar explicitly runs it.

The default only reads frozen protocol/seal and writes a new plan, never world
cards, Runtime, SQLite, Native or product. Execution reuses the existing owned
RP supervisor (512MiB, paused startup), current campaign limits and same-ID
saved-card ledger, including PI09 lives moved into the product. No cloning,
adoption, automatic repair or ambiguous-request retry occurs in this script.
"""
from pathlib import Path
from datetime import datetime,timezone
import argparse,copy,hashlib,importlib.util,json,os,re

P=Path(__file__).resolve().parents[1];H=P/'codigo';C=P.parents[2]/'DEE Cognitive 2.0';RP=C/'reproducibilidad';PY=C/'motor/python313/python.exe'
LEDGER=H/'ledger_PI09_misma_identidad_R01.py';LEDGER_SHA='bb1f326aa981ba00b9a6e3417700cca31d92a0d28a6e8a5ad601042bf2a26260'
MODULE=H/'pi09_entorno_persistente_D_R02.py';PROTOCOL=H/'PROTOCOLO_PI09_D_R02.json';SEAL=H/'SELLO_PI09_D_R02.json'
ADOPTED=P/'control/ADOPCION_PRODUCTO_PI09.json'
PREPARE='eci01-pi09-d-preparar';EPISODE='eci01-pi09-d-episodio';STATE='eci01-pi09-d-estado'
def require(ok,why):
    if not ok:raise ValueError(why)
def read(file):return json.loads(Path(file).read_text('utf-8-sig'))
def sha(file):
    h=hashlib.sha256()
    with Path(file).open('rb')as f:
        for block in iter(lambda:f.read(1048576),b''):h.update(block)
    return h.hexdigest()
def imported(name,path):
    s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def checked_seal():
    require(sha(LEDGER)==LEDGER_SHA,'Same-identity ledger source changed')
    seal=read(SEAL);protocol=read(PROTOCOL)
    require(seal['schema']=='DEE.PI09.persistent_environment.D.source_seal.R02'and seal['protocol_sha256']==sha(PROTOCOL),'Exact current D2 source seal required')
    require(seal.get('first_milestone_committed')is True and re.fullmatch('[0-9a-f]{64}',seal.get('first_milestone_adoption_sha256','')),'First milestone must already be COMMITTED; a prepared D script is not authorization')
    adopted=read(ADOPTED)
    require(sha(ADOPTED)==seal['first_milestone_adoption_sha256']and adopted.get('schema')=='DEE.PI09.same_identity.adopted_product.R01'and adopted.get('phase')=='COMMITTED'and adopted.get('life_id')=='ECI02_PI03_REPRO_PI04_PI05_PI07_PI09_NATIVE_01'and adopted.get('commit_witness')and adopted.get('source_history_not_rewritten')is True,'Actual immutable first-milestone COMMITTED receipt required; seal boolean alone is insufficient')
    require(protocol['max_ticks_per_whole_D_opportunity']==2510 and protocol['evaluation_horizon']==6 and len(protocol['schedule'])==12,'Fixed6evaluation+6future D2 contract')
    for name,digest in seal['files_sha256'].items():require(Path(name).name==name and sha(H/name)==digest,'D2 sealed source changed: '+name)
    require(MODULE.name in seal['files_sha256'],'D2 module must be pinned')
    return seal,protocol
def make_plan(seal,protocol,arm,system,tag,phase,start,hasta,tick,yoke_text=None,reproduction=False):
    require(arm in('real','none','yoked')and re.fullmatch(r'PI09_D_[A-Za-z0-9_]{1,60}',tag),'Explicit D arm/fresh short tag')
    require(phase in('preparar','evaluar','completo'),'Finite preparation/evaluation phase')
    require(type(start)is int and type(hasta)is int and 0<=start<=hasta<=12 and(arm=='real'or hasta<=6),'Real up to12, controls up to6; no reset')
    require(not reproduction or arm=='real','Reproduction is real policy only')
    life=seal['native_reproduction_ids'][0]if reproduction else seal['arms'][arm]
    if phase in('preparar','completo'):require(start==0 and tick==seal['source_prefix']['tick'],'Preparation only from exact sealed parent, never a restarted ordinal')
    require(phase=='preparar'or hasta>start,'At least one explicit continuation opportunity')
    require(phase!='evaluar'or type(tick)is int,'Actual closed starting boundary required for a continuation')
    admission={'modo':PREPARE,'brazo':arm}
    if arm=='yoked':
        require(isinstance(yoke_text,str),'Yoke requires full actual closed real6 return plan')
        plan=json.loads(yoke_text);require(plan['schema']=='DEE.PI09.D.yoked_return.fixed_permutation.v1'and plan['permutation']==[2,0,4,1,5,3]and len(plan['source_failed'])==6 and all(type(v)is bool for v in plan['source_failed'])and plan['values']==[plan['source_failed'][i]for i in plan['permutation']],'Literal prespecified actual return yoke, never optimized')
        admission['plan']=json.dumps(plan,ensure_ascii=False,sort_keys=True,separators=(',',':'))
    steps=[{'label':'STATE_BEFORE','literal':{'modo':STATE},'max_ticks':0}]
    if phase in('preparar','completo'):steps.append({'label':'D_FIXED_P0','literal':admission,'max_ticks':3,'require_ready':True})
    if phase in('evaluar','completo'):
        steps.extend({'label':'D_EP%02d'%i,'ordinal':i,'literal':{'modo':EPISODE},'max_ticks':2510,'evaluation_or_future':'evaluation'if i<6 else'explicit_future_use','expected_reply_passed_to_actor':False}for i in range(start,hasta))
    steps.append({'label':'STATE_AFTER','literal':{'modo':STATE},'max_ticks':0})
    return {'schema':'DEE.PI09.D.prospective.finite_owned_plan.R02','created_utc':datetime.now(timezone.utc).isoformat(),'system':str(system),'life_id':life,'arm':arm,'phase':phase,'tag':tag,'initial_tick':tick,'from_ordinal':start,'until_ordinal_exclusive':hasta if phase!='preparar'else 0,'declared_real_capacity':12,'control_capacity':6,'evaluation_horizon':6,'explicitly_consumes_future_stock':phase!='preparar'and hasta>6,'remaining_declared_D_stock_if_completed':12-hasta if phase!='preparar'else 12,'steps':steps,'finite_bound':sum(v['max_ticks']for v in steps),'source_prefix':seal['source_prefix'],'first_milestone_adoption_sha256':seal['first_milestone_adoption_sha256'],'pins':{str(p):sha(p)for p in(MODULE,PROTOCOL,SEAL,LEDGER,ADOPTED,RP/'propietario_diagnostico.py',Path(__file__))},'scientific_reader_decoder_return_unchanged':True,'first_query_credit_not_isolated':True,'clone_or_budget_revision_performed':False}
def no_native_writer():
    require(not(P/'PI09_ROOT_NATIVE_WRITER.lock').exists()and not(RP/'EJECUCION_MATERIAL.lock').exists(),'Root/RP writer active or unresolved; preserve it')
    # Check lock namespaces only, BEFORE any world/card/ledger read. No cached
    # running=False is taken as proof of an active owner's absence.
    for folder in [*(P/'estados').glob('*/sistema/estado/locks'),C/'sistema/estado/locks']:
        require(not folder.exists()or not any(folder.iterdir()),'Owner lock remains; Root must inspect before starting D: '+str(folder))
def execute(planpath):
    plan=read(planpath);system=Path(plan['system']).resolve(strict=True);life=plan['life_id'];tag=plan['tag'];steps=plan['steps'];bound=plan['finite_bound']
    require(system.name=='sistema'and system.parent.parent==(P/'estados').resolve(),'Isolated PI09 system only; never use this supervisor on selected product')
    require(not(system/'estado/ACTIVO.json').exists(),'Selected source is protected')
    no_native_writer();seal,_=checked_seal();require(seal['first_milestone_adoption_sha256']==plan['first_milestone_adoption_sha256'],'Milestone permission changed')
    budget=read(P/'REGISTRO_CAMPANA.json')['budget'];cutoff=datetime.fromisoformat(budget['new_experimental_uses_cutoff_local']).astimezone(timezone.utc)
    require(datetime.now(timezone.utc)<cutoff,'Actual campaign science cutoff')
    require(budget['owned_Native_job_memory_bytes']==512*1024*1024 and budget['Native_threads']==1,'Effective inherited512MiB/one-thread contract')
    ledger=imported('PI09_D_actual_same_identity_ledger',LEDGER).ledger();require(ledger['ticks']+bound<=budget['Native_ticks_all_branches']and ledger['world_count']<=budget['diagnostic_worlds_all_new'],'Current recorded ticks/world budget insufficient; no hardcoded12 or silent increase')
    # Same scope as the existing Root finite driver; Root's campaign meter also
    # accounts for RP/product additions and reserved final delivery elsewhere.
    logical=sum(f.stat().st_size for f in P.rglob('*')if f.is_file());require(logical+budget['closure_storage_reserved_bytes']<budget['additional_logical_bytes_including_delivery'],'P9 logical storage plus closure reserve exhausted')
    cardpath=system/'estado/vidas'/life/'VIDA.json';card=read(cardpath);require(card['physical']['tick']==plan['initial_tick'],'Stale D plan; never restore/retry silently')
    require(not(cardpath.parent/'FUTURO_INTERRUMPIDO.json').exists(),'Interrupted future must remain fenced')
    proof=P/'control'/(tag+'.json');marker=P/'PI09_ROOT_NATIVE_WRITER.lock';require(not proof.exists(),'Fresh tag/proof only')
    pins={Path(k):v for k,v in plan['pins'].items()};pins[planpath]=sha(planpath);require(all(sha(p)==v for p,v in pins.items()),'Prospective code/protocol pins changed')
    active=C/'sistema/estado/ACTIVO.json';acard=C/'sistema/estado/vidas'/read(active)['life_id']/'VIDA.json';protected=[active,acard,C/'sistema'/read(acard)['snapshot']];before={str(f):sha(f)for f in protected}
    with marker.open('x',encoding='utf8')as f:json.dump({'pid':os.getpid(),'life':life,'tag':tag,'finite_bound':bound,'same_identity_ledger_ticks':ledger['ticks']},f)
    owner=None;error=None;records=[]
    try:
        driver=imported('PI09_D_existing_owned_supervisor',RP/'propietario_diagnostico.py');driver.configure(P,system,PY);require(driver.MEMORY_LIMIT==budget['owned_Native_job_memory_bytes'],'Supervisor effective memory limit differs')
        owner=driver.Owner(life,tag)
        with owner:
            for index,step in enumerate(steps):
                require(datetime.now(timezone.utc)<cutoff,'Cutoff before next opportunity');require(all(sha(p)==v for p,v in pins.items()),'Sealed source/plan changed')
                identifier=tag+'_%03d'%index;result=owner.material(identifier,copy.deepcopy(step['literal']),feedback='real',actuator='closed',allow_failure=True)
                primary=P/'ensayos'/(identifier+'.json');entry={'index':index,'id':identifier,'label':step['label'],'literal':step['literal'],'primary':str(primary),'sha256':sha(primary),'transport_status':read(primary)['status']}
                if isinstance(result,dict)and'before_tick'in result and'after_tick'in result:
                    entry.update(before_tick=result['before_tick'],after_tick=result['after_tick'],ticks=result['after_tick']-result['before_tick'],rows=result.get('result',{}).get('rows',[]))
                records.append(entry);require(entry['transport_status']=='completed'and'ticks'in entry,'Preserved transport failure; same ID never resent')
                require(0<=entry['ticks']<=step['max_ticks'],'Whole operation exceeds predeclared finite horizon')
                if step.get('require_ready'):require(len(entry['rows'])==1 and entry['rows'][0].get('ready')is True,'Legal guard preparation did not become ready; preserve result, no EP/reinjection')
                if'ordinal'in step:require(len(entry['rows'])==1 and entry['rows'][0]['ordinal']==step['ordinal'],'Actual ordinal differs; no skip/reset')
                if step['label']=='STATE_BEFORE'and plan['phase']=='evaluar':require(entry['rows'][0]['progress']['ordinal']==plan['from_ordinal'],'Continuation source ordinal differs')
            owner.control('guardar')
    except BaseException as exc:error={'type':type(exc).__name__,'message':str(exc),'automatic_retry':False}
    closed=bool(owner is not None and owner.proc is not None and owner.proc.poll()==0 and not(owner.q.get_meta('owner')or{}).get('running'))
    after={str(f):sha(f)for f in protected}
    if before!=after:error={'type':'PROTECTED_PRINCIPAL_CHANGED','automatic_retry':False}
    final=read(cardpath)
    result={'schema':'DEE.PI09.D.actual.finite_owner_phase.R02','status':'CLOSED_FINITE_PHASE'if closed and error is None else'STOPPED_PRESERVED','closed':closed,'error':error,'life_id':life,'arm':plan['arm'],'phase':plan['phase'],'tag':tag,'plan':str(planpath),'plan_sha256':sha(planpath),'initial_tick':plan['initial_tick'],'final_tick':final['physical']['tick'],'new_Native_ticks':final['physical']['tick']-plan['initial_tick'],'finite_bound':bound,'records':records,'ledger_before':ledger,'budget_read_at_start':budget,'protected_before':before,'protected_after':after,'no_adoption':True,'no_cloning_or_budget_revision':True,'source_C1_and_R02_not_reset':True,'storage_preflight_scope':'P9 logical files + closure reserve; Root campaign meter remains authority for external RP/product additions'}
    with proof.open('x',encoding='utf8')as f:json.dump(result,f,ensure_ascii=False,indent=2);f.write('\n')
    if closed and marker.exists():marker.unlink()
    print(json.dumps({'proof':str(proof),'sha256':sha(proof),'status':result['status'],'error':error,'new_Native_ticks':result['new_Native_ticks']}))
    if error:raise SystemExit(1)
def main(a):
    if a.ejecutar:
        require(a.plan is not None,'Explicit frozen plan required for Root execution');execute(a.plan.resolve(strict=True));return
    seal,protocol=checked_seal();require(a.sistema is not None,'Explicit isolated target system required');system=a.sistema.absolute();require(system.name=='sistema'and system.parent.parent==(P/'estados').resolve(),'Explicit target under P9/estados, without opening it')
    require(a.tag is not None,'Fresh explicit tag required');tick=a.tick_inicial if a.tick_inicial is not None else seal['source_prefix']['tick']if a.fase in('preparar','completo')else None
    text=a.plan_retornos.read_text('utf-8-sig')if a.plan_retornos else None
    plan=make_plan(seal,protocol,a.brazo,system,a.tag,a.fase,a.desde,a.hasta,tick,text,a.reproduccion)
    out=H/('PLAN_'+a.tag+'.json');require(not out.exists(),'New prospective plan only')
    with out.open('x',encoding='utf8')as f:json.dump(plan,f,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps({'mode':'PREPARED_NO_NATIVE','plan':str(out),'sha256':sha(out),'bound':plan['finite_bound'],'explicit_future_consumption':plan['explicitly_consumes_future_stock'],'worlds_read_or_cloned':False}))
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--ejecutar',action='store_true');ap.add_argument('--plan',type=Path);ap.add_argument('--brazo',choices=('real','none','yoked'),default='real');ap.add_argument('--sistema',type=Path);ap.add_argument('--tag');ap.add_argument('--fase',choices=('preparar','evaluar','completo'),default='completo');ap.add_argument('--desde',type=int,default=0);ap.add_argument('--hasta',type=int,default=6);ap.add_argument('--tick-inicial',type=int);ap.add_argument('--plan-retornos',type=Path);ap.add_argument('--reproduccion',action='store_true');main(ap.parse_args())
