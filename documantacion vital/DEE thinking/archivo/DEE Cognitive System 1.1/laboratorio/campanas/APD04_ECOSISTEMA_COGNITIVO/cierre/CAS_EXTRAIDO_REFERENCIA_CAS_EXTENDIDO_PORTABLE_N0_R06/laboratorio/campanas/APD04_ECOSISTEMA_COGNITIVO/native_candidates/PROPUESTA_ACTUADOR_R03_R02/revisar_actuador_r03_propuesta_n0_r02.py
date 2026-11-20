"""Declared N0 refinement: R03-only cursor description and prospective SAFE scope.

Keeps the R01 proposal and current installed R02 reserve sources untouched.
"""
from pathlib import Path
from datetime import datetime, timezone
import ast
import difflib
import hashlib
import importlib.util
import json
import shutil

HERE=Path(__file__).resolve().parent
OLD=HERE/'PROPUESTA_ACTUADOR_R03_R01'
OUT=HERE/'PROPUESTA_ACTUADOR_R03_R02'


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def write(path,value):
    with path.open('x',encoding='utf8')as stream:json.dump(value,stream,ensure_ascii=False,indent=2);stream.write('\n')
def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module


def main():
    if OUT.exists():raise FileExistsError('Declared R02 proposal exists; no overwrite')
    shutil.copytree(OLD,OUT)
    target=OUT/'sistema/capacidades/ecosistema_apd04.py'
    before=target.read_text(encoding='utf8')
    old="        if quality_witness is not None:result_row['posteffect_quality']=quality_witness"
    new="        if quality_witness is not None:\n            result_row['posteffect_quality']=quality_witness\n            result_row['cursor_rule']='Prepared circular view after any opportunity; Native emits INSPECT/WAIT/USE through the fixed R03 map, not an arbitrary numeric source address.'"
    if before.count(old)!=1:raise ValueError('Exact frozen proposal base differs')
    after=before.replace(old,new);tree=ast.parse(after)
    target.write_text(after,encoding='utf8',newline='\n')
    # Retain the exact earlier manifest/tests under explicit prior-revision names.
    (OUT/'MANIFIESTO_PROPUESTA_N0.json').rename(OUT/'MANIFIESTO_PROPUESTA_N0_R01_ANTERIOR.json')
    (OUT/'PRUEBAS_P0_N0.json').rename(OUT/'PRUEBAS_P0_N0_R01_ANTERIORES.json')
    first=(OUT/'PARCHE_PROPUESTO.diff').read_text(encoding='utf8')
    (OUT/'PARCHE_PROPUESTO_R01_ANTERIOR.diff').write_text(first,encoding='utf8',newline='\n')
    complete=[];members=[]
    for relative in('app/protocolo_apd04.py','capacidades/ecosistema_apd04.py','app/usar_dee.py'):
        base=OUT/'FUENTES_BASE'/relative;proposed=OUT/'sistema'/relative
        ast.parse(proposed.read_text(encoding='utf8'))
        complete.append(''.join(difflib.unified_diff(base.read_text(encoding='utf8').splitlines(True),
            proposed.read_text(encoding='utf8').splitlines(True),fromfile='sistema/'+relative,tofile='sistema/'+relative)))
        members.append({'file':'sistema/'+relative,'base_sha256':sha(base),'proposed_sha256':sha(proposed)})
    (OUT/'PARCHE_PROPUESTO.diff').write_text(''.join(complete),encoding='utf8',newline='\n')
    selected=[node for node in tree.body if isinstance(node,ast.FunctionDef)and node.name in('task_env_signature','formed_native_choice','posteffect_quality_r03')]
    contract='APD04.posteffect_quality.relevant_gain_or_irrelevant_formed_wait.R03.v1'
    namespace={'json':json,'QUALITY_R03':contract};exec(compile(ast.Module(body=selected,type_ignores=[]),'<pure-N0-quality-replay>','exec'),namespace)
    previous=json.loads((OLD/'PRUEBAS_P0_N0.json').read_bytes());replayed=[]
    for test in previous['pure_quality_tests']:
        value=test['result']
        if value['status']=='out_of_domain':
            args=(0,'WAIT',{'choice':0,'candidates':[{'choice':0}]},False,1,0,{},{} ,'nulled')
        else:
            sign=value['formed_native_sign'];action=value['transduced_action']
            if test['name']=='ambiguous_zero_not_WAIT':reader={'choice':None,'candidates':[{'choice':0},{'choice':1}]}
            elif sign is None:reader={'choice':None,'candidates':[]}
            else:reader={'choice':sign,'candidates':[{'choice':sign}]}
            args=(sign,action,reader,value['old_work_gain'],value['tag_auditor_after_effect'],value['goal_auditor_after_effect'],
                  value['task_env_before'],value['task_env_after'],value['actuator'])
        actual=namespace['posteffect_quality_r03'](*args)
        assert actual==value,test['name']
        replayed.append({'name':test['name'],'identical_result':True,'new_quality':actual['new_quality']})
    old_cli=load('actr03_previous_cli_N0',OUT/'FUENTES_BASE/app/usar_dee.py')
    cli=load('actr03_candidate_cli_N0',OUT/'sistema/app/usar_dee.py')
    for argv in previous['legacy17_unchanged']:
        aa=old_cli.command_parser().parse_args(argv);bb=cli.command_parser().parse_args(argv)
        assert vars(aa)==vars(bb)and old_cli.literal_rows(aa)==cli.literal_rows(bb)
    write(OUT/'PRUEBAS_P0_N0_R02.json',{'schema':'APD04.ACT_R03.single_proposal.refinement.N0.r02',
        'pure_quality_tests_replayed':replayed,'legacy17_unchanged':True,'new_native_ticks':0,
        'only_source_difference_from_R01':'R03-only cursor_rule descriptive text; no reader, score, choice, preparation or physical protocol changed.'})
    write(OUT/'ALCANCE_PRETEST_SAFE_R02.json',{
        'declared_utc':datetime.now(timezone.utc).isoformat(),'new_native_ticks':0,
        'parent':'APD04_MAIN_T639374_EXPLORACION_R01',
        'parent_pair_sha256':'5d938d56497571fb4af8ac814eac0cde59214814afb7f3d9280543ea074ca6db',
        'parent_snapshot_sha256':'771e041363b39ef830603cb32ed2bbe7fc5938e4783a9dfe2a733a6e3ee4f9a8',
        'reason':'Root observed dense growth on a later R02 reserve after the old22 panel even on INSPECT/SUCCESS. '
                 'The new experiment starts another explicitly identified SAFE-history fork; it does not repair, reset or inherit the uncommitted later REAL future.',
        'first_exposure':'goal1 before the first tag0 opportunity; if INSPECT is not useful this is a legitimate posteffect FAILURE, not a target sent to the actor.',
        'common_second_exposure':'Predetermined exogenous goal0 change before opportunity2; goal0 continues through5, goal1 applies to6..10.',
        'cache_scope':'Keep actual SAFE cached values exactly, not hypothetical18/24 values from the superseded pre60 parent. No cache insertion.',
        'not_guaranteed':'No guarantee of formed0/WAIT, learning, useful policy or continued viability; retain every outcome.',
        'plan_owner':'Root and apd04_controls freeze the exact literal10-op agenda and resources before any Native GO.',
        'current_reserve_untouched':True,'R01_R02_scientific_scores_unchanged':True})
    shutil.copy2(Path(__file__),OUT/Path(__file__).name)
    write(OUT/'MANIFIESTO_PROPUESTA_N0.json',{'schema':'APD04.ACT_R03.single_proposal.N0.r02',
        'members':members,'quality_contract':contract,'previous_R01_preserved':str(OLD),
        'new_native_ticks':0,'Runtime_created':False,'shared_sistema_modified':False,
        'scope':'Same single ACT_R03 design; descriptive correction and explicit prospective SAFE fork. Not a new Native result.'})
    print(json.dumps({'folder':str(OUT),'members':members,'replayed_quality_cases':len(replayed),'Native_ticks':0},indent=2))


if __name__=='__main__':main()
