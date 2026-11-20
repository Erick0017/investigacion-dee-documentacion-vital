"""Refresh the declared RP frontdoor hash in never-imported control contexts.

No world/SQLite/source code change. The frontdoor gained a PI11 recipe after
these empty diagnostic preparations; the importer correctly pins its tools.
Only that expected tool delta is accepted, with literal backups before writes.
"""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,shutil
P=Path(__file__).resolve().parents[1];C=P.parents[2]/'DEE Cognitive 2.0';RP=C/'reproducibilidad'
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,v):
 with p.open('x',encoding='utf8')as f:json.dump(v,f,ensure_ascii=False,indent=2);f.write('\n')
def main():
 registration=P/'control/INSTALACION_REPRODUCCION_PI11_R01/REGISTRO_COMPLETADO.json';r=read(registration)
 assert sha(RP/'reproducir.py')==r['files_after']['frontdoor']
 records=[]
 for slug in('HEREDADO01','NONE01','YOKE01'):
  dest=P/'estados'/slug;ctxfile=dest/'CONTEXTO_EJECUCION.json';prepfile=dest/'PREPARACION_PI11.json';ctx=read(ctxfile);prep=read(prepfile)
  assert not(dest/'IMPORTACION_PI11.json').exists()and not(dest/'sistema/estado/vidas'/ctx['life']).exists()
  assert sha(ctxfile)==prep['context_sha256']
  before=sha(ctxfile);changes=[]
  for item in ctx['tool_sources']:
   actual=sha(RP/item['file'])
   if actual!=item['sha256']:
    assert item['file']=='reproducir.py'and item['sha256']==r['original_hashes']['frontdoor']
    changes.append({'file':item['file'],'before':item['sha256'],'after':actual});item['sha256']=actual
  assert len(changes)==1
  backup=dest/'CONTEXTO_PRE_RP_PI11_R01';backup.mkdir()
  shutil.copyfile(ctxfile,backup/ctxfile.name);shutil.copyfile(prepfile,backup/prepfile.name)
  temporary=ctxfile.with_suffix('.NEW.json');write(temporary,ctx);temporary.replace(ctxfile)
  prep['context_sha256']=sha(ctxfile);temporary=prepfile.with_suffix('.NEW.json');write(temporary,prep);temporary.replace(prepfile)
  records.append({'slug':slug,'before_context_sha256':before,'after_context_sha256':sha(ctxfile),'changes':changes,'Native':0,'world_not_imported':True})
 write(P/'control/ACTUALIZACION_CONTEXTOS_PREIMPORT_PI11_R01.json',{'schema':'DEE.PI11.prospective_unimported_tool_binding_update.R01','at_utc':datetime.now(timezone.utc).isoformat(),'registration_sha256':sha(registration),'records':records,'Native_ticks':0,'not_a_scientific_protocol_or_state_change':True})
 print(json.dumps({'contexts':len(records),'Native':0}))
if __name__=='__main__':main()
