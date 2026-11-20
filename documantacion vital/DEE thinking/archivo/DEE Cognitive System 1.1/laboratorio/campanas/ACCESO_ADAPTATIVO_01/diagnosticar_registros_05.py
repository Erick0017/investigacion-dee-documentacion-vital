"""Read-only comparison of measured route frames; no engine import."""
from pathlib import Path
import argparse,gzip,json
p=argparse.ArgumentParser();p.add_argument('--primary',type=Path,required=True);a=p.parse_args();v=json.loads(a.primary.read_bytes());n=67
def pack(raw):
    raw=int(raw);d=[]
    for k in(48,52,56):
        z=(raw>>k)&15;d.append(z-16 if z&8 else z)
    return {'state':raw&0xffffffff,'s_reg':(raw>>32)&65535,'semantic':raw>>60,'direction':d}
def ix(q):return(q[0]*n+q[1])*n+q[2]
S=v['geometry']['policy'];routes=v['geometry']['training_routes'];found=[]
with gzip.open(a.primary.parent/'CAMPOS_REVISION.jsonl.gz','rt',encoding='utf8')as f:
    for line in f:
        q=json.loads(line);t=q['tick']-v['epoch'];rows={i:r for i,r,c in q['rows']};item={'t':t,'at_policy':pack(rows.get(ix(S),'0')),'routes':{}}
        if t in(9,13,18,19,80,85,86):
            for key,z in routes.items():
                if t==9:site=z['query']
                elif t in (13,80):site=z['outcome']
                else:
                    launch=13 if t<67 else 80
                    direction=(z['j'],-z['r'],0)
                    site=[(z['outcome'][k]+(t-launch)*direction[k])%n for k in range(3)]
                item['routes'][key]={'site':site,'native':pack(rows.get(ix(site),'0'))}
            found.append(item)
print(json.dumps(found,ensure_ascii=False,indent=2))
