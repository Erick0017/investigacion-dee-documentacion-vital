"""Compact exact-subtree extraction from original receipts/observations.
No DEE import or native ticks. Removed subtrees have canonical hashes and
original locators. This is NOT a byte-identical or complete historical backup.
"""
from pathlib import Path
import argparse,gzip,hashlib,json
LAB=Path(__file__).resolve().parent;ROOT=LAB.parents[2]
EV=ROOT/'evidencia/campanas/CONSOLIDACION_EVOLUCION_E1_CICLO_02'
OUT=EV/'EXPORTACION/EVIDENCIA_CAUSAL/PRIMARIOS'
def canonical(v):return json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode('utf8')
def sha(b):return hashlib.sha256(b).hexdigest()
def escape(k):return str(k).replace('~','~0').replace('/','~1')
DROP={'body_frames','social_frames','passive_trace','operational_protocol','context125','context'}
def prune(v,pointer,omitted):
    if isinstance(v,dict):
        out={}
        for k,q in v.items():
            p=pointer+'/'+escape(k)
            if k in DROP and isinstance(q,(list,dict))and q:
                b=canonical(q);omitted.append({'pointer':p,'canonical_sha256':sha(b),'canonical_bytes':len(b),'items':len(q),'reason':'Deep passive context/protocol kept locally; all actions/receipts/endpoints and selected full witnesses exported separately.'})
            else:out[k]=prune(q,p,omitted)
        return out
    if isinstance(v,list):return[prune(q,pointer+'/'+str(i),omitted)for i,q in enumerate(v)]
    return v
def short_life(d):
    return{k:d[k]for k in('life_id','world_id','profile','branch','parent','snapshot','snapshot_sha256','physical','availability')if k in d}
def get_payload(d):
    if 'data'in d:return d['data'].get('result',d['data']),'/data/result'if 'result'in d['data']else'/data'
    if 'returncode'in d:
        r=d.get('result',{})
        if isinstance(r,dict)and'result'in r:return r['result'],'/result/result'
        return r,'/result'
    if 'error'in d:return d['error'],'/error'
    return d,''
def export(p):
    raw=p.read_bytes();d=json.loads(raw);payload,pointer=get_payload(d);omitted=[]
    # Passive status commands may contain full previous operations. Keep their
    # actual physical/protocol state; no duplicate serialized life histories.
    if isinstance(payload,dict)and'operations'in payload:
        omitted.append({'pointer':pointer+'/operations','canonical_sha256':sha(canonical(payload['operations'])),'reason':'Duplicated previous life operations remain in original; actual operation primaries are separately exported.'})
        payload={k:v for k,v in payload.items()if k!='operations'}
    out={'schema':'DCS.C02.primary.exact-subtrees.v1','id':p.stem,
        'original':{'path':str(p.relative_to(ROOT)),'bytes':len(raw),'sha256':sha(raw)},
        'payload_pointer':pointer,'payload':prune(payload,pointer,omitted),
        'omissions':omitted,'native_ticks_during_extraction':0}
    for a,b in(('before','initial_life'),('after','final_life')):
        if a in d:out[b]=short_life(d[a])
    for k in('id','life','returncode','argv','wall_seconds','stderr','error','code'):
        if k in d:out[k]=d[k]
    if 'returncode'in d and isinstance(d.get('result'),dict)and'INSTRUMENTO'in d['result']:
        out['instrument_context']=d['result']['INSTRUMENTO']
        out.setdefault('life',d['result']['INSTRUMENTO'].get('life_id'))
    # Deterministic gzip; originals are never overwritten.
    path=OUT/(p.stem+'.json.gz');blob=gzip.compress(canonical(out),compresslevel=9,mtime=0);path.write_bytes(blob)
    check=json.loads(gzip.decompress(path.read_bytes()));assert check==out
    return{'id':p.stem,'original':out['original'],'extracted_path':str(path.relative_to(EV/'EXPORTACION')),
           'extracted_bytes':len(blob),'sha256':sha(blob),'omitted_subtrees':len(omitted),'payload_canonical_sha256':sha(canonical(out['payload']))}
if __name__=='__main__':
    parser=argparse.ArgumentParser();a=parser.parse_args();OUT.mkdir(parents=True,exist_ok=True)
    rows=[]
    for p in sorted(EV.glob('C02_*.json')):
        d=json.loads(p.read_text(encoding='utf8'))
        if 'data'not in d and'returncode'not in d and'error'not in d:continue
        rows.append(export(p))
    index={'extraction':'Exact retained JSON subtrees and exact integer/string values, not identical original JSON bytes. Original bytes hashes and omitted subtree locators retained. No native reproduction claimed.',
           'files':rows,'total_original_bytes':sum(r['original']['bytes']for r in rows),'total_extracted_bytes':sum(r['extracted_bytes']for r in rows)}
    (OUT.parent/'INDICE_EXTRACCION.json').write_bytes(canonical(index))
    print(json.dumps({'files':len(rows),'original_bytes':index['total_original_bytes'],'extracted_bytes':index['total_extracted_bytes']},ensure_ascii=False))
