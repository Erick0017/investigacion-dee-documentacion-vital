"""Pure prospective client fix: paused queue needs explicit technical resume."""
from pathlib import Path
import ast,hashlib,json
H=Path(__file__).resolve().parent;src=H/'pi10_gestor_publico_R02.py';out=H/'pi10_gestor_publico_R03.py';text=src.read_text('utf8').replace('subprocess,sys','subprocess,sys,time').replace("VERSION='DEE.PI10.exact_public_manager.R02'","VERSION='DEE.PI10.exact_public_manager.R03'")
start=text.index('def use(');end=text.index('def main():',start)
new='''def use(system,identifier,wait):
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
'''
text=text[:start]+new+text[end:];ast.parse(text)
def exact(p,data):
 p.parent.mkdir(parents=True,exist_ok=True)
 if p.exists():assert p.read_bytes()==data
 else:
  with p.open('xb')as f:f.write(data)
exact(out,text.encode('utf8'));generator=(H/'preparar_gestor_publico_PI10_R02.py').read_text('utf8').replace('GESTOR_PUBLICO_PI10_R02_PREPARADO','GESTOR_PUBLICO_PI10_R03_PREPARADO').replace('pi10_gestor_publico_R02.py','pi10_gestor_publico_R03.py').replace('DEE.PI10.public_manager.staged_exact_delta.R02','DEE.PI10.public_manager.staged_exact_delta.R03');ast.parse(generator);namespace={'__file__':str(H/'preparar_gestor_publico_PI10_R02.py'),'__name__':'PI10_R03_stage_only'};exec(compile(generator,'PI10_R03_manager_fixed_resume_pause_only','exec'),namespace)
