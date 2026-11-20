"""Only two frozen proof JSONs; no current Native root, database or runtime."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
names=['evidencia/PUNTO34_R06/PAREJA_INTEGRAL_V3.json',
       'evidencia/CTRL1_SEIS_R06/CONCILIACION_CIERRE_R06.json']
def walk(value,pointer,found):
    if isinstance(value,dict):
        if any(k.lower()in('raw_sha256','clocks_sha256')for k in value):
            found.append({'pointer':pointer,'physical':{k:v for k,v in value.items()
                if k in('N','tick','RAW_sha256','raw_sha256','clocks_sha256')}})
        for key,v in value.items():walk(v,pointer+'/'+str(key),found)
    elif isinstance(value,list):
        for i,v in enumerate(value):walk(v,pointer+'/'+str(i),found)
result=[]
for name in names:
    value=json.loads((ROOT/name).read_text('utf-8-sig'));matches=[];walk(value,'',matches)
    result.append({'file':name,'root_keys':list(value)[:25],'matches':matches})
print(json.dumps(result,ensure_ascii=False))
