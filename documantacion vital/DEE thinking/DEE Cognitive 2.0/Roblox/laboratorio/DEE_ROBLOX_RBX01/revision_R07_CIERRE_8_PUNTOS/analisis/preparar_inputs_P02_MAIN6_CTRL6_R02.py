"""Only closed-file input mapping; does not recalculate or inspect Native roots."""
from pathlib import Path
import hashlib
import json
ROOT=Path(__file__).resolve().parents[1]
main=ROOT/'analisis/RECALCULO_MAIN6_R01/HECHOS_CIERRE8_R07.json'
raw=main.read_bytes()
ctrl=ROOT/'evidencia/CTRL1_SEIS_R06'
expected={'result':'8514a6211df2ca5744856b130de8b0b446d6d4a337f5da023bfca5ddd029e2eb',
    'world':'19a682a2c8032daa845ee31bd49d57b287f77c253b5768d1388f7cce078c1e43'}
for key,name in(('result','RESULTADO.json'),('world','WORLD_CHECKPOINT.json')):
    assert hashlib.sha256((ctrl/name).read_bytes()).hexdigest()==expected[key]
spec={'schema':'DEE.R07.MAIN_CTRL.reuse.inputs.v1',
    'reused_main_facts':str(main),'reused_main_facts_sha256':hashlib.sha256(raw).hexdigest(),
    'parent_world':str(ROOT.parent/'revision_R06_INTEGRAL_V2/evidencia/PAR28/WORLD_CHECKPOINT.json'),
    'main_closed_physical_proof':str(ROOT/'evidencia/PUNTO34_R06/PAREJA_INTEGRAL_V3.json'),
    'control_closed_physical_proof':str(ctrl/'CONCILIACION_CIERRE_R06.json'),
    'controls':[{'name':'NATIVE_CTRL1_CONSTANT_TAG2_FIRST6','participant':'LIVE_NATIVE','sensor_arm':'constant_tag2',
        'blocks':[{'result':str(ctrl/'RESULTADO.json'),'world':str(ctrl/'WORLD_CHECKPOINT.json'),
            'events':str(ctrl/'EVENTS.jsonl'),'expected_source_sha256':expected}]}]}
target=ROOT/'analisis/INPUTS_P02_MAIN6_CTRL6_REUSO_R02.json'
with target.open('x',encoding='utf-8')as f:json.dump(spec,f,ensure_ascii=False,indent=2);f.write('\n')
print(json.dumps({'inputs':str(target),'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),
    'MAIN_facts_reused_not_recalculated':True,'Native_MCP_SQLite_model_calls':0},ensure_ascii=False))
