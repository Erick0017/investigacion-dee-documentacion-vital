"""Add exact prerequisites missed by generic suffix routing; read-only originals."""
from pathlib import Path
import base64,gzip,hashlib,json,zipfile
RUN=Path(__file__).resolve().parents[1];CORE=RUN/'core/DEE_COGNITIVE_CORE';CASES=RUN.parents[3]
def sha(b):return hashlib.sha256(b).hexdigest()
index_path=CORE/'documentacion/INDICE_MIEMBROS.json';idx=json.loads(index_path.read_text(encoding='utf8'));store=CORE/'mecanismos/RECUPERACION_POR_HASH.jsonl.gz'
known={r['sha256']for r in idx['paths'].values()};new=[]
with gzip.open(store,'ab',compresslevel=9)as f:
 def add(name,b,origin):
  h=sha(b)
  if name in idx['paths']:
   assert idx['paths'][name]['sha256']==h;return
  if h not in known:
   known.add(h);f.write(json.dumps({'sha256':h,'bytes':len(b),'base64':base64.b64encode(b).decode('ascii')},separators=(',',':')).encode('ascii')+b'\n')
  idx['paths'][name]={'sha256':h,'bytes':len(b),'origin':origin};new.append(name)
 archive=CASES/'CPC3_ENTE_COGNITIVO_CAUSAL_DEE_3_5_0_RESULTADOS.zip'
 with zipfile.ZipFile(archive)as z:
  for i in z.infolist():
   if i.is_dir():continue
   n=i.filename
   selected=(n.startswith('CPC3/genealogia/CP01_C08/casos/')and n.endswith(('/RESULTADOS.json','/CONFIG.json','/EXPERIMENT_CONFIG.json')))or n in('CPC3/genealogia/CP01_C08/casos/EXPERIMENT_CONFIG.json','CPC3/genealogia/CP02_B/EXPERIMENT_CONFIG.json','CPC3/genealogia/CP02_B/resultados/CONFIRMED.json')
   if selected:add('historico/'+n,z.read(i),{'archive':archive.name,'archive_sha256':'1c10b8501ff0bb9756d6b1ebe5876a63ae7300ec4722d651e94dfe9e8f45a0f6','member':n})
 old=CASES/'trabajo_codex/CPC8/runs/RECONSTRUCCION_20261019_002104'
 for p in(old/'base_validada/product45/fixtures/whl_v27').glob('*'):
  if p.is_file():add('cpc8/'+p.relative_to(old).as_posix(),p.read_bytes(),{'directory_cut':'CPC8_RECONSTRUCCION_20261019_002104','relative':p.relative_to(old).as_posix()})
 for p in(old/'base_validada/product45/fixtures/mbp4').rglob('*.deetsnap'):
  add('cpc8/'+p.relative_to(old).as_posix(),p.read_bytes(),{'directory_cut':'CPC8_RECONSTRUCCION_20261019_002104','relative':p.relative_to(old).as_posix(),'reason':'Requiredexacthistoricalseed/checkpointforMBP4regression;notregenerablewithouttheexcludedhistoricalhistory'})
 for group in('fuentes','corpus_seleccionado','antecedentes'):
  for p in(old/'genealogia'/group).rglob('*'):
   if p.is_file()and'__pycache__'not in p.parts:add('cpc8/'+p.relative_to(old).as_posix(),p.read_bytes(),{'directory_cut':'CPC8_RECONSTRUCCION_20261019_002104','relative':p.relative_to(old).as_posix()})
 archive=CASES/'CPC6_MENTE_DEE_INTEGRADA_APRENDIZAJE_Y_COMUNICACION_RESULTADOS.zip'
 with zipfile.ZipFile(archive)as z:
  for i in z.infolist():
   if i.filename.startswith('CPC6/resultados/R03_WORD_BUS_V2/')and i.filename.endswith('/MEASUREMENTS.json'):
    add('historico/'+i.filename,z.read(i),{'archive':archive.name,'archive_sha256':'9d8c72a2536a7d8a782e0f3885d6d9ceba48b5f3d9111f618386def13fff708b','member':i.filename,'reason':'Five originalCPC6 keyprimaries exceedgeneric8MBfilter;explicitlyretained'})
 for archive in sorted(CASES.glob('CPC[34567]_*.zip')):
  if 'REVISION_EXTERNA'in archive.name:continue
  with zipfile.ZipFile(archive)as z:
   for i in z.infolist():
    if i.filename.endswith('.py')and not i.is_dir():add('historico/'+i.filename,z.read(i),{'archive':archive.name,'member':i.filename,'reason':'Unique executed/corrected historical code variants retained inertly, never auto-run as cleanup or benchmark'})
 for p in(old/'resultados').rglob('*.py'):
  if '__pycache__'not in p.parts:add('cpc8/'+p.relative_to(old).as_posix(),p.read_bytes(),{'directory_cut':'CPC8_RECONSTRUCCION_20261019_002104','relative':p.relative_to(old).as_posix(),'reason':'Unique executed source revisions required by terminal-primary hashes'})
idx['content_store_sha256']=sha(store.read_bytes());index_path.write_text(json.dumps(idx,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
(RUN/'notes/core_audit/EXTENSION_PRERREQUISITOS.json').write_text(json.dumps({'added':new,'added_count':len(new),'store_sha256':idx['content_store_sha256']},ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'added':len(new),'store_bytes':store.stat().st_size}))
