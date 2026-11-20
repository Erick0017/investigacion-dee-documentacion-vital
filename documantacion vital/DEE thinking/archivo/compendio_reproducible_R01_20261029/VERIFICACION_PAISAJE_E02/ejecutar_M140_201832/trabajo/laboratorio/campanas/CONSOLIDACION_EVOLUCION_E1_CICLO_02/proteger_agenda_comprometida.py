"""Domain check on the actual historical191-pending body, not the pre-arm
state with identical RAW. Keep its complete agenda and compare same inputs.
"""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from comun import *
from capacidades import integracion_situada_01 as ic
from capacidades.integracion_situada_01 import delayed_social as social,social_guard,ic_native_core as core,ic_body
s=Store();h='fa46e6cfec7516ed799723a6bc4edc71869bb6f80780bf78059f1b416936a512'
source=next(p for p in(s.root/'estado/checkpoints').glob('E1_INTEGRADO_MAIN.T3312.*')if digest_file(p)==h)
CASES=[('C02_COMMIT_340_PROTEGIDO',45,'protect'),('C02_COMMIT_341_SHAM',45,'sham'),
       ('C02_COMMIT_342_SIN_RECORD',45,'none'),('C02_COMMIT_343_OPUESTO',18,'protect')]
atomic_json(EV/'AGENDA_COMPROMETIDA_PROTOCOLO_340.json',{'source':str(source.relative_to(s.root)),'sha256':h,'initial_pending':191,'cases':CASES,
 'source_distinction':'This is IC01MAIN_COMMITTED_BODY38, not the pre-arm0658state used by isolatedC2DIV cases. Equal RAW/clocks do NOT imply equal future causal agenda.',
 'controlled':'Same current body plan, all191pending inputs kept. New private B comparison, delayed native recording/retrieval, both record5 challenged except explicitno-recordcontrol. Protection2zero or equal-dose off-route.',
 'observations':'Known body-end boundaries respected through the owner, then explicit native continuation. Score ports at3420+67k, not global samples3899/4435.',
 'horizon':[3899,4435],'stop':'If occupied>100000 at3899, preserve and omit longer exposure. Not a declaration of death.',
 'criterion':'Actual private B source and received sign under committed body; diagnose separately body activity, legacy interface interference and global occupation. No new global guarantee from isolated-route success.'})
for name,value,mode in CASES:
    fork('E1_INTEGRADO_MAIN',name,checkpoint=str(source.relative_to(s.root)))
    def test(a):
        initial=physical(a.world,occupation=True);body_start=ic_body.report(a);p=social.begin(a,name=name,value=value,mode='full');rr=[]
        guard=social_guard.divert_record(a,name=name,record_tick=3362,sham=mode=='sham')if mode!='none'else None
        if mode!='none':
            for label in('minus','plus'):
                port='back.'+label+'.record';r=a.world.submit(port,5,3362);rr.append({'id':int(r.id),'port':port,'payload':5,'tick':3362})
        frames=[]
        def advance(t):
            b=ic_body.get(a)
            if b and a.tick<b['end_tick']<t:ic.advance(a,until=b['end_tick'],record=False)
            ic.advance(a,until=t,record=False)
        times=sorted(set([3362,3363,3364]+[3420+67*k for k in range(7)]+[3899]))
        for t in times:
            advance(t);frames.append({'tick':t,'B':observe(a.world,p['B']),
              'ports':[{'sign':b['sign'],'read':observe(a.world,b['target'])}for b in p['banks']],
              'body':ic_body.report(a),'global':physical(a.world,occupation=True)})
            if t in(3363,3899):a.save(EV/(name+'.T'+str(t)+'.deetsnap.gz'))
        if frames[-1]['global']['occupied']<100000:
            for t in(4033,4090,4167,4301,4425,4435):
                advance(t);frames.append({'tick':t,'ports':[{'sign':b['sign'],'read':observe(a.world,b['target'])}for b in p['banks']],
                   'body':ic_body.report(a),'global':physical(a.world,occupation=True)})
        return{'initial':initial,'body_initial':body_start,'private_value':value,'mode':mode,'frames':frames,
               'record_requests':core.receipts(a,rr),'protection_requests':core.receipts(a,guard['requests'])if guard else[],
               'social_requests':core.receipts(a,social.get(a)['plan']['requests']),'body_final':ic_body.report(a),'final':physical(a.world,occupation=True),
               'scope':'Matched historical committed agenda; not a new T0 training or an independent learner. Received private code and global deterioration scored separately.'}
    run(name,name,test,{'spec':'AGENDA_COMPROMETIDA_PROTOCOLO_340.json'})
