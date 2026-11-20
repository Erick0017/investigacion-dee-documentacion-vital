"""Read-only-to-native incremental evidence index; writes auditor reports only."""
from datetime import datetime,timezone
import hashlib,json,sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'resultados/auditor'
def read(path):return json.loads(Path(path).read_text(encoding='utf-8'))
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def inherited_protocol_difference():
    import dee_thinking as d
    sys.path.insert(0,str(ROOT))
    from src.auditor.passive import operation_state
    base=ROOT.parents[1]
    replay=OUT/'INHERITED_REFERENCE148_149/REPLAY_T149.deetsnap'
    reference=base/'resultados/confirmacion/FULL_PLUS/NATIVO/AFTER_COMMON_QUERY_PLUS.deetsnap'
    if not replay.exists():return None
    a=operation_state(d.OrganizationalWorld.load_snapshot(str(replay)))
    b=operation_state(d.OrganizationalWorld.load_snapshot(str(reference)))
    added_receipts=[r for r in b['receipts'] if r not in a['receipts']]
    added_calls=[c for c in b['external_operations'] if c not in a['external_operations']]
    row={'mode':'PASSIVE_COMPARISON_NO_ADVANCE_NO_ADDED_INPUT',
       'physical_equal':a['physics']==b['physics'],'operational_equal':a==b,
       'different_operational_components':[key for key in a if a[key]!=b[key]],
       'receipts_only_in_historical_target':added_receipts,'external_calls_only_in_historical_target':added_calls,
       'explanation':'The historical t149 cut was saved after its host runner submitted resource at149 and supply at155. Those new boundary calls are not contained in source148 and do not follow from advancing Runtime one tick. At149 before their application physics still matches; pending protocol state legitimately differs.',
       'scope':'Physical reference transition reproduced; full external-environment continuation not replayed. No queue was lost by save/load and no artificial input was added just to force equality.'}
    (OUT/'INHERITED_REFERENCE_OP_DIFF.json').write_text(json.dumps(row,ensure_ascii=False,indent=2),encoding='utf-8')
    return row

def main():
    source=read(OUT/'SOURCE_REVIEW.json');reg=read(OUT/'R14_PUBLIC_COMPONENT/RUN_SUMMARY.json')
    windows=[]
    for name in ('ABCD_WINDOW160_161_V2','ABCD_WINDOW93_94'):
        p=OUT/name/'TECHNICAL_CHECKS.json';x=read(p)
        windows.append({'id':name,'evidence':str(p.relative_to(ROOT)),'sha256':sha(p),
            'window':[x['start_tick'],x['end_tick']],'continuations':x['continuations'],
            'checks':x['technical_checks'],'pending_at_boundary':x['pending_at_boundary'],
            'diagnostic_edit_was_noop':x['diagnostic']['RAW_sites_changed']==0,
            'note':'No-op removal does not certify independent buffers; see separate live-record isolation checks.'})
    forks=read(OUT/'NONTRIVIAL_FORK_ISOLATION.json');context=read(OUT/'D_SOCIAL_CONTEXT93_94.json')
    red=[]
    for path in sorted((ROOT/'resultados/red').glob('**/MEASUREMENTS.json')):
        x=read(path);case=x.get('case',{});row={'id':case.get('id',path.parent.name),
            'evidence':str(path.relative_to(ROOT)),'sha256':sha(path),'configuration':case,
            'scope':x.get('scope'),'task_profile':x.get('task_profile'),'external_utility':x.get('external_utility'),
            'evaluated_bank':'B_ROLE_417_431' if 'B_future_read' in x else 'D_FIRST_BANK228_242'}
        for key in ('A_emission','C_emission','B_contact','joint','D_social_contact','D_first_read','D_reused_read',
                    'D_first','D_reused','native_turn','B_social_received','B_future_read'):
            if key in x:row[key]=x[key]
        for first,later in (('D_first_read','D_reused_read'),('D_first','D_reused')):
            if first in x and later in x:
                a,b=x[first],x[later]
                row['D_two_use_panel']={'first_tick':a['tick'],'later_tick':b['tick'],
                    'delta_ticks':b['tick']-a['tick'],'loads':[a['s_reg'],b['s_reg']],
                    'directions':[a['direction'],b['direction']],
                    'both_available':a['active'] and b['active'],
                    'same_direction':a['direction']==b['direction'],
                    'scope':'Two physical sequential uses of one continuing D state; not indefinite renewal or two independent replicas.'}
        red.append(row)
    pairing=[]
    confirm=ROOT/'resultados/red/confirmacion02'
    for identifier,component,acquired_tick in [('C_UNPAIRED_U','C',13),('D_UNPAIRED_U','D',27)]:
        full_path=confirm/'FULL_U/MEASUREMENTS.json';control_path=confirm/identifier/'MEASUREMENTS.json'
        if not(full_path.exists() and control_path.exists()):continue
        full,control=read(full_path),read(control_path)
        def sample(x,t,name):
            frame=next((v for v in x['trace'] if v['tick']==t),None)
            return None if frame is None else frame['samples'].get(name)
        pairing.append({'control':identifier,'component':component,'acquisition_cut':acquired_tick,
           'paired_acquisition_sample':sample(full,acquired_tick,component),
           'unpaired_acquisition_sample':sample(control,acquired_tick,component),
           'C_query80':{'paired':sample(full,80,'C'),'unpaired':sample(control,80,'C')},
           'joint86':{'paired':sample(full,86,'joint'),'unpaired':sample(control,86,'joint')},
           'D94':{'paired':sample(full,94,'D'),'unpaired':sample(control,94,'D')},
           'later_D_loads':{'paired':[full['D_first']['s_reg'],full['D_reused']['s_reg']],
                            'unpaired':[control['D_first']['s_reg'],control['D_reused']['s_reg']]},
           'B_role_read417':{'paired':full['B_future_read'],'unpaired':control['B_future_read']},
           'profiles':{'paired':full['task_profile'],'unpaired':control['task_profile']},
           'inference':'Pairing changes the acquired intermediate direction/load and later loads, but is not necessary for the measured utility in this panel. A residual teacher carrying the useful directional component is a supported alternative; source tracking beyond sampled windows is not asserted as unique genealogy.',
           'evidence':[str(full_path.relative_to(ROOT)),str(control_path.relative_to(ROOT))]})
    (OUT/'PAIRING_SCOPE_REVIEW.json').write_text(json.dumps({'mode':'PASSIVE_REANALYSIS_NO_NEW_NATIVE_RUN',
          'contrasts':pairing,'scope':'Do not turn a functional unpaired control into an alleged missing effect; preserve state-level and task-level distinctions.'},ensure_ascii=False,indent=2),encoding='utf-8')
    result={'utc':datetime.now(timezone.utc).isoformat(),'classification':'EXTERNAL_TECHNICAL_AND_MECHANISM_AUDIT',
      'source_recovery':{'requested':len(source['sources']),'recovered':sum(x['exists'] for x in source['sources']),
          'historical_runners_executed':0,'evidence':'resultados/auditor/SOURCE_REVIEW.json'},
      'public_finite_regulation_component':{'fresh_preparations':reg['new_fresh_component_preparations'],
          'diagnostic_forks':reg['diagnostic_forks'],'max_tick':reg['maximum_tick'],
          'integration_into_ABCD_claimed':False,'scope':reg['scope'],
          'evidence':'resultados/auditor/R14_PUBLIC_COMPONENT/RUN_SUMMARY.json'},
      'new_network_technical_windows':windows,
      'inherited_reference_brief':read(OUT/'INHERITED_REFERENCE148_149/MEASUREMENTS.json') if (OUT/'INHERITED_REFERENCE148_149/MEASUREMENTS.json').exists() else None,
      'inherited_reference_protocol_difference':inherited_protocol_difference(),
      'technical_scope':{'successful_backend_and_direct_continuations':sum(x['continuations'] for x in windows),
          'additional_failed_instrument_assert_attempt_continuations':4,
          'nontrivial_diagnostic_forks_without_advance':len(forks['checks']),
          'all_nontrivial_forks_one_RAW_zero_clocks_parent_intact':all(x['RAW_sites_changed']==1 and x['clock_sites_changed']==0 and x['full_parent_operational_unchanged'] for x in forks['checks']),
          'fresh_network_preparations_created_by_auditor':0,
          'backend_threads':1,'no_GUDHI_requested':True,
          'corrections':'Opaque format comparison distinguished serialized backend/checksum; initial fixed-port RAW0 diagnostics explicitly recognized as no-op, replaced by live58/74 isolation checks without repeating trajectories.'},
      'D_social_local_context':{'transition':context['transition'],'empty_target_before':context['empty_target_before'],
          'proposals':context['pre_context']['directional_proposals_without_activity_prefilter'],
          'post':context['post_target'],'local_fields_match':context['post_matches_two_source_context'],
          'necessity':'Separate native cuts are needed; equality of summed loads alone is not necessity.'},
      'red_measurements_read':red,
      'pairing_scope_contrasts':pairing,
      'information_audit':{'expected_evaluation_only_read_by_physics_recipe':False,
          'utility_used_as_native_input':False,'host_copies_social_output':False,
          'actual_scope':'History/report signs and future U/V are declared external experience/environment conditions. Initial history is physically acquired online. Protocol metadata is not read by F_v27.',
          'observer_limit':'The recipe panel A_segment predicts only the positive-Y segment. Its absence is not evidence of A-minus loss. Current field contexts retain actual directions.'},
      'reviewed_source_hashes':{str(p.relative_to(ROOT)):sha(p) for p in (ROOT/'src/red/recipe.py',ROOT/'src/red/session.py',ROOT/'src/red/run_roles.py') if p.exists()},
      'remaining':'Final confirmatory controls/reserves/continuations and lexical cases may still be running; rerun this passive index only after their own outputs close. This report does not create another physical case.'}
    OUT.mkdir(parents=True,exist_ok=True);(OUT/'AUDITOR_SUMMARY.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'red_measurements_read':len(red),'technical_windows':len(windows),'status':'INDEXED'}))

if __name__=='__main__':main()
