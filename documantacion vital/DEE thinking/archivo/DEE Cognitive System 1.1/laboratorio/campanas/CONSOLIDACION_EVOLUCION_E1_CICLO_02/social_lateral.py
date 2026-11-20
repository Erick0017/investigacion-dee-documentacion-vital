"""Second bounded physical family: add one Y component to native encoding,
not a turn sequence or answer supplied by the host. Same N/phase/private B.
"""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from comun import *
from capacidades import integracion_situada_01 as ic
from capacidades.integracion_situada_01 import delayed_social as social,social_guard,ic_native_core as core,ic_external as external,regression
def lateral(a,p,name,sham=False):
    rr=[];banks=[]
    bridge=external.saved(a);parallel=list(bridge['social_ports'])
    for b in p['banks']:
        # The native B output already forms at T, before these same-boundary
        # sources are applied. Both signs get the same zero resource.
        site=core.move(b['birth'],(0,1,0),-1)
        if sham:site=core.move(site,(0,1,0),19)
        rr.append(core.submit(a,name+'.encodeY.'+str(b['sign']),site,(0,1,0),p['source_tick'],0))
        target=core.move(b['target'],(0,1,0),56)
        for v,label in(([0,0,-1],'Z'),([0,-1,0],'Y')):
            rr.append(core.arrive(a,name+'.read'+label+'.'+str(b['sign']),target,v,p['end_tick'],0))
        alt={**b,'target':target,'access':'fixed_lateral_Yplus56','incoming_direction':[b['sign'],1,1]};banks.append(alt)
        if not any(q['sign']==alt['sign']and q['target']==alt['target']for q in parallel):parallel.append(alt)
    bridge['social_ports']=parallel;external.store(a,bridge)
    return{'name':name,'sham':sham,'banks':banks,'requests':rr,'same_arrival_phase':True,
           'classification':'P0 native3D coding/decoding opportunities, not learned Y orientation, filtering or route selection. Existing content and old readers remain intact.'}
if __name__=='__main__':
    cases=[('C02_LATERAL_270_REAL',False,'full'),('C02_LATERAL_271_SHAM',True,'full'),
           ('C02_LATERAL_272_SIN_B',False,'no_partner'),('C02_LATERAL_273_CORTE',False,'cut')]
    values=[20,52,12,60]
    atomic_json(EV/'SOCIAL_LATERAL_PROTOCOLO_270.json',{'parent':'E1_CICLO02_CORTE_VALIDADO_20927','tick':20927,'cases':cases,'private_values':values,
      'bounded_family':'R1 late Y excursion was mixed. R2 ghost diversion preserved new updates but not old memory. Test a simpler native lateral code with no turns: two zero Y encoding resources plus four zero Y/Z readers.',
      'geometric_change':'Same original B comparison, source and end phase. Y+ during56native steps gives a fixed new recipient plane y48. Both signs/ports fixed before content, with all old ports retained. No N change, field edit, memory transplant or packet copied by Python.',
      'criteria':'Actual private B code at new plane y48 and old+7 at y59,z23 must both be usable; opposite contents in episodes1/3 rule out merely copying the same sign. Gate/reference and old comparisons also checked.',
      'controls':'Equal-dose Y-encoding sham displaced19y, no B, postformed cuts using the admitted native SEM4 mechanism. New reader ports and resources stay available in all arms.',
      'horizon':'Four complete private updates and later use, then two gate opportunities and another external step. No early favorable stop.'})
    for name,sham,mode in cases:
        fork('E1_CICLO02_CORTE_VALIDADO_20927',name)
        def test(a):
            initial=physical(a.world,occupation=True);episodes=[];rr=[]
            for i,value in enumerate(values):
                p=social.begin(a,name=name+'_'+str(i),value=value,mode=mode);l=lateral(a,p,name+'_'+str(i),sham)
                guard=social_guard.divert_record(a,name=name+'_'+str(i),record_tick=p['source_tick']-1);rr.extend(l['requests']+guard['requests']);record=[]
                for label in('minus','plus'):
                    port='back.'+label+'.record';r=a.world.submit(port,5,p['source_tick']-1);item={'id':int(r.id),'port':port,'payload':5,'tick':p['source_tick']-1};rr.append(item);record.append(item)
                frames=[]
                for t in(p['source_tick'],p['source_tick']+1,p['source_tick']+2,p['source_tick']+51,p['end_tick']):
                    ic.advance(a,until=t,record=False)
                    site=[(11+t-20572)%67,59,23]
                    frames.append({'tick':t,'B':observe(a.world,p['B']),'old_expected':observe(a.world,site),
                         'lateral_ports':[{'bank':b['sign'],'read':observe(a.world,b['target'])}for b in l['banks']],
                         'expected_trajectories':[{'bank':b['sign'],'read':observe(a.world,core.move(b['birth'],(b['sign'],1,1),max(0,t-p['birth_tick'])))}for b in l['banks']if t>=p['birth_tick']]})
                    if i in(0,3)and t in(p['source_tick']+1,p['end_tick']):a.save(EV/(name+'.EP'+str(i)+'.T'+str(t)+'.deetsnap.gz'))
                before_use=a.tick;use=ic.act_external(a,steps=1);a.save(EV/(name+'.EP'+str(i)+'.USO_T'+str(a.tick)+'.deetsnap.gz'))
                episodes.append({'index':i,'private_object':value,'mode':mode,'plan':p,'lateral':l,'frames':frames,
                  'record_requests':core.receipts(a,record),'social_requests':core.receipts(a,social.get(a)['plan']['requests']),
                  'cuts':social.get(a)['cuts'],'use':use,'after':physical(a.world,occupation=True)})
                if episodes[-1]['after']['occupied']>100000:break
            h=ic.attach(a,record=False)
            try:panel=regression.inherited_panel(a,social=False)
            finally:h['detach']()
            gate=ic.experience(a,kind='puerta',options={'forces':[85,100],'wear':[5,5]});last=ic.act_external(a,steps=1)
            return{'initial':initial,'sham':sham,'mode':mode,'episodes':episodes,'requests':core.receipts(a,rr),'old_panel':panel,'gate':gate,
                    'final_use':last,'final':physical(a.world,occupation=True),'limits':'Prepared interface remains P0. Native private content/old retention must be scored separately. No general policy or P2 claim.'}
        run(name,name,test,{'spec':'SOCIAL_LATERAL_PROTOCOLO_270.json'})
