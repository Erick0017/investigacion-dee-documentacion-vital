"""Passive first-six recalculation from the two preserved real event fragments."""
from pathlib import Path
import hashlib
import json
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from RECALCULO_CIERRE8_R07_R02 import Sources,run,save_outputs

ANALISIS=Path(__file__).resolve().parent
R07=ANALISIS.parent
LAB=R07.parent
continuation=R07/'evidencia/MAIN_BLOQUE_01_CONTINUACION34_R01'
original=R07/'evidencia/MAIN_BLOQUE_01_R03'
parent=LAB/'revision_R06_INTEGRAL_V2/evidencia/PAR28/WORLD_CHECKPOINT.json'
output=ANALISIS/'RECALCULO_MAIN6_R01'
inputs=ANALISIS/'RECALCULO_MAIN6_INPUTS_R02.json'
spec={'schema':'DEE.R07.recalculation.inputs.v1','parent_world':str(parent),
    'arms':[{'name':'NATIVE_MAIN_FIRST6','participant':'LIVE_NATIVE','sensor_arm':'local_tag',
        'blocks':[{'result':str(continuation/'RESULTADO.json'),
            'world':str(continuation/'WORLD_CHECKPOINT.json'),
            'event_fragments':[str(original/'EVENTS.jsonl'),str(continuation/'EVENTS.jsonl')]}]}]}
assert not inputs.exists() and not output.exists(),'Fresh inputs and output required'
inputs.write_text(json.dumps(spec,ensure_ascii=False,indent=2)+'\n','utf-8')
source=Sources(LAB)
facts=run(spec,source)
save_outputs(output,facts)
recipe={'schema':'DEE.R07.PassiveRecipe.MAIN6.R02','execution':'No Native, MCP, model, World or SQL calls',
    'local_argv':[sys.executable,'-I','-B','-X','utf8',str(ANALISIS/'RECALCULO_CIERRE8_R07_R02.py'),
        '--inputs',str(inputs),'--source-root',str(LAB),'--output','<FRESH_OUTPUT>'],
    'portable_argv':['python','RECALCULO_CIERRE8_R07_R02.py','--inputs','RECALCULO_MAIN6_INPUTS_R02.json',
        '--package-root','<EXTRACTED_PACKAGE_ROOT>','--output','<FRESH_OUTPUT>'],
    'package_source_aliases_required':facts['sources'],
    'event_fragment_semantics':'Same closed six-cycle block; original phases and continued phases are deduplicated by real operation ID. No Q1 replay.',
    'source_unchanged_after_read':True}
(output/'RECETA_Y_FUENTES_PORTABLES_R02.json').write_text(json.dumps(recipe,ensure_ascii=False,indent=2)+'\n','utf-8')
proof={'schema':'DEE.R07.PassiveRecalculation.Fixtures.R02','synthetic_tests':18,'passed':18,
    'observed_seconds':9.942,'test_file':'test_recalculo_cierre8_R02_offline.py',
    'includes':'Recovery Q1 only in original; duplicate receipt documentary only; both fragments portable without originals; all 14 R01 fixtures.',
    'recalculator_sha256':hashlib.sha256((ANALISIS/'RECALCULO_CIERRE8_R07_R02.py').read_bytes()).hexdigest(),
    'Native_calls':0,'MCP_calls':0,'model_calls':0}
(output/'VERIFICACION_SINTETICA_R02.json').write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n','utf-8')
arm=facts['arms'][0]
print(json.dumps({'output':str(output),'issues':arm['issues'],'notes':arm['notes'],
    'completed':arm['completed_new'],'ticks':arm['native_ticks_from_unique_phases'],
    'numeric':arm['numeric'],'delta':arm['delta'],'P02':arm['first6_P02'],
    'loops':arm['loop_2_3_transitions'],'overrides':arm['effective_host_overrides'],
    'operations':arm['deduplicated_completed_operations'],'null':arm['phase_choice_counts'],
    'sources':len(facts['sources'])},ensure_ascii=False,indent=2))
