import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from comun import *
from desvio_mensaje_social import divert_message,shunt_turn_ghosts
from capacidades import integracion_situada_01 as ic
from capacidades.integracion_situada_01 import delayed_social as social,social_guard,ic_native_core as core,regression
s=Store();src_h=json.loads((EV/'C02_MAIN_171_RECORD_plus.json').read_text(encoding='utf8'))['result']['INSTRUMENTO']['snapshot_sha256']
source=next(p for p in(s.root/'estado/checkpoints').glob('E1_CICLO02_MAIN.T20927.*')if digest_file(p)==src_h)
CASES=[('C02_DETOUR_240_FANTASMA',(40,48,56),False),('C02_DETOUR_241_SHAM_FANTASMA',(40,48,56),True),
       ('C02_DETOUR_242_EXCURSION9',(38,47,56),False)]
VALUES=[20,52,12,60]
atomic_json(EV/'DESVIO_MENSAJE_PROTOCOLO_R2_240.json',{'cases':CASES,'private_values':VALUES,'source_sha256':src_h,
 'R1_result':'Real detour preserves two+7 contents after first update, but both old and new social uses fail after the opposite update. Sham preserves new content but coalesces old. Do not promote as globally superior.',
 'hypothesis':'Zero turn opportunities on the absent message branch produce a ghost that can be harmful. Compare a fixed native downstream diversion with same-dose off-route sham; no host checks which branch carries an answer.',
 'variants':'Only one ghost intervention and one identified excursion revision, not an unbounded geometry search.',
 'reserve':'Third/fourth private values12/60, opposite ordering, fixed before responses. Same phase/reader, no recovery reinsertion.',
 'criteria':'Independent old+7 atz23 AND actual current private sign atz29, later native use, old comparisons and useful gate actions. Resources/admissions and counterexamples remain in denominators.'})
for name,offsets,ghost_sham in CASES:
    fork('E1_CICLO02_MAIN',name,checkpoint=str(source.relative_to(s.root)))
    def test(a):
        initial=physical(a.world,occupation=True);episodes=[];all_requests=[]
        for i,value in enumerate(VALUES):
            p=social.get(a)['plan']if i==0 else social.begin(a,name=name+'_'+str(i),value=value,mode='full')
            if i>0:
                guard=social_guard.divert_record(a,name=name+'_'+str(i),record_tick=p['source_tick']-1);all_requests.extend(guard['requests'])
                for label in('minus','plus'):
                    port='back.'+label+'.record';r=a.world.submit(port,5,p['source_tick']-1);all_requests.append({'id':int(r.id),'port':port,'payload':5,'tick':p['source_tick']-1})
            detour=divert_message(a,p,name+'_'+str(i),False,offsets);shunt=shunt_turn_ghosts(a,detour,name+'_'+str(i),ghost_sham)
            all_requests.extend(detour['requests']+shunt['requests']);frames=[]
            for t in sorted({p['source_tick']+40,p['source_tick']+48,p['source_tick']+51,p['end_tick']}):
                ic.advance(a,until=t,record=False);site=[(11+t-20572)%67,59,23]
                frames.append({'tick':t,'old_expected':observe(a.world,site),'B':observe(a.world,p['B']),
                               'new_ports':[{'bank':b['sign'],'read':observe(a.world,b['target'])}for b in p['banks']]})
            use=ic.act_external(a,steps=1);a.save(EV/(name+'.EP'+str(i)+'.T'+str(a.tick)+'.deetsnap.gz'))
            episodes.append({'index':i,'private_object':value,'plan':p,'detour':detour,'ghost_diversion':shunt,'frames':frames,'use':use,
                             'after':physical(a.world,occupation=True)})
            if episodes[-1]['after']['occupied']>100000:break
        h=ic.attach(a,record=False)
        try:panel=regression.inherited_panel(a,social=False)
        finally:h['detach']()
        gate=ic.experience(a,kind='puerta',options={'forces':[85,100],'wear':[5,5]});use=ic.act_external(a,steps=1)
        return{'initial':initial,'offsets':list(offsets),'ghost_sham':ghost_sham,'episodes':episodes,'requests':core.receipts(a,all_requests),
          'old_panel':panel,'gate':gate,'final_use':use,'final':physical(a.world,occupation=True),'not_claimed':'No learned protection, P2 access initiation or global promotion from one local gain.'}
    run(name,name,test,{'spec':'DESVIO_MENSAJE_PROTOCOLO_R2_240.json'})
