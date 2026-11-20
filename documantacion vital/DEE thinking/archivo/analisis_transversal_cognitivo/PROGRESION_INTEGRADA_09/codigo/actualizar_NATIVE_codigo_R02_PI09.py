"""Root-only CAS upgrade of NATIVE imported0, before any PI09 request.

Default prepares a plan/beforeimages under codigo. --aplicar changes code and
administrative code/context pointers only. No Native import or state writes.
"""
from pathlib import Path
import argparse,datetime,hashlib,importlib.util,json,os,sqlite3
P=Path(__file__).resolve().parents[1];D=P/'estados/NATIVE';S=D/'sistema';PREP=P/'codigo/ACTUALIZACION_NATIVE_R02_PREPARADA'
PLAN=PREP/'PLAN.json';PROOF=PREP/'APLICACION.json'
PAIR=P/'pares/C_HEREDADA_T884835';C=P.parents[2]/'DEE Cognitive 2.0';RP=C/'reproducibilidad'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def require(ok,msg):
 if not ok:raise ValueError(msg)
def write(p,v):
 p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('x',encoding='utf8')as f:json.dump(v,f,ensure_ascii=False,indent=2);f.write('\n')
def inspect():
 require(not(P/'PI09_ROOT_NATIVE_WRITER.lock').exists(),'Hay un escritor/importador no cerrado')
 imported=read(D/'IMPORTACION_PI09.json');require(imported['closed']is True and imported['error']is None and imported['new_Native_ticks']==0,'Se requiere importación0 cerrada real')
 context=read(D/'CONTEXTO_EJECUCION.json');life=context['life'];require(life=='ECI02_PI03_REPRO_PI04_PI05_PI07_PI09_NATIVE_01','Sólo NATIVE exacta')
 lifehome=S/'estado/vidas'/life;card=read(lifehome/'VIDA.json');snapshot=S/card['snapshot'];db=S/'estado/servicios_persistentes'/life/'cola.sqlite3'
 require(not(S/'estado/ACTIVO.json').exists()and not(lifehome/'FUTURO_INTERRUMPIDO.json').exists()and not(S/'estado/locks'/(card['world_id']+'.lock')).exists(),'No se actualiza una vida seleccionada/interrumpida/abierta')
 require(card['physical']==read(PAIR/'EXPORTACION_SERVICIO.json')['physical']and card['physical']['tick']==884835,'NATIVE ya avanzó: no procede esta actualización')
 require(not any(Path(str(db)+x).exists()and Path(str(db)+x).stat().st_size for x in('-wal','-journal')),'SQLite con WAL/journal no vacío')
 con=sqlite3.connect(db.as_uri()+'?mode=ro&immutable=1',uri=True)
 try:
  require(con.execute('PRAGMA integrity_check').fetchone()[0]=='ok','SQLite no íntegra')
  owner=json.loads(con.execute("SELECT value FROM meta WHERE key='owner'").fetchone()[0]);require(owner.get('running')is False and owner.get('imported_not_yet_started')is True and not owner.get('pid'),'NATIVE debe seguir recién importada antes del primer Owner')
  require(con.execute("SELECT COUNT(*) FROM requests WHERE status IN('queued','processing','uncertain')").fetchone()[0]==0,'Transporte pendiente')
  require(not any('eci01-pi09-'in row[0]for row in con.execute('SELECT payload FROM requests')),'Ya hubo una petición PI09; conservar la revisión utilizada')
 finally:con.close()
 sp=importlib.util.spec_from_file_location('PI09_upgrade_passive',RP/'observador_pasivo.py');obs=importlib.util.module_from_spec(sp);sp.loader.exec_module(obs)
 v=obs.snapshot_view(snapshot);require(not any(k.startswith('DEE.Cognitive.PI09.')for k in v['metadata']),'Ya existe metadata de consulta PI09')
 require(v['encoded_sha256']==card['snapshot_sha256'],'Snapshot no coincide con ficha')
 active=C/'sistema/estado/ACTIVO.json';a=read(active);acard=C/'sistema/estado/vidas'/a['life_id']/'VIDA.json'
 critical=[lifehome/'VIDA.json',lifehome/'HISTORIA.jsonl',snapshot,db,active,acard,C/'sistema'/read(acard)['snapshot']]
 return context,life,{str(p):sha(p)for p in critical}
def prepare():
 require(not PREP.exists(),'Plan de actualización ya existe')
 for name in('pi09_transporte_heredado_R02.py','pi09_dispatcher_R02.py','pi09_consulta_selectiva_R02.py','SELLO_PI09_CONSULTA_R02.json'):
  require((P/'codigo'/name).is_file(),'Falta fuente R02 antes de preparar: '+name)
 seal=read(P/'codigo/SELLO_PI09_CONSULTA_R02.json')
 require(seal.get('schema')=='DEE.PI09.selective_consultation.source_seal.R02','Sello R02 prospectivo requerido')
 for name,digest in seal['files_sha256'].items():
  require(Path(name).name==name,'Miembro de sello no simple')
  source=P/'codigo'/name
  if not source.is_file():source=S/'capacidades'/name
  require(source.is_file()and sha(source)==digest,'Fuente R02 distinta del sello: '+name)
 context,life,critical=inspect();PREP.mkdir(parents=True);(PREP/'ANTES').mkdir();(PREP/'PROPUESTOS').mkdir()
 mutations=[]
 def add(relative,source):
  target=D/relative;before=sha(target)if target.exists()else None
  if before==sha(source):return
  if target.exists():backup=PREP/'ANTES'/relative;backup.parent.mkdir(parents=True,exist_ok=True);backup.write_bytes(target.read_bytes())
  mutations.append({'file':relative,'source':str(source),'before_sha256':before,'after_sha256':sha(source)})
 for name in('pi09_transporte_heredado_R02.py','pi09_dispatcher_R02.py','pi09_consulta_selectiva_R02.py','SELLO_PI09_CONSULTA_R02.json'):
  source=P/'codigo'/name;require(source.is_file(),'Falta fuente R02: '+name);add('sistema/capacidades/'+name,source)
 for name in('mundo_genesis_apd05.py','cola_local.py'):add('sistema/app/'+name,P/'codigo/HOOKS_PI09_R04_PREPARADOS/app'/name)
 scope=read(S/'capacidades/PI09_TRANSPORTE_HEREDADO_R01.json');scope['source_code_revision']='R02_COMPACT_BEFORE_FIRST_QUERY'
 f=PREP/'PROPUESTOS/PI09_TRANSPORTE_HEREDADO_R02.json';write(f,scope);add('sistema/capacidades/'+f.name,f)
 files=['pi09_transporte_heredado_R02.py','pi09_dispatcher_R02.py','pi09_consulta_selectiva_R02.py','pi09_aritmetica_diagnostica_R01.py','PROTOCOLO_PI09_CONSULTA_R01.json','SELLO_PI09_CONSULTA_R02.json']
 registry={'schema':'DEE.PI09.fixed_plugins_source_registry.R01','plugins':['pi09_consulta_selectiva_R02','pi09_aritmetica_diagnostica_R01'],'files_sha256':{n:sha(P/'codigo'/n)for n in files}}
 f=PREP/'PROPUESTOS/PI09_PLUGINS_R02.json';write(f,registry);add('sistema/capacidades/'+f.name,f)
 old_manifest=read(D/'SISTEMA_CODIGO_PI09.json');mapping={r['file']:r for r in old_manifest['files']}
 for r in mutations:
  if r['file'].startswith('sistema/'):mapping[r['file'][8:]]={'file':r['file'][8:],'bytes':Path(r['source']).stat().st_size,'sha256':r['after_sha256']}
 new_manifest={**old_manifest,'files':[mapping[k]for k in sorted(mapping)],'technical_revision':'R02_COMPACT_BEFORE_FIRST_QUERY','prior_manifest_sha256':sha(D/'SISTEMA_CODIGO_PI09.json')}
 f=PREP/'PROPUESTOS/SISTEMA_CODIGO_PI09.json';write(f,new_manifest);add(f.name,f)
 new_context={**context,'source_code_manifest_sha256':sha(f),'source_code_revision':'R02_COMPACT_BEFORE_FIRST_QUERY','prior_context_sha256':sha(D/'CONTEXTO_EJECUCION.json')}
 f=PREP/'PROPUESTOS/CONTEXTO_EJECUCION.json';write(f,new_context);add(f.name,f)
 prepared={**read(D/'PREPARACION_PI09.json'),'context_sha256':sha(f),'source_code_revision':'R02_COMPACT_BEFORE_FIRST_QUERY','prior_preparation_sha256':sha(D/'PREPARACION_PI09.json')}
 f=PREP/'PROPUESTOS/PREPARACION_PI09.json';write(f,prepared);add(f.name,f)
 write(PLAN,{'schema':'DEE.PI09.NATIVE_prequery_code_upgrade.CAS.R02','life_id':life,'Native_executed':False,'applied':False,'critical_before':critical,'mutations':mutations,'scope':'Before first PI09 request; all324beforeimages/pointers preserved, no Native state or scientific old C/B edit.'})
 print(json.dumps({'plan':str(PLAN),'sha256':sha(PLAN),'mutations':len(mutations),'Native_executed':False}))
def apply():
 plan=read(PLAN);_,_,critical=inspect();require(critical==plan['critical_before'],'Cambió el futuro antes de aplicar')
 require(not PROOF.exists(),'Ya existe comprobante')
 for r in plan['mutations']:
  target=D/r['file'];require((sha(target)if target.exists()else None)==r['before_sha256']and sha(Path(r['source']))==r['after_sha256'],'CAS no coincide: '+r['file'])
 for r in plan['mutations']:
  target=D/r['file'];target.parent.mkdir(parents=True,exist_ok=True);tmp=target.with_name(target.name+'.PI09_R02.pending')
  with tmp.open('xb')as f:f.write(Path(r['source']).read_bytes())
  os.replace(tmp,target)
 require(inspect()[2]==critical,'Cambió estado Native/SQLite/A durante actualización')
 write(PROOF,{**plan,'applied':True,'recorded_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'plan_sha256':sha(PLAN),'critical_after':critical,'Native_inputs_added':0})
 print(json.dumps({'applied':True,'proof':str(PROOF),'sha256':sha(PROOF),'Native_executed':False}))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--aplicar',action='store_true');a=p.parse_args();apply()if a.aplicar else prepare()
