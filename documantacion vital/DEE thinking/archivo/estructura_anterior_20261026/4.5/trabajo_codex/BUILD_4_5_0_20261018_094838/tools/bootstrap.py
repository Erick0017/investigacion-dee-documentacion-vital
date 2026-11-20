"""Read-only reference inventory and exact private source copy; no old runners."""
import hashlib,json,shutil,sys,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT.parents[2]
CASES=BASE/'casos practicos'
def sha(path):
 h=hashlib.sha256()
 with Path(path).open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
def put(path,value):
 path=Path(path);path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(value,ensure_ascii=False,indent=2),encoding='utf-8')
refs={
 'PRODUCT40':(BASE/'4.0/DEE_thinking_4_0_0_ENTREGA_FINAL_RESULTADOS.zip','c78609a7d0d501324324408ed955f60f127965c77efbcbe3b3d04fc14dbb16cf'),
 'WHEEL40':(BASE/'4.0/dee_thinking-4.0.0-cp313-cp313-win_amd64.whl','17c07745b9687d8686d132f055c39c149da1dde807e7246a67d457fe69df5623'),
 'CPC7':(CASES/'CPC7_MENTE_DEE_ACCESO_SELECTIVO_Y_APRENDIZAJE_CONTINUO_RESULTADOS.zip','64a9ca648d10bb8bc42c02e218091b4e7c5599a55301c65d67c7f6f8ac83a128'),
 'CPC6':(CASES/'CPC6_MENTE_DEE_INTEGRADA_APRENDIZAJE_Y_COMUNICACION_RESULTADOS.zip','9d8c72a2536a7d8a782e0f3885d6d9ceba48b5f3d9111f618386def13fff708b'),
 'CPC5':(CASES/'CPC5_ARQUITECTURAS_COMPUESTAS_Y_APRENDIZAJE_ACUMULATIVO_RESULTADOS.zip','d31972a47f12bb574a71a14d7ddca3b7a011f320eaba37dcb2ac97abe1f4ce05'),
 'CPC4':(CASES/'CPC4_COMUNICACION_NATIVA_Y_META_ROSETTA_RESULTADOS.zip','4a14a81f913a434a8e54e47c0c700d7ee54418bb16913aedded8bf49a3294723'),
 'CPC3':(CASES/'CPC3_ENTE_COGNITIVO_CAUSAL_DEE_3_5_0_RESULTADOS.zip','1c10b8501ff0bb9756d6b1ebe5876a63ae7300ec4722d651e94dfe9e8f45a0f6')}
records=[]
for key,(path,expected) in refs.items():
 actual=sha(path);assert actual==expected,(key,actual);records.append({'id':key,'name':path.name,'bytes':path.stat().st_size,'sha256':actual,'original_read_only':True})
put(ROOT/'evidence/REFERENCES.json',records)
with zipfile.ZipFile(refs['PRODUCT40'][0]) as z:
 prefix='DEE_thinking_4_0_0/source/'
 files=[]
 for info in z.infolist():
  if info.is_dir() or not info.filename.startswith(prefix):continue
  rel=Path(info.filename[len(prefix):]);assert not rel.is_absolute() and '..' not in rel.parts
  target=ROOT/'source'/rel;target.parent.mkdir(parents=True,exist_ok=True)
  if target.exists():raise FileExistsError(target)
  data=z.read(info);target.write_bytes(data);files.append({'path':rel.as_posix(),'sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data)})
 for member in ('PRODUCT_CONTRACT.json','BUILD_PROVENANCE.json','tools/build40.ps1'):
  target=ROOT/'evidence/product40'/member;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(z.read('DEE_thinking_4_0_0/'+member))
put(ROOT/'evidence/SOURCE40_MANIFEST.json',files)
assert sha(ROOT/'source/src/kernel_v27.cpp')=='fbd8190381ed76085f404e6578ff15fe185ab66cd48c67300d2abad61ddc7e31'
(ROOT/'reference/wheel').mkdir(parents=True,exist_ok=True)
shutil.copyfile(refs['WHEEL40'][0],ROOT/'reference/wheel'/refs['WHEEL40'][0].name)
with zipfile.ZipFile(refs['CPC7'][0]) as z:
 selected=[]
 for info in z.infolist():
  rel=info.filename.removeprefix('CPC7/')
  if info.is_dir() or rel==info.filename:continue
  if (rel.startswith(('src/','app/','configuraciones/','revision/','base_validada/','genealogia/')) and not rel.endswith(('.deetsnap','.gz','.whl','.npz'))):
   target=ROOT/'evidence/CPC7'/rel;target.parent.mkdir(parents=True,exist_ok=True);data=z.read(info);target.write_bytes(data)
   selected.append({'member':info.filename,'sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data)})
put(ROOT/'evidence/CPC7_SELECTION.json',selected)
print(json.dumps({'source_files':len(files),'CPC7_members':len(selected),'kernel_unchanged':True,'root':str(ROOT)}))
