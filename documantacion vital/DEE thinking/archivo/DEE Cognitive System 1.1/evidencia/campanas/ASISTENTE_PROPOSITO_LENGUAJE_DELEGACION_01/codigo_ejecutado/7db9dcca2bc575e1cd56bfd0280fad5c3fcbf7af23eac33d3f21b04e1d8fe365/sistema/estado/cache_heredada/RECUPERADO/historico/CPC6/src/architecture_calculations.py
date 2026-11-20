"""Auditor-only reconciled architecture/message calculations from primary JSON.

Never imported by a participant or used to select its stimuli.
"""
from pathlib import Path
import json,sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import ROOT,put,sha

FOLDERS=('ARCHITECTURE_SCREEN_01','ARCHITECTURE_BRIDGE_01','ARCHITECTURE_BRIDGE_DELAYED_02','ARCHITECTURE_BRIDGE_DELAYED_04','ARCHITECTURE_BRIDGE_CONFIRM_05')


def read(path):return json.loads(Path(path).read_text(encoding='utf-8'))


def main():
    primary=[];by_id={}
    for label in FOLDERS:
        index=read(ROOT/'resultados'/label/'INDEX.json')
        for item in index['cases']:
            path=ROOT/item['evidence'];m=read(path);by_id[item['id']]=m
            calls=m.get('calls',m.get('requests',[]))
            primary.append({'case_id':item['id'],'family':label,'primary':item['evidence'],'sha256':sha(path),
                'owner_runtimes':m['owner_runtimes'],'new_preparations':m['preparations'],
                'individual_candidates':m.get('individual_candidates',2),
                'summary':m['summary'],'receipt_counts':{'total':len(calls),'applied':sum(q['receipt']['status']=='applied' for q in calls),
                    'rejected':sum(q['receipt']['status'].startswith('rejected') for q in calls)},
                'elapsed_seconds':m['elapsed_seconds']})
    one=by_id['AS01_ONE_COMPOUND'];two=by_id['AS02_TWO_COMPOUNDS'];four=by_id['AS03_FOUR_COMPOUNDS']
    u1=lambda m:[row['units']['U1'] for row in m['rows']]
    panel_invariance={'one_vs_two_all_captured_U1_fields':u1(one)==u1(two),'one_vs_four_all_captured_U1_fields':u1(one)==u1(four),
       'one_vs_two_expressed_U1_stage_records':one['summary']['U1']==two['summary']['U1'],
       'one_vs_four_expressed_U1_stage_records':one['summary']['U1']==four['summary']['U1'],
       'scope':'Stageexpressionequivalence is not equalityofallobservedcandidatefields orphysicalworlds.'}
    bridge=by_id['BD31_TWO_COMPOUNDS_LATE_SUPPORT'];base30=bridge['rows'][30]['bridge_relay_site']
    controls={}
    for key in ('BC01_RECEIVER_NO_ORDER_EXPERIENCE','BC02_RECEIVER_OPPOSITE_ORDER','BC03_RECEIVER_SOURCE_UNPAIRED','BC04_RESERVED_RECEIVER_LOAD_QUERY'):
        m=by_id[key];controls[key]={'relay30_raw_clock_site_identical':m['rows'][30]['bridge_relay_site']==base30,
           'receiving75':m['rows'][75]['bridge_receiving_site'],'U2_summary':m['summary']['U2'],
           'final_U1_order_delta':m['rows'][-1]['units']['U1']['body']['delta'],
           'final_U2_order_delta':m['rows'][-1]['units']['U2']['body']['delta']}
    failures=[]
    for label in ('architecture_bridge_delayed_01','architecture_bridge_delayed_03'):
        p=ROOT/'jobs'/label/'COMMAND.json'
        files=[str(x.relative_to(ROOT)) for x in (ROOT/'jobs'/label).iterdir() if x.is_file()]
        failures.append({'job':label,'evidence':files,'status':'TECHNICAL_ERROR_BEFORE_NATIVE_WORLD',
          'cause':'Public APIdecodername unpack_record instead of decode_record' if label.endswith('01') else 'Constructor validation rejected supportdirection decomposition before Runtime creation'})
    out={'schema':'CPC6.architectures_and_dialogue.v1','calculation_source_sha256':sha(__file__),
      'counts':{'measured_new_preparations':len(primary),'owner_runtimes_per_preparation':1,
        'physical_candidate_bodies_across_worlds':sum(r['individual_candidates'] for r in primary),
        'technical_errors_before_world':len(failures),'directed_technical_reproductions':1,'diagnostic_rescue_forks':2,
        'independent_statistical_replications_claimed':0},
      'measured_cases':primary,'technical_failures':failures,'U1_common_panel':panel_invariance,
      'same_message_receiver_experience_controls':controls,
      'directed_inspection':{'file':'resultados/ARCHITECTURE_U4_INSPECTION_01.json','sha256':sha(ROOT/'resultados/ARCHITECTURE_U4_INSPECTION_01.json')},
      'causal_rescue':{'file':'resultados/ARCHITECTURE_U4_RESCUE_01/MEASUREMENTS.json','sha256':sha(ROOT/'resultados/ARCHITECTURE_U4_RESCUE_01/MEASUREMENTS.json')},
      'formulas':{'expressed_stage':'Active semantic1 plus exact stage direction, from frozen source decoder. Multiple aliases for same tick/site/RAW/clock counted once.',
        'same_message':'Equality of the entire exact passive record at relay30 across complete worlds, calculated AFTER trajectories.',
        'candidate_bodies':'Sum physical candidate bodies across19 deterministic worlds; not an accumulated singlemind repertory or independentstochastic samplecount.'},
      'scope':'Coexistence1/2/4 and native messageuse2; no measured3compoundcase and no superiorityunder equalresources. Programmedsymmetric24supportexposures are not learnedregulatorychoice.'}
    put(ROOT/'resultados/ARCHITECTURES_AND_DIALOGUE.json',out)
    print({'counts':out['counts'],'panel':panel_invariance,'identical_messages':{k:v['relay30_raw_clock_site_identical'] for k,v in controls.items()}},flush=True)


if __name__=='__main__':main()
