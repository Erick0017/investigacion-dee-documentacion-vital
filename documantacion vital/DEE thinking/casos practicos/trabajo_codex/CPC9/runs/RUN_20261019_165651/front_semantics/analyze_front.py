"""Recalculate observables and denominators without importing the DEE engine.

Scientific interpretations below are authored and bounded; no generic NSM
level is awarded automatically from a threshold or a count of successes.
"""
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parent


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    return json.loads(Path(path).read_text(encoding='utf8'))


def locator(path):
    return {'path':str(Path(path).relative_to(ROOT)).replace('\\','/'),'sha256':sha(path)}


def qualified(frame, index):
    out=[]
    for row in frame['readers']:
        obs=row['reading'+str(index)]
        if obs['active'] and obs['semantic']==1 and obs['s_reg']>7 and obs['direction']==row['query'+str(index)]['expected_direction']:
            out.append({'axis':row['route_axis_candidate'],'candidate_x':row['candidate_comparator_x'],
                        'heading':row['heading'],'physical':obs})
    return out


def count_tables():
    tables=[]
    for family in ('COUNT_ACCESS_V1','COUNT_ACCESS_V2'):
        rows=[]
        for path in sorted((ROOT/'resultados'/family).glob('*/MEASUREMENTS.json')):
            m=read(path);frames={f['tick']:f for f in m['frames']}
            rows.append({'id':m['case']['id'],'case':m['case'],'primary':locator(path),
                'first_read114':qualified(frames[114],1),'second_read148':qualified(frames[148],2),
                'counter10':frames[10]['counter'],
                'comparators91':frames[91]['branches'],
                'extra103':frames[103]['extra'],'extra170':frames[170]['extra'],
                'requests':len(m['requests']),'receipt_statuses':{status:sum(r['receipt']['status']==status for r in m['requests'])for status in sorted({r['receipt']['status']for r in m['requests']})}})
        tables.append({'family':family,'preparations':len(rows),'rows':rows})
    causal=[]
    for path in sorted((ROOT/'resultados/COUNT_ACCESS_CAUSAL_RESTORE').glob('*/MEASUREMENTS.json')):
        m=read(path)
        causal.append({'id':m['id'],'mode':m['mode'],'primary':locator(path),
            'first_read114':len(m['qualified']['114']),'second_read148':len(m['qualified']['148']),
            'physical_equal_reference':m['final_physical_equal_reference'],
            'receipts_equal_reference':m['receipts_equal_reference'],
            'parent_unchanged_for_fork':m['parent_unchanged_for_fork']})
    return {'designs':tables,'causal_and_crossprocess':causal,
        'interpretation':'V1 signed access repairedTWO/ONE_A but excludedzeroXandlostB-only. V2 includesallthreefixedroutesfromT0, noobservedbankselection. Positivecalibratedassociation/retention is not doseinvariantcardinality or a jointONE/TWOlexicon. Actorload3 remains an adversarialconfound, not silently classified.',
        'semantic_recommendation':'ONE/TWO may support boundedE2 operational association in auxiliary lives ifcausalchecks pass. Reservedstates demonstrate parameterinvariance, not generalNSMsemantics. RootmustadjudicateE1integrationseparately.'}


def perspective_tables():
    directory=ROOT/'resultados/REL_PERSPECTIVE_AUX_V1';rows=[];all_data={}
    for path in sorted(directory.glob('*/MEASUREMENTS.json')):
        m=read(path);all_data[m['case']['id']]=m
        frames={f['tick']:f for f in m['frames']}
        rows.append({'id':m['case']['id'],'primary':locator(path),'references':m['case']['references'],
            'current_effects':m['case']['effects'],'actor_metadata_not_input':m['case']['auditor_actor_labels'],
            'responses':{str(t):frames[t]['observers']for t in(70,137,204)},
            'independent_new_physical_preparation':m['independent_new_physical_preparation']})
    pair=None
    a=all_data.get('RP_C04_EQUAL_EFFECT_ACTOR_A');b=all_data.get('RP_C05_EQUAL_EFFECT_ACTOR_B')
    if a and b:
        pair={'same_all_frame_physical_hashes':[f['physical']for f in a['frames']]==[f['physical']for f in b['frames']],
              'same_receipts':a['requests']==b['requests'],
              'same_local_observations':[f['observers']for f in a['frames']]==[f['observers']for f in b['frames']],
              'claim':'Actorlabels differ only for auditor; neitherorganismhasphysicalinformationtodistinguishtheseactorsunderthisinterface. Notuniversalv27limit.'}
    return {'rows':rows,'equal_effect_rolelabel_counterexample':pair,
        'interpretation':'Instrumented localcalibrations change contextualresponse to identicalcurrenteffectinputs. Invertingcalibration reverseswhichobservermatches. This is relativeeffectfingerprintcomparison, NOTnativeaction, learnedproprioception, causalidentity, deicticYO/TU, or selfawareness.',
        'NSM_I_YOU_recommendation':'E0; execution is partialnativecontextbinding and a valid informationindistinguishabilitycounterexample, not self/otheracquisition.'}


def two_memory_tables():
    tables=[]
    for family in('TWO_MEMORY_PILOT','TWO_MEMORY_CONFIRMATORY'):
        rows=[]
        for path in sorted((ROOT/'resultados'/family).glob('*/MEASUREMENTS.json')):
            m=read(path);frames={f['tick']:f for f in m['frames']};case=m['case'];reads=m['geometry'].get('protocol',{}).get('readers',[71,138,205]);trials=[]
            for t in reads:
                pre=frames[t];out=frames[t+1]['center'];r=pre['reference'];o=pre['object']
                valid_operands=(r['active']and o['active']and r['semantic']==o['semantic']==1 and r['direction']==o['direction']==[0,1,0]and r['s_reg']==case['reference']+5 and o['s_reg']==case['remembered_object']+5)
                difference=case['reference']-case['remembered_object'];expected=[(difference>0)-(difference<0),0,0]
                valid_response=out['active']and out['semantic']==1 and out['s_reg']==7 and out['direction']==expected
                trials.append({'pre_tick':t,'output_tick':t+1,'R':r,'O':o,'output':out,'both_operand_criterion':valid_operands,
                    'response_criterion':valid_response,'joint_criterion':valid_operands and valid_response})
            rows.append({'id':case['id'],'case':case,'primary':locator(path),'trials':trials,
                'joint_passed':sum(t['joint_criterion']for t in trials),'denominator':len(trials),
                'actual_inputs':[{'port':r['port'],'payload':r['payload'],'tick':r['tick'],'status':r['receipt']['status']}for r in m['requests']]})
        tables.append({'family':family,'preparations':len(rows),'rows':rows})
    causal=[]
    for path in sorted((ROOT/'resultados/TWO_MEMORY_CAUSAL_RESTORE').glob('*/MEASUREMENTS.json')):
        m=read(path)
        causal.append({'id':m['id'],'mode':m['mode'],'operand':m['operand'],'primary':locator(path),
            'outputs':{str(f['tick']):f['center']for f in m['frames']if f['tick']in(72,139,206)},
            'physical_equal_reference':m['final_physical_equal_reference'],'receipts_equal_reference':m['receipts_equal_reference'],
            'parent_unchanged':m['parent_unchanged']})
    return {'designs':tables,'causal_and_restore':causal,
        'formula':'Before each reader: both acquiredR/O must equal experience+formatcue5, active normal and direction+Y. Nexttickresponse must be active normal load7 dx=sign(R-O). Allthreeconditionsrequired, outputaloneinsufficient.',
        'interpretation':'A prepared native comparison jointly uses two separatelyacquired circulatingcontents without currentobjectreinjection. This is functionalcomposition of storedoperands, not learnedcomparisonlaw, genericconditional/THINKsemantics, or arbitrarygrammar.'}


def presence_tables():
    tables=[]
    for family in('PRESENCE_COUNT_PILOT','PRESENCE_COUNT_GEOMETRY_V2','PRESENCE_COUNT_V3','PRESENCE_COUNT_DOSE_RESERVE'):
        rows=[]
        for path in sorted((ROOT/'resultados'/family).glob('*/MEASUREMENTS.json')):
            m=read(path);frames={f['tick']:f for f in m['frames']};n=len(m['case']['contacts']);trials=[]
            for index,tick in enumerate((10,77,144)):
                obs=frames[tick]['collector'];expected=5+7*n+7*index
                direction_ok=(obs['direction'][2]==1 if index==0 else obs['direction'][1:]==[1,1]if index==1 else obs['direction'][1:]==[1,0])
                qualified=obs['active']and obs['semantic']==1 and obs['s_reg']==expected and direction_ok
                trials.append({'tick':tick,'raw_observation':obs,'declared_expected_load':expected,'expected_event_count':n,
                    'native_qualified':qualified,'formula_value':(obs['s_reg']-5-7*index)/7,
                    'formula_scope':'AUDITOR arithmetic only; fractional/out-of-domain values not converted to a count answer'})
            rows.append({'id':m['case']['id'],'case':m['case'],'primary':locator(path),'trials':trials,
                'normalizer_observations':{str(t):frames[t]['normalizers']for t in(6,7,8)},
                'extra103':frames[103]['extra'],'extra170':frames[170]['extra'],
                'query_receipts':[r for r in m['requests']if r['port'].startswith('presence.query')]})
        tables.append({'family':family,'preparations':len(rows),'rows':rows})
    causal=[]
    for path in sorted((ROOT/'resultados/PRESENCE_CAUSAL_RESTORE').glob('*/MEASUREMENTS.json')):
        m=read(path);causal.append({'id':m['id'],'mode':m['mode'],'primary':locator(path),
            'observed_counts':{str(f['tick']):f['collector']for f in m['frames']if f['tick']in(10,77,144)},
            'parent_unchanged':m['parent_unchanged'],'physical_equal_reference':m['final_physical_equal_reference'],
            'receipts_equal_reference':m['receipts_equal_reference']})
    traces=[]
    for name in('PRESENCE_TRACE_ONE_A','PRESENCE_TRACE_ONE_A_TO76'):
        path=ROOT/'resultados'/name/'MEASUREMENTS.json'
        if path.exists():
            m=read(path);traces.append({'primary':locator(path),'new_inputs':m['new_inputs'],
                'fixed_plus_heading':[{k:v for k,v in {'tick':f['tick'],'observation':next(p['observation']for p in f['fixed_candidate_paths']if p['initial_heading']==1)}.items()}for f in m['frames']],
                'coverage':m['coverage']})
    reconstruction_path=ROOT/'resultados/PRESENCE_LOCAL_RECONSTRUCTION/MEASUREMENTS.json'
    reconstruction=None
    if reconstruction_path.exists():
        rm=read(reconstruction_path)
        reconstruction={'primary':locator(reconstruction_path),'branches':[{'tick':b['post_tick'],'sources':b['sources_pointing_to_target'],
            'predicted_raw':b.get('predicted_raw_before_step'),'post':b['post'],'raw_match':b['predicted_raw_equal_post'],
            'clock_match':b['clock_rule_equal']}for b in rm['branches']]}
    return {'designs':tables,'causal_and_restore':causal,'passive_diagnostic_continuations':traces,'local_branch_reconstruction':reconstruction,
        'interpretation':'Native positive contact operands are normalized by equal supplied readers7 and converge as0/1/2 emissions without hostcounting. Firstcount10 can be dose-robust while later access fails. V1 anchors stabilized collector; V2 recurrentteachers and occupiedqueries causedrecount; V3 preservesTWO in its domain butONE/NONE still diverge. These are separate preparations and all adverses are retained.',
        'not_claimed':'No abstract unbounded cardinality, semantic mastery ofONE/TWO, trained normalization law, or integration inrootE1 fromthisauxiliary alone.'}


def remote_tables():
    tables=[]
    for family in('PRESENCE_REMOTE_PILOT','PRESENCE_REMOTE_ACCESS_V2','PRESENCE_REMOTE_V3','PRESENCE_REMOTE_RESERVE'):
        rows=[]
        for path in sorted((ROOT/'resultados'/family).glob('*/MEASUREMENTS.json')):
            m=read(path);frames={f['tick']:f for f in m['frames']};n=len(m['case']['contacts']);expected_reference=5+7*n;trials=[]
            for pre_tick,threshold in((89,16),(156,8),(223,5)):
                qualifying=[];all_banks=[]
                for before,after in zip(frames[pre_tick]['remote'],frames[pre_tick+1]['remote']):
                    r=before['reference'];o=before['object'];out=after['output'];delta=expected_reference-threshold;expected=[(delta>0)-(delta<0),0,0]
                    reference_ok=r['active']and r['semantic']==1 and r['s_reg']==expected_reference and r['direction']==[0,1,0]
                    object_ok=o['active']and o['semantic']==1 and o['s_reg']==threshold and o['direction']==[0,1,0]
                    output_ok=out['active']and out['semantic']==1 and out['s_reg']==7 and out['direction']==expected
                    bank={'heading':before['heading'],'reference':r,'object':o,'output':out,'reference_criterion':reference_ok,
                          'object_criterion':object_ok,'output_criterion':output_ok,'joint_criterion':reference_ok and object_ok and output_ok}
                    all_banks.append(bank)
                    if bank['joint_criterion']:qualifying.append(bank)
                trials.append({'pre_tick':pre_tick,'output_tick':pre_tick+1,'threshold':threshold,'all_banks':all_banks,
                    'qualifying_bank_count':len(qualifying),'native_joint_use':bool(qualifying)})
            rows.append({'id':m['case']['id'],'case':m['case'],'primary':locator(path),'expected_event_count':n,
                'expected_acquired_reference':expected_reference,'trials':trials,'joint_passed':sum(t['native_joint_use']for t in trials),'denominator':len(trials),
                'source10':frames[10]['source_collector'],'extra103':frames[103]['extra'],'extra170':frames[170]['extra'],
                'acquisition23':frames[23]['remote']})
        tables.append({'family':family,'preparations':len(rows),'rows':rows})
    causal=[]
    for path in sorted((ROOT/'resultados/PRESENCE_REMOTE_CAUSAL_RESTORE').glob('*/MEASUREMENTS.json')):
        m=read(path);causal.append({'id':m['id'],'mode':m['mode'],'primary':locator(path),
            'outputs':{str(f['tick']):f['remote']for f in m['frames']if f['tick']in(90,157,224)},
            'physical_equal_reference':m['final_physical_equal_reference'],'receipts_equal_reference':m['receipts_equal_reference'],
            'parent_unchanged_for_fork':m['parent_unchanged_for_fork']})
    trace_path=ROOT/'resultados/PRESENCE_REMOTE_MIDDLE_TRACE/MEASUREMENTS.json';trace=None
    if trace_path.exists():
        tm=read(trace_path);trace={'primary':locator(trace_path),'middle_reference_path':[{'tick':f['tick'],'physical':f['fixed_reference_paths'][1]['observation']}for f in tm['frames']]}
    return {'designs':tables,'causal_and_restore':causal,'passive_middle_trace':trace,
        'formula':'Remote reference must equal actualnativecount5+7n. For eachfixedbank actualthreshold16/8/5 and fixedreader7 produce sign(reference-threshold). Audit allbanks; no bankselectedbyobservedtarget beforeinput.',
        'interpretation':'Native capture12 prevents the known firstshadowencounter. V1invalidtransport, V2ONEretainedbutmiddlezerocurrentchangesreference71, V3allfirstusespositive andONEbothrolesretained3/3withnewdoses/states. TWO/NONEonlyfirstusevalid; laterZresidual is neither erased nor recoded. Cutalllearnedhubs23 removes lateroutputs; shams/restores225exact. AllareauxiliarynewT0worlds, notsubjectMAIN.'}


def action_trace_tables():
    tables=[]
    for family in ('ACTION_TRACE_V1_COMPLETE','ACTION_TRACE_V2'):
        rows=[]
        for path in sorted((ROOT/'resultados'/family).glob('A*.json')):
            m=read(path);frames={f['tick']:f for f in m['frames']};actor=m['case']['actor'];other='B' if actor=='A' else 'A'
            def valid(o,load,direction):return o['active'] and o['semantic']==1 and o['s_reg']==load and o['direction']==direction
            load=m['geometry']['command_load'];trials=[]
            for tick in (16,31):
                r=frames[tick]['readers']
                ok=valid(r[actor],7,[0,0,1]) and valid(r[other],7,[0,0,0]) and valid(r['C'],7,[0,0,1])
                trials.append({'tick':tick,'readers':r,'joint_criterion':ok})
            source=frames[1]['sites'][actor]
            emitted_site=list(m['geometry']['sites'][actor]);emitted_site[0]+=(1 if actor=='A' else -1);emitted_site[0]%=67
            emitted=next(o for o in frames[1]['Moore27'][actor] if o['site']==emitted_site)
            rows.append({'id':m['case_id'],'case':m['case'],'primary':locator(path),'source_trace1':source,'emitted1':emitted,
                         'native_split_criterion':valid(source,load,[0,0,0]) and valid(emitted,load,[1 if actor=='A' else -1,0,0]),
                         'common_feedback11':frames[11]['sites']['C'],'trials':trials,'passed':sum(t['joint_criterion']for t in trials),
                         'denominator':2,'requests':m['receipts']})
        pairs=[]
        for left,right in (('AT_P01_A','AT_P02_B'),('AT_H01_NEW_DOSE_A','AT_H02_NEW_DOSE_B'),('AV2_P01_A','AV2_P02_B'),('AV2_H01_NEW_DOSE_A','AV2_H02_NEW_DOSE_B')):
            ls=[r for r in rows if r['id']==left];rs=[r for r in rows if r['id']==right]
            if ls and rs:
                pairs.append({'A':left,'B':right,'full_common_feedback11_equal':ls[0]['common_feedback11']==rs[0]['common_feedback11']})
        tables.append({'family':family,'preparations':len(rows),'rows':rows,'matched_pairs':pairs})
    causal=[]
    for path in sorted((ROOT/'resultados/ACTION_TRACE_CAUSAL_RESTORE').glob('AV2_*.json')):
        m=read(path);reference=read(ROOT/'resultados/ACTION_TRACE_V2'/(m['parent_case']+'.json'));actor=reference['case']['actor']
        ref_frames={f['tick']:f for f in reference['frames']};same_consequence=all(f['sites']['C']==ref_frames[f['tick']]['sites']['C'] for f in m['frames'])
        same_own_readers=all(f['readers'][actor]==ref_frames[f['tick']]['readers'][actor] for f in m['frames'])
        causal.append({'id':m['id'],'mode':m['mode'],'primary':locator(path),'interventions':m['interventions'],
                       'readers':{str(f['tick']):f['readers'] for f in m['frames'] if f['tick']in(16,31)},
                       'common_consequence_equal_reference':same_consequence,'own_readers_equal_reference':same_own_readers,
                       'parent_unchanged':m['parent_unchanged'],'full_state_equal_reference':m['full_state_equal_parent_reference'],
                       'receipts_equal_reference':m['receipts_equal_parent_reference']})
    return {'designs':tables,'causal_and_restore':causal,
            'formula':'Same acting-source input c produces stationary source trace c/0 plus emitted c/(±X) at1. Common feedback at11 must have full equality in opposite acting-role pair. All identical c7 readers: own+Z, other0(active), common+Z at16/31.',
            'interpretation':'A prepared native emitter bifurcates locally under two v27 branches; retained causal-origin trace is functionally accessible despite identical common consequence. Selective local tracecut preserves common consequence but changes ownreader; consequencecut preserves ownreader. Command source chosen by external protocol; no learned initiative, agency attribution, YO/TU semantics or full mind follows.'}


def reflection_tables():
    designs=[]
    for family,arrival_tick,operator_tick in (('CONTENT_REFLECTION_V1',74,75),('CONTENT_REFLECTION_V2',81,82)):
        rows=[]
        for path in sorted((ROOT/'resultados'/family).glob('R*.json')):
            m=read(path);frames={f['tick']:f for f in m['frames']};case=m['case'];delta=case['reference']-case['object'];side=(delta>0)-(delta<0)
            def valid(o,load,dr):return o['active'] and o['semantic']==1 and o['s_reg']==load and o['direction']==dr
            operands=valid(frames[71]['reference'],case['reference']+5,[0,1,0]) and valid(frames[71]['object'],case['object']+5,[0,1,0])
            content=valid(frames[72]['center'],7,[side,0,0]);arrive=None;operate=None
            if side:
                arrive=next(b['material'] for b in frames[arrival_tick]['reflection'] if b['side']==side)
                operate=next(b['material'] for b in frames[operator_tick]['reflection'] if b['side']==side)
            arrival_ok=bool(side and valid(arrive,7,[side,0,0]));operator_ok=bool(side and valid(operate,7,[-side,0,0]))
            later=[]
            for t in (138,205):
                f=frames[t];o=frames[t+1]['center']
                qualified=valid(f['reference'],case['reference']+5,[0,1,0]) and valid(f['object'],case['object']+5,[0,1,0]) and valid(o,7,[side,0,0])
                later.append({'tick':t+1,'R':f['reference'],'O':f['object'],'output':o,'joint_criterion':qualified})
            rows.append({'id':m['case_id'],'case':case,'primary':locator(path),'R71':frames[71]['reference'],'O71':frames[71]['object'],
                         'operands_criterion':operands,'content72':frames[72]['center'],'content_criterion':content,
                         'arrival':arrive,'arrival_criterion':arrival_ok,'operator_post':operate,'operator_criterion':operator_ok,
                         'joint_criterion':operands and content and arrival_ok and operator_ok,'later':later,
                         'rejected_receipts':[r for r in m['receipts'] if r['receipt']['status']!='applied']})
        designs.append({'family':family,'preparations':len(rows),'rows':rows})
    causal=[]
    for path in sorted((ROOT/'resultados/CONTENT_REFLECTION_CAUSAL_RESTORE').glob('RR_*.json')):
        m=read(path);causal.append({'id':m['id'],'mode':m['mode'],'primary':locator(path),'interventions':m['interventions'],
                                  'predictions_before_82':m['predictions_before_82'],'parent_unchanged':m['parent_unchanged'],
                                  'outputs82':next(f['reflection'] for f in m['frames'] if f['tick']==82),
                                  'full_state_equal_reference':m['full_state_equal_reference'],'receipts_equal_reference':m['receipts_equal_reference']})
    return {'designs':designs,'causal_and_restore':causal,
            'formula':'Require acquired R/O at71, original c7 sign(R-O) at72, same c7 at remoteP81, and c7 opposite sign at82. Counterload21 is prepared. All four predicates required; absence is not decoded as negation.',
            'interpretation':'A finite prepared active contrariety operator transforms a native consequence of two acquired operands. V1 invalidated its input by stabilizing old teachers; V2 isolates first operation remotely, but third original comparison later fails under both on/off control. No learned NO, linguistic negation over contents, operator choice or associated lexical form is claimed.'}


def main():
    data={'schema':'CPC9.semantics.aux.recalculation.v1','auditor_source_sha256':sha(__file__),
          'count_access':count_tables(),'perspective':perspective_tables(),'two_memories':two_memory_tables(),'presence_normalized_count':presence_tables(),'remote_native_count':remote_tables(),'action_origin_trace':action_trace_tables(),'active_content_reflection':reflection_tables(),
          'no_engine_imports':True,'automatic_NSM_adjudication':False,
          'separation':'Alllivesinthisfrontareauxiliary; integrationintoE1requiresrootprimaries. Countsaretasks/readingsnotindependentconcepts.'}
    path=ROOT/'revision/FRONT_SEMANTICS_CALCULOS.json'
    path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps({'path':str(path),'sha256':sha(path),'count_preparations':sum(t['preparations']for t in data['count_access']['designs']),
        'perspective_preparations':len(data['perspective']['rows']),
        'two_memory_preparations':sum(t['preparations']for t in data['two_memories']['designs'])}))


if __name__=='__main__':main()
