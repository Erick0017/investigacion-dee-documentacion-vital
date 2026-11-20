"""Copia entradas ZIP comprimidas exactas y sella sólo los cambios declarados."""
from pathlib import Path
import argparse,copy,gzip,hashlib,json,zipfile,datetime,shutil,io
B=Path(__file__).resolve().parent
def sha(x):return hashlib.sha256(x).hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def main():
 p=argparse.ArgumentParser();p.add_argument('--source',required=True,type=Path);p.add_argument('--target',required=True,type=Path);p.add_argument('--updates',type=Path);p.add_argument('--validation',type=Path);a=p.parse_args()
 if a.target.exists():raise FileExistsError(a.target)
 prefix='DEE_COMPENDIO_REPRODUCIBLE/'
 with zipfile.ZipFile(io.BytesIO(a.source.read_bytes()))as src:
  cat=json.loads(src.read(prefix+'CATALOGO.json'));added={};changes=[];direct={}
  if a.updates:
   for rel,path in read(a.updates).items():
    data=Path(path).read_bytes();h=sha(data)
    if '/'not in rel and rel.endswith(('.py','.bat')):
     direct[rel]=data
     for entry in cat['entrypoints']:
      if entry['path']==rel:entry.update(bytes=len(data),sha256=h)
     if not any(e['path']==rel for e in cat['entrypoints']):cat['entrypoints'].append(dict(path=rel,bytes=len(data),sha256=h))
     changes.append(rel);continue
    packed=gzip.compress(data,compresslevel=6,mtime=0);codec='gzip'if len(packed)<len(data)else'raw';storage='objetos/'+h[:2]+'/'+h+('.gz'if codec=='gzip'else'');added[storage]=packed if codec=='gzip'else data
    row=dict(path=rel,bytes=len(data),sha256=h,storage=storage,compression=codec)
    index=next((i for i,x in enumerate(cat['files'])if x['path']==rel),None)
    if index is None:cat['files'].append(row)
    else:cat['files'][index]=row
    changes.append(rel)
  if a.validation:
   validation=read(a.validation);cat['release_verification']=validation
   for m in cat['mechanisms']:
    result=validation.get('mechanisms',{}).get(m['id'])
    if result:m['validation_this_release']=result;m['new_validation_status']=result.get('summary','Véase el informe de cierre')
  cat['revision']=dict(name='R01',utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),parent_zip_sha256=sha(a.source.read_bytes()),changes=changes,scope='Consolidación técnica sobre copias; código físico, decodificadores y referencias históricas conservados. Se distingue cada modalidad y alcance comprobado.')
  cat['files'].sort(key=lambda x:x['path']);used={r['storage']for r in cat['files']}
  cat['compression'].update(logical_files=len(cat['files']),logical_bytes=sum(r['bytes']for r in cat['files']),unique_blobs=len(used),unique_stored_bytes=sum(len(added[s])if s in added else src.getinfo(prefix+s).file_size for s in used))
  infos=src.infolist();positions={x.filename:x.header_offset for x in infos};ends={x.filename:(infos[i+1].header_offset if i+1<len(infos)else src.start_dir)for i,x in enumerate(infos)}
  with a.target.open('w+b',buffering=4*1024*1024)as destination,zipfile.ZipFile(destination,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6,allowZip64=True)as dest:
   for info in infos:
    rel=info.filename[len(prefix):]
    if rel=='CATALOGO.json'or rel in direct or(rel.startswith(('objetos/','motor/'))and(rel not in used or rel in added)):continue
    # Sin descomprimir ni recomprimir un blob ya verificado. El directorio
    # central se regenera con sus nuevos offsets por la biblioteca estándar.
    offset=dest.fp.tell();src.fp.seek(info.header_offset);remaining=ends[info.filename]-info.header_offset
    while remaining:
     block=src.fp.read(min(4*1024*1024,remaining))
     if not block:raise EOFError(info.filename)
     dest.fp.write(block);remaining-=len(block)
    record=copy.copy(info);record.header_offset=offset;dest.filelist.append(record);dest.NameToInfo[record.filename]=record;dest.start_dir=dest.fp.tell();dest._didModify=True
   for rel,data in added.items():dest.writestr(prefix+rel,data)
   for rel,data in direct.items():dest.writestr(prefix+rel,data)
   dest.writestr(prefix+'CATALOGO.json',json.dumps(cat,ensure_ascii=False,indent=2)+'\n')
 with zipfile.ZipFile(a.target)as z:
  assert len(z.namelist())==len(set(z.namelist()));assert z.testzip()is None;members=len(z.namelist())
 result=dict(zip=str(a.target),bytes=a.target.stat().st_size,sha256=sha(a.target.read_bytes()),members=members,crc_all_members=True,updated_logical_files=changes)
 (B/(a.target.stem+'_SELLO.json')).write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps(result,ensure_ascii=False))
if __name__=='__main__':main()
