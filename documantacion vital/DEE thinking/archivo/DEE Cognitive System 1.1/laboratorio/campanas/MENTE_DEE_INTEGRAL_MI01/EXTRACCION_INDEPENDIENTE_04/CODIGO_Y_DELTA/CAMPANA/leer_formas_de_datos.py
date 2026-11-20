"""Zero-tick structural reading for the portable auditor."""
import json
from pathlib import Path
L=Path(__file__).resolve().parent;E=L.parents[2]/'evidencia/campanas/MENTE_DEE_INTEGRAL_MI01'
names=['MI01_CONSULTA_110','MI01_PROTECCION_170','MI01_RETORNO_PROTEGIDO_211','MI01_COMPOSICION_30','MI01_100_MAIN_COMPOSICION','MI01_ESPANOL_150','MI01_B_OPERANDOS_306','MI01_DIRECCION_40','MI01_411_MAIN_RESERVA_1']
def outline(d,depth=0):
    if depth>=3:return type(d).__name__
    if isinstance(d,dict):return{k:outline(v,depth+1)for k,v in d.items()if k not in('requests','before','after','metadata','sources','plan','training','experience','initial','final')}
    if isinstance(d,list):return{'count':len(d),'first':outline(d[0],depth+1)if d else None}
    return str(d)[:100]
for name in names:
    p=E/(name+'.json')
    if not p.exists():continue
    d=json.loads(p.read_bytes());z=d.get('data',d.get('result',{}));v=z.get('result',z)
    print(name,json.dumps(outline(v),ensure_ascii=False))
