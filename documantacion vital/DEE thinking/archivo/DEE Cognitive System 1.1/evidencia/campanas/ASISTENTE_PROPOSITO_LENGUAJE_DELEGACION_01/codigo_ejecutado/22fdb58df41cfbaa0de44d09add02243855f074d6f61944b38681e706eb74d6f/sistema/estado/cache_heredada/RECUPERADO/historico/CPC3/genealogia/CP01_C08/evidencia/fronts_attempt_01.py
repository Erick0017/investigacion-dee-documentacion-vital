"""Eight practical questions, finite supervised cases, common native instrument."""
from array import array
import json
from pathlib import Path
import time
import dee_thinking as d
from laboratorio import *
from sesion import Session,install_offpath


def C01(root,cfg):
    e=CaseEvidence(root,'C01',cfg);rows=[]
    for history in cfg['histories']+cfg['reserved']:
        w=make_body(origin=tuple(cfg['origin']));e.snapshot(w,history+'_T0');rs=body_experience(w,list(history)) if history else []
        if not history:w.run_until(34)
        initial=body_panel(w);reads=[]
        for horizon in cfg['horizons']:
            w.run_until(34+horizon);p,f=body_probe(w,cfg['query']);dx=p['response']['direction'][0] if p['response']['active'] else None
            truth=1 if history.startswith('A') else -1 if history.startswith('B') else 0
            reads.append({'horizon':horizon,'probe':p,'predicted_first_event':dx,'task_target_first_event':truth,'correct':dx==truth})
        rows.append({'history':history,'reserved':history in cfg['reserved'],'receipts':rs,'initial_panel':initial,'reads':reads,'baseline_FSM':{'first_event':truth,'state_slots':1,'same_effective_inputs':True}});e.snapshot(w,history+'_FINAL')
    return e.finish({'trials':rows,'accuracy':sum(x['correct'] for r in rows for x in r['reads'])/sum(len(r['reads']) for r in rows),
                     'interface':'ONLINE zero-load events at A/B neighbor ports; not selecting AB/BA preset','scope':'first-event latch in a frozen phase domain, not arbitrary sequence language'})


def C02(root,cfg):
    e=CaseEvidence(root,'C02',cfg);rows=[]
    for refs,paired in [((12,16),True),((16,12),True),((12,16),False)]:
        w,rs=learned_mobile(refs,cue=0,paired=paired);e.snapshot(w,'ACQUIRED_'+str(refs[0])+('_paired' if paired else '_unpaired'));probes=[]
        for q in cfg['queries']:
            p,f=mobile_query(w,q,protocol='q'+str(q));got=[r['s_reg'] if r['active'] else None for r in p['responses']]
            target=[q+x for x in refs];probes.append({'query':q,'measured':got,'target':target,'errors':[None if a is None else a-b for a,b in zip(got,target)],'physical':p})
        after=w.fork();after.run_until(6+cfg['rest']);ret,f=mobile_query(after,cfg['reserved_query'],protocol='retained')
        seq=w.fork();seq.start_mobile_sequence('sequential_queries',cfg['queries'],6);seq.run_until(6+5*len(cfg['queries']))
        sequential=[[reading(o) for o in s.captured] for s in seq.protocols[0].steps]
        rows.append({'reference_values':refs,'paired':paired,'inputs':rs,'independent':probes,'retention':ret,'sequential':sequential,
                     'baseline':'zero-origin slope1 calibration: y=q+reference; no native memory edits','experiences_presented':1})
    trained=[r for r in rows if r['paired']];errors=[abs(v) for r in trained for p in r['independent'] for v in p['errors'] if v is not None]
    return e.finish({'trials':rows,'reserved_absolute_error_max':max(errors),'representation':'native collision and directed carrier; unit gain is a declared mechanism, not an acquired arbitrary gain',
                     'queries_consumption':'independent forks vs sequential memory increments are different tasks'})


def C03(root,cfg):
    e=CaseEvidence(root,'C03',cfg);cases=[]
    for h in ('AB','BA',''):
        w=make_body();body_experience(w,list(h)) if h else w.run_until(34);w.run_until(84)
        variants=[('retained_latent',w)]
        if h=='AB':
            variants.append(('missing_center',edit_fork(w,w.view('body').spec.a,0,'authorized missing center diagnostic')))
            port=next(i.channel.injection_site for i in w.interfaces if i.name=='body.common_query');variants.append(('blocked_input',edit_fork(w,port,d.pack_record(1,0,0,0,0,4),'authorized occupied probe port')))
        for truth,x in variants:
            before=body_panel(x);p,f=body_probe(x);allowed={'baseline_comparator':before['observations']['comparator'],'panel_after_passive':before,'probe_receipt':p['receipt'],'probe_response':p['response']}
            # Explicit external diagnostic, blind to trial names and ground truth.
            diagnosis='RELATION_UNAVAILABLE' if not before['centers_available'] else 'INPUT_BLOCKED' if p['receipt']['status']=='rejected_occupied' else 'LATENT_RELATION_ACCESSIBLE' if p['response']['active'] else 'EXPRESSION_NOT_DETECTED'
            cases.append({'evaluator_only_condition':truth,'history':h,'allowed_observations':allowed,'external_diagnosis':diagnosis,'queries_used':1,'relation_before':before['delta'],'relation_after':p['after']['delta'],'probe_effect':physical(x)!=physical(f)})
    distributed=d.create_organization('distributed');distributed.submit('integration.A',8,0);distributed.submit('integration.B',9,0);distributed.run_until(cfg['saturation_horizon'])
    f=distributed.fork();r=f.probe('history.common_query',7,f.runtime.current_tick);f.advance(3);e.snapshot(distributed,'SATURATION_WITH_RELATION')
    cases.append({'evaluator_only_condition':'saturated_channel','allowed_observations':{'q':reading(distributed.observe('integration','q')),'relative_delta':distributed.view('history').observe().delta,'probe_receipt':receipt(f.runtime.receipt(r.id)),'probe_delta':f.view('history').observe().delta},'external_diagnosis':'CHANNEL_AT_CAP_RELATION_STILL_AVAILABLE','queries_used':1})
    return e.finish({'trials':cases,'distinct_diagnostic_classes':sorted({r['external_diagnosis'] for r in cases}),'not_entity_introspection':True,
                     'single_observer_limit':'comparator or saturated scalar alone does not specify relation/readout availability'})


def C04(root,cfg):
    e=CaseEvidence(root,'C04',cfg);rows=[]
    for params in cfg['preparations']:
        w=d.create_organization('competition',**params);w.run_until(5);pre=w.runtime.fork();w.advance();meet=w.view('encounter').spec.ports['meeting'];enc=d.observe_encounter(pre,w.runtime,meet)
        row={'preparation':params,'meeting':reading(w.runtime.observe(meet)),'contributors':[reading(o) for o in enc.direct_ballistic_contributors],'branch':enc.branch,'attribution_scope':enc.attribution_scope}
        if not params:
            e.snapshot(w,'JOINT_PRODUCT');r=w.probe('joint_query',13,6);w.run_until(14);row['first_use']=reading(w.observe('encounter','response'));row['first_receipt']=receipt(w.runtime.receipt(r.id));r=w.probe('later_query',17,14);w.run_until(20);row['second_use']=reading(w.observe('encounter','later_response'));e.snapshot(w,'JOINT_USED_TWICE')
        rows.append(row)
    w,_=learned_mobile(cue=0);a=w.probe('q0.query',13,6);b=w.probe('q0.query',17,6);w.advance()
    return e.finish({'native_trials':rows,'host_conflict_receipts':[receipt(w.runtime.receipt(a.id)),receipt(w.runtime.receipt(b.id))],
                     'baseline':'simultaneous bounded numeric sum and discrete direction resolver; DEE also retains physical product and later uses','no_host_arbitration_of_native_encounter':True})


def C05(root,cfg):
    e=CaseEvidence(root,'C05',cfg);rows=[]
    for teacher in cfg['teachers']:
        w=d.create_organization('native_transfer',cue0=0,teacher0=teacher);w.probe('query',0,6);w.run_until(13);e.snapshot(w,'TRANSFER_IN_FLIGHT_'+str(teacher));hub=w.view('stage0').spec.ports['response'];q=d.Coordinate((hub.x-2)%127,(hub.y+2)%127,hub.z)
        cut=edit_fork(w,q,0,'remove already emitted native relay');w.run_until(16);cut.run_until(16);states={'full':w,'relay_cut':cut}
        absent=d.create_organization('native_transfer',source_absent=1,cue0=0,teacher0=teacher);absent.probe('query',0,6);absent.run_until(16);states['source_absent']=absent
        signatures={}
        for arm,base in states.items():
            values=[]
            for query in cfg['queries']:
                f=base.fork();r=f.probe('receiver_query',query,16);f.run_until(21);o=f.observe('stage0','receiver_response');values.append({'query':query,'reading':reading(o),'receipt':receipt(f.runtime.receipt(r.id)),'evaluative_expected_only':teacher+query if arm=='full' else None})
            signatures[arm]=values
        e.snapshot(w,'RECEIVER_READY_'+str(teacher));rows.append({'teacher':teacher,'signatures':signatures,'main_untouched_by_reserved_probes':w.runtime.current_tick==16,'transfer_modality':'NATIVE_EVOLUTION_IN_SAME_RUNTIME'})
    return e.finish({'trials':rows,'baseline':'technical copy can replicate a parameter but is not the tested native transport','source_presented_as_prepared_physical_exposure':'zero cue and reference carriers collide during evolution, not a stored terminal learned snapshot'})


def C06(root,cfg):
    e=CaseEvidence(root,'C06',cfg);rows=[]
    for independent in (False,True):
        w=d.create_organization('contingent',history=d.BasalHistory.AB,independent=independent);w.advance(8);action=w.view('body').spec.ports['action'];r=reading(w.runtime.observe(action));cut=edit_fork(w,action,0,'late removal of formed native action');e.snapshot(w,'ACTION_'+str(int(independent)))
        w.advance(5);cut.advance(5);full13=body_panel(w);cut13=body_panel(cut);environment=reading(w.observe('body','environment'));environment_cut=reading(cut.observe('body','environment'))
        ret=w.view('body').spec.ports.get('return');retcut=edit_fork(w,ret,0,'late return-site interception') if ret and w.runtime.observe(ret).raw else w.fork()
        w.run_until(82);cut.run_until(82);retcut.run_until(82)
        panel={}
        for arm,x in [('full',w),('action_cut',cut),('return_site_cut',retcut)]:p,f=body_probe(x);panel[arm]=p
        rows.append({'independent_environment':independent,'action_at_t40':r,'environment_at_t45':environment,'environment_after_action_cut':environment_cut,'return_interception_applied':ret is not None and bool(full13['observations'].get('return',{}).get('RAW')),'post_return_panel':panel,
                     'history_scope':'AB preset is a technical reference, not online acquisition in this C06 internal apparatus'})
    return e.finish({'internal_DEE':rows,'external_repeated_learning_case':'C08 uses matched environment returns, no-return and yoked controls on one continuing native memory',
                     'MBP4_correction':'late exterior-action contrast is separated from omission of the initial local query; effects on environment do not imply necessity for a later A/B rewrite'})


def C07(root,cfg):
    e=CaseEvidence(root,'C07',cfg);parent=Path(root)/'casos/C05/RESULTADOS.json'
    if not parent.exists():return e.finish({'dependency':'C05 not available'},'BLOQUEADO_DEPENDENCIA')
    data=json.loads(parent.read_text());diagnoses=[]
    for t in data['measurements']['trials']:
        signature={arm:[v['reading']['s_reg'] if v['reading']['active'] else None for v in values] for arm,values in t['signatures'].items()}
        contrasts=[{'query':q,'full':a,'cut':b,'causal_effect':None if a is None or b is None else a-b} for q,a,b in zip(cfg['queries'],signature['full'],signature['relay_cut'])]
        diagnoses.append({'source_case':'C05','teacher':t['teacher'],'signatures':signature,'contrasts':contrasts,'statement_scope':'effect of this selective late relay removal, not universal unique provenance'})
    return e.finish({'diagnoses':diagnoses,'new_native_runs':0,'reused_evidence':str(parent.relative_to(Path(root))),'external_analysis_not_native_introspection':True})


def C08(root,cfg):
    e=CaseEvidence(root,'C08',cfg);rows=[]
    for refs,origin,role in [((12,16),(0,0,0),'confirmatory'),((16,12),(0,0,0),'history_inverted'),((18,23),(3,2,1),'reserved')]:
        s=Session.create(origin=origin,slots=cfg['slots'],resource=cfg['resource']);install_offpath(s);s.experience(0,*refs);s.advance_to(6);e.snapshot(s.world,'ACQUIRED_'+role)
        s.signal('s0',0);s.advance_to(11);first=s.state['frames'][-1];feedback=s.state['environment']['resource'];arms={}
        for arm in ('full_return','no_return','offpath','yoked'):
            f=s.fork()
            if arm!='no_return':f.schedule(feedback if arm!='yoked' else cfg['yoked_value'],1,'environment_return',offpath=arm=='offpath')
            f.advance_to(16);f.schedule(cfg['common_query'],2,'signal');f.advance_to(21);arms[arm]={'frames':f.state['frames'],'state':physical(f.world),'final_outputs':f.state['frames'][-1]['outputs'],'environment':f.state['environment']}
            if arm=='full_return' and role=='confirmatory':
                f.save(e.folder/'C08_MAIN_MID.deetsnap');resumed=Session.load(e.folder/'C08_MAIN_MID.deetsnap');resumed.schedule(cfg['reserved_query'],3,'signal');resumed.advance_to(26);f.schedule(cfg['reserved_query'],3,'signal');f.advance_to(26)
                assert physical(f.world)==physical(resumed.world);assert f.state==resumed.state
                f.save(e.folder/'C08_MAIN_FINAL.deetsnap');e.snapshots.append({'name':str((e.folder/'C08_MAIN_FINAL.deetsnap').relative_to(Path(root))),'sha256':__import__('hashlib').sha256((e.folder/'C08_MAIN_FINAL.deetsnap').read_bytes()).hexdigest(),'state':physical(f.world)})
        rows.append({'references':refs,'origin':origin,'role':role,'first_signal_same_interface':first,'environment_generated_feedback':feedback,'branches':arms})
    # Non-use and autonomous/driven distinction on a continuing acquired state.
    rest=Session.create(slots=cfg['slots']);rest.experience(0,12,16);rest.advance_to(56)
    q,f=mobile_query(rest.world,cfg['reserved_query'],protocol='rest_probe');rows.append({'rest_ticks_without_new_inputs':50,'retention_query':q,'new_acquisition_from_ticks_alone_claimed':False})
    return e.finish({'trials':rows,'communication':'opaque s0/s1 -> fixed physical load; response is newly measured native output','same_individual_between_episodes':True,'save_restore_exact':True,
                     'architecture':'two mobile acquired transforms in one Runtime, source-supported by finite declared contacts; external sandbox environment','relational_body_alternative':'DISCOVERY_01/02 acquired and retained order but repeated input was occupied/rejected; no feedback rewriting claimed',
                     'arbitrary_dictionary_or_human_language_claimed':False})


FIELDS={f'C{i:02}':globals()[f'C{i:02}'] for i in range(1,9)}
