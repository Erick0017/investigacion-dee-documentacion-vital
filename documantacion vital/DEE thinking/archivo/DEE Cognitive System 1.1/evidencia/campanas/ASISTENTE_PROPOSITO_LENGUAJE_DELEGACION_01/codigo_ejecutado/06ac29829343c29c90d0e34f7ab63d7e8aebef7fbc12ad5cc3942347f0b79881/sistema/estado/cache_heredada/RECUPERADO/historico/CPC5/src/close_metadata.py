"""External close accounting. No simulation and no modification of prior products."""
from datetime import datetime, timezone
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import ROOT, identity, put, sha
from supervisor import remaining


def finalize():
    """Close the saved scientific cut using completed, non-circular clean proof."""
    proof_path=ROOT/'resultados/reproduccion_limpia_prepublicacion/CLEAN_REPORT.json'
    proof=json.loads(proof_path.read_text(encoding='utf-8'))
    assert proof['status']=='VERIFIED' and proof.get('error') is None
    assert len(proof['commands'])==12
    assert all(x['status']=='COMPLETED' and x['exit_code']==0 for x in proof['commands'])
    plan=ROOT/'configuraciones/clean_reproduction_plan.json'
    assert proof['plan_sha256']==sha(plan)
    assert all(all(x['assertions'].values()) for x in proof['explicit_posttrajectory_verification'])
    now=datetime.now(timezone.utc).isoformat()
    left=remaining()
    assert left>0, 'Original campaign deadline has expired; no finalization budget reset is allowed'
    validation=json.loads((ROOT/'VALIDATION_REPORT.json').read_text(encoding='utf-8'))
    for parent in validation['originals_unchanged']:
        assert sha(ROOT.parents[1]/parent['file'])==parent['sha256']
    validation.update({
        'status':'TECHNICAL_CHECKS_AND_CLEAN_PREPUBLICATION_REPRODUCTION_VERIFIED',
        'cut_closed_utc':now,
        'clean_reproduction':{'path':str(proof_path.relative_to(ROOT)),
                              'sha256':sha(proof_path),
                              'tested_prepublication_candidate_sha256':proof['candidate_sha256'],
                              'setup_and_reproduction_commands':len(proof['commands']),
                              'all_exit_codes_zero':True,
                              'scope':'This embedded proof identifies the earlier candidate explicitly. The exact final ZIP proof is an external sidecar, avoiding a circular archive identity.'},
        'reconciled_counts':'revision/CONTEOS_RECONCILIADOS.json',
        'scientific_evidence_index':'revision/INDICE_EVIDENCIA.json',
        'scientific_scope':'Measured cases, counterexamples, local mechanisms and remaining questions are reported individually; technical verification is not a global scientific verdict.',
        'exact_final_archive_verification':'CPC5_VERIFICACION_FINAL.json beside the canonical ZIP; produced only after exact-candidate clean reproduction and publication.'})
    put(ROOT/'VALIDATION_REPORT.json',validation)
    state=json.loads((ROOT/'REANUDACION.json').read_text(encoding='utf-8'))
    state.update({'status':'SAVED_CUT_CLOSED_FINAL_ARCHIVE_VERIFICATION_AND_PUBLICATION_ONLY',
                  'cut_closed_utc':now,'remaining_seconds':left,'consumed_seconds':14400-left,
                  'active_supervised_jobs':[],'active_scientific_jobs':[],
                  'completed_since_resume':['Scientific case coverage and causal controls frozen in revision/INDICE_EVIDENCIA.json',
                                            'Public demos, backend/passive/fork/persistence technical validation',
                                            'Clean extraction, offline installation and directed reproduction: all12 commands exit0'],
                  'next_tasks':['Seal exact final candidate','Verify exact final candidate in clean extraction','Atomic publication and delivery'],
                  'main_resume_checkpoint':'resultados/compound_reuse_confirmation/CORE_QUIET_RETENTION1008/MAIN_FINAL_T1008.deetsnap',
                  'checkpoint_scope':'Saved outcome at tick1008; future experiences must respect current occupancy, phase and finite resources. Loading does not renew consumed products.',
                  'original_budget_not_reset':True})
    put(ROOT/'REANUDACION.json',state)
    counts=json.loads((ROOT/'revision/CONTEOS_RECONCILIADOS.json').read_text(encoding='utf-8'))
    put(ROOT/'CLOSED.json',{'schema':'CPC5.closed-cut.v1','cut_closed_utc':now,
        'status':'SCIENTIFIC_CUT_CLOSED_TECHNICAL_REPRODUCTION_VERIFIED',
        'primary_records':counts['primary_records'],
        'historical_reproductions':counts['directed_historical_reproductions'],
        'original_budget':json.loads((ROOT/'BUDGET.json').read_text(encoding='utf-8')),
        'consumed_seconds_at_cut_close':14400-left,
        'no_scientific_jobs_active':True,'no_background_work_after_handoff':True,
        'final_publication_receipt':'External CPC5_VERIFICACION_FINAL.json records the exact archive identity and publication verification.',
        'scientific_remaining_objectives':'revision/LECTURA_PROVISIONAL.md and revision/NSM65_EVIDENCIAS.json preserve the unfulfilled domains; no new experiments are scheduled.',
        'resume_requires_new_explicit_authorization':True})
    print(json.dumps({'status':state['status'],'remaining_seconds':left,'commands_verified':12,'originals_unchanged':True}))


def main():
    if '--finalize' in sys.argv:
        finalize()
        return
    cases=ROOT.parents[1]
    expected={
        'CPC4_COMUNICACION_NATIVA_Y_META_ROSETTA_RESULTADOS.zip':'4a14a81f913a434a8e54e47c0c700d7ee54418bb16913aedded8bf49a3294723',
        'CPC3_ENTE_COGNITIVO_CAUSAL_DEE_3_5_0_RESULTADOS.zip':'1c10b8501ff0bb9756d6b1ebe5876a63ae7300ec4722d651e94dfe9e8f45a0f6'}
    parents=[]
    for name,h in expected.items():
        path=cases/name;actual=sha(path)
        assert actual==h
        parents.append({'file':name,'sha256':actual,'bytes':path.stat().st_size,'unchanged':True})
    kernel=ROOT/'referencias/producto4/kernel_v27.cpp'
    assert sha(kernel)=='fbd8190381ed76085f404e6578ff15fe185ab66cd48c67300d2abad61ddc7e31'
    version=identity()
    artifact={'schema':'CPC5.provenance.v1','created_utc':datetime.now(timezone.utc).isoformat(),
              'project':'DEE Universe / INVESTIGACION DEE','author':'Ivan Erick Tlaltecatl Morales',
              'instrument':version,'kernel_source':{'path':str(kernel.relative_to(ROOT)),'sha256':sha(kernel)},
              'frozen_parent_archives':parents,'source_selection':'Selected mechanisms and source only; no historical archive or entire corpus nested',
              'runtime_implementation':'Official native4.0.0 binary. New Python code prepares ports, presents events and observes; no second physics, response table or LLM.',
              'scientific_sources':'referencias/ and per-case code hashes; executed source versions retained',
              'models_separated':['native evolution','external experience protocol','physical probe','passive observation','diagnostic fork','external posthoc auditor'],
              'original_budget':json.loads((ROOT/'BUDGET.json').read_text(encoding='utf-8')),
              'remaining_seconds_at_accounting':remaining()}
    put(ROOT/'PROVENANCE.json',artifact)
    checks=ROOT/'resultados/technical_suite_01/TECHNICAL_CHECKS.json'
    validation={'schema':'CPC5.validation.v1','status':'LOCAL_TECHNICAL_CHECKS_COMPLETE_CLEAN_EXTRACTION_PENDING',
                'instrument':version,'originals_unchanged':parents,
                'technical_evidence':{'path':str(checks.relative_to(ROOT)),'sha256':sha(checks)},
                'completed':['DenseSequential/Lazy/DenseParallel relevant full state equivalence',
                             'passive tracker unchanged RAW/clocks and bounded trace',
                             'deep fork isolation','pending input save/load across process',
                             'lexical and compound public APIs','continued live integrated demonstration',
                             'historical states matched in8 targeted reproductions'],
                'old_snapshot_metadata_nuance':'A serialization envelope can appear after load. Both original mismatch and reconciliation retain physical and operational comparisons; no kernel change.',
                'clean_reproduction_plan':'configuraciones/clean_reproduction_plan.json',
                'clean_plan_sha256':sha(ROOT/'configuraciones/clean_reproduction_plan.json'),
                'final_ZIP_identity':'Reported externally after closing the ZIP; not embedded in itself',
                'scientific_global_verdict':None}
    put(ROOT/'VALIDATION_REPORT.json',validation)
    state=json.loads((ROOT/'REANUDACION.json').read_text(encoding='utf-8'))
    state.update({'status':'SCIENTIFIC_CASES_FROZEN_TECHNICAL_REPRODUCTION_AND_PACKAGING',
                  'freeze_utc':datetime.now(timezone.utc).isoformat(),'remaining_seconds':remaining(),
                  'consumed_seconds':14400-remaining(),'active_scientific_jobs':[],
                  'main_resume_checkpoint':'resultados/compound_reuse_confirmation/CORE_QUIET_RETENTION1008/MAIN_FINAL_T1008.deetsnap',
                  'next_tasks':['Clean independent reproduction','Final manifest/CRC/hash verification','Atomic publication']})
    put(ROOT/'REANUDACION.json',state)
    print(json.dumps({'status':state['status'],'remaining_seconds':remaining(),'originals_unchanged':True}))


if __name__=='__main__':main()
