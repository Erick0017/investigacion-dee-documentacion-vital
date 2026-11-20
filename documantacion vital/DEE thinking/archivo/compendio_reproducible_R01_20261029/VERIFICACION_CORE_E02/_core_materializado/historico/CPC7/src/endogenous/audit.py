"""External reconstruction/calculations; never feeds a participant."""
from pathlib import Path
import json,sys,time
sys.path.insert(0,str(Path(__file__).resolve().parents[1]));sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import ROOT,put,sha,digest,record,operational
from integrated import Session
import comparison_need


def summaries():
    cases=[];data={}
    for folder in ('comparison_discovery','comparison_confirm'):
        for path in sorted((ROOT/'resultados/endogenous'/folder).glob('*/MEASUREMENTS.json')):
            m=json.loads(path.read_text(encoding='utf-8'));data[m['case']['id']]=m
            body5=m['rows'][5]['body'];body35=m['rows'][-1]['body']
            cases.append({'id':m['case']['id'],'phase':m['case']['phase'],'primary':path.relative_to(ROOT).as_posix(),'sha256':sha(path),
                'body_delta5':body5['delta'],'body_delta35':body35['delta'],'body_emission5':body5['emission'],
                'native_questions':m['native_questions'],'information':m['received_information'],'later_use':m['later_physical_use'],
                'calls':len(m['requests']),'admitted':sum(x['receipt']['status']=='applied' for x in m['requests']),
                'rejections':[x for x in m['requests'] if x['receipt']['status']!='applied'],
                'diagnostic_edits':m['diagnostic_edits'],'final_physical':m['final_physical'],
                'snapshots':[{'path':(path.parent/x['path']).relative_to(ROOT).as_posix(),'sha256':x['sha256'],'tick':x['physical']['tick']} for x in m['snapshots']]})
    full=data['NEED_D02_CURRENT_MISMATCH'];cut=data['NEED_C07_FORMED_QUESTION_CUT'];sham=data['NEED_C08_FORMED_QUESTION_SHAM']
    physical=lambda m,t:next(x['physical'] for x in m['snapshots'] if x['physical']['tick']==t)
    causal={'full_cut_same_preintervention_T19':physical(full,19)==physical(cut,19),
            'full_sham_same_preintervention_T19':physical(full,19)==physical(sham,19),
            'sham_full_same_final_RAW_clock_tick':full['final_physical']==sham['final_physical'],
            'full_received_and_used':[len(full['received_information']),len(full['later_physical_use'])],
            'cut_received_and_used':[len(cut['received_information']),len(cut['later_physical_use'])],
            'scope':'A formed request is needed for this source-contact product and subsequent physical-use panel. It does not demonstrate source-state meaning or unique world-wide ancestry.'}
    limits=[
        {'auditor_condition':'current singleton match','native_result':'no horizontal request','coverage':'NEED_D01_CURRENT_MATCH;NEED_H02_MATCH_NEW_LOCATION'},
        {'auditor_condition':'current singleton discrepancy, potentially outdated expectation','native_result':'horizontal request before source contact and later use','coverage':'NEED_D02_CURRENT_MISMATCH;NEED_H01_OPPOSITE_HISTORY_NEW_LOCATION','limit':'No autonomous timestamp or general stale-information diagnosis is claimed.'},
        {'auditor_condition':'incomplete actual observation','native_result':'no request in this comparator-only family','coverage':'NEED_C04_NO_CURRENT_ACTUAL','limit':'Silence is not a statement of sufficiency; absence detector not constructed.'},
        {'auditor_condition':'reader failure/omission while A/B relation remains','native_result':'no request; the measured A/B relation remains (see exact per-case delta fields)','coverage':'NEED_C06_READER_OMITTED','limit':'External observer identifies cause; participant emits no six-way diagnosis. Do not import an earlier apparatus sign convention.'},
        {'auditor_condition':'explicit current negative information','native_result':'question plus negative-Y information and later product','coverage':'NEED_C01_NEGATIVE_CURRENT_INFORMATION','limit':'Finite binary negative report, not general logical negation or arbitrary absence.'},
        {'auditor_condition':'source not present','native_result':'request emitted; no coupled response in the panel','coverage':'NEED_C02_SOURCE_NONE','limit':'No host timeout is interpreted as native detection of absence.'}]
    put(ROOT/'resultados/endogenous/COMPARISON_SUMMARY.json',{'schema':'CPC7.native_need.audit.v1','cases':cases,
        'counts':{'independent_preparations':len(cases),'scientific_trajectory_ticks':36*len(cases),'diagnostic_forks':2,'technical_replays_are_not_replicates':True},
        'causal_contrast':causal,'six_requested_conditions_scope':limits,
        'measured_native_sequence':'Actual acquired order-body emission5 -> local physical comparison15 -> request19 -> source contact24 -> common physical use29.',
        'no_answers_written_by_auditor':True})
    recurrent=[]
    for path in sorted((ROOT/'resultados/endogenous/recurrent').glob('*/MEASUREMENTS.json')):
        m=json.loads(path.read_text(encoding='utf-8'));recurrent.append({'id':m['case']['id'],'phase':m['case']['phase'],
            'primary':path.relative_to(ROOT).as_posix(),'sha256':sha(path),'calculations':m['calculations'],
            'gate_positive_Y_ticks':m['positive_Y_gate_ticks'],'outlet_positive_Y_ticks':m['positive_Y_outlet_ticks'],
            'final_physical':m['final_physical']})
    put(ROOT/'resultados/endogenous/RECURRENT_SUMMARY.json',{'schema':'CPC7.recurrent.audit.v1','cases':recurrent,
        'counts':{'independent_preparations':len(recurrent),'ticks_per_trajectory':101},
        'scope':'Renewable native carrier opportunities and fixed directional inhibition are measured. Context/source prepared beforeT0 is not learned attention or evidence that the organization detects missing knowledge.'})
    return {'comparison_cases':len(cases),'recurrent_cases':len(recurrent),'causal':causal}


def technical():
    import dee_thinking as d
    root=ROOT/'resultados/endogenous';out=root/'technical'
    out.mkdir(parents=True,exist_ok=True)
    m=json.loads((root/'comparison_discovery/NEED_D02_CURRENT_MISMATCH/MEASUREMENTS.json').read_text(encoding='utf-8'))
    parent=Session.load(root/'comparison_discovery/NEED_D02_CURRENT_MISMATCH/T19.deetsnap');parent.advance_to(20)
    before=digest(parent.world);raw=parent.world.runtime.raw_copy();clock=parent.world.runtime.clock_copy();g=parent.geometry['need']
    captures=[comparison_need.capture(parent.world,g) for _ in range(3)]
    passive_same=digest(parent.world)==before
    edits=[];changed_sites=[]
    for name,b in g['branches'].items():
        if not b['dx']:continue
        site=comparison_need.moved(b['request_site'],(b['dx'],0,0),1)
        r=record(parent.world,site)
        if r['active'] and r['direction']==[b['dx'],0,0]:
            e=d.ResearchStateEdit();e.coordinate=d.Coordinate(*site);e.raw=0;e.label='Technical replay of exact formed-question removal';edits.append(e);changed_sites.append({'site':site,'before':r})
    child=parent.world.diagnostic_fork(edits,True)
    diffs=[i for i,(a,b) in enumerate(zip(raw,child.runtime.raw_copy())) if a!=b]
    same_clocks=clock==child.runtime.clock_copy();same_parent=digest(parent.world)==before
    child.run_until(35)
    cut=json.loads((root/'comparison_confirm/NEED_C07_FORMED_QUESTION_CUT/MEASUREMENTS.json').read_text(encoding='utf-8'))
    cut_future_equal=digest(child)==cut['final_physical']
    parent.advance_to(35);full_future_equal=digest(parent.world)==m['final_physical']
    result={'schema':'CPC7.need.technical.v1','passive_capture_no_mutation':passive_same,
        'exact_diagnostic_RAW_changed_sites':len(diffs),'declared_changed_sites':changed_sites,
        'clock_arrays_equal_after_edit':same_clocks,'parent_unchanged_after_edit':same_parent,
        'restored_pending_inputs_direct_future_equal':full_future_equal,
        'restored_question_cut_future_equal':cut_future_equal,
        'scope':'Technical replay only; no additional independent scientific preparation or six-state learned classifier.'}
    put(out/'TECHNICAL.json',result)
    assert passive_same and len(diffs)==1 and same_clocks and same_parent and full_future_equal and cut_future_equal
    return result


if __name__=='__main__':
    print(json.dumps({'summary':summaries(),'technical':technical()}),flush=True)
