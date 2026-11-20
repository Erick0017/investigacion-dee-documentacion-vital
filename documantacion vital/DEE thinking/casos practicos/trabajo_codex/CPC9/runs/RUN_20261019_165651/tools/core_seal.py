"""Seal a separate candidate; never replace official/historical artifacts."""
from pathlib import Path
import argparse,hashlib,json,zipfile
RUN=Path(__file__).resolve().parents[1];CORE=RUN/'core/DEE_COGNITIVE_CORE'
def sha(p):
 h=hashlib.sha256()
 with p.open('rb')as f:
  for b in iter(lambda:f.read(1024**2),b''):h.update(b)
 return h.hexdigest()
p=argparse.ArgumentParser();p.add_argument('--candidate',type=Path,required=True);a=p.parse_args();dest=a.candidate.resolve()
if dest.exists():raise FileExistsError('Protected existing candidate')
rows=[]
for f in sorted(CORE.rglob('*')):
 if f.is_file()and f.name not in('MANIFIESTO.json','HASHES.sha256'):rows.append({'path':f.relative_to(CORE).as_posix(),'bytes':f.stat().st_size,'sha256':sha(f)})
manifest={'schema':'DEE_CORE.manifest.v1','files':rows,'payload_files':len(rows),'expanded_payload_bytes':sum(r['bytes']for r in rows),'scope':'Contentstoreislosslessinertdata; its logicalmembershaveindependenthashesinINDICE_MIEMBROS. No ZIPselfhashinside.'}
(CORE/'MANIFIESTO.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
lines=[r['sha256']+'  '+r['path']for r in rows]+[sha(CORE/'MANIFIESTO.json')+'  MANIFIESTO.json'];(CORE/'HASHES.sha256').write_text('\n'.join(lines)+'\n',encoding='ascii')
dest.parent.mkdir(parents=True,exist_ok=True)
with zipfile.ZipFile(dest,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=9,allowZip64=True)as z:
 for f in sorted(CORE.rglob('*')):
  if f.is_file():z.write(f,'DEE_COGNITIVE_CORE/'+f.relative_to(CORE).as_posix())
with zipfile.ZipFile(dest)as z:
 assert z.testzip()is None;expanded=sum(i.file_size for i in z.infolist());members=len(z.infolist())
result={'schema':'DEE_CORE.sealed.v1','candidate':str(dest),'sha256':sha(dest),'compressed_bytes':dest.stat().st_size,'expanded_bytes':expanded,'members':members,'manifest_sha256':sha(CORE/'MANIFIESTO.json'),'status':'SEALED_NOT_YET_CLEAN_VERIFIED'}
(dest.parent/(dest.stem+'_IDENTIDAD.json')).write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps(result,ensure_ascii=False))
