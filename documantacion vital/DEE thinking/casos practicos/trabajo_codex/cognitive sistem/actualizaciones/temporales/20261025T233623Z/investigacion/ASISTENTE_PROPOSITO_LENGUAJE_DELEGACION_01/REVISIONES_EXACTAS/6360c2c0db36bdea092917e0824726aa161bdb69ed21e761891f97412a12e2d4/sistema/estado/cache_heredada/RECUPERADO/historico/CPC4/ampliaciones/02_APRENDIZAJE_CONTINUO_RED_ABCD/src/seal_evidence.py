"""Post-hoc indexes, preservation checks and finite-cut technical accounting."""
from pathlib import Path
from datetime import datetime,timezone
import ctypes,json,sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from campaign import identity,put,sha

def main():
    from information_audit import run as audit
    from assemble_cut import main as assemble
    from auditor.global_coverage import run as coverage
    from auditor.review_closed_red import main as review
    audit();coverage();review();assemble()
    before=json.loads((ROOT/'PROVENANCE.json').read_text(encoding='utf-8'));now=identity()
    assert before['wheel_sha256']==now['wheel_sha256'] and before['pyd_sha256']==now['pyd_sha256']
    for name,h in before['immutable_artifacts'].items():assert sha(name)==h,name
    put(ROOT/'resultados/PRESERVATION_CHECK.json',{'original_record':before,'current_record':now,
      'original_product_zip_and_CPC3_unchanged':True,'frozen_wheel_pyd_kernel_unchanged':True,
      'parent_member_comparison':'Append packager separately compares every uncompressed inherited member to PARENT_MEMBERS.json before atomic publication.'})
    jobs=[]
    for p in sorted((ROOT/'jobs').glob('*/job.json')):
        data=json.loads(p.read_text(encoding='utf-8'));jobs.append({'path':p.relative_to(ROOT).as_posix(),'exit_code':data.get('exit_code'),
          'status':data.get('status'),'elapsed':data.get('elapsed'),'owned_windows_job':data.get('owned_windows_job')})
    budget=json.loads((ROOT/'BUDGET.json').read_text(encoding='utf-8-sig'))
    counter=ctypes.windll.kernel32.GetTickCount64;counter.restype=ctypes.c_ulonglong
    used=(int(counter())-budget['monotonic_start_ms'])/1000
    # Candidate extraction checks will be added without changing actor sources.
    checks={'schema':'CPC4.A02.validation_index.v1','created_utc':datetime.now(timezone.utc).isoformat(),
      'budget_seconds':14400,'elapsed_monotonic_seconds_at_index':used,
      'records':jobs,'nonzero_attempts_retained':[x for x in jobs if x['exit_code'] not in (0,None)],
      'public_ui_final':'resultados/technical/PUBLIC_UI_SEALED06/PUBLIC_UI_CHECKS.json',
      'normalized_runtime_technical_reference':'resultados/technical/CLEAN_WORKER_PREFLIGHT03/CLEAN_REPRODUCTION.json',
      'clean_extraction':'resultados/reproduccion_limpia/CLEAN_REPRODUCTION.json',
      'normalization_explained':'OrganizationalWorld::save_snapshot creates a Runtime copy and writes inert organizational.v1 chunks there. A live new Runtime may have none, a restored Runtime has a fresh envelope. Complete Runtime comparison removes ONLY that derived prefix on independent technical forks and normalizes backend options; actual RAW/clocks/tick/queue/channels/receipts/own protocol metadata remain. Organizational interfaces and external operations are compared separately.',
      'resource_estimates':{'basic_buffer_rule':'32*N^3 bytes, not measured RSS','N17':32*17**3,'N47':32*47**3,'N67':32*67**3,
        'scratch_clones_python_arrays_not_included':True},
      'ui_repairs':[{'issue':'Frontend sent salir twice after a completed event file','resolution':'Track closing response; retain first failed attempt and its exact frontend'},
        {'issue':'Language loader admitted foreign pending teacher and unchecked protocol flags','resolution':'Safe loader validates neutral progress and complete receipts; no physics change'},
        {'issue':'Failed cargar could replace live candidate before all protocol checks','resolution':'Transactional load; rejected commands leave live MAIN unchanged'},
        {'issue':'Completed directional protocol rejected a later saved continuation','resolution':'Keep completed historical boundary while current tick may increase; do not reactivate old linguistic decoder'},
        {'issue':'Test compared stale serialized organizational envelope with its newly saved representation','resolution':'Read native implementation, compare actual operative fields and normalized complete Runtime snapshots; no physical expectations changed; failed attempts retained'},
        {'issue':'Technical dictionary comprehension used map iteration instead of items','resolution':'Corrected the test only, before final UI validation'}],
      'no_global_cognitive_verdict':True}
    put(ROOT/'resultados/VALIDATION_INDEX.json',checks)
    print(json.dumps({'post_hoc_index':'complete','seconds_from_original_start':used,'jobs':len(jobs),'retained_nonzero':len(checks['nonzero_attempts_retained'])}))

if __name__=='__main__':main()
