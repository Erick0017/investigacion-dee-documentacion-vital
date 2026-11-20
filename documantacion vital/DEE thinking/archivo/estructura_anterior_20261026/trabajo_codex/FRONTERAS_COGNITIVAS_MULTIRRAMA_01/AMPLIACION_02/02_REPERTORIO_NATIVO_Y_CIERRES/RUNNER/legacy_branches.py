"""Finite case definitions. Names are external questions, never Runtime labels."""
import json
from pathlib import Path
import dee_thinking as dt
from apparatus import *
from observations import *

BRANCH_SPECS={
 'L01':{'question':'Does paired physical exposure alter a later signal-alone response?',
        'apparatus':'two fixed C6 learner/query routes in N=34, one Runtime',
        'mechanism':'cue/event collision creates a mobile relation queried later',
        'treatment':'two correspondences; controls unpaired, signal-only, event-only, inverted, omitted',
        'panel':['response0 load/direction','response1 load/direction','actual receipts'],
        'horizon':11,'numeric_budget_criterion':'at least one query response differs from no-exposure and unpaired controls, with Applied inputs',
        'limits':'one architecture, <=4 discovery settings, 2 reserves, 1 retention extension'},
 'L02':{'question':'Does acquired history route an action before a prepared consequence arrives?',
        'apparatus':'C6 directional relation, symmetric query opportunities, native later consequence',
        'mechanism':'history establishes +y/-y transport; query joins it before later collision',
        'treatment':'matched paired/unpaired and inverse directional histories; omitted consequence',
        'panel':['action direction at 11','route occupancy at 14','earliest consequence at 18','timing margin'],
        'horizon':19,'numeric_budget_criterion':'history-dependent directional response and positive causal timing margin under reversed history',
        'limits':'one architecture, 2 reserves, 1 timing extension; route appropriateness external frozen contract'},
 'L03':{'question':'Can late action interception change sensory consequences and a later response?',
        'apparatus':'published relational turn-loop; contingent native collision and open replay control',
        'mechanism':'action product evolves into environment, return changes common readers',
        'treatment':'intact vs action removed after emission vs return cut vs sham',
        'panel':['emitted action','environmental outcome','returned carrier','A/B/reader response'],
        'horizon':26,'numeric_budget_criterion':'post-emission cut changes return and subsequent body response',
        'limits':'2 interface families maximum; sensory matching and learned contingency remain explicit pending requirements'},
 'L04':{'question':'Do fixed learned relations act consistently on held-out physical query realizations?',
        'apparatus':'same two C6 routes; translated queries and new payloads',
        'mechanism':'mobile acquired relation transforms query in a physical collision',
        'treatment':'distinct paired event consequences vs absent/inverted correspondences',
        'panel':['class response residual','route/direction','new query payload readout'],
        'horizon':11,'numeric_budget_criterion':'nonzero between-class residual separation and zero within-class variation on reserved payloads',
        'limits':'domain is finite transport/translation; no post-hoc learned decoder; inherited route symmetry is preparation'},
 'L05':{'question':'Can one query physically use two separately acquired relations in sequence?',
        'apparatus':'two C6 learned mobile relations at different hubs in one N=34 Runtime',
        'mechanism':'query meets relation1 at 11, then relation2 at 16',
        'treatment':'full, omit1, omit2, both omitted, late intermediate carrier cut',
        'panel':['first transformed query','second transformed query','directions/latencies'],
        'horizon':20,'numeric_budget_criterion':'common final query differs under both history omissions and intermediate route cut',
        'limits':'one sum/route architecture, 2 reserves, one retained-path extension; no symbolic composition claim'},
 'L06':{'question':'How does identical history express after native intervals without new inputs?',
        'apparatus':'relational and contextual basal presets, recurrent reader present/cut',
        'mechanism':'local phase/context recurrence plus common probe on isolated diagnostic branches',
        'treatment':'AB, H0, BA and recurring-reader cut; common probes at 1/25/100/170',
        'panel':['delta','axis_projection','query response','support readiness','local write gate'],
        'horizon':170,'numeric_budget_criterion':'same-history physical query signature differs between horizons or recurrence cut',
        'limits':'two preset families; propagation/phase vs historical reorganization not automatically adjudicated'},
 'L07':{'question':'What functional recovery occurs after declared damage with no host restoration?',
        'apparatus':'H3 calibration and separate basal damage/readiness experiment',
        'mechanism':'trained backup vs native basal recurrence following local loss',
        'treatment':'intact, damage A, support cut, identical-copy sham; H3 no-backup/path controls',
        'panel':['function before damage','site loss','future common query','support','latency'],
        'horizon':200,'numeric_budget_criterion':'lost signature subsequently returns without repair writes and depends on prepared/history controls',
        'limits':'H3 is coupled calibration, not new autonomous maintenance; 2 architectures maximum'},
 'L08':{'question':'Does a learned emitter effect reach a receiver whose own acquired relation alters its response?',
        'apparatus':'C6 emitter y relation and receiver z relation in one N=34 Runtime',
        'mechanism':'same mediator reaches receiver at 16; acquired receiver relation alters direction',
        'treatment':'full, emitter unexposed, receiver unexposed, late channel cut, inverted receiver direction',
        'panel':['mediator','receiver outgoing direction','both histories','later downstream consequence'],
        'horizon':22,'numeric_budget_criterion':'receiver direction depends on both emitter and receiver histories and channel cut',
        'limits':'finite mobile-relation apparatus; no full persistent material body or language claim'},
 'L09':{'question':'Can history-selected routes expose a hidden environmental state and affect later output?',
        'apparatus':'basal +y/-y routes with remote load condition on one native turn source',
        'mechanism':'history biases route; source difference becomes accessible only through downstream interaction',
        'treatment':'two hidden loads, AB/BA/H0, local-prefix equality and return cut',
        'panel':['initial local indistinguishability','route selection','hidden effect on return','later response'],
        'horizon':26,'numeric_budget_criterion':'equal initial local signature, differing return, different subsequent action; informative-route preference itself must be acquired',
        'limits':'one candidate interface; externally prepared preference does not establish information-seeking acquisition'}
}

def response(rt,q): return record(rt.observe(c(q)))

def association(ctx,s):
    w=c6_pair(tuple(tuple(x) for x in s.get('anchors',((10,10,8),(10,10,24)))))
    rt=ctx.track(w.runtime); ctx.recipe(json.loads(w.manifest_json()))
    arm=s.get('arm','paired'); cues=s.get('cues',[5,9]); events=s.get('events',[7,11])
    log=[]; ctx.cp(rt,'BEFORE_EXPERIENCE')
    for i in range(2):
        if arm not in ('event_only','none'): schedule_composed(w,log,f'l{i}','cue',0,cues[i])
        if arm not in ('signal_only','none'):
            if arm=='unpaired' and s.get('research_timing',False):
                schedule(rt,log,w.qualified_channel(f'l{i}','teacher'),1,events[i])
            else:schedule_composed(w,log,f'l{i}','teacher',1 if arm=='unpaired' else 0,events[i])
    ctx.to(rt,6);ctx.cp(rt,'AFTER_EXPERIENCE')
    age=s.get('extra_age',0)
    if age:
        ctx.to(rt,6+age)
        # Fixed ballistic extrapolation defines channels; does not inspect or move memory.
        for i in range(2):
            site=coord(w.landmarks[f'q{i}.response']); site=add(site,(0,1,0),age,rt.dimension)
            channel(rt,f'delayed{i}',add(site,(-1,0,0),-5,rt.dimension),(-1,0,0))
    ctx.cp(rt,'BEFORE_QUERY')
    query=s.get('query',13);queries=query if isinstance(query,list) else [query,query]
    sites={}
    for i in range(2):
        if age: schedule(rt,log,f'delayed{i}',rt.current_tick,queries[i],'probe')
        else: schedule_composed(w,log,f'q{i}','query',6,queries[i],True)
        sites[f'output{i}']=add(tuple(coord(w.landmarks[f'q{i}.response'])),(0,1,0),age,rt.dimension)
    rows=ctx.trace(rt,sites,rt.current_tick,11+age)
    out=[response(rt,sites[f'output{i}']) for i in range(2)]
    ctx.cp(rt,'FINAL')
    ctx.data('TRACE',rows);ctx.data('INPUTS',{'calls':log,'effective':[receipt(r) for r in rt.receipts]})
    return {'arm':arm,'query':query,'responses':out,'phi':[signature(r) for r in out],
            'residuals':[r['s_reg']-queries[i] for i,r in enumerate(out)],
            'input_receipts':[receipt(r) for r in rt.receipts],
            'host_writes_after_t0':ctx.effective_writes(rt,0),
            'modality':'P','age_at_query':6+age,
            'ambiguity':'Physical fixed routes select two relation carriers; the finite acquisition uses explicit event contributions, not human labels.'}

def composition(ctx,s):
    rt,m=chain_world(tuple(s.get('loads1',(5,7))),tuple(s.get('loads2',(9,15))),
                     s.get('query',13),s.get('arm','full'),tuple(s.get('translation',(0,0,0))),
                     s.get('receiver_axis','y'),s.get('receiver_sign',1),tuple(s.get('receiver_shift',(0,0,0))))
    ctx.track(rt);ctx.recipe(m);ctx.cp(rt,'T0'); ctx.to(rt,3);ctx.cp(rt,'ACQUIRED')
    log=[];ctx.to(rt,6);ctx.cp(rt,'BEFORE_QUERY');schedule(rt,log,'query',6,m['query'],'probe')
    meet1=tuple(m['meeting1']);meet2=tuple(m['meeting2']);d2=tuple(m['direction2'])
    sites={'relation1':lambda t:add(tuple(m['hub1']),(0,1,0),t-3,34),
           'relation2':lambda t:add(tuple(m['hub2']),d2,t-3,34),
           'first_response':meet1,'second_response':meet2}
    rows=ctx.trace(rt,sites,6,13)
    first=next(x['sites']['first_response'] for x in rows if x['tick']==11)
    edit=None
    if s.get('arm')=='link_cut':
        pos=add(meet1,(-1,1,0),2,34); new,edit=edited(rt,pos,0,label='late_intermediate_cut')
        rt=ctx.track(new);ctx.cp(rt,'AFTER_DIAGNOSTIC_CUT')
    rows+=ctx.trace(rt,sites,13,16)[1:]
    second=response(rt,meet2);ctx.cp(rt,'SECOND_RESPONSE')
    outdir=tuple(second['direction']);rows+=ctx.trace(rt,{'descendant':lambda t:add(meet2,outdir,t-16,34)},16,s.get('horizon',22))[1:]
    reuse=None
    if s.get('extra_query') is not None:
        # Fixed future path, not calculated from measured output. The frozen path is (-1,+1,0).
        at=25;target=add(meet2,(-1,1,0),at-16,34)
        channel(rt,'reuse',add(target,(-1,0,0),-5,34),(-1,0,0))
        if rt.current_tick != 20:raise ValueError('reuse protocol requires first horizon 20')
        schedule(rt,log,'reuse',20,s['extra_query'],'probe')
        rows+=ctx.trace(rt,{'reused_lineage':target},20,25)[1:]
        reuse=response(rt,target);ctx.cp(rt,'REUSE_RESPONSE')
    final=response(rt,add(meet2,outdir,rt.current_tick-16,34));ctx.cp(rt,'FINAL')
    ctx.data('TRACE',rows);ctx.data('INPUTS',{'calls':log,'effective':[receipt(r) for r in rt.receipts]})
    return {'arm':s.get('arm','full'),'first_response':first,'second_response':second,
            'descendant':final,'phi':[signature(first),signature(second),signature(final)],
            'intervention':edit,'reuse_reading':reuse,'host_writes_after_t0':ctx.effective_writes(rt,0),
            'diagnostic_edits_after_t0':0 if edit is None else 1,'modality':'P + diagnostic cut when declared',
            'ambiguity':'Query physically consumes/modifies learned carriers; this apparatus has finite routes, not autonomous renewal.'}

def anticipation(ctx,s):
    rt,m=predictive_world(s.get('sign',1),s.get('paired',True),s.get('consequence',True),
                          tuple(s.get('translation',(0,0,0))),s.get('query',13),s.get('consequence_tick',18))
    if s.get('naive',False):
        # Remove only the two training carriers before T0, preserving later consequence/opportunities.
        from apparatus import research_world
        placements=m['placements'][2:];rt=research_world(34,placements)
        for j,sign in enumerate((1,-1)):
            qsite=add(add(tuple(m['hub']),(0,sign,0),8,34),(-1,0,0),-5,34)
            channel(rt,f'signal{j}',qsite,(-1,0,0))
        m['placements']=placements;m['preparation_note']='training carriers absent; opportunity and consequence retained'
    ctx.track(rt);ctx.recipe(m);ctx.cp(rt,'T0');ctx.to(rt,3);ctx.cp(rt,'ACQUIRED');ctx.to(rt,6)
    log=[]
    for i in range(2):schedule(rt,log,f'signal{i}',6,m['query'],'probe')
    ctx.cp(rt,'BEFORE_ACTION');sites={'response':tuple(m['response_site']),
                                     'opportunity':tuple(m['opportunity']),
                                     'consequence':tuple(m['consequence_site'])}
    rows=ctx.trace(rt,sites,6,m['consequence_tick']+1)
    action=next(x['sites']['response'] for x in rows if x['tick']==11)
    reach=next(x['sites']['opportunity'] for x in rows if x['tick']==14)
    consequence=next(x['sites']['consequence'] for x in rows if x['tick']==m['consequence_tick'])
    ctx.cp(rt,'FINAL');ctx.data('TRACE',rows);ctx.data('INPUTS',{'calls':log,'effective':[receipt(r) for r in rt.receipts]})
    return {'action':action,'opportunity':reach,'environmental_consequence':consequence,
            'timing_margin_to_consequence':m['consequence_tick']-11,
            'route_contract_direction':m['goal_route_direction'],
            'phi':[signature(action),signature(reach),signature(consequence)],
            'host_writes_after_t0':ctx.effective_writes(rt,0),'modality':'P; consequence is prepared natively at T0',
            'ambiguity':'A physical history-conditioned early route is measured; learned prediction of a repeated temporal regularity requires further evidence.'}

def basal_intervention(ctx,s):
    kind=s.get('kind','contingency');hist=s.get('history','AB');control=s.get('control','FULL')
    w=basal(hist,control,tuple(s.get('origin',(15,15,15))));rt=ctx.track(w.runtime)
    a=tuple(coord(w.ports.a));b=tuple(coord(w.ports.b));o=tuple(coord(w.ports.origin));
    action=add(o,(1,1,0),5,47);bend=add(action,(0,0,1),5,47);ret=add(bend,(-1,-1,-1),1,47)
    ctx.recipe({'preset':'relational','history':hist,'control':control,'origin':o,'N':47,'t0':32,
                'a':a,'b':b,'action':action,'environment':bend,'return':ret})
    ctx.cp(rt,'T0');rows=[];changes=[];end=s.get('horizon',26)
    sites={'A':a,'B':b,'comparator':o,'action':action,'environment':bend,'return':ret,
           'reader':add(o,(0,1,0),1,47)}
    pre=rt.current_tick
    if kind=='hidden':
        # Distinct remote conditions installed once before T0; core and clocks unchanged.
        source=add(bend,(-1,-1,-1),-13,47);old=rt.observe(c(source)).record
        raw=dt.pack_record(old.state,old.s_reg+s.get('hidden_load_delta',0),old.dx,old.dy,old.dz,old.semantic)
        rt,e=edited(rt,source,raw,label='pre-T0 remote condition');ctx.track(rt);changes.append(e)
        ctx.cp(rt,'HIDDEN_WORLD_T0')
    for rel in range(0,end+1):
        ctx.to(rt,32+rel)
        r={'relative_tick':rel,'tick':rt.current_tick,'sites':{k:response(rt,q) for k,q in sites.items()},
           'gates':{'A':gate(rt,a),'B':gate(rt,b)}}
        rows.append(r)
        if rel in (1,3,8,13,14,18,end):ctx.cp(rt,f'T{rel}')
        if rel==s.get('cut_tick',8) and s.get('cut'):
            q=action if s['cut']=='action' else (ret if s['cut']=='return' else add(o,(0,0,1),10,47))
            new,e=edited(rt,q,0,label='late_'+s['cut']);rt=ctx.track(new);changes.append(e);ctx.cp(rt,'CUT')
    ctx.cp(rt,'FINAL');ctx.data('TRACE',rows);ctx.data('INTERVENTIONS',changes)
    return {'history':hist,'context_rows':rows,'phi':[signature(rows[-1]['sites'][k]) for k in ('A','B','comparator','return','reader')],
            'interventions':changes,'host_writes_after_t0':ctx.effective_writes(rt,32),
            'modality':'N after declared T0; any late cut is diagnostic',
            'pending':'Matched open sensory replay and acquisition of the informative/contingent policy are not established by native propagation alone.'}

def rest_or_damage(ctx,s):
    hist=s.get('history','AB');control=s.get('control','READ_CUT');context=s.get('contextual',False)
    w=basal(hist,control,tuple(s.get('origin',(15,15,15))),context);rt=ctx.track(w.runtime)
    preparation_edits=[]
    if s.get('remove_environment',False):
        for q in w.ports.environmental_sources:
            rt,e=edited(rt,tuple(coord(q)),0,label='pre-T0 environment-source omission');preparation_edits.append(e)
        ctx.track(rt)
    a=tuple(coord(w.ports.a));b=tuple(coord(w.ports.b));o=tuple(coord(w.ports.origin))
    ctx.recipe({'preset':'contextual' if context else 'relational','history':hist,'control':control,'ports':{'A':a,'B':b,'O':o},'N':47,
                'preparation_edits':preparation_edits})
    ctx.cp(rt,'T0');ctx.to(rt,35);ctx.cp(rt,'AFTER_EXPERIENCE');edits=[]
    if s.get('damage'):
        site=a if s['damage']=='A' else (tuple(coord(w.ports.supports[0])) if s['damage']=='support' else add(o,(0,0,1),12,47))
        new,e=edited(rt,site,0,label='declared_damage_'+s['damage']);rt=ctx.track(new);edits.append(e);ctx.cp(rt,'POST_DAMAGE')
    end=s.get('horizon',170);rows=[];probes=[]
    for rel in sorted(set([3,25,50,100,131,132,170,end])):
        if rel>end:continue
        ctx.to(rt,32+rel)
        local={'relative_tick':rel,'A':response(rt,a),'B':response(rt,b),
               'comparator':response(rt,o),'gateA':gate(rt,a),'gateB':gate(rt,b)}
        local['delta']=local['A']['s_reg']-local['B']['s_reg'];rows.append(local)
        ctx.cp(rt,f'BEFORE_PROBE_T{rel}')
        if rel in (3,25,100,170,end):
            reference=None
            if s.get('reference_control',False):
                reference=ctx.track(rt.fork());ctx.to(reference,32+rel+3)
            f=ctx.track(rt.fork());channel(f,'common_query',add(o,(0,1,0),-1,47),(0,1,0),6000,5)
            log=[];schedule(f,log,'common_query',f.current_tick,7,'probe');ctx.to(f,32+rel+3)
            probes.append({'origin_relative_tick':rel,'calls':log,'receipts':[receipt(r) for r in f.receipts],
                           'response':response(f,o),'downstream':[response(f,add(o,(sgn,1,0),1,47)) for sgn in (-1,0,1)],
                           'A':response(f,a),'B':response(f,b),
                           'no_query_reference':None if reference is None else {'response':response(reference,o),'A':response(reference,a),'B':response(reference,b),
                                                  'downstream':[response(reference,add(o,(sgn,1,0),1,47)) for sgn in (-1,0,1)]},
                           'modality':'DIAGNOSTIC_QUERY_FORK'})
    ctx.cp(rt,'FINAL');ctx.data('NATIVE_REST',rows);ctx.data('COMMON_PROBES',probes);ctx.data('DAMAGE',edits)
    return {'history':hist,'native_rows':rows,'common_probes':probes,'damage':edits,
            'phi':[[p['response']['s_reg'],p['response']['direction'],[signature(d) for d in p['downstream']]] for p in probes],
            'host_writes_after_t0_main':ctx.effective_writes(rt,32),
            'diagnostic_probe_receipts_count':sum(len(p['receipts']) for p in probes),
            'modality':'N main; probes/damage in declared diagnostic forks',
            'ambiguity':'Same observation time and local phase are recorded; time points are not independent replicates.'}

def repair_calibration(ctx,s):
    cfg=dt.RepairConfig();cfg.arm=getattr(dt.RepairArm,s.get('arm','TREATMENT'));cfg.authorize_diagnostic_damage=True
    out=dt.run_trained_redundancy_repair(cfg,OPTIONS)
    raw=out.final_raw;clk=out.final_clock;rt=ctx.track(dt.Runtime.import_research_state(31,193,raw,clk),count=False)
    ctx.cp(rt,'CALIBRATION_FINAL');ctx.recipe({'protocol':'H3','configuration':s,'N':31,'horizon_from_source':193,
                                              'host_policy':'published coupled protocol injections and explicit damage; not autonomous host-stop'})
    keys=['backup_learned','primary_function_before_damage','damage_applied','function_lost_after_damage',
          'reconstructed_at_arrival','fresh_function','primary_source_depleted','backup_source_depleted','query_load']
    vals={k:getattr(out,k) for k in keys};vals['query_direction']=[out.query_direction.dx,out.query_direction.dy,out.query_direction.dz]
    return {'calibration_only':True,'protocol_reported_readings':vals,
            'native_internal_tick_count':193,'operational_final_import':'exported complete RAW/clock; protocol state not reconstructed as live machine',
            'host_writes_after_t0':'coupled protocol, see product source; not counted as zero',
            'modality':'P/DIAGNOSTIC inherited calibration','phi':[vals['query_load'],vals['query_direction']]}

HANDLERS={'association':association,'composition':composition,'anticipation':anticipation,
          'basal_intervention':basal_intervention,'rest_or_damage':rest_or_damage,'repair_calibration':repair_calibration}

def initial_cases():
    cases=[]
    def a(branch,case,kind,spec,role='control',level=0):
        cases.append({'branch':branch,'case':case,'kind':kind,'spec':spec,'role':role,'level':level,'configuration':0})
    for arm in ('paired','none','signal_only','event_only','unpaired'):
        a('L01',arm,'association',{'arm':arm},'treatment' if arm=='paired' else 'control')
    a('L01','inverted','association',{'arm':'paired','events':[11,7]},'control')
    for sign in (1,-1):
        a('L02',f'paired_{sign}','anticipation',{'sign':sign},'treatment')
        a('L02',f'unpaired_{sign}','anticipation',{'sign':sign,'paired':False})
    a('L02','consequence_omitted','anticipation',{'consequence':False})
    for cut in (None,'action','return','sham'):
        a('L03',cut or 'contingent_intact','basal_intervention',{'cut':cut,'cut_tick':8 if cut=='action' else 14},'treatment' if cut is None else 'control')
    for arm in ('paired','none','unpaired'):
        a('L04',arm,'association',{'arm':arm,'events':[7,15]},'treatment' if arm=='paired' else 'control')
    a('L04','inverted','association',{'events':[15,7]},'control')
    for arm in ('full','omit1','omit2','link_cut'):
        a('L05',arm,'composition',{'arm':arm,'horizon':20},'treatment' if arm=='full' else 'control')
    for hist in ('AB','H0','BA'):
        a('L06',f'rest_{hist}','rest_or_damage',{'history':hist},'treatment' if hist=='AB' else 'control')
    a('L06','reader_intact','rest_or_damage',{'control':'FULL'},'control')
    for damage in (None,'A','support','sham'):
        a('L07',f'basal_{damage or "intact"}','rest_or_damage',{'damage':damage,'horizon':200},'treatment' if damage=='A' else 'control')
    for arm in ('TREATMENT','BACKUP_UNTRAINED','NO_BACKUP','PATH_CUT','OFFPATH_CUT'):
        a('L07','H3_'+arm,'repair_calibration',{'arm':arm},'calibration')
    for arm in ('full','naive1','naive2','link_cut'):
        a('L08',arm,'composition',{'arm':arm,'receiver_axis':'z','horizon':22},'treatment' if arm=='full' else 'control')
    a('L08','receiver_inverted','composition',{'receiver_axis':'z','receiver_sign':-1,'horizon':22},'control')
    for hist in ('AB','BA','H0'):
        for hidden in (0,2):
            a('L09',f'{hist}_hidden{hidden}','basal_intervention',{'kind':'hidden','history':hist,'hidden_load_delta':hidden},'treatment' if hist=='AB' else 'control')
    a('L09','hidden_return_cut','basal_intervention',{'kind':'hidden','hidden_load_delta':2,'cut':'return','cut_tick':14})
    return cases
