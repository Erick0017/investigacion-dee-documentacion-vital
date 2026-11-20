"""Verify CPC8 workspace members against its exact protected ZIP."""
from pathlib import Path
import hashlib,json,zipfile
RUN=Path(__file__).resolve().parents[1];CORE=RUN/'core/DEE_COGNITIVE_CORE';cases=RUN.parents[3]
artifact=cases/'trabajo_codex/CPC8/runs/resultados/CPC8_ORGANIZACION_COGNITIVA_NATIVA_APRENDIZAJE65_RESULTADOS.zip'
def sha(p):
 h=hashlib.sha256()
 with p.open('rb')as f:
  for b in iter(lambda:f.read(1024**2),b''):h.update(b)
 return h.hexdigest()
assert sha(artifact)=='4cf266a0ab968e26986a9935317ba146a8f769fc5717092470c4bead8983b8ed'
idx=json.loads((CORE/'documentacion/INDICE_MIEMBROS.json').read_text(encoding='utf8'))['paths'];matching=[];missing=[];different=[]
with zipfile.ZipFile(artifact)as z:
 names=set(z.namelist())
 for n,row in idx.items():
  if not n.startswith('cpc8/'):continue
  member='CPC8/'+n[len('cpc8/'):]
  if member not in names:missing.append({'path':n,'origin':row['origin']});continue
  h=hashlib.sha256()
  with z.open(member)as f:
   for b in iter(lambda:f.read(1024**2),b''):h.update(b)
  if h.hexdigest()!=row['sha256']:different.append(n)
  else:matching.append(n)
result={'schema':'DEE_CORE.source_archive_parity.v1','artifact_sha256':sha(artifact),'archive_members_matched':len(matching),'not_in_official_cut':missing,'different_hashes':different,'status':'PASS'if not missing and not different else'WORKSPACE_VARIANTS_REQUIRE_EXPLICIT_PROVENANCE','scope':'EverylistedCPC8source/configuration/primarybyteiscomparedagainsttheexactprotected4cf266ZIP,notjustadirectorylabel.'}
dest=CORE/'verificaciones/FUENTES_CPC8_VS_ZIP.json';dest.parent.mkdir(parents=True,exist_ok=True);dest.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps({'status':result['status'],'matching':len(matching),'missing':len(missing),'different':len(different)}))
