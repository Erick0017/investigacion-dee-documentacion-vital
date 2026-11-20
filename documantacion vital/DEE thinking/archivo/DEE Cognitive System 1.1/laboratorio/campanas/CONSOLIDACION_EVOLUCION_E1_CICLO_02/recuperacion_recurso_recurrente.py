"""Un recurso cero preparado antes de la pérdida; ninguna decisión si-falla."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from comun import *
from capacidades import integracion_situada_01 as ic
from capacidades.integracion_situada_01 import ic_native_core as core,delayed_social as social

CASES=[('C02_REC_030_RECURSO',True,False,True),
       ('C02_REC_031_SIN_RECURSO',False,False,True),
       ('C02_REC_032_SHAM',True,True,True),
       ('C02_REC_033_SIN_PERDIDA',True,False,False)]
atomic_json(EV/'RECUPERACION_PROTOCOLO_PREVIO_R1.json',{
    'parent':'E1_INTEGRADO_CONTINUABLE_01:T16485','cases':CASES,
    'hypothesis':'A generic zero-load carrier installed well before loss could recur natively and meet a history-transformed content carrier, with no host loss detector or recovery command.',
    'classification_limit':'Prepared opportunities remain P0. Different native utilization depending on a loss history is at most local P1; this protocol alone cannot establish a learned failure strategy or general R2.',
    'decoder':'Fixed both signs at original z29 and alternative z26, state1 semantic1, pureX load7 only; no expected sign read during experiment.'})
for name,resource,sham,loss in CASES:
    fork('E1_INTEGRADO_CONTINUABLE_01',name)
    def test(a):
        initial=physical(a.world,occupation=True)
        if loss:p=social.begin(a,name=name,value=18,mode='no_partner')
        else:
            # Pure schedule arithmetic and existing geometry, no prepare() call:
            # that routine itself submits matter and is NOT a passive planner.
            from copy import deepcopy
            T=147+67*max(0,(a.tick+10-142+66)//67)
            p={'end_tick':T+57,'banks':deepcopy(social.get(a)['plan']['banks']),
               'source_tick':T,'mode':'NO_GENERIC_QUERY_CONTROL','requests':[]}
        end=p['end_tick'];rr=[];targets=[]
        for b in p['banks']:
            target=core.move(b['target'],(b['sign'],0,-1),3)
            launch=end-30
            site=core.move(target,(0,0,1),-33)
            if sham:site=core.move(site,(0,1,0),19)
            if resource:rr.append(core.submit(a,name+'.preexisting_zero.'+str(b['sign']),site,(0,0,1),launch,0))
            targets.append({'sign':b['sign'],'original':b['target'],'alternative':core.move(b['target'],(0,0,-1),3),'meeting':target,'zero_launch':launch,'zero_site':site})
        frames=[]
        for t in sorted(set([a.tick+1,end-31,end-30,end-1,end,end+1,end+2,end+3,end+4,end+5,end+67,end+134,end+201,end+268])):
            ic.advance(a,until=t,record=False)
            frames.append({'tick':t,'regions':[{'sign':b['sign'],'original':observe(a.world,b['original']),'alternative':observe(a.world,b['alternative']),'meeting':observe(a.world,b['meeting']),
                'moving_old':observe(a.world,core.move(b['original'],(b['sign'],0,-1),max(0,t-end))),
                'context':[observe(a.world,core.move(b['meeting'],(x,y,z)))for x in(-1,0,1)for y in(-1,0,1)for z in(-1,0,1)]if end-1<=t<=end+5 else[]}for b in targets],
                'global':physical(a.world,occupation=True)if t in(end-1,end+3,end+268)else None})
            if t in(end-1,end+3):a.save(EV/(name+'.T'+str(t)+'.deetsnap.gz'))
        return{'initial':initial,'plan':p,'preexisting_resources':core.receipts(a,rr),'frames':frames,'fixed_ports':targets,'final':physical(a.world,occupation=True),'no_recovery_call_after_loss':True,'classification':'Prepared finite zero resource, no acquired detection claimed.'}
    run(name,name,test,{'spec':'RECUPERACION_PROTOCOLO_PREVIO_R1.json'})
