"""Retain one irreplaceable historical diagnostic parent and its tiny runner."""
from pathlib import Path
import base64,gzip,hashlib,json,zipfile
RUN=Path(__file__).resolve().parents[1];CORE=RUN/'core/DEE_COGNITIVE_CORE';CASES=RUN.parents[3]
archive=CASES/'trabajo_codex/CPC8/runs/resultados/CPC8_ORGANIZACION_COGNITIVA_NATIVA_APRENDIZAJE65_RESULTADOS.zip'
index=CORE/'documentacion/INDICE_MIEMBROS.json';idx=json.loads(index.read_text(encoding='utf8'));store=CORE/'mecanismos/RECUPERACION_POR_HASH.jsonl.gz';known={r['sha256']for r in idx['paths'].values()};rows=[]
with zipfile.ZipFile(archive)as z,gzip.open(store,'ab',compresslevel=9)as f:
 for member in('resultados/diagnostico_L15_r1/passive_original_PRE_JOIN_T78.deetsnap.gz','tools/ejecutar_cantidad_forma_movil.py'):
  names=[n for n in z.namelist()if n.endswith('/'+member)];assert len(names)==1;original=names[0];b=z.read(original);h=hashlib.sha256(b).hexdigest();logical='cpc8/'+member
  if logical in idx['paths']:assert idx['paths'][logical]['sha256']==h;continue
  if h not in known:f.write(json.dumps({'sha256':h,'bytes':len(b),'base64':base64.b64encode(b).decode('ascii')},separators=(',',':')).encode('ascii')+b'\n');known.add(h)
  idx['paths'][logical]={'sha256':h,'bytes':len(b),'origin':{'archive_sha256':'4cf266a0ab968e26986a9935317ba146a8f769fc5717092470c4bead8983b8ed','member':original,'reason':'One indispensable inherited diagnostic parent including exact clocks/pending queue; no new E1 learning claim.'if member.endswith('.gz')else'Exact tiny executed QFM runner needed to reconstruct preserved function.'}};rows.append({'logical':logical,'bytes':len(b),'sha256':h})
idx['content_store_sha256']=hashlib.sha256(store.read_bytes()).hexdigest();index.write_text(json.dumps(idx,ensure_ascii=False,indent=2)+'\n',encoding='utf8');(RUN/'notes/core_audit/CPC8_ESSENTIAL_ADDITIONS.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps(rows))
