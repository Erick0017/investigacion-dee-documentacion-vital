"""Pure stdlib directory import checks; no DEE, Owner, SQLite mutation or Native."""
from pathlib import Path
from types import SimpleNamespace
import hashlib,importlib.util,json
H=Path(__file__).resolve().parent;OUT=H/'PRUEBA_DIRECTORIOS_RP_PI09_R01'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 if OUT.exists():raise FileExistsError('Se conserva la prueba anterior')
 OUT.mkdir();sp=importlib.util.spec_from_file_location('dirs_pure',H/'directorios_RP_PI09_R01.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);tests=[]
 def check(n,v):
  if v is not True:raise AssertionError(n)
  tests.append({'name':n,'pass':True})
 def rejects(n,fn):
  try:fn()
  except ValueError:check(n,True);return
  raise AssertionError(n)
 life='ECI02_PI03_REPRO_PI04_PI05_PI07_PI09_REPRO_01';source=OUT/'source';state=OUT/'sistema/estado';service=state/'servicios_persistentes'/life;worker=state/'servicios_locales'/life
 for root in(source/'artefactos_trabajador/old30/inflight',source/'artefactos_trabajador/old30/reservoir',source/'resultados/vacios',service/'resultados',worker/'old30'):
  root.mkdir(parents=True,exist_ok=True)
 (source/'artefactos_trabajador/old30/manifest.json').write_bytes(b'{"literal":30}\n');(worker/'old30/manifest.json').write_bytes(b'{"literal":30}\n');(service/'cola.sqlite3').write_bytes(b'FAKE_LITERAL_NOT_SQLITE')
 manifest={'schema':'DEE.persistent_service.paired_export.v1','life_id':'ECI02_PI03_REPRO_PI04_PI05_PI07_PI08_C_01','physical':{'tick':884835},'empty_directories_preserved':['artefactos_trabajador','artefactos_trabajador/old30','artefactos_trabajador/old30/inflight','artefactos_trabajador/old30/reservoir','resultados','resultados/vacios']}
 before={str(p):sha(p)for p in(state.rglob('*'))if p.is_file()};r=m.restore_declared(SimpleNamespace(state=state),source,manifest,life)
 check('all_empty_directories_preserved',r['created']==['resultados/vacios','artefactos_trabajador/old30/inflight','artefactos_trabajador/old30/reservoir'])
 check('existing_content_byte_identical',before=={str(p):sha(p)for p in state.rglob('*')if p.is_file()})
 r2=m.restore_declared(SimpleNamespace(state=state),source,manifest,life);check('directory_recheck_creates_nothing',r2['created']==[])
 rejects('different_life_rejected',lambda:m.restore_declared(SimpleNamespace(state=state),source,manifest,life+'X'))
 for bad in('../outside','artefactos_trabajador/../../outside','C:/bad','artefactos_trabajador\\bad'):
  rejects('unsafe_'+bad,lambda:m.relative(bad))
 actual=json.loads((H.parent/'pares/C_HEREDADA_T884835/EXPORTACION_SERVICIO.json').read_text('utf8'))
 for name in actual['empty_directories_preserved']:
  p=m.relative(name);check('actual_prefix_directory_'+name,(H.parent/'pares/C_HEREDADA_T884835'/name).is_dir()and p.parts[0]in('artefactos_trabajador','resultados'))
 result={'schema':'DEE.PI09.RP.directory_transport.pure_tests.R01','passed':len(tests),'tests':tests,'actual_manifest_sha256':sha(H.parent/'pares/C_HEREDADA_T884835/EXPORTACION_SERVICIO.json'),'Native_executed':False,'DEE_imports':0,'source_state_read':False,'fixture_only_materialization':True}
 file=OUT/'RESULTADO.json';file.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n','utf8');print(json.dumps({'passed':len(tests),'proof':str(file),'sha256':sha(file),'Native_executed':False}))
if __name__=='__main__':main()
