from pathlib import Path
import json,hashlib
H=Path(__file__).resolve().parent;C=H.parents[3]/'DEE Cognitive 2.0'
names=('PROYECTO.json','CONTINUIDAD_DEE_COGNITIVE_2_0.json','sistema/estado/ACTIVO.json','sistema/estado/genesis/SELECCION_PERSONAL.json','aplicacion/GENESIS/SELECCION_CANDIDATA.json','sistema/capacidades/CATALOGO_CAPACIDADES.json')
for name in names:
 p=C/name;v=json.loads(p.read_text('utf-8-sig'))
 print('\nFILE',name,'SHA',hashlib.sha256(p.read_bytes()).hexdigest(),'KEYS',list(v)if isinstance(v,dict)else'LIST')
 if name.endswith('CATALOGO_CAPACIDADES.json'):
  def walk(x,path=''):
   if isinstance(x,dict):
    if x.get('id')=='PI10_R02_CONSULTA_CONTEXTO_DOS_TRAZAS':print('PI10_ENTRY',path,json.dumps(x,ensure_ascii=False,indent=2))
    for k,z in x.items():
     if 'PI10' in str(k)or'current' in str(k)or'manual' in str(k):print('FIELD',path+'/'+str(k),json.dumps(z,ensure_ascii=False)[:2500])
     walk(z,path+'/'+str(k))
   elif isinstance(x,list):
    for i,z in enumerate(x):walk(z,path+'/'+str(i))
  walk(v)
 else:
  for k,z in v.items():
   if any(t in k.lower()for t in('prior','history','historical','before','alternative','stage','adopt','extension','confirmed','source')):continue
   print('FIELD',k,json.dumps(z,ensure_ascii=False)[:4500])

