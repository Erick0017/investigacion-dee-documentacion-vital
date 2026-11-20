"""Read-only exact snapshot/archive comparison for the technical migration."""
import argparse,gzip,hashlib,importlib.util,json
from pathlib import Path


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--sistema',type=Path,required=True);p.add_argument('--salida',type=Path,required=True);a=p.parse_args();system=a.sistema.resolve()
    current=json.loads((system/'estado/vidas/MU_MAIN/VIDA.json').read_bytes());entry=current['archived_operation_ledgers'][-1]
    encoded=(system/entry['file']).read_bytes();decoded=gzip.decompress(encoded);old=json.loads(decoded)
    spec=importlib.util.spec_from_file_location('external_snapshot_observer',system/'capacidades/observador_causal_retrospectivo_01.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    before=module.Snapshot(system/old['snapshot']);after=module.Snapshot(system/current['snapshot']);excluded=('DEE.Cognitive.System.1.1.life.v1',)
    left=hashlib.sha256(before.normalized_bytes(exclude=excluded)).hexdigest();right=hashlib.sha256(after.normalized_bytes(exclude=excluded)).hexdigest()
    checks={'lossless_original_record_bytes':len(decoded)==entry['decoded_bytes']and hashlib.sha256(decoded).hexdigest()==entry['decoded_sha256'],
        'compressed_archive_identity':len(encoded)==entry['encoded_bytes']and hashlib.sha256(encoded).hexdigest()==entry['encoded_sha256'],
        'full_saved_state_identical_except_declared_system_identity_metadata':left==right,
        'full_native_tick_preserved':before.tick==after.tick,'snapshot_checksums':before.checksum_valid and after.checksum_valid,
        'operation_count_offset_preserved':current['operation_count_offset']==old.get('operation_count_offset',0)+len(old['operations'])}
    result={'schema':'DEE.unified.lossless_compaction.read_only_verification.v1','checks':checks,'issues':[k for k,v in checks.items()if not v],
        'archive':entry,'tick':after.tick,'native_ticks':0,'no_Runtime_restored':True,'normalized_before_sha256':left,'normalized_after_sha256':right,
        'exclusion_exactly':list(excluded),'before_snapshot_sha256':before.encoded_sha256,'after_snapshot_sha256':after.encoded_sha256,
        'fields_covered':'All native RAW/clocks, dimensions, tick, channels, pending events, receipts, backend/threads and all nonidentity metadata including OrganizationalWorld owner/interfaces/queues/progress and service protocol. Only the documented System life metadata packet and format checksum are normalized.',
        'original_bytes':entry['decoded_bytes'],'compressed_archive_bytes':entry['encoded_bytes'],'current_record_bytes':(system/'estado/vidas/MU_MAIN/VIDA.json').stat().st_size,
        'scope':'External archival instrument verification, not learning or physical improvement. Archive and full snapshots remain local; this result is not reconstruction of omitted states from their hashes.'}
    a.salida.parent.mkdir(parents=True,exist_ok=True);a.salida.write_text(json.dumps(result,sort_keys=True,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps({'checks':checks,'issues':result['issues'],'tick':after.tick,'native_ticks':0}));return bool(result['issues'])


if __name__=='__main__':raise SystemExit(main())
