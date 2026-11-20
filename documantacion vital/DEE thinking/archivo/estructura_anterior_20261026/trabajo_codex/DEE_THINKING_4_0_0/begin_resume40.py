"""Explicit user-authorized resumption; original deadline/cut remain immutable."""
import ctypes,hashlib,json,os,shutil,uuid
from datetime import datetime,timezone,timedelta
from pathlib import Path
ROOT=Path(__file__).resolve().parent
ctypes.windll.kernel32.GetTickCount64.restype=ctypes.c_uint64
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(p,x):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf-8')
def main():
    name=ROOT/'RESUMPTION_BUDGET.json'
    if name.exists():print(name.read_text());return
    now=datetime.now(timezone.utc);mono=int(ctypes.windll.kernel32.GetTickCount64())
    parent=ROOT.parents[1]/'4.0/DEE_thinking_4_0_0_ENTREGA_FINAL_RESULTADOS.zip'
    assert sha(parent)=='530b329829e15afb9387013142aa42f512a919b6577ce4956c986a2067be163d'
    sealed=ROOT/'sealed_parent'/parent.name;sealed.parent.mkdir(exist_ok=True);shutil.copy2(parent,sealed)
    for rel in ('VALIDATION_REPORT.json','BUILD_PROVENANCE.json','PRODUCT_CONTRACT.json','EXPERIMENT_REPORT.md','PHENOMENA_AND_LANGUAGE.json','MANIFEST.json','HASHES.sha256','README.md'):
        p=ROOT/rel;dest=ROOT/'validation/partial_cut'/rel;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dest)
    put(name,{'campaign':'DEE thinking4 resumption of incomplete scope','authorization':'User explicitly requested continuation of partial result without repeating closed work','start_utc':now.isoformat(),'deadline_utc':(now+timedelta(seconds=14400)).isoformat(),'budget_seconds':14400,'monotonic_start_ms':mono,'monotonic_deadline_ms':mono+14400000,'science_stop_seconds':13200,'original_budget_sha256':sha(ROOT/'BUDGET.json'),'parent_partial_zip_sha256':sha(parent),'original_budget_preserved':True})
    put(ROOT/'ACTIVE_BUDGET.json',{'record':'RESUMPTION_BUDGET.json','closed_marker':'CLOSED_RESUMPTION.json'})
    fixes=ROOT/'evidence/UNBUILT_CLOSURE_FIXES/source';copied=[]
    for p in fixes.rglob('*'):
        if p.is_file():
            rel=p.relative_to(fixes);target=ROOT/'source'/rel;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,target);copied.append({'path':rel.as_posix(),'sha256':sha(target)})
    put(ROOT/'validation/RESUMPTION_INTEGRATION.json',{'status':'RESTORED_PENDING_BUILD_AND_TEST','parent_partial_zip_sha256':sha(parent),'restored_files':copied,'closed_evidence_reused':['22 distinct C++ tests (two timeout retries resolved)','36 Python tests; rerun only affected facilitator module','CPC3 physical parity24+202 state boundaries','Dense/Parallel/Lazy/passive and C++→Python→C++ checks'],'pending':['affected Python facilitator tests','two unexecuted Python modules','new wheel clean install and seal','BLOQUEII23 planned trajectories','final extraction installation and continuation']})
    print(name.read_text())
if __name__=='__main__':main()
