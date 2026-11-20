"""Recalculate the bounded residue intervention; no Runtime is imported."""
from collections import Counter
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import ROOT,put,sha


def main():
    directory=ROOT/'resultados/residue_regulation';data={};rows=[];count_all=Counter();count_new=Counter();snapshots=0
    for path in sorted(directory.glob('*/MEASUREMENTS.json')):
        m=json.loads(path.read_text(encoding='utf8'));cid=m['case']['id'];data[cid]=m
        for q in m['requests']:
            count_all[q['receipt']['status']]+=1
            if not q['inherited_from_parent']:count_new[q['receipt']['status']]+=1
        for s in m['snapshots']:
            assert sha(path.parent/s['path'])==s['sha256'];snapshots+=1
        rows.append({'case_id':cid,'path':str(path.relative_to(ROOT)),'sha256':sha(path),'schema':m['schema'],
            'preparations':m['preparations'],'diagnostic_forks':m['diagnostic_forks'],
            'parent':m.get('parent',{}),'lower':m['calculations']['lower_repertoire'],
            'sign142':[{'bank':r['name_bank'],'value':r['value']} for r in m['opaque_name_reads'] if r['coverage']],
            'question19':len(m['native_questions']) if 'native_questions' in m else None,
            'information70':len(m['native_selected_information']) if 'native_selected_information' in m else None,
            'action72':len(m['native_actions']) if 'native_actions' in m else None,
            'initial_material_sites':m['geometry']['initial_material_sites'],'interfaces':m['geometry']['interfaces'],
            'configured_value_count':len(m['case']['bank_values']),
            'actually_exposed_first16_values':m['case']['bank_values'][:16],
            'matched_current_records76':m.get('diagnostic_edits',{}).get('matched_records') if isinstance(m.get('diagnostic_edits'),dict) else None,
            'final_physical':m['final_physical'],'snapshots':len(m['snapshots']),'elapsed_seconds':m['elapsed_seconds']})
    parent_path=ROOT/'resultados/selective_native/SEL_R301_AB/MEASUREMENTS.json';parent=json.loads(parent_path.read_text(encoding='utf8'))
    sham=data['RES_C02_SHAM'];cut=data['RES_C01_CUT'];guard=data['RES_G301_PREPARED'];offpath=data['RES_G302_OFFPATH']
    fields=('port','payload','tick','kind','id','call_tick')
    requests=lambda m:[[q.get(k) for k in fields] for q in m['requests']]
    assert parent['final_physical']==sham['final_physical']
    assert requests(parent)==requests(sham)==requests(cut)
    # These are after-the-fact neighborhood measurements, not input decisions.
    local=[]
    for row in guard['guard_observations']:
        if row['tick'] not in (79,80,82,83):continue
        for site in row['sites']:
            moving=[p for p in site['Moore27'] if p['active'] and p['semantic']==1 and any(p['direction'])]
            if moving or site['site'] in ([33,12,54],[38,5,41]):
                local.append({'tick':row['tick'],'interceptor_site':site['site'],'interceptor':site['physical'],'neighbor_moving_records':moving})
    summary={'schema':'CPC7.residue_regulation.analysis.v1','generated_by':'src/analyze_residue_regulation.py',
        'layer':'Calculations and provisional interpretation after completed trajectories; no analysis feeds MAIN',
        'parent_reference':{'path':str(parent_path.relative_to(ROOT)),'sha256':sha(parent_path),'lower':parent['calculations']['lower_repertoire']},
        'counts':{'records':len(rows),'independent_preparations':sum(r['preparations'] for r in rows),
            'diagnostic_forks':sum(r['diagnostic_forks'] for r in rows),'snapshots_hash_verified':snapshots,
            'requests_including_inherited':dict(count_all),'new_requests':dict(count_new)},
        'configuration_audit':{'supersedes':'ANALYSIS_V1_SUPERSEDED_CONFIG_CONFOUND.json',
            'error_case':'RES_G301_PREPARED','configured_values':len(guard['case']['bank_values']),
            'used_indices':'0..15, because the fixed curriculum has16 banks',
            'first16_equal_parent_and_offpath':guard['case']['bank_values'][:16]==parent['case']['bank_values']==offpath['case']['bank_values'],
            'effect':'The treatment first16 differ from the intended parent/sham atL14-L16. The old treatment14/14 versus offpath6/14 is not a history-matched causal contrast. Both primary trajectories/configurations are retained. The diagnostic cut/sham does remain exactly matched.'},
        'cases':rows,'checks':{'diagnostic_sham_final_complete_RAW_clocks_tick_equal_parent':True,
            'exact_request_port_payload_tick_kind_id_calltick_equal_parent_cut_sham':True,
            'parent_unchanged_after_fork':all(data[x]['parent']['parent_RAW_clocks_and_operational_unchanged_after_fork'] for x in ('RES_C01_CUT','RES_C02_SHAM')),
            'no_MAIN_external_RAW_clock_edits_guarded':all(not data[x]['host_RAW_clock_writes_on_MAIN'] for x in ('RES_G301_PREPARED','RES_G302_OFFPATH','RES_G503_RESERVE'))},
        'diagnostic_current_classes':cut['diagnostic_edits']['candidate_positions'],
        'prepared_local_measurements':local,
        'interpretation':{'observed_capacity':'Previously inaccessible lower correspondences become usable at204 and338 while the acquired sign response142 remains available.',
            'causal_class_intervention':'At76 three remaining unpaired cues and one unmatched +z resource match the six fixed candidate positions/directions. Cutting those four exact records in a fork changes6/14 to14/14; identical-RAW sham keeps6/14 and reproduces the parent full final physical arrays.',
            'native_prepared_intervention':'The old treatment has14/14 and the old offpath case6/14, but their experienced histories differ due the17-value configuration error; no placement-only causal inference follows from that pair. A distinct16-value reserve obtains14/14 twice. New corrected matched comparisons, if executed, are recorded separately under resultados/integrated_revision, not substituted into these original primaries.',
            'coverage':'The six-object preparation localizes a useful physical interception arrangement. Moore27 records show +z current7 adjacent79 then absent80, and one cue5 adjacent82 then absent83. Not all four candidate streams were reconstructed to individual target encounters.',
            'resources':'Treatment and offpath each have21 initial material sites versus15 unguarded,65 interfaces, N67. Resource counts match, but the old pair does not match experience. Unguarded versus guarded also adds six prepared objects.',
            'regulation_modality':'Prepared fixed internal interception operating by v27, plus an external diagnostic fork ablation. No consequence-dependent learned scheduling or autonomous decision to regulate is demonstrated.',
            'preservation':'Original R301 and all original selective-native primaries are preserved. No external clearing or clock reset occurs on either new guarded MAIN.',
            'limits':'One finite layout and horizon338; reserve503 is a distinct world/history, not proof of arbitrary timing, unlimited reuse,65 acquired meanings, or a generic cleanup law.'}}
    put(directory/'ANALYSIS.json',summary)
    put(directory/'INDEX_ALL.json',{'schema':'CPC7.primary_evidence.index.v1','cases':[{k:r[k] for k in ('case_id','path','sha256','schema','preparations','diagnostic_forks','parent')} for r in rows]})
    print(json.dumps(summary['counts']))


if __name__=='__main__':main()
