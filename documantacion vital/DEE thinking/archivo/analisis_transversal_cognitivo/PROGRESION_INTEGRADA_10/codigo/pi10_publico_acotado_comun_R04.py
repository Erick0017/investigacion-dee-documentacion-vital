"""Root-only published public Owner/client utilities; no Native on import."""
from pathlib import Path
from datetime import datetime,timezone
import ast,hashlib,importlib.util,json,os,time,types
P=Path(__file__).resolve().parents[1];H=P/'codigo';P9=P.with_name('PROGRESION_INTEGRADA_09');C=P.parents[2]/'DEE Cognitive 2.0';S=C/'sistema';RP=C/'reproducibilidad';PY=C/'motor/python313/python.exe';LIFE='ECI02_PI03_REPRO_PI04_PI05_PI07_PI10_REAL2_01';OLD='ECI02_PI03_REPRO_PI04_PI05_PI07_PI09_DISCOVERY_01';KEY='DEE.Cognitive.PI10.adaptive_query.two_native_traces.R02';LOCK=P/'PI10_ROOT_NATIVE_WRITER.lock'
def need(ok,msg):
 if not ok:raise ValueError(msg)
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(name,p,pin=None):
 if pin:need(sha(p)==pin,'Reviewed public helper changed')
 spec=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def write(p,v):
 p.parent.mkdir(parents=True,exist_ok=True);temp=p.with_name(p.name+'.WRITING')
 with temp.open('w',encoding='utf8')as f:json.dump(v,f,ensure_ascii=False,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
 os.replace(temp,p)
def parser():return load('PI10_public_fixed_saved_snapshot',RP/'observador_pasivo.py','dbb2a5e15d70c64112d36505197f4aebf6ff7d4092972923e17cd60c10a1c873')
def snapshot(reader):
 card=read(S/'estado/vidas'/LIFE/'VIDA.json');file=S/card['snapshot'];need(card['life_id']==card['world_id']==LIFE and sha(file)==card['snapshot_sha256'],'Exact full current product identity');v=reader.snapshot_view(file);need(all(v['physical'][k]==card['physical'][k]for k in('N','tick','RAW_sha256','clocks_sha256')),'Current Native/card mismatch');return card,v
def brief(v):return{k:v[k]for k in('physical','encoded_sha256','causal_prefix_sha256','interfaces','pending_native','native_receipts','phase','scope')}
def selection(selected):
 active=read(S/'estado/ACTIVO.json');profile=read(S/'contratos/PI10_USO_OPERATIVO_R01.json');need(active['life_id']==(LIFE if selected else OLD),'Actual selected/unselected product phase mismatch');need(profile.get('schema')=='DEE.PI10.exact_operational_permission.v2'and profile.get('life_id')==LIFE and profile.get('status')==('COMMITTED'if selected else'PREPARED_DIAGNOSTIC')and profile.get('all_adoption_gates_met')is True,'Exact actual prepared/committed PI10 permission required');proof=P/'control'/('ADOPCION_PRODUCTO_PI10_R02.json'if selected else'PREPARACION_TRASLADO_PRODUCTO_PI10_R02.json');p=read(proof);need(p['life_id']==LIFE and p['phase']==('COMMITTED'if selected else'PREPARED_MOVED_NOT_PROMOTED'),'Actual whole-move/adoption proof required');return profile,proof
def guard():
 g=load('PI10_public_closed_process_queue',H/'comprobar_proceso_PI10_R02.py','21d41a1e429f135d100f17826258561dc9f98ca52a465cc2015f30efb5966adb').inspect('PI10_product_public_before_owner',S,LIFE);need(g['no_live_affected_writer'],'Current product writer/queue not proven closed');return g
def old_protected():
 cardfile=S/'estado/vidas'/OLD/'VIDA.json';card=read(cardfile);need(card['physical']['tick']==922371 and card['snapshot_sha256']=='72743ad2fc708e41c2529af8f7192fe1087184562e4cd094f469384faedcd331','Historical D original must stay protected');return {str(f):sha(f)for f in(cardfile,S/card['snapshot'])}
def idle_ownerlib(seconds):
 need(120<=seconds<=600,'Finite existing Owner lifetime');source=RP/'propietario_diagnostico.py';need(sha(source)=='e7053088b6492d9d10abe1c861da560de1fb1f4a9d00468661df53782523e52b','Published512MiB Owner changed');text=source.read_text('utf-8-sig');anchor="'--max-segundos','7200'";need(text.count(anchor)==1,'Finite Owner anchor changed');text=text.replace(anchor,"'--max-segundos',str(ROOT_MAX_SECONDS)");anchor='def wait(self,identifier,limit=240):';need(text.count(anchor)==1,'Published queue wait anchor changed');text=text.replace(anchor,'def wait(self,identifier,limit=120):');ast.parse(text);m=types.ModuleType('PI10_public_literal_owned_finite_lifetime');m.__file__=str(source);m.ROOT_MAX_SECONDS=seconds;exec(compile(text,str(source)+':PI10_only_finite_seconds_and_wait_bound','exec'),m.__dict__)
 # Host library caps do not replace or edit the inherited Native world config.
 for name in('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[name]='1'
 m.configure(P,S,PY);return m
def client():
 m=load('PI10_public_P9_literal_client',P9/'codigo/reabrir_producto_PI09_0_R02.py','fd3aab3aaaf1e4940d4fc0e55670301dbbaa0289a534509ff183d2e021adf88f');m.P=P;m.C=C;m.S=S;m.RP=RP;m.PY=PY;m.LIFE=LIFE;return m
def owned_closed(owner):return bool(owner is not None and owner.proc is not None and owner.proc.poll()==0 and not(owner.q.get_meta('owner')or{}).get('running')and not owner.q.outstanding())
def retain_live(owner):
 if owner is None or owner.proc is None:return
 while owner.proc.poll()is None:
  try:owner.sample();time.sleep(.1)
  except KeyboardInterrupt:pass
 if owner.job is not None:ownerlib=load('PI10_public_existing_process_tools',S/'app/process_control.py');ownerlib.close_job(owner.job);owner.job=None
def equality(a,b):
 fields={k:a[k]==b[k]for k in('physical','causal_prefix_sha256','interfaces','pending_native','native_receipts','phase')};changed=[k for k in set(a['metadata'])|set(b['metadata'])if a['metadata'].get(k)!=b['metadata'].get(k)];allowed=lambda k:k=='DEE.Cognitive.System.1.1.life.v1'or k=='DEE.Cognitive.System.1.1.PERSISTENT_SERVICE.v1'or k.startswith('DEE.Cognitive.System.1.1.PERSISTENT_SERVICE.v1.queue.');return fields,changed,all(allowed(k)for k in changed)
def code_pins():
 files=[S/'gestionar.py',S/'app/mundo_genesis_apd05.py',S/'capacidades/pi10_consulta_adaptativa_R02.py',S/'capacidades/pi10_permiso_operativo_R02.py',S/'capacidades/PROTOCOLO_PI10_R02.json',S/'capacidades/PI10_EXPERIMENTO_R02.json',S/'capacidades/PI10_TRANSPORTE_ANCESTRAL_R01.json',S/'capacidades/PI10_PLUGINS_R01.json',S/'contratos/PI10_USO_OPERATIVO_R01.json'];return {str(f):sha(f)for f in files}
