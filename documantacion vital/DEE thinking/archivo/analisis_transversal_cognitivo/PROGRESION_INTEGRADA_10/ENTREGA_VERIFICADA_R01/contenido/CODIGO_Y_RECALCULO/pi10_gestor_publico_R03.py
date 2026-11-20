"""Small stdlib public PI10 adapter; state is frozen-file observation only.

Use submits exactly EP to the existing paused persistent owner through the
published queue client. No Runtime import, policy, answer, reset, new owner,
retry or implicit new life is present in this adapter.
"""
from pathlib import Path
from datetime import datetime,timezone
import argparse,ctypes,hashlib,importlib.util,json,os,re,sqlite3,subprocess,sys,time
MAIN='ECI02_PI03_REPRO_PI04_PI05_PI07_PI10_REAL2_01';KEY='DEE.Cognitive.PI10.adaptive_query.two_native_traces.R02';VERSION='DEE.PI10.exact_public_manager.R03';PARSER_SHA='dbb2a5e15d70c64112d36505197f4aebf6ff7d4092972923e17cd60c10a1c873'
def need(ok,msg):
 if not ok:raise ValueError(msg)
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def regular(p):
 for n in(p,*p.parents):need(not n.exists()or not(n.is_symlink()or getattr(n.lstat(),'st_file_attributes',0)&1024),'No linked public system or queue')
def root():return Path(__file__).resolve().parents[1]
def saved_state(system):
 regular(system);active=read(system/'estado/ACTIVO.json');profile=read(system/'contratos/PI10_USO_OPERATIVO_R01.json');need(active.get('life_id')==MAIN and profile.get('schema')=='DEE.PI10.exact_operational_permission.v2'and profile.get('life_id')==MAIN and profile.get('status')=='COMMITTED'and profile.get('all_adoption_gates_met')is True,'PI10 public commands require the actually selected COMMITTED REAL2; no fallback to another life');cardfile=system/'estado/vidas'/MAIN/'VIDA.json';card=read(cardfile);snapshot=system/card['snapshot'];regular(snapshot);need(card['life_id']==card['world_id']==MAIN and sha(snapshot)==card['snapshot_sha256'],'Current full saved identity mismatch');parser=system.parent/'reproducibilidad/observador_pasivo.py';need(sha(parser)==PARSER_SHA,'Published passive snapshot parser changed');spec=importlib.util.spec_from_file_location('PI10_public_saved_snapshot_no_Runtime',parser);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);v=module.snapshot_view(snapshot);m=json.loads(v['metadata'][KEY]);need(m.get('ready')and m.get('admitted')and m['ordinal']==len(m['rows'])and not m.get('pending')and not m.get('uncertain')and m.get('admission_control')=={'role':'evaluation','arm':'real','trace_control':'none','force_query':None},'Closed acquired unforced PI10 history required; preserve any interrupted future');need(v['physical']==card['physical']and v['encoded_sha256']==card['snapshot_sha256'],'Current saved Native/card mismatch');return card,m,{'version':VERSION,'life_id':MAIN,'physical_saved':card['physical'],'snapshot_sha256':card['snapshot_sha256'],'used_original_offers':m['ordinal'],'total_original_offers':18,'remaining_original_offers':18-m['ordinal'],'assistance':'Operator initiates one opportunity; fixed environment and interfaces. Native history selects material query and subsequent route.','observation':'Saved complete checkpoint, not instantaneous live state. No Native query/tick/Owner was executed by pi10-estado.','Native_imports_in_adapter':0,'new_Native_ticks_in_state':0,'no_reset_or_new_supply':True}
def live_process(owner):
 need(os.name=='nt'and type(owner.get('pid'))is int and owner['pid']>0,'Windows actual existing owner PID required');k=ctypes.WinDLL('kernel32',use_last_error=True);k.OpenProcess.argtypes=[ctypes.c_uint32,ctypes.c_int,ctypes.c_uint32];k.OpenProcess.restype=ctypes.c_void_p;k.GetExitCodeProcess.argtypes=[ctypes.c_void_p,ctypes.POINTER(ctypes.c_uint32)];k.GetProcessTimes.argtypes=[ctypes.c_void_p,*([ctypes.c_void_p]*4)];k.CloseHandle.argtypes=[ctypes.c_void_p];handle=k.OpenProcess(0x1000,False,owner['pid']);need(bool(handle),'Owner PID absent/inaccessible; no request queued')
 try:
  code=ctypes.c_uint32();need(k.GetExitCodeProcess(handle,ctypes.byref(code))and code.value==259,'Owner no longer running; no request queued');created=ctypes.c_ulonglong();exited=ctypes.c_ulonglong();kernel=ctypes.c_ulonglong();user=ctypes.c_ulonglong();need(k.GetProcessTimes(handle,ctypes.byref(created),ctypes.byref(exited),ctypes.byref(kernel),ctypes.byref(user)),'Cannot identify actual owner creation time');born=created.value/10000000-11644473600;stamp=datetime.fromisoformat(owner['wall_utc']).timestamp();need(stamp>=born-2,'Cached PID was reused; no request queued')
 finally:k.CloseHandle(handle)
def use(system,identifier,wait):
 need(re.fullmatch('[A-Za-z0-9][A-Za-z0-9_.-]{0,68}',identifier)is not None and 0<wait<=120,'Explicit fresh ID and bounded client wait (0,120] required');card,m,state=saved_state(system);need(m['ordinal']<18,'Original18-offer supply exhausted; no reset or hidden resupply');db=system/'estado/servicios_persistentes'/MAIN/'cola.sqlite3';regular(db);need(db.is_file(),'Existing persistent service required; no hidden owner/life creation');control_ids=[identifier+'_reanudar',identifier+'_pausar'];con=sqlite3.connect(db.resolve().as_uri()+'?mode=ro',uri=True)
 try:
  con.execute('PRAGMA query_only=ON');row=con.execute("SELECT value FROM meta WHERE key='owner'").fetchone();need(row is not None,'Owner cache absent; no request queued');owner=json.loads(row[0]);need(owner.get('life_id')==MAIN and owner.get('running')is True and owner.get('paused')is True and owner.get('uncertain_external_result')is False,'Start the existing ECI01 owner paused and reconcile pending operations before use; adapter does not start it');need(not con.execute("SELECT COUNT(*) FROM requests WHERE status IN('queued','processing','uncertain')").fetchone()[0],'Existing outstanding/uncertain request, never resend/purge')
  for request_id in(identifier,*control_ids):need(con.execute('SELECT id FROM requests WHERE id=?',(request_id,)).fetchone()is None,'ID already used; inspect receipt, never resend')
  need(owner['tick']==owner['last_saved_tick']==card['physical']['tick'],'Unsaved/in-flight owner differs from stable checkpoint');live_process(owner)
 finally:con.close()
 literal=[{'modo':'eci01-pi10-episodio'}];client=system/'app/cliente_mente_unificada.py';commands=[]
 def call(request_id,operation,extra=()):
  command=[sys.executable,'-I','-B','-X','utf8',str(client),'--cola',str(db),'--id',request_id,'--esperar','0'if operation=='sesion'else'30',operation,*extra];completed=subprocess.run(command,cwd=system,capture_output=True,text=True,encoding='utf8',errors='strict',shell=False,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0),timeout=45);value=json.loads(completed.stdout)if completed.stdout.strip()else None;commands.append({'operation':operation,'id':request_id,'exit_code':completed.returncode,'result':value});need(completed.returncode==0 and value is not None,'Published client failed; same ID preserved, no retry');return value
 admission=call(identifier,'sesion',('--retorno','omit','--actuador','closed','--situaciones',json.dumps(literal,separators=(',',':'))));need(admission.get('admission')=='queued','Expected one newly queued fixed EP only');resume=call(control_ids[0],'reanudar');need(resume.get('request',{}).get('status')=='completed','Resume control did not complete; preserve the original EP')
 deadline=time.monotonic()+wait;row=None
 while time.monotonic()<deadline:
  con=sqlite3.connect(db.resolve().as_uri()+'?mode=ro',uri=True);con.row_factory=sqlite3.Row
  try:value=con.execute('SELECT * FROM requests WHERE id=?',(identifier,)).fetchone();row=None if value is None else dict(value)
  finally:con.close()
  if row and row['status']in('completed','failed_preserved','uncertain','rejected_invalid'):break
  time.sleep(.05)
 need(row is not None and row['status']in('completed','failed_preserved','uncertain','rejected_invalid'),'Original material ID remains waiting/processing; no resend or guessed result');paused=call(control_ids[1],'pausar');need(paused.get('request',{}).get('status')=='completed','Pause control did not complete; preserve original IDs')
 print(json.dumps({'version':VERSION,'life_id':MAIN,'request_id':identifier,'submitted_literal':literal,'host_selected_query_or_route':False,'receipt_or_waiting':{'admission':'queued','request':row,'native_result_not_replaced':True},'technical_controls':commands,'automatic_retry':False,'no_hidden_new_owner':True,'scope':'Operator initiates one opportunity. Resume/pause only let the existing owner process the exact EP; no target, answer, route or recovery policy is selected.'},ensure_ascii=False,indent=2));return 0 if row['status']=='completed'else 3
def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('mode',choices=('pi10-estado','pi10-usar'));ap.add_argument('--id');ap.add_argument('--esperar',type=float,default=120);a=ap.parse_args();system=root()
 try:
  if a.mode=='pi10-estado':print(json.dumps(saved_state(system)[2],ensure_ascii=False,indent=2));return 0
  need(a.id is not None,'pi10-usar requires a unique explicit --id; never generates a retry ID');return use(system,a.id,a.esperar)
 except Exception as exc:print(json.dumps({'version':VERSION,'error':type(exc).__name__,'detail':str(exc),'automatic_retry':False,'no_hidden_owner_or_life':True},ensure_ascii=False),file=sys.stderr);return 2
if __name__=='__main__':raise SystemExit(main())
