"""Integrated MI02 native habitat; no host reads a failure to ask B."""
import json
from dee_thinking.persistence import encode_metadata,decode_metadata
from capacidades import arquitectura_distribuida_mi02_r8 as body
from capacidades import distribucion_social_mi02_r2 as social
from app.native_tools import physical
KEY='DEE.Cognitive.System.1.1.MI02.unified.v1'

def saved(a):
    m=dict(a.world.runtime.snapshot_metadata_entries);return decode_metadata(m[KEY])if KEY in m else None

def put(a,s):a.world.runtime.set_snapshot_metadata(KEY,encode_metadata(json.loads(json.dumps(s,allow_nan=False))))

def acquire(a,*,geometry,own=(10,10),private=(47,17)):
    if saved(a)is not None:raise ValueError('Already lived; no silent reconstruction')
    g=json.loads(json.dumps(geometry));t=a.tick+8;rr=[]
    rr.append(body.send(a,'MI02.unified.A.reader',g['A'],(0,0,-1),t,0))
    for participant,values in(('A',own),('B',private)):
        for j,value in enumerate(values):
            if value is not None:rr.append(body.send(a,'MI02.unified.'+participant+'.sample.'+str(j),body.xyz(a,g[participant],(-1 if j==0 else 1,1,1)),(0,0,0),t+4*j,int(value)))
    a.run_until(t+20)
    put(a,{'schema':'MI02.unified.r3','geometry':g,'index':0,'history':[{'kind':'RAW_SCALAR_EXPERIENCES_ONLY','tick':t,'own':list(own),'B_private_only':list(private)}],'query_initiation':'No host call activates B. Native x0 material enters a prepared gate with generic load5.','motor_role_codec':'x+ left, x- right, x0 query. Absence/invalidity is not a native wait decision.'})
    social.put(a,{**g['social'],'current_tick':a.tick,'deferred_B_reader':True})
    body.put(a,{'schema':'MI02.unified.motor_view','Q':g['A'],'memories':[body.xyz(a,g['A'],v)for v in[(-1,1,1),(1,1,1)]],'N':g['N'],'index':0,'pending':[],'route_revision':'unified_r3','zero_role':'query','initial_experiences':list(own),'external_sensors':g['external_sensors']})
    return{'requests':body.receipts(a,rr),'after':state(a),'B_reader_not_initialized_by_host':True}

def state(a):
    s=saved(a)
    if not s:raise ValueError('No actual MI02 unified lived state')
    return{'physical':physical(a.world,occupation=True),'regions':social.state(a),'query_gate':body.obs(a,s['geometry']['query'][-1]['head']),'index':s['index'],'motor_role_codec':s['motor_role_codec'],'prepared_vs_acquired':s['query_initiation']}

def live(a,*,availability,mode='intact',trace=True):
    if not 1<=len(availability)<=32 or any(v not in(-1,1)for v in availability)or mode not in('intact','omit_return'):raise ValueError('Finite exogenous environmental sequence required')
    s=saved(a)
    if not s:raise ValueError('Existing unified life required')
    g=s['geometry'];C=g['A'];first=391+782*max(0,(a.tick+30-391+781)//782);requests=[];plans=[]
    for i,available in enumerate(availability):
        plan=body.cycle_plan(a,{'Q':C},available,first+782*i);plan['sources']=[v for v in plan['sources']if not v['name'].startswith('MI02.outer.0.')];plan['routes']=[v for v in plan['routes']if v['r']];plans.append(plan)
        if mode!='omit_return':
            for v in plan['sources']:requests.append(body.send(a,v['name'],v['site'],v['direction'],v['tick'],v['payload']))
    rows=[]
    for plan in plans:
        crit=plan['critical'];frames=[];times=range(crit-20,crit+81)if trace else(crit-20,crit-15,crit,crit+3,crit+40,crit+80)
        for t in times:
            a.run_until(t);row={'tick':t,'A':body.obs(a,C),'M':[body.obs(a,p)for p in body.get(a)['memories']],'B':body.obs(a,g['B']),'contacts':{str(r):body.obs(a,body.xyz(a,C,(r,-1,-1)))for r in(-1,0,1)},'query_gate':body.obs(a,g['query'][-1]['head'])}
            if trace:row['query_turns']=[body.obs(a,p['head'])for p in g['query']];row['B_memories']=[body.obs(a,body.xyz(a,g['B'],v))for v in[(-1,1,1),(1,1,1)]]
            frames.append(row)
        contact=next(f for f in frames if f['tick']==crit-15)['contacts'];useful=[];failed=[]
        for r in(-1,1):
            v=contact[str(r)]
            if v['state']>0 and v['semantic']==1:
                if r==plan['availability'] and v['direction']==[r,-1,-1]:useful.append(r)
                if r!=plan['availability'] and v['direction']==[r,-1,0]:failed.append(r)
        q=contact['0'];query=bool(q['state']>0 and q['semantic']==1 and q['direction']==[0,-1,-1])
        rows.append({'index':s['index'],'critical_tick':crit,'availability':plan['availability'],'useful_material_actions':useful,'failed_material_actions':failed,'query_material':query,'conflict':bool(useful and failed),'no_motor_output':not useful and not failed,'frames':frames});s['index']+=1
    put(a,s);view=body.get(a);view['index']=s['index'];body.put(a,view)
    return{'plans':plans,'mode':mode,'requests':body.receipts(a,requests),'rows':rows,'final':state(a),'attribution':'Only exogenous availability selects environmental contact conditions. Actual native consequence updates local fields; all query, B response and A combination occur through the shared Runtime. Metrics do not feed any action or memory update.'}
