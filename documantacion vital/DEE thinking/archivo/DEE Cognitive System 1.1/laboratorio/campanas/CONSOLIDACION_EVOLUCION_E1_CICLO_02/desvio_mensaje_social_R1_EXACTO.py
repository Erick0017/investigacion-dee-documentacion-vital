"""Bounded spatial detour, not deletion, gatekeeper or learned attention.
Both possible B messages receive identical fixed zero turn opportunities.
X/Z distance, final reader, arrival phase and sign decoder stay unchanged.
"""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from comun import *
from capacidades import integracion_situada_01 as ic
from capacidades.integracion_situada_01 import delayed_social as social,social_guard,ic_native_core as core
from capacidades.conductos_acceso_aa01 import turning_inputs
def divert_message(a,p,name,sham=False,offsets=(40,48,56)):
    T=p['source_tick'];rr=[];turns=[];first,middle,last=offsets
    if middle-first!=last-middle:raise ValueError('Equal opposed Y excursions, no reader relocation')
    for b in p['banks']:
        sign=b['sign'];v0=[sign,0,1];v1=[sign,1,1];v2=[sign,-1,1]
        p1=core.move(b['birth'],v0,first-1);p2=core.move(p1,v1,middle-first);p3=core.move(p2,v2,last-middle)
        for index,(site,t,vin,vout)in enumerate(((p1,T+first,v0,v1),(p2,T+middle,v1,v2),(p3,T+last,v2,v0))):
            target=core.move(site,(0,1,0),19)if sham else site
            pulses=turning_inputs(vin,vout)
            turn={'bank':sign,'site':target,'on_route_site':site,'tick':t,'incoming':vin,'outgoing':vout,'pulses':pulses};turns.append(turn)
            for j,q in enumerate(pulses):rr.append(core.arrive(a,name+'.turn.'+str(sign)+'.'+str(index)+'.'+str(j),target,q['direction'],t,q['payload']))
    return{'name':name,'sham':sham,'offsets':list(offsets),'turns':turns,'requests':rr,'classification':'P0 designed native3D message detour. Same private content, final phase, resources and reader; not acquired routing or host answer choice.'}
if __name__=='__main__':
    s=Store();src_h=json.loads((EV/'C02_MAIN_171_RECORD_plus.json').read_text(encoding='utf8'))['result']['INSTRUMENTO']['snapshot_sha256']
    source=next(p for p in(s.root/'estado/checkpoints').glob('E1_CICLO02_MAIN.T20927.*')if digest_file(p)==src_h)
    cases=[('C02_DETOUR_230_CONSERVAR',False),('C02_DETOUR_231_SHAM',True)]
    atomic_json(EV/'DESVIO_MENSAJE_PROTOCOLO_230.json',{'cases':cases,'source':str(source.relative_to(s.root)),'sha256':src_h,'parent_tick':20927,
      'cause':'Observed old+X7 departs at21035 intoX+Z+14, when the already formed private+message approaches its plane; full pre/post retained.',
      'geometry':'Y+8thenY-8 during fixed40/48/56 offsets, both signs. Same X/Z displacement, same original phase3 final readers.12zero inputs or19y off-route sham.',
      'future':'Use first private20, then actual private52 update with same record5 challenge/protection/detour, old brief functions, gate85/100, external use.',
      'frozen_criteria':'Old+ atz23 remains independently usable AND actual new private sign atoriginalz29, without teacher, target or host reader switch. Torque consequences measured separately from raw retention.',
      'limits':'Designed P0 protection, not learned attention. No automatic default promotion or rewriting adverse MAIN.'})
    for name,sham in cases:
        fork('E1_CICLO02_MAIN',name,checkpoint=str(source.relative_to(s.root)))
        def test(a):
            initial=physical(a.world,occupation=True);p=social.get(a)['plan'];first=divert_message(a,p,name+'_0',sham);frames=[]
            for t in sorted({p['source_tick']+40,p['source_tick']+48,21034,21035,p['source_tick']+56,p['end_tick']}):
                ic.advance(a,until=t,record=False);site=[(11+t-20572)%67,59,23]
                frames.append({'tick':t,'old_expected':observe(a.world,site),'ports':[{'sign':b['sign'],'read':observe(a.world,b['target'])}for b in p['banks']],
                  'turns':[{'bank':q['bank'],'read':observe(a.world,q['site'])}for q in first['turns']if q['tick']==t],'global':physical(a.world,occupation=True)})
                if t in(21034,21035,p['end_tick']):a.save(EV/(name+'.T'+str(t)+'.deetsnap.gz'))
            uses=[ic.act_external(a,steps=1)]
            p2=social.begin(a,name=name+'_1',value=52,mode='full');guard=social_guard.divert_record(a,name=name+'_1',record_tick=p2['source_tick']-1)
            second=divert_message(a,p2,name+'_1',sham);record=[]
            for label in('minus','plus'):
                port='back.'+label+'.record';r=a.world.submit(port,5,p2['source_tick']-1);record.append({'id':int(r.id),'port':port,'payload':5,'tick':p2['source_tick']-1})
            ic.advance(a,until=p2['end_tick'],record=False);uses.append(ic.act_external(a,steps=1))
            old=ic.attach(a,record=False)
            try:panel=__import__('capacidades.integracion_situada_01.regression',fromlist=['inherited_panel']).inherited_panel(a,social=False)
            finally:old['detach']()
            gate=ic.experience(a,kind='puerta',options={'forces':[85,100],'wear':[5,5]});uses.append(ic.act_external(a,steps=1))
            return{'initial':initial,'sham':sham,'first_plan':p,'first_detour':first,'frames':frames,'second_plan':p2,'second_detour':second,
                   'second_record_requests':core.receipts(a,record),'second_record_protection':core.receipts(a,guard['requests']),
                   'first_detour_requests':core.receipts(a,first['requests']),'second_detour_requests':core.receipts(a,second['requests']),
                   'uses':uses,'old_panel':panel,'gate':gate,'final':physical(a.world,occupation=True),
                   'attribution':'Same exact inherited continuous state per branch; designed opportunities are external. No successful branch knowledge returned to original MAIN.'}
        run(name,name,test,{'spec':'DESVIO_MENSAJE_PROTOCOLO_230.json'})
