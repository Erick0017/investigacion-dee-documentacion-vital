"""One exact frozen Cognitive code capsule, one shared official wheel, no DEE imports."""
from pathlib import Path
import ast,datetime,hashlib,json,os,shutil
P=Path(__file__).resolve().parents[1];C=P.parents[2]/'DEE Cognitive 2.0';OLD=P.with_name('PROGRESION_INTEGRADA_04')
SOURCE=C/'reproducibilidad/codigo_preservado/PI04_C2C_FINAL_OP2';DEST=P/'estados/candidato/sistema'
def sha(f):return hashlib.sha256(f.read_bytes()).hexdigest()
def main():
 assert not DEST.exists(),'Never replace an experimental system'
 mf=SOURCE/'SISTEMA_CODIGO.json';assert sha(mf)=='40de79d295b60773cc1ed8c43ea69c82c595a45fd35ad14c90d48f9afa46795b'
 rows=json.loads(mf.read_text(encoding='utf-8-sig'))['files'];assert len(rows)==195
 for row in rows:
  f=SOURCE/row['file'];assert f.resolve().is_relative_to(SOURCE.resolve()) and f.is_file() and not f.is_symlink() and sha(f)==row['sha256']
 DEST.mkdir(parents=True)
 for row in rows:
  f=DEST/row['file'];f.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(SOURCE/row['file'],f)
 (DEST/'runtime').mkdir(exist_ok=True);wheel='dee_thinking-4.5.0-cp313-cp313-win_amd64.whl'
 assert sha(C/'sistema/runtime'/wheel)=='09e191d259fd15d321ea11b587f8cc02c12c7adfe81b7b96ca2dbebb1fb12d0c'
 os.link(C/'sistema/runtime'/wheel,DEST/'runtime'/wheel)
 for rel in ('control','ensayos','fuentes','pares','observacion','codigo/originales_PI04'):(P/rel).mkdir(parents=True,exist_ok=True)
 (DEST/'estado/checkpoints').mkdir(parents=True,exist_ok=True)
 # Preserve the verified OP3 transport fix. It changes argument dispatch only.
 mgr=OLD/'estados/candidato_R02/sistema/gestionar.py';assert sha(mgr)=='2db0e6218899481f0756aca2c463aa2707f79301c93f9002928c0f20b0e25933'
 shutil.copyfile(DEST/'gestionar.py',P/'codigo/originales_PI04/gestionar_OP2.py');shutil.copyfile(mgr,DEST/'gestionar.py')
 adapted=[]
 for name in ('servicio_ensayo_R02.py','clonar_PI04_R02.py'):
  src=OLD/'codigo'/name;shutil.copyfile(src,P/'codigo/originales_PI04'/name)
  text=src.read_text(encoding='utf-8-sig').replace('estados/candidato_R02/sistema','estados/candidato/sistema')
  text=text.replace('supervised for PI04','supervised for PI05').replace('isolated PI04 system','isolated PI05 system').replace('DEE.PI04.full_pair_diagnostic_import.v1','DEE.PI05.full_pair_diagnostic_import.v1')
  if name.startswith('clonar_'):
   text=text.replace("source.is_relative_to(P/'estados')","source.is_relative_to(P/'estados')or source.is_relative_to(P/'pares')")
   text=text.replace("r'ECI02_PI03_[A-Za-z0-9_]{1,48}'","r'ECI02_PI03_REPRO_PI04_PI05_[A-Za-z0-9_]{1,32}'")
  ast.parse(text);target=P/'codigo'/('clonar_PI05.py'if name.startswith('clonar_')else'servicio_ensayo_PI05.py')
  with target.open('x',encoding='utf8')as f:f.write(text)
  adapted.append({'original':str(src),'original_sha256':sha(src),'adaptation':str(target),'adaptation_sha256':sha(target)})
 # Keep the known old-panel recipe here as a fixed directed procedure, not a new platform.
 for name in ('ejecutar_panel_PI04.py','ejecutar_C2C_R01.py'):
  src=OLD/'codigo'/name;shutil.copyfile(src,P/'codigo/originales_PI04'/name)
  text=src.read_text(encoding='utf-8-sig').replace('servicio_ensayo_R02','servicio_ensayo_PI05').replace('estados/candidato_R02/sistema','estados/candidato/sistema')
  text=text.replace("P/'REGISTRO_CAMPANA.json'","P/'REGISTRO_CAMPANA.json'").replace("budget['closure_target_local']","budget['science_cutoff_local']")
  text=text.replace('PI04_', 'PI05_') if False else text
  # Tag namespaces are kept by these historical runners until the targeted PI05 version is reviewed; do not silently alter their scientific literals.
  ast.parse(text);target=P/'codigo'/('PANEL_HISTORICO_BASE.py'if name.startswith('ejecutar_panel')else'C2C_HISTORICO_BASE.py')
  with target.open('x',encoding='utf8')as f:f.write(text)
  adapted.append({'original':str(src),'original_sha256':sha(src),'adaptation':str(target),'adaptation_sha256':sha(target),'status':'BASE_FOR_PI05_ADAPTATION_NOT_EXECUTED'})
 proof={'schema':'DEE.PI05.isolated_code_base.v1','at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'source':str(SOURCE),'capsule_manifest_sha256':sha(mf),'copied_code_files':len(rows),'system':str(DEST),'shared_wheel_hardlink':str(DEST/'runtime'/wheel),'reviewed_transport_override':{'source':str(mgr),'sha256':sha(mgr)},'adaptations':adapted,'Native_ticks':0,'DEE_imports':0,'original_code_or_states_modified':False,'primary_selected':False}
 out=P/'control/SISTEMA_BASE_PI05.json'
 with out.open('x',encoding='utf8')as f:json.dump(proof,f,ensure_ascii=False,indent=2)
 print(json.dumps({'system':str(DEST),'copied_files':len(rows),'proof':str(out),'Native_ticks':0}))
if __name__=='__main__':main()
