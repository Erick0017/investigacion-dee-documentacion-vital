"""Read existing records only; no engine import, no native ticks."""
import json
from pathlib import Path
L=Path(__file__).resolve().parent;E=L.parents[2]/'evidencia/campanas/MENTE_DEE_INTEGRAL_MI01'
names=['MI01_SELECTOR_10','MI01_DIRECCION_40','MI01_PROTECCION_170','MI01_RETORNO_PROTEGIDO_211','MI01_COMPUESTA_220','MI01_ESPANOL_150','MI01_COMPARTIDO_270','MI01_252_MOTOR','MI01_315_MAIN_RETENCION_EXTERNA','MI01_321_MAIN_REUSO']
for name in names:
    d=json.loads((E/(name+'.json')).read_bytes());z=d.get('data',d.get('result',{}));v=z.get('result',z)
    print(name,'outer=',list(d),'body=',list(v)if isinstance(v,dict)else type(v).__name__)
    if isinstance(v,dict):
        for k,x in v.items():
            if isinstance(x,list)and x:print(' list',k,len(x),'first=',list(x[0])if isinstance(x[0],dict)else type(x[0]).__name__)
            elif isinstance(x,dict):print(' map',k,list(x)[:12])
