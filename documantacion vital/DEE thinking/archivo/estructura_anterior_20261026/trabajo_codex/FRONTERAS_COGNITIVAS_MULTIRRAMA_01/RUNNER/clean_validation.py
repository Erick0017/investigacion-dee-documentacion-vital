"""Offline clean-extraction/install/restore/case reproduction verification."""
import argparse,hashlib,json,subprocess,sys,zipfile
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from observations import dump,sha
from run_multibranch import verify,utc

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--root',type=Path,required=True)
    ap.add_argument('--zip',type=Path,required=True);ap.add_argument('--scratch',type=Path,required=True)
    ap.add_argument('--resume',action='store_true');ap.add_argument('--environment',type=Path)
    args=ap.parse_args();root=args.root.resolve();archive=args.zip.resolve();scratch=args.scratch.resolve()
    if not scratch.is_relative_to(root/'VALIDATION_SCRATCH'):raise ValueError('scratch must be inside declared validation workspace')
    if scratch.exists() and not args.resume:raise ValueError('clean extraction requires new scratch path or explicit --resume')
    integrity=verify(archive)
    scratch.mkdir(parents=True,exist_ok=args.resume)
    with zipfile.ZipFile(archive) as z:
        for name in z.namelist():
            if not (scratch/name).resolve().is_relative_to(scratch):raise ValueError('unsafe ZIP member')
        if args.resume:
            for entry in json.loads(z.read('MANIFEST.json'))['files']:
                assert sha(scratch/entry['path'])==entry['sha256'],entry['path']
        else:z.extractall(scratch)
    env=args.environment.resolve() if args.environment else root/'VALIDATION_SCRATCH/v'
    if not env.is_relative_to(root/'VALIDATION_SCRATCH'):raise ValueError('environment outside allowed validation workspace')
    if env.exists():raise ValueError('Use a new environment directory')
    subprocess.run([sys.executable,'-I','-B','-m','venv',str(env)],check=True)
    python=env/'Scripts/python.exe';wheel=next((scratch/'SHARED_TOOLS').glob('*.whl'))
    subprocess.run([str(python),'-I','-B','-m','pip','install','--no-index','--no-deps',str(wheel)],check=True)
    results=[]
    for branch,case in (('L05','lineage_reuse_query'),('L06','quiescent_AB')):
        replica=scratch/('CASE_'+branch)
        subprocess.run([str(python),'-I','-B',str(scratch/'RUNNER/run_multibranch.py'),
                        '--root',str(scratch),'--mode','case','--case',branch+'/'+case,'--replica-root',str(replica)],check=True)
        a=json.loads((scratch/f'BRANCHES/{branch}/{case}/MEASUREMENTS.json').read_text(encoding='utf-8'))
        b=json.loads((replica/f'BRANCHES/{branch}/{case}/MEASUREMENTS.json').read_text(encoding='utf-8'))
        assert a['phi']==b['phi']
        checkscript="import sys; sys.path.insert(0,sys.argv[1]); import dee_thinking as dt; from observations import state_equal; a=dt.Runtime.load_snapshot(sys.argv[2]); b=dt.Runtime.load_snapshot(sys.argv[3]); assert state_equal(a,b); x=a.fork(); y=b.fork(); x.advance(2); y.advance(2); assert state_equal(x,y); print('EXACT_CHECKPOINT_AND_FUTURE',a.current_tick)"
        subprocess.run([str(python),'-I','-B','-c',checkscript,str(scratch/'RUNNER'),
                        str(scratch/a['checkpoints'][-1]['path']),str(replica/b['checkpoints'][-1]['path'])],check=True)
        results.append({'case':branch+'/'+case,'phi_exact':True,'final_raw_clock_tick_exact':True,
                        'future_two_ticks_exact':True,'checkpoint_sha256':a['checkpoints'][-1]['sha256'],
                        'replica_checkpoint_sha256':b['checkpoints'][-1]['sha256']})
    dump(root/'SHARED_TOOLS/CLEAN_EXTRACTION_CHECK.json',{'utc':utc(),'tested_staging_zip':str(archive),
        'tested_staging_sha256':sha(archive),'crc_hash_manifest':integrity,
        'new_isolated_venv':True,'offline_install_exact_wheel_sha256':sha(wheel),
        'case_reproductions':results,'scope':'Same frozen scientific payload; final package adds this verification report and helper.'})
    print('CLEAN_EXTRACTION_OFFLINE_INSTALL_AND_CASES_VERIFIED',len(results),flush=True)

if __name__=='__main__':main()
