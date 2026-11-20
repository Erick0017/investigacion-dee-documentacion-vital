"""Reproduce one recorded case using the installed final wheel, not saved answers.

This auditor tool creates a new explicitly bounded reproduction, never resets
the original campaign/resumption budget and never merges a fork into a MAIN.
"""
import argparse,hashlib,importlib.util,json,re,sys,time
from datetime import datetime,timezone,timedelta
from pathlib import Path
def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def put(path,x):path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf-8')
def main():
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1]);p.add_argument('--case',required=True);p.add_argument('--suite',choices=('block','signal'),default='block');p.add_argument('--output',type=Path,required=True);p.add_argument('--timeout',type=int,default=180);a=p.parse_args();root=a.root.resolve();out=a.output.resolve()
    if not re.fullmatch(r'[A-Za-z0-9_]+',a.case):raise ValueError('Invalid case identifier')
    if not 1<=a.timeout<=600:raise ValueError('timeout outside [1,600]')
    if out.exists() and any(out.iterdir()):raise ValueError('Output must be new/empty; no evidence is overwritten')
    out.mkdir(parents=True,exist_ok=True)
    folder='BLOCK_II' if a.suite=='block' else 'SIGNAL_PREDICTION';runner='run_block_ii.py' if a.suite=='block' else 'run_signal_prediction40.py'
    original=root/'experiments'/folder/a.case;case=original/'CASE.json';assert case.is_file(),case
    install=load('local_identity_check',root/'validation/install_resumption40.py');identity_file=out/'LOCAL_IDENTITY.json';wheel=root/'wheel/dee_thinking-4.0.0-cp313-cp313-win_amd64.whl';install.child(str(wheel),str(identity_file))
    identity=json.loads(identity_file.read_text());release=json.loads((root/'validation/BLOCK_I_QUALIFICATION.json').read_text());assert release['qualified'] and identity['wheel_sha256']==release['wheel_sha256'] and identity['native_sha256']==release['native_sha256']
    gate={**identity,'qualified':True,'utc':release['utc'],'scope':'local installed byte identity under the published functional qualification; not a new claim that all release tests were rerun','original_qualification_sha256':hashlib.sha256((root/'validation/BLOCK_I_QUALIFICATION.json').read_bytes()).hexdigest()};put(out/'LOCAL_QUALIFICATION.json',gate)
    supervisor=load('local_reproduction_supervisor',root/'supervise40.py');now=datetime.now(timezone.utc);mono=int(supervisor.ctypes.windll.kernel32.GetTickCount64());jobroot=out/'supervisor';jobroot.mkdir()
    put(jobroot/'BUDGET.json',{'scope':'one user-invoked reproduction only; original campaign records unchanged','start_utc':now.isoformat(),'deadline_utc':(now+timedelta(seconds=a.timeout+650)).isoformat(),'monotonic_deadline_ms':mono+(a.timeout+650)*1000})
    target=out/'trajectory';job=supervisor.run(jobroot,'reproduce_'+a.case,[sys.executable,'-I','-B',str(root/'experiments'/runner),'--root',str(root),'--qualification',str(out/'LOCAL_QUALIFICATION.json'),'--child',str(case),'--output',str(target)],a.timeout,cwd=str(out))
    assert job['exit_code']==0,job
    actual=json.loads((target/'MEASUREMENTS.json').read_text());expected=json.loads((original/'MEASUREMENTS.json').read_text())
    comparison={'full_final_physical_signature':actual.get('final')==expected['final']} if 'final' in expected else {key:actual.get(key)==expected.get(key) for key in ('case','intact','cut','intervention')}
    assert all(comparison.values()),comparison
    put(out/'REPRODUCTION_CHECK.json',{'case':a.case,'trajectory_generated':True,'terminal_snapshot_not_used_as_response':True,'physical_comparison':comparison,'job':job,'attribution':'INSTRUMENTO','modality':'directed deterministic reproduction, not an independent experimental sample'});print('REPRODUCTION_TRAJECTORY_VERIFIED')
if __name__=='__main__':main()
