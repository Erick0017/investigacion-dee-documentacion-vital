"""Specific P0 native reorientation of an already acquired inaccessible
contribution. No field edit, old code, teacher or answer is supplied.
"""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from comun import *
from capacidades import integracion_situada_01 as ic
from capacidades.integracion_situada_01 import ic_native_core as core,delayed_social as social,social_guard,lateral_social,regression
s=Store();i=json.loads((EV/'C02_LATOP_306_USO.json').read_text(encoding='utf8'))['result']['INSTRUMENTO']
source=next(p for p in(s.root/'estado/checkpoints').glob('E1_CICLO02_LATERAL_LOCAL_01.T21108.*')if digest_file(p)==i['snapshot_sha256'])
CASES=[('C02_SEPARA_330_DOS_PULSOS','paired'),('C02_SEPARA_331_SHAM','sham'),('C02_SEPARA_332_SOLO_ELEVAR','lift_only')]
atomic_json(EV/'SEPARACION_SOPORTES_PROTOCOLO_330.json',{'source':str(source.relative_to(s.root)),'source_sha256':digest_file(source),'cases':CASES,
 'causal_basis':'Observed -X-Z7 at[31,59,26] T21108 becomes-X7 at[28,59,23] T21111, then coalesces with+X7 into direction0load14 atT21118. Same loss without new entries. Antecedent before21108 not assigned from equal loads alone.',
 'intervention':'Fixed zero Z+ meets the negative candidate at[27,59,23] T21112; fixed zero Z- meets its predicted deflected route at[24,59,26] T21115. No new decoder: existing fixed negative-z26 port retained.',
 'controls':'Same2zero inputs19y off-route; only first zero pulse. Prior full334/315 trajectory supplies no-new-intervention reference. Admission failures are not successful interventions.',
 'frozen_criteria':'Old+at23 and old-negative at26 become separately qualified in three actual later uses, while lateral new+atY48 remains. Then one new private52, one gate experience and old functions, all in the same branch. Native old code, not action utility under saturated actuator, is primary outcome.',
 'planned_cut':'A complete operational checkpoint after the three uses is preserved BEFORE adding the private52 experience, regardless of its result. Future adverse state is never erased.',
 'classification':'Researcher-prepared native P0 redirection, not autonomous failure detection, P2/R2 or reconstruction after complete causal convergence.'})
for name,mode in CASES:
    fork('E1_CICLO02_LATERAL_LOCAL_01',name,checkpoint=str(source.relative_to(s.root)))
    def test(a):
        initial=physical(a.world,occupation=True);rr=[];layout=[]
        for index,(target,v,t)in enumerate((([27,59,23],[0,0,1],21112),([24,59,26],[0,0,-1],21115))):
            if index==1 and mode=='lift_only':continue
            target=core.move(target,(0,1,0),19)if mode=='sham'else target
            r=core.arrive(a,name+'.redirect.'+str(index),target,v,t,0);rr.append(r);layout.append({'site':target,'direction':v,'tick':t,'request':r})
        frames=[]
        for t in(21110,21111,21112,21113,21114,21115,21117,21118,21120):
            ic.advance(a,until=t,record=False)
            frames.append({'tick':t,'old_positive_tube':observe(a.world,[(11+t-21108)%67,59,23]),
                'old_negative_unredirected_tube':observe(a.world,[(31-t+21108)%67,59,23]),
                'predicted_lifted':observe(a.world,[(31-t+21108)%67,59,23+min(max(t-21112,0),3)]),
                'global':physical(a.world,occupation=True)})
            if t in(21111,21112,21114,21115,21118):a.save(EV/(name+'.T'+str(t)+'.deetsnap.gz'))
        uses=ic.act_external(a,steps=3);cut=EV/(name+'.CORTE_ANTES_NUEVA_EXPERIENCIA.T'+str(a.tick)+'.deetsnap.gz');a.save(cut)
        p=social.begin(a,name=name+'_NEXT',value=52,mode='full');lat=lateral_social.prepare(a,name=name+'_NEXT');guard=social_guard.divert_record(a,name=name+'_NEXT',record_tick=p['source_tick']-1);records=[]
        for label in('minus','plus'):
            port='back.'+label+'.record';r=a.world.submit(port,5,p['source_tick']-1);records.append({'id':int(r.id),'port':port,'payload':5,'tick':p['source_tick']-1})
        ic.advance(a,until=p['end_tick'],record=False);new_use=ic.act_external(a,steps=1)
        gate=ic.experience(a,kind='puerta',options={'forces':[85,100],'wear':[1,1]});last=ic.act_external(a,steps=1)
        h=ic.attach(a,record=False)
        try:panel=regression.inherited_panel(a,social=False)
        finally:h['detach']()
        return{'initial':initial,'mode':mode,'layout':layout,'requests':core.receipts(a,rr),'frames':frames,'first_uses':uses,
               'planned_cut':{'path':str(cut.relative_to(ROOT)),'sha256':digest_file(cut),'tick':21309},
               'new_private_plan':p,'new_lateral':lat,'new_record_requests':core.receipts(a,records),'new_protection_requests':core.receipts(a,guard['requests']),
               'new_use':new_use,'gate':gate,'last_use':last,'old_panel':panel,'final':physical(a.world,occupation=True),
               'classification':'P0 reorientation. Codes/signs come only from reached physical state. Prepared interception before loss is not autonomous recovery.'}
    run(name,name,test,{'spec':'SEPARACION_SOPORTES_PROTOCOLO_330.json'})
