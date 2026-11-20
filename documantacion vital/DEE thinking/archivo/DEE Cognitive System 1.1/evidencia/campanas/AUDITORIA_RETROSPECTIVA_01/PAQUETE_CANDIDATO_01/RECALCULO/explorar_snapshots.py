"""Zero-tick exploration. Never imports the DEE runtime."""
from pathlib import Path
import argparse,json,sys,re
sys.path.insert(0,str(Path(__file__).resolve().parent))
from leer_estado import Snapshot,organization,fields,sha,load_json,index

ap=argparse.ArgumentParser();ap.add_argument('--root',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args();root=a.root
c=load_json(root/'CONTINUIDAD_ACCESO_ADAPTATIVO_01.json');chain=[]
p=c['states']['E1_ACCESO_ADAPTATIVO_01']
chain.append((p['life'],p['tick']))
p=p['parent']
while 'life_id'in p:
    chain.append((p['life_id'],p['tick']));p=p.get('historical_parent',{})
result={'method':'Read all existing checkpoints on the declared ancestral spine, bounded by each fork tick; ballistic locations are hypotheses, not unique lineage.','new_native_ticks':0,'chain':chain,'snapshots':[]}
for life,limit in reversed(chain):
    files=sorted((root/'sistema/estado/checkpoints').glob(life+'.T*.deetsnap.gz'),key=lambda p:int(p.name.split('.T')[1].split('.')[0]))
    for p in files:
        t=int(p.name.split('.T')[1].split('.')[0])
        if t>limit:continue
        s=Snapshot(p,False);site=[(27+s.tick-45028)%s.N,11,11];v=s.observation(site)
        row={'life':life,'source':str(p),'encoded_sha256':s.encoded_sha256,'tick':s.tick,'ballistic_site':site,'observation':v,'match_X5':v['state']==1 and v['semantic']==1 and v['s_reg']==5 and v['direction']==[1,0,0],'pending':len(s.pending)}
        result['snapshots'].append(row)
        print(life,s.tick,site,v['s_reg'],v['direction'],row['match_X5'],flush=True)
s=Snapshot(c['states']['E1_ACCESO_ADAPTATIVO_01']['snapshot'],False)
names={k:v for k,v in s.channels.items()if v['site'][1:]==[11,11]and v['direction']==[1,0,0]}
result['candidate_phase_aligned_inputs']=[]
receipts={r['id']:r for r in s.receipts}
for op in organization(s)['operations']:
    m=re.search(r'interface=(.*?) at=([0-9]+) load=5 receipt=([0-9]+)',op)
    if m and m[1]in names and(names[m[1]]['site'][0]-int(m[2]))%67==23:
        result['candidate_phase_aligned_inputs'].append({'operation':op,'channel':names[m[1]],'receipt':receipts.get(int(m[3]))})
a.out.parent.mkdir(exist_ok=True,parents=True);a.out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
