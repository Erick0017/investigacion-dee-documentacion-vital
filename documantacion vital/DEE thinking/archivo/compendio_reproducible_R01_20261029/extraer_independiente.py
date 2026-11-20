from pathlib import Path
import argparse,json,hashlib,zipfile,datetime
p=argparse.ArgumentParser();p.add_argument('zip',type=Path);p.add_argument('destination',type=Path);a=p.parse_args()
if a.destination.exists():raise FileExistsError(a.destination)
with zipfile.ZipFile(a.zip)as z:
 assert len(z.namelist())==len(set(z.namelist()))
 for info in z.infolist():
  path=Path(info.filename);assert not path.is_absolute()and '..'not in path.parts and ':'not in info.filename
 z.extractall(a.destination) # La lectura completa compruebaCRC de cada miembro.
 count=len(z.namelist())
root=a.destination/'DEE_COMPENDIO_REPRODUCIBLE';cat=json.loads((root/'CATALOGO.json').read_bytes())
result=dict(zip=str(a.zip),bytes=a.zip.stat().st_size,sha256=hashlib.sha256(a.zip.read_bytes()).hexdigest(),members=count,all_members_extracted_with_crc=True,root=str(root),mechanisms=len(cat['mechanisms']),logical_files=len(cat['files']),original_source_directories_read=False,utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
(a.destination/'EXTRACCION_VERIFICADA.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps(result,ensure_ascii=False))
