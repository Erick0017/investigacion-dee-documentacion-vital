"""Synthetic transport-only unit test; no actual SQLite/DEE/Owner execution."""
from pathlib import Path
import contextlib,hashlib,importlib.util,io,json,types
P=Path(__file__).resolve().parents[1];H=P/'codigo';source=H/'GESTOR_PUBLICO_PI10_R03_PREPARADO/app/pi10_gestor_publico_R03.py';s=importlib.util.spec_from_file_location('PI10_synthetic_public_transport_test',source);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);fixture=P/'fuentes/PRUEBA_GESTOR_PUBLICO_SINTETICA_R03';db=fixture/'estado/servicios_persistentes'/m.MAIN/'cola.sqlite3';db.parent.mkdir(parents=True,exist_ok=True)
if not db.exists():db.write_bytes(b'SYNTHETIC FILE ONLY: no SQLite and no Native state\n')
identifier='PI10_SYNTHETIC_TRANSPORT_ONLY';calls=[];connections=[]
class Cursor:
 def __init__(self,value):self.value=value
 def fetchone(self):return self.value
class Connection:
 def execute(self,query,args=()):
  if query.startswith('PRAGMA'):return Cursor(None)
  if "key='owner'"in query:return Cursor((json.dumps({'life_id':m.MAIN,'running':True,'paused':True,'uncertain_external_result':False,'tick':100,'last_saved_tick':100,'pid':123456}),))
  if query.startswith('SELECT COUNT'):return Cursor((0,))
  if query.startswith('SELECT id'):return Cursor(None)
  if query.startswith('SELECT *'):return Cursor({'id':identifier,'status':'completed','result':'{"synthetic_only":true}'})
  raise AssertionError('Unexpected SQL '+query)
 def close(self):pass
def connect(*args,**kwargs):c=Connection();connections.append(c);return c
def run(command,**kwargs):
 calls.append(command);operation='sesion'if'sesion'in command else'reanudar'if'reanudar'in command else'pausar'if'pausar'in command else None;assert operation is not None
 if operation=='sesion':
  assert json.loads(command[command.index('--situaciones')+1])==[{'modo':'eci01-pi10-episodio'}];assert command[command.index('--esperar')+1]=='0';value={'admission':'queued','id':identifier,'status':'waiting_or_processing'}
 else:value={'request':{'status':'completed','id':command[command.index('--id')+1]}}
 return types.SimpleNamespace(returncode=0,stdout=json.dumps(value),stderr='')
m.saved_state=lambda system:({'physical':{'tick':100}},{'ordinal':13},{'synthetic_only':True});m.live_process=lambda owner:None;m.sqlite3.connect=connect;m.subprocess.run=run
capture=io.StringIO()
with contextlib.redirect_stdout(capture):exitcode=m.use(fixture,identifier,120)
packet=json.loads(capture.getvalue());operations=['sesion'if'sesion'in c else'reanudar'if'reanudar'in c else'pausar'for c in calls];assert exitcode==0 and operations==['sesion','reanudar','pausar']and packet['submitted_literal']==[{'modo':'eci01-pi10-episodio'}]and packet['host_selected_query_or_route']is False and len(calls)==3
report={'schema':'DEE.PI10.synthetic_public_transport.fixed_sequence_test.R03','synthetic_only':True,'not_a_Native_or_functional_capability_test':True,'DEE_imports':0,'actual_SQLite_connections':0,'actual_subprocesses':0,'Native_ticks':0,'operation_sequence':operations,'material_EP_count':1,'all_three_IDs_distinct':len({c[c.index('--id')+1]for c in calls})==3,'material_literal_exact':True,'expected_or_target_passed':False,'helper_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'published_client_commands':calls};out=P/'control/PRUEBA_GESTOR_PUBLICO_R03_SINTETICA.json'
with out.open('x',encoding='utf8')as f:json.dump(report,f,ensure_ascii=False,indent=2);f.write('\n')
print(json.dumps({'proof':str(out),'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'operations':operations,'Native':0}))
