import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from comun import *
from capacidades import integracion_situada_01 as ic
from capacidades.integracion_situada_01 import ic_native_core as core,delayed_social as social,social_guard
s=Store();expected='0658add9835a1c5b8f7a0d99b64153a54658f014a7c991921a499c2f9b608216'
source=next(p for p in(s.root/'estado/checkpoints').glob('E1_INTEGRADO_MAIN.T3312.*')if digest_file(p)==expected)
cases=[('C02_DIV_080_MINUS',45,False,False),('C02_DIV_081_PLUS',18,False,False),
       ('C02_DIV_082_SHAM',45,True,False),('C02_DIV_083_TERMINAL',45,False,True)]
atomic_json(EV/'PROTECCION_SOCIAL_PROTOCOLO_R3.json',{'source':expected,'cases':cases,'record_tick':3362,'record_load':5,'counterflow':'Zero-load Z- at one-step Y transit, both banks, fixed before outputs',
    'diagnosis_R2':'Permanent occupancy guarded admission but spoiled B communication. These controls keep admission and move only the two record-cue trajectories.',
    'criterion':'Private B source sign, both delayed received signs and later native use must survive, not just lower occupancy.',
    'horizons':[3899,4435],'variant_terminal':'Optional two prepared native far absorbers; compare with diversion alone rather than assume every circulating resource is harmful.'})
for name,value,sham,terminate in cases:
    fork('E1_INTEGRADO_MAIN',name,checkpoint=str(source.relative_to(s.root)))
    def test(a):
        initial=physical(a.world,occupation=True);guard=social_guard.divert_record(a,name=name,record_tick=3362,sham=sham,terminate=terminate)
        p=social.begin(a,name=name,value=value,mode='full');assert p['source_tick']==3363
        rr=[]
        for label in('minus','plus'):
            port='back.'+label+'.record';r=a.world.submit(port,5,3362);rr.append({'id':int(r.id),'port':port,'tick':3362,'payload':5})
        frames=[];samples=[];times=sorted(set(list(range(3359,3368))+[3420,3500,3600,3710,3743,3899]+[3420+67*i for i in range(1,7)]))
        for t in times:
            ic.advance(a,until=t,record=False);samples.append(physical(a.world,occupation=True))
            frames.append({'tick':t,'B':observe(a.world,p['B']),'ports':[{'sign':b['sign'],'read':observe(a.world,b['target'])}for b in p['banks']],
                'deflection':[{'bank':b['bank'],'meeting':observe(a.world,b['meeting']),
                    'context':[observe(a.world,core.move(b['meeting'],(x,y,z)))for x in(-2,-1,0,1,2)for y in(-2,-1,0,1,2)for z in(-2,-1,0,1,2)]if t in(3362,3363,3364)else[]}for b in guard['layout']]if t<3370 else[]})
            if t in(3362,3363):a.save(EV/(name+'.T'+str(t)+'.deetsnap.gz'))
        a.save(EV/(name+'.T3899.deetsnap.gz'))
        if samples[-1]['occupied']<20000:
            for t in(4033,4090,4167,4301,4425,4435):
                ic.advance(a,until=t,record=False);samples.append(physical(a.world,occupation=True));frames.append({'tick':t,'ports':[{'sign':b['sign'],'read':observe(a.world,b['target'])}for b in p['banks']]})
        return{'initial':initial,'guard':guard,'private_value':value,'legacy_record_requests':core.receipts(a,rr),'protection_requests':core.receipts(a,guard['requests']),
               'social_requests':core.receipts(a,social.get(a)['plan']['requests']),'samples':samples,'frames':frames,'final':physical(a.world,occupation=True)}
    run(name,name,test,{'spec':'PROTECCION_SOCIAL_PROTOCOLO_R3.json'})
