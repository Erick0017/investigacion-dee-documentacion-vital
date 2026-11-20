"""Explicit, zero-tick close of a stopped persistent transport epoch."""
import hashlib,json,uuid


def finalize(store,life):
    try:
        from .cola_local import QueueDB
        from .servicio_persistente import NativeWorld,KEY
    except ImportError:
        from cola_local import QueueDB
        from servicio_persistente import NativeWorld,KEY
    from app.native_tools import physical,atomic_json
    from dee_thinking.persistence import encode_metadata,decode_metadata
    folder=store.state/'servicios_persistentes'/store.record(life)['world_id'];path=folder/'cola.sqlite3'
    if not path.is_file():raise ValueError('No paired service journal; never substitute an empty protocol.')
    queue=QueueDB(path)
    def close(a):
        owner=queue.get_meta('owner')
        if not owner or owner.get('running')is not False:raise ValueError('Stop the existing owner gracefully before finalizing its transport protocol.')
        entries=dict(a.world.runtime.snapshot_metadata_entries)
        if KEY not in entries:raise ValueError('No native persistent service epoch to finalize.')
        protocol=decode_metadata(entries[KEY])
        if protocol.get('closed_epoch'):raise ValueError('This epoch is already explicitly closed; do not duplicate closure.')
        if protocol.get('uncertain_external_result'):raise ValueError('Uncertain external outcome prevents protocol closure; preserve and diagnose it.')
        if protocol.get('native_tick_at_checkpoint',a.tick)!=a.tick:raise ValueError('Protocol already out of sync; closure cannot disguise an earlier unrecorded continuation.')
        queue.close_admission_if_idle()
        before=physical(a.world);rec=store.record(life)
        proxy=NativeWorld(store.root,life,protocol.get('backend','ma02'));proxy.store=store;proxy.rec=rec;proxy.folder=folder
        proxy.work_directory=store.state/'servicios_locales'/life;proxy.atomic_json=atomic_json
        exported=proxy.export_pair('closed_epoch_'+uuid.uuid4().hex[:12],queue)
        after_protocol={**protocol,'closed_epoch':True,'paused':True,'native_tick_at_checkpoint':int(a.tick),
            'explicit_external_continuation_allowed_after_close':True,'closure_export_manifest_sha256':exported['manifest_sha256'],
            'closure_source_snapshot_sha256':rec['snapshot_sha256'],
            'closure_scope':'Technical epoch closed after stopped owner and empty/unambiguous transport. No native ticks, RAW edits, memory reset or rollback. Future ordinary declared Store mutations may continue this same life; next explicit service start opens a new epoch preserving prior transport IDs.'}
        a.world.runtime.set_snapshot_metadata(KEY,encode_metadata(after_protocol))
        if physical(a.world)!=before:raise AssertionError('Metadata-only epoch closure altered native RAW/clocks/tick')
        return {'life_id':life,'epoch':int(protocol.get('epoch',1)),'physical_before':before,'physical_after':physical(a.world),
            'native_ticks_advanced':0,'closed_epoch':True,'paired_preclosure_export':exported,
            'retained_transport_ids':True,'queue_admission_closed_until_explicit_service_start':True,
            'no_external_uncertainty_or_pending_queue_discarded':True}
    result=store.mutate(life,'EXPLICIT_PERSISTENT_TRANSPORT_EPOCH_CLOSE',close,{'prepared_technical_transition_not_cognitive_adaptation':True})
    queue.meta('epoch_closed',{'life_id':life,'result':result,'next_start_opens_new_epoch':True})
    return result
