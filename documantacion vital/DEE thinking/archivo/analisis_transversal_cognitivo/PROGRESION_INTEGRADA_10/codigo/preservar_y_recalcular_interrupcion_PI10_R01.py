"""Preserve exact failed primary plus honest partial denominators; no Native.

Completed episode witnesses and the failed host receipt remain separate.
Missing q1/q2/FI readings in an aborted opportunity are not extra Native
NULLs. A pipeline/codec failure is not scored as material destruction.
"""
from pathlib import Path
from datetime import datetime,timezone
import argparse,hashlib,importlib.util,json
H=Path(__file__).resolve().parent
def need(ok,why):
    if not ok:raise ValueError(why)
def sha(b):return hashlib.sha256(b).hexdigest()
def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--indice',type=Path,required=True);parser.add_argument('--primario-fallido',type=Path,required=True);args=parser.parse_args()
    source=args.primario_fallido;fb=source.read_bytes();failed=json.loads(fb)
    need(failed['status']=='failed_preserved'and failed['result']is None,'Exact failed-preserved primary with no fabricated result')
    error=json.loads(failed['error']);future=error['failed_native_future_preserved']
    need(error['detail']=='No expected-bit fallback for NULL current preview'and error['type']=='ValueError','This specific preserved preview-domain failure, not a generic execution error')
    need(error['external_execution_may_be_uncertain']is False and error['no_retry_or_rollback']is True,'Retain exact known Native future and no-retry status')
    spec=importlib.util.spec_from_file_location('audit',H/'recalcular_primarios_PI10_R02.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    recalc=m.bundle(args.indice);rows=recalc['rows'];need(rows and len({r['life_id']for r in rows})==1,'One stopped actual candidate, not combined branches')
    need(sorted(r['ordinal']for r in rows)==list(range(len(rows))),'All completed prefix opportunities')
    need(future['life_id']==rows[0]['life_id']and future['physical']['tick']==error['native_tick_after_attempt'],'Exact preserved candidate/cut')
    completed=len(rows);attempts=completed+1;reserved_complete=sum(r['reserved']for r in rows)
    ids={}
    for r in rows:
        for ident,status in r['receipt_id_status'].items():
            need(ident not in ids or ids[ident]==status,'Consistent own Native aliases');ids[ident]=status
    outdir=args.indice.parent/'FALLO';need(not outdir.exists(),'Never overwrite an earlier failed-future export');outdir.mkdir()
    exported=outdir/'PRIMARIO_FALLIDO_ORIGINAL.json'
    with exported.open('xb')as f:f.write(fb)
    need(source.read_bytes()==fb and exported.read_bytes()==fb,'Original failed primary preserved byte-for-byte without observed concurrent change')
    result={'schema':'DEE.PI10.stopped_pipeline_denominators.R01','at_utc':datetime.now(timezone.utc).isoformat(),
      'Native_executed':False,'DEE_imported':False,'candidate_life_id':future['life_id'],'preserved_Native_tick':future['physical']['tick'],
      'source_failed_primary':{'path':str(source.absolute()),'bytes':len(fb),'sha256':sha(fb),'exported_member':'FALLO/PRIMARIO_FALLIDO_ORIGINAL.json'},
      'closed_completed_bundle_index_sha256':sha(args.indice.read_bytes()),'last_completed_tick':max(r['after_tick']for r in rows),
      'completed_opportunity_Native_ticks':sum(r['Native_ticks']for r in rows),
      'additional_ticks_in_failed_attempt':future['physical']['tick']-max(r['after_tick']for r in rows),
      'denominators':{'planned_evaluation':18,'planned_reserved':12,'opportunities_attempted':attempts,'completed':completed,
        'codec_or_pipeline_failure_before_q1':1,'not_attempted':18-attempts,'reserved_completed':reserved_complete,
        'Native_q1_readings':completed,'Native_q1_formed':sum(r['q1_Native_choice']is not None for r in rows),
        'Native_q1_NULL':sum(r['q1_Native_choice']is None for r in rows),'q1_not_reached_in_failed_attempt':1,
        'Native_q2_readings':completed,'Native_FI_readings':completed,'physical_resources':sum(r['physical_delivered']for r in rows),
        'attributed_useful':sum(r['attributed_useful']for r in rows),'completed_whole_task_failures':sum(r['actual_failed']for r in rows),
        'not_completed_failure':1,'Native_requests_unique_completed_only':len(ids),'Native_applied_completed_only':sum(s=='applied'for s in ids.values()),
        'Native_rejected_completed_only':sum(s!='applied'for s in ids.values()),'failed_attempt_Native_requested':None,'failed_attempt_Native_applied':None},
      'failed_attempt_unobserved_fields':{'Native_q1_choice':None,'Native_q2_choice':None,'FI_choice':None,'resource_transfer':None,
        'meaning':'Not reached/no completed recorded result, not extra NULL, zero or a negative physical outcome.'},
      'preserved_failure_state':{'physical':future['physical'],'snapshot':future['snapshot'],'snapshot_sha256':future['snapshot_sha256'],
        'external_execution_may_be_uncertain':error['external_execution_may_be_uncertain'],'actor_own_pending':'Root separately reported preserved PI10 pending/uncertain; this failed primary omits its new metadata key, so do not infer cleared progress from ancestral dependencies.'},
      'failure_classification':'The fixed preview decoder rejected an actual Native observation outside its admitted domain before q1 was submitted. This is a concrete interface/pipeline limitation, not demonstrated loss of all memory or absence of Native activity.',
      'source_error_detail':error['detail'],'no_rollback_or_retry':True,'reserve_complete':False,'controlled_gain_evaluated':False,'automatic_adoption':False,
      'qualification':'A partial prefix4/5 is not18-case evidence or an independent validation of the question-value learning criterion. Receipt totals for the incomplete attempt remain unreported until exact Native receipts are separately extracted. Resource64B delivered after a NULLq1 remains physical but not attributed.'}
    output=outdir/'DENOMINADORES_Y_ESTADO_FALLO.json'
    with output.open('x',encoding='utf8')as f:json.dump(result,f,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps({'file':str(output),'sha256':sha(output.read_bytes()),'attempted':attempts,'completed':completed,'Native_executed':False}))
if __name__=='__main__':main()
