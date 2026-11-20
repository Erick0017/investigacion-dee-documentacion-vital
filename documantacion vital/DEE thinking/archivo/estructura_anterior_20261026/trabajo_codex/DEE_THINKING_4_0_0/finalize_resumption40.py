"""Aggregate existing evidence and seal release metadata; never rerun science.

--verified is accepted only after actual clean extraction/install/trajectory
checks. Technical release status is not a scientific or ontological verdict.
"""
import argparse,hashlib,json,shutil,sys,zipfile
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parent
if ROOT.name=='tools':ROOT=ROOT.parent
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def put(p,x):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,ensure_ascii=False,indent=2,default=str),encoding='utf-8')
def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
    return h.hexdigest()
def main():
    p=argparse.ArgumentParser();p.add_argument('--verified',action='store_true');a=p.parse_args()
    qualified=read(ROOT/'validation/BLOCK_I_QUALIFICATION.json');assert qualified['qualified']
    wheel=ROOT/'wheel/dee_thinking-4.0.0-cp313-cp313-win_amd64.whl';assert sha(wheel)==qualified['wheel_sha256']
    unit={}
    for folder in ('python_02','python_resume_03'):
        for file in (ROOT/'validation'/folder).glob('test*.json'):unit[file.name]=read(file)
    assert len(unit)==8 and all(x['success'] for x in unit.values())
    block=read(ROOT/'experiments/BLOCK_II/RESULTS.json');assert len(block['cases'])==24 and all(x.get('status')!='TECHNICAL_ERROR' for x in block['cases'])
    validation=read(ROOT/'validation/partial_cut/VALIDATION_REPORT.json')
    status='RELEASE_VERIFIED' if a.verified else 'RELEASE_CANDIDATE_FINAL_EXTRACTION_PENDING'
    checks=read(ROOT/'validation/FINAL_EXTRACTION_CHECK.json') if (ROOT/'validation/FINAL_EXTRACTION_CHECK.json').exists() else None
    if a.verified:assert checks and checks['all_commands_succeeded'] and checks['installed_wheel_sha256']==qualified['wheel_sha256'] and checks['trajectory_reproduction_equal'] and checks['native_app_pending_restore_continue']
    originals=[]
    for parent in read(ROOT/'PARENTS.json'):
        value=sha(parent['path']);assert value==parent['sha256'];originals.append({'path':parent['path'],'sha256':value,'unchanged':True})
    with zipfile.ZipFile(Path(originals[0]['path']).parents[1]/'3.5/dee_thinking-3.5.0-cp313-cp313-win_amd64.whl') as old:
        names=[n for n in old.namelist() if n.endswith('.pyd')];old_binary=hashlib.sha256(old.read(names[0])).hexdigest()
    assert old_binary!=qualified['native_sha256']
    report={'status':status,'version':'4.0.0','kernel':27,'wheel_sha256':qualified['wheel_sha256'],'native_sha256':qualified['native_sha256'],'kernel_source_sha256':qualified['kernel_source_sha256'],
      'block_I':{'qualified_before_block_II':True,'qualification':'validation/BLOCK_I_QUALIFICATION.json','cpp_unique_tests':22,'cpp_initial_and_retry_attempts':validation['block_I']['cpp_tests'],'python_unique_methods':sum(x['run'] for x in unit.values()),'python_modules':[{'name':n,'methods':x['run'],'success':x['success'],'failures':x['failures'],'errors':x['errors'],'skipped':x['skipped']} for n,x in unit.items()],
        'reused_without_rerun':['unchanged C++22 tests and external C++ consumer','CPC3 exact physical parity24+202 boundaries','Dense/Parallel/Lazy, passive observation and C++→Python→C++ continuation','five unmodified Python modules (29 methods)'],
        'resumption_executed':['repackage corrected Python/stubs into new final wheel','noneditable clean installation and all package bytes check','9 affected facilitator methods','14 organizational methods previously unexecuted','9 MBP4 regression methods previously unexecuted','owned process-tree timeout containment'],
        'compatibility':'Runtime v1/v2 and inherited organizational snapshots retained; legacy CPC3 Python session import explicitly physical only','pending_tests':[]},
      'block_II':{'status':'EXECUTED_ON_QUALIFIED_4_0','batch_case_records':24,'not_independent_when_sharing_contact_measurements':True,'case_ids':[x['identity'] for x in block['cases']],
        'records':'experiments/BLOCK_II/RESULTS.json','technical_evidence_check':'experiments/BLOCK_II/TECHNICAL_EVIDENCE_CHECKS.json','mechanism_review':'docs/RESULTS_MECHANISM_REVIEW.json','same_runtime_native_chain':{'contact_tick5':36,'acquired_relation_tick8':41,'main_queries':[13,19],'main_responses':[54,73],'reserved_queries':[17,23],'reserved_responses':[58,81],'route_and_cue_controls':[13,19],'scope':'finite moving relation, two consuming probes; not an indefinitely renewable basal body'},
        'native_demonstrations':'experiments/BLOCK_II/online_demonstrator_main and online_demonstrator_reserved','signal_prediction_extension':'experiments/SIGNAL_PREDICTION/RESULTS.json' if (ROOT/'experiments/SIGNAL_PREDICTION/RESULTS.json').exists() else None},
      'final_clean_extraction':checks,'engineering_incidents':validation['operational_errors']+[{'resolved':'post-partial Python alias collision, real receipt export and active semantic5 predicate','preserved':'validation/source_revisions and evidence/UNBUILT_CLOSURE_FIXES','integrated_and_tested':True}],
      'scope_limits':['physical signal/contact profiles are not calibrated external temperature or inertial mass','labels are external interface names; acquired functions are bounded native relational transformations','why responses retain instrument/documentary attribution; no spontaneous introspection claim','N34/N47/N67/N127 are separate finite realizations, not silently fused into one MAIN','no external-universe measurement was performed'],
      'originals':originals,'partial_cut_parent_sha256':read(ROOT/'RESUMPTION_BUDGET.json')['parent_partial_zip_sha256'],'budget_original':read(ROOT/'BUDGET.json'),'budget_resumption':read(ROOT/'RESUMPTION_BUDGET.json'),'updated_utc':datetime.now(timezone.utc).isoformat(),'automatic_scientific_verdict':False}
    put(ROOT/'VALIDATION_REPORT.json',report)
    provenance={'status':status,'wheel_sha256':qualified['wheel_sha256'],'native_sha256':qualified['native_sha256'],'native_3_5_reference_sha256':old_binary,'native_binary_new_4_0_not_renamed_3_5':old_binary!=qualified['native_sha256'],'kernel_sha256':qualified['kernel_source_sha256'],'kernel_unchanged':True,'build_wheel':read(ROOT/'BUILD_wheel.json'),'build_cpp':read(ROOT/'BUILD_cpp.json'),'cpp_consumer':read(ROOT/'BUILD_consumer.json'),'resumption_change_scope':'Python facilitators/stubs only; exact already compiled native4 binary preserved','native_source_audit':'validation/release_continuation_source_audit.json','dependencies':read(ROOT/'validation/partial_cut/BUILD_PROVENANCE.json')['dependencies'],'originals':originals}
    put(ROOT/'BUILD_PROVENANCE.json',provenance)
    signal=ROOT/'experiments/SIGNAL_PREDICTION/RESULTS.json'
    if signal.exists():
        signal_data=read(signal);report['block_II']['signal_prediction_extension_records']=len(signal_data['cases']);report['block_II']['scientific_case_records_total']=24+len(signal_data['cases']);report['block_II']['prediction_scope']='Current local observed class retained in native history predicts a fixed prepared toroidal-return window; no acquisition of arbitrary period, and one inaccessible-obstacle error retained';put(ROOT/'VALIDATION_REPORT.json',report)
    contract=read(ROOT/'PRODUCT_CONTRACT.json');contract['release_status']=status;contract['block_II_executed']=True;contract['validation_report']='VALIDATION_REPORT.json';contract['release_wheel_sha256']=qualified['wheel_sha256'];contract['new_science_scope']='EXPERIMENT_REPORT.md';contract['application_native_world']={'path':'app/mundo_nativo.py','mode':'prepared N47 native world plus physical probes, external names and passive presentation','horizon':21,'renewable':False};put(ROOT/'PRODUCT_CONTRACT.json',contract)
    put(ROOT/'validation/RESUMPTION_INTEGRATION.json',{**read(ROOT/'validation/RESUMPTION_INTEGRATION.json'),'status':'INTEGRATED_BUILT_INSTALLED_AND_TESTED','final_wheel_sha256':qualified['wheel_sha256'],'affected_tests':'validation/python_resume_03/test_cognition_facilitators.json'})
    critical=[]
    for name in ('online_contact_main','reserved_online_contact','online_demonstrator_main','online_demonstrator_reserved','spanish_new_combined_question'):
        for file in (ROOT/'experiments/BLOCK_II'/name).glob('*.deetsnap'):critical.append({'path':file.relative_to(ROOT).as_posix(),'sha256':sha(file),'size':file.stat().st_size})
    put(ROOT/'checkpoints/INDEX.json',{'single_copy':'Snapshots remain beside the exact case recipe and telemetry; this index avoids duplicates','critical':critical})
    put(ROOT/'results/RUN_SUMMARY.json',{'technical_release_status':status,'cpp_unique_tests':22,'python_unique_methods':report['block_I']['python_unique_methods'],'batch_case_records':24,'scientific_case_records_total':report['block_II'].get('scientific_case_records_total',24),'primary_evidence':'experiments/BLOCK_II/RESULTS.json','additional_prediction_extension':report['block_II']['signal_prediction_extension'],'counts_are_not_capabilities_or_independent_samples':True})
    for name in ('EXPERIMENT_REPORT.md','PHENOMENA_AND_LANGUAGE.json'):
        shutil.copy2(ROOT/'experiments'/name,ROOT/name)
    for name in ('build40.ps1','begin_resume40.py','finalize_resumption40.py'):
        shutil.copy2(ROOT/name,ROOT/'tools'/name)
    shutil.copytree(ROOT/'jobs',ROOT/'validation/jobs',dirs_exist_ok=True)
    print(json.dumps({'status':status,'wheel_sha256':qualified['wheel_sha256'],'cpp':22,'python':report['block_I']['python_unique_methods'],'batch_cases':24},indent=2))
if __name__=='__main__':main()
