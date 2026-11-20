"""PI11 public saved-state read or one EP on an existing paused owner.

Standard library only. No Runtime/Store/owner creation, policy, automatic
retry, supply/reset, desired answer, route choice or learned-memory update.
"""
from pathlib import Path
from datetime import datetime
import argparse,ctypes,hashlib,importlib.util,json,os,re,sqlite3,subprocess,sys,time
VERSION='DEE.PI11.fixed_public_manager.R01'
KEY='DEE.Cognitive.PI11.persistent_habitat.native_continuation.R01'
PARSER_SHA='dbb2a5e15d70c64112d36505197f4aebf6ff7d4092972923e17cd60c10a1c873'
def need(ok,msg):
    if not ok:raise ValueError(msg)
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def regular(p):
    for n in(p,*p.parents):need(not n.exists()or not(n.is_symlink()or getattr(n.lstat(),'st_file_attributes',0)&1024),'No reparse public path')
def root():return Path(__file__).resolve().parents[1]
def saved_state(system):
    regular(system);profile=read(system/'contratos/PI11_USO_OPERATIVO_R01.json');life=profile['life_id'];active=system/'estado/ACTIVO.json'
    need(profile.get('schema')=='DEE.PI11.exact_operational_permission.R01'and profile.get('all_adoption_gates_met')is True,'Exact validated PI11 contract')
    if active.is_file():need(read(active).get('life_id')==life and profile.get('status')=='COMMITTED','Selected PI11 must be COMMITTED')
    else:
        marker=read(system/'contratos/PI11_INTERFAZ_DIAGNOSTICA_R01.json')
        need(system.parent.parent.name=='estados'and system.parent.parent.parent.name=='PROGRESION_INTEGRADA_11'and marker.get('schema')=='DEE.PI11.explicit_product_interface_diagnostic.R01'and marker.get('life_id')==life and Path(marker['system']).resolve()==system.resolve()and marker.get('contract_sha256')==sha(system/'contratos/PI11_USO_OPERATIVO_R01.json')and marker.get('allow_material_interface_test')is True and marker.get('not_a_principal')is True,'Only explicitly scoped interface test without ACTIVO')
    card=read(system/'estado/vidas'/life/'VIDA.json');snapshot=system/card['snapshot'];regular(snapshot)
    need(card['life_id']==card['world_id']==life and sha(snapshot)==card['snapshot_sha256'],'Complete current saved identity mismatch')
    parser=system.parent/'reproducibilidad/observador_pasivo.py'
    if not parser.is_file():
        need(not active.exists(),'Product needs its preserved reproducibility parser')
        parser=Path(profile['diagnostic_passive_parser_source'])
    need(sha(parser)==PARSER_SHA,'Exact passive snapshot parser')
    sp=importlib.util.spec_from_file_location('PI11_saved_parser_no_Native',parser);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);v=m.snapshot_view(snapshot)
    need(v['encoded_sha256']==card['snapshot_sha256']and all(v['physical'][k]==card['physical'][k]for k in('N','tick','RAW_sha256','clocks_sha256')),'Saved Native/card mismatch')
    state=json.loads(v['metadata'][KEY]);need(state.get('ready')and state['ordinal']==len(state['rows'])and not state.get('pending')and not state.get('uncertain'),'Incomplete future preserved; no inferred state')
    protocol=read(system/'capacidades/PROTOCOLO_PI11_R01.json');need(sha(system/'capacidades/PROTOCOLO_PI11_R01.json')==state['protocol_sha256']==profile['PI11_protocol_sha256'],'Exact current habitat protocol')
    folder=system/'estado/servicios_locales'/life/'PI11_HABITAT_ADAPTATIVO_R01/PI11_HABITAT_R01';environment=read(folder/'ESTADO.json')
    need(environment['tick']==card['physical']['tick']and environment['open_offer']is None,'Saved habitat/Native continuation mismatch')
    result={'version':VERSION,'life_id':life,'physical_saved':card['physical'],'snapshot_sha256':card['snapshot_sha256'],'status':profile['status'],'opportunities_consumed':state['ordinal'],'opportunity_limit':protocol['max_opportunities'],'opportunities_available':protocol['max_opportunities']-state['ordinal'],'resource_slots_remaining':sum(not r['delivered']for r in environment['slots']),'permissions':environment['permissions'],'certificate':environment['certificate'],'observation':'Frozen saved checkpoint and environmental state; not instantaneous live state. No material query, tick or owner.','Native_imports_in_adapter':0,'new_Native_ticks':0,'no_hidden_reset_or_supply':True}
    return life,card,state,result
def live_process(owner):
    need(os.name=='nt'and type(owner.get('pid'))is int and owner['pid']>0,'Existing actual Windows owner PID required')
    k=ctypes.WinDLL('kernel32',use_last_error=True);k.OpenProcess.argtypes=[ctypes.c_uint32,ctypes.c_int,ctypes.c_uint32];k.OpenProcess.restype=ctypes.c_void_p;k.GetExitCodeProcess.argtypes=[ctypes.c_void_p,ctypes.POINTER(ctypes.c_uint32)];k.GetProcessTimes.argtypes=[ctypes.c_void_p,*([ctypes.c_void_p]*4)];k.CloseHandle.argtypes=[ctypes.c_void_p]
    handle=k.OpenProcess(0x1000,False,owner['pid']);need(bool(handle),'Owner PID absent/inaccessible; no queue write')
    try:
        code=ctypes.c_uint32();need(k.GetExitCodeProcess(handle,ctypes.byref(code))and code.value==259,'Owner no longer running; no queue write');created=ctypes.c_ulonglong();exited=ctypes.c_ulonglong();kernel=ctypes.c_ulonglong();user=ctypes.c_ulonglong()
        need(k.GetProcessTimes(handle,ctypes.byref(created),ctypes.byref(exited),ctypes.byref(kernel),ctypes.byref(user)),'Cannot prove actual process identity');born=created.value/10000000-11644473600
        need(datetime.fromisoformat(owner['wall_utc']).timestamp()>=born-2,'Cached PID reused; no queue write')
    finally:k.CloseHandle(handle)
def use(system,identifier,wait):
    need(re.fullmatch('[A-Za-z0-9][A-Za-z0-9_.-]{0,68}',identifier or'')is not None and 0<wait<=600,'Fresh explicit ID and bounded wait<=600')
    life,card,m,state=saved_state(system);need(state['opportunities_available']>0 and state['resource_slots_remaining']>0,'Finite habitat exhausted; no reset')
    db=system/'estado/servicios_persistentes'/life/'cola.sqlite3';regular(db);controls=[identifier+'_reanudar',identifier+'_pausar'];con=sqlite3.connect(db.resolve().as_uri()+'?mode=ro',uri=True)
    try:
        con.execute('PRAGMA query_only=ON');row=con.execute("SELECT value FROM meta WHERE key='owner'").fetchone();need(row is not None,'Existing owner cache required');owner=json.loads(row[0]);need(owner.get('life_id')==life and owner.get('running')is True and owner.get('paused')is True and owner.get('uncertain_external_result')is False,'Start existing owner paused and reconcile first; adapter does not start it')
        need(not con.execute("SELECT COUNT(*) FROM requests WHERE status IN('queued','processing','uncertain')").fetchone()[0],'Outstanding request; never resend or purge')
        for rid in(identifier,*controls):need(con.execute('SELECT id FROM requests WHERE id=?',(rid,)).fetchone()is None,'Used ID; inspect original receipt')
        need(owner['tick']==owner['last_saved_tick']==card['physical']['tick'],'In-flight or unsaved owner differs from checkpoint');live_process(owner)
    finally:con.close()
    commands=[];literal=[{'modo':'eci01-pi11-episodio'}];client=system/'app/cliente_mente_unificada.py'
    def call(rid,operation,extra=()):
        command=[sys.executable,'-I','-B','-X','utf8',str(client),'--cola',str(db),'--id',rid,'--esperar','0'if operation=='sesion'else'30',operation,*extra]
        result=subprocess.run(command,cwd=system,capture_output=True,text=True,encoding='utf8',errors='strict',shell=False,timeout=45,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0));value=json.loads(result.stdout)if result.stdout.strip()else None;commands.append({'id':rid,'operation':operation,'exit_code':result.returncode,'result':value});need(result.returncode==0 and value is not None,'Public client failed; original IDs preserved');return value
    admission=call(identifier,'sesion',('--retorno','omit','--actuador','closed','--situaciones',json.dumps(literal,separators=(',',':'))));need(admission.get('admission')=='queued','One newly queued fixed opportunity required');resumed=call(controls[0],'reanudar');need(resumed.get('request',{}).get('status')=='completed','Resume incomplete; preserve original request')
    end=time.monotonic()+wait;row=None
    while time.monotonic()<end:
        con=sqlite3.connect(db.resolve().as_uri()+'?mode=ro',uri=True);con.row_factory=sqlite3.Row
        try:value=con.execute('SELECT * FROM requests WHERE id=?',(identifier,)).fetchone();row=None if value is None else dict(value)
        finally:con.close()
        if row and row['status']in('completed','failed_preserved','uncertain','rejected_invalid'):break
        time.sleep(.05)
    need(row is not None and row['status']in('completed','failed_preserved','uncertain','rejected_invalid'),'Original request still pending/processing; no guessed outcome or resend');paused=call(controls[1],'pausar');need(paused.get('request',{}).get('status')=='completed','Pause incomplete; preserve original IDs')
    print(json.dumps({'version':VERSION,'life_id':life,'request_id':identifier,'literal':literal,'host_selected_query_route_or_renewal':False,'request':row,'technical_controls':commands,'automatic_retry':False,'no_hidden_new_owner':True},ensure_ascii=False,indent=2));return 0 if row['status']=='completed'else 3
def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('mode',choices=('pi11-estado','pi11-usar'));ap.add_argument('--id');ap.add_argument('--esperar',type=float,default=240);a=ap.parse_args();system=root()
    try:
        if a.mode=='pi11-estado':print(json.dumps(saved_state(system)[3],ensure_ascii=False,indent=2));return 0
        return use(system,a.id,a.esperar)
    except Exception as exc:print(json.dumps({'version':VERSION,'error':type(exc).__name__,'detail':str(exc),'automatic_retry':False,'new_owner':False},ensure_ascii=False),file=sys.stderr);return 2
if __name__=='__main__':raise SystemExit(main())
