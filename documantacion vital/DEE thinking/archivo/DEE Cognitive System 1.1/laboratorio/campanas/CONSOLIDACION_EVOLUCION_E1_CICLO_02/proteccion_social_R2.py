import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from comun import *
from capacidades import integracion_situada_01 as ic
from capacidades.integracion_situada_01 import ic_native_core as core,delayed_social as social,social_guard
s=Store();expected='0658add9835a1c5b8f7a0d99b64153a54658f014a7c991921a499c2f9b608216'
source=next(p for p in(s.root/'estado/checkpoints').glob('E1_INTEGRADO_MAIN.T3312.*')if digest_file(p)==expected)
cases=[('C02_GUARD_070_MINUS',45,False),('C02_GUARD_071_PLUS',18,False),('C02_GUARD_072_SHAM',45,True),('C02_GUARD_073_SIN_B',None,False)]
atomic_json(EV/'PROTECCION_SOCIAL_PROTOCOLO_R2.json',{'source':expected,'cases':cases,'record_requests':{'ports':['back.minus.record','back.plus.record'],'tick':3362,'payload_each':5},
    'horizon':4435,'criterion':'Both acquired signs remain readable past historical flood; native engine rejects protected legacy record doses without a host filter. Sham receives the same two prepared SEM4 zero supports elsewhere.',
    'loss_of_interface_declared':'Old record ports become unavailable, not all communication. Delayed native B-E1 channel must still work, with no-B control.',
    'not_learned_attention':True})
for name,value,sham in cases:
    fork('E1_INTEGRADO_MAIN',name,checkpoint=str(source.relative_to(s.root)))
    def test(a):
        initial=physical(a.world,occupation=True);h=ic.attach(a,record=False)
        try:guard=social_guard.install(a,name=name,sham=sham)
        finally:h['detach']()
        p=social.begin(a,name=name,value=18 if value is None else value,mode='no_partner'if value is None else'full');assert p['source_tick']==3363
        rr=[]
        for label in('minus','plus'):
            port='back.'+label+'.record';r=a.world.submit(port,5,3362);rr.append({'id':int(r.id),'port':port,'tick':3362,'payload':5})
        frames=[];samples=[];times=sorted(set([3362,3363,3364,3365,3420,3500,3600,3710,3743,3899]+[3420+67*i for i in range(1,7)]))
        for t in times:
            ic.advance(a,until=t,record=False);samples.append(physical(a.world,occupation=True));frames.append({'tick':t,'B':observe(a.world,p['B']),'ports':[{'sign':b['sign'],'read':observe(a.world,b['target'])}for b in p['banks']]})
        a.save(EV/(name+'.T3899.deetsnap.gz'))
        if samples[-1]['occupied']<20000:
            for t in(4033,4090,4167,4301,4425,4435):
                ic.advance(a,until=t,record=False);samples.append(physical(a.world,occupation=True));frames.append({'tick':t,'ports':[{'sign':b['sign'],'read':observe(a.world,b['target'])}for b in p['banks']]})
        return{'initial':initial,'guard':guard,'social_plan':p,'legacy_record_requests':core.receipts(a,rr),'social_requests':core.receipts(a,social.get(a)['plan']['requests']),
               'samples':samples,'frames':frames,'final':physical(a.world,occupation=True),'scope':'Prepared protected alternative channel; do not claim old record learning survived or that E1 learned to protect itself.'}
    run(name,name,test,{'spec':'PROTECCION_SOCIAL_PROTOCOLO_R2.json'})
