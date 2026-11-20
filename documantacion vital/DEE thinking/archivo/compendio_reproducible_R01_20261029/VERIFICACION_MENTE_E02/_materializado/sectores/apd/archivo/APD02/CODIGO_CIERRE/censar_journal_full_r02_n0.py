"""Readonly census of this stopped personal R02 journal, never the source life."""
import argparse,collections,hashlib,json,sqlite3
from datetime import datetime,timezone
from pathlib import Path
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--journal',type=Path,required=True);p.add_argument('--prueba',type=Path,required=True);p.add_argument('--salida',type=Path,required=True);a=p.parse_args();journal=a.journal.resolve(strict=True);proof=json.loads(a.prueba.read_bytes());life=proof['exact_import']['life_id'];prefix=proof['protocol']['prefix']
    if life!='APD02_DIST_R02'or journal.parent.name!=life or journal.name!='cola.sqlite3'or'trabajo_personal'not in journal.parts:raise ValueError('Only the own stopped R02 personal copy is in scope')
    if len(proof['owned_close'])!=2 or any(v['resources']['job_active_processes']!=0 for v in proof['owned_close'])or proof.get('forced_owned_job_cleanup'):raise ValueError('Proof did not establish both own owners closed')
    sidecars={suffix:{'exists':Path(str(journal)+suffix).exists(),'bytes':Path(str(journal)+suffix).stat().st_size if Path(str(journal)+suffix).exists()else 0}for suffix in('-wal','-shm')}
    if sidecars['-wal']['bytes']:raise ValueError('A nonempty WAL requires a different declared read protocol; do not mutate it')
    before=sha(journal);c=sqlite3.connect(journal.as_uri()+'?mode=ro&immutable=1',uri=True);c.row_factory=sqlite3.Row
    try:
        integrity=c.execute('pragma integrity_check').fetchone()[0]
        rows=[dict(r)for r in c.execute('SELECT seq,id,is_control,status,arrived_ns,arrived_utc,started_utc,finished_utc,payload,payload_sha,error FROM requests WHERE substr(id,1,?)=? ORDER BY seq',(len(prefix),prefix))]
        outstanding=[dict(r)for r in c.execute("SELECT id,status FROM requests WHERE status IN ('queued','processing','uncertain') ORDER BY seq")]
    finally:c.close()
    after=sha(journal);issues=[]
    for row in rows:
        if sha_bytes(row['payload'].encode())!=row['payload_sha']:issues.append('payload_sha:'+row['id'])
    if integrity!='ok'or before!=after:issues.append('journal_changed_or_integrity_failure')
    if len(rows)!=len({r['id']for r in rows}):issues.append('duplicate_ID')
    result={'schema':'APD02.Full.R02.closed_journal_census.N0','recorded_utc':datetime.now(timezone.utc).isoformat(),'life_id':life,'world_id':proof['exact_import']['world_id'],'journal_localizer':str(journal),'journal_bytes':journal.stat().st_size,'journal_sha256_before':before,'journal_sha256_after':after,'journal_unchanged':before==after,'sidecars_before':sidecars,'integrity_check':integrity,'proof_localizer':str(a.prueba),'proof_sha256':sha(a.prueba),'prefix':prefix,'rows':rows,'unique_ids':len({r['id']for r in rows}),'sequence_min':min(r['seq']for r in rows),'sequence_max':max(r['seq']for r in rows),'material_ids':sum(r['is_control']==0 for r in rows),'control_ids':sum(r['is_control']==1 for r in rows),'status_counts':dict(collections.Counter(r['status']for r in rows)),'all_journal_outstanding':outstanding,'issues':issues,'new_native_ticks':0,'new_provider_calls':0,'requeued_actions':0,'scope':'Only one stopped personal-copy SQLite file is read, via mode=ro&immutable=1 with no nonempty WAL. No Runtime, source original, actor input, resume, requeue, table editing or new simulation. This is separate from the CLOSED Full stage and does not change its manifest or recount Native inputs. R01 is a distinct world, not included in this census.'}
    with a.salida.open('x',encoding='utf8')as f:json.dump(result,f,sort_keys=True,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps({'output':str(a.salida),'sha256':sha(a.salida),'unique_ids':result['unique_ids'],'material':result['material_ids'],'controls':result['control_ids'],'status_counts':result['status_counts'],'issues':issues,'new_native_ticks':0}));return bool(issues)
def sha_bytes(value):return hashlib.sha256(value).hexdigest()
if __name__=='__main__':raise SystemExit(main())
