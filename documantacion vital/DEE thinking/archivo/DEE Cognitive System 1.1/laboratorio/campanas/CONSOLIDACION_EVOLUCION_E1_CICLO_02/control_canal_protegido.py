"""Final bounded social causal controls; never touch protected originals."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from comun import *
from capacidades import integracion_situada_01 as ic
from capacidades.integracion_situada_01 import delayed_social as social,social_guard,ic_native_core as core
CASES=[('C02_CAUSAL_180_CORTE_MENOS',45,'cut'),('C02_CAUSAL_181_CORTE_MAS',18,'cut'),
       ('C02_CAUSAL_182_SHAM',45,'sham'),('C02_CAUSAL_183_SIN_B',45,'no_partner')]
s=Store();source=next(p for p in(s.root/'estado/checkpoints').glob('E1_INTEGRADO_MAIN.T3312.*')if digest_file(p)=='0658add9835a1c5b8f7a0d99b64153a54658f014a7c991921a499c2f9b608216')
atomic_json(EV/'CONTROL_CANAL_PROTEGIDO_PROTOCOLO_180.json',{'cases':CASES,'parent_sha256':digest_file(source),
  'initial_agenda':'Pre-arm T3312, pending0, not the later committed-body agenda with the same RAW',
  'protection':'Same two transient zero counterflows. All two record5requests remain admitted or are counted as rejected.',
  'cut':'Existing admitted delayed_social cut after B source formed, before message birth. Native SEM4, both branches. A rejected or unsupported cut is not a completed causal ablation.',
  'common_future':[3420,3899,4435],'use':'One real external use after last horizon, quantity kept available.',
  'criterion':'Message-specific output must disappear under a performed cut while fixed sham retains it. No B tests whether prepared protection creates the acquired sign by itself.'})
for name,value,mode in CASES:
    fork('E1_INTEGRADO_MAIN',name,checkpoint=str(source.relative_to(s.root)))
    def test(a):
        initial=physical(a.world,occupation=True);p=social.begin(a,name=name,value=value,mode=mode)
        guard=social_guard.divert_record(a,name=name,record_tick=p['source_tick']-1)
        rr=[]
        for label in('minus','plus'):
            port='back.'+label+'.record';r=a.world.submit(port,5,p['source_tick']-1);rr.append({'id':int(r.id),'port':port,'tick':p['source_tick']-1,'payload':5})
        frames=[]
        for t in(p['source_tick'],p['source_tick']+1,p['end_tick'],3899,4435):
            ic.advance(a,until=t,record=False)
            frames.append({'tick':t,'B':observe(a.world,p['B']),'ports':[{'sign':b['sign'],'read':observe(a.world,b['target'])}for b in p['banks']],
                           'global':physical(a.world,occupation=True),'cuts':social.get(a)['cuts']})
            if t==p['source_tick']+1:a.save(EV/(name+'.T'+str(t)+'.deetsnap.gz'))
        source_state=social.get(a)
        external=ic.act_external(a,steps=1)
        return{'initial':initial,'private_value':value,'mode':mode,'plan':p,'frames':frames,'source':source_state['source'],
               'cuts':source_state['cuts'],'record_requests':core.receipts(a,rr),
               'protection_requests':core.receipts(a,guard['requests']),
               'social_requests':core.receipts(a,source_state['plan']['requests']),
               'external':external,'final':physical(a.world,occupation=True)}
    run(name,name,test,{'spec':'CONTROL_CANAL_PROTEGIDO_PROTOCOLO_180.json'})
