"""Read only the stopped failed Full-copy journal; never retries an action."""
import argparse,hashlib,json,sqlite3
from pathlib import Path
def read(p):return json.loads(p.read_bytes())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    p=argparse.ArgumentParser();p.add_argument('--extraido',type=Path,required=True);p.add_argument('--externo',type=Path,required=True);p.add_argument('--salida',type=Path,required=True);a=p.parse_args();root=a.extraido.resolve();life='APD02_DIST_R01';folder=root/'trabajo_personal/resultados'/('ENTREGA_'+life);primary=folder/'PRUEBA_SERVICIO_APD02.json';x=read(primary);external=read(a.externo);db=root/'trabajo_personal/estado/servicios_persistentes'/life/'cola.sqlite3';wal=db.with_name('cola.sqlite3-wal')
    if wal.exists()and wal.stat().st_size:raise ValueError('Never use immutable over nonempty WAL')
    before=sha(db);con=sqlite3.connect(db.as_uri()+'?mode=ro&immutable=1',uri=True);con.row_factory=sqlite3.Row
    try:
        integrity=con.execute('PRAGMA integrity_check').fetchone()[0];ownerrow=con.execute('SELECT value FROM meta WHERE key=?',('owner',)).fetchone();owner=json.loads(ownerrow[0]);request=dict(con.execute('SELECT * FROM requests WHERE id=?',('apd02full_r01_queued_delta_zero',)).fetchone());outstanding=[dict(v)for v in con.execute("SELECT id,status,payload,payload_sha FROM requests WHERE status IN ('queued','processing','uncertain')")]
    finally:con.close()
    if owner.get('running')is not False:raise ValueError('Diagnostic requires actual stopped own owner')
    result={'schema':'APD02.FullR01.zero_wait_wrapper_diagnosis.N0','new_native_ticks':0,'requeued_actions':0,'primary':{'sha256':sha(primary),'bytes':primary.stat().st_size},'external_failure':external['error'],'first_zero_wait_response':x['results']['queued_delta_zero'],'same_ID_actual_closed_journal_row':request,'outstanding':outstanding,'journal_integrity':integrity,'journal_SHA_before':before,'journal_SHA_after':sha(db),'journal_byte_unchanged':before==sha(db),'owner':owner,'exact_import':x['exact_import'],'baseline_memory_RAW':x['baseline_memory_RAW'],'after_teaching_memory_RAW':x['after_teaching_memory_RAW'],'declared_beta_revision_verified':x['declared_teaching_is_verified_new_revision'],'teacher_admission':x['teacher_actual_admission'],'delta_before':x['delta_before'],'raw128':x['raw128_reader_audit'],'APD_audits':x['APD_archived_audits'],'function_audits':x.get('function_archived_audits'),'goal_before_reload':x['goal_before_reload'],'functional_issues':x['functional_issues'],'owned_close':x['owned_close'],'originals_unchanged':external['originals_unchanged'],'zip_unchanged':external['zip_unchanged'],'scope':'Only this own stopped R01 copy is read. The zero-wait response was an admission summary; its queued request is real, unconsumed and not resubmitted. The incomplete goal is separate external world state. No main-world inference, new tick, continuation, table repair or source edit.'}
    with a.salida.open('x',encoding='utf8')as f:json.dump(result,f,sort_keys=True,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps({'integrity':integrity,'same_ID_status':request['status'],'same_ID':request['id'],'outstanding':len(outstanding),'owner_running':owner['running'],'journal_unchanged':before==sha(db),'beta_new_revision':result['declared_beta_revision_verified'],'raw128':x['raw128_reader_audit']['native_aggregate_from_RAW'],'functional_issues':x['functional_issues'],'new_native_ticks':0}))
if __name__=='__main__':main()

