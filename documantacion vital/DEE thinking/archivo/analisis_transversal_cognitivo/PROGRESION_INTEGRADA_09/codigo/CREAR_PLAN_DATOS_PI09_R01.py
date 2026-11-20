"""Pure prefixed sample yoke from all12 actual always-real primaries.
No Native, DEE, return labels, selection of favourable permutation or actor.
Outputs a JSON object; pass its compact JSON text as the prepare literal plan.
"""
from pathlib import Path
import argparse,hashlib,json,re
P=Path(__file__).resolve().parents[1]
def sha(data):return hashlib.sha256(data).hexdigest()
def canon(value):return json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode('utf8')
def require(ok,why):
    if not ok:raise ValueError(why)
def main(args):
    require(re.fullmatch(r'[A-Za-z0-9_]+',args.prefijo)is not None,'Source prefix must be one bounded literal tag, no paths/globs')
    files=sorted((P/'ensayos').glob(args.prefijo+'*.json'));samples={};references=[]
    for file in files:
        raw=file.read_bytes();p=json.loads(raw);v=p.get('result');v=json.loads(v)if isinstance(v,str)else v
        if v is None:continue
        for row in v.get('result',v).get('rows',[]):
            if row.get('version')not in {'DEE.PI09.selective_registered_consultation.R01','DEE.PI09.selective_registered_consultation.R02'}or'first_stage'not in row:continue
            require(p['status']=='completed'and row['query_control']=='always'and row['information_control']=='real','Only actual completed always-real material source')
            i=row['ordinal'];require(i not in samples and 0<=i<12,'Exactly once each source ordinal')
            observation=row['first_stage']['sample_register']['actual_preview_observation']
            rawint=int(observation['raw']);ds=[(rawint>>s)&15 for s in(48,52,56)];fields={'state':rawint&0xffffffff,'s_reg':(rawint>>32)&65535,'semantic':rawint>>60,'direction':[x-16 if x&8 else x for x in ds]}
            require(all(observation[k]==v for k,v in fields.items()),'RAW source decoder mismatch')
            require(rawint==0 or(fields['state']>0 and fields['semantic']==1 and fields['direction']in([1,0,0],[0,0,1])),'Unrecognized source sample: preserve blocked plan, no fill or new permutation')
            samples[i]={'ordinal':i,'observation':observation,'observation_sha256':sha(canon(observation)),'primary_sha256':sha(raw)};references.append({'file':str(file),'sha256':sha(raw)})
    require(set(samples)==set(range(12)),'All12 source opportunities must exist and be complete; no partial yoke')
    sourcehash=sha(Path(args.evidencia).read_bytes())if args.evidencia else sha(canon(sorted(references,key=lambda x:x['file'])))
    plan={'schema':'DEE.PI09.actual_RAW_sample_yoke.v1','permutation':[(i+5)%12 for i in range(12)],'source_arm':'always_real','source_evidence_sha256':sourcehash,'samples':[samples[i]for i in range(12)]}
    encoded=canon(plan);require(len(encoded)<=6500,'Plan exceeds explicit local transport bound')
    out=Path(args.salida).absolute();require(out.is_relative_to(P.resolve())and not out.exists(),'New output inside PI09 only')
    with out.open('xb')as f:f.write(encoded+b'\n')
    print(json.dumps({'plan':str(out),'sha256':sha(out.read_bytes()),'samples':12,'permutation':'source_plus_5','UTF8_bytes':len(encoded),'Native_executed':False,'no_permutation_search':True}))
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--prefijo',default='PI09_ALWAYS_R03');ap.add_argument('--evidencia');ap.add_argument('--salida',required=True);main(ap.parse_args())
