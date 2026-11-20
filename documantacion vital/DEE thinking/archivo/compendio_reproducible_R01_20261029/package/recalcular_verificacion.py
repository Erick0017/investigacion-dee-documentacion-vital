"""Recalcula campos exactos de los informes exportados; cero ticksNative."""
from pathlib import Path
import argparse,gzip,json,importlib.util
_spec=importlib.util.spec_from_file_location('r01_reproduccion_verificada',Path(__file__).resolve().parent/'reproducir.py')
reproducir=importlib.util.module_from_spec(_spec);_spec.loader.exec_module(reproducir)
def walk(x):
 if isinstance(x,dict):
  yield x
  for key,value in x.items():
   if key=='result_json'and isinstance(value,str):
    try:value=json.loads(value)
    except ValueError:pass
   yield from walk(value)
 elif isinstance(x,list):
  for value in x:yield from walk(value)
def run():
 cat=reproducir.catalogue();errors=[];raw_fields=0;matches=0;different=0;files=[]
 for row in cat['files']:
  if not row['path'].startswith('verificacion/primarios/'):continue
  data=reproducir.content(row)
  if row['path'].endswith('.gz'):data=gzip.decompress(data)
  doc=json.loads(data);files.append(row['path'])
  for obj in walk(doc):
   if 'matches'in obj and isinstance(obj['matches'],bool):matches+=obj['matches'];different+=not obj['matches']
   if 'raw'not in obj or not any(isinstance(obj.get(k),int)for k in('state','s_reg','semantic')):continue
   try:raw=int(obj['raw'])
   except (ValueError,TypeError):continue
   if isinstance(obj['raw'],float)or not 0<=raw<2**64:errors.append([row['path'],'uint64_domain']);continue
   decoded={'state':raw&0xffffffff,'s_reg':(raw>>32)&65535,'semantic':(raw>>60)&15}
   for key,value in decoded.items():
    if isinstance(obj.get(key),int):
     raw_fields+=1
     if obj[key]!=value:errors.append([row['path'],key,str(raw),obj[key],value])
 result=dict(mode='RECALCULO_ARCHIVADO_SIN_MOTOR',new_native_ticks=0,files=len(files),raw_fields_recomputed=raw_fields,comparison_flags_true=matches,comparison_flags_false=different,errors=errors,scope='Los flagsFalse incluyen intentos parciales/negativos y fallos del anfitrión conservados; no se reinterpretan como un fallo general deDEE.')
 return result
if __name__=='__main__':
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--salida',type=Path);a=parser.parse_args();r=run();text=json.dumps(r,ensure_ascii=False,indent=2)+'\n'
 if a.salida:
  if a.salida.exists():raise FileExistsError(a.salida)
  a.salida.write_text(text,encoding='utf8')
 print(text);raise SystemExit(bool(r['errors']))
