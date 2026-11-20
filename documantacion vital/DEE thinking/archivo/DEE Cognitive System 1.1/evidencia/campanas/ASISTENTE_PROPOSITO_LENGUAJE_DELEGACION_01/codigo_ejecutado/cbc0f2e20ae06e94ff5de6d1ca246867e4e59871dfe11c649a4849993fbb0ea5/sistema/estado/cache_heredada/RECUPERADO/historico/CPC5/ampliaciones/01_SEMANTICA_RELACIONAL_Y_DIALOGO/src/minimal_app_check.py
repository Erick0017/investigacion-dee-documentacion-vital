"""Technical isolation test: run public app without any laboratory result/target files."""
import argparse
import json
from pathlib import Path
import shutil
import subprocess
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import ROOT,BASE,put,sha,digest,operational

def main():
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);p.add_argument('--full-demo',type=Path,required=True);p.add_argument('--staging',type=Path);a=p.parse_args()
    a.output.mkdir(parents=True,exist_ok=False)
    # Windows CreateProcess rejects an excessively long cwd even when Python
    # can open long filenames. A fresh short staging root is explicit, not a
    # fallback to any laboratory content.
    mini=a.staging if a.staging else a.output/'minimal_CPC5'
    if mini.exists():raise FileExistsError(mini)
    ext=mini/'ampliaciones/01_SEMANTICA_RELACIONAL_Y_DIALOGO'
    sources=[(BASE/'src/common.py',mini/'src/common.py'),(BASE/'src/supervisor.py',mini/'src/supervisor.py'),
             (BASE/'runtime/dee_thinking-4.0.0-cp313-cp313-win_amd64.whl',mini/'runtime/dee_thinking-4.0.0-cp313-cp313-win_amd64.whl')]
    for name in ('demostracion.py','ejecutar.py','configuraciones/demo_longitudinal.json'):
        sources.append((ROOT/name,ext/name))
    for name in ('common.py','supervisor.py','public_sessions.py','order_stream.py','semantic_relations.py','architectures.py','capacity.py','dialogue.py','portable_batch.py','network_dialogue.py','network_session.py'):
        source=ROOT/'src'/name
        if source.exists():sources.append((source,ext/'src'/name))
    copied=[]
    for source,dest in sources:
        dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,dest)
        assert sha(source)==sha(dest);copied.append({'path':str(dest.relative_to(mini)),'sha256':sha(dest),'bytes':dest.stat().st_size})
    assert not (mini/'resultados').exists() and not (ext/'resultados').exists()
    appout=a.output/'generated';argv=[sys.executable,'-I','-B',str(ext/'ejecutar.py'),'demostracion','--eventos',str(ext/'configuraciones/demo_longitudinal.json'),'--salida',str(appout)]
    result=subprocess.run(argv,capture_output=True,timeout=240)
    # Keep exact process output even if Windows emits a legacy code page.
    (a.output/'STDOUT.log').write_bytes(result.stdout);(a.output/'STDERR.log').write_bytes(result.stderr)
    assert result.returncode==0
    import dee_thinking as d
    w=d.OrganizationalWorld.load_snapshot(str(appout/'LONGITUDINAL_T338.deetsnap'))
    full=d.OrganizationalWorld.load_snapshot(str(a.full_demo/'LONGITUDINAL_T338.deetsnap'))
    op1,op2=operational(w),operational(full)
    for op in (op1,op2):op['metadata']={k:v for k,v in op['metadata'].items() if not k.startswith('dee_thinking.organizational.')}
    fields={'RAW_complete':w.runtime.raw_copy()==full.runtime.raw_copy(),'clocks_complete':w.runtime.clock_copy()==full.runtime.clock_copy(),
            'tick':w.runtime.current_tick==full.runtime.current_tick,'mutable_operative_and_session':op1==op2,
            'no_lab_results_or_targets_in_minimal_tree':not (mini/'resultados').exists() and not (ext/'resultados').exists(),
            'commands_all_accepted':json.loads((appout/'DEMO_RESULT.json').read_text(encoding='utf-8'))['rejected_commands']==0}
    report={'schema':'CPC5.extension.minimal_app.v1','verified':all(fields.values()),'fields':fields,'argv':argv,'exit_code':result.returncode,
            'comparisons_after_trajectories_only':True,
            'copied_files_only':copied,'physical':digest(w),
            'scope':'No results, targets, teaching map, historical checkpoints, catalogs, venv or external laboratory implementation copied into minimal application. Input events are declared experiences. Comparison only after both trajectories.'}
    put(a.output/'MINIMAL_REPORT.json',report);assert report['verified'];print(json.dumps({'verified':True,'files':len(copied)}))

if __name__=='__main__':main()
