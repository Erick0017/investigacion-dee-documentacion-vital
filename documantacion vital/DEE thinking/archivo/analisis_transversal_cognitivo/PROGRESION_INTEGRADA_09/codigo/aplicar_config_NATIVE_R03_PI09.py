"""Root-only CAS of normalized seal/config after a preserved0Native rejection.

No actor/scientific body or Native/SQLite state is written. Default plan;
--aplicar uses exact beforeimages and retains the rejected request forever.
"""
from pathlib import Path
import argparse,datetime,hashlib,importlib.util,json,os,sqlite3
P=Path(__file__).resolve().parents[1];D=P/'estados/NATIVE';S=D/'sistema';C=P.parents[2]/'DEE Cognitive 2.0';RP=C/'reproducibilidad'
PREP=P/'codigo/CONFIG_NATIVE_R03_PREPARADA';PLAN=PREP/'PLAN.json';PROOF=PREP/'APLICACION.json'
OLD='505a403f9d42d4c231f536740d16306ead8d4363731b42ab89ca55afe45f0118'
NEW='30e0160fa4bdb05dd258295611a68416ddab7858fc06d1f9cea7e9b67df931d8'
BODY='3b81573f4dc0d9401db2210f3b23694e1f1f4a4d820d7654bcbd1e1b42b2dfbf'
NAME='SELLO_PI09_CONSULTA_R02.json';LIFE='ECI02_PI03_REPRO_PI04_PI05_PI07_PI09_NATIVE_01'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def require(ok,msg):
 if not ok:raise ValueError(msg)
def write(p,v):
 p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('x',encoding='utf8')as f:json.dump(v,f,ensure_ascii=False,indent=2);f.write('\n')
def inspect():
 require(not(P/'PI09_ROOT_NATIVE_WRITER.lock').exists(),'Persiste un escritor/importador')
 proof=read(P/'control/PI09_NATIVE_R02.json');require(proof['closed']is True and proof['initial_tick']==proof['final_tick']==884835 and proof['new_Native_ticks']==0,'Cierre real0Native requerido')
 life=S/'estado/vidas'/LIFE;card=read(life/'VIDA.json');snapshot=S/card['snapshot'];db=S/'estado/servicios_persistentes'/LIFE/'cola.sqlite3'
 require(not(S/'estado/ACTIVO.json').exists()and not(life/'FUTURO_INTERRUMPIDO.json').exists()and not(S/'estado/locks'/(card['world_id']+'.lock')).exists(),'Vida abierta/seleccionada/interrumpida')
 require(card['physical']['tick']==884835 and sha(S/'capacidades/pi09_consulta_selectiva_R02.py')==BODY,'Cambió física o cuerpo científico')
 require(not any(Path(str(db)+x).exists()and Path(str(db)+x).stat().st_size for x in('-wal','-journal')),'SQLite con WAL/journal no vacío')
 con=sqlite3.connect(db.as_uri()+'?mode=ro&immutable=1',uri=True)
 try:
  require(con.execute('PRAGMA integrity_check').fetchone()[0]=='ok','SQLite no íntegra')
  owner=json.loads(con.execute("SELECT value FROM meta WHERE key='owner'").fetchone()[0]);require(owner.get('running')is False and owner['tick']==884835 and not owner.get('uncertain_external_result'),'Owner no cerrado/coherente')
  require(con.execute("SELECT COUNT(*) FROM requests WHERE status IN('queued','processing','uncertain')").fetchone()[0]==0,'Transporte pendiente')
  row=con.execute("SELECT status,error FROM requests WHERE id='PI09_NATIVE_R02_001'").fetchone();require(row and row[0]=='rejected_invalid','Debe conservarse el rechazo exactoR02_001')
  error=json.loads(row[1]);require(error.get('no_material_input_submitted')is True and error.get('native_tick_unchanged')is True,'El rechazo no acredita0entrada material')
 finally:con.close()
 sp=importlib.util.spec_from_file_location('PI09_configRO',RP/'observador_pasivo.py');obs=importlib.util.module_from_spec(sp);sp.loader.exec_module(obs)
 view=obs.snapshot_view(snapshot);require(not any(k.startswith('DEE.Cognitive.PI09.')for k in view['metadata']),'Ya hay historia de consultaPI09: no se modifica este sello con esta herramienta')
 old=obs.snapshot_view(P/'pares/C_HEREDADA_T884835/VIDA.deetsnap.gz');comparison=obs.compare_native(old,view,allow_service=True)
 active=C/'sistema/estado/ACTIVO.json';acard=C/'sistema/estado/vidas'/read(active)['life_id']/'VIDA.json'
 critical=[life/'VIDA.json',life/'HISTORIA.jsonl',snapshot,db,active,acard,C/'sistema'/read(acard)['snapshot']]
 return {str(p):sha(p)for p in critical},comparison
def prepare():
 require(not PREP.exists(),'Plan ya existente')
 source=P/'codigo'/NAME;require(sha(source)==NEW and sha(S/'capacidades'/NAME)==OLD,'Sellos before/after no coinciden')
 fresh=read(source);require(set(fresh['source_prefix']['physical'])=={'N','tick','RAW_sha256','clocks_sha256'}and len(fresh['source_prefix']['manifest_physical_complete'])==8,'Normalización4+8exacta requerida')
 critical,comparison=inspect();PREP.mkdir(parents=True);mutations=[]
 def add(rel,src):
  target=D/rel;backup=PREP/'ANTES'/rel;backup.parent.mkdir(parents=True,exist_ok=True);backup.write_bytes(target.read_bytes())
  mutations.append({'file':rel,'source':str(src),'before_sha256':sha(target),'after_sha256':sha(src)})
 add('sistema/capacidades/'+NAME,source)
 registry=read(S/'capacidades/PI09_PLUGINS_R02.json');require(registry['files_sha256'][NAME]==OLD,'Registro no corresponde aR02original');registry['files_sha256'][NAME]=NEW
 f=PREP/'PROPUESTOS/PI09_PLUGINS_R02.json';write(f,registry);add('sistema/capacidades/'+f.name,f)
 manifest=read(D/'SISTEMA_CODIGO_PI09.json')
 for row in manifest['files']:
  for change in mutations:
   if row['file']==change['file'][8:]:row.update(bytes=Path(change['source']).stat().st_size,sha256=change['after_sha256'])
 manifest['configuration_normalization_R03']={'prior_manifest_sha256':sha(D/'SISTEMA_CODIGO_PI09.json'),'old_seal_sha256':OLD,'new_seal_sha256':NEW,'scientific_body_unchanged':BODY}
 f=PREP/'PROPUESTOS/SISTEMA_CODIGO_PI09.json';write(f,manifest);add(f.name,f)
 context=read(D/'CONTEXTO_EJECUCION.json');context['source_code_manifest_sha256']=sha(f);context['configuration_normalization_R03']=True
 f=PREP/'PROPUESTOS/CONTEXTO_EJECUCION.json';write(f,context);add(f.name,f)
 prepared=read(D/'PREPARACION_PI09.json');prepared['context_sha256']=sha(f);prepared['configuration_normalization_R03']=True
 f=PREP/'PROPUESTOS/PREPARACION_PI09.json';write(f,prepared);add(f.name,f)
 write(PLAN,{'schema':'DEE.PI09.zero_input_config_normalization.CAS.R03','Native_executed':False,'applied':False,'critical_before':critical,'actual_comparison':comparison,'rejected_id_preserved':'PI09_NATIVE_R02_001','mutations':mutations})
 print(json.dumps({'plan':str(PLAN),'sha256':sha(PLAN),'mutations':len(mutations),'Native_executed':False}))
def apply():
 plan=read(PLAN);require(not PROOF.exists(),'Comprobante ya existente');require(inspect()[0]==plan['critical_before'],'Cambió un estado protegido')
 for r in plan['mutations']:require(sha(D/r['file'])==r['before_sha256']and sha(Path(r['source']))==r['after_sha256'],'CAS no coincide: '+r['file'])
 for r in plan['mutations']:
  target=D/r['file'];tmp=target.with_name(target.name+'.CONFIG_R03.pending')
  with tmp.open('xb')as f:f.write(Path(r['source']).read_bytes())
  os.replace(tmp,target)
 critical,comparison=inspect();require(critical==plan['critical_before'],'Cambió física/SQLite/A')
 write(PROOF,{**plan,'applied':True,'recorded_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'plan_sha256':sha(PLAN),'critical_after':critical,'actual_comparison_after':comparison,'body_sha256_unchanged':BODY})
 print(json.dumps({'applied':True,'proof':str(PROOF),'sha256':sha(PROOF),'Native_executed':False}))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--aplicar',action='store_true');a=p.parse_args();apply()if a.aplicar else prepare()
