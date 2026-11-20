"""Build a standalone C++ consumer without executing PowerShell script files.

Uses one Visual Studio installation and its official x64 Developer environment.
Does not change Windows execution policy, compile physics, or install software.
"""
import argparse
import json
import os
from pathlib import Path
import subprocess


def main(a):
    vswhere=Path(os.environ['ProgramFiles(x86)'])/'Microsoft Visual Studio/Installer/vswhere.exe'
    result=subprocess.run([str(vswhere),'-latest','-products','*','-requires','Microsoft.VisualStudio.Component.VC.Tools.x86.x64','-property','installationPath'],capture_output=True,text=True,check=True)
    vs=Path(result.stdout.strip());assert vs.is_dir(),'Visual Studio not found'
    developer=vs/'Common7/Tools/VsDevCmd.bat'
    invocation=f'"{os.environ["ComSpec"]}" /d /c call "{developer}" -no_logo -arch=x64 -host_arch=x64 >nul && set'
    result=subprocess.run(invocation,capture_output=True,text=True)
    if result.returncode:raise RuntimeError('Developer environment initialization failed: '+result.stderr)
    environment=os.environ.copy()
    for line in result.stdout.splitlines():
        key,sep,value=line.partition('=')
        if sep and key:environment[key]=value
    # Windows environment keys are case-insensitive. Avoid propagating two PATH
    # spellings from different sources to compiler children.
    path_value=next(value for key,value in environment.items() if key.upper()=='PATH' and key=='PATH')
    environment={k:v for k,v in environment.items() if k.upper()!='PATH'};environment['PATH']=path_value
    cmake=vs/'Common7/IDE/CommonExtensions/Microsoft/CMake/CMake/bin/cmake.exe'
    ninja=vs/'Common7/IDE/CommonExtensions/Microsoft/CMake/Ninja/ninja.exe'
    source=Path(a.source).resolve() if a.source else Path(__file__).resolve().parent.parent/'examples/external_3_5'
    build=Path(a.build_root).resolve(); build.mkdir(parents=True,exist_ok=True)
    commands=[[str(cmake),'-S',str(source),'-B',str(build),'-G','Ninja','-DCMAKE_MAKE_PROGRAM='+str(ninja),'-DCMAKE_PREFIX_PATH='+str(Path(a.install).resolve()),'-DCMAKE_BUILD_TYPE=Release'],[str(cmake),'--build',str(build),'--parallel','2']]
    records=[]
    for command in commands:
        result=subprocess.run(command,env=environment,capture_output=True,text=True)
        record={'argv':command,'exit_code':result.returncode,'stdout':result.stdout,'stderr':result.stderr};records.append(record)
        print('\n'.join(line for line in result.stdout.splitlines() if not line.startswith(('Nota: inclusi','Note: including file:'))))
        print(result.stderr,end='')
        (build/'BUILD_COMMANDS.json').write_text(json.dumps({'visual_studio':str(vs),'commands':records,'windows_execution_policy_changed':False},indent=2),encoding='utf-8')
        if result.returncode:raise RuntimeError('External consumer compilation failed; see BUILD_COMMANDS.json')
    return 0


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--install',required=True);p.add_argument('--build-root',required=True);p.add_argument('--source')
    raise SystemExit(main(p.parse_args()))
