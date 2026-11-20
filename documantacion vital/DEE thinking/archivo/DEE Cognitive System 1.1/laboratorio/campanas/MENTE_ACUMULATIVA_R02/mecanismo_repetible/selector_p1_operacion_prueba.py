"""Minimal load/admit/save and later-process use/reload checks, no re-teaching.
Run phases separately. Outputs refer to copies of complete existing snapshots.
"""
import argparse,hashlib,json,sys,importlib.util
from pathlib import Path
from dee_thinking.persistence import load_world_snapshot,save_world_snapshot
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3];sys.path.insert(0,str(ROOT/'sistema'))
from app.lives import WorldAdapter
from app.native_tools import physical
sp=importlib.util.spec_from_file_location('p1oper',HERE/'selector_p1_operativo.py');o=importlib.util.module_from_spec(sp);sp.loader.exec_module(o)
def main():
    p=argparse.ArgumentParser();p.add_argument('phase',choices=['admitir','usar','recargar']);p.add_argument('source');p.add_argument('output_prefix');a=p.parse_args();prefix=Path(a.output_prefix)
    source=Path(a.source);w,_=load_world_snapshot(source);s=WorldAdapter(w);before=physical(w);result=None
    if a.phase=='admitir':result=o.admit(s)
    elif a.phase=='usar':result=o.use(s,detailed=True)
    else:
        result={'state':o.state(s),'repeat_attempt':None}
        try:o.use(s);raise RuntimeError('A second use was silently permitted')
        except ValueError as e:result['repeat_attempt']={'rejected_by_contract':True,'message':str(e)}
    after=physical(w)
    if a.phase in('admitir','recargar')and before!=after:raise RuntimeError('Metadata-only phase changed physical world')
    snapshot=prefix.with_suffix('.deetsnap.gz');proof=save_world_snapshot(w,snapshot,compress=True)
    record={'schema':'MA02.P1.operational_check.1','phase':a.phase,'source':{'path':str(source),'sha256':hashlib.sha256(source.read_bytes()).hexdigest()},'before':before,'after':after,'result':result,'snapshot':{'path':str(snapshot),'sha256':hashlib.sha256(snapshot.read_bytes()).hexdigest(),'proof':proof},'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'adapter_sha256':hashlib.sha256((HERE/'selector_p1_operativo.py').read_bytes()).hexdigest(),'no_new_teaching':True,'another_process_required_by_runbook':True}
    dest=prefix.with_suffix('.json')
    if dest.exists():raise FileExistsError(dest)
    dest.write_text(json.dumps(record,ensure_ascii=False,sort_keys=True),encoding='utf8');print(json.dumps({'phase':a.phase,'tick':s.tick,'formed':result.get('reader',{}).get('formed_native_command'),'snapshot':str(snapshot)},ensure_ascii=False))
if __name__=='__main__':main()
