"""CAS Root-only de una clave administrativa del registro D, cero Native.

No cambia el scope global de NATIVE ni dispatcher/cuerpos/sello. Conserva
PREPARACION y decisión originales; el suplemento registra su vínculo exacto.
"""
from pathlib import Path
from datetime import datetime,timezone
import argparse,copy,hashlib,importlib.util,json,os
H=Path(__file__).resolve().parent;P=H.parent;C=P.parents[2]/'DEE Cognitive 2.0';S=C/'sistema';CAP=S/'capacidades';STAGE=H/'SUPLEMENTO_REGISTRO_D_ALIAS_R01';OUTPUT=P/'control/SUPLEMENTO_REGISTRO_D_ALIAS_APLICADO_PI09_R01.json'
FILE='capacidades/PI09_PLUGINS_D_R02.json';OLD='PI09_TRANSPORTE_HEREDADO_R02.json';NEW='PI09_TRANSPORTE_D_ANCESTRO_R02.json';DIGEST='3504effe949237c74fb805ade9ce15a5749f7ae06ae844d38e795f7b1a95f38d';PREPARED=P/'control/PREPARACION_TRASLADO_D_PRODUCTO_PI09.json'
def need(ok,msg):
 if not ok:raise ValueError(msg)
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ref(p):return {'path':str(Path(p).resolve(strict=True)),'sha256':sha(p)}
def regular(p):
 for q in(Path(p),*Path(p).parents):need(not q.exists()or not(q.is_symlink()or getattr(q.lstat(),'st_file_attributes',0)&1024),'No enlaces ni reparse en suplemento')
def write(p,v):
 p=Path(p);regular(p);p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('x',encoding='utf8')as f:json.dump(v,f,ensure_ascii=False,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
def transformed(value):
 value=copy.deepcopy(value);pins=value['files_sha256'];need(pins.get(OLD)==DIGEST and NEW not in pins,'Registro D original exacto requerido');value['files_sha256']={NEW if k==OLD else k:v for k,v in pins.items()};return value
def prepare():
 file=S/FILE;regular(file);regular(CAP/NEW);before=read(file);after=transformed(before);need(sha(CAP/NEW)==DIGEST,'El alias ancestral separado debe conservar los bytes Discovery exactos')
 prepared=read(PREPARED);need(prepared.get('phase')=='PREPARED_MOVED_NOT_PROMOTED','Sólo la fase D ya trasladada pendiente de promoción');rows=[r for r in prepared['deployed_code']if r['file']==FILE];need(len(rows)==1 and rows[0]['sha256']==sha(file),'La preparación original debe sellar exactamente el registro actual')
 decision=Path(prepared['decision']['path']);need(sha(decision)==prepared['decision']['sha256'],'Decisión original alterada')
 if not STAGE.exists():
  STAGE.mkdir();(STAGE/'ANTES.json').write_bytes(file.read_bytes());write(STAGE/'DESPUES.json',after);write(STAGE/'PLAN.json',{'schema':'DEE.PI09.D.one_registry_alias.CAS_plan.R01','file':FILE,'before':ref(STAGE/'ANTES.json'),'after':ref(STAGE/'DESPUES.json'),'prepared':ref(PREPARED),'decision':ref(decision),'old_name':OLD,'new_name':NEW,'same_digest':DIGEST,'global_Native_scope':ref(CAP/OLD),'ancestral_D_scope':ref(CAP/NEW),'semantic_changed_paths':['/files_sha256/'+OLD,'/files_sha256/'+NEW],'Native_inputs':0,'Native_ticks':0})
 plan=read(STAGE/'PLAN.json');need(sha(file)==plan['before']['sha256']and read(STAGE/'DESPUES.json')==after and sha(STAGE/'DESPUES.json')==plan['after']['sha256'],'Propuesta previa conservada y CAS actual coincidentes')
 # Ejecuta el verificador REAL del dispatcher literal con el JSON propuesto.
 sp=importlib.util.spec_from_file_location('D_registry_actual_code_no_Native',CAP/'pi09_dispatcher_D_R02.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);m.REGISTRY=STAGE/'DESPUES.json';verified=m.registry();need(verified==after,'Registro real no verifica todos los pines')
 return plan
def apply(plan,proofpath):
 need(not OUTPUT.exists()and not(P/'PI09_ROOT_NATIVE_WRITER.lock').exists()and not(C/'reproducibilidad/EJECUCION_MATERIAL.lock').exists(),'Ventana cerrada y comprobante suplementario nuevo requeridos');proof=read(proofpath);age=(datetime.now(timezone.utc)-datetime.fromisoformat(proof['recorded_utc'])).total_seconds();need(0<=age<=600 and proof.get('no_live_affected_writers')is True,'Root debe comprobar PID/colas/locks actuales antes del CAS')
 need({'ECI02_PI03_REPRO_PI04_PI05_PI07_PI09_NATIVE_01','ECI02_PI03_REPRO_PI04_PI05_PI07_PI09_DISCOVERY_01'}<=set(proof['affected_life_ids']),'Ámbito Native/Discovery requerido')
 protected={str(S/'estado/ACTIVO.json'):sha(S/'estado/ACTIVO.json')}
 for row in proof['evidence']:
  if not row.get('present'):continue
  need(row.get('no_live_affected_writer')is True,'Writer no cerrado')
  for key in('card','snapshot'):
   item=row[key];need(sha(Path(item['path']))==item['sha256'],'Estado cambió tras el proof de Root');protected[item['path']]=item['sha256']
  db=Path(row['SQLite']['path']);protected[str(db)]=sha(db)
 for item in(plan['prepared'],plan['decision'],plan['global_Native_scope'],plan['ancestral_D_scope'],plan['before'],plan['after']):need(sha(Path(item['path']))==item['sha256'],'Referencia suplementaria alterada')
 file=S/FILE;need(sha(file)==plan['before']['sha256'],'Registro concurrente distinto');temp=file.with_name(file.name+'.D_ALIAS_SUPPLEMENT_WRITING');need(not temp.exists(),'Escritura parcial conservada')
 with temp.open('xb')as f:f.write(Path(plan['after']['path']).read_bytes());f.flush();os.fsync(f.fileno())
 os.replace(temp,file);need(sha(file)==plan['after']['sha256']and all(sha(Path(p))==v for p,v in protected.items()),'Estado protegido alterado durante CAS')
 result={**plan,'schema':'DEE.PI09.D.one_registry_alias.applied.R01','applied':True,'recorded_utc':datetime.now(timezone.utc).isoformat(),'writer_proof':ref(proofpath),'target':ref(file),'protected_unchanged':protected,'original_decision_and_preparation_literal_unchanged':True,'only_one_of_24_deployed_rows_changed':True,'scientific_sources_and_all_other_registry_pins_unchanged':True,'original_failed_load_preserved':True};write(OUTPUT,result);print(json.dumps({'proof':str(OUTPUT),'sha256':sha(OUTPUT),'applied':True,'Native_ticks':0}))
def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--aplicar',action='store_true');ap.add_argument('--process-proof',type=Path);a=ap.parse_args();plan=prepare()
 if a.aplicar:need(a.process_proof is not None,'Proof fresco explícito requerido');apply(plan,a.process_proof.resolve(strict=True))
 else:print(json.dumps({'mode':'PREPARED_ONLY_CODE_AND_CLOSED_EVIDENCE','plan':ref(STAGE/'PLAN.json'),'actual_dispatcher_registry_check':True,'product_writes':False,'Native_executed':False}))
if __name__=='__main__':main()
