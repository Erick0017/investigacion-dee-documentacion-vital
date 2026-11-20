"""Finite R14-derived native source-policy revision after physical comparison.

One research Runtime, one continuing mobile policy carrier. All alternative
turns, symmetric queries and source data exist at T0. The only later sensor
input is the actual explicit environmental consequence, duplicated on two
fixed comparator lanes. No host error, desired action or chosen source enters.
This is a finite consumed-resource apparatus, not an indefinitely renewed body.
"""
import json
from pathlib import Path
import dee_thinking as d
from .comparison import observed,coordinate,plus,make_placement,make_interface

# Exact direction constants in I01/RUNNERS/VENDORED/core10_apparatus.py.
A=(1,0,0);B=(0,1,0);SENSOR=(-1,0,1);NORMALIZER=(1,0,-1)
PENALTY0=(-1,1,0);ACTION0=(0,0,1);ACTION1=(-1,1,1)

def prepare(*,origin=(30,30,30),n=67,roles='P_INFORMATIVE',truth=1,actual_enabled=True):
    if truth not in (-1,1) or roles not in ('P_INFORMATIVE','Q_INFORMATIVE'):raise ValueError('Finite source/report domain')
    if n!=67:raise ValueError('This finite geometry was prepared for N67 only')
    p_value=truth if roles=='P_INFORMATIVE' else -truth;q_value=-p_value
    positions={};roles_at={};shared=[]
    def put(site,load,direction,state=1,clock=0,role='resource'):
        site=tuple(site);raw=d.pack_record(state,load,*direction,1)
        if site in positions:
            old=positions[site]
            if old.raw!=raw or old.clock!=clock:raise ValueError('Initial preparation overlap: '+str((site,roles_at[site],role)))
            shared.append({'site':site,'roles':[roles_at[site],role]});return
        p=make_placement(site,load,direction,state=state,clock=clock,role=role);positions[site]=p;roles_at[site]=role
    def arrival(target,tick,direction,load,role):put(plus(target,direction,-tick,n),load,direction,role=role)
    q=origin;put(q,7,A,clock=11,role='initial_policy_P')
    first_action=plus(q,A,1,n);arrival(first_action,1,SENSOR,47,'first_common_sensor')
    # The initial action physically gets P's report, not a host-selected lane.
    first_report=plus(first_action,ACTION0,1,n)
    arrival(first_report,2,(p_value,1,-1),31,'source_P_initial_actual_content')
    cmp_tick=6;write_tick=10;select_tick=11;info_tick=14
    interfaces=[];ports={'initial_policy':coordinate(q),'first_action':coordinate(first_action),'first_report':coordinate(first_report)}
    branches={};hubs={}
    for e in (-1,1):
        hub=plus(first_report,(e,1,0),4,n);tag='negative' if e<0 else 'positive';hubs[tag]=hub;ports[tag+'_comparison']=coordinate(hub)
        for c in (-1,1):
            dr=(-c,0,1);name='actual.'+tag+'.'+str(c);src=plus(hub,dr,-(cmp_tick-2),n);interfaces.append(make_interface(name,src,dr))
        # Oppositely signed error relative to e cannot occur in this binary
        # comparator. Only the two reachable branches per physical lane exist.
        for dx in (0,e):
            key=tag+'_'+str(dx);di=(dx,1,1);wp=plus(hub,di,4,n)
            nd=(1,-1,-1) if dx==0 else (-dx,0,-1)
            arrival(wp,write_tick,nd,11,'native_comparison_to_policy_'+key)
            ports[key+'_policy']=coordinate(wp);branches[key]={'hub':hub,'policy':wp,'dx':dx,'outputs':{}}
            for source,policy,action,value in [('P',A,ACTION0,p_value),('Q',B,ACTION1,q_value)]:
                query=plus(wp,policy,1,n);arrival(query,select_tick,SENSOR,17,'symmetric_policy_query_'+key+'_'+source)
                info=plus(query,action,3,n)
                # Source reports use the same finite physical content code.
                # Q's incoming action has x=-1: its +1 report needs two
                # distinct present contributors, explicitly declared here.
                vectors=[(value,1,-1)] if source=='P' else ([(0,0,-1)] if value<0 else [(1,0,-1),(1,0,0)])
                for j,vec in enumerate(vectors):arrival(info,info_tick,vec,23+j,'source_'+source+'_content_'+key+'_'+str(j))
                ports[key+'_'+source+'_action']=coordinate(query);ports[key+'_'+source+'_information']=coordinate(info)
                branches[key]['outputs'][source]={'query':query,'information':info,'native_action_direction':action,'source_report_value':value,'data_vectors':vectors}
    recipe=d.OrganizationRecipe.research(n,list(positions.values()),0);recipe.execution=d.TickOptions(d.Backend.LAZY,1);recipe.interfaces=interfaces
    view=d.OrganizationSpec();view.id='selection';view.recipe_id='finite_r14_source_revision.cpc3.v1';view.ports=ports;recipe.organizations=[view]
    world=d.OrganizationalWorld.create(recipe)
    m={'schema':1,'origin':list(origin),'n':n,'roles':roles,'truth':truth,'P_report':p_value,'Q_report':q_value,'actual_enabled':actual_enabled,'hubs':hubs,'branches':branches,'ticks':{'first_action':1,'first_report':2,'comparison':cmp_tick,'policy_revision':write_tick,'next_selection':select_tick,'selected_information':info_tick},'resources':{'initial_placements':len(positions),'initial_channels':len(interfaces),'shared_identical_placements':shared,'single_initial_policy':True,'separate_source_codec_costs':True},'scope':'finite prepared controller rule; experience-dependent policy state; no optimal/general/repeated utility learning claimed'}
    return world,m

def capture(world,metadata):
    ports=world.view('selection').spec.ports
    return {'tick':world.runtime.current_tick,'ports':{name:observed(world.runtime.observe(q)) for name,q in ports.items()}}

def measures(trace,metadata):
    at={r['tick']:r for r in trace};policies=[];actions=[];information=[]
    for key,branch in metadata['branches'].items():
        p=at[metadata['ticks']['policy_revision']]['ports'][key+'_policy']
        if p['active'] and tuple(p['direction']) in (A,B):policies.append({'branch':key,'policy':'P' if tuple(p['direction'])==A else 'Q','physical':p})
        for source,desc in branch['outputs'].items():
            action=at[metadata['ticks']['next_selection']]['ports'][key+'_'+source+'_action']
            if action['active'] and tuple(action['direction'])==tuple(desc['native_action_direction']):actions.append({'branch':key,'selected_source':source,'physical':action})
            o=at[metadata['ticks']['selected_information']]['ports'][key+'_'+source+'_information']
            if o['active'] and o['direction'][1:]==[1,0] and o['direction'][0] in (-1,1):information.append({'branch':key,'source':source,'observed_report':o['direction'][0],'physical':o})
    return {'native_policy_candidates':policies,'native_action_candidates':actions,'native_information_candidates':information,'unique_selected_sources':sorted({a['selected_source'] for a in actions}),'audit_only_report_truth':metadata['truth'],'audit_only_roles':metadata['roles'],'limits':'geometric path candidates, not provenance certified solely by a load; interference/extra products retained in full port traces'}

def run(configuration,output):
    output=Path(output);output.mkdir(parents=True,exist_ok=True);config=dict(configuration);cut=config.pop('late_action_cut',False);w,m=prepare(**config);w.save_snapshot(str(output/'T0.deetsnap'));trace=[];operations=[];receipts=[];interventions=[]
    while w.runtime.current_tick<=15:
        tick=w.runtime.current_tick
        if tick==1:
            w.save_snapshot(str(output/'FIRST_ACTION_T1.deetsnap'))
            if cut:
                site=w.view('selection').spec.ports['first_action'];old=w.runtime.observe(site);edit=d.ResearchStateEdit();edit.coordinate=site;edit.raw=0;edit.label='AUDITOR_DIAGNOSTIC_LATE_ACTION_CUT_CLOCK_UNCHANGED';w=w.diagnostic_fork([edit],True);interventions.append({'tick':1,'site':[site.x,site.y,site.z],'raw_before':old.raw,'raw_after':w.runtime.observe(site).raw,'clock_before':old.clock,'clock_after':w.runtime.observe(site).clock,'changed_sites':1,'changed_fields':['RAW'],'scope':'separate diagnostic trajectory; no merge'})
        if tick==2 and m['actual_enabled']:
            # The environment reports its actual current class. No forecast,
            # policy, source choice, discrepancy or decoder is read here.
            actual={'tick':tick,'observed_explicit_class':m['truth'],'modality':'DECLARED_EXTERNAL_ENVIRONMENT_SENSOR'}
            for tag in ('negative','positive'):
                name='actual.'+tag+'.'+str(actual['observed_explicit_class']);r=w.submit(name,1,tick);receipts.append(r.id);operations.append({'tick':tick,'operation':'submit','channel':name,'value':1,'source_actual':actual,'duplicate_encoding_of_one_observation':True,'receipt_id':r.id})
        trace.append(capture(w,m))
        if tick==10:w.save_snapshot(str(output/'REVISED_POLICY_T10.deetsnap'))
        if tick==15:break
        w.advance()
    w.save_snapshot(str(output/'FINAL_T15.deetsnap'));result={'configuration':configuration,'metadata':m,'trace':trace,'measurements':measures(trace,m),'external_operations':operations,'interventions':interventions,'receipts':[{'id':i,'status':str(w.runtime.receipt(i).status),'reason':w.runtime.receipt(i).reason,'effective_tick':w.runtime.receipt(i).effective_tick} for i in receipts],'host_cognitive_writes':[],'operational_forks':0,'diagnostic_forks':int(cut),'direct_RAW_clock_edits_on_native_cases':0}
    (output/'MEASUREMENTS.json').write_text(json.dumps(result,indent=2),encoding='utf-8');return result

def revalidate_r14(output):
    """Port of the exact recovered R14 placements, not its old Runtime/binary."""
    rows=[]
    for bit in (0,1):
        n=23;q=(10,10,10);placements=[]
        def arrival(target,t,dr,load):placements.append(make_placement(plus(target,dr,-t,n),load,dr))
        placements.append(make_placement(q,7,A,clock=11));t1=plus(q,A,1,n);arrival(t1,1,SENSOR,47);t2=plus(t1,ACTION0,1,n);arrival(t2,2,NORMALIZER,53)
        if bit:arrival(t2,2,PENALTY0,59)
        ta=plus(t2,A,1,n);tb=plus(t2,B,1,n);arrival(ta,3,SENSOR,101);arrival(tb,3,SENSOR,103)
        r=d.OrganizationRecipe.research(n,placements,0);r.execution=d.TickOptions(d.Backend.LAZY,1);w=d.OrganizationalWorld.create(r);w.advance();action=observed(w.runtime.observe(coordinate(t1)));w.advance();policy=observed(w.runtime.observe(coordinate(t2)));w.advance();a=observed(w.runtime.observe(coordinate(ta)));b=observed(w.runtime.observe(coordinate(tb)));rows.append({'bit_prepared_in_environment':bit,'action':action,'policy':policy,'probeP':a,'probeQ':b,'source':'feedback_apparatus_v1.py exact placement/direction algorithm, new 3.5 Runtime','expected_only_in_test':{'policy':B if bit else A,'later_action':ACTION1 if bit else ACTION0}})
    Path(output).write_text(json.dumps(rows,indent=2),encoding='utf-8');return rows
