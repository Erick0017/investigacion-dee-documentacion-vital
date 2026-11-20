"""Read-only archive/JSON reconnaissance. Never imports DEE or executes science."""
from pathlib import Path
import argparse,json,zipfile,hashlib,sys
sys.stdout.reconfigure(encoding='utf8')

def shape(x,depth=1):
    if isinstance(x,dict):
        return {k:shape(v,depth-1) if depth>0 else (str(type(v).__name__)+('['+str(len(v))+']' if isinstance(v,(list,dict,str))else ':'+str(v))) for k,v in x.items()}
    if isinstance(x,list):return {'length':len(x),'first':shape(x[0],depth)if x else None}
    return x if not isinstance(x,str) or len(x)<300 else x[:300]+'…'

def main():
    p=argparse.ArgumentParser();p.add_argument('source',type=Path);p.add_argument('--match',default='');p.add_argument('--member');p.add_argument('--depth',type=int,default=1);p.add_argument('--full',action='store_true');p.add_argument('--pointer',default='');a=p.parse_args()
    def choose(x):
        for k in a.pointer.strip('/').split('/')if a.pointer else []:x=x[int(k)]if isinstance(x,list)else x[k]
        return x
    if a.source.suffix.lower()=='.zip':
        with zipfile.ZipFile(a.source)as z:
            if a.member:
                b=z.read(a.member);print('MEMBER_SHA256',hashlib.sha256(b).hexdigest())
                if a.member.endswith(('.json','.jsonl')):
                    x=json.loads(b)if a.member.endswith('.json')else[json.loads(l)for l in b.splitlines()if l.strip()]
                    x=choose(x);print(json.dumps(x if a.full else shape(x,a.depth),ensure_ascii=False,indent=2))
                else:print(b.decode('utf-8-sig'))
            else:
                for i in z.infolist():
                    if a.match in i.filename:print(i.file_size,i.compress_size,i.filename)
    else:
        x=choose(json.loads(a.source.read_text(encoding='utf-8-sig')));print(json.dumps(x if a.full else shape(x,a.depth),ensure_ascii=False,indent=2))
if __name__=='__main__':main()
