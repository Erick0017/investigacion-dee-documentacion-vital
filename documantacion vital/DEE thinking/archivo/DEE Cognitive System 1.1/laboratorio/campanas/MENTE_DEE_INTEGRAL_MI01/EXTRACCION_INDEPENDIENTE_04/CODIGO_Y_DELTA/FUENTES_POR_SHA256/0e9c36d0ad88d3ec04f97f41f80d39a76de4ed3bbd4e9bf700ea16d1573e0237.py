"""Selected passive microscopic replay of reserved window1, not MAIN repair."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from comun import *
from controles_desde_prefijo_fijado import prefix,name
from capacidades.mente_integral_mi01 import externo_selector as motor,saved
from capacidades.integracion_situada_01 import ic_native_core as n
from capacidades.observador_causal_retrospectivo_01 import Snapshot,compare,organization
life='MI01_OBSERVACION_PASIVA_470';fork('E1_MI01_MAIN',life,checkpoint=prefix())
atomic_json(E/'OBSERVADOR_PROTOCOLO_470.json',{'prefix_sha256':sha(prefix()),'scope':'Replay exact reserved1 in a diagnostic copy; no new teaching/candidate and no returned future. Record both possible first-failure reply paths and exact pre/post turn times.','inocuity':'Compare full RAW,clocks,pending,channels,receipts and owner sections against the real reserved1 boundary, not text alone. Metadata/life documentary differences reported separately.','snapshot_limit':'Mid-step traces are physical diagnostic snapshots, NOT supported continuation checkpoints: local in-flight bridge variables have not yet all been committed. The final Store boundary is operational.'})
def fn(a):
    cfg=saved(a);h=cfg['native_habitats'][name];f=h['direct_failure']['opportunities'][0];rp=cfg['selector_returns'][f['reply_name']];qp=cfg['material_queries'][f['query_name']];q=h['plans'][0]['query_tick'];times={};end=q+339
    def at(t,label,site,expected=None):
        if a.tick<t<=end:times.setdefault(t,[]).append({'label':label,'site':site,'expected_direction':expected})
    at(q,'first_action',h['S']);at(q+16,'native_failure_question',h['S']);at(qp['comparison_arrival'],'B_arrival',qp['B']);at(qp['source_tick'],'B_private_reply',qp['B'])
    for sign,r in rp['routes'].items():
        for i,turn in enumerate(r['turns']):
            at(turn['tick']-1,'pre_return_'+sign+'_'+str(i),turn['site']);at(turn['tick'],'post_return_'+sign+'_'+str(i),turn['site'],turn['outgoing'])
        for step in r['travel']:
            at(step['tick_after'],'travel_'+sign+'_'+str(step['tick_after']),step['site_after'],step['direction'])
    at(rp['arrival_tick']-1,'pre_selector_return',rp['S']);at(rp['arrival_tick'],'selector_return',rp['S'])
    original=a.run_until;frames=[]
    def log_until(t):
        for when in sorted(k for k in times if a.tick<k<=t):
            original(when);items=[]
            for event in times[when]:
                p=event['site'];context=[]
                for dx in(-1,0,1):
                    for dy in(-1,0,1):
                        for dz in(-1,0,1):
                            context.append(n.obs(a,[(p[0]+dx)%67,(p[1]+dy)%67,(p[2]+dz)%67]))
                items.append({**event,'native':n.obs(a,p),'context27':context})
            snap=E/(life+'.T'+str(when)+'.DIAGNOSTICO_NO_OPERATIVO.deetsnap.gz');a.save(snap)
            frames.append({'tick':when,'items':items,'physical':physical(a.world,occupation=True),'diagnostic_snapshot':str(snap.relative_to(R)),'snapshot_sha256':sha(snap),'coverage':'Local27 sampling plus complete raw/clocks/full stored world. Causal dependency of the full tick is not asserted to end at Moore26.'})
        original(t)
    a.run_until=log_until
    try:r=motor.run(a,steps=16,mode='closed',feedback='cost',transition=True,habitat=name,motor_codec='native_body_roles')
    finally:a.run_until=original
    final=E/(life+'.FINAL_OPERATIVO.deetsnap.gz');a.save(final)
    return{'external':r,'frames':frames,'route_plan':rp,'query_plan':qp,'final_snapshot':str(final.relative_to(R)),'final':physical(a.world,occupation=True)}
v=run(life,'MI01_470_TRAZA_RESERVA',fn)['result']
target='3429dc96e70df2abe142300864ca3e1c7c1583c96f16c0b5d7382bba3bcc7320';original=None
for p in(S/'estado/checkpoints').glob('E1_MI01_MAIN.T25757.*.deetsnap.gz'):
    if sha(p)==target:original=p;break
if original is None:raise FileNotFoundError('Exact actual reserved1 boundary missing')
x=Snapshot(original);y=Snapshot(R/v['final_snapshot']);c=compare(x,y);z={'native_ticks_of_this_recalculation':0,'comparison':c,'physical_and_agenda_equal':x.raw==y.raw and x.clocks==y.clocks and x.pending==y.pending and x.channels==y.channels and x.receipts==y.receipts,'different_owner_sections':c['different_owner_sections'],'original_snapshot_sha256':target,'replay_final_sha256':y.encoded_sha256,'scope':'The replay itself has new diagnostic ticks and is technical reproduction, not independent learning. This final comparison computes0ticks. Documentary metadata differences are not silently removed.'};atomic_json(E/'OBSERVADOR_INOCUIDAD_470.json',z);print(json.dumps(z,ensure_ascii=False))
