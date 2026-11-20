"""Fresh reconstruction workspace; selected immutable antecedents, no benchmarks."""
import ctypes,hashlib,json,shutil,sys
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OLD=ROOT.parent/'RUN_20261018_204718'
WHL='dee_thinking-4.5.0-cp313-cp313-win_amd64.whl'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def copy(src,dst):
 dst.parent.mkdir(parents=True,exist_ok=True)
 if dst.exists():raise FileExistsError(dst)
 shutil.copyfile(src,dst)
 return {'source':str(src),'path':dst.relative_to(ROOT).as_posix(),'sha256':sha(dst),'bytes':dst.stat().st_size}
def main():
 for name in ('app','src','configuraciones','resultados','checkpoints','runtime','base_validada','genealogia','revision','reproduccion','tools'):(ROOT/name).mkdir(exist_ok=True)
 rows=[]
 for name in ('supervisor.py','check_instrument.py','regress_base45.py','publicar_cpc8.py','REUNIR_CPC8.py','test_publication_tools.py','control_entrega.py'):
  rows.append(copy(OLD/'tools'/name,ROOT/'tools'/name))
 rows.append(copy(OLD/'runtime'/WHL,ROOT/'runtime'/WHL))
 assert rows[-1]['sha256']=='09e191d259fd15d321ea11b587f8cc02c12c7adfe81b7b96ca2dbebb1fb12d0c'
 rows.append(copy(OLD/'runtime/REFERENCE_IDENTITY.json',ROOT/'runtime/REFERENCE_IDENTITY_HEREDADA.json'))
 for sourcefolder,targetfolder in [('genealogia/product45','genealogia/product45'),('base_validada/product45','base_validada/product45')]:
  for p in sorted((OLD/sourcefolder).rglob('*')):
   if p.is_file()and'__pycache__'not in p.parts:rows.append(copy(p,ROOT/targetfolder/p.relative_to(OLD/sourcefolder)))
 class Memory(ctypes.Structure):
  _fields_=[('dwLength',ctypes.c_ulong),('dwMemoryLoad',ctypes.c_ulong)]+[(n,ctypes.c_ulonglong)for n in('total','available','total_page','available_page','total_virtual','available_virtual','extended')]
 m=Memory();m.dwLength=ctypes.sizeof(m);ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m))
 (ROOT/'revision/RECURSOS_INICIALES.json').write_text(json.dumps({'utc':datetime.now(timezone.utc).isoformat(),'physical_total_bytes':m.total,'physical_available_bytes':m.available,'disk':{str(ROOT.anchor):shutil.disk_usage(ROOT)._asdict()},'budget':'BUDGET.json','max_native_workers':2,'worker_memory_bytes':1073741824},indent=2),encoding='utf-8')
 (ROOT/'genealogia/BOOTSTRAP_SELECCION.json').write_text(json.dumps({'kind':'SELECTED_TECHNICAL_DEPENDENCIES_NOT_NEW_RESULTS','copies':rows,'excluded':['comparadores/B1/B2','old full ZIP','old whole snapshots','old scientific summaries as new findings'],'expected_official_source_sha256':'fbd8190381ed76085f404e6578ff15fe185ab66cd48c67300d2abad61ddc7e31'},ensure_ascii=False,indent=2),encoding='utf-8')
 print(json.dumps({'copied_files':len(rows),'available_RAM':m.available,'root':str(ROOT)}))
if __name__=='__main__':main()
