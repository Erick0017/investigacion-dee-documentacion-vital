"""Descriptive cross-references, coverage and measured panels; no scientific verdict."""
import datetime as D,json
from pathlib import Path
from collections import Counter
from observations import dump,sha

def analyze(root):
    root=Path(root);cfg=json.loads((root/'EXPERIMENT_CONFIG.json').read_text(encoding='utf-8'))
    files=sorted((root/'BRANCHES').glob('*/*/MEASUREMENTS.json'))
    values={p.parent.parent.name+'/'+p.parent.name:json.loads(p.read_text(encoding='utf-8')) for p in files}
    values={k:m for k,m in values.items() if m.get('level')!='technical'}
    clean_path=root/'ANALYSIS/CLEAN_EXTRACTION_CHECK.json'
    clean=json.loads(clean_path.read_text(encoding='utf-8')) if clean_path.exists() else {}
    windows_path=root/'ANALYSIS/TECHNICAL_WINDOWS.json'
    windows=json.loads(windows_path.read_text(encoding='utf-8')) if windows_path.exists() else {}
    def evidence(ids):
        return [{'case':cid,'member':'BRANCHES/'+cid+'/MEASUREMENTS.json',
                 'measurement_sha256':sha(root/'BRANCHES'/cid/'MEASUREMENTS.json'),
                 'phi':values[cid].get('phi'),'status':values[cid]['execution_status']} for cid in ids]
    index=[]
    for cid,m in values.items():
        ops=root/'BRANCHES'/cid/f"attempt_{m['attempt']:03d}"/'OPERATIONS.json'
        events=json.loads(ops.read_text(encoding='utf-8'))
        statuses=Counter(str(r['status']) for row in events['receipts_by_runtime'] for r in row['events'])
        index.append({'case':cid,'work_type':m['work_type'],'role':m['role'],'level':m['level'],'modality':m['modality'],
            'status':m['execution_status'],'runtime_ticks':m['runtime_ticks_executed'],
            'registered_external_calls':len(m['external_calls']),'diagnostic_writes':len(m['diagnostic_writes']),
            'receipt_status_occurrences_including_inherited_fork_prefixes':dict(statuses),
            'state_evidence':[{k:x[k] for k in ('label','path','tick','sha256')} for x in m['checkpoints'] if x['label']=='MAIN_FINAL'],
            'measurement_member':'BRANCHES/'+cid+'/MEASUREMENTS.json'})
    dump(root/'ANALYSIS/COMPARACION_CORTE_ANTERIOR.json',{
        'parent_sha256':cfg['parent_sha256'],'historical_cases':100,'historical_members':1155,
        'new_unique_ids':len(index),'new_measured_runtime_cases':sum(m['runtime_ticks_executed']>0 for m in values.values()),
        'retrospective_readings':sum(m['work_type']=='A' for m in values.values()),
        'source_not_recovered':sum(m['execution_status']=='SOURCE_NOT_RECOVERED' for m in values.values()),
        'technical_reference_reproduction_separate':1,'cases':index,
        'clean_extraction_case_reproductions_separate':len(clean.get('isolated_reproductions',[])),
        'decisive_technical_windows_separate':len(windows.get('decisive_windows',[])),
        'technical_summary_scope':'RUN_SUMMARY.technical_reproductions counts the initial inherited-case reference only; extraction reproductions and window checks are separately recorded here.',
        'counting_rule':'One case ID counted once. Cross-front analysis and combination references add no duplicated executions; fork ticks are not statistical replicas.',
        'technical_attempt_errors_preserved':[p.relative_to(root).as_posix() for p in sorted((root/'BRANCHES').rglob('TECHNICAL_ERROR.json'))]})
    corrections=[
        ('L01/L04','Catalog rejection was not an effective exposure control. Runtime and catalog are distinct admission contracts. New physical calls and actual receipts are retained.',['P01/contracts_reread','P01/independent5_naive','P01/inverted5']),
        ('L01/L04/L05/L08','Different operations of C6 are grouped as one mobile acquired-relation mechanism, not four independent organizational families.',['P01/independent50','P04/native_zero_relay','P09/depth8']),
        ('L02','Emission at t11 also exists in naive. New panels include direction/route adequacy and actual toroidal signature departures; constructor delay is not itself an anticipation horizon.',['P02/appropriate_paired18','P02/naive18','P02/actual_contact_h50','P02/actual_contact_h100']),
        ('L03','Late action cuts, comparable prepared independent exposure and reversed environment geometry are measured. They do not isolate acquired contingency discrimination or learned inversion.',['P03/contingent_d5','P03/contingent_d5_cut','P03/independent_d5','P03/independent_d5_cut','P03/contingency_reversed']),
        ('L06','Rejected occupied-site probes are not evidence of forgetting. Admissible routes, pair validity, retained differences and ordinary expression are recorded separately.',['P13/reread_observer_coverage','P05/latent_AB','P05/latent_BA','P05/latent_equalized']),
        ('L07','Missing material centers invalidate delta as functional memory. Prepared finite contact tolerance is separated from support removal and material regrowth.',['P08/previous_availability_reread','P08/one_native_contact','P08/support_removed']),
        ('L08','A relay or joint mobile product is not two complete renewable bodies or acquired communication. New joint products are physically queried again without promoting them to complete bodies.',['P12/both_empty','P12/later_use_both_empty']),
        ('L09','Selectivity is measured at the downstream descendant, not merely the visible hidden carrier. The P/Q informative side is swapped; informative preference acquisition remains unisolated.',['P11/P_hidden23','P11/P_hidden25','P11/Q_hidden23','P11/Q_hidden25','P11/P_mediator_cut']),
        ('L04_PLUS_L05','The inherited experiment remains one crossing containing five cases. New crossings are separately identified and do not recount inherited cases.',['P09/mobile_basal_full','P06/distributed_HA'])]
    # IDs are validated: no unresolved narrative link is silently published.
    known=set(values)
    for _,_,ids in corrections:
        if any(cid not in known for cid in ids):raise KeyError([cid for cid in ids if cid not in known])
    dump(root/'ANALYSIS/CORRECCIONES_METODOLOGICAS.json',[
        {'prior_reading':old,'restriction_or_extension':text,'evidence':evidence(ids)} for old,text,ids in corrections])
    groups=[
        {'mechanism':'Acquired mobile C6 relation and native vector/load reducer','fronts':['P01','P02','P04','P09','P10','P12'],
         'distinct_operations':['independent/repeated query','directional routing','zero relay','depth','saturation','simultaneous encounter'],'not_inferred':'one separate memory per query, complete bodies, linguistic semantics'},
        {'mechanism':'Supported relative material A/B and reader/phase context','fronts':['P03','P04','P05','P07','P08','P11','P13'],
         'distinct_operations':['write gates','latent relation','assisted sufficiency','entry/return','route selection','contact tolerance'],'not_inferred':'delta alone exhausts identity or current expression'},
        {'mechanism':'CORE05 protected source phase and target-aware native returns','fronts':['P13','P14'],
         'distinct_operations':['transient phase modification','temporal alias','wrapped flux interception','common physical probe'],'not_inferred':'cycle of complete RAW+uint64 clock, universal frame invariance'},
        {'mechanism':'Shared i05 scaffold + i02 relative history + p02 renewed contextual multichannel function','fronts':['P06'],
         'distinct_operations':['joint context','link omission','late local perturbation','finite saturation','independent functional queries'],'not_inferred':'correlation equals signal or quantum entanglement'}]
    dump(root/'ANALYSIS/MAPA_MECANISMOS_COMPARTIDOS.json',groups)
    phase_ids=['P13/access_phase_baseline','P13/access_phase_transient','P13/access_phase_ablation',
               'P14/ablation_wrapped_flux_cut','P14/flux_cut_replication1','P14/flux_cut_replication2']
    continuation_ids=['P06/continued_distributed_HA','P06/continued_distributed_H0','P06/continued_late_region_A_load']
    phase_rows=evidence(phase_ids)
    progression=[]
    for cid in continuation_ids:
        m=values[cid]
        progression.append({'case':cid,'samples':[{'tick':r['tick'],'renewed_q_load':r['renewed_q']['s_reg'],
            'renewed_q_direction':r['renewed_q']['direction'],'valid_pair':r['body']['valid_relation'],
            'delta':r['body']['delta_validated'],'A_load':r['body']['A']['s_reg'],'B_load':r['body']['B']['s_reg']} for r in m['native_no_new_inputs_series']],
            'final_common_queries':[q['response'] for q in m['final_common_queries']]})
    dump(root/'ANALYSIS/REGULARIDADES_Y_ALTERNATIVAS.json',{
        'candidate_limit':4,'open_candidates_followed':2,
        'candidates':[
            {'id':'OPEN_PHASE_ACCESS','prior_local_reading':'Transient and source-ablated preparations both give hub 41/0.',
             'prediction':'Two timing-matched lateral queries distinguish [absent,32] from [absent,54]; baseline shifts 32 to the other phase.',
             'measured_panels':phase_rows[:3],
             'reserved_evidence':evidence([f'P14/reserved_phase_access{k}_mode{mode}' for k in (1,2) for mode in (0,1,2)]),
             'alternative':'Current phase, protected source and returning flux jointly matter; equal local hub readings are not equal complete causal states.'},
            {'id':'OPEN_WRAPPED_REPLACEMENT','prediction_before_replicates':'Remove only the native 41 carrier at T40, preserving clocks: the T43 output contribution is removed.',
             'measured_panels':phase_rows[2:],'route_evidence':evidence(['P14/route_phase_ablation','P14/route_phase_transient']),
             'mechanism_scope':'Forward toroidal replay locates 41 at the protected source site T41. The source blocks that material trajectory in the transient condition; the ablated source leaves a returning route.',
             'not_inferred':'Single isolated portador equals complete organization; no universal transport lineage after a semantic/load-changing encounter.'}],
        'bounded_saturation_and_observer_change':progression,
        'observation':'At T700 q-load coalesces at 19664 in these three trajectories; the common physical pair panel remains history-distinguishing. No exact full-state convergence is inferred.',
        'cross_family_expression':evidence(['P09/mobile_basal_full','P09/mobile_basal_late_cut','P13/retained_expression_mobile_basal_full','P13/retained_expression_mobile_basal_late_cut'])})
    pending={
        'P01':'Measured up to 50 queries on two acquired routes; not 50 independent memories. Admission and sequential transformation recorded.',
        'P02':'Measured 18/50/100 and omitted controls. No independent acquired forecast of unseen consequence is isolated; 500 not attempted because wrapping already changes declared flight.',
        'P03':'Contingent versus prepared independent exposure, late action cuts and reversed geometry measured; acquired discrimination/inversion not isolated from present reader context.',
        'P04':'Native finite mobile functional transfer and assisted subset sufficiency measured. Exact ORGREINSTANTIATE20CX/WARPORG146X source not recovered; complete-body reinstantiation not executed.',
        'P05':'Native retained relative histories and externally admitted recovery queries measured through relative250. Own-action-driven reactivation not isolated.',
        'P06':'Distributed joint function and cuts measured; longer source-supported continuation reaches load saturation. Causal effects are not quantum correlations.',
        'P07':'Common zero-load experience phase/routing selectively changes B write. Late exterior action removal still permits no-E B write; endogenous control of this gate not established by these comparisons.',
        'P08':'One/two finite native contacts and support removal measured. Active structural defense and recovery of damaged learned signature not built; reappeared matter not promoted to recovered function.',
        'P09':'Depth2/4/8 and inter-family bridge measured in single Runtimes. Depth10/20 and indefinitely renewable bridge not tested.',
        'P10':'Finite payload/direction/idle timing domain measured, including saturation. Arbitrary direction/frame/density universalization not attempted.',
        'P11':'Selective conditional native downstream information tested with swapped side and two reserved preparations. Acquisition of preference for the informative route not demonstrated by this apparatus.',
        'P12':'Simultaneous convergence, timing/direction/target context and later physical use measured. Joint mobile descendant is not classified as full renewable B12.',
        'P13':'Independent local/relational/temporal/functional reads reuse actual histories; reserved phase panels belong to P14 and are not recounted as P13 holdouts.',
        'P14':'Two open candidates followed by replay, selective counterfactual and two translated replicates. Coverage is finite, not an exhaustive search of DEE states.'}
    dump(root/'ANALYSIS/COBERTURA_Y_PENDIENTES.json',{'fronts':[{'front':front,'visited':True,
         'completed_cases':sum(m['front']==front for m in values.values()),'coverage_and_pending':note} for front,note in pending.items()],
         'resources':{'processes':2,'native_threads_per_process':1,'dimensions_used':[17,31,34,47,127],
                      'base_buffer_bytes_N127':32*127**3,'native_clock':'full uint64, never reduced for equality'},
         'bounded_cut':'No persistent workers remain scheduled; all cases are finite and resumable from identified snapshots.',
         'host_observation_scope':'Declared sites and relational/ballistic segments, sampled checkpoints and targeted replay, not all microinteractions or a universal mobile-identity detector.'})
    combos=[
        {'id':'MOBILE_RELATION_TO_BASAL_EXPRESSION','families':['C6 acquired mobile relation','supported basal A/B and contextual reader'],
         'recipe_case':'P09/mobile_basal_full','controls':['P09/mobile_basal_late_cut','P09/mobile_basal_offpath','P09/mobile_alone','P09/basal_alone'],
         'reserved_cases':['P09/reserved_bridge1','P09/reserved_bridge1_cut','P09/reserved_bridge2','P09/reserved_bridge2_cut'],
         'measured':evidence(['P09/mobile_basal_full','P09/mobile_basal_late_cut','P09/mobile_basal_offpath','P09/mobile_alone','P09/basal_alone']),
         'same_runtime':True,'construction_before_history':True,'counted_new_case_again':False,
         'scope':'Native mobile input modifies reader/expression; it is not promoted to a retained A/B rewrite.'},
        {'id':'SHARED_CONTEXT_RELATIVE_HISTORY_RENEWED_USE','families':['i05 shared scaffold','i02 relative history','p02 contextual renewal'],
         'recipe_case':'P06/distributed_HA','controls':['P06/distributed_H0','P06/distributed_link_cut','P06/distributed_link_sham','P06/late_region_A_load'],
         'reserved_cases':['P06/reserved_distributed1','P06/reserved_distributed1_cut','P06/reserved_distributed2','P06/reserved_distributed2_cut'],
         'measured':evidence(['P06/distributed_HA','P06/distributed_H0','P06/distributed_link_cut','P06/distributed_link_sham']),
         'same_runtime':True,'construction_before_history':True,'counted_new_case_again':False,
         'scope':'Joint function, not a new output-to-input copy between worlds; late local erasure does not retroactively erase an in-flight historical consequence.'}]
    dump(root/'COMBINATIONS/COMBINATION_MEASUREMENTS.json',{'new_crossings':2,'additional_case_ids':0,'crossings':combos,
        'prior_crossing':'Inherited L04_PLUS_L05, exactly five cases, unchanged.'})
    print(json.dumps({'analysis_completed_utc':D.datetime.now(D.timezone.utc).isoformat(),
        'unique_case_ids':len(index),'crossings_referenced':2,'open_candidates_followed':2}))

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);a=p.parse_args();analyze(a.root)
