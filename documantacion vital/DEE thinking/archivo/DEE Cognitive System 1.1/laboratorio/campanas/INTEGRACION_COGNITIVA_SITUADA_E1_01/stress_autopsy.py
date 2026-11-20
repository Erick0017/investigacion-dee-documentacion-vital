from pathlib import Path
import sys,json,time,random
LAB=Path(__file__).resolve().parent;ROOT=LAB.parents[2];EV=ROOT/'evidencia/campanas/INTEGRACION_COGNITIVA_SITUADA_E1_01'
sys.path[:0]=[str(ROOT/'sistema'),str(LAB)]
from app.lives import Store
from app.native_tools import atomic_json,digest_file,physical,observe,exact_receipt
from app.process_control import protect_current
import ic_external as ext,delayed_social as social,ic_native_core as ic
protect_current();s=Store();deadline=json.loads((LAB/'PRESUPUESTO_Y_PADRE.json').read_text())['monotonic_deadline_seconds']
# Complete the originally specified six recovery opportunities; the first
# withdrawal accidentally inherited the stress stop counter and ran only one.
for base,life in [('STRESS_SEVERE_146','IC01_STRESS_SEVERE_146'),('STRESS_DELAY_147','IC01_STRESS_DELAY_147'),('STRESS_NOMINAL_MAIN_145','E1_INTEGRADO_COSTO_SOCIAL_01')]:
    path=EV/(base+'_WITHDRAW_REMAINING5.json')
    if not path.exists():
        def recover(a):return ext.run(a,steps=5,mode='delay1'if 'DELAY'in base else'closed',readout='magnitude',feedback='cost',reader='omit',codec=2,stop_invalid=None,social_ports=social.get(a)['plan']['banks'])
        atomic_json(path,s.mutate(life,'IC01_COMPLETE_DECLARED_RECOVERY_WINDOW_NO_RESTORE',recover,{'correction':'First withdrawal ran1 of6 because a cumulative invalid counter was applied too early. These5 opportunities complete the specified window, without reset, removal of pending noise, reader change or re-teaching.','source':digest_file(__file__)}))
parent=json.loads((EV/'INTERLEAVE_SPEC_141.json').read_text())['parent']
# The stress start is the reached6237 endpoint, not the older5698 input.
record=json.loads((EV/'STRESS_SPEC_144.json').read_text())['parent']
cp=next(p for p in(s.root/'estado/checkpoints').glob('E1_INTEGRADO_COSTO_SOCIAL_01.T6237.*')if digest_file(p)==record)
cases=[('STRESS_REPLAY_ALL_148','all',True),('STRESS_OMIT_READER_149','omit_reader',False),('STRESS_OMIT_CUE_150','omit_cue',False),('STRESS_OMIT_BOTH_151','omit_both',False),('STRESS_SHAM_READER_152','sham_reader',False),('STRESS_REPLAY_PASSIVITY_153','all',False)]
for name,mode,trace in cases:
    if time.monotonic()>deadline:raise TimeoutError('Original campaign deadline')
    out=EV/(name+'.json');life='IC01_'+name
    if out.exists():continue
    s.fork('E1_INTEGRADO_COSTO_SOCIAL_01',life,kind='DIAGNOSTIC_COPY',checkpoint=str(cp.relative_to(s.root)))
    def run(a):
        rng=random.Random(81231);rr=[];omissions=[];first=6301
        for i in range(12):
            for j in range(2):
                port=rng.choice(['quantity.object.cue','quantity.object.resource','quantity.reader']);when=first+67*i-5+rng.randrange(5);load=rng.randrange(4);skip=(i==1 and j==0 and mode in('omit_reader','omit_both'))or(i==1 and j==1 and mode in('omit_cue','omit_both'))
                item={'index':2*i+j,'port':port,'tick':when,'payload':load}
                if skip:omissions.append(item);continue
                if i==1 and j==0 and mode=='sham_reader':
                    channel=next(p.channel for p in a.world.interfaces if p.name==port);site=[channel.injection_site.x,channel.injection_site.y,channel.injection_site.z];v=[channel.direction.dx,channel.direction.dy,channel.direction.dz];r=ic.submit(a,'IC01.noise.sham_reader',ic.move(site,(0,0,1),9),v,when,load);rr.append(dict(item,**{'id':r['id'],'sham_site':r['site']}))
                else:r=(a.world.probe if port.endswith('reader')else a.world.submit)(port,load,when);rr.append(dict(item,id=int(r.id)))
        frames=[];first_birth=None;snaps=[];base=a.run_until
        def advance(t):
            nonlocal first_birth
            if not trace:return base(t)
            for at in range(a.tick+1,t+1):
                pre_raw=a.world.runtime.raw_copy()if 6345<=at<=6440 else None
                base(at);raw=a.world.runtime.raw_copy();clock=a.world.runtime.clock_copy();states={};occ=0
                for v in raw:
                    state=v&0xffffffff
                    if state:occ+=1;states[state]=states.get(state,0)+1
                row={'tick':at,'occupied':occ,'state_counts':states,'quantity':observe(a.world,a.quantity.geometry['center']),'reference_route':observe(a.world,a.quantity.geometry['reference_hub'])}
                if any(k not in(1,)for k in states)and first_birth is None:
                    first_birth=at;indices=[i for i,v in enumerate(raw)if(v&0xffffffff)not in(0,1)][:3];row['first_new_class_context']=[]
                    for idx in indices:
                        p=[idx//4489,(idx//67)%67,idx%67];context=[]
                        for x in range(-3,4):
                            for y in range(-3,4):
                                for z in range(-3,4):
                                    q=ic.move(p,(x,y,z));k=(q[0]*67+q[1])*67+q[2];context.append({'site':q,'pre_raw':str(pre_raw[k])if pre_raw is not None else None,'post_raw':str(raw[k]),'post_clock':str(clock[k])})
                        row['first_new_class_context'].append({'site':p,'coverage':'7cubed context around first detected new-state sites. Full tick may consult larger composed dependencies; this is not a complete global lineage.','context':context})
                frames.append(row)
                if at in(6367,6368,first_birth):
                    path=EV/(name+'_T'+str(at)+'.deetsnap.gz');a.save(path);snaps.append({'path':str(path),'sha256':digest_file(path),'tick':at})
        a.run_until=advance
        try:r=ext.run(a,steps=4,readout='magnitude',feedback='cost',codec=2,reader='omit',stop_invalid=3,social_ports=social.get(a)['plan']['banks'])
        finally:a.run_until=base
        return{'source_prefix':str(cp.relative_to(s.root)),'mode':mode,'all_noise_requests':[dict(q,receipt=exact_receipt(a.world.runtime.receipt(q['id'])))for q in rr],'omissions':omissions,'frames':frames,'snapshots':snaps,'first_other_state_tick':first_birth,'external':r,'final':physical(a.world,occupation=True),'scope':'A new bounded diagnostic replay/intervention, not a retrospective claim that these controls already existed. Omitted noise inputs are environmental interventions, not erased E1 memory.'}
    r=s.mutate(life,'IC01_MINIMAL_NOISE_CAUSAL_DIAGNOSTIC',run,{'mode':mode,'trace':trace,'fixed_common_protocol':'4 external opportunities; same exogenous RNG and original complete6237prefix; only declared noise event differs','source':digest_file(__file__)});atomic_json(out,r);print(name+' '+str(r['INSTRUMENTO']['tick']),flush=True)
