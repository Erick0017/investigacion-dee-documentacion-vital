"""Fourteen bounded fronts; all meanings live only in external measurements."""
import json,math
from pathlib import Path
import dee_thinking as dt
from apparatus import *
from observers import *

FRONT_SPECS={
 'P01':{'question':'Independent vs successive physical queries on acquired fixed routes','family':'C6 mobile relations','criterion':'Applied queries and history-conditioned residual; successive effective use count','panel':['actual receipts','loads','directions','latency','carrier consumption']},
 'P02':{'question':'History-conditioned route adequacy, distinct from mere earlier emission','family':'C6 directional history plus future encounter','criterion':'reaches frozen opportunity with correct direction vs naive; first actual contact precedes declared toroidal delay?','panel':['action','opportunity','first interaction','causal local equality']},
 'P03':{'question':'Contingent action, independent replay and later relational/readout state','family':'contextual basal feedback','criterion':'late cut/replay changes later common panel, with matching memory before replay','panel':['A/B validity','delta','return','common physical probe']},
 'P04':{'question':'Native transfer vs assisted sufficiency of partial relational state','family':'C6 zero relay and basal pair','criterion':'two source histories yield distinct receiver queries; subset restores source panel in matched background','panel':['source','recipient','three physical queries','mode of transfer']},
 'P05':{'question':'Different retained histories behind the same ordinary expression','family':'relative basal and phase sources','criterion':'ordinary expression equal while admitted common mediator reveals distinct histories','panel':['ordinary local','relation validity','common query','phase-resolved output']},
 'P06':{'question':'Which joint functions require distributed scaffold/history/context?','family':'catalog i05+i02+p02 N127','criterion':'common q panel differs under selective omissions/cuts; regions and latency tracked','panel':['two material centers','context reader','multichannel consequence','recurrent q']},
 'P07':{'question':'Does own action change write conditions or only expression?','family':'contextual basal return','criterion':'history/action cut changes effective common-E effect on A/B or expression','panel':['gates','A/B individually','delta valid','actual admission','query expression']},
 'P08':{'question':'Functional signature versus reappearing material and finite perturbation tolerance','family':'quiescent basal and prepared native contacts','criterion':'valid pre-damage panel restored; loss of a center never encoded as valid zero-memory','panel':['availability','support','functional probe','material reappearance']},
 'P09':{'question':'Depth and physically connected composition across families','family':'C6 cascade N127; C6-to-basal N47','criterion':'stage histories or link cut alter final query; cross-family input changes joint panel','panel':['each stage','actual load/direction','timing','basal expression']},
 'P10':{'question':'Finite generalization domain, phase/timing and saturation regimes','family':'C6 plus CORE05 phase','criterion':'paired same-dose control and finite reserved axes; distinguish scalar coalescence from full signature','panel':['payload','residual','direction','input receipts','retained pre-query state']},
 'P11':{'question':'Repair physical selectivity P versus Q before assessing preference acquisition','family':'relative basal + one conditional native encounter','criterion':'hidden variants differ in chosen P lineage, not Q, under same local prefix','panel':['initial interface','history route','conditional event','downstream use']},
 'P12':{'question':'Competing acquired contributions and occupied-target precedence','family':'two native C6 acquisitions, shared encounter','criterion':'combined panel compared to single contributions, timing and occupied/protected target','panel':['source histories','reducer encounter','material target','later query']},
 'P13':{'question':'Functions hidden by local/coarse/fixed-coordinate observers','family':'relative basal and phase observation','criterion':'same ordinary readout with distinct admitted functional probes or temporal patterns','panel':['local','relational','temporal','route','full RAW/clock']},
 'P14':{'question':'Open finite regularities without preassigned cognitive category','family':'CORE05/native windows and derived fronts','criterion':'specific prediction, alternative control and reserved realization','panel':['phase series','mouths','functional periodicity','RAW/clock dependence']}
}

def common_probe(ctx,rt,origin,load=7,direction=(0,1,0),h=3,shift=(0,0,0)):
    f=ctx.track(rt.fork());q=add(add(origin,(0,1,0),-1,rt.dimension),shift,1,rt.dimension)
    channel(f,'common_query',q,direction,6000,5);ctx.schedule(f,'common_query',f.current_tick,load,'probe')
    ctx.to(f,rt.current_tick+h)
    return {'input_start_tick':rt.current_tick,'actual_receipts':[receipt(r) for r in f.receipts if r.requested_tick>=rt.current_tick],
            'response':site(f,origin),'relationship':relational(f,origin),
            'downstream':[site(f,add(origin,(j,1,0),1,rt.dimension)) for j in (-1,0,1)]}

def repertoire(ctx,s):
    n=s.get('count',5);order=s.get('order','ascending');mode=s.get('mode','independent');arm=s.get('arm','paired')
    values=list(range(n))
    if order=='reverse':values.reverse()
    if s.get('payloads') is not None:values=list(s['payloads'])
    anchors=tuple(tuple(q) for q in s.get('anchors',((10,10,8),(10,10,24))))
    w=c6_pair(anchors);rt=ctx.track(w.runtime);ctx.recipe(json.loads(w.manifest_json()));ctx.cp(rt,'T0')
    events=[11,7] if arm=='inverted' else [7,11]
    if arm!='none':
        for j in range(2):
            ctx.schedule(rt,w.qualified_channel(f'l{j}','cue'),0,5)
            ctx.schedule(rt,w.qualified_channel(f'l{j}','teacher'),1 if arm=='unpaired' else 0,events[j])
    ctx.to(rt,6);ctx.cp(rt,'ACQUIRED_BEFORE_QUERY');initial=rt.fork()
    outputs=[];query_runtimes=[]
    for k,payload in enumerate(values):
        f=ctx.track(initial.fork()) if mode=='independent' else rt
        if mode=='independent' or k==0:
            begin=6;end=11;targets=[tuple(coord(w.landmarks[f'q{j}.response'])) for j in range(2)]
            for j in range(2):
                if s.get('query_direction'):
                    d=tuple(s['query_direction']);name=f'research_query{j}'
                    channel(f,name,add(targets[j],d,-5,34),d);ctx.schedule(f,name,begin,payload,'probe')
                else:ctx.schedule(f,w.qualified_channel(f'q{j}','query'),begin,payload,'probe')
        else:
            begin=11+5*(k-1);end=begin+5
            targets=[add(tuple(coord(w.landmarks[f'q{j}.response'])),(-1,1,0),end-11,34) for j in range(2)]
            for j,target in enumerate(targets):
                name=f'successive_{k}_{j}';channel(f,name,add(target,(-1,0,0),-5,34),(-1,0,0))
                ctx.schedule(f,name,begin,payload,'probe')
        ctx.to(f,end);readings=[site(f,q) for q in targets]
        outputs.append({'index':k,'payload':payload,'input_tick':begin,'read_tick':end,'response':readings,
                        'input_receipts':[receipt(r) for r in f.receipts if r.requested_tick==begin],
                        'residuals':[r['s_reg']-payload for r in readings],
                        'numeric_oracle_only': [min(19664,payload+(12 if j==0 else 16)) for j in range(2)] if mode=='independent' and arm=='paired' else None})
        if k in (0,len(values)-1):ctx.cp(f,'QUERY_FIRST' if k==0 else 'QUERY_LAST')
        query_runtimes.append(f)
    ctx.cp(rt if mode=='sequential' else initial,'MAIN_FINAL')
    ctx.data('QUERY_SERIES',outputs)
    signatures={json.dumps([record_signature(r) for r in row['response']]) for row in outputs}
    return {'mode':mode,'arm':arm,'query_order':values,'query_count':len(values),'response_series':outputs,
            'distinct_panel_responses':len(signatures),'initial_relation_loads':[12,16] if arm=='paired' else None,
            'history_count_not_inferred_from_response_count':True,
            'phi':[[r['s_reg'],r['direction']] for r in outputs[-1]['response']],
            'notes':'Fixed two routes, not a fiber per query. Sequential queries transform the same descendants; independent forks never reintegrated.'}

def horizon(ctx,s):
    sign=s.get('sign',1);h=s.get('consequence_tick',18)
    rt,m=predictive_world(sign,s.get('paired',True),s.get('consequence',True),tuple(s.get('translation',(0,0,0))),s.get('query',13),h)
    if s.get('naive'):
        placements=m['placements'][2:];rt=research_world(34,placements)
        for j,side in enumerate((1,-1)):
            target=add(m['hub'],(0,side,0),8,34);channel(rt,f'signal{j}',add(target,(-1,0,0),-5,34),(-1,0,0))
        m['placements']=placements
    ctx.track(rt);ctx.recipe(m);ctx.cp(rt,'T0');ctx.to(rt,6);ctx.cp(rt,'PRE_COMMON_INPUT')
    for j in range(2):ctx.schedule(rt,f'signal{j}',6,m['query'],'probe')
    samples=[];first=None;expected_load=m['query']+12
    for t in range(6,h+1):
        ctx.to(rt,t)
        pos=add(m['response_site'],(-1,sign,0),max(0,t-11),34)
        if t>=11:
            r=site(rt,pos)
            if first is None and (r['s_reg']!=expected_load or r['direction']!=[-1,sign,0]):first=t
        else:r=site(rt,m['response_site'])
        if t in (6,11,14,h) or (first is not None and abs(t-first)<=1):
            samples.append({'tick':t,'lineage_sample':r,'opportunity':site(rt,m['opportunity']),
                            'consequence_site':site(rt,m['consequence_site'])})
        if t in (11,14,h):ctx.cp(rt,f'T{t}')
    action=next(x['lineage_sample'] for x in samples if x['tick']==11)
    opportunity=next(x['opportunity'] for x in samples if x['tick']==14)
    appropriate=opportunity['state']>0 and opportunity['direction']==[-1,sign,0]
    return {'frozen_route_contract':[-1,sign,0],'action_at_11':action,'opportunity_at_14':opportunity,
            'route_adequacy_numeric':appropriate,'first_ballistic_signature_departure_tick':first,
            'declared_consequence_tick':h,'toroidal_flight_period':34,
            'trajectory':samples,'phi':[record_signature(action),record_signature(opportunity)],
            'limits':'Early emission exists also in naive. Adequacy is directional physical contract; delayed constructor is not by itself learned anticipation.'}

def contextual(ctx,s):
    origin=tuple(s.get('origin',(15,15,15)));w=basal('AB',s.get('control','FULL'),origin,True)
    rt=ctx.track(w.runtime);a=tuple(coord(w.ports.a));b=tuple(coord(w.ports.b));o=origin
    action=tuple(coord(w.ports.action_site));bend=tuple(coord(w.ports.bend_site));ret=tuple(coord(w.ports.return_site))
    ctx.recipe({'preset':'contextual_rewrite','N':47,'t0':32,'origin':o,'action':action,'bend':bend,'return':ret,
                'sources':[tuple(coord(q)) for q in w.ports.environmental_sources],**s});ctx.cp(rt,'T0')
    if s.get('common_event'):
        q=add(add(b,(0,1,0),1,47),tuple(s.get('event_shift',(0,0,0))),1,47);channel(rt,'common_event',q,(0,0,1))
        ctx.schedule(rt,'common_event',32+s.get('event_tick',130),s.get('event_load',0))
    rows=[];writes=[];previous=None;end=s.get('horizon',170)
    for rel in range(end+1):
        ctx.to(rt,32+rel);r=relational(rt,o)
        if previous is not None:
            for key in ('A','B'):
                if previous[key]['s_reg']!=r[key]['s_reg'] or previous[key]['material_center_present']!=r[key]['material_center_present']:
                    writes.append({'relative_transition':[rel-1,rel],'site':key,'before':previous[key],
                                   'after':r[key],'gate_before':previous['gate'+key]})
        previous=r
        if rel in (0,1,2,18,19,54,55,94,120,131,132,150,end) or 125<=rel<=133:
            rows.append({'relative_tick':rel,'body':r,'action':site(rt,action),'bend':site(rt,bend),'return':site(rt,ret)})
        if rel in (1,18,54,131,132,end):ctx.cp(rt,f'T{rel}')
        if rel==s.get('cut_tick',18) and s.get('cut'):
            q=action if s['cut']=='action' else ret
            rt=ctx.edit(rt,q,0,label='late_'+s['cut']);ctx.cp(rt,'AFTER_LATE_CUT')
        if rel==54 and s.get('replay'):
            ref=ctx.cut_runtime('P03','context_full','T54');assert ref.current_tick==rt.current_tick
            rbefore=relational(rt,o);raw=ref.observe(c(bend)).raw
            rt=ctx.edit(rt,bend,raw,label='external_one_site_environmental_replay')
            assert relational(rt,o)==rbefore;ctx.cp(rt,'AFTER_EXTERNAL_REPLAY')
    before_probe=relational(rt,o);probe=common_probe(ctx,rt,o)
    ctx.cp(rt,'MAIN_FINAL');ctx.data('CONTEXT_TRACE',rows);ctx.data('RELATIONAL_CHANGES',writes)
    return {'body_before_probe':before_probe,'common_probe':probe,'context_trace':rows,'relational_changes':writes,
            'phi':[before_probe['delta_validated'],record_signature(probe['response'])],
            'limits':'Full/cut/replay are causal contrasts. No acquired C/U policy or interface inversion is inferred from sensory difference alone.'}

def transplant(ctx,s):
    hist=s.get('history','AB');mode=s.get('mode','clone')
    src=ctx.parent_runtime(f'CHECKPOINTS/L06/quiescent_{hist}/AFTER_EXPERIENCE.deetsnap')
    o=(15,15,15);ctx.cp(src,'SOURCE_ACQUIRED');source_panel=relational(src,o)
    if mode=='clone':rt=ctx.track(src.fork())
    else:
        rt=ctx.parent_runtime('CHECKPOINTS/L06/quiescent_H0/AFTER_EXPERIENCE.deetsnap')
        a,b=(14,15,15),(16,15,15)
        if mode in ('delta_only','wrong_delta'):
            delta=source_panel['delta_validated']*(-1 if mode=='wrong_delta' else 1)
            old=rt.observe(c(a)).record
            raw=dt.pack_record(old.state,100+delta,old.dx,old.dy,old.dz,old.semantic)
            rt=ctx.edit(rt,a,raw,label='assisted_delta_only',modality='ASSISTED_RECONSTRUCTION')
        elif mode=='raw_pair':
            for q in (a,b):rt=ctx.edit(rt,q,src.observe(c(q)).raw,label='assisted_pair_RAW',modality='ASSISTED_RECONSTRUCTION')
        elif mode=='relation_context_phase':
            for dx in range(-2,3):
                for dy in range(-2,3):
                    for dz in range(-2,3):
                        q=add(o,(dx,dy,dz),1,47);x=src.observe(c(q));v=rt.observe(c(q))
                        if x.raw!=v.raw or x.clock!=v.clock:
                            rt=ctx.edit(rt,q,x.raw,x.clock,label='assisted_local_relation_context',modality='ASSISTED_RECONSTRUCTION')
    ctx.cp(rt,'RECEIVER_BEFORE_QUERY');queries=[common_probe(ctx,rt,o,p) for p in (0,7,13)]
    ctx.cp(rt,'MAIN_FINAL')
    return {'history':hist,'mode':mode,'source_panel':source_panel,'recipient_panel':relational(rt,o),
            'queries':queries,'phi':[record_signature(p['response']) for p in queries],
            'limits':'Partial edits are external sufficiency tests, not native transfer or organism preservation.'}

def native_transfer(ctx,s):
    rt,m=cascade_world(2,loads=[(5,s.get('event_load',7)),(9,15)],omit=1 if not s.get('source_absent') else 0,translation=tuple(s.get('translation',(0,0,0))))
    if s.get('source_absent'):
        # Receiver is empty, not a separately trained second relation.
        rt,m=cascade_world(1,loads=[(5,s.get('event_load',7))],omit=0,translation=tuple(s.get('translation',(0,0,0))))
    ctx.track(rt);ctx.recipe(m);ctx.cp(rt,'T0');ctx.to(rt,3);ctx.cp(rt,'SOURCE_ACQUIRED')
    ctx.to(rt,6);ctx.schedule(rt,'query',6,0,'probe');ctx.to(rt,11)
    first=site(rt,m['meetings'][0]['site']);ctx.cp(rt,'ZERO_RELAY_EMITTED')
    ctx.to(rt,13)
    if s.get('cut'):
        q=add(m['meetings'][0]['site'],(-1,1,0),2,127);rt=ctx.edit(rt,q,0,label='late_native_transfer_cut')
    ctx.to(rt,16);target=add(m['meetings'][0]['site'],(-1,1,0),10,127)
    channel(rt,'reserved_receiver_query',add(target,(-1,0,0),-5,127),(-1,0,0))
    ctx.schedule(rt,'reserved_receiver_query',16,s.get('receiver_query',13),'probe');ctx.to(rt,21);out=site(rt,target)
    src_after=site(rt,m['hubs'][0]);ctx.cp(rt,'MAIN_FINAL')
    return {'source_relation_event':s.get('event_load',7),'zero_relay_response':first,'recipient_response':out,
            'source_old_coordinate_after':src_after,'phi':[record_signature(first),record_signature(out)],
            'limits':'Native transfer of a finite mobile functional relation into a predeclared query route, not whole-body reinstantiation.'}

def latent(ctx,s):
    hist=s.get('history','AB');origin=tuple(s.get('origin',(15,15,15)))
    rt,m=quiescent(hist,origin);ctx.track(rt);ctx.recipe(m);ctx.cp(rt,'T0');ctx.to(rt,35);ctx.cp(rt,'ACQUIRED')
    ctx.to(rt,32+s.get('rest',25));pre=relational(rt,origin);ctx.cp(rt,'LATENT_BEFORE_MEDIATOR')
    if s.get('equalize'):
        a=tuple(m['A']);old=rt.observe(c(a)).record
        load=rt.observe(c(tuple(m['B']))).record.s_reg
        rt=ctx.edit(rt,a,dt.pack_record(old.state,load,old.dx,old.dy,old.dz,old.semantic),label='selective_relational_load_equalization')
    if s.get('sham'):
        a=tuple(m['A']);rt=ctx.edit(rt,a,rt.observe(c(a)).raw,label='identical_RAW_copy_sham')
    probes=[common_probe(ctx,rt,origin,load,direction=(0,-1,0) if s.get('wrong_mediator') else (0,1,0)) for load in (0,7)]
    ctx.cp(rt,'MAIN_FINAL')
    return {'history':hist,'ordinary_before_mediator':pre,'retained_full_hashes':full_hash(rt),
            'probes':probes,'phi':[record_signature(p['response']) for p in probes],
            'limits':'The common mediator is externally presented in forks; a silent ordinary reader is not evidence of destroyed history.'}

def distributed(ctx,s):
    w=distributed_world(s.get('history_mode',1),tuple(s.get('anchor',(30,30,30))),True,s.get('with_recurrence',True));rt=ctx.track(w.runtime)
    manifest=json.loads(w.manifest_json());ctx.recipe(manifest);ctx.cp(rt,'T0')
    o=tuple(s.get('anchor',(30,30,30)));sites={'center':o,'left':add(o,(-1,0,0),1,127),'right':add(o,(1,0,0),1,127)}
    if s.get('with_recurrence',True):
        sites.update({'consequence':tuple(coord(w.landmarks['integration.consequence'])),'q':tuple(coord(w.landmarks['integration.q']))})
        for port,load in (('A',8),('B',9)):
            ctx.schedule(rt,w.qualified_channel('integration',port),0,load)
        if s.get('link'):
            ctx.schedule(rt,w.qualified_channel('integration',s['link']),0,0)
    rows=[]
    for t in (0,1,3,6,8,10,12,16,20):
        ctx.to(rt,t);rows.append(panel(rt,sites))
        if t in (3,8,12):ctx.cp(rt,f'T{t}')
        if t==8 and s.get('late_center_cut'):
            rt=ctx.edit(rt,sites['left'],0,label='late_region_A_cut')
        if t==8 and s.get('late_load_change'):
            q=sites[s.get('region','left')];r=rt.observe(c(q)).record
            rt=ctx.edit(rt,q,dt.pack_record(r.state,r.s_reg+s['late_load_change'],r.dx,r.dy,r.dz,r.semantic),label='late_one_region_load_change')
    ctx.cp(rt,'MAIN_FINAL')
    return {'history_mode':s.get('history_mode',1),'regional_panels':rows,
            'phi':[record_signature(x) for x in rows[6]['sites'].values()],
            'joint_full_hashes':full_hash(rt),'limits':'Two regions/context share one native Runtime; static planner connections are only metadata, actual route samples are stored.'}

def damage(ctx,s):
    rt,m=quiescent(s.get('history','AB'),tuple(s.get('origin',(15,15,15))));ctx.track(rt);ctx.recipe(m);ctx.cp(rt,'T0');ctx.to(rt,35)
    before=common_probe(ctx,rt,m['origin']);ctx.cp(rt,'BEFORE_PERTURBATION')
    if s.get('remove_support'):
        rt=ctx.edit(rt,m['supports'][0],0,label='one_support_removed_once')
    if s.get('sham'):
        q=add(m['origin'],(0,0,1),12,47);rt=ctx.edit(rt,q,rt.observe(c(q)).raw,label='off_body_identical_copy')
    directions=[(0,1,0)] if s.get('contacts',1)==1 else [(0,1,0),(0,0,-1)]
    if s.get('contacts',1)>0:
        for j,d in enumerate(directions):
            target=m['A'];q=add(target,d,-4,47);channel(rt,f'finite_contact{j}',q,d)
            ctx.schedule(rt,f'finite_contact{j}',40,13)
    rows=[];probes=[]
    for rel in (4,8,12,25,100,170):
        ctx.to(rt,32+rel);rows.append(relational(rt,m['origin']))
        if rel in (12,25,170):probes.append(common_probe(ctx,rt,m['origin']))
    ctx.cp(rt,'MAIN_FINAL')
    return {'pre_damage_function':before,'body_trajectory':rows,'post_probes':probes,
            'phi':[record_signature(p['response']) for p in probes],
            'limits':'Finite contacts versus declared support removal. No host repair; stable occupied-target guard is not automatically an active defense policy.'}

def cascade(ctx,s):
    rt,m=cascade_world(s.get('depth',4),s.get('loads'),s.get('omit'),tuple(s.get('translation',(0,0,0))))
    ctx.track(rt);ctx.recipe(m);ctx.cp(rt,'T0');ctx.to(rt,3);ctx.cp(rt,'ACQUIRED')
    ctx.to(rt,6);ctx.schedule(rt,'query',6,s.get('query',13),'probe');out=[]
    for j,meeting in enumerate(m['meetings']):
        ctx.to(rt,meeting['tick']);r=site(rt,meeting['site']);out.append({'stage':j,'tick':meeting['tick'],'actual':r,
                  'evaluation_oracle_only':min(19664,s.get('query',13)+sum(sum(x['loads']) for x in m['meetings'][:j+1]))})
        if j in (0,len(m['meetings'])-1):ctx.cp(rt,f'STAGE_{j}')
        if j==s.get('cut_after',-1):
            ctx.to(rt,meeting['tick']+2);pos=add(meeting['site'],(-1,1,0),2,127)
            rt=ctx.edit(rt,pos,0,label='late_cascade_intermediate_cut')
    ctx.cp(rt,'MAIN_FINAL')
    return {'depth':len(out),'stages':out,'phi':[record_signature(x['actual']) for x in out],
            'limits':'Additive collision family, not a hierarchy of abstractions; each relation acquired within this Runtime.'}

def bridge(ctx,s):
    rt,m=mobile_basal_world(s.get('history','AB'),s.get('paired',True),s.get('offpath',False),s.get('mobile_only',False),s.get('body_only',False),tuple(s.get('origin',(15,15,15))))
    ctx.track(rt);ctx.recipe(m);ctx.cp(rt,'T0');rows=[]
    for rel in range(13):
        ctx.to(rt,32+rel);rows.append({'relative_tick':rel,'body':relational(rt,m['origin']),
                       'mobile_predicted_site':ballistic(rt,35,m['mobile_hub'],(0,1,0)) if rel>=3 else None})
        if rel==4 and s.get('cut'):
            pos=add(m['mobile_hub'],(0,1,0),1,47);rt=ctx.edit(rt,pos,0,label='late_interfamily_input_cut')
        if rel in (1,3,6,12):ctx.cp(rt,f'T{rel}')
    p=common_probe(ctx,rt,m['origin']);ctx.cp(rt,'MAIN_FINAL');ctx.data('BRIDGE_TRACE',rows)
    return {'joint_trace':rows,'later_common_probe':p,
            'phi':[rows[-1]['body']['delta_validated'],record_signature(rows[6]['body']['comparator']),record_signature(p['response'])],
            'limits':'Mobile-to-basal coexistence and native entry are measured separately from retained rewrite; installation is not learning.'}

def information(ctx,s):
    rt,m=native_probe_world(s.get('history','AB'),s.get('hidden',23),s.get('informative_side',1),tuple(s.get('origin',(15,15,15))))
    ctx.track(rt);ctx.recipe(m);ctx.cp(rt,'T0');rows=[];sign=1 if s.get('history','AB')=='AB' else -1
    for rel in range(17):
        ctx.to(rt,32+rel)
        choice=add(m['origin'],(sign,1,0),max(0,rel-3),47)
        conditional=m['conditional_meeting'];moving=add(conditional,(0,1,1),max(0,rel-8),47)
        rows.append({'relative_tick':rel,'body':relational(rt,m['origin']),
                     'chosen_action_segment':site(rt,choice),'conditional_site':site(rt,conditional),
                     'post_conditional_segment':site(rt,moving),'downstream_use':site(rt,m['downstream_site'])})
        if rel in (3,8,16):ctx.cp(rt,f'T{rel}')
        if rel==9 and s.get('cut'):
            pos=add(conditional,(0,1,1),1,47);rt=ctx.edit(rt,pos,0,label='late_information_mediator_cut')
    ctx.cp(rt,'MAIN_FINAL');ctx.data('SELECTIVITY_TRACE',rows)
    return {'history':s.get('history','AB'),'hidden_load':s.get('hidden',23),'informative_side':s.get('informative_side',1),
            'local_prefix':rows[:4],'conditional8':rows[8],'downstream16':rows[16],
            'phi':[record_signature(rows[8]['conditional_site']),record_signature(rows[16]['downstream_use'])],
            'limits':'First adjudicate physical P/Q selectivity. A history-selected route does not establish that informative preference itself was acquired.'}

def competition(ctx,s):
    rt,m=competition_world(s.get('arm','both'),s.get('occupied','empty'),s.get('shift',0),tuple(s.get('translation',(0,0,0))),tuple(s.get('second_direction',(0,0,1))))
    ctx.track(rt);ctx.recipe(m);ctx.cp(rt,'T0');rows=[]
    for t in (3,5,6,7,10,14):
        ctx.to(rt,t);r=site(rt,m['meeting'])
        Apos=add(m['hubs'][0],(0,1,0),t-3,34);Bpos=add(m['hubs'][1],m['second_direction'],t-3,34)
        rows.append({'tick':t,'target':r,'A_ballistic':site(rt,Apos),'B_ballistic':site(rt,Bpos),'common_readout':site(rt,m['readout'])})
        if t==6:
            ctx.cp(rt,'POST_CONTACT');ctx.schedule(rt,'joint_query',6,13,'probe')
        if t==10:ctx.cp(rt,'POST_JOINT_QUERY')
    ctx.cp(rt,'MAIN_FINAL')
    return {'arm':m['arm'],'destination_kind':m['occupied'],'shift':m['shift'],'contact':rows[2],
            'followup':rows,'phi':[record_signature(rows[2]['target']),record_signature(rows[4]['common_readout'])],
            'limits':'Proposals/reducer versus occupied material branch are distinct. Later targets are not automatically direct DEMUX recipients.'}

def phase(ctx,s):
    w=phase_world(s.get('mode',0),tuple(s.get('anchor',(15,15,15))),s.get('N',31),s.get('distance',4),s.get('clock_offset',0),s.get('permutation',0),s.get('signs',0),s.get('selected_source',3));rt=ctx.track(w.runtime)
    ctx.recipe(json.loads(w.manifest_json()));ctx.cp(rt,'T0');sites={'hub':tuple(coord(w.landmarks['phase.hub']))}
    for j in range(4):
        sites['source'+str(j)]=tuple(coord(w.landmarks[f'phase.installed_source{j}']))
        sites['mouth'+str(j)]=tuple(coord(w.landmarks[f'phase.mouth{j}']))
    rows=[];end=s.get('horizon',40)
    for t in range(end+1):
        ctx.to(rt,t)
        rows.append(panel(rt,sites))
        if t in (4,8,20,end):ctx.cp(rt,f'T{t}')
    means=[{'ticks':[t,t+1],'mean_load':(rows[t]['sites']['hub']['s_reg']+rows[t+1]['sites']['hub']['s_reg'])/2,
            'ordered_loads':[rows[t]['sites']['hub']['s_reg'],rows[t+1]['sites']['hub']['s_reg']]} for t in range(4,end,2)]
    probe=None
    if s.get('probe'):
        f=ctx.track(rt.fork());hub=sites['hub'];channel(f,'phase_query',add(hub,(-1,0,0),-4,rt.dimension),(-1,0,0))
        ctx.schedule(f,'phase_query',rt.current_tick,13,'probe');ctx.to(f,rt.current_tick+4);probe=site(f,hub);ctx.cp(f,'COMMON_QUERY_RESPONSE')
    ctx.data('PHASE_TRACE',rows);ctx.cp(rt,'MAIN_FINAL')
    return {'parameters':s,'phase_series':[r['sites']['hub'] for r in rows],'two_tick_observer':means,
            'phase_probe':probe,'final_raw_clock_hashes':full_hash(rt),
            'phi':[record_signature(r['sites']['hub']) for r in rows[-8:]],
            'limits':'Prepared recurrent source mechanism; clock offsets are pre-T0 controls. Mean aliasing and periodic emissions are not a cycle of complete RAW+clock state.'}

def reread(ctx,s):
    what=s.get('topic','contracts');result={}
    if what=='contracts':
        for branch in ('L01','L04'):
            for name in ('unpaired','unpaired_runtime_contract','paired'):
                member=f'BRANCHES/{branch}/{name}/'+('TECHNICAL_ERROR.json' if name=='unpaired' else 'MEASUREMENTS.json')
                result[branch+'/'+name]=ctx.parent_json(member)
        result['correction']='Rejected catalog input is not matched exposure; explicit Runtime timing is a distinct accepted contract.'
    elif what=='damage_availability':
        for name in ('basal_intact','basal_A','basal_support','basal_sham'):
            m=ctx.parent_json(f'BRANCHES/L07/{name}/MEASUREMENTS.json');rows=[]
            for row in m['native_rows']:
                ar,br=row['A'],row['B'];valid=ar['state']>0 and ar['semantic']==1 and br['state']>0 and br['semantic']==1
                rows.append({'relative_tick':row['relative_tick'],'A_state_semantic_load':[ar['state'],ar['semantic'],ar['s_reg']],
                             'B_state_semantic_load':[br['state'],br['semantic'],br['s_reg']],
                             'previous_delta':row['delta'],'valid_relation':valid,'delta_validated':row['delta'] if valid else None})
            result[name]=rows
        result['correction']='Reappeared matter and a scalar difference do not guarantee the old learned valid A/B relation.'
    elif what=='observers':
        for name in ('rest_AB','reader_intact','quiescent_AB','quiescent_BA','quiescent_H0'):
            m=ctx.parent_json(f'BRANCHES/L06/{name}/MEASUREMENTS.json')
            result[name]={'native_rows':m['native_rows'],'probes':[{ 'relative':p['origin_relative_tick'],
                'applied':any(str(r['status']).lower()=='applied' and r['requested_tick']==32+p['origin_relative_tick'] for r in p['receipts']),
                'expression':p['response'],'no_query_reference':p.get('no_query_reference')} for p in m['common_probes']]}
        result['correction']='Rejected late query is not demonstrated forgetting; quiescent variant is a new context, not a repaired historical run.'
    else:
        result['historical_combination']=ctx.parent_json('COMBINATIONS/COMBINATION_MEASUREMENTS.json')
        result['correction']='Exactly one L04+L05 crossing, five cases, same mobile collision family.'
    ctx.data('RETROSPECTIVE_READING',result)
    return {'topic':what,'readings':result,'phi':None,'new_execution':False,'limits':'A: retrospective analysis, not fresh simulation or holdout.'}

def phase_access(ctx,s):
    """Reuse a phase endpoint, then test another physical output rather than relabeling its hub."""
    anchor=tuple(s.get('anchor',(15,15,15)));n=s.get('N',31);distance=s.get('distance',4)
    if s.get('source_case'):
        rt=ctx.cut_runtime('P14',s['source_case']);start=rt.current_tick
    else:
        w=phase_world(s.get('mode',1),anchor,n,distance);rt=ctx.track(w.runtime);ctx.cp(rt,'T0')
        for t in range(41):ctx.to(rt,t)
        start=40
    mouth=add(anchor,(1,1,1),-(distance-1),n);target=add(mouth,(1,1,1),s.get('lane_step',1),n)
    ctx.recipe({'source_case':s.get('source_case'),'mode':s.get('mode',1),'anchor':anchor,'N':n,'distance':distance,
                'mouth3':mouth,'query_target':target,'prefix_horizon':40,'fixed_query_times':[start,start+1],
                'description':'Matched physical queries of phase-resolved lane, not scientist mean as native input.'})
    ctx.cp(rt,'PHASE_BEFORE_QUERY');before={'hub':site(rt,anchor),'source3':site(rt,add(mouth,(1,1,1),-1,n)),'mouth3':site(rt,mouth)}
    if s.get('cut_wrapped_flux'):
        q=add(anchor,(1,1,1),26,n)
        before['intercepted_wrapped_flux']=site(rt,q)
        rt=ctx.edit(rt,q,0,label='one_native_wrapped_carrier_removed_at40')
        ctx.cp(rt,'AFTER_WRAPPED_FLUX_CUT')
    outputs=[]
    for delay in (0,1):
        f=ctx.track(rt.fork());ctx.to(f,start+delay)
        channel(f,'access_query',add(target,(-1,0,0),-2,n),(-1,0,0))
        ctx.schedule(f,'access_query',start+delay,13,'probe');ctx.to(f,start+delay+2)
        outputs.append({'delay':delay,'input_tick':start+delay,'read_tick':start+delay+2,'actual':site(f,target),
                        'receipts':[receipt(r) for r in f.receipts]});ctx.cp(f,'INDEPENDENT_QUERY_'+str(delay))
    together=ctx.track(rt.fork());channel(together,'access_query',add(target,(-1,0,0),-2,n),(-1,0,0))
    for delay in (0,1):ctx.schedule(together,'access_query',start+delay,13,'probe')
    joint=[]
    for t in (start+2,start+3,start+4):ctx.to(together,t);joint.append(site(together,target))
    ctx.cp(together,'SUCCESSIVE_QUERIES_FINAL');ctx.cp(rt,'MAIN_FINAL');ctx.data('PHYSICAL_ACCESS',outputs)
    return {'ordinary_before_probe':before,'independent_queries':outputs,'successive_queries':joint,
            'phi':[record_signature(x['actual']) for x in outputs],
            'limits':'Forked externally scheduled queries; source phase acquired by transient T0 encounter, not a semantic memory label. Exact complete-state cycles are not claimed.'}

def phase_route(ctx,s):
    case=s.get('source_case','phase_ablation');rt=ctx.cut_runtime('P14',case,'T8');o=(15,15,15)
    ctx.to(rt,14);birth=site(rt,o);ctx.cp(rt,'HUB_BIRTH14');rows=[]
    for t in range(14,44):
        ctx.to(rt,t);q=add(o,(1,1,1),t-14,31)
        rows.append({'tick':t,'ballistic_prediction':list(q),'actual':site(rt,q),
                     'source3':site(rt,(11,11,11)),'mouth3':site(rt,(12,12,12))})
        if t in (30,40,41,43):ctx.cp(rt,'T'+str(t))
    ctx.cp(rt,'MAIN_FINAL');ctx.data('TOROIDAL_ROUTE',rows)
    return {'source_case':case,'birth14':birth,'route':rows,
            'phi':[record_signature(x['actual']) for x in rows[-4:]],
            'limits':'Forward replay of declared segment; a changed semantic or load stops identity correspondence. Equal-valued pulses elsewhere are not merged by labels.'}

def joint_followup(ctx,s):
    case=s.get('source_case','both_empty');tr=tuple(s.get('translation',(0,0,0)));rt=ctx.cut_runtime('P12',case)
    pos=add(add((12,20,19),tr,1,34),(-1,1,1),4,34);target=add(pos,(-1,1,1),6,34)
    before=site(rt,pos);ctx.cp(rt,'PARENT_POST_JOINT_QUERY');out=[]
    for payload in (0,17):
        f=ctx.track(rt.fork());channel(f,'new_joint_query',add(target,(0,0,-1),-6,34),(0,0,-1))
        ctx.schedule(f,'new_joint_query',14,payload,'probe');ctx.to(f,20)
        out.append({'payload':payload,'actual':site(f,target)});ctx.cp(f,'NEW_QUERY_'+str(payload))
    ctx.cp(rt,'MAIN_FINAL')
    return {'source_case':case,'observed_mobile_continuation_at14':before,'new_target':target,'queries':out,
            'phi':[record_signature(x['actual']) for x in out],
            'limits':'Further native use of joint mobile product; does not promote a single product to a complete renewable body.'}

def distributed_drift(ctx,s):
    source=s.get('source_case','distributed_HA');rt=ctx.cut_runtime('P06',source);o=(30,30,30)
    cat=dt.OrganizationCatalog();org=cat.instantiate(request('contextual_multichannel_recurrence.p02.v1','integration',o))
    q=tuple(coord(org.landmarks['q']));rows=[];ctx.cp(rt,'PARENT_T20')
    for t in (20,50,100,200,500,655,700):
        ctx.to(rt,t);rows.append({'tick':t,'body':relational(rt,o),'renewed_q':site(rt,q),
                               'last_counters':{k:getattr(rt.last_tick_info,k) for k in ('genesis','overflows','evaluated')}})
        if t in (100,500,700):ctx.cp(rt,'T'+str(t))
    queries=[common_probe(ctx,rt,o,p) for p in (0,7)];ctx.cp(rt,'MAIN_FINAL')
    return {'source_case':source,'native_no_new_inputs_series':rows,'final_common_queries':queries,
            'phi':[record_signature(rows[-1]['renewed_q']),rows[-1]['body']['delta_validated'],[record_signature(x['response']) for x in queries]],
            'limits':'Source-supported continuation, not elapsed-time learning. Scalar coalescence, full-state convergence, pair relation and expression are distinct measurements.'}

def bridge_retention(ctx,s):
    source=s.get('source_case','mobile_basal_full');o=(15,15,15)
    rt=ctx.cut_runtime('P09',source);rows=[];ctx.cp(rt,'PARENT_CROSS_FAMILY_ENDPOINT')
    for rel in (12,25,100,170):
        ctx.to(rt,32+rel);r=relational(rt,o);queries=[common_probe(ctx,rt,o,p) for p in (7,13)]
        rows.append({'relative_tick':rel,'body':r,'queries':queries});ctx.cp(rt,'H'+str(rel))
    ctx.cp(rt,'MAIN_FINAL')
    return {'source_case':source,'retention_series':rows,
            'phi':[[r['body']['delta_validated'],[record_signature(q['response']) for q in r['queries']]] for r in rows],
            'limits':'Continuation of the actual cross-family endpoint. Comparator state and pair relation are separate; equal or rejected probes do not imply destruction.'}

def latent_followup(ctx,s):
    case=s.get('source_case','latent_AB');rt=ctx.cut_runtime('P05',case);o=(15,15,15);rows=[]
    ctx.cp(rt,'PARENT_LATENT_ENDPOINT')
    for rel in (25,100,170,250):
        ctx.to(rt,32+rel);r=relational(rt,o);queries=[common_probe(ctx,rt,o,p) for p in (0,7)]
        rows.append({'relative_tick':rel,'body':r,'independent_queries':queries});ctx.cp(rt,'H'+str(rel))
    ctx.cp(rt,'MAIN_FINAL')
    return {'source_case':case,'readout_series':rows,'phi':[[r['body']['delta_validated'],[record_signature(q['response']) for q in r['independent_queries']]] for r in rows],
            'limits':'Actual previously acquired endpoints, native idle between diagnostic queries; complete clocks and common drift are not treated as erased memory.'}

def repertoire_delay(ctx,s):
    rt=ctx.cut_runtime('P01','independent5' if not s.get('naive') else 'independent5_naive','ACQUIRED_BEFORE_QUERY')
    start=6+s.get('gap',50);ctx.to(rt,start);ctx.cp(rt,'BEFORE_LATE_QUERIES');rows=[]
    for payload in (0,13):
        f=ctx.track(rt.fork());targets=[]
        for j,z in enumerate((8,24)):
            target=add((10,10,z),(0,1,0),start+5-3,34);targets.append(target)
            name=f'late_query{j}';channel(f,name,add(target,(-1,0,0),-5,34),(-1,0,0))
            ctx.schedule(f,name,start,payload,'probe')
        ctx.to(f,start+5);rows.append({'payload':payload,'read_tick':start+5,'responses':[site(f,q) for q in targets]})
        ctx.cp(f,'LATE_QUERY_'+str(payload))
    ctx.cp(rt,'MAIN_FINAL')
    return {'gap':s.get('gap',50),'naive':s.get('naive',False),'queries':rows,'phi':[[record_signature(x) for x in row['responses']] for row in rows],
            'limits':'Coordinates predict toroidal free flight; actual queried records are stored. No payload is copied from a reader into the world.'}

def missing_historical(ctx,s):
    return {'execution_status':'SOURCE_NOT_RECOVERED','phi':None,'requested':'ORGREINSTANTIATE20CX / WARPORG146X exact constructor',
            'search_scope':['product 3.0 package indexed source names','MBP3 ZIP core10_minimal','targeted filenames under documantacion vital'],
            'related_source_found':'MBP3 provenance/core10_minimal/RUNNERS/core10_apparatus.py::run_learned_policy_transfer',
            'not_equated_with_requested_historical_constructor':True,
            'closure_reason':'No exact ORGREINSTANTIATE20CX/WARPORG146X runner recovered in the bounded targeted search; native zero-relay and assisted sufficiency remain independently measured.'}

def contingency_loop(ctx,s):
    """Comparable prepared independent return, and physical reversal of the environment map."""
    origin=tuple(s.get('origin',(15,15,15)));history=s.get('history','AB');w=basal(history,'FULL',origin)
    rt=w.runtime;action=tuple(coord(w.ports.action_site));bend=tuple(coord(w.ports.bend_site));returned=tuple(coord(w.ports.return_site))
    preparation=[];direction=(1,1,-1) if s.get('inverse') else (-1,-1,-1)
    if s.get('independent'):
        for q in w.ports.environmental_sources:
            rt,e=edited(rt,tuple(coord(q)),0,label='pre-T0 omit contingent environment');preparation.append(e)
        q=add(bend,direction,-13,47)
        assert rt.observe(c(q)).raw==0
        rt,e=edited(rt,q,dt.pack_record(1,48,*direction,1),label='pre-T0 independent ballistic dose 48');preparation.append(e)
    elif s.get('inverse'):
        old=add(bend,(-1,-1,-1),-13,47);new=add(bend,direction,-13,47);r=rt.observe(c(old)).record
        assert (r.dx,r.dy,r.dz)==(-1,-1,-1) and rt.observe(c(new)).raw==0
        rt,e=edited(rt,old,0,label='pre-T0 reverse return converter route');preparation.append(e)
        rt,e=edited(rt,new,dt.pack_record(r.state,r.s_reg,*direction,r.semantic),label='pre-T0 reversed converter');preparation.append(e)
    ctx.track(rt);ctx.recipe({'origin':origin,'history':history,'N':47,'t0':32,'action':action,'bend':bend,'return':returned,
            'environment_preparation':preparation,'independent_dose':48 if s.get('independent') else None,
            'return_direction':direction,'inversion_is_native_geometry_not_learned_inversion':True})
    ctx.cp(rt,'T0');rows=[]
    for rel in range(27):
        ctx.to(rt,32+rel);rows.append({'relative_tick':rel,'body':relational(rt,origin),'action':site(rt,action),
            'environment':site(rt,bend),'return':site(rt,returned),
            'declared_ballistic_return':site(rt,add(bend,direction,max(0,rel-13),47))})
        if rel in (1,8,13,18,26):ctx.cp(rt,'T'+str(rel))
        if rel==8 and s.get('cut'):
            rt=ctx.edit(rt,action,0,label='late_one_product_action_cut')
    q=common_probe(ctx,rt,origin);ctx.cp(rt,'MAIN_FINAL');ctx.data('CONTINGENCY_WINDOW',rows)
    return {'history':history,'environment_independent':s.get('independent',False),'inverse_route':s.get('inverse',False),
            'environment_at13':rows[13]['environment'],'body_at13':rows[13]['body'],'rows':rows,'later_common_probe':q,
            'phi':[rows[-1]['body']['delta_validated'],record_signature(q['response'])],
            'limits':'Prepared noncontingent carrier is a control exposure, not learned response. Reversed mapping is an environmental manipulation; acquisition of contingency/inversion remains a separate question.'}

HANDLERS={'repertoire':repertoire,'horizon':horizon,'contextual':contextual,'transplant':transplant,'native_transfer':native_transfer,
          'latent':latent,'distributed':distributed,'damage':damage,'cascade':cascade,'bridge':bridge,
          'information':information,'competition':competition,'phase':phase,'reread':reread,
          'phase_access':phase_access,'bridge_retention':bridge_retention,'contingency_loop':contingency_loop,'latent_followup':latent_followup,
          'repertoire_delay':repertoire_delay,'missing_historical':missing_historical,'phase_route':phase_route,'joint_followup':joint_followup,'distributed_drift':distributed_drift}

def initial_cases():
    out=[]
    def add_case(front,id,handler,params,role='control',work='C',modality='EXPERIENCE_PROTOCOL',configuration=0):
        out.append({'front':front,'id':id,'handler':handler,'parameters':params,'role':role,'work_type':work,
                    'modality':modality,'level':'D','configuration':configuration,'horizon':params.get('horizon',170 if handler in ('latent','damage','contextual') else 40),
                    'panel':FRONT_SPECS[front]['panel'],'numerical_followup':FRONT_SPECS[front]['criterion'],
                    'closure':'finite preregistered protocol; no fitted cognitive verdict'})
    add_case('P01','independent5','repertoire',{'count':5},'treatment','B')
    add_case('P02','appropriate_paired18','horizon',{},'treatment','B')
    add_case('P03','context_full','contextual',{},'treatment','B','NATIVE')
    add_case('P04','assisted_clone_AB','transplant',{'history':'AB','mode':'clone'},'reference','B','ASSISTED_RECONSTRUCTION')
    add_case('P05','latent_AB','latent',{},'treatment','C','NATIVE + DIAGNOSTIC_PROBES')
    add_case('P06','distributed_HA','distributed',{},'treatment','C')
    add_case('P07','context_full_E','contextual',{'common_event':True},'treatment','C')
    add_case('P08','one_native_contact','damage',{'contacts':1},'treatment','C')
    add_case('P09','depth2_reference','cascade',{'depth':2},'reference','B')
    add_case('P10','payload_boundary','repertoire',{'payloads':[0,13,19500,19652,19664]},'treatment','C')
    add_case('P11','P_hidden23','information',{'history':'AB','hidden':23},'treatment','C','NATIVE')
    add_case('P12','both_empty','competition',{},'treatment','C')
    add_case('P13','reread_observer_coverage','reread',{'topic':'observers'},'reread','A','PASSIVE')
    add_case('P14','phase_baseline','phase',{'mode':0,'horizon':40},'treatment','C','NATIVE')
    add_case('P01','sequential5','repertoire',{'mode':'sequential','count':5},'treatment','B')
    add_case('P01','independent5_naive','repertoire',{'count':5,'arm':'none'},'control','B')
    add_case('P01','contracts_reread','reread',{'topic':'contracts'},'reread','A','PASSIVE')
    add_case('P02','naive18','horizon',{'naive':True},'control','B')
    add_case('P02','unpaired18','horizon',{'paired':False},'control','B')
    add_case('P02','inverse18','horizon',{'sign':-1},'control','B')
    add_case('P02','omitted18','horizon',{'consequence':False},'control','B')
    add_case('P03','late_action_cut','contextual',{'cut':'action','cut_tick':18},'control','B','DIAGNOSTIC')
    add_case('P03','late_action_open_replay','contextual',{'cut':'action','cut_tick':18,'replay':True},'control','B','DIAGNOSTIC')
    add_case('P03','native_no_initial_query','contextual',{'control':'NO_ACTION'},'control','B','NATIVE')
    for hist in ('AB','BA'):
        if hist=='BA':add_case('P04','assisted_clone_BA','transplant',{'history':hist,'mode':'clone'},'reference','B','ASSISTED_RECONSTRUCTION')
        for mode in ('virgin','delta_only','raw_pair','relation_context_phase','wrong_delta'):
            add_case('P04',f'{hist}_{mode}','transplant',{'history':hist,'mode':mode},'diagnostic','C','ASSISTED_RECONSTRUCTION')
    add_case('P04','native_zero_relay','native_transfer',{},'treatment','C')
    add_case('P04','native_zero_relay_cut','native_transfer',{'cut':True},'control','C','DIAGNOSTIC')
    add_case('P05','latent_BA','latent',{'history':'BA'},'control','C','NATIVE + DIAGNOSTIC_PROBES')
    add_case('P05','latent_H0','latent',{'history':'H0'},'control','C','NATIVE + DIAGNOSTIC_PROBES')
    add_case('P05','latent_equalized','latent',{'equalize':True},'diagnostic','C','DIAGNOSTIC')
    add_case('P05','latent_wrong_mediator','latent',{'wrong_mediator':True},'control','C')
    add_case('P05','latent_identical_copy','latent',{'sham':True},'control','C','DIAGNOSTIC')
    add_case('P06','distributed_HB','distributed',{'history_mode':2},'control','C')
    add_case('P06','distributed_H0','distributed',{'history_mode':0},'control','C')
    add_case('P06','distributed_link_cut','distributed',{'link':'cut_link'},'control','C')
    add_case('P06','distributed_link_sham','distributed',{'link':'sham_link'},'control','C')
    add_case('P06','distributed_no_recurrence','distributed',{'with_recurrence':False},'control','C')
    add_case('P07','context_cut_E','contextual',{'common_event':True,'cut':'action','cut_tick':18},'control','C','DIAGNOSTIC + EXPERIENCE_PROTOCOL')
    # P07 reuses the exact no-E trajectories P03/context_full and P03/late_action_cut.
    # They are not executed or counted again under new names.
    add_case('P08','intact_no_contact','damage',{'contacts':0},'control','B','NATIVE + DIAGNOSTIC_PROBES')
    add_case('P08','two_native_contacts','damage',{'contacts':2},'treatment','C')
    add_case('P08','support_removed','damage',{'contacts':0,'remove_support':True},'diagnostic','C','DIAGNOSTIC')
    add_case('P08','offbody_sham','damage',{'contacts':1,'sham':True},'control','C','DIAGNOSTIC')
    add_case('P08','previous_availability_reread','reread',{'topic':'damage_availability'},'reread','A','PASSIVE')
    add_case('P09','depth4','cascade',{'depth':4},'treatment','C',configuration=1)
    add_case('P09','depth4_omit2','cascade',{'depth':4,'omit':2},'control','C',configuration=1)
    add_case('P09','depth4_late_cut','cascade',{'depth':4,'cut_after':1},'control','C','DIAGNOSTIC',configuration=1)
    add_case('P09','mobile_basal_full','bridge',{},'treatment','C','NATIVE',configuration=2)
    add_case('P09','mobile_basal_late_cut','bridge',{'cut':True},'control','C','DIAGNOSTIC',configuration=2)
    add_case('P09','mobile_basal_offpath','bridge',{'offpath':True},'control','C','NATIVE',configuration=2)
    add_case('P09','mobile_alone','bridge',{'mobile_only':True},'control','C','NATIVE',configuration=2)
    add_case('P09','basal_alone','bridge',{'body_only':True},'control','C','NATIVE',configuration=2)
    add_case('P10','boundary_without_history','repertoire',{'payloads':[0,13,19500,19652,19664],'arm':'none'},'control','C')
    add_case('P10','same_dose_unpaired','repertoire',{'payloads':[0,13,19500,19652,19664],'arm':'unpaired'},'control','C')
    add_case('P11','P_hidden25','information',{'history':'AB','hidden':25},'treatment','C','NATIVE')
    add_case('P11','Q_hidden23','information',{'history':'BA','hidden':23},'control','C','NATIVE')
    add_case('P11','Q_hidden25','information',{'history':'BA','hidden':25},'control','C','NATIVE')
    add_case('P11','P_mediator_cut','information',{'history':'AB','hidden':25,'cut':True},'control','C','DIAGNOSTIC')
    for params,id in (({'arm':'A_only'},'A_only'),({'arm':'B_only'},'B_only'),({'shift':1},'one_tick_miss'),({'occupied':'protected'},'protected_destination'),({'occupied':'material'},'material_destination')):
        add_case('P12',id,'competition',params,'control','C')
    # P13's later probes will fork the immutable P14 endpoints, not rerun their histories.
    add_case('P14','phase_transient','phase',{'mode':1,'horizon':40},'treatment','C','NATIVE')
    add_case('P14','phase_ablation','phase',{'mode':2,'horizon':40},'control','C','NATIVE')
    add_case('P14','phase_high_uint64_clock','phase',{'mode':0,'horizon':40,'clock_offset':2**40+7},'control','C','NATIVE')
    return out

def followup_cases(root):
    """Finite numeric follow-up selected after breadth. Reserved cases use only frozen translations."""
    root=Path(root);out=[]
    def add_case(front,id,handler,params,role='control',level='D',work='C',modality='EXPERIENCE_PROTOCOL',configuration=0,reserve=None):
        out.append({'front':front,'id':id,'handler':handler,'parameters':params,'role':role,'work_type':work,'modality':modality,
            'level':level,'configuration':configuration,'reserve_realization':reserve,'horizon':params.get('horizon','finite in protocol'),
            'panel':FRONT_SPECS[front]['panel'],'numerical_followup':FRONT_SPECS[front]['criterion'],
            'closure':'Frozen finite follow-up; no refit after reserved results','selection_evidence':'completed first breadth within same extension'})
    m=json.loads((root/'BRANCHES/P01/independent5/MEASUREMENTS.json').read_text(encoding='utf-8'))
    if all(all(r['state']>0 for r in row['response']) for row in m['response_series']):
        add_case('P01','independent20','repertoire',{'count':20},'treatment',configuration=0)
        add_case('P01','sequential20','repertoire',{'count':20,'mode':'sequential'},'treatment',configuration=0)
    add_case('P01','inverted5','repertoire',{'count':5,'arm':'inverted'},'control','C',work='B')
    for k,offset in enumerate(((4,3,5),(11,6,9)),1):
        anchors=[list(add(q,offset,1,34)) for q in ((10,10,8),(10,10,24))]
        add_case('P01',f'reserved_order{k}','repertoire',{'count':20,'mode':'sequential','order':'reverse','anchors':anchors},'treatment','C',reserve=k)
        add_case('P01',f'reserved_independent{k}','repertoire',{'payloads':[20,27,33,41,49],'anchors':anchors},'treatment','C',reserve=k)
    for h in (50,100):
        add_case('P02',f'actual_contact_h{h}','horizon',{'consequence_tick':h},'treatment','E')
        add_case('P02',f'omitted_h{h}','horizon',{'consequence_tick':h,'consequence':False},'control','E')
    for k,translation in enumerate(((3,8,4),(12,15,15)),1):
        add_case('P02',f'reserved_history{k}','horizon',{'translation':translation},'treatment','C',reserve=k)
        add_case('P02',f'reserved_naive{k}','horizon',{'translation':translation,'naive':True},'control','C',reserve=k)
    for id,params in (('contingent_d5',{}),('independent_d5',{'independent':True}),('contingent_d5_cut',{'cut':True}),
                      ('independent_d5_cut',{'independent':True,'cut':True}),('contingency_reversed',{'inverse':True}),
                      ('independent_reversed',{'independent':True,'inverse':True})):
        add_case('P03',id,'contingency_loop',params,'treatment' if id in ('contingent_d5','contingency_reversed') else 'control','D',modality='NATIVE + DIAGNOSTIC_PROBES',configuration=1)
    for k,origin in enumerate(((22,20,24),(28,26,18)),1):
        add_case('P03',f'reserved_full{k}','contextual',{'origin':origin},'treatment','C',modality='NATIVE',reserve=k)
        add_case('P03',f'reserved_action_cut{k}','contextual',{'origin':origin,'cut':'action','cut_tick':18},'control','C',modality='DIAGNOSTIC',reserve=k)
    add_case('P04','native_zero_relay_other_history','native_transfer',{'event_load':11},'treatment','D')
    add_case('P04','native_source_absent','native_transfer',{'source_absent':True},'control','D')
    add_case('P04','historical_exact_dependency','missing_historical',{},'reference','D',work='B',modality='NO_EXECUTION')
    for k,(translation,payload) in enumerate((((7,8,6),23),((12,10,9),31)),1):
        for history in (7,11):
            add_case('P04',f'reserved_native{k}_event{history}','native_transfer',{'event_load':history,'translation':translation,'receiver_query':payload},'treatment','C',reserve=k)
        add_case('P04',f'reserved_native{k}_cut','native_transfer',{'translation':translation,'receiver_query':payload,'cut':True},'control','C',modality='DIAGNOSTIC',reserve=k)
    for k,origin in enumerate(((22,20,24),(28,26,18)),1):
        for hist in ('AB','BA'):
            add_case('P05',f'reserved_latent{k}_{hist}','latent',{'origin':origin,'history':hist},'treatment','C',modality='NATIVE + DIAGNOSTIC_PROBES',reserve=k)
    for source in ('latent_AB','latent_BA','latent_H0','latent_equalized'):
        add_case('P05','drift_'+source,'latent_followup',{'source_case':source},'treatment' if source in ('latent_AB','latent_BA') else 'control','E',modality='NATIVE + DIAGNOSTIC_PROBES')
    add_case('P06','late_region_A_load','distributed',{'late_load_change':-1},'diagnostic','D',modality='DIAGNOSTIC')
    add_case('P06','late_region_B_load','distributed',{'late_load_change':1,'region':'right'},'diagnostic','D',modality='DIAGNOSTIC')
    for k,anchor in enumerate(((45,40,36),(65,60,52)),1):
        add_case('P06',f'reserved_distributed{k}','distributed',{'anchor':anchor},'treatment','C',reserve=k)
        add_case('P06',f'reserved_distributed{k}_cut','distributed',{'anchor':anchor,'link':'cut_link'},'control','C',reserve=k)
    add_case('P07','external_E_phase129','contextual',{'common_event':True,'event_tick':129},'control','D')
    add_case('P07','external_E_offpath','contextual',{'common_event':True,'event_shift':(0,0,4)},'control','D')
    for k,origin in enumerate(((22,20,24),(28,26,18)),1):
        add_case('P07',f'reserved_common_E{k}','contextual',{'origin':origin,'common_event':True},'treatment','C',reserve=k)
        # No-E references are P03/reserved_full{k}, never executed twice.
    for k,origin in enumerate(((22,20,24),(28,26,18)),1):
        add_case('P08',f'reserved_contact{k}','damage',{'origin':origin,'contacts':1},'treatment','C',reserve=k)
    add_case('P09','depth8','cascade',{'depth':8},'treatment','E',configuration=3)
    for k,translation in enumerate(((10,8,9),(15,16,12)),1):
        add_case('P09',f'reserved_cascade{k}','cascade',{'depth':4,'translation':translation},'treatment','C',configuration=1,reserve=k)
        add_case('P09',f'reserved_cascade{k}_omit','cascade',{'depth':4,'translation':translation,'omit':2},'control','C',configuration=1,reserve=k)
    for k,origin in enumerate(((22,20,24),(28,26,18)),1):
        add_case('P09',f'reserved_bridge{k}','bridge',{'origin':origin},'treatment','C',modality='NATIVE',configuration=2,reserve=k)
        add_case('P09',f'reserved_bridge{k}_cut','bridge',{'origin':origin,'cut':True},'control','C',modality='DIAGNOSTIC',configuration=2,reserve=k)
    for direction,id in (((0,0,-1),'zminus'),((1,0,0),'xplus')):
        add_case('P10','research_direction_'+id,'repertoire',{'payloads':[0,13,47],'query_direction':direction},'treatment','D',configuration=1)
        add_case('P10','research_direction_'+id+'_naive','repertoire',{'payloads':[0,13,47],'query_direction':direction,'arm':'none'},'control','D',configuration=1)
    for k,anchors in enumerate(([[14,13,13],[14,13,29]],[[21,16,17],[21,16,33]]),1):
        add_case('P10',f'reserved_direction{k}','repertoire',{'payloads':[51,97],'query_direction':(0,0,-1),'anchors':anchors},'treatment','C',configuration=1,reserve=k)
    add_case('P10','native_gap50','repertoire_delay',{'gap':50},'treatment','E')
    add_case('P10','native_gap50_naive','repertoire_delay',{'gap':50,'naive':True},'control','E')
    for history in ('AB','BA'):
        add_case('P11','informative_side_swapped_'+history,'information',{'history':history,'hidden':25,'informative_side':-1},'control','D',modality='NATIVE',configuration=1)
    for k,origin in enumerate(((22,20,24),(28,26,18)),1):
        for history in ('AB','BA'):
            for hidden in (23,25):
                add_case('P11',f'reserved_selectivity{k}_{history}_{hidden}','information',{'origin':origin,'history':history,'hidden':hidden},'treatment' if history=='AB' else 'control','C',modality='NATIVE',reserve=k)
    add_case('P12','opposing_directions','competition',{'second_direction':(0,-1,0)},'control','D',configuration=1)
    for k,translation in enumerate(((15,17,14),(22,23,21)),1):
        add_case('P12',f'reserved_joint{k}','competition',{'translation':translation},'treatment','C',reserve=k)
        add_case('P12',f'reserved_singleA{k}','competition',{'translation':translation,'arm':'A_only'},'control','C',reserve=k)
    for source in ('phase_baseline','phase_transient','phase_ablation'):
        add_case('P13','access_'+source,'phase_access',{'source_case':source},'treatment' if source=='phase_transient' else 'control','D',modality='DIAGNOSTIC_PROBES',configuration=1)
    for source in ('mobile_basal_full','mobile_basal_late_cut','basal_alone'):
        add_case('P13','retained_expression_'+source,'bridge_retention',{'source_case':source},'treatment' if source=='mobile_basal_full' else 'control','E',modality='NATIVE + DIAGNOSTIC_PROBES',configuration=0)
    for mode in (0,1,2):
        add_case('P14',f'published_frame_mode{mode}','phase',{'mode':mode,'N':17,'distance':3,'anchor':(1,6,13),'permutation':2,'signs':1,'horizon':16},'treatment' if mode==1 else 'control','D',modality='NATIVE',configuration=1)
    seq20=root/'BRANCHES/P01/sequential20/MEASUREMENTS.json'
    if seq20.exists():
        measurements=json.loads(seq20.read_text(encoding='utf-8'))
        if all(all(r['state']>0 for r in row['response']) for row in measurements['response_series']):
            add_case('P01','independent50','repertoire',{'count':50},'treatment','E')
            add_case('P01','sequential50','repertoire',{'count':50,'mode':'sequential'},'treatment','E')
    if (root/'BRANCHES/P13/access_phase_transient/MEASUREMENTS.json').exists():
        for k,anchor in enumerate(((23,21,26),(8,12,19)),1):
            for mode in (0,1,2):
                add_case('P14',f'reserved_phase_access{k}_mode{mode}','phase_access',{'anchor':anchor,'mode':mode},'treatment' if mode==1 else 'control','C',modality='NATIVE + DIAGNOSTIC_PROBES',reserve=k)
        for source in ('phase_ablation','phase_transient'):
            add_case('P14','route_'+source,'phase_route',{'source_case':source},'diagnostic','D',modality='NATIVE_REPLAY')
        add_case('P14','ablation_wrapped_flux_cut','phase_access',{'source_case':'phase_ablation','cut_wrapped_flux':True},'diagnostic','D',modality='DIAGNOSTIC')
        # Prediction before these variants: removing load41 at (10,10,10), T40,
        # restricts its contribution to the T43 lateral query, with clocks unchanged.
    if (root/'BRANCHES/P12/both_empty/MEASUREMENTS.json').exists():
        for source in ('both_empty','A_only','B_only'):
            add_case('P12','later_use_'+source,'joint_followup',{'source_case':source},'treatment' if source=='both_empty' else 'control','E')
    if (root/'BRANCHES/P14/ablation_wrapped_flux_cut/MEASUREMENTS.json').exists():
        for k,anchor in enumerate(((23,21,26),(8,12,19)),1):
            add_case('P14',f'flux_cut_replication{k}','phase_access',{'source_case':f'reserved_phase_access{k}_mode2','anchor':anchor,'cut_wrapped_flux':True},
                     'diagnostic','C',modality='DIAGNOSTIC',reserve=k)
    if (root/'BRANCHES/P06/late_region_A_load/MEASUREMENTS.json').exists():
        for source in ('distributed_HA','distributed_H0','late_region_A_load'):
            add_case('P06','continued_'+source,'distributed_drift',{'source_case':source},'treatment' if source=='distributed_HA' else 'control','E',modality='NATIVE + DIAGNOSTIC_PROBES')
    return out
