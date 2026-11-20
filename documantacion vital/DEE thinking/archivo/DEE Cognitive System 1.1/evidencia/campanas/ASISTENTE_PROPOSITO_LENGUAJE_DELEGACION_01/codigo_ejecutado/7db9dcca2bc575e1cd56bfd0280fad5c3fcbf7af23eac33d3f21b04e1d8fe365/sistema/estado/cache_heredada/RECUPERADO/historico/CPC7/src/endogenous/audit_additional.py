"""External calculations of fallback, regulation and source calibration."""
from pathlib import Path
import json,sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]));sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import ROOT,put,sha,digest,record,gate
from integrated import Session
import comparison_need,audit

BASE=ROOT/'resultados/endogenous'


def rows(folder):
    result=[]
    for path in sorted((BASE/folder).glob('*/MEASUREMENTS.json')):
        value=json.loads(path.read_text(encoding='utf-8'));case=value['case']
        result.append({'id':case['id'],'phase':case['phase'],'primary':path.relative_to(ROOT).as_posix(),'sha256':sha(path),
            'questions':value.get('native_questions',[]),'information':value.get('received_information',[]),
            'use':value.get('later_physical_use',[]),'body_delta5':value['rows'][5]['body']['delta'],
            'body_final_delta':value['rows'][-1]['body']['delta'],'snapshots':value['snapshots']})
    return result


def fallback():
    primary=rows('missing_actual_fallback')
    parent=Session.load(BASE/'missing_actual_fallback/FALL_D01_MISSING_ACTUAL/T19.deetsnap')
    parent.advance_to(20);before=digest(parent.world);clocks=parent.world.runtime.clock_copy();raw=parent.world.runtime.raw_copy()
    import dee_thinking as d
    edits=[];sites=[];g=parent.geometry['need']
    for name,b in g['branches'].items():
        if not b['dx']:continue
        site=comparison_need.moved(b['request_site'],(b['dx'],0,0),1);value=record(parent.world,site)
        if value['active'] and value['direction']==[b['dx'],0,0]:
            e=d.ResearchStateEdit();e.coordinate=d.Coordinate(*site);e.raw=0;e.label='Explicit fallback request diagnostic';edits.append(e);sites.append({'branch':name,'site':site,'before':value})
    child=parent.world.diagnostic_fork(edits,True);diff=sum(a!=b for a,b in zip(raw,child.runtime.raw_copy()))
    same_clock=clocks==child.runtime.clock_copy();same_parent=digest(parent.world)==before
    cut_rows=[]
    for tick in (24,29,35):
        child.run_until(tick);cut_rows.append(comparison_need.capture(child,g))
    parent.advance_to(35)
    full=json.loads((BASE/'missing_actual_fallback/FALL_D01_MISSING_ACTUAL/MEASUREMENTS.json').read_text(encoding='utf-8'))
    full_equal=digest(parent.world)==full['final_physical']
    info=[x for x in cut_rows[0]['source_contacts'].values() if x['active'] and x['direction'][0] in (-1,1) and x['direction'][1] in (-1,1) and x['direction'][2]==0]
    use=[x for x in cut_rows[1]['later_use'].values() if x['active'] and x['direction'][0] in (-1,1) and x['direction'][1] in (-1,1) and x['direction'][2]==1]
    technical={'diagnostic_RAW_sites_changed':diff,'clock_arrays_equal':same_clock,'parent_unchanged':same_parent,
               'restored_pending_inputs_full_future_equal':full_equal}
    assert diff==1 and same_clock and same_parent and full_equal
    put(BASE/'FALLBACK_SUMMARY.json',{'schema':'CPC7.fallback.audit.v1','cases':primary,
        'causal_diagnostic':{'sites':sites,'intervention_tick':20,'source_information24':info,'later_use29':use,'rows':cut_rows,
            'technical':technical,'counting':'One counterfactual fork from a saved world, not a new independently prepared participant.'},
        'measured_scope':'The original-z path issues a native question when a represented expectation lacks the finite on-time actual report. Current match suppresses it; current mismatch uses the original branch. Reader omission is still a separate silent state.',
        'interpretation_revision':'v1 lacked this original-z opportunity and remained silent without actual. v2 is a new prepared interface, not a retroactive discovery that v1 already detected absence.'})


def regulation():
    result=[]
    for folder in ('need_regulation','need_regulation_v2','need_regulation_v3'):
        for row in rows(folder):
            path=ROOT/row['primary'];m=json.loads(path.read_text(encoding='utf-8'))
            trace=json.loads((path.parent/'REGULATION_TRACE.json').read_text(encoding='utf-8'))
            active_after27=sum(o['active'] and o['direction']==[0,1,-1] for t in trace['rows'] if t['tick']>=27 for o in t['normalizers'].values())
            row.update({'guard_mode':m['case']['guard_mode'],'guard_schema':m['geometry']['need']['regulation']['schema'],
                'nominal_negative_Z_records_24_to35':trace['retained_negative_Z_nominal_records_24_to35'],
                'nominal_negative_Z_records_27_to35':active_after27,
                'selective_replay_same_physics35':trace['physical_equal_at35'],
                'trace':(path.parent/'REGULATION_TRACE.json').relative_to(ROOT).as_posix()})
            continuation=path.parent/'GLOBAL_TRAFFIC_AND_CONTINUATION.json'
            if continuation.exists():
                c=json.loads(continuation.read_text(encoding='utf-8'));row['global_traffic']=[{'tick':v['tick'],
                    'active_Z_low_planes':v['Z_record_panel']['active_nonzero_Z_in_lexical_planes_1_to31']} for v in c['continuation_rows']]
                row['continuation']={'physical':c['snapshot100']['physical'],'primary':continuation.relative_to(ROOT).as_posix(),
                                     'counting':'Same individual continued35->100 without new input; not an independent preparation.'}
            result.append(row)
    put(BASE/'REGULATION_SUMMARY.json',{'schema':'CPC7.regulation.audit.v1','cases':result,
        'interpretive_revisions':[
            {'design':'v1 barrier at residual step4','observation':'Matching-branch barrier coincides with comparison hub and suppresses the desired question too','current_reading':'An adverse apparatus result; not accepted as selective regulation.'},
            {'design':'v2 barrier at residual step8','observation':'Question/source/use retained and sampled nominal negative-Z mediators absent after interception27','current_reading':'Selective fixed interface maintenance within observed branches, not experience-dependent attention.'},
            {'design':'v3 adds four possible uncombined actual-report absorbers','observation':'Native functions retained but global Z-directed traffic still reaches lower planes','current_reading':'Local ray protection is not closure of all flows; body-source contrast is needed before attributing remaining traffic.'}],
        'scope':'Native fixed absorbers, finite local causal windows and global current records. No universal source suppression or unique genealogy from load equality.'})


def source():
    seven_path=BASE/'body_source/BODY_SOURCE_C01_ORIGINAL_7/MEASUREMENTS.json';zero_path=BASE/'body_source/BODY_SOURCE_D01_INITIAL_0/MEASUREMENTS.json'
    seven=json.loads(seven_path.read_text(encoding='utf-8'));zero=json.loads(zero_path.read_text(encoding='utf-8'))
    a=Session.load(seven_path.parent/'T0.deetsnap');b=Session.load(zero_path.parent/'T0.deetsnap')
    raw0=a.world.runtime.raw_copy();raw1=b.world.runtime.raw_copy();differences=[i for i,(x,y) in enumerate(zip(raw0,raw1)) if x!=y]
    same_clock=a.world.runtime.clock_copy()==b.world.runtime.clock_copy();site=zero['geometry']['body']['prepared_scalar_source']['site']
    sa,sb=record(a.world,site),record(b.world,site)
    conserved_fields=all(sa[k]==sb[k] for k in ('site','state','semantic','direction','clock','active'))
    same_emission=seven['emission5']==zero['emission5']
    relation_equal=all(x['body']['delta']==y['body']['delta'] for x,y in zip(seven['rows'],zero['rows']))
    panel=[]
    for x,y in zip(seven['traffic'],zero['traffic']):
        panel.append({'tick':x['tick'],'source7_active_Z_low':x['panel']['active_nonzero_Z_in_lexical_planes_1_to31'],
                     'source0_active_Z_low':y['panel']['active_nonzero_Z_in_lexical_planes_1_to31'],
                     'denominator':'one continuing world per design, one exact state per tick; not independent repeated samples'})
    result={'schema':'CPC7.body_source.audit.v1','source7_primary':seven_path.relative_to(ROOT).as_posix(),'source0_primary':zero_path.relative_to(ROOT).as_posix(),
        'identities':{'source7_sha256':sha(seven_path),'source0_sha256':sha(zero_path)},
        'initial_RAW_changed_sites':len(differences),'initial_clock_arrays_equal':same_clock,
        'source_fields_other_than_load_conserved':conserved_fields,'before':sa,'after':sb,
        'initial_local_gates':{'source7':{k:gate(a.world,a.geometry['body'][k]) for k in ('A','B')},
                               'source0':{k:gate(b.world,b.geometry['body'][k]) for k in ('A','B')}},
        'exact_emission5_equal':same_emission,'emission5':zero['emission5'],
        'same_measured_delta_trajectory0to100':relation_equal,
        'source7_delta5':seven['rows'][5]['body']['delta'],'source0_delta5':zero['rows'][5]['body']['delta'],
        'source7_delta100':seven['rows'][100]['body']['delta'],'source0_delta100':zero['rows'][100]['body']['delta'],
        'query_receipts':{'source7':seven['requests'],'source0':zero['requests']},'traffic':panel,
        'measured_scope':'One designer-prepared immutable scalar source load changed beforeT0 while geometry, active presence, semantic, state, clock and inputs remain. Initial emission and measured relative history remain; Z-directed lower-plane traffic differs in the sampled window.',
        'retention_limit':'The second physical reader request69 is rejected_occupied. Current emission72 is not a newly admitted query result. No automatic indefinite renewable reader or learned homeostasis is claimed.'}
    put(BASE/'BODY_SOURCE_SUMMARY.json',result)
    assert len(differences)==1 and same_clock and conserved_fields and same_emission


if __name__=='__main__':
    audit.summaries();fallback();regulation();source()
    paths=list(BASE.glob('*/*/MEASUREMENTS.json'))
    put(BASE/'AREA_COVERAGE.json',{'schema':'CPC7.endogenous.coverage.v1','primary_measurement_files':len(paths),
        'primary_identities':[{'path':p.relative_to(ROOT).as_posix(),'sha256':sha(p),'id':json.loads(p.read_text(encoding='utf-8'))['case']['id']} for p in sorted(paths)],
        'families':['finite comparison-conditioned access, with optional missing-actual route','fixed native renewable opportunity and directional inhibition','fixed interface/source maintenance calibrations'],
        'no_new_six_way_internal_classifier':True,'no_global_semantic_verdict':True})
    print(json.dumps({'primary_files':len(paths),'summaries':['COMPARISON_SUMMARY','FALLBACK_SUMMARY','RECURRENT_SUMMARY','REGULATION_SUMMARY','BODY_SOURCE_SUMMARY']}),flush=True)
