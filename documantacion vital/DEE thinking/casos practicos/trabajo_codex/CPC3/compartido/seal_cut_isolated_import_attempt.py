"""Record closure of measured finite cut. No simulation is executed here."""
import argparse,hashlib,json
from datetime import datetime,timezone
from pathlib import Path
from supervise import Budget,atomic_json
def main():
    p=argparse.ArgumentParser();p.add_argument('--root',required=True);p.add_argument('--phase',choices=['publication','cleanup_recorded'],default='publication');a=p.parse_args();root=Path(a.root).resolve();budget=Budget(root)
    proof=json.loads((root/'resultados/CLEAN_REPRODUCTION.json').read_text(encoding='utf-8'))
    assert all(proof.get(k) for k in ('verified','inherited_reference_reproduced','new_result_reproduced','snapshot_new_question','no_old_path_dependency'))
    jobs=[json.loads(q.read_text(encoding='utf-8')) for q in (root/'compartido/ACTIVE').glob('*.json')]
    assert not [q for q in jobs if q.get('status')=='RUNNING']
    for rel,digest in {**proof['critical_source_hashes'],**proof['critical_artifact_hashes']}.items():assert hashlib.sha256((root/rel).read_bytes()).hexdigest()==digest,rel
    migration=json.loads((root/'MIGRACION_Y_LIMPIEZA.json').read_text(encoding='utf-8'));coverage=json.loads((root/'resultados/CASE_COVERAGE.json').read_text(encoding='utf-8'))
    checkpoint=root/'checkpoints/continuidad/BA_FULL/MAIN_FINAL.deetsnap'
    report={'campaign':'CPC3','author':'Ivan Erick Tlaltecatl Morales','library':'DEE thinking3.5.0 frozen','kernel':27,'phase':a.phase,'original_budget':budget.data,'elapsed_seconds':budget.elapsed(),'recorded_utc':datetime.now(timezone.utc).isoformat(),'source_profiles':'Distinct worlds: continuous N47; central comparison N47; finite revisable policy N67; association N34/cascade N127. No fusion of individuals.','scientific_coverage':coverage['scientific_summary'],'independent_qualification':{'verified':proof['verified'],'tested_package_sha256':proof['package_sha256'],'critical_code_unchanged':True,'scope':'Final package adds qualification evidence, closure and cleanup receipts; tested scientific/public-code bytes are unchanged.'},'main_checkpoint':{'path':checkpoint.relative_to(root).as_posix(),'absolute_tick':1032,'elapsed_native_ticks':1000,'sha256':hashlib.sha256(checkpoint.read_bytes()).hexdigest()},'finite_policy_measurement':'P retained on agreement; Q selected on discrepancy; four treatments plus two reserves receive faithful report under complementary-source, single-revision domain.','limits':['No indefinitely integrated compare/rewrite/reselect loop demonstrated','Rule retainP/switchQ is physically prepared, not learned from scratch','Spanish grammar and aliases external; acquired relations/composition numeric, not arbitrary semantics'],'migrated_members':len(migration['migrated']),'cleanup_status':migration['cleanup_status'],'owned_jobs_status_counts':{s:sum(q.get('status')==s for q in jobs) for s in sorted({q.get('status','UNKNOWN') for q in jobs})},'scientific_global_verdict':None}
    atomic_json(root/'resultados/RUN_SUMMARY.json',report)
    atomic_json(root/'compartido/CLOSED.json',{'reason':'finite scientific cut and independent qualification complete','partial_emergency_cut':False,'elapsed_seconds':budget.elapsed(),'utc':datetime.now(timezone.utc).isoformat(),'owned_running_jobs':0,'phase':a.phase})
    print(json.dumps({'phase':a.phase,'elapsed_seconds':budget.elapsed(),'cleanup_status':migration['cleanup_status'],'migrated_members':len(migration['migrated']),'owned_running_jobs':0}))
if __name__=='__main__':main()
