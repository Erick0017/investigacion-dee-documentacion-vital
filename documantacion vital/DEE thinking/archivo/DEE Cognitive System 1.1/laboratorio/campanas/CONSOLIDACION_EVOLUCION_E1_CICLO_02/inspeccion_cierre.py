"""Read existing primaries only; no engine import and zero native ticks."""
from pathlib import Path
import json,hashlib
LAB=Path(__file__).resolve().parent
ROOT=LAB.parents[2]
EV=ROOT/'evidencia/campanas/CONSOLIDACION_EVOLUCION_E1_CICLO_02'
def payload(d):
    if 'data'in d:return d['data'].get('result',d['data'])
    if 'returncode'in d:
        z=d.get('result',{})
        return z.get('result',z)if isinstance(z,dict)else z
    return d
def concise(p):
    d=json.loads(p.read_text(encoding='utf8'));v=payload(d)
    out={'id':p.stem,'keys':list(v)if isinstance(v,dict)else type(v).__name__}
    if isinstance(v,dict):
        for k in('mode','initial','final','final_environment','end_tick','tick'):
            if k in v:out[k]=v[k]
        if 'rows'in v:
            out['rows']=[]
            for r in v['rows']:
                rr={k:r[k]for k in('index','tick','force_sensor','native_action','executed_action','environment','utility_auditor_only','useful_auditor_only','private_object','valid','correct','received_codes')if k in r}
                if 'native_pre'in r:rr['pre_reference']=r['native_pre']['reference']
                if 'native_response'in r:rr['response']=r['native_response']
                if 'after'in r:rr['after']=r['after']
                if 'external'in r:rr['external_keys']=list(r['external'])
                out['rows'].append(rr)
    return out
if __name__=='__main__':
    for pattern in('C02_REUSO_13*.json','C02_MAIN_171_USO.json','C02_MAIN_172_USO.json','C02_MAIN_173_ANTERIORES.json','C02_MAIN_174_PUERTA.json','C02_MAIN_175_EXTERNO.json','C02_BOUND_14*.json'):
        for p in sorted(EV.glob(pattern)):print(json.dumps(concise(p),ensure_ascii=False))
    states=[]
    for name in('E1_SOCIAL_11','E1_CICLO02_MAIN','E1_CICLO02_CORTE_VALIDADO_20927','C02_SELECTOR_USO_151','E1_SELECTOR_CONSERVADO_C02'):
        p=ROOT/'sistema/estado/vidas'/name/'VIDA.json';d=json.loads(p.read_text(encoding='utf8'))
        states.append({k:d[k]for k in('life_id','profile','physical','snapshot','snapshot_sha256','availability')if k in d})
    print(json.dumps({'states':states},ensure_ascii=False))
    files=[p for p in EV.rglob('*')if p.is_file()]
    print(json.dumps({'evidence_files':len(files),'expanded_bytes':sum(p.stat().st_size for p in files),'largest':[(p.name,p.stat().st_size)for p in sorted(files,key=lambda x:x.stat().st_size,reverse=True)[:6]]}))
