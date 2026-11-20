"""Lossless technical ledger compaction, no native ticks or learned-state edit."""
import gzip,hashlib,json,os
from pathlib import Path


def file_sha(path):
    h=hashlib.sha256()
    with path.open('rb')as f:
        for block in iter(lambda:f.read(1048576),b''):h.update(block)
    return h.hexdigest()


def compact(store,life):
    from app.native_tools import physical,SYSTEM_KEY
    if life in('E1_SOCIAL_11','MA02_MAIN_5','MA_MAIN_R9','MA_U0_ACUMULATIVO_AUX','EO02_MAIN'):
        raise ValueError('Protected original; no ledger migration is applied to this identity.')
    rec=store.record(life)
    with store.writer(rec['world_id']):
        rec,a=store.load(life);before=physical(a.world);entries_before=dict(a.world.runtime.snapshot_metadata_entries)
        service_key='DEE.Cognitive.System.1.1.PERSISTENT_SERVICE.v1'
        if service_key in entries_before:
            from dee_thinking.persistence import decode_metadata
            if not decode_metadata(entries_before[service_key]).get('closed_epoch'):raise ValueError('Explicitly close the service epoch before this technical migration.')
        source=store.life_dir(life)/'VIDA.json';original_size=source.stat().st_size
        if original_size<8388608:raise ValueError('Ficha already compact; no repeated migration or gratuitous archival.')
        original_sha=file_sha(source);journal=store.life_dir(life)/'HISTORIA.jsonl';journal_prefix=journal.read_bytes()
        directory=store.state/'historiales_archivados'/life;directory.mkdir(parents=True,exist_ok=True)
        target=directory/(original_sha+'.VIDA.original.json.gz')
        if target.exists():raise FileExistsError('Previous archive with identical name is protected; inspect an interrupted migration instead of overwriting.')
        with source.open('rb')as src,target.open('xb')as raw:
            with gzip.GzipFile(filename='',fileobj=raw,mode='wb',mtime=0,compresslevel=6)as out:
                for block in iter(lambda:src.read(1048576),b''):out.write(block)
            raw.flush();os.fsync(raw.fileno())
        h=hashlib.sha256();decoded=0
        with gzip.open(target,'rb')as archive:
            for block in iter(lambda:archive.read(1048576),b''):h.update(block);decoded+=len(block)
        if h.hexdigest()!=original_sha or decoded!=original_size:raise AssertionError('Archive regeneration is not byte-identical; original ficha remains untouched.')
        count=len(rec.get('operations',[]));old_offset=rec.get('operation_count_offset',0)
        if type(old_offset)is not int or old_offset<0:raise ValueError('Invalid documented operation-count offset')
        archived={'file':target.relative_to(store.root).as_posix(),'encoded_sha256':file_sha(target),'encoded_bytes':target.stat().st_size,
            'decoded_sha256':original_sha,'decoded_bytes':original_size,'operations_in_this_archive':count,
            'operation_count_offset_before':old_offset,'operation_count_through_archive':old_offset+count,
            'scope':'Lossless original record/operations archive for retrospective study. Not an actor input and not required to restore complete native snapshots; no learned content is stored in this index.'}
        compacted={**rec,'operations':[],'operation_count_offset':old_offset+count,
            'archived_operation_ledgers':list(rec.get('archived_operation_ledgers',[]))+[archived]}
        operation={'kind':'LOSSLESS_OPERATION_LEDGER_COMPACTION','archive':archived,'native_ticks_advanced':0,
            'native_full_state_preserved':True,'old_journal_prefix_sha256':hashlib.sha256(journal_prefix).hexdigest(),
            'scope':'Technical serialization-cost correction. Old record preserved as exact gzip; append-only HISTORIA is retained. Neither learning nor memory transfer.'}
        saved=store.commit(compacted,a,operation)
        after=physical(a.world);entries_after=dict(a.world.runtime.snapshot_metadata_entries)
        unchanged=all(entries_after.get(k)==v for k,v in entries_before.items()if k!=SYSTEM_KEY)
        expected_keys=set(entries_before)|{SYSTEM_KEY}
        if set(entries_after)!=expected_keys or not unchanged or before!=after:raise AssertionError('Compaction altered native fields or nonidentity operational metadata; preserve reached state for diagnosis.')
        current=journal.read_bytes()
        if current[:len(journal_prefix)]!=journal_prefix:raise AssertionError('Append-only journal prefix was altered')
        return {'life_id':life,'native_ticks_advanced':0,'before':before,'after':after,'nonidentity_snapshot_metadata_unchanged':unchanged,
            'complete_queue_interfaces_progress_preserved_by_official_snapshot':True,'archive':archived,
            'old_record_bytes':original_size,'new_record_bytes':source.stat().st_size,'old_operation_count':old_offset+count,
            'new_operation_count_offset':saved['operation_count_offset'],'new_operation_count_total':saved['operation_count_offset']+len(saved['operations']),
            'snapshot':saved['snapshot'],'snapshot_sha256':saved['snapshot_sha256'],
            'old_journal_prefix_unchanged':True,'old_journal_prefix_sha256':hashlib.sha256(journal_prefix).hexdigest(),
            'queue_and_outbox_not_modified':True,'not_a_cognitive_improvement':True}
