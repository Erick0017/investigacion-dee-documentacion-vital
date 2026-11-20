import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from comun import *
from capacidades import integracion_situada_01 as ic
from capacidades.integracion_situada_01 import ic_native_core as core,delayed_social as social,social_guard
VALUES=[20,48,12,60,24,52,18,45]
CASES=[('C02_REUSO_130_TRANSITORIO','C02_DIV_080_MINUS','none'),
       ('C02_REUSO_131_TERMINAL','C02_DIV_083_TERMINAL','existing'),
       ('C02_REUSO_132_TERMINAL_TARDIO','C02_DIV_080_MINUS','late'),
       ('C02_REUSO_133_TERMINAL_SHAM','C02_DIV_080_MINUS','late_sham')]
atomic_json(EV/'REUTILIZACION_SOCIAL_PROTOCOLO_130.json',{'cases':CASES,'private_values':VALUES,
    'score':'Actual B reference has physical load36 and object format adds5. All chosen values strictly straddle it. Fixed pure-X received direction must match the private comparison, not merely be active.',
    'episodes':8,'new_record_load_each':5,'protection':'Same two zero counterflows each episode; no adaptive selection from output',
    'hypothesis':'Earlier deflected record contributions might interfere, remain neutral or acquire another function. Compare finite native absorption without assuming garbage.',
    'stop':'After2 consecutive invalid received signs or occupied>100000, preserve the actual reached state. No rollback or new favorable branch.',
    'native_time_horizon':'At least sixteen further67tick recurrences when all8opportunities complete, not a CPU benchmark.'})
for name,parent,termination in CASES:
    fork(parent,name)
    def test(a):
        initial=physical(a.world,occupation=True);rr=[];terminal=[];rows=[];invalid=0
        original_guard=social_guard.get(a)
        first=next(iter(original_guard['episodes'].values()))
        if termination in('late','late_sham'):
            for b in first['layout']:
                site=b['optional_terminator'];site=core.move(site,(0,0,1),19)if termination=='late_sham'else site
                terminal.append({'bank':b['bank'],'site':site,'pre':observe(a.world,site)})
                rr.append(core.submit(a,name+'.late_terminal.'+b['bank'],site,(0,0,0),a.tick+2,0,4))
        for i,value in enumerate(VALUES):
            p=social.begin(a,name=name+'_'+str(i),value=value,mode='full');rtime=p['source_tick']-1
            guard=social_guard.divert_record(a,name=name+'_'+str(i),record_tick=rtime)
            events=[]
            for label in('minus','plus'):
                port='back.'+label+'.record';r=a.world.submit(port,5,rtime);events.append({'id':int(r.id),'port':port,'tick':rtime,'payload':5})
            rr.extend(events+guard['requests']);frames=[]
            for t in(rtime,p['source_tick'],p['source_tick']+2,p['end_tick']):
                ic.advance(a,until=t,record=False);frames.append({'tick':t,'B':observe(a.world,p['B']),
                    'received':[{'sign':b['sign'],'read':observe(a.world,b['target'])}for b in p['banks']],
                    'record_contributions':[{'bank':b['bank'],'read':observe(a.world,b['meeting'])}for b in guard['layout']]})
                if i in(0,7)and t==p['source_tick']:a.save(EV/(name+'.EP'+str(i)+'.T'+str(t)+'.deetsnap.gz'))
            expected=1 if value+5<36 else-1
            outputs=frames[-1]['received'];codes=[b['sign']for b in outputs if b['read']['state']==1 and b['read']['semantic']==1 and b['read']['s_reg']>0 and b['read']['direction']==[b['sign'],0,0]]
            valid=len(codes)==1;correct=codes==[expected];invalid=invalid+1 if not valid else 0
            external=ic.act_external(a,steps=1);global_state=physical(a.world,occupation=True)
            rows.append({'index':i,'private_object':value,'expected_auditor_only':expected,'frames':frames,'received_codes':codes,'valid':valid,'correct':correct,
                'record_requests':core.receipts(a,events),'protection_requests':core.receipts(a,guard['requests']),
                'social_requests':core.receipts(a,social.get(a)['plan']['requests']),'external':external,'after':global_state})
            if invalid>=2 or global_state['occupied']>100000:break
        return{'initial':initial,'termination_variant':termination,'terminal_sites':terminal,'initial_requests':core.receipts(a,rr),
               'rows':rows,'requested_episodes':8,'completed_episodes':len(rows),'final':physical(a.world,occupation=True),
               'scope':'Repeated real social acquisition/use within each life. Different alternatives are not summed into MAIN.'}
    run(name,name,test,{'spec':'REUTILIZACION_SOCIAL_PROTOCOLO_130.json'})
