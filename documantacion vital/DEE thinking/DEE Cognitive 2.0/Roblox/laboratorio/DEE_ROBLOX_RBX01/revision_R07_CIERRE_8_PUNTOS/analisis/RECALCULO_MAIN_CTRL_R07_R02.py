"""Passive P02 pairing: reuse frozen MAIN facts; calculate only the closed control.

No Native/World/database/SDK/model. MAIN original phases are not recalculated.
Historical source aliases resolve through the package manifest when requested.
"""
from pathlib import Path
import argparse
import copy
import csv
import hashlib
import json
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from RECALCULO_CIERRE8_R07_R02 import Sources,analyze_arm,save_outputs,ensure,canonical
from RECALCULO_MAIN_CTRL_R07 import paired_view

def execute(inputs,source_root,package_root,output):
    spec=json.loads(Path(inputs).read_text('utf-8-sig'))
    ensure(spec['schema']=='DEE.R07.MAIN_CTRL.reuse.inputs.v1','Explicit reuse input schema')
    source=Sources(source_root or Path(inputs).parent,package_root)
    raw=source.raw(spec['reused_main_facts'])
    ensure(hashlib.sha256(raw).hexdigest()==spec['reused_main_facts_sha256'],'Frozen MAIN fact hash differs')
    previous=json.loads(raw.decode('utf-8-sig'))
    main=[a for a in previous['arms']if a['participant']=='LIVE_NATIVE'and a['sensor_arm']=='local_tag']
    ensure(len(main)==1 and main[0]['completed_cycles']==list(range(29,35)),'Exactly previously calculated MAIN6')
    parent=source.json(spec['parent_world'])
    ensure(parent['native_tick']==991187 and parent['S']['completedCycles']==28,'Exact closed PAR28 baseline')
    controls=[]
    for arm in spec['controls']:
        ensure(arm['participant']=='LIVE_NATIVE'and arm['sensor_arm']=='constant_tag2','Fixed declared control')
        for block in arm['blocks']:
            for key,expected in block.get('expected_source_sha256',{}).items():
                ensure(hashlib.sha256(source.raw(block[key])).hexdigest()==expected,'Closed control source differs: '+key)
        controls.append(analyze_arm(source,arm,parent))
    ensure(controls,'An actually closed control is required')
    main_proof=source.json(spec['main_closed_physical_proof'])
    control_proof=source.json(spec['control_closed_physical_proof'])
    m=main_proof['boundary']['native_physical']
    c=control_proof['physical_fingerprint_recorded_by_official_owner']
    keys=('N','tick','RAW_sha256','clocks_sha256')
    fingerprint_main={k:m[k]for k in keys};fingerprint_control={k:c[k]for k in keys}
    physical={'source_main':{'path':spec['main_closed_physical_proof'],'pointer':'/boundary/native_physical'},
        'source_control':{'path':spec['control_closed_physical_proof'],'pointer':'/physical_fingerprint_recorded_by_official_owner'},
        'main':fingerprint_main,'control':fingerprint_control,'equal_N_T_RAW_clocks':fingerprint_main==fingerprint_control,
        'source_scope':'Archived closed owner fingerprints, not a fresh inspection of either live world',
        'complete_organization_or_global_causal_equality':'NOT_ESTABLISHED',
        'known_distinctions':['Life/session identity','scope capacity/role and lease metadata','World identity, environment/auditor history and full organization metadata'],
        'no_claim_of_identical_history_or_future':True}
    facts=copy.deepcopy(previous)
    facts.update(schema='DEE.R07.MAIN_CTRL.ReusedMainFacts.R02',
        mode='PASSIVE_CLOSED_CONTROL_AND_REUSED_MAIN_NOT_NATIVE_REPRODUCTION',
        arms=[copy.deepcopy(main[0]),*controls],
        reused_main={'file':spec['reused_main_facts'],'sha256':spec['reused_main_facts_sha256'],
            'MAIN_scientific_recalculation_performed_now':False,'previous_verified_primary_provenance':previous.get('sources',[])},
        physical_comparison=physical,has_all_three_configurations=False)
    paired=paired_view(facts)
    common=set(main[0]['completed_cycles'])
    for a in controls:common&=set(a['completed_cycles'])
    facts['common_observed_cycles']=sorted(common)
    facts['comparison_group_arms']=[a['name']for a in facts['arms']]
    facts['comparison']=paired['table'];facts['P02_paired_comparisons']=paired['pairs']
    facts['issues_total']=sum(len(a['issues'])for a in facts['arms'])
    source.verify_unchanged();facts['sources']=list(source.records.values())
    save_outputs(output,facts);output=Path(output)
    (output/'CONTROLES_PAREADOS_R07.json').write_text(json.dumps(paired,ensure_ascii=False,indent=2)+'\n','utf-8')
    (output/'HUELLAS_FISICAS_Y_LIMITES_R07.json').write_text(json.dumps(physical,ensure_ascii=False,indent=2)+'\n','utf-8')
    table=paired['table']
    with(output/'COMPARACION_PAREADA_MAIN_CTRL_R07.csv').open('w',encoding='utf-8',newline='')as f:
        writer=csv.DictWriter(f,fieldnames=list(table[0]));writer.writeheader()
        for row in table:writer.writerow({k:canonical(v)if isinstance(v,(dict,list))else v for k,v in row.items()})
    recipe={'script':'analisis/RECALCULO_MAIN_CTRL_R07_R02.py','inputs':str(Path(inputs).resolve()),
        'local_args':['--inputs',str(Path(inputs).resolve()),'--source-root',str(source.root),'--output','<FRESH_OUTPUT>'],
        'portable_args':['--inputs','<DELIVERED_INPUTS>','--package-root','<EXTRACTED_ROOT>','--output','<FRESH_OUTPUT>'],
        'sources':facts['sources'],'MAIN_reused_not_recalculated':True,
        'package_rule':'Manifest.source exact absolute provenance alias -> archive relative path; never open original drive with --package-root'}
    (output/'RECETA_PORTABLE_Y_FUENTES_R02.json').write_text(json.dumps(recipe,ensure_ascii=False,indent=2)+'\n','utf-8')
    return facts,paired

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--inputs',type=Path,required=True)
    p.add_argument('--source-root',type=Path);p.add_argument('--package-root',type=Path)
    p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    facts,paired=execute(a.inputs,a.source_root,a.package_root,a.output)
    print(json.dumps({'output':str(a.output),'issues':facts['issues_total'],'pairs':paired['pairs'],
        'physical_equal':facts['physical_comparison']['equal_N_T_RAW_clocks'],
        'MAIN_recalculated':False,'Native_MCP_SQLite_model_calls':0},ensure_ascii=False))
