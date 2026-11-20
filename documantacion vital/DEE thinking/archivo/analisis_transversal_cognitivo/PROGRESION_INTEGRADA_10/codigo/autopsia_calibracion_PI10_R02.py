"""Passive PI10 calibration autopsy from explicit closed episode witnesses.

No DEE import, owner, engine, database, subprocess or environment action.
Reuses the independent primary reader; additional metrics describe measured
references, fixed stencil observations and receipt dose. Predicted free
carrier positions are labelled hypotheses, never a reconstructed genealogy.
"""
from pathlib import Path
import argparse, hashlib, importlib.util, json

VERSION = 'DEE.PI10.passive_calibration_autopsy.R02'
def sha(data): return hashlib.sha256(data).hexdigest()
def need(ok, why):
    if not ok: raise ValueError(why)
def read(path): return json.loads(path.read_text('utf-8-sig'))
def load_reader():
    path = Path(__file__).with_name('recalcular_primarios_PI10_R02.py')
    spec = importlib.util.spec_from_file_location('PI10_independent_closed_primary_reader', path)
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    return module, path
def at(origin, d): return [(origin[k] + d[k]) % 67 for k in range(3)]
def phases(clock): return {'clock':clock, 'mod67':clock%67, 'mod391':clock%391, 'mod782':clock%782}
def references(v, origin, auditor):
    delta = auditor.reference(v, origin)
    return {'tick':v['tick'], 'A_minus_B':delta, 'A':{'s_reg':v['A']['s_reg'], **phases(int(v['A']['clock']))}, 'B':{'s_reg':v['B']['s_reg'], **phases(int(v['B']['clock']))}}
def reference_delta(before, after):
    dt = after['tick'] - before['tick']
    return {'elapsed_ticks':dt, 'delta_A_minus_B':after['A_minus_B']-before['A_minus_B'],
      'delta_A':after['A']['s_reg']-before['A']['s_reg'], 'delta_B':after['B']['s_reg']-before['B']['s_reg'],
      'clocks_advance_with_ticks':all(after[k]['clock']-before[k]['clock']==dt for k in('A','B'))}
def receipt_dose(rows):
    ids = {}; aliases = 0
    for row in rows:
        ident = row['id']; receipt = row['receipt']
        need(ident == receipt['id'], 'Receipt own identity')
        if ident in ids:
            need(ids[ident]['receipt'] == receipt, 'Incompatible receipt alias'); aliases += 1
        else: ids[ident] = row
    groups = {}
    for row in ids.values():
        channel = row.get('channel',row.get('port','<unlabelled>'))
        suffix = channel.split('.')[-1]
        kind = 'outcome' if '.outcome.' in channel else 'copy' if '.copy.' in channel else 'datum' if suffix=='datum' else 'support' if '.support.' in channel else 'question' if 'material_question' in channel else 'preview' if 'actual_plus' in channel else 'query' if suffix=='query' else 'other'
        key = kind + ':' + row['receipt']['status']; groups[key] = groups.get(key,0) + 1
    return {'unique_requested':len(ids),'aliases_not_counted':aliases,'kind_status_counts':groups,
      'rejected_or_nonterminal':[{'id':k,'channel':v.get('channel',v.get('port')),'status':v['receipt']['status']} for k,v in ids.items() if v['receipt']['status']!='applied']}
def preparation(wrapper, closed_owner):
    """Recalculate actual P0 receipts/clearance; no claim of acquired learning."""
    need(closed_owner.get('closed')is True and closed_owner.get('error')is None,'Explicit closed Owner proof')
    need(wrapper.get('status')=='completed'and wrapper.get('error')is None,'Completed exact preparation request')
    outer=json.loads(wrapper['result'])if isinstance(wrapper['result'],str)else wrapper['result']
    rows=outer['result']['rows'];need(len(rows)==1,'One P0 installation record')
    v=rows[0];need(v.get('version')=='DEE.PI10.adaptive_query.two_native_traces.R01'and v.get('not_learning')is True,'Declared architecture only')
    need(v['before_tick']==922371 and v['after_tick']==922374 and v['new_native_ticks']==3 and v['ready']is True,'Actual three-tick P0 reached cut')
    need(closed_owner['final_tick']==v['after_tick'],'Closed owner reaches exact P0 cut')
    prep=v['preparation'];tc=prep['preflight'];device=v['preserved_C_device_preflight'];dose=receipt_dose(v['requests'])
    need(tc['eligible']is True and not tc['conflicts']and tc['origin']==[24,12,12]and tc['reference_clocks']==[922371,922371],'Actual pre-install complete RAW TC clearance')
    need(device['eligible']is True and device['all_eight_RAW0']is True and device['exact_historical_sink_present']is True and not device['conflicts'],'Actual pre-install device clearance and sole immutable sink')
    need(dose['unique_requested']==31 and dose['aliases_not_counted']==0 and not dose['rejected_or_nonterminal'],'All 31 actual P0 births applied once')
    need(all(r['receipt']['effective_tick']==922373 and r['receipt']['requested_tick']==922373 for r in v['requests']),'Future-boundary P0 admission without resubmission')
    need(prep['initial_reference_payloads']=={'A':0,'B':0}and prep['clock_edits']is False and prep['physical_bank_copy']is False,'Zero unlearned supports, no bank copy or clock edit')
    return {'schema':'DEE.PI10.passive_P0_preparation_recalc.R01','Native_executed':False,'new_ticks_in_this_recalculation':0,
      'life_id':closed_owner['life_id'],'actual_Native_before_tick':v['before_tick'],'actual_Native_after_tick':v['after_tick'],'actual_preparation_ticks':3,
      'architecture_not_learning':True,'new_TC_origin':tc['origin'],'preflight_TC_sites':tc['checked_sites'],'preflight_device_sites':device['sites_checked'],
      'initial_reference_payloads':prep['initial_reference_payloads'],'dose':dose,'old_metadata_literal_unchanged_actor_report':v['old_metadata_literal_unchanged'],
      'independent_metadata_comparison_performed':False,'scope':'Closed primary receipt and preflight recalculation, not a Native replay or acquired functional capability.'}
def trace_metric(frame, first, origin, auditor):
    stencil = frame['q1']; tick = stencil['tick']; seed = first['seed_tick']; motor = first['actual_motor']
    points = [auditor.raw_observation(o) for o in stencil['observations']]
    active = [o for o in points if o['state']>0 and o['semantic']==1]
    result = {'label':frame['phase'],'tick':tick,'ticks_after_efference_seed':tick-seed,
      'observed_sites':len(points),'active_SEM1_sites':active,
      'scope':'Fixed sampled stencil. Presence/direction is not a unique carrier identity; absence is not global loss.'}
    if motor in(-1,1):
        pos = at(origin,(-motor*(tick-seed),-1,-2)); actual = next((o for o in points if o['site']==pos),None)
        result['free_uninterfered_copy_hypothesis'] = {'site':pos,'direction':[-motor,0,0],
          'observed_in_fixed_stencil':actual is not None,'actual_observation':actual,
          'matching_signature':None if actual is None else bool(actual['state']>0 and actual['semantic']==1 and actual['direction']==[-motor,0,0]),
          'not_a_measured_path_or_lineage':True}
    return result
def autopsy(v, protocol, auditor):
    need(v.get('version')=='DEE.PI10.adaptive_query.two_native_traces.R01','Exact closed PI10 witness')
    need(v.get('operator_calibration') is True, 'Only identified forced calibration, never candidate learning')
    validation = {'passed':False,'reason':None}
    try: projected = auditor.project_episode(v,protocol); validation['passed']=True
    except (ValueError,KeyError,TypeError,IndexError) as e:
        projected = None; validation['reason']=type(e).__name__+': '+str(e)
    origin = protocol['query_origin']; old = protocol['old_origin']
    q1b=references(v['Q1_references_before'],origin,auditor);q1a=references(v['references_after']['q1'],origin,auditor)
    q2b=references(v['Q2_references_before'],old,auditor);q2a=references(v['references_after']['q2'],old,auditor)
    one=v['calendar']['first'];two=v['calendar']['second'];first=v['first_stage'];second=v['second_stage']
    timeline=[];trace=[]
    for frame in v['trace_observations']:
        if 'q1_references' in frame: timeline.append({'phase':frame['phase'],**references(frame['q1_references'],origin,auditor)})
        trace.append(trace_metric(frame,{'seed_tick':one['seed_tick'],'actual_motor':first['actual_query_motor']},origin,auditor))
    q1change=reference_delta(q1b,q1a);q2change=reference_delta(q2b,q2a)
    calendar={}
    for name,cal,refs in(('q1',one,q1b),('q2',two,q2b)):
        calendar[name]={'seed_tick':cal['seed_tick'],'collision_tick':cal['collision_tick'],'contact_tick':cal['contact_tick'],
          'delay_from_seed_to_collision_ticks':cal['collision_tick']-cal['seed_tick'],
          'delay_laps':(cal['collision_tick']-cal['seed_tick'])/67,
          'nominal_calendar_query_read_tick':cal['query_read_tick'],'actual_observed_central_tick':first['reader']['observation']['tick'] if name=='q1' else second['reader']['observation']['tick'],
          'predicted_clock_at_contact_from_actual_before':[phases(refs[k]['clock']+cal['contact_tick']-refs['tick']) for k in('A','B')],
          'prediction_scope':'Arithmetic on actual before clocks; actual bank/contact frames are listed separately.'}
    flags=[]
    if not validation['passed']:flags.append('independent_primary_validation_failed')
    if first['sample_register']['question_applied'] and not first['sample_register']['question_signature']:flags.append('admitted_query_missing_fixed_signature')
    if q2change['delta_A_minus_B']!=0:flags.append('Q2_bank_delta_drift')
    if second['FI']['old_q6_choice']!=1:flags.append('FI_not_actual_positive_at_frozen_q6')
    if v['returned_failed'] and q1change['delta_A_minus_B']==0:flags.append('failure_return_without_net_Q1_delta_change_not_global_loss_proof')
    if not q1change['clocks_advance_with_ticks'] or not q2change['clocks_advance_with_ticks']:flags.append('reference_clock_advance_differs_from_elapsed_ticks')
    dose=receipt_dose(v['requests'])
    if dose['rejected_or_nonterminal']:flags.append('material_admission_or_terminal_status_problem')
    return {'ordinal':v['ordinal'],'life_id':v['life_id'],'regime':v['environment_spec']['regime'],'cue':v['environment_spec']['cue'],
      'forced_query':first['operator_forced_query'],'not_candidate_learning':True,'before_tick':v['before_tick'],'after_tick':v['after_tick'],
      'independent_primary_validation':validation,'primary_projection':projected,'calendar_and_actual_clock_phases':calendar,
      'q1_reference_before':q1b,'q1_reference_after':q1a,'q1_reference_change':q1change,
      'q2_reference_before':q2b,'q2_reference_after':q2a,'q2_reference_change':q2change,
      'q1_reference_return_timeline':timeline,'trace_stencil_evidence':trace,
      'question':{'Native_choice':first['reader']['choice'],'actual_motor':first['actual_query_motor'],'sample_register':first['sample_register'],'question_observation':first['question_observation'],'actual_request':first['question_request']},
      'actuation':{'q2_Native_choice':second['reader']['choice'],'actual_route':second['actual_route'],'command_valid':second['command_valid'],'FI_actual_q6':second['FI']['old_q6_choice'],'resource':v['resource']},
      'actual_failed':v['actual_failed'],'returned_failed':v['returned_failed'],'dose':dose,'flags':flags}
def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--protocolo',type=Path,required=True);ap.add_argument('--testigo',type=Path,action='append',required=True);ap.add_argument('--salida',type=Path,required=True);a=ap.parse_args()
    need(not a.salida.exists(),'Preserve previous autopsy output; choose a fresh explicit destination')
    auditor,reader_path=load_reader();protocol=read(a.protocolo);rows=[];sources=[]
    for path in a.testigo:
        b=path.read_bytes();rows.append(autopsy(json.loads(b),protocol,auditor));sources.append({'path':str(path.resolve()),'bytes':len(b),'sha256':sha(b)})
    keys=[(r['life_id'],r['ordinal'])for r in rows];need(len(keys)==len(set(keys)),'No duplicate calibration opportunities')
    out={'schema':VERSION,'Native_imported':False,'Native_executed':False,'new_ticks':0,'protocol':{'path':str(a.protocolo.resolve()),'sha256':sha(a.protocolo.read_bytes())},
      'primary_reader_sha256':sha(reader_path.read_bytes()),'sources':sources,'calibrations':rows,
      'all_independent_projections_valid':all(r['independent_primary_validation']['passed']for r in rows),
      'scope':'Recorded-state autopsy, not Native reproduction, approval, promotion or an autonomous learned policy.'}
    with a.salida.open('x',encoding='utf8')as f:json.dump(out,f,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps({'file':str(a.salida.resolve()),'sha256':sha(a.salida.read_bytes()),'calibrations':len(rows),'all_independent_projections_valid':out['all_independent_projections_valid'],'Native_executed':False}))
if __name__=='__main__':main()
