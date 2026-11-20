"""External allowlisted FOCAL_R06 CLI bootstrap for Python -I. No implicit action."""
from pathlib import Path,PurePosixPath
import argparse,hashlib,json,runpy,sys
EXPECTED_FREEZE='f0c15fb16afc404f12beb5ef990ec9b5b8c82d7731af689c79149b63dd44a3c8'
COMMANDS={'verify':'verificar_fuentes_focal_R06.py','seal':'sellar_ventana_focal_R06.py',
          'prepare':'preparar_focal_R06.py','scenes':'preparar_escenas_focales_R06.py',
          'start':'iniciar_focal_R06.py'}
ROOT=Path(__file__).resolve().parent.parent

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def checked_sources(runtime=ROOT,expected=EXPECTED_FREEZE):
    runtime=Path(runtime).resolve(strict=True)
    manifest=runtime/'backend/focal_r06/FUENTES_FOCAL_R06.json'
    if sha(manifest)!=expected:raise ValueError('EXACT_ORIGINAL_FOCAL30_FREEZE_REQUIRED')
    value=json.loads(manifest.read_text('utf8'))
    if value.get('schema')!='DEE.SDK.FOCAL_R06.source_freeze.01' or len(value['members'])!=30:
        raise ValueError('ORIGINAL_FOCAL30_MANIFEST_REQUIRED')
    for row in value['members']:
        relative=PurePosixPath(row['file'])
        if relative.is_absolute() or '..' in relative.parts or not row['file'].startswith('backend/focal_r06/'):
            raise ValueError('FROZEN_CONTAINED_SOURCE_REQUIRED')
        target=runtime.joinpath(*relative.parts)
        for p in (target,*target.parents):
            if p.exists() and (p.is_symlink() or getattr(p.lstat(),'st_file_attributes',0)&1024):
                raise ValueError('LINKED_SOURCE_REJECTED')
        if not target.is_file() or target.stat().st_size!=row['bytes'] or sha(target)!=row['sha256']:
            raise ValueError('FROZEN_FOCAL_SOURCE_CHANGED:'+row['file'])
    return runtime

def diagnose(runtime=ROOT):
    runtime=checked_sources(runtime)
    window=runtime/'configuracion/VENTANA_FOCAL_R06.json'
    registry=runtime/'estado_demo/PARTICIPANTES_FOCAL_R06.json'
    # Read no participant contents, ledger, Native state, SQLite, credentials or processes.
    return {'schema':'DEE.SDK.FocalLauncher.Diagnostic.R06.R01',
        'freezeSha256':EXPECTED_FREEZE,'focalWindowExists':window.exists(),
        'focalParticipantRegistryExists':registry.exists(),'NativeOpenedByLauncher':False,
        'stateOrSQLiteRead':False,'identityCreated':False,'windowWritten':False,
        'instruction':'DO_NOT_RESEAL_USE_EXISTING_WINDOW' if window.exists() else 'No window file found; this is not proof of global Native state. Root may explicitly seal once.',
        'scope':'FS footprint only; no Native closure certification or automatic recovery.'}

def launch(command,arguments,*,runtime=ROOT):
    if command not in COMMANDS:raise ValueError('CLI_NOT_ALLOWLISTED')
    runtime=checked_sources(runtime);args=list(arguments)
    if command=='seal' and '--help' not in args and '-h' not in args and (runtime/'configuracion/VENTANA_FOCAL_R06.json').exists():
        raise FileExistsError('WINDOW_ALREADY_SEALED_DO_NOT_RESEAL')
    focal=runtime/'backend/focal_r06';target=focal/COMMANDS[command]
    if not target.is_file():raise FileNotFoundError('ALLOWLISTED_CLI_MISSING')
    prior_path=list(sys.path);prior_argv=list(sys.argv)
    try:
        sys.path.insert(0,str(focal)) # Explicitly restores local imports removed by Python -I.
        sys.argv=[str(target),*args]
        runpy.run_path(str(target),run_name='__main__')
    finally:
        sys.path[:]=prior_path;sys.argv[:]=prior_argv

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('command',choices=[*COMMANDS,'diagnose-zero'])
    p.add_argument('arguments',nargs=argparse.REMAINDER);a=p.parse_args()
    if a.command=='diagnose-zero':
        if a.arguments:p.error('diagnose-zero accepts no arguments and never executes recovery')
        print(json.dumps(diagnose(),ensure_ascii=False,sort_keys=True))
    else:launch(a.command,a.arguments)
if __name__=='__main__':main()
