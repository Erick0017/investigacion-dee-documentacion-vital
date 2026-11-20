"""Copy/hash the closed actual A control only, P8 files; no Native or RP writes."""
from pathlib import Path
import hashlib,json,shutil
P=Path(__file__).resolve().parents[1];H=P/'codigo';C=P.parents[2]/'DEE Cognitive 2.0';RP=C/'reproducibilidad';D=P/'estados/RP_A_PANEL12_R01'
DEST=P/'control/A_PANEL12_PORTABLE_R01';RID='pi08_a_panel12_regulado_T861426_R01'
def read(p):return json.loads(p.read_text('utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def require(ok,text):
 if not ok:raise ValueError(text)
def copy(source,target):
 for path in(source,*source.parents):require(not path.is_symlink()and not(getattr(path.lstat(),'st_file_attributes',0)&1024),'No linked source')
 target.parent.mkdir(parents=True,exist_ok=True);before=sha(source)
 with source.open('rb')as src,target.open('xb')as dst:shutil.copyfileobj(src,dst)
 require(before==sha(source)==sha(target),'Copy/hash/source stability failure')
 return{'file':target.relative_to(DEST).as_posix(),'bytes':target.stat().st_size,'sha256':sha(target),'source_reference_for_packager_only':str(source)}
def put(target,value):
 target.parent.mkdir(parents=True,exist_ok=True)
 with target.open('x',encoding='utf8')as f:json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n')
require(not DEST.exists(),'Existing portable bundle preserved')
result=read(D/'RESULTADO_REPRODUCCION.json');supervision=read(P/'control/SUPERVISION_RP_A_PANEL12_PI08_R01.json');ro=read(P/'control/VERIFICACION_RO_A_PANEL12_PI08_R01.json')
require(result['status']=='COMPLETED'and result['owner_closed_coherently']and result['criteria_met']and supervision['closed']and ro['correct']==12,'Actual closed12/12 required')
index={'schema':'DEE.PI08.portable_primary_index.v1','primaries':[],'administrative_primaries':[],'products':[],
 'scope':'Actual A RP diagnostic panel12; raw primaries copied once. Source_reference fields are provenance only and never opened by recálculo.'}
for number,row in enumerate(result['rows']):
 source=(D/row['primary']).resolve(strict=True);require(source.is_relative_to(D.resolve()),'Bounded actual original primary')
 entry=copy(source,DEST/'04_EVIDENCIAS/PRIMARIOS'/('P%02d.json'%number));entry.update(step=row['step'],life_id=result['life'],world_key=result['life'],modality='ACTUAL_RP_A_DIAGNOSTIC_PANEL12')
 if row['decoder_used']:index['primaries'].append(entry)
 else:index['administrative_primaries'].append({**entry,'interpretation':'Actual habitat pause0, hash-preserved administrative primary; not a thirteenth functional witness.'})
require(len(index['primaries'])==12 and len(index['administrative_primaries'])==1,'Twelve Native witnesses plus one0tickadministrative request')
put(DEST/'04_EVIDENCIAS/PRIMARIOS/INDICE_PRIMARIOS_PI08.json',index)
for source,name in[(D/'RESULTADO_REPRODUCCION.json','RESULTADO_RP_ORIGINAL.json'),(D/'CONTEXTO_EJECUCION.json','CONTEXTO_RP_ORIGINAL.json'),
 (D/'IMPORTACION_DIAGNOSTICA.json','IMPORTACION_ORIGINAL.json'),(P/'control/SUPERVISION_RP_A_PANEL12_PI08_R01.json','SUPERVISION_ORIGINAL.json'),
 (P/'control/VERIFICACION_RO_A_PANEL12_PI08_R01.json','VERIFICACION_RO_ORIGINAL.json'),(RP/'recetas'/(RID+'.json'),'RECETA_PUBLICADA_LITERAL.json')]:copy(source,DEST/name)
for name in('RECALCULAR_A_PANEL12_PI08_R01.py','RECALCULAR_PRIMARIOS_PI08.py','auditoria_documental_PI08.py','heredado/RECALCULAR_PRIMARIOS_PI07_LITERAL.py'):copy(H/name,DEST/name)
members=[{'file':f.relative_to(DEST).as_posix(),'bytes':f.stat().st_size,'sha256':sha(f)}for f in sorted(DEST.rglob('*'))if f.is_file()]
put(DEST/'MANIFIESTO_ESTABLE.json',{'schema':'DEE.PI08.A.RP.panel12_portable_files.R01','files':members,'Native_executed_by_exporter':False,'Cognitive_RP_or_source_state_modified':False,'original_Native_execution_completed':True})
print(json.dumps({'bundle':str(DEST),'files':len(members),'bytes':sum(r['bytes']for r in members),'index_sha256':sha(DEST/'04_EVIDENCIAS/PRIMARIOS/INDICE_PRIMARIOS_PI08.json'),'manifest_sha256':sha(DEST/'MANIFIESTO_ESTABLE.json'),'Native_executed':False}))
