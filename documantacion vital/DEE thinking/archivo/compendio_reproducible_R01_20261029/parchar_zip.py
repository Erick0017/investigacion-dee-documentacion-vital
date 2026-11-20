"""Sella otra revisión desde el ZIP previo y cambios funcionales declarados."""
from pathlib import Path
import gzip,hashlib,json,zipfile,datetime
B=Path(__file__).resolve().parent
def sha(b):return hashlib.sha256(b).hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def main():
 source=B/'CANDIDATO_03.zip';target=B/'CANDIDATO_04.zip'
 if target.exists():raise FileExistsError(target)
 prefix='DEE_COMPENDIO_REPRODUCIBLE/'
 with zipfile.ZipFile(source)as old:
  cat=json.loads(old.read(prefix+'CATALOGO.json'));added={}
  changed={
   'sectores/mente/ejecutar_mente.py':B/'sector_mente/stage/ejecutar_mente.py',
   'sectores/core/configuraciones/RECUPERACION_CONGELADA.json':B/'sector_core/stage/configuraciones/RECUPERACION_CONGELADA.json',
   'sectores/core/sector.json':B/'sector_core/sector.json',
   'sectores/apd/ejecutar.py':B/'sector_apd/stage/ejecutar.py',
   'sectores/apd/native_jobs.json':B/'sector_apd/stage/native_jobs.json',
   'sectores/apd/sector.json':B/'sector_apd/sector.json',
   'codigo_comun/entorno_seguro.py':B/'package/codigo_comun/entorno_seguro.py'}
  for rel,p in changed.items():
   data=p.read_bytes();h=sha(data);z=gzip.compress(data,compresslevel=6,mtime=0);codec='gzip'if len(z)<len(data)else'raw';storage='objetos/'+h[:2]+'/'+h+('.gz'if codec=='gzip'else'')
   added[storage]=z if codec=='gzip'else data
   record=dict(path=rel,sha256=h,bytes=len(data),storage=storage,compression=codec)
   existing=next((i for i,r in enumerate(cat['files'])if r['path']==rel),None)
   if existing is None:cat['files'].append(record)
   else:cat['files'][existing]=record
  cat['files'].sort(key=lambda x:x['path'])
  cat['shared_sources']=read(B/'common_sources.json');cat['documentary_sources']=read(B/'FUENTES_DOCUMENTALES.json')
  for sector in('core','apd'):
   current=read(B/('sector_'+sector)/'sector.json')
   for m in current['mechanisms']:
    oldm=next(x for x in cat['mechanisms']if x['id']==m['id']);oldm.update(m);oldm.update(sector=sector,location='sectores/'+sector)
  cat['revision']=dict(name='R01 candidato04',utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),parent_zip_sha256=sha(source.read_bytes()),changes=list(changed),scope='Correcciones instrumentales de lectura, temporal y límiteCPU; no modificaciones de leyes, entradas físicas, respuestas esperadas ni vidas originales.')
  cat['technical_adaptations']=[dict(mechanism='M304',historical_host_seconds=600,replay_host_seconds=1800),dict(mechanism='M305',historical_host_seconds=240,replay_host_seconds=900)]
  used={r['storage']for r in cat['files']};unique={}
  for r in cat['files']:unique.setdefault(r['storage'],r)
  cat['compression']=dict(logical_files=len(cat['files']),logical_bytes=sum(r['bytes']for r in cat['files']),unique_blobs=len(used),unique_stored_bytes=sum(len(added[s])if s in added else old.getinfo(prefix+s).file_size for s in used),method='Alias porSHA256 de bytes exactos, compresión sin pérdida. No incluye distribucionesZIP históricas.')
  with zipfile.ZipFile(target,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6,allowZip64=True)as z:
   for info in old.infolist():
    rel=info.filename[len(prefix):]
    if rel=='CATALOGO.json'or rel.startswith(('objetos/','motor/'))and(rel not in used or rel in added):continue
    z.writestr(info,old.read(info),compress_type=zipfile.ZIP_DEFLATED,compresslevel=6)
   for rel,data in added.items():z.writestr(prefix+rel,data)
   z.writestr(prefix+'CATALOGO.json',json.dumps(cat,ensure_ascii=False,indent=2)+'\n')
 result=dict(zip=str(target),bytes=target.stat().st_size,sha256=sha(target.read_bytes()),mechanisms=len(cat['mechanisms']),logical_files=len(cat['files']))
 (B/'CANDIDATO_04_SELLO.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps(result,ensure_ascii=False))
if __name__=='__main__':main()
