"""Manifest-declared empty directories in the fresh full-pair import only.

Called inside the existing import transaction after every file was copied,
before its initial Owner. No Native imports, content recreation or repairs.
The full immutable source manifest remains the directory authority.
"""
from pathlib import Path,PurePosixPath
import hashlib

def require(ok,text):
 if not ok:raise ValueError(text)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def regular(p):
 for node in(p,*p.parents):
  require(not node.exists()or not(node.is_symlink()or getattr(node.lstat(),'st_file_attributes',0)&1024),'No se permiten enlaces en el transporte emparejado')
 return p
def relative(value):
 require(isinstance(value,str)and value and '\\'not in value and ':'not in value,'Directorio de manifiesto no válido')
 p=PurePosixPath(value);require(not p.is_absolute()and all(x not in('.','..')for x in p.parts),'Directorio fuera del manifiesto')
 return p

def restore_declared(store,source,manifest,life):
 source=regular(Path(source).resolve(strict=True));state=regular(Path(store.state).resolve(strict=True))
 require(life=='ECI02_PI03_REPRO_PI04_PI05_PI07_PI09_REPRO_01','Este suplemento RP sólo admite la identidad REPRO PI09 predeclarada')
 require(not(state/'ACTIVO.json').exists(),'No se materializan directorios en un principal seleccionado')
 require(manifest.get('schema')=='DEE.persistent_service.paired_export.v1'and manifest.get('life_id')=='ECI02_PI03_REPRO_PI04_PI05_PI07_PI08_C_01'and manifest.get('physical',{}).get('tick')==884835,'Sólo el prefijo C completo fijado para esta receta')
 declared=manifest.get('empty_directories_preserved');require(isinstance(declared,list)and len(declared)==len(set(declared)),'Falta la lista exacta de directorios conservados')
 worker=state/'servicios_locales'/life;service=state/'servicios_persistentes'/life
 require(worker.is_dir()and service.is_dir(),'El importador completo debe haber creado los dos transportes')
 created=[];targets=[]
 for name in declared:
  rel=relative(name)
  if rel.parts[0]=='artefactos_trabajador':target=worker.joinpath(*rel.parts[1:])
  elif rel.parts[0]=='resultados':target=service.joinpath(*rel.parts)
  else:raise ValueError('Sólo se admiten artefactos_trabajador y resultados')
  original=regular(source.joinpath(*rel.parts));regular(target)
  require(original.is_dir(),'El directorio declarado no existe en el prefijo estable')
  if target.exists():require(target.is_dir(),'Una ruta de directorio está ocupada por un archivo')
  else:
   require(not any(p.is_file()for p in original.rglob('*')),'Falta contenido de un directorio; no puede reconstruirse como vacío')
   created.append((name,target))
  targets.append(target)
 critical=[p for p in(state/'servicios_persistentes'/life/'cola.sqlite3',state/'vidas'/life/'VIDA.json')if p.is_file()]
 # All existing content, including SQLite, must stay literal. This is small
 # only for paths being created: no parent or Native content is regenerated.
 before={str(p):sha(p)for p in critical}
 for name,target in sorted(created,key=lambda row:(len(row[1].parts),str(row[1]))):
  require(target.parent.is_dir(),'Un ancestro faltante no figura en la lista declarada')
  target.mkdir(exist_ok=False)
 require(all(p.is_dir()for p in targets),'No se conservaron todos los directorios declarados')
 require(before=={str(p):sha(p)for p in critical},'Cambió contenido existente durante la preservación de directorios')
 return {'schema':'DEE.PI09.RP.manifest_empty_directories.v1','declared':len(declared),'created':[name for name,_ in created],'existing_files_unchanged':True,'new_native_ticks':0,'not_a_scientific_repair':True}
