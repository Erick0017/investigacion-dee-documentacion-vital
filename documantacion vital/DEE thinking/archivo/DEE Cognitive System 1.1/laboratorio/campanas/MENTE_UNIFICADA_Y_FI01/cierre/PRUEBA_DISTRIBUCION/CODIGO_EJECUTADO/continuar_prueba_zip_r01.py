"""Finish the preserved first extraction after an export-client timeout.

This is an explicit operational harness revision, not historical science and
not a new import. It never submits the already queued material FINISH twice.
All actor/runtime/manager bytes continue to come from the first exact ZIP.
"""
import argparse
import hashlib
import importlib.util
import json
import sqlite3
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path


def read(p):return json.loads(Path(p).read_bytes())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,value):
    p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('x',encoding='utf8')as f:json.dump(value,f,ensure_ascii=False,sort_keys=True,indent=2);f.write('\n')


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--raiz-extraida',type=Path,required=True)
    ap.add_argument('--prueba-previa',type=Path,required=True)
    ap.add_argument('--helper-corregido',type=Path,required=True)
    ap.add_argument('--protocolo',type=Path,required=True)
    ap.add_argument('--salida',type=Path,required=True)
    a=ap.parse_args();root=a.raiz_extraida.resolve(strict=True)
    previous=read(a.prueba_previa);life='MUFI_COLLAB_PRUEBA';folder=root/'trabajo_personal/resultados'/('ENTREGA_'+life)
    result=read(folder/'PRUEBA_SERVICIO.json');card=root/'trabajo_personal/estado/vidas'/life/'VIDA.json'
    db=root/'trabajo_personal/estado/servicios_persistentes'/life/'cola.sqlite3'
    if not all(sha(Path(p))==s for p,s in previous['originals_before'].items()):raise ValueError('A protected source changed before continuation')
    if sha(previous['zip'])!=previous['zip_sha256']:raise ValueError('First exact ZIP changed before continuation')
    if read(card)['physical']['tick']!=105605:raise ValueError('Preserved first-copy boundary changed; no silent rollback')
    wal=Path(str(db)+'-wal')
    if wal.exists()and wal.stat().st_size:raise ValueError('Live WAL blocks immutable read of stopped queue')
    with sqlite3.connect(db.as_uri()+'?mode=ro&immutable=1',uri=True)as c:
        c.row_factory=sqlite3.Row
        ids=('delivery_pending_export','delivery_emergency_stop','delivery_chain_finish')
        rows={i:dict(c.execute('SELECT * FROM requests WHERE id=?',(i,)).fetchone())for i in ids}
        owner=c.execute("SELECT value FROM meta WHERE key='owner'").fetchone()
    if owner and json.loads(owner[0]).get('running'):raise ValueError('Existing owner is still running')
    if rows['delivery_pending_export']['status']!='completed'or rows['delivery_emergency_stop']['status']!='completed':raise ValueError('The original export/stop must already have completed; do not retry them')
    if rows['delivery_chain_finish']['status']!='queued'or rows['delivery_chain_finish']['started_utc']is not None:raise ValueError('The original FINISH is not the untouched queued request')
    result['paired_pending_export']=json.loads(rows['delivery_pending_export']['result'])
    result['owner1_stop']=json.loads(rows['delivery_emergency_stop']['result'])
    result['instrumental_continuation']={'reason':'Export completed in49.78s after the40s client wait; no native error or material retry.',
        'first_copy_tick':105605,'first_attempt_sha256':sha(a.prueba_previa),'helper_revision_sha256':sha(a.helper_corregido),
        'not_a_new_import':True,'same_literal_FINISH_only_waited':True,'queued_before':rows['delivery_chain_finish']}
    proof={'schema':'DEE.independent_delivery.explicit_harness_continuation.v1','started_utc':datetime.now(timezone.utc).isoformat(),
        'first_attempt':str(a.prueba_previa),'first_attempt_sha256':sha(a.prueba_previa),'zip':previous['zip'],'zip_sha256':previous['zip_sha256'],
        'destination':previous['destination'],'commands':previous['commands'].copy(),'originals_before':previous['originals_before'],
        'instrument_scope':'A new external continuation runner; not represented as bytes that belonged to the first exact ZIP. Actor and all commands come only from that unchanged extraction.',
        'helper_sha256':sha(a.helper_corregido),'queue_rows_before':rows,'new_scientific_campaign':False}
    python=root/'motor/python313/python.exe';launcher=root/'actualizaciones/arrancar.py'
    def call(label,argv,require_fence=False):
        command=[str(python),'-I','-B','-X','utf8',str(launcher),*argv];t=time.perf_counter()
        p=subprocess.run(command,cwd=root,text=True,encoding='utf8',capture_output=True,timeout=240)
        proof['commands'].append({'label':label,'argv':command,'exit_code':p.returncode,'host_seconds':time.perf_counter()-t,'stdout':p.stdout,'stderr':p.stderr})
        if p.returncode:raise RuntimeError('Continuation command failed: '+label)
        return p.stdout
    try:
        spec=importlib.util.spec_from_file_location('explicit_delivery_harness_revision',a.helper_corregido)
        module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        proof['service_sequence']=module.run(root,life,'MENTE_UNIFICADA',read(a.protocolo),call,resume=result)
        proof['continued_state']=proof['service_sequence']['continued_state'];proof['status']='COMPLETED'
    except BaseException as e:
        proof['status']='FAILED_WITH_STATE_PRESERVED';proof['error']={'type':type(e).__name__,'detail':str(e)}
    finally:
        proof['originals_after']={p:sha(p)for p in proof['originals_before']}
        proof['originals_unchanged']=proof['originals_after']==proof['originals_before']
        proof['zip_unchanged']=sha(proof['zip'])==proof['zip_sha256']
        proof['finished_utc']=datetime.now(timezone.utc).isoformat();write(a.salida,proof)
    print(json.dumps({'status':proof['status'],'output':str(a.salida),'error':proof.get('error')}))
    return 0 if proof['status']=='COMPLETED'else 1


if __name__=='__main__':raise SystemExit(main())
