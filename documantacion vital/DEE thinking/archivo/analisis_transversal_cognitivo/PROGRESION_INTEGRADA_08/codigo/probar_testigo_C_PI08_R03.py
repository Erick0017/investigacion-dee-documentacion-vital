"""Focused pure test of immediate C witness; no new Native test battery."""
from pathlib import Path
import ast,copy,hashlib,importlib.util,json,tempfile,sys
P=Path(__file__).resolve().parents[1];H=P/'codigo'
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def main():
    change=json.loads((P/'control/C_INSTRUMENTACION_R03_CAMBIO_PRE_NATIVE.json').read_text('utf8'))
    before=Path(change['before']['path']);after=Path(change['after']['path'])
    assert sha(before)==change['before']['sha256']and sha(after)==change['after']['sha256']
    restored=after.read_text('utf8')
    for edit in reversed(change['changes']):
        assert restored.count(edit['after'])==1
        restored=restored.replace(edit['after'],edit['before'])
    assert restored==before.read_text('utf8')
    names={'_submit','_observe','_native','_read','run_until','submit_query','submit_motor_copy','submit_generic_outcome','raw_copy','clock_copy'}
    def native_calls(text):
        return [(node.func.id if isinstance(node.func,ast.Name)else node.func.attr)for node in ast.walk(ast.parse(text))if isinstance(node,ast.Call)and((isinstance(node.func,ast.Name)and node.func.id in names)or(isinstance(node.func,ast.Attribute)and node.func.attr in names))]
    assert sorted(native_calls(after.read_text('utf8')))==sorted(native_calls(before.read_text('utf8')))
    spec=importlib.util.spec_from_file_location('PI08_C_witness_pure',after);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    assert not any(name.startswith('dee_thinking')for name in sys.modules)
    payload={'ordinal':0,'query_tick':123,'observation_tick':131,'actual_preview_observation':{'raw':'0','state':0,'direction':[0,0,0]},
             'reader':{'choice':None},'requests':[{'id':7,'receipt':{'id':7,'status':'applied'}}],
             'question_observation':{'raw':'0','state':0},'Native_inputs':{'unique_requested':1,'applied':1}}
    literal=copy.deepcopy(payload)
    with tempfile.TemporaryDirectory(prefix='PI08_C_immediate_witness_pure_')as directory:
        witness=module.write_first_stage_witness(directory,payload)
        file=Path(directory)/witness['file'];data=json.loads(file.read_text('utf8'))
        assert payload==literal and witness['sha256']==sha(file)and witness['bytes']==file.stat().st_size
        assert data['reader']['choice']is None and data['actual_preview_observation']['state']==0 and data['new_Native_calls_for_witness']==0
        digest=sha(file)
        try:module.write_first_stage_witness(directory,payload)
        except FileExistsError:pass
        else:raise AssertionError('Immediate witness was overwritten')
        assert sha(file)==digest
    source=after.read_text('utf8')
    assert source.index('first_stage_witness = write_first_stage_witness')<source.index("if not summary1['all_terminal']")<source.index('if applied and not signature:')
    assert "'external_immediate_first_stage_witness':locals().get('first_stage_witness')"in source
    files=['pi08_consulta_condicional_C_R03.py','preparar_C_PI08_R03.py','importar_C_PI08_R04.py','ejecutar_C_PI08_R03.py']
    for name in files:ast.parse((H/name).read_bytes())
    result={'schema':'DEE.PI08.C.immediate_witness.focused_pure_tests.R03','passed':True,'Native_executed':False,'DEE_imported':False,
            'checks':{'literal_beforeimage_and_reversible_patch':True,'Native_call_set_unchanged':True,'writer_mutates_no_supplied_values':True,'RAWzero_and_NULL_preserved':True,'duplicate_witness_not_overwritten':True,'witness_precedes_first_stage_failure_checks':True,'failure_metadata_keeps_witness_pointer':True,'new_CLIs_AST_valid':True},
            'scope':'Pure host-instrumentation scope: existing data -> externalartifact, no new Native call. HostI/O and an artifact are added. No actual Native with/without observer passivity claim.',
            'Native_passivity_materially_tested':False,'protocol_scientific_unchanged':{'file':'PROTOCOLO_PI08_C_R02.json','sha256':sha(H/'PROTOCOLO_PI08_C_R02.json')},
            'second_Native_episode_unchanged':{'file':'pi08_consulta_condicional_C_segunda_R02.py','sha256':sha(H/'pi08_consulta_condicional_C_segunda_R02.py')},
            'files':{name:{'bytes':(H/name).stat().st_size,'sha256':sha(H/name)}for name in files}}
    file=P/'control/C_TESTIGO_INMEDIATO_PRUEBAS_PURAS_R03.json'
    with file.open('x',encoding='utf8')as out:json.dump(result,out,ensure_ascii=False,indent=2);out.write('\n')
    print(json.dumps({'passed':True,'checks':8,'proof':str(file),'sha256':sha(file),'files':result['files']},indent=2))
if __name__=='__main__':main()
