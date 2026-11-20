"""Post-trajectory reconciliation; never runs a world or fills missing clocks."""
import hashlib,json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'resultados/core17_repair'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def put(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
summary=json.loads((OUT/'SUMMARY_all.json').read_text(encoding='utf-8'))
assert summary['status']=='PASS' and len(summary['records'])==12
pairs=[]
for idx in (0,3,4,7):
 a=json.loads((OUT/f'C17R_{idx:02d}_exact_diagnostic/MEASUREMENTS.json').read_text(encoding='utf-8'))
 b=json.loads((OUT/f'C17R_{idx:02d}_standard_channels/MEASUREMENTS.json').read_text(encoding='utf-8'))
 pairs.append({'reference_row':idx,'boundaries':[{'label':x['label'],'tick_equal':x['physical']['tick']==y['physical']['tick'],
    'RAW_equal':x['physical']['RAW_sha256']==y['physical']['RAW_sha256'],
    'clocks_equal':x['physical']['clocks_sha256']==y['physical']['clocks_sha256']} for x,y in zip(a['snapshots'],b['snapshots'])]})
for case in summary['records']:
 assert sha(ROOT/case['measurements'])==case['measurements_sha256']
 d=json.loads((ROOT/case['measurements']).read_text(encoding='utf-8'))
 for s in d['snapshots']:assert sha((ROOT/case['measurements']).parent/s['path'])==s['sha256']
correction={'schema':'CPC8.CORE17.clock_label_correction.v1',
 'source_contract':'Runtime4.5 apply_events_at_boundary writes RAW and explicitly preserves the existing full clock word; ChannelSpec does not select a fresh clock.',
 'superseded_fields':['repair45.py docstring channel arm clock0','standard-channel MEASUREMENTS.input_clock_contract clock0 wording','standard-channel ledger.actual_input_clock = 0'],
 'actual_contract':'PRESERVE_EXISTING_CLOCK_NOT_ZERO_ASSIGNMENT',
 'capture_gap':'Prior clock was not retained in each standard-channel input ledger row. No per-input value has been invented or reconstructed retrospectively.',
 'primary_preserved':True,'physical_code_changed':False,'native_trajectory_repeated_for_this_correction':False,
 'result':'All24 paired saved boundaries have equal RAW; only4 T0 boundaries have equal clocks. The20 later clock arrays differ. Local published readouts and functional results coincide in these four finite pairs.',
 'comparison':pairs}
put(OUT/'CLOCK_CONTRACT_CORRECTION.json',correction)
closure={'schema':'CPC8.CORE17.reference_closure.v1','technical_status':'LOCAL_REFERENCE_COMPARISONS_PASS_WITH_DECLARED_CLOCK_LABEL_INCIDENT',
 'summary':{'path':'resultados/core17_repair/SUMMARY_all.json','sha256':sha(OUT/'SUMMARY_all.json')},
 'clock_correction':{'path':'resultados/core17_repair/CLOCK_CONTRACT_CORRECTION.json','sha256':sha(OUT/'CLOCK_CONTRACT_CORRECTION.json')},
 'trajectories':12,'exact_clock_diagnostic_replays':8,'standard_channel_adaptations_with_diagnostic_damage':4,
 'save_load_continuations_equal':12,'snapshots_verified':72,'new_blind_scientific_holdouts':0,
 'reserve':'Second historical geometry was withheld from adapter pilot; this is technical port reservation, not a new unseen historical result.',
 'preserved_incidents':['pre-run resume-label correction','post-pilot receipt status lower-case evaluator correction; existing trajectories reused','post-run clock0 label corrected from actual Runtime source; missing per-input clocks not invented'],
 'causal_scope':'Carrier-supported recovery from a separately acquired redundant copy. Fixed relay/converter/resources and explicit diagnostic damage. No CPC8 E1 MAIN changed; no R0_FACTOR_52 replay; no autonomous local regeneration.',
 'source_and_evaluator_separation':'repair45.py imports only installed dee_thinking and standard library. Expected historical rows are read in ejecutar_referencia.py after each trajectory, not by the participant.'}
put(OUT/'CLOSURE.json',closure)
links_path=ROOT/'genealogia/CPC8_RESULT_LINKS.json'
links=json.loads(links_path.read_text(encoding='utf-8')) if links_path.exists() else {}
links['CORE17_COMPRESSED_OPERATOR_AND_REPAIR']={'result':'resultados/core17_repair/CLOSURE.json','sha256':sha(OUT/'CLOSURE.json'),
 'state':'PARTIAL_REFERENCE_REPRODUCED_REPAIR_ONLY_DIAGNOSTIC_NOT_INTEGRATED','scope':closure['causal_scope'],
 'reproduced':True,'adapted':True,'integrated_MAIN':False,
 'reproduced_components':['carrier_supported_redundant_repair_local_RAW_and_function'],
 'not_reproduced_components':['R0_FACTOR_52'],
 'input_contracts':'Exact-clock replay is diagnostic only; standard-channel adaptation preserves current clock rather than the legacy clock injections.'}
put(links_path,links)
print(json.dumps(closure,ensure_ascii=False))
