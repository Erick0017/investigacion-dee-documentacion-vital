"""Reconcile the completed cut; never changes primary scientific records."""
import argparse
import ctypes
from datetime import datetime,timezone
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import ROOT,BASE,put,sha

PARENT='26c5b0f207b235b6f5990d85f586a5bd7dde440eeb989c4ae5e7eb47fe54b075'

def read(path):return json.loads(Path(path).read_text(encoding='utf-8'))

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--stage',choices=['VALIDATION_PENDING','SEALED'],required=True)
    parser.add_argument('--clean-proof',type=Path);a=parser.parse_args()
    budget=read(ROOT/'BUDGET.json');counter=ctypes.c_longlong()
    if not ctypes.windll.kernel32.QueryPerformanceCounter(ctypes.byref(counter)):raise OSError('QPC failed')
    elapsed=(counter.value-budget['start_qpc'])/budget['qpc_frequency']
    now=datetime.now(timezone.utc);assert elapsed>=0 and elapsed<budget['budget_seconds']
    index=read(ROOT/'revision/INDICE_EVIDENCIA.json')
    sources=[]
    for path in sorted((ROOT/'src').glob('*.py')):
        sources.append({'path':path.relative_to(ROOT).as_posix(),'sha256':sha(path)})
    configs=[{'case_id':c['case_id'],'config':c.get('config'),'config_sha256':c.get('config_sha256'),
              'source_sha256':c.get('source_sha256'),'family':c['family'],'declared_phase':c.get('declared_phase')}
             for c in index['cases']]
    put(ROOT/'EXPERIMENT_CONFIG.json',{'schema':'CPC5.extension.executed-config-index.v1',
        'scope':'Post-trajectory inventory, NOT a retrospective claim of global preregistration. Original case configurations, criteria, discovery/reservation labels, failures and exact source versions are retained.',
        'budget':'BUDGET.json','source_matrix':'revision/SOURCES.json','parent_sha256':PARENT,
        'cases':configs,'current_auxiliary_source_versions':sources,'updated_utc':now.isoformat()})
    checks={
        'physical_and_operative_technical_checks':'resultados/technical_extension_01/TECHNICAL_CHECKS.json',
        'previous_case_reproduced':'resultados/reference_reproduction_check.json',
        'target_free_minimal_application':'resultados/minimal_app_03/MINIMAL_REPORT.json'}
    verified=[]
    for name,rel in checks.items():
        path=ROOT/rel;assert path.is_file();data=read(path)
        if name=='physical_and_operative_technical_checks':
            assert all(data[key] for key in ('trace_budget_preserves_world_advance','other_process_before_equal','other_process_after_equal','deep_fork_initial_equal','fork_MAIN_unchanged'))
            assert data['other_process_exit_code']==0
        if name=='target_free_minimal_application':assert data['verified']
        verified.append({'test':name,'evidence':rel,'sha256':sha(path),'result':data})
    clean=None
    if a.clean_proof:
        clean=read(a.clean_proof);assert clean['status']=='VERIFIED'
        clean={'evidence':str(a.clean_proof.relative_to(ROOT)),'sha256':sha(a.clean_proof),
               'candidate_sha256':clean['candidate_sha256'],'status':clean['status'],
               'scope':'Proof of this explicitly identified preliminary candidate. Exact final-candidate proof is supplied externally after sealing, avoiding self-referential archive identities.'}
    if a.stage=='SEALED' and clean is None:raise ValueError('A sealed cut requires preliminary clean verification')
    put(ROOT/'VALIDATION_REPORT.json',{'schema':'CPC5.extension.validation-summary.v1','status':a.stage,
        'engine_unchanged':read(ROOT/'PROVENANCE.json')['instrument'],'checks':verified,'clean_candidate':clean,
        'scientific_census':index['census'],'primary_records':index['primary_records'],
        'technical_incidents_preserved':[
            {'evidence':'resultados/dialogue_context_replay_longitudinal_diagnostic/FAILED_EQUALITY.json','scope':'A strict cached-framework-envelope equality check failed after physical and mutable/session equality. The failure remains INSTRUMENTATION_ERROR; no failed assert is relabelled PASS.'},
            {'evidence':'jobs/minimal_app_01/stderr.log','scope':'Windows legacy-codepage stderr was not UTF-8; output capture now preserves bytes.'},
            {'evidence':'resultados/minimal_app_02/STDERR.log','scope':'Nested Windows cwd exceeded CreateProcess path tolerance; a fresh explicit short staging root passed without changing physics.'}],
        'check_coverage':'CRC, preservation and new member hashes are container tests, not substitutes for native functional replay.',
        'current_stage_utc':now.isoformat(),'elapsed_monotonic_seconds':elapsed})
    checkpoints=[]
    for rel in ['resultados/capacity_longitudinal','resultados/dialogue_longitudinal','resultados/network_dialogue','resultados/order_access_extension','resultados/demo_longitudinal_01']:
        directory=ROOT/rel
        paths=sorted(directory.rglob('*.deetsnap')) if directory.exists() else []
        if paths:
            path=paths[-1];checkpoints.append({'file':path.relative_to(ROOT).as_posix(),'sha256':sha(path)})
    put(ROOT/'REANUDACION.json',{'schema':'CPC5.extension.resume.v2','status':a.stage,
        'budget':budget,'elapsed_monotonic_seconds':elapsed,'wall_utc':now.isoformat(),
        'parent_sha256':PARENT,'completed_tasks':['Exact parent inventory','8/16/32/65 physical correspondences and longitudinal controls',
            '12-component matched architectural screen','Order, later form and context controls','Noncommutative learned-route composition',
            'Native request-return and delayed acquisition in MAIN','One-to-four shared-Runtime dialogue networks',
            'Separate-process continuations','Public demonstrator','Backend/passivity/admission/deep-fork checks','Directed previous reference replay'],
        'active_scientific_tasks':[],'next_task':'Final exact-candidate reproduction and atomic publication' if a.stage!='SEALED' else 'Exact final-candidate verification/publication; no new science',
        'resumable_examples':checkpoints,'checkpoint_index':'revision/INDICE_EVIDENCIA.json',
        'no_background_continuation':True,'future_resume_requires_authorization':True,'no_budget_reset':True})
    if a.stage=='SEALED':
        put(ROOT/'CLOSED.json',{'schema':'CPC5.extension.closed-cut.v1','stage':'SCIENCE_AND_PAYLOAD_SEALED',
            'elapsed_monotonic_seconds':elapsed,'utc':now.isoformat(),'budget':'BUDGET.json','primary_records':index['primary_records'],
            'pending':'Only exact final-candidate clean reproduction and atomic publication, reported outside ZIP. No experiment continues after publication.',
            'scope':'This is the scientific payload close, not a claim of a self-contained hash of its own container.'})
    print(json.dumps({'stage':a.stage,'primary_records':index['primary_records'],'elapsed_seconds':elapsed}))

if __name__=='__main__':main()
