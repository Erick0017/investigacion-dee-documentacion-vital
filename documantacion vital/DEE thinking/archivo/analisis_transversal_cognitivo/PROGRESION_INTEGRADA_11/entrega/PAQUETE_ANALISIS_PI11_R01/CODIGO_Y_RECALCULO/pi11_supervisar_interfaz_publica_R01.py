"""Finite Root-owned public interface exercise; no Native import on import.

Uses the unchanged installed owner supervisor with its outer 512 MiB Job.
Only an explicit isolated IF clone, prepared moved MAIN, or committed MAIN
is accepted. A material request is never retried or replaced after failure.
"""
from pathlib import Path
from datetime import datetime, timezone
import argparse, ast, hashlib, importlib.util, json, os, subprocess, sys, types
P=Path(__file__).resolve().parents[1]; H=P/'codigo'; C=P.parents[2]/'DEE Cognitive 2.0'
PY=C/'motor/python313/python.exe'; RP=C/'reproducibilidad'; S=C/'sistema'
PARENT='ECI02_PI03_REPRO_PI04_PI05_PI07_PI10_REAL2_01'
MAIN='ECI02_PI03_REPRO_PI04_PI05_PI07_PI10_PI11_MAIN01'
IFLIFE='ECI02_PI03_REPRO_PI04_PI05_PI07_PI10_PI11_IF01'
DRIVER_SHA='e7053088b6492d9d10abe1c861da560de1fb1f4a9d00468661df53782523e52b'
def need(ok,msg):
    if not ok: raise ValueError(msg)
def read(p): return json.loads(Path(p).read_text('utf-8-sig'))
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(name,p):
    sp=importlib.util.spec_from_file_location(name,p); m=importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m
def write(p,v):
    with Path(p).open('x',encoding='utf8') as f: json.dump(v,f,ensure_ascii=False,indent=2); f.write('\n'); f.flush(); os.fsync(f.fileno())
def view(system,life):
    card=read(system/'estado/vidas'/life/'VIDA.json'); parser=RP/'observador_pasivo.py'
    need(sha(parser)=='dbb2a5e15d70c64112d36505197f4aebf6ff7d4092972923e17cd60c10a1c873','Frozen passive parser')
    need(sha(system/card['snapshot'])==card['snapshot_sha256'],'Actual saved card/checkpoint')
    return card,load('PI11_public_passive_'+life[-6:],parser).snapshot_view(system/card['snapshot'])
def main():
    ap=argparse.ArgumentParser(description=__doc__); ap.add_argument('--mode',choices=('interface','prepared-reopen','committed-use','committed-reopen'),required=True); ap.add_argument('--ejecutar',action='store_true'); a=ap.parse_args()
    life=IFLIFE if a.mode=='interface' else MAIN; system=P/'estados/IF01/sistema' if a.mode=='interface' else S
    tags={'interface':'PI11_IF01_PUBLICO_OWNER_R01','prepared-reopen':'PI11_PRODUCTO_PREPARED_REOPEN_OWNER_R01','committed-use':'PI11_PRODUCTO_PUBLICO_OWNER_R01','committed-reopen':'PI11_PRODUCTO_FINAL_REOPEN_OWNER_R01'}
    tag=tags[a.mode]; bound=4032 if a.mode=='interface' else 2016 if a.mode=='committed-use' else 0
    if not a.ejecutar:
        print(json.dumps({'mode':'PLAN_ONLY_NO_NATIVE_IMPORT','phase':a.mode,'life_id':life,'system':str(system),'finite_bound':bound,'tag':tag})); return
    need(Path(sys.executable).resolve()==PY.resolve(),'Official Python only')
    budget=read(P/'REGISTRO_CAMPANA.json')['budget']; need(datetime.now(timezone.utc)<datetime.fromisoformat(budget['new_experimental_uses_cutoff_utc']).astimezone(timezone.utc),'Native cutoff reached')
    contract=read(system/'contratos/PI11_USO_OPERATIVO_R01.json'); need(contract['life_id']==life,'Exact current permission')
    expected='DIAGNOSTIC_INTERFACE_ONLY' if a.mode=='interface' else 'PREPARED_DIAGNOSTIC' if a.mode=='prepared-reopen' else 'COMMITTED'
    need(contract['status']==expected,'Actual interface/prepared/committed status required')
    if a.mode=='interface': need(not (system/'estado/ACTIVO.json').exists() and contract['all_adoption_gates_met'] is False,'No diagnostic adoption claim')
    elif a.mode=='prepared-reopen': need(read(S/'estado/ACTIVO.json')['life_id']==PARENT,'Prepared MAIN must remain unselected')
    else: need(read(S/'estado/ACTIVO.json')['life_id']==MAIN and contract['all_adoption_gates_met'] is True,'Actual committed selection')
    proof=P/'control'/(tag+'.json'); marker=P/'PI11_ROOT_NATIVE_WRITER.lock'
    need(not proof.exists() and not marker.exists() and not (RP/'EJECUCION_MATERIAL.lock').exists(),'No repeated phase or overlapping owner')
    guard=load('PI11_public_exact_closed_guard',H/'comprobar_proceso_PI11_R01.py'); before_guard=guard.inspect('PI11_public_before',system,life); need(before_guard['no_live_affected_writer'],'Prove affected writer closed')
    prior=load('PI11_public_budget_continuity',H/'ledger_continuidad_PI11_R02.py').ledger()
    need(prior['charged_ticks']+bound<=budget['Native_ticks_all_new_branches'] and prior['world_count']<=budget['new_worlds_all'],'Aggregate Native/world budget insufficient')
    card,before=view(system,life); initial=card['physical']['tick']; parentcard=read(S/'estado/vidas'/PARENT/'VIDA.json')
    protected=[S/'estado/vidas'/PARENT/'VIDA.json',S/parentcard['snapshot']]
    if a.mode=='interface': protected += [S/'estado/ACTIVO.json']
    parenthashes={str(p):sha(p) for p in protected}; commands=[]; records=[]; error=None; owner=None
    source=RP/'propietario_diagnostico.py'; need(sha(source)==DRIVER_SHA,'Pinned outer Job supervisor')
    text=source.read_text('utf-8-sig'); anchor="'--max-segundos','7200'"; need(text.count(anchor)==1,'Exact owner horizon anchor'); text=text.replace(anchor,"'--max-segundos','900'"); ast.parse(text)
    write(proof.with_suffix('.INTENT.json'),{'schema':'DEE.PI11.public_finite_owner_intent.R01','phase':a.mode,'life_id':life,'initial_tick':initial,'finite_bound':bound,'proof':str(proof),'started_utc':datetime.now(timezone.utc).isoformat(),'ledger_before':prior})
    write(marker,{'pid':os.getpid(),'life_id':life,'tag':tag,'phase':a.mode,'finite_bound':bound})
    d=types.ModuleType('PI11_fixed_public_outer_owner'); d.__file__=str(source); exec(compile(text,str(source)+':PI11_public_fixed_900_seconds','exec'),d.__dict__); d.configure(P,system,PY)
    def cli(command,label):
        r=subprocess.run(command,cwd=system,capture_output=True,text=True,encoding='utf8',timeout=300,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0)); out=P/'ensayos'/(tag+'_'+label+'.CLI.json')
        value=None
        try: value=json.loads(r.stdout) if r.stdout.strip() else None
        except json.JSONDecodeError: pass
        rec={'label':label,'command':command,'exit_code':r.returncode,'stdout':r.stdout,'stderr':r.stderr,'parsed':value}; write(out,rec); commands.append({'path':str(out),'sha256':sha(out),'label':label,'command':command,'exit_code':r.returncode}); need(r.returncode==0 and value is not None,'Public command failed; preserve original request ID, no resend'); return value
    try:
        if a.mode in ('interface','committed-use','committed-reopen'): cli([str(PY),'-I','-B','-X','utf8',str(system/'gestionar.py'),'pi11-estado'],'estado_antes')
        owner=d.Owner(life,tag)
        with owner:
            if a.mode in ('interface','committed-use'):
                identifier=tag+'_EP'
                result=cli([str(PY),'-I','-B','-X','utf8',str(system/'gestionar.py'),'pi11-usar','--id',identifier,'--esperar','240'],'uso_publico')
                row=owner.q.get(identifier); need(row and row['status']=='completed','Original public receipt completed'); value=json.loads(row['result']); need(value['before_tick']==initial and 0<=value['after_tick']-initial<=2016,'Fixed one-opportunity horizon'); records.append({'id':identifier,'literal':{'modo':'eci01-pi11-episodio'},'before_tick':value['before_tick'],'after_tick':value['after_tick'],'ticks':value['after_tick']-value['before_tick'],'rows':value['result']['rows']})
                if a.mode=='interface':
                    value=owner.material(tag+'_BALANCE',{'modo':'eci01-balance','izquierda':14,'derecha':3},feedback='omit',actuator='closed',allow_failure=True)
                    need(value.get('status','completed') not in ('failed_preserved','uncertain','rejected_invalid'),'Balance failed; preserve receipt')
                    need(value['before_tick']==records[-1]['after_tick'] and 0<=value['after_tick']-value['before_tick']<=1300,'Fixed comparison horizon'); actual=value['result']['rows'][0]['early_physical_choice']; records.append({'id':tag+'_BALANCE','literal':{'modo':'eci01-balance','izquierda':14,'derecha':3},'before_tick':value['before_tick'],'after_tick':value['after_tick'],'ticks':value['after_tick']-value['before_tick'],'actual':actual,'expected':1,'correct':actual==1,'rows':value['result']['rows']}); need(actual==1,'Actual public comparison is not correct')
            else:
                value=owner.material(tag+'_ESTADO',{'modo':'eci01-pi11-estado'},feedback='omit',actuator='closed',allow_failure=True); need(value['before_tick']==value['after_tick']==initial,'State-only reopening must advance zero Native ticks'); records.append({'id':tag+'_ESTADO','before_tick':initial,'after_tick':initial,'ticks':0,'rows':value['result']['rows']})
            if a.mode in ('interface','committed-use'):
                # Synchronize the persistent habitat clock after the inherited
                # comparison as a zero-tick state read, without another offer.
                state=owner.material(tag+'_ESTADO_FINAL',{'modo':'eci01-pi11-estado'},feedback='omit',actuator='closed',allow_failure=True)
                need(state['before_tick']==state['after_tick']==records[-1]['after_tick'],'Final technical state advances zero ticks')
            owner.control('guardar')
    except BaseException as exc: error={'type':type(exc).__name__,'detail':str(exc),'automatic_retry':False}
    if owner is not None and owner.proc is not None and owner.proc.poll() is None:
        write(P/'control'/(tag+'.OWNER_VIVO.json'),{'pid':owner.proc.pid,'life_id':life,'error':error,'forced_kill':False,'automatic_retry':False})
        while owner.proc.poll() is None:
            try: owner.sample(); d.time.sleep(.1)
            except KeyboardInterrupt: pass
        if owner.job is not None: d.pc.close_job(owner.job); owner.job=None
    closed=bool(owner is not None and owner.proc is not None and owner.proc.poll()==0 and not (owner.q.get_meta('owner')or{}).get('running'))
    final,after=view(system,life); closed_guard=guard.inspect('PI11_public_after',system,life) if closed else None
    valid=bool(closed_guard and closed_guard['no_live_affected_writer']); need(final['physical']['tick']-initial<=bound,'Actual aggregate public tick bound')
    unchanged=parenthashes=={p:sha(Path(p)) for p in parenthashes}
    if not unchanged: error={'type':'PROTECTED_ORIGINAL_CHANGED','automatic_retry':False}
    if not valid and error is None: error={'type':'CLOSED_PROCESS_QUEUE_NOT_PROVEN','automatic_retry':False}
    equal=all(before[k]==after[k] for k in ('physical','causal_prefix_sha256','interfaces','phase','pending_native','native_receipts'))
    result={'schema':'DEE.PI11.actual_public_interface_owner.R01','phase':a.mode,'life_id':life,'system':str(system),'tag':tag,'closed':closed,'owner_closed':closed,'error':error,'initial_tick':initial,'final_tick':final['physical']['tick'],'new_ticks':final['physical']['tick']-initial,'new_Native_ticks':final['physical']['tick']-initial,'snapshot_sha256':final['snapshot_sha256'],'Native_executed':True,'material_use_completed':bool(a.mode in ('interface','committed-use') and records and error is None),'product_originals_modified':False if a.mode=='interface' else None,'operational_state_valid':valid and error is None,'pending_reconciled':valid,'physical_unchanged':equal,'Native_components_equal_on_zero_reopening':equal,'records':records,'commands':commands,'owner_start_command':None if owner is None else owner.cmd,'owner_control_operations':['guardar','detener'],'closed_process_queue':closed_guard,'protected_original_unchanged':unchanged,'protected_hashes':parenthashes,'outer_job_memory_limit_bytes':536870912,'owner_finite_host_max_seconds':900,'automatic_retry':False,'before_snapshot':{'sha256':card['snapshot_sha256'],'physical':before['physical']},'after_snapshot':{'sha256':final['snapshot_sha256'],'physical':after['physical']}}
    result['finite_bound']=bound
    write(proof,result)
    if closed and valid and marker.exists(): marker.unlink()
    print(json.dumps({'proof':str(proof),'phase':a.mode,'closed':closed,'error':error,'new_ticks':result['new_ticks'],'final_tick':result['final_tick'],'snapshot_sha256':final['snapshot_sha256']},ensure_ascii=False)); raise SystemExit(0 if closed and valid and error is None else 1)
if __name__=='__main__': main()
