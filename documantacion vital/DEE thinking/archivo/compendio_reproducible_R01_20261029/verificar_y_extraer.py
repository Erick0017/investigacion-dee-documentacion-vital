from pathlib import Path
import argparse,hashlib,json,zipfile,datetime
B=Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument('name');p.add_argument('--folder',required=True);a=p.parse_args()
source=B/(a.name+'.zip');out=B/a.folder
if out.exists():raise SystemExit('Se conserva extracción previa; use otra carpeta')
with zipfile.ZipFile(source)as z:
 assert len(z.namelist())==len(set(z.namelist()))
 for name in z.namelist():
  parts=Path(name).parts
  assert '..'not in parts and not Path(name).is_absolute() and ':'not in name
 assert z.testzip()is None
 z.extractall(out)
root=out/'DEE_COMPENDIO_REPRODUCIBLE';cat=json.loads((root/'CATALOGO.json').read_bytes());stage_errors=[]
for row in cat['files']:
 rel=row['path'];current=None
 if rel.startswith('codigo_comun/')or rel.startswith('motor/'):current=B/'package'/rel
 elif rel.startswith('sectores/'):
  _,sector,*suffix=rel.split('/');current=B/('sector_'+sector)/'stage'/Path(*suffix)
  if not current.exists()and suffix==['seleccion.json']:current=B/('sector_'+sector)/'seleccion.json'
 if current is not None and current.exists():
  if hashlib.sha256(current.read_bytes()).hexdigest()!=row['sha256']:stage_errors.append(rel)
for row in cat['entrypoints']:
 if hashlib.sha256((B/'package'/row['path']).read_bytes()).hexdigest()!=row['sha256']:stage_errors.append(row['path'])
result=dict(zip_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),zip_bytes=source.stat().st_size,crc_all_members=True,extracted_root=str(root),source_stage_changes_after_seal=stage_errors,mechanisms=len(cat['mechanisms']),variants=sum(len(m.get('variants',[]))for m in cat['mechanisms']),utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
(B/(a.name+'_EXTRACCION.json')).write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps(result,ensure_ascii=False))
raise SystemExit(bool(stage_errors))
