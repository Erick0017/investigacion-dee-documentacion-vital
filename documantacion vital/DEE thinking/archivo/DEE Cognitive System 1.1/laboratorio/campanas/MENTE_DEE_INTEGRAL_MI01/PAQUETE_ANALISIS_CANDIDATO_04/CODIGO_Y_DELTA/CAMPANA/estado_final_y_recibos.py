"""Complete-state retrospective counts, no engine import or new ticks."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from comun import *
from capacidades.observador_causal_retrospectivo_01 import Snapshot,fields
from collections import Counter
labels={1:'SCHEDULED',2:'APPLIED',3:'REJECTED_LATE',4:'REJECTED_INVALID',5:'REJECTED_OCCUPIED',6:'REJECTED_CONFLICT',7:'REJECTED_QUEUE_FULL'}
def find(h):
    for p in(S/'estado/checkpoints').glob('E1_MI01_MAIN.T24752.*.deetsnap.gz'):
        if sha(p)==h:return p
    raise FileExistsError('Required complete known prefix not found')
sealed=json.loads((E/'SELLO_EVALUACION_FIJADA.json').read_bytes());x=Snapshot(S/sealed['selected_snapshot']);p=find('afc1d19c27da44ec1810704cfd08cd6c2c2ff0148dcc5af8411f7b91c9402713');y=Snapshot(p);r=Store().record('E1_MI01_MAIN');z=Snapshot(S/r['snapshot']);old={v['id']for v in x.receipts};prepared={v['id']for v in y.receipts};new=[v for v in z.receipts if v['id']not in old]
groups={}
for name,rows in[('all_since_preparation400',new),('frozen_native_preparation',[v for v in new if v['id']in prepared]),('external_and_post_free',[v for v in new if v['id']not in prepared])]:
    groups[name]={'requested_unique_event_ids':len(rows),'status_counts':dict(Counter(labels[v['status']]for v in rows)),'receipts':rows}
old_sites=[('negative7',[31,59,26]),('positive7',[11,59,23]),('lateral7',[11,48,29]),('new_positive145',[10,56,26]),('selector40',[40,35,55])]
distribution=Counter((fields(v)['state'],fields(v)['semantic'],fields(v)['s_reg'],tuple(fields(v)['direction']))for v in z.raw)
out={'native_ticks':0,'before':x.summary(),'prepared':y.summary(),'final':z.summary(),'final_record':{k:r[k]for k in('life_id','profile','parent','snapshot','snapshot_sha256','physical')},'receipt_groups':groups,'current_raw_port_observations':[{'id':k,'native':z.observation(site)}for k,site in old_sites],'most_frequent_raw_classes':[{'state':k[0],'semantic':k[1],'s_reg':k[2],'direction':list(k[3]),'sites':n}for k,n in distribution.most_common(12)],'port_observation_limit':'Read at the actual current tick, not assumed phase3. A field, code signature or raw difference alone does not certify native recall/meaning.','interpretation_limit':'RAW equality within one world is not convergence of different complete histories. Clocks, owner progress, queues and external state remain causal data.'}
atomic_json(E/'ESTADO_FINAL_Y_RECIBOS_440_0TICKS.json',out);print(json.dumps({'final_tick':z.tick,'occupied':out['final']['occupied'],'pending':len(z.pending),'groups':{k:{a:b for a,b in v.items()if a!='receipts'}for k,v in groups.items()},'ports':out['current_raw_port_observations']},ensure_ascii=False))
