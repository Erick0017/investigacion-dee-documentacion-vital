"""Clean archive extraction/install/use without source or laboratory on sys.path."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path,PurePosixPath
import shutil
import sys
import zipfile


def sha(path):
    with Path(path).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()


def main(a):
    destination=Path(a.destination).resolve()
    if destination.exists():raise FileExistsError('Clean validation requires a new, empty destination; no existing evidence overwritten')
    destination.mkdir(parents=True); root=destination/'package'
    archive=Path(a.zip).resolve(); logs=Path(a.log_root).resolve();logs.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(archive) as z:
        assert z.testzip() is None,'candidate CRC'
        for name in z.namelist():
            p=PurePosixPath(name);assert not p.is_absolute() and '\\' not in name and '..' not in p.parts and ':' not in name
        expected={}
        for line in z.read('HASHES.sha256').decode().splitlines():
            h,name=line.split('  ',1);expected[name]=h;assert hashlib.sha256(z.read(name)).hexdigest()==h,name
        assert set(expected)==set(z.namelist())-{'HASHES.sha256'}
        z.extractall(root)
    manifest=json.loads((root/'MANIFEST.json').read_text())
    for entry in manifest['files']:
        p=root/entry['path'];assert p.stat().st_size==entry['size'] and sha(p)==entry['sha256']
    tools=root/'source/tools';wheel=root/'wheel/dee_thinking-3.5.0-cp313-cp313-win_amd64.whl'
    spec=importlib.util.spec_from_file_location('extract_harness35',tools/'run_validation_3_0.py')
    h=importlib.util.module_from_spec(spec);sys.modules[spec.name]=h;spec.loader.exec_module(h)
    venv=destination/'venv';python=venv/'Scripts/python.exe';consumer=destination/'consumer'
    example=destination/'public_example.py';shutil.copy2(root/'source/examples/organizational_public.py',example)
    cmds=[]
    def command(name,args,kind='other'):
        cmds.append({'name':name,'command':list(map(str,args)),'cwd':str(destination),'kind':kind,'timeout_seconds':1200,'required':True})
    command('extracted_clean_venv',[sys.executable,'-I','-m','venv',venv])
    command('extracted_noneditable_install',[python,'-I','-m','pip','install','--no-index',wheel],'wheel_smoke')
    command('extracted_public_API_outside_source',[python,'-I','-B',tools/'check_installed_3_5.py','--wheel',wheel,'--example',example,'--output',logs/'installed_public'],'wheel_smoke')
    command('extracted_external_cpp',[python,'-I','-B',tools/'build_external_3_5.py','--install',root/'install','--build-root',consumer,'--source',root/'source/examples/external_3_5'],'consumer')
    command('extracted_cpp_python_continuation',[python,'-I','-B',tools/'validate_cross_language_3_5.py','--consumer',consumer/'dee_public_consumer.exe','--output',logs/'cross_language'],'cross_language')
    commands_file=logs/'COMMAND_SPEC.json';commands_file.write_text(json.dumps({'commands':cmds},indent=2),encoding='utf-8')
    exit_code=h.main(['--spec',str(commands_file),'--output',str(logs/'commands'),'--wheel',str(wheel),'--kernel',str(root/'source/src/kernel_v27.cpp')])
    if exit_code:raise RuntimeError('Clean extracted walkthrough failed; logs retained: '+str(logs))
    install=json.loads((logs/'installed_public/INSTALLATION_RESULT.json').read_text());cross=json.loads((logs/'cross_language/CROSS_LANGUAGE_RESULT.json').read_text())
    assert cross['cpp_to_python'] and cross['python_to_cpp'] and cross['interfamily_native_bridge_equal']
    result={'archive_tested_sha256':sha(archive),'archive_name':archive.name,'extracted_package':str(root),
            'CRC_hash_manifest_verified':True,'members':len(expected)+1,'wheel_sha256':sha(wheel),'native_sha256':install['native_sha256'],
            'public_installed_walkthrough':install['noneditable_site_packages'] and install['cross_process_operational_future_equal'],
            'external_cpp_consumer':True,'cross_language_persistence':True,'laboratory_imports_blocked':install['laboratory_modules_blocked'],
            'loaded_module':install['module'],'loaded_native':install['native_module'],'commands_record':str(logs/'commands/COMMAND_RESULTS.json'),
            'scope':'Archive payload extracted and checked; wheel installed noneditable in fresh environment; example run outside source; external C++ consumer and cross-language operational continuation. Final outer ZIP hash is recorded externally, never inside itself.'}
    report=Path(a.report);report.parent.mkdir(parents=True,exist_ok=True);report.write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(json.dumps(result,indent=2));return 0


if __name__=='__main__':
    p=argparse.ArgumentParser()
    for name in ['zip','destination','log-root','report']:p.add_argument('--'+name,required=True)
    raise SystemExit(main(p.parse_args()))
