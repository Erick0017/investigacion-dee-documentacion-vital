"""Post-trajectory calculations; does not create or mutate a Runtime."""
from collections import Counter
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import ROOT,put,sha


def main():
    directory=ROOT/'resultados/selective_native';rows=[];measurements={};receipts=Counter();fresh=Counter();snapshots=0
    for path in sorted(directory.glob('*/MEASUREMENTS.json')):
        m=json.loads(path.read_text(encoding='utf8'));cid=m['case']['id'];measurements[cid]=m
        obs={r['tick']:r for r in m['rows']}
        joint=[{'bank':r['name_bank'],'value':r['value'],'tick':r['tick']} for r in m['opaque_name_reads'] if r['coverage']]
        selection=[{'bank':r['bank'],'value':r['physical']['direction'][1],'load':r['physical']['s_reg']} for r in m['native_selected_information']]
        joint_match=sum(any(r['bank'].split('.')[0]==s['bank'] and r['value']==s['value'] for s in selection) for r in joint)
        for q in m['requests']:
            receipts[q['receipt']['status']]+=1
            if not q['inherited_from_parent']:fresh[q['receipt']['status']]+=1
        for snapshot in m['snapshots']:
            stored=path.parent/snapshot['path'];assert stored.is_file() and sha(stored)==snapshot['sha256'];snapshots+=1
        rows.append({'case_id':cid,'group':m['case']['group'],'history':m['case']['history'],'current_actual':m['case']['actual'],
            'path':str(path.relative_to(ROOT)),'sha256':sha(path),'schema':m['schema'],
            'preparations':m['preparations'],'diagnostic_forks':m['diagnostic_forks'],'parent':m['parent'],
            'comparison_emission5':obs.get(5,{}).get('body',{}).get('emission'),
            'question19_covered':len(m['native_questions']) if 19 in obs else None,
            'selected_own_memory70':selection,'native_actions72':len(m['native_actions']),
            'later_opaque_sign142':joint,'sign_joint_bank_and_value_match_to_information70':joint_match,
            'lower_forms_functional_use':m['calculations']['lower_repertoire'],
            'query_receipts':dict(Counter(r['receipt']['status'] for r in m['opaque_name_reads']+m['lower_repertoire_reads'])),
            'snapshot_count':len(m['snapshots']),'initial_source_load':m['geometry']['body']['prepared_scalar_source']['initial_load'],
            'final_physical':m['final_physical'],'elapsed_seconds':m['elapsed_seconds']})
    parent=measurements['SEL_P21_AB'];cut=measurements['SEL_C21_CUT'];sham=measurements['SEL_C22_SHAM']
    assert parent['final_physical']==sham['final_physical']
    physical_sham={'RAW_sha256_equal':parent['final_physical']['raw_sha256']==sham['final_physical']['raw_sha256'],
        'clocks_sha256_equal':parent['final_physical']['clock_sha256']==sham['final_physical']['clock_sha256'],
        'tick_equal':parent['final_physical']['tick']==sham['final_physical']['tick'],
        'operational_identity_and_diagnostic_log':'Different intentionally; compare physical arrays separately from wrapper metadata'}
    summary={'schema':'CPC7.selective_native.analysis.v1','generated_by':'src/analyze_selective_native.py',
        'data_source':'Primary MEASUREMENTS only; all comparisons after the trajectories; no engine called',
        'cases':rows,'counts':{'records':len(rows),'independent_preparations':sum(r['preparations'] for r in rows),
            'diagnostic_forks':sum(r['diagnostic_forks'] for r in rows),'snapshot_hashes_verified':snapshots,
            'request_receipts_including_inherited':dict(receipts),'new_request_receipts':dict(fresh),
            'covered_opaque_sign_responses142':sum(len(r['later_opaque_sign142']) for r in rows),
            'independent_preparations_with_covered_sign142':sum(bool(r['later_opaque_sign142']) and bool(r['preparations']) for r in rows),
            'distinct_opaque_sign_protocols':1,'general_NSM_primitives_proven':0},
        'causal':{'formed_question_cut':{'parent':'SEL_P21_AB','cut':'SEL_C21_CUT','sham':'SEL_C22_SHAM',
            'fields':'Only RAW in a complete diagnostic fork20 at two fixed candidate question sites; no clocks changed, no branch selected from content',
            'parent_unchanged_checks':all(m['diagnostic_edits'][0]['parent_unchanged'] for m in (cut,sham)),
            'sham_final_full_array_equivalence':physical_sham,
            'cut_information70':len(cut['native_selected_information']),'cut_actions72':len(cut['native_actions']),
            'cut_sign142':cut['calculations']['opaque_covered'],
            'specificity':'Fourteen other acquired correspondences retain functional queries204/338 in cut and sham; all common action resources remain scheduled and receipts are included'},
            'name_pairing':{'paired':'SEL_P21_AB','unpaired':'SEL_N21_UNPAIRED','omitted':'SEL_N22_OMITTED',
                'observation':'Unpaired/omitted cues preserve native question, own-bank information and native use; neither yields covered sign-only response142.'},
            'same_interface_different_own_experience':{'AB':['SEL_P21_AB','SEL_R301_AB'],'BA':['SEL_P22_BA','SEL_R411_BA'],
                'observation':'Selected bank and native-question route fixed within each pair; opposite acquired bank direction changes information70 and sign-only142. Reserved query loads differ as declared.'}},
        'counterexamples':{'matching_comparison':['SEL_P11_AB','SEL_P12_BA'],
            'matching_scope':'These exposed a matching actual event, not a discrepancy. No moving X-question and no later own-memory use is expected from this specific request mechanism.',
            'reserve_R301_access':{'primary':'SEL_R301_AB','acquisition':'All sixteen reference records present at first acquired boundaries3/137; all new experience receipts134 Applied.',
                'observations':'Eight of fourteen lower-bank first probes204 are Applied but show only common query load5 and direction[-1,0,0], not a covered learned direction. Those eight next probes338 are RejectedOccupied. Six remain covered at both windows.',
                'scope':'Observed history-dependent interference/access counterexample in this integrated geometry. The causal intervening route and persistence of those lost functions are not localized by this panel.'}},
        'domain':{'N':67,'initial_material_sites':15,'interfaces':65,'acquired_candidate_banks':16,
            'fixed_low_panel':14,'native_question_candidates':2,'per_individual_selected_banks_used70':1,
            'preparation':'Body semantic4 source load0 set beforeT0; fixed comparison/opportunities, external paired cue and new lower-bank experiences. No MAIN clearing or reset.',
            'time':'Prediction5; actual sensor11/comparison15; question19; own-bank read70; use72; new cue association75; second acquisition134; sign query139/read142; lower panels201/read204 and335/read338.',
            'attribution':'One continuing U0 Runtime; own-bank choice determined by physical comparison of history-dependent emission and actual event, not host lookup. Prepared finite route, not a general uncertainty detector, utility policy, or autonomous linguistic discovery.',
            'retention':'Fourteen lower correspondences are a mix of six older plus eight new, with two physical output classes. Nine records (seven preparations plus two forks) show14/14 twice; the reserved counterexample shows6/14. Unselected high memory has not been later queried in that same MAIN.',
            'meaning':'A later opaque sign reproduces the selected directional relation. This does not credit65 interface ports as65 meanings, nor abstract NSM semantics.'}}
    put(directory/'ANALYSIS.json',summary)
    put(directory/'INDEX_ALL.json',{'schema':'CPC7.primary_evidence.index.v1','cases':[{k:r[k] for k in ('case_id','group','path','sha256','schema','preparations','diagnostic_forks','parent')} for r in rows]})
    for version,ids in (('V2',('SEL_P11_AB','SEL_P12_BA')),('V3',('SEL_P21_AB','SEL_P22_BA'))):
        put(directory/('INDEX_'+version+'_pilot.json'),{'schema':'CPC7.primary_evidence.index.v1',
            'derivation':'Rebuilt from exact primary measurements, not additional trajectories',
            'cases':[{k:r[k] for k in ('case_id','group','path','sha256','schema','preparations','diagnostic_forks','parent')} for r in rows if r['case_id'] in ids]})
    print(json.dumps(summary['counts']))


if __name__=='__main__':main()
