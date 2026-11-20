"""One bounded correction: two remote native SEM4 supports on the predicted
resource-only YZ rays, not on B, its admission sites or either actual XYZ ray.
Same-dose off-ray controls. No deletion and no learned regulation claim.
"""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from comun import *
from social_lateral import lateral
from capacidades import integracion_situada_01 as ic
from capacidades.integracion_situada_01 import delayed_social as social,social_guard,ic_native_core as core,regression
CASES=[('C02_LATERAL_280_SOPORTE',False),('C02_LATERAL_281_SHAM_SOPORTE',True)]
VALUES=[20,52,12,60]
atomic_json(EV/'SOCIAL_LATERAL_PROTOCOLO_R2_280.json',{'parent':'E1_CICLO02_CORTE_VALIDADO_20927','cases':CASES,'private_values':VALUES,
 'diagnosis':'Lateral R1 retains two separate+codes on first use, then loses later uses and expands near the fourth exposure; off-route encoding control remains low occupation. No universal memory/space conclusion.',
 'bounded_correction':'Once before first query, two stationary SEM4zero supports sixY/Z steps from B births. Actual XYZ messages differ in X by6 at this stage; both signs receive same opportunity. Keep sinks or19y off-ray sham. Admission and all functions must be verified, never inferred from low occupancy.',
 'criterion':'Old+at23 AND actual new private sign at lateralY48 survive, including opposite signs, while old comparisons and gate use remain. Stop at the fixed four-episode horizon; preserve adverse reached states.',
 'attribution':'Prepared remote native absorption P0, not acquired filtering, clearing from Python, energy regulation or host-selected packet removal.'})
for name,sham in CASES:
    fork('E1_CICLO02_CORTE_VALIDADO_20927',name)
    def test(a):
        initial=physical(a.world,occupation=True);episodes=[];all_rr=[];sinks=[]
        for i,value in enumerate(VALUES):
            p=social.begin(a,name=name+'_'+str(i),value=value,mode='full');l=lateral(a,p,name+'_'+str(i),False)
            guard=social_guard.divert_record(a,name=name+'_'+str(i),record_tick=p['source_tick']-1);all_rr.extend(l['requests']+guard['requests'])
            if i==0:
                for b in p['banks']:
                    target=core.move(b['birth'],(0,1,1),6)
                    if sham:target=core.move(target,(0,1,0),19)
                    pre=observe(a.world,target);r=core.submit(a,name+'.native_sink.'+str(b['sign']),target,(0,0,0),p['source_tick']+4,0,4)
                    sinks.append({'bank':b['sign'],'site':target,'pre':pre,'request':r});all_rr.append(r)
            record=[]
            for label in('minus','plus'):
                port='back.'+label+'.record';r=a.world.submit(port,5,p['source_tick']-1);q={'id':int(r.id),'port':port,'payload':5,'tick':p['source_tick']-1};record.append(q);all_rr.append(q)
            frames=[]
            for t in(p['source_tick'],p['source_tick']+1,p['source_tick']+6,p['source_tick']+7,p['end_tick']):
                ic.advance(a,until=t,record=False)
                frames.append({'tick':t,'B':observe(a.world,p['B']),'old_expected':observe(a.world,[(11+t-20572)%67,59,23]),
                    'lateral_ports':[{'bank':b['sign'],'read':observe(a.world,b['target'])}for b in l['banks']],
                    'sinks':[observe(a.world,q['site'])for q in sinks]})
                if i in(0,3)and t in(p['source_tick']+6,p['source_tick']+7):a.save(EV/(name+'.EP'+str(i)+'.T'+str(t)+'.deetsnap.gz'))
            use=ic.act_external(a,steps=1);a.save(EV/(name+'.EP'+str(i)+'.USO_T'+str(a.tick)+'.deetsnap.gz'))
            episodes.append({'index':i,'private_object':value,'plan':p,'lateral':l,'frames':frames,'use':use,
                             'record_requests':core.receipts(a,record),'after':physical(a.world,occupation=True)})
        h=ic.attach(a,record=False)
        try:panel=regression.inherited_panel(a,social=False)
        finally:h['detach']()
        gate=ic.experience(a,kind='puerta',options={'forces':[85,100],'wear':[5,5]});last=ic.act_external(a,steps=1)
        return{'initial':initial,'sham':sham,'sinks':sinks,'sink_receipts':core.receipts(a,[q['request']for q in sinks]),'episodes':episodes,
               'requests':core.receipts(a,all_rr),'old_panel':panel,'gate':gate,'final_use':last,'final':physical(a.world,occupation=True),
               'scope':'Only effects supported by actual old/new contents and actual admission; no inference from occupation alone.'}
    run(name,name,test,{'spec':'SOCIAL_LATERAL_PROTOCOLO_R2_280.json'})
