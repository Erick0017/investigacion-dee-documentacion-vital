from pathlib import Path
import sys,json,time
LAB=Path(__file__).resolve().parent;ROOT=LAB.parents[2];EV=ROOT/'evidencia/campanas/INTEGRACION_COGNITIVA_SITUADA_E1_01'
sys.path[:0]=[str(ROOT/'sistema'),str(LAB)]
from app.lives import Store
from app.native_tools import physical,atomic_json,digest_file
from app.process_control import protect_current
import ic_body as body,ic_external as ext
protect_current();s=Store();deadline=json.loads((LAB/'PRESUPUESTO_Y_PADRE.json').read_text())['monotonic_deadline_seconds']
cases=[('DIRECT_INTEGRATED_85','E1_SITUADO_DIRECTO_01',18,'full','closed','live',81017),('DIRECT_OPPOSITE_CONTENT_86','IC01_DIRECT_OPPOSITE',45,'full','closed','live',81017),('DIRECT_NO_PARTNER_87','IC01_DIRECT_NOPARTNER',18,'no_partner','closed','live',81017),('DIRECT_MESSAGE_CUT_88','IC01_DIRECT_CUT',18,'cut','closed','live',81017),('DIRECT_MESSAGE_SHAM_89','IC01_DIRECT_SHAM',18,'sham','closed','live',81017),('DIRECT_ACTUATOR_NULL_90','IC01_DIRECT_NULL',18,'full','nulled','live',81017),('DIRECT_SENSOR_CLAMP_91','IC01_DIRECT_CLAMP',18,'full','closed','clamp',81017),('DIRECT_SECOND_SEED_92','IC01_DIRECT_SEED2',18,'full','closed','live',81031)]
frozen={'design_before_cases':'Exact alternative fork from R11 native12-decision state T4003; NOT MAIN or a transfer of its future. Keep same world, prepared native feedback and transient A shunts. Simplify social opportunity: private native B object and one-hop E1 receiver, no new back.record/read/use. Prepared motor13 reads both physical body and receiver wires simultaneously. This tests current message use, not new persistent social association, negotiated language or a learned Pendulum policy.', 'contexts':[-1,-1,1,1]*4,'motor_clock':13,'steps_max':64,'stop_after_invalid_body_opportunities':3,'feedback_cost':'omitted in this declared variant, no disguised policy update','private_source_alignment':'First source147+67*k after current tick with source+1 congruent to the frozen motor13 anchor; geometric clock alignment, never chosen after an answer.'}
for name,life,value,smode,mode,sensor,seed in cases:
    if time.monotonic()>deadline:raise TimeoutError('Deadline')
    out=EV/(name+'.json')
    if out.exists():continue
    s.fork('IC01_TRANSIENT_A_43',life,kind='CANDIDATE'if name=='DIRECT_INTEGRATED_85'else'DIAGNOSTIC_COPY')
    def run(a):
        initial=physical(a.world,occupation=True);anchor=a.tick;armed=body.arm(a,name=name,contexts=tuple(frozen['contexts']),shunt='a_only');k=max(0,(a.tick+10-142+66)//67)
        while(147+67*k+1-anchor)%13:k+=1
        T=147+67*k;rr=[]
        if smode!='no_partner':
            for port,payload,t in [('B.quantity.object.cue',5,T-5),('B.quantity.object.resource',value,T-5),('B.quantity.reader',7,T-1)]:
                r=(a.world.probe if port.endswith('reader')else a.world.submit)(port,payload,t);rr.append({'id':int(r.id),'port':port,'payload':payload,'tick':t})
        h=body.attach(a);base=a.run_until;social_frames=[];cuts=[];events={T:'SOURCE',T+1:'RECEIVER'}
        def joint(t):
            for at,role in sorted(events.items()):
                if a.tick<at<=t:
                    base(at);row={'tick':at,'role':role,'B':body.ic.obs(a,a.transferred_quantity.geometry['center']),'receivers':[{'bank':b['id'],'read':body.ic.obs(a,b['message_site'])}for b in a.geometry['cpc9_return']['banks']]};social_frames.append(row)
                    if role=='SOURCE'and smode in('cut','sham'):
                        for b in a.geometry['cpc9_return']['banks']:
                            target=b['message_site']if smode=='cut'else body.ic.move(b['message_site'],(0,0,1),9);before=body.ic.obs(a,target)
                            item={'site':target,'before':before,'source_already_formed':True}
                            if before['raw']=='0':r=body.ic.submit(a,'IC01.direct.'+name+'.'+b['id'],target,(0,0,0),at,0,4);rr.append(r);item['request']=r
                            else:item['unsupported_occupied']=True
                            cuts.append(item)
            return base(t)
        a.run_until=joint
        try:external=ext.run_clocked(a,steps=64,mode=mode,feedback='omit',sensor=sensor,social_output=True,seed=seed,social_wire='direct',stop_invalid_body=3)
        finally:h['detach']()
        return{'frozen':frozen,'initial':initial,'body_preparation':armed,'native_frames':h['frames'],'private_B_value':value,'social_mode':smode,'source_tick':T,'social_frames':social_frames,'cuts':cuts,'social_requests':body.ic.receipts(a,rr),'external':external,'final':physical(a.world,occupation=True),'not_claimed':'A one-hop receiver/current output use is not persistent association learning or a second complete mind. External motor summation is prepared assistance, not composition learned inside DEE.'}
    r=s.mutate(life,'IC01_SIMPLIFIED_SOCIAL_BODY_AND_EXTERNAL_CONTINUITY',run,{'frozen':frozen,'condition':{'private':value,'social':smode,'actuator':mode,'sensor':sensor,'seed':seed},'sources':{p.name:digest_file(p)for p in[LAB/'ic_native_core.py',LAB/'ic_body.py',LAB/'ic_external.py',Path(__file__)]}});atomic_json(out,r);print(name+' '+str(r['INSTRUMENTO']['tick']),flush=True)
