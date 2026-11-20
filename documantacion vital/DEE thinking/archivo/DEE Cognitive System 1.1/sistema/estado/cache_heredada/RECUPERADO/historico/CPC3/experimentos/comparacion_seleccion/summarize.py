"""Read-only retrospective controls and exact bookkeeping; no native import."""
from pathlib import Path
import argparse,json,hashlib


def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))


def main():
    p=argparse.ArgumentParser();p.add_argument('--root',required=True);a=p.parse_args()
    root=Path(a.root).resolve();base=root/'experimentos/comparacion_seleccion'
    # Source choices are fixed here. Neither the context nor any actual report
    # enters a policy. Truth is consulted exclusively by the later evaluator.
    ids=['positive_contextQ','negative_contextP','roles_swapped_positive','roles_swapped_negative']
    policies={'P_FIJA':['P']*4,'Q_FIJA':['Q']*4,
              'ALTERNANCIA_P_PRIMERO':['P','Q','P','Q'],
              'ALTERNANCIA_Q_PRIMERO':['Q','P','Q','P']}
    rows=[]
    for j,cid in enumerate(ids):
        x=read(base/'seleccion'/cid/'MEASUREMENTS.json');m=x['metadata']
        frame=next(t for t in x['trace'] if t['tick']==17)['ports']
        available={}
        for name in ('P','Q'):
            o=frame[name+'_access'];dr=o['direction'];coupled=bool(o['active'] and dr[0]!=0 and dr[1]==1)
            value=o['load']-143 if coupled else o['load']
            available[name]={'physical_record':o,'accessible_source_field':value,
                             'transport_correction':143 if coupled else 0}
        truth={name:bool(m['branch_contract'][name]['informative']) for name in ('P','Q')}
        native=x['source_products'][0]['source'] if len(x['source_products'])==1 else None
        rows.append({'case':cid,'native_choice':native,
                     'native_informative':truth[native] if native else None,
                     'observable_source_fields':available,
                     'open_policy_choices':{name:choices[j] for name,choices in policies.items()},
                     'open_policy_scores':{name:int(truth[choices[j]]) for name,choices in policies.items()},
                     'truth_used_only_after_policy_choice':truth})
    analysis={'mode':'ANALISIS_EXTERNO_RETROSPECTIVO','case_ids':ids,
              'case_order':'Order frozen in this script; variants already existed, not new holdouts',
              'rows':rows,'scores':{'NATIVE_ROUTER':{'informative':sum(x['native_informative'] is True for x in rows),'opportunities':4}},
              'not_new_executions':True,'new_native_worlds':0,
              'information_cut':'Policies use a fixed source name or visible opportunity index only; no hidden context or future values select their source',
              'resource_scope':'One planned source access per opportunity. Baselines were not physically enacted and have no measured native timing/resource cost.',
              'causal_limit':'This is retrospective source-availability analysis on saved fields, not a native counterfactual or proof of an acquired utility policy.'}
    for name in policies:analysis['scores'][name]={'informative':sum(x['open_policy_scores'][name] for x in rows),'opportunities':4}
    (base/'OPEN_POLICY_RETROSPECTIVE.json').write_text(json.dumps(analysis,indent=2),encoding='utf-8')
    groups=[
        ('DIRECTIONAL_COMPARISON','resultados',13,0,0),
        ('FINITE_SELECTION_COMPONENT','seleccion',13,0,0),
        ('OFFAXIS_NATIVE_BODY_DISCOVERY','native_discovery',4,0,0),
        ('OFFAXIS_NATIVE_BODY_CONFIRMATION','native_confirmation',9,0,0),
        ('OFFAXIS_LATE_DIAGNOSTICS','late_controls',0,3,0),
        ('INFORMATION_REUSE_EXTENSION','post_information',3,2,0),
        ('CENTRAL_MAIN_COMPARISON_DISCOVERY','central_discovery',4,0,0),
        ('CENTRAL_MAIN_COMPARISON_CONFIRMATION','central_confirmation',4,0,0),
        ('CENTRAL_HISTORY_CONTROLS_AND_FOLLOWUP','central_followup',0,3,4)]
    counts=[]
    for name,directory,fresh,forks,continuations in groups:
        measurements=sorted(p for p in (base/directory).glob('*/MEASUREMENTS.json'))
        configs=list((base/directory).glob('EXPERIMENT_CONFIG.json'))
        if directory=='resultados':configs=[base/'EXPERIMENT_CONFIG.json']
        # Every counted scientific trajectory has a separate primary result.
        assert len(measurements)==fresh+forks+continuations,(directory,len(measurements))
        counts.append({'family':name,'directory':str((base/directory).relative_to(root)),
                       'fresh_preparations':fresh,'diagnostic_forks':forks,
                       'restored_scientific_continuation_branches':continuations,
                       'primary_result_files':[str(p.relative_to(root)) for p in measurements],
                       'configuration_files':[str(p.relative_to(root)) for p in configs]})
    tech=read(base/'technical/TECHNICAL_CHECKS.json')
    checks={'passive_observer_repeated':tech['passive_observer_repeated'],
            'trace_on_off_same_future':tech['trace_on_off_same_future'],
            'direct_save_load_same_future':tech['direct_save_load_same_future'],
            'dense_sequential':tech['backend_equalities']['dense_sequential'],
            'dense_parallel':tech['backend_equalities']['dense_parallel'],
            'future_consequence_inert_before_submission':tech['future_consequence_inert_before_submission'],
            'post_information_save_load_same_future':read(base/'post_information/CONTINUITY.json')['RAW_clock_equal']}
    modules=['src/core/comparison.py','src/core/central_comparison.py','src/habitat/selection.py','src/habitat/native_loop.py']
    audit=[]
    for rel in modules:
        text=(root/rel).read_text(encoding='utf-8')
        audit.append({'path':rel,'sha256':hashlib.sha256((root/rel).read_bytes()).hexdigest(),
                      'old_CP01_CP02_absolute_path_literals':any(x in text for x in ('CP02_DOS_LINEAS','CP01_8_CAMPOS')),
                      'terminal_result_fixture_reads':any(x in text for x in ('MEASUREMENTS.json\').read','SUMMARY.json\').read')),
                      'scope':'Text check plus manual source review, not a proof from grep alone'})
    summary={'fresh_scientific_preparations':sum(x['fresh_preparations'] for x in counts),
             'diagnostic_forks':sum(x['diagnostic_forks'] for x in counts),
             'restored_scientific_continuation_branches':sum(x['restored_scientific_continuation_branches'] for x in counts),
             'independent_replicates':'These counts are trajectories/controls; correlated timepoints are never replicates.',
             'groups':counts,'technical_checks':checks,
             'technical_trajectories_separate':{'successful_backend_observer_attempt':6,
                'post_information_restored_continuation':1,
                'failed_technical_attempts':1,
                'failed_attempt_completed_evolutions_before_interface_error':2,
                'scientific_cases_not_repeated_for_interface_fix':True},
             'retrospective_analysis_cases':4,'new_native_baseline_worlds':0,
             'no_double_count':'Four discovery references reused by confirmation remain counted once; post-information save/load is technical, not another individual.',
             'module_source_review':audit,
             'remaining_limits':['No acquired arbitrary P/Q utility policy','No complete central comparison -> renewed writing integration',
                                 'The off-axis and central profiles are different individuals and are not fused'],
             'open_policy_retrospective':'experimentos/comparacion_seleccion/OPEN_POLICY_RETROSPECTIVE.json'}
    (base/'SUMMARY_FOR_ROOT.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
    print(json.dumps({k:summary[k] for k in ('fresh_scientific_preparations','diagnostic_forks','restored_scientific_continuation_branches')}))
    print(json.dumps(analysis['scores']))


if __name__=='__main__':main()
