"""Finite logged final qualification; reference science is used only in tests."""
import argparse
import importlib.util
import json
from pathlib import Path
import sys


def main(a):
    source = Path(__file__).resolve().parent.parent; tools = source/'tools'
    spec = importlib.util.spec_from_file_location('validation_harness_35',tools/'run_validation_3_0.py')
    harness = importlib.util.module_from_spec(spec); sys.modules[spec.name]=harness; spec.loader.exec_module(harness)
    workspace=Path(a.workspace).resolve(); build=Path(a.build_root).resolve(); venv=Path(a.venv).resolve()
    python=venv/'Scripts/python.exe'; wheel=build/'wheel/dee_thinking-3.5.0-cp313-cp313-win_amd64.whl'
    science=Path(a.science).resolve(); out=workspace/'validation'; out.mkdir(parents=True,exist_ok=True)
    scratch=Path(a.scratch).resolve(); scratch.mkdir(parents=True,exist_ok=True)
    commands=[]
    def command(name,args,kind='other',cwd=None,timeout=7200):
        commands.append({'name':name,'command':list(map(str,args)),'kind':kind,'cwd':str(cwd or scratch),'timeout_seconds':timeout,'required':True})
    if a.phase=='setup':
        assert wheel.is_file(),'Wheel build must finish first'
        command('create_final_clean_venv',[sys.executable,'-I','-m','venv',venv])
        command('install_final_wheel',[python,'-I','-m','pip','install','--no-index','--force-reinstall',wheel],'wheel_smoke')
        consumer=scratch/'cpp_consumer'
        command('external_cpp_find_package',[python,'-I','-B',tools/'build_external_3_5.py','--install',build/'install','--build-root',consumer],'consumer')
    elif a.phase=='test':
        command('clean_installed_public_API',[python,'-I','-B',tools/'check_installed_3_5.py','--wheel',wheel,'--example',source/'examples/organizational_public.py','--output',out/'clean_install'],'wheel_smoke')
        command('python_full_suite',[python,'-I','-B','-m','unittest','discover','-s',source/'tests/python','-v'],'unittest')
        command('native_recipe_comparison',[python,'-I','-B',tools/'compare_native_recipes.py','--science',science,'--output',out/'NATIVE_RECIPE_COMPARISON_FINAL.json'],'unittest')
        command('organizational_cpp_python',[python,'-I','-B',tools/'validate_cross_language_3_5.py','--consumer',scratch/'cpp_consumer/dee_public_consumer.exe','--output',out/'cross_language_3_5'],'cross_language')
        seed=source/'fixtures/mbp4/OBP_FRESH_VALIDATED_T32.deetsnap'
        command('basal_cpp_python',[python,'-I','-B',source/'tests/python/basal_cross_language_driver.py',build/'native/bin/dee_basal_checkpoint_bridge.exe',seed,out/'cross_language_basal'],'cross_language')
        bridge_cpp=build/'native/bin/dee_cross_language_bridge.exe'; bridge_py=source/'tests/python/cross_language_bridge.py'
        runtime=out/'cross_language_runtime'; runtime.mkdir(exist_ok=True)
        for lang,writer,reader in [('cpp',bridge_cpp,[python,'-I','-B',bridge_py]),('python',[python,'-I','-B',bridge_py],bridge_cpp)]:
            before=runtime/(lang+'_before.deetsnap'); after=runtime/(lang+'_after.deetsnap')
            writer=writer if isinstance(writer,list) else [writer]; reader=reader if isinstance(reader,list) else [reader]
            command('runtime_'+lang+'_produce',[*writer,'produce',before,after],'cross_language')
            command('runtime_'+lang+'_consume',[*reader,'consume',before,after],'cross_language')
        protocol_cpp=build/'native/bin/dee_protocol_checkpoint_bridge.exe'; protocol_py=source/'tests/python/protocol_checkpoint_bridge.py'
        protocols=out/'cross_language_protocols'; protocols.mkdir(exist_ok=True)
        for mode in ['h1','h2-separated','h2-overlap','h3','f1','f2']:
            for lang,writer,reader in [('cpp',[protocol_cpp],[python,'-I','-B',protocol_py]),('python',[python,'-I','-B',protocol_py],[protocol_cpp])]:
                checkpoint=protocols/(lang+'_'+mode+'.deetsnap')
                command('protocol_'+lang+'_save_'+mode,[*writer,'save-'+mode,checkpoint],'cross_language')
                command('protocol_'+lang+'_resume_'+mode,[*reader,'resume-'+mode,checkpoint],'cross_language')
        command('measured_reference_cost',[python,'-I','-B',tools/'measure_cost_3_5.py','--output',out/'REFERENCE_COST.json'],'benchmark')
    elif a.phase=='primary':
        for suite in ['inherited','extension']:
            command('primary_final_'+suite,[python,'-I','-B',tools/'replay_primary_cases.py','--science',science,'--suite',suite,'--output',out/'primary_final_3_5'/suite],'unittest',timeout=14400)
    elif a.phase=='supplement':
        command('operational_errors',[python,'-I','-B',tools/'check_operational_errors_3_5.py','--output',out/'OPERATIONAL_ERRORS.json'],'unittest')
    config=out/('COMMAND_SPEC_'+a.phase+'.json'); config.write_text(json.dumps({'commands':commands},indent=2),encoding='utf-8')
    return harness.main(['--spec',str(config),'--output',str(out/('commands_'+a.phase)),'--wheel',str(wheel),'--kernel',str(source/'src/kernel_v27.cpp')])


if __name__=='__main__':
    p=argparse.ArgumentParser()
    for name in ['workspace','build-root','venv','science','scratch']:p.add_argument('--'+name,required=True)
    p.add_argument('--phase',choices=['setup','test','primary','supplement'],required=True)
    raise SystemExit(main(p.parse_args()))
