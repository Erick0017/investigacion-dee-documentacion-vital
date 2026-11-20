"""No engine: locate the first violated nominal encounter, not a word target."""
from pathlib import Path
import argparse,gzip,json,sys
sys.path.insert(0,str(Path(__file__).parent))
from instrumentos_pc01 import idx,coord,packed,sha
p=argparse.ArgumentParser();p.add_argument('--evidence',type=Path,required=True);a=p.parse_args();out={}
for folder in sorted((a.evidence/'ACONTECIMIENTOS_UNO_26').glob('*')):
    path=folder/'PRIMARIOS.json'
    if not path.exists():continue
    prim=json.loads(path.read_bytes());n=67;event=prim['event'];start=event['start'];k=event['k'];delay=(11-k)//2;meet=event['nominal_AB_meet'];trace=folder/prim['trace']['file']
    with gzip.open(trace,'rt',encoding='utf8')as f:frames={r['tick']:{i:int(v)for i,v,c in r['rows']}for line in f if(r:=json.loads(line))}
    def at(t,q):return packed(frames[t].get(idx(q,n),0))
    def incoming(t,q):
        result=[]
        for i,v in frames[t].items():
            row=packed(v);site=coord(i,n)
            if any(row['direction'])and all(abs(z)<=1 for z in row['direction'])and[(site[j]+row['direction'][j])%n for j in range(3)]==q:result.append({'site':site,**row})
        return result
    paths={}
    for label,origin,direction in(('A',[38+k,50+k,8+k],[1,1,1]),('B',[49,50+k,8+(11+k)//2],[-1,1,0])):
        pathrows=[]
        for step in range(1,delay+1):
            t=start+step;q=[(origin[j]+step*direction[j])%n for j in range(3)];r=at(t,q);pathrows.append({'tick':t,'site':q,'post':r,'target_pre':at(t-1,q),'incoming':incoming(t-1,q),'same_nominal_content':r['direction']==direction and r['s_reg']==3 and r['state']==1})
        paths[label]=pathrows
    tail=[]
    for step in range(delay,14):
        q=[meet[0],(meet[1]+step-delay)%n,(meet[2]+step-delay)%n];t=start+step;tail.append({'tick':t,'site':q,'post':at(t,q),'target_pre':at(t-1,q),'incoming':incoming(t-1,q)})
    out[prim['case']]={'source':str(path),'sha256':sha(path),'trace_sha256':sha(trace),'event':event,'paths_until_AB':paths,'nominal_product_tail':tail,'bank_observations':[{ 'tick':r['tick'],'banks':r['banks']}for r in prim['critical']if r['tick']in(start+13,start+80)],'scope':'Nominalpathsarepredictionsonly. Stopclaiminglineageata failedexactedge; actualglobalframesandradius3witnessesretained. NoSpanishlabelused.'}
dest=a.evidence/'ACONTECIMIENTOS_SIN_PALABRA_26.json';dest.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({k:{'first_A_failure':next((r for r in v['paths_until_AB']['A'][:-1]if not r['same_nominal_content']),None),'meet':v['nominal_product_tail'][0],'at_bank':v['nominal_product_tail'][-1]}for k,v in out.items()},ensure_ascii=False))
