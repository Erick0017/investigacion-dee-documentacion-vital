"""Finite question: does an experienced loss select another physical support
under the SAME all-support query, and do generic resources suffice twice?
No learned-policy claim; this is P0 opportunity and possible P1 use.
"""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from comun import *
from capacidades import integracion_situada_01 as ic
from capacidades.integracion_situada_01 import recovery,ic_native_core as core,ic_external as external
OLD=ROOT/'evidencia/campanas/INTEGRACION_COGNITIVA_SITUADA_E1_01'
no=json.loads((OLD/'INTEGRATED_NO_B_134.json').read_text(encoding='utf8'))['final_record']
CASES=[('C02_REPET_190_DOS_CAPAS','E1_INTEGRADO_CONTINUABLE_01',None,2,False),
       ('C02_REPET_191_UNA_CAPA','E1_INTEGRADO_CONTINUABLE_01',None,1,False),
       ('C02_REPET_192_SIN_PERDIDA_PREVIA','E1_INTEGRADO_CONTINUABLE_01',None,2,True),
       ('C02_REPET_193_SIN_CONTENIDO','IC01_INTEGRATED_NO_B_134',no['snapshot'],2,False)]
atomic_json(EV/'ACCESO_REPETIDO_PROTOCOLO_190.json',{'cases':CASES,
 'question':'Two experienced losses, with identical all-support final query. Does the first loss improve future access, merely relocate it, or consume the prepared opportunity?',
 'prepared':'One or two zero-resource planes, ALL6parallel ports and BOTH-sign probes fixed before the first loss. No loss detector or host response-dependent selection.',
 'query_schedule':'First fixed anchor+134, second anchor+268. First sham19y for192. Second query identical on original and fallback supports for all arms.',
 'primary_outcome':'Pure-X acquired sign at any predeclared fixed support after each encounter; later actual4externaluses. Missing output and rejection retained.',
 'not_P2':'A native relocation caused by a past loss is not by itself learned choice of recovery policy. Query initiative remains prepared.',
 'no_content_control':'Existing no-B historical life at5698; matched relative phases, NOT age-matched with the16485 positive cohort.'})
for name,parent,checkpoint,layers,first_sham in CASES:
    fork(parent,name,checkpoint=checkpoint)
    def test(a):
        initial=physical(a.world,occupation=True);p=recovery.preposition_social_access(a,name=name)
        banks=p['base_banks'];bridge=external.saved(a);rr=list(p['requests']);q1=p['anchor_tick']+134;q2=q1+134
        for b in banks:
            alt={**b,'target':core.move(b['target'],(0,0,-1),6),'access':'second_prepared_fallback_not_learned_policy'}
            bridge['social_ports'].append(alt)
            if layers==2:
                launch=core.move(next(z['zero_launch_site']for z in p['layout']if z['bank']==b['sign']),(0,0,-1),3)
                rr.append(core.submit(a,name+'.layer2.'+str(b['sign']),launch,(0,0,1),p['anchor_tick']-30,0))
        bridge['two_episode_prepared_access']={'queries':[q1,q2],'layers':layers,'first_query_sham':first_sham,'fixed_before_first_response':True}
        external.store(a,bridge)
        # Commit all query resources before any answer. Both geometric supports
        # receive the same probe, regardless of what the earlier query did.
        for index,when in enumerate((q1,q2)):
            for b in banks:
                for offset in(0,3):
                    site=core.move(b['target'],(0,0,-1),offset)
                    if index==0 and first_sham:site=core.move(site,(0,1,0),19)
                    rr.append(core.arrive(a,name+'.query.'+str(index)+'.'+str(b['sign'])+'.'+str(offset),site,(0,0,-1),when,0))
        frames=[]
        times=sorted(set([q1-1,q1,q1+1,q1+2,q1+3,q1+67,q2-1,q2,q2+1,q2+2,q2+3]))
        for t in times:
            ic.advance(a,until=t,record=False)
            frames.append({'tick':t,'ports':[{'bank':b['sign'],'zoffset':off,'read':observe(a.world,core.move(b['target'],(0,0,-1),off))}for b in banks for off in(0,3,6)],
                           'global':physical(a.world,occupation=True)})
            if t in(q1-1,q1+3,q2+3):a.save(EV/(name+'.T'+str(t)+'.deetsnap.gz'))
        uses=ic.act_external(a,steps=4)
        return{'initial':initial,'preparation':p,'layers':layers,'first_sham':first_sham,'query_ticks':[q1,q2],
               'frames':frames,'requests':core.receipts(a,rr),'external':uses,'final':physical(a.world,occupation=True),
               'classification':'P0/P1 candidate, never P2 merely for resource consumption or prepared multi-support query.'}
    run(name,name,test,{'spec':'ACCESO_REPETIDO_PROTOCOLO_190.json'})
