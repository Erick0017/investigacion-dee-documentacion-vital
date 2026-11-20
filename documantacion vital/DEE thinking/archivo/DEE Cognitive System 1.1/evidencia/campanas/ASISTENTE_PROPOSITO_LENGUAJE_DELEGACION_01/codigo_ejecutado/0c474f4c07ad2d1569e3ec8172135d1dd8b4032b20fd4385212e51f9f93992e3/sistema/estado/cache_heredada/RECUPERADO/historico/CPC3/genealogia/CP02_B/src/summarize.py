"""Derive coverage and errors from primary records; no new native runs."""
import json,hashlib,sys
from pathlib import Path


def atomic(path,x):
    p=Path(path);p.parent.mkdir(parents=True,exist_ok=True);q=p.with_suffix('.tmp');q.write_text(json.dumps(x,indent=2,ensure_ascii=False),encoding='utf-8');q.replace(p)


def metrics(evaluations):
    errors=[e['absolute_error_binary'] for e in evaluations if e['absolute_error_binary'] is not None]
    return {'evaluations':len(evaluations),'singletons':len(errors),'unresolved_sets':len(evaluations)-len(errors),
            'coverage':len(errors)/len(evaluations) if evaluations else None,'binary_errors':sum(errors),
            'accuracy_on_singletons':1-sum(errors)/len(errors) if errors else None,
            'set_containment':sum(e['set_contains_outcome'] for e in evaluations)/len(evaluations) if evaluations else None,
            'temporal_samples_are_not_independent_replicates':True}


def main(root):
    root=Path(root);f=json.loads((root/'resultados/CONFIRMED.json').read_text(encoding='utf-8'));a=json.loads((root/'resultados/ASSISTED_CONFIRMED.json').read_text(encoding='utf-8'));act=json.loads((root/'resultados/ACTIVE_ATTEMPT.json').read_text(encoding='utf-8'));tech=json.loads((root/'resultados/TECHNICAL_CHECKS.json').read_text(encoding='utf-8'))
    groups={}
    for condition in ('PAIRED','NONE','UNPAIRED','MEMORY_EQUALIZED','ROUTE_BLOCKED'):
        rs=[r for r in f['rows'] if r.get('condition')==condition];groups[condition]=metrics([e for r in rs for e in r['evaluations']]);groups[condition]['genealogies_or_diagnostic_branches']=len(rs)
    reserved=[r for r in f['rows'] if r.get('type')=='RESERVED'];groups['RESERVED']=metrics([e for r in reserved for e in r['evaluations']]);groups['RESERVED']['genealogies']=len(reserved)
    assisted={}
    for condition in ('PAIRED_RESULTS','OMITTED_RESULTS','UNPAIRED_RESULTS','OFF_PATH_RESULTS'):
        rs=[r for r in a['rows'] if r['treatment']==condition];assisted[condition]={'genealogies':len(rs),'all_timepoints':metrics([x['evaluation'] for r in rs for x in r['reads']]),
            'final_timepoint':metrics([r['reads'][-1]['evaluation'] for r in rs]),'native_delta_traces':[[r['reads'][0]['emission']['panel_before']['delta']]+[x['panel_after']['delta'] for x in r['events']] for r in rs],
            'baseline_final_errors':[r['reads'][-1]['baseline_error'] for r in rs]}
    corrections=[]
    for name in ('PREDICCIONES_ASSISTED_DISCOVERY.jsonl','PREDICCIONES_ASSISTED.jsonl'):
        for line_no,line in enumerate((root/name).read_text(encoding='utf-8').splitlines(),1):
            x=json.loads(line)
            if x.get('record_type')=='EMISSION' and x.get('modality')=='PHYSICAL_PROBE_ON_MAIN':corrections.append({'file':name,'line':line_no,'run_id':x['run_id'],'recorded_modality':x['modality'],'actual_modality':'DIAGNOSTIC_PHYSICAL_PROBE_IN_DESCENDANT','reason':'old default metadata set before row annotation; physics executed exclusively on fork; parent unchanged asserted in primary rows'})
    atomic(root/'resultados/METADATA_CORRECTIONS.json',{'physics_not_changed':True,'historical_logs_not_overwritten':True,'corrections':corrections,'public_runner_corrected_before_demo_and_reproduction':True})
    cps=[{'path':str(p.relative_to(root)),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in sorted((root/'checkpoints').glob('*.deetsnap'))]
    changes=next(r for r in f['rows'] if r['id']=='CHANGED_CONTEXT')
    x={'line':'CP02 B — ente predictivo','engine':'DEE thinking3.5.0 / kernelv27 frozen','completion':'MEASURED_WITH_DECLARED_FUNCTIONAL_LIMITS',
      'counts':{'primary_rows':17,'primary_forecast_trajectories':15,'new_reserved_preparations':4,'assisted_reserved_genealogies_with_controls':8,'active_attempt_genealogies':6,
                'discovery_smoke_and_assisted_genealogies':3,'local_gate_discovery_preparations':4,'timing_domain_preparations':6,'information_nonleak_preparations':2,'historical_CP01_reruns':0,'technical_replays_not_scientific_replicates':True},
      'direct_forecast':groups,'context_change':{'emitted37_first_targets':[e['absolute_error_binary'] for e in changes['evaluations']],
               'new_event_admission':changes['new_sensor_receipt']['status'],'after_new_input_query_admission':changes['second_emission']['receipt']['status'],
               'after_new_input_prediction':changes['second_emission']['prediction_set']},
      'assisted_acquisition_and_update':assisted,'active_information_attempt':{'rows':len(act['rows']),'native_selections':[r['action_selected'] for r in act['rows'] if r['strategy']=='NATIVE_OUTPUT_FIXED_MAPPING'],
               'native_informative_count':sum(r['informative_action'] for r in act['rows'] if r['strategy']=='NATIVE_OUTPUT_FIXED_MAPPING'),
               'fixed_P_informative_count':sum(r['informative_action'] for r in act['rows'] if r['strategy']=='FIXED_P'),
               'learned_optimal_selection_demonstrated':False,'prediction_quality_after_one_sensor':'unresolved for5/6; random uninformedQ retains wrong singleton in1/6'},
      'technical_checks':tech,'checkpoints':cps,'capacity_profile':{'past_outcome_state_acquisition':True,'prospective_live_native_output':True,'reserved_realizations':True,
               'persistent_native_main':True,'snapshot_predictive_continuation':True,'autonomous_natural_MAIN_repeated_reader':False,
               'external_assisted_physical_reader_reusable':True,'adaptive_context_update':'phase-qualified3samples to a reversed singleton in assisted regime',
               'arbitrary_precursor_dictionary':False,'learned_probability':False,'general_intelligence_claim':False},
      'baseline_comparison':'conventional persistence same supplied past sensor reaches equal stable accuracy and updates after1newprimarysample; DEEassisted reversal requires3phasequalifiedsamples; no performance advantage claimed',
      'information_audit':'AUDITORIA_INFORMACION.json','prospective_log':'PREDICCIONES.jsonl','new_metadata_corrections':'resultados/METADATA_CORRECTIONS.json',
      'uncertainties':['General regularity/transition-rule learning beyond installed persistence family not tested','Longer reuse of direct in-situ reader blocked by occupied site/context','Offpath controls are not universal noncausal shams; late wrapping altered negative delta without improving prediction']}
    atomic(root/'RESULTADOS.json',x);print(json.dumps({'direct':groups,'assisted':assisted,'metadata_corrections':len(corrections)}))


if __name__=='__main__':main(sys.argv[1])
