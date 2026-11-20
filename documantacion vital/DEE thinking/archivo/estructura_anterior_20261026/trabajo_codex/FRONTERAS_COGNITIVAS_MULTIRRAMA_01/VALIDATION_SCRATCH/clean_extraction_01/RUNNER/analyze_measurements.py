"""Descriptive measurements only: no cognitive adjudication or fitted decoder."""
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from observations import dump,signature,receipt,sha
from run_multibranch import summarize,utc

def main(root):
    root=Path(root);cfg=json.loads((root/'CAMPAIGN_CONFIG.json').read_text(encoding='utf-8'))
    results={b:{p.parent.name:json.loads(p.read_text(encoding='utf-8')) for p in sorted((root/'BRANCHES'/b).glob('*/MEASUREMENTS.json'))} for b in cfg['branches']}
    def point(row):return {k:row[k] for k in ('position','state','s_reg','direction','semantic','clock_uint64')}
    def row_at(m,t):return next(x for x in m['context_rows'] if x['relative_tick']==t)
    def common(b):
        rows=results[b]
        return {'question':cfg['branches'][b]['question'],'numeric_budget_criterion':cfg['branches'][b]['numeric_budget_criterion'],
                'status':'MEASURED','levels_executed':sorted({r['level'] for r in rows.values()}),
                'measurement_files':[{ 'case':n,'path':f'BRANCHES/{b}/{n}/MEASUREMENTS.json','sha256':sha(root/f'BRANCHES/{b}/{n}/MEASUREMENTS.json')} for n in rows],
                'pending':cfg.get('coverage_pending',{}).get(b),
                'scope':'Descriptive finite panel measurements; not an automatic cognitive verdict.'}
    reports={b:common(b) for b in results}
    for b in ('L01','L04'):
        reports[b]['physical_query_outputs']={n:{'responses':[point(x) for x in m['responses']],
            'residuals':m['residuals'],'query':m['query'],'query_age':m['age_at_query'],
            'inputs':m['host_writes_after_t0'],'modality':m['modality']} for n,m in results[b].items()}
    reports['L01']['balanced_mapping']={n:results['L01'][n]['residuals'] for n in ('balanced_paired','balanced_unpaired','balanced_none','balanced_inverted')}
    reports['L02']['time_and_path']={n:{'action':point(m['action']),'opportunity':point(m['opportunity']),
        'later_consequence':point(m['environmental_consequence']),'causal_tick_margin':m['timing_margin_to_consequence'],
        'first_observed_action_tick':m['action']['tick'],'consequence_read_tick':m['environmental_consequence']['tick'],
        'history_parameter':json.loads((root/f'BRANCHES/L02/{n}/CASE_CONFIG.json').read_text())['spec']} for n,m in results['L02'].items()}
    reports['L03']['causal_context_comparisons']={n:{'readings':[{ 'relative_tick':t,
        'A':point(row_at(m,t)['sites']['A']),'B':point(row_at(m,t)['sites']['B']),
        'delta':row_at(m,t)['sites']['A']['s_reg']-row_at(m,t)['sites']['B']['s_reg'],
        'comparator':point(row_at(m,t)['sites']['comparator']),
        'return':point(row_at(m,t)['sites']['return']),
        'reader':point(row_at(m,t)['sites']['reader'])} for t in (14,18,20,26) if any(x['relative_tick']==t for x in m['context_rows'])],
        'interventions':m['interventions'],'matched_A_B_before_replay':m.get('matched_A_B_before_replay'),
        'final_phi':m['phi'],'modality':m['modality']} for n,m in results['L03'].items()}
    reports['L03']['replay_scope']='One-site external environmental replay in diagnostic fork at relative 13; A/B and clocks not copied. It tests measured return/expression, not acquired contingency.'
    for b in ('L05','L08'):
        reports[b]['physical_serial_responses']={n:{'first':point(m['first_response']),'second':point(m['second_response']),
           'descendant':point(m['descendant']),'reuse':None if m.get('reuse_reading') is None else point(m['reuse_reading']),
           'intervention':m['intervention'],'inputs':m['host_writes_after_t0']} for n,m in results[b].items()}
    for b in ('L06','L07'):
        native={};calibration={}
        for n,m in results[b].items():
            if m.get('calibration_only'):calibration[n]=m['protocol_reported_readings'];continue
            probes=[]
            for p in m['common_probes']:
                effective=[r for r in p['receipts'] if r['requested_tick']==32+p['origin_relative_tick']]
                probes.append({'query_relative_tick':p['origin_relative_tick'],'response':point(p['response']),
                    'actual_receipts':effective,'admitted':any(str(r['status']).lower()=='applied' for r in effective),
                    'downstream':[point(x) for x in p['downstream']],
                    'no_query_reference':p.get('no_query_reference')})
            native[n]={'native_relationship':[{ 'relative_tick':r['relative_tick'],'s_A':r['A']['s_reg'],'s_B':r['B']['s_reg'],
                       'delta':r['delta'],'gateA':r['gateA'],'gateB':r['gateB']} for r in m['native_rows']],
                       'probes':probes,'damage':m['damage'],'main_inputs':m['host_writes_after_t0_main']}
        reports[b]['native_trajectories']=native
        if calibration:reports[b]['inherited_H3_calibration_readings']=calibration
    reports['L09']['hidden_condition_and_background']={n:{'initial_declared_interface':row_at(m,0)['sites'],
        'action8':point(row_at(m,8)['sites']['action']),'return14':point(row_at(m,14)['sites']['return']),
        'reader18':point(row_at(m,18)['sites']['comparator']),'final_phi':m['phi'],
        'interventions':m['interventions']} for n,m in results['L09'].items()}
    for b,r in reports.items():dump(root/'BRANCHES'/b/'BRANCH_MEASUREMENTS.json',r)
    combo={p.parent.name:json.loads(p.read_text(encoding='utf-8')) for p in (root/'COMBINATIONS').glob('*/MEASUREMENTS.json')}
    dump(root/'COMBINATIONS/COMBINATION_MEASUREMENTS.json',{'combination':'L04_PLUS_L05',
          'preparation':cfg['combinations'],'outputs':{n:{'first':point(m['first_response']),'second':point(m['second_response']),
            'diagnostic_edit':m['intervention'],'inputs':m['host_writes_after_t0']} for n,m in combo.items()},
          'isolated_component_references':['BRANCHES/L04/paired/MEASUREMENTS.json','BRANCHES/L05/full/MEASUREMENTS.json'],
          'limitation':'Shared installed route geometry and finite additive transforms; no claim of emergent category or syntax.'})
    cfg['coverage_pending']['L03']='Late native action/return cuts and one-site external replay measured, with two translated repetitions. Learned distinction between C/U and interface swap remain unexecuted.'
    if not any(x.get('issue')=='L03 supplemental replay missing import' for x in cfg['technical_hotfixes']):
        cfg['technical_hotfixes'].append({'issue':'L03 supplemental replay missing import','exception':'NameError: response',
                 'correction':'Imported existing passive serializer, no physical parameter change.',
                 'scope':'first unfinished supplementary arm; other completed experiments not rerun','utc':utc()})
    dump(root/'CAMPAIGN_CONFIG.json',cfg);summarize(root,cfg)
    summary=json.loads((root/'RUN_SUMMARY.json').read_text())
    summary['checkpoint_count']=len(list((root/'CHECKPOINTS').rglob('*.deetsnap')))
    summary['branch_reports']={b:f'BRANCHES/{b}/BRANCH_MEASUREMENTS.json' for b in reports}
    summary['measured_technical_errors_excluded_from_functional_comparisons']=['L01/unpaired','L04/unpaired']
    dump(root/'RUN_SUMMARY.json',summary)
    print(json.dumps({'measured_cases':summary['cases_measured'],'joint_cases':summary['joint_cases_measured'],
                      'ticks':summary['total_runtime_ticks'],'checkpoints':summary['checkpoint_count']},indent=2))

if __name__=='__main__':main(sys.argv[1] if len(sys.argv)>1 else Path(__file__).resolve().parents[1])
