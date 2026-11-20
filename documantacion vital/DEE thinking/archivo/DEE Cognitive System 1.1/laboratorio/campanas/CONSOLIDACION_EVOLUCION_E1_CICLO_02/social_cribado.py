"""Variantes fijadas de dosis/fase/ruta, mismo padre y oportunidades nativas."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from comun import *
from capacidades import integracion_situada_01 as ic
from capacidades.integracion_situada_01 import ic_native_core as core,delayed_social as social

s=Store()
expected='0658add9835a1c5b8f7a0d99b64153a54658f014a7c991921a499c2f9b608216'
source=next(p for p in(s.root/'estado/checkpoints').glob('E1_INTEGRADO_MAIN.T3312.*')if digest_file(p)==expected)
cases=[('C02_SOCIAL_010_Y0',45,'legacy',0,0),
       ('C02_SOCIAL_011_FASE1',45,'legacy',5,1),
       ('C02_SOCIAL_012_RUTA_MINUS',45,'delayed',0,0),
       ('C02_SOCIAL_013_RUTA_PLUS',18,'delayed',0,0),
       ('C02_SOCIAL_014_RUTA_SIN_B',None,'delayed',0,0)]
atomic_json(EV/'SOCIAL_PROTOCOLO_PREVIO_R1.json',{'source':expected,'cases':cases,
    'historical_comparison_not_repeated':['IC01_SOCIAL_SOURCE_RECORD_80','IC01_RECORD_ONLY_NO_B_94','IC01_RECORD_ONLY_SHAM_95'],
    'initial_horizon':3899,'later_horizon_for_survivors':4435,
    'criterion':'Native content must reach a fixed E1 reader, remain usable at multiple later67tick opportunities, and avoid historical mass expansion through the historical failure horizon. Record output/occupancy separately.',
    'assistance':'Dose/phase/new fixed spatial routes are designer variants. No acquired avoidance or general repair claim.'})

for name,value,route,dose,shift in cases:
    life=name
    fork('E1_INTEGRADO_MAIN',life,checkpoint=str(source.relative_to(s.root)))
    def test(a):
        initial=physical(a.world,occupation=True);T=3363;rr=[]
        if route=='delayed':
            p=social.begin(a,name=name,value=18 if value is None else value,mode='no_partner'if value is None else'full')
            assert p['source_tick']==T
            banks=p['banks'];end=p['end_tick']
        else:
            if value is not None:
                for port,payload,t in [('B.quantity.object.cue',5,T-5),('B.quantity.object.resource',value,T-5),('B.quantity.reader',7,T-1)]:
                    r=(a.world.probe if port.endswith('reader')else a.world.submit)(port,payload,t);rr.append({'id':int(r.id),'port':port,'payload':payload,'tick':t})
            banks=a.geometry['cpc9_return']['banks'];end=T+78
            for b in banks:
                for role,payload,t in [('record',dose,T-1+shift),('read',7,T+66),('use',13,T+71)]:
                    port='back.'+b['id']+'.'+role;r=(a.world.probe if role=='read'else a.world.submit)(port,payload,t);rr.append({'id':int(r.id),'port':port,'payload':payload,'tick':t})
        frames=[];samples=[]
        times=sorted(set([T-1,T,T+1,T+2,T+3,end-1,end]+[end+67*i for i in range(1,7)]+[3500,3600,3660,3710,3743,3899]))
        for t in times:
            if t<a.tick:continue
            info=ic.advance(a,until=t,record=False)
            samples.append(physical(a.world,occupation=True))
            if route=='delayed':reads=[{'sign':b['sign'],'site':b['target'],'read':observe(a.world,b['target'])}for b in banks]
            else:reads=[{'sign':b['sign'],'hub':observe(a.world,b['hub']),'delivery':observe(a.world,b['delivery_site'])}for b in banks]
            frames.append({'tick':t,'B':observe(a.world,a.transferred_quantity.geometry['center']),'reads':reads})
        a.save(EV/(name+'.T3899.deetsnap.gz'))
        if samples[-1]['occupied']<20000:
            for t in(4033,4167,4301,4435):
                ic.advance(a,until=t,record=False);samples.append(physical(a.world,occupation=True));frames.append({'tick':t,'reads':[{'sign':b['sign'],'read':observe(a.world,b['target']if route=='delayed'else b['delivery_site'])}for b in banks]})
        return{'variant':{'route':route,'record_dose':dose,'record_shift':shift,'private_B_value':value},'initial':initial,'samples':samples,'frames':frames,'requests':core.receipts(a,rr if route!='delayed'else social.get(a)['plan']['requests']),'plan':social.get(a)if route=='delayed'else banks,'final':physical(a.world,occupation=True),'full_witness_3899':str(EV/(name+'.T3899.deetsnap.gz'))}
    run(life,name,test,{'frozen_spec':'SOCIAL_PROTOCOLO_PREVIO_R1.json'})
