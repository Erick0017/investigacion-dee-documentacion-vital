"""Post-run read-only primary extraction, never another native continuation."""
import argparse,gzip,hashlib,importlib.util,json,shutil
from collections import Counter
from pathlib import Path


def write_gz(path,value):
    with gzip.GzipFile(filename=str(path),mode='wb',mtime=0)as f:f.write((json.dumps(value,sort_keys=True,ensure_ascii=False,indent=2)+'\n').encode('utf8'))
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--sistema',type=Path,required=True);p.add_argument('--ensayo',type=Path,required=True);a=p.parse_args();root=a.ensayo;system=a.sistema
    result=json.loads((root/'RESULTADO.json').read_bytes());before=result['before'];after=result.get('final')
    if not after:raise ValueError('No completed final pointer: do not replace it with a later favorable state')
    spec=importlib.util.spec_from_file_location('external_observer',system/'capacidades/observador_causal_retrospectivo_01.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    snapshots={};objects={}
    for label,rec in(('before',before),('after',after)):
        s=m.Snapshot(system/rec['snapshot']);objects[label]=s
        if s.encoded_sha256!=rec['snapshot_sha256']:raise ValueError('Named exact source snapshot hash mismatch')
        default=Counter(s.clocks).most_common(1)[0][0]
        snapshots[label]={'source_snapshot':str(system/rec['snapshot']),'snapshot_sha256':s.encoded_sha256,'N':s.N,'tick':s.tick,
            'RAW_sha256':m.sha(m.pbytes(s.raw)),'clocks_sha256':m.sha(m.pbytes(s.clocks)),
            'raw_nonzero':[[i,str(v)]for i,v in enumerate(s.raw)if v],
            'clock_default':str(default),'clock_exceptions':[[i,str(v)]for i,v in enumerate(s.clocks)if v!=default],
            'checksum_valid':s.checksum_valid,'next_event_id':s.next_event_id,'pending':s.pending,'channels':s.channels,
            'coverage':'Complete RAW/clocks and declared event/channel state; not all snapshot metadata/protocol and not an operational backup.'}
    baseline_ids={r['id']for r in objects['before'].receipts}
    receipts=[r for r in objects['after'].receipts if r['id']not in baseline_ids]
    write_gz(root/'CAMPOS_Y_RECIBOS_COMPLETOS.json.gz',{'schema':'DEE.unified.sixty_minute_complete_fields.v1','snapshots':snapshots,'baseline_receipt_ids':sorted(baseline_ids),'new_receipts':receipts,'receipt_selection':'Exact event-ID set difference between complete named saved snapshots; not inferred from absolute ticks or native status labels.','native_ticks':0,'no_Runtime_restored':True})
    transport=json.loads(gzip.decompress((root/'REGISTROS_TRANSPORTE.json.gz').read_bytes()));files={}
    artifact_root=Path(result['final_paired_export']['paired_export']['directory'])/'artefactos_trabajador'
    def walk(q):
        if isinstance(q,dict):
            if all(k in q for k in('output_name','output_bytes','output_sha256')):
                key=q['output_sha256']+'_'+q['output_name'];matches=[f for f in artifact_root.rglob(q['output_name'])if f.is_file()and f.stat().st_size==q['output_bytes']and hashlib.sha256(f.read_bytes()).hexdigest()==q['output_sha256']]
                if not matches:raise ValueError('Actual named worker artifact missing from the exact paired export; do not regenerate it')
                source=matches[0];data=source.read_bytes()
                if len(data)!=q['output_bytes']or hashlib.sha256(data).hexdigest()!=q['output_sha256']:raise ValueError('Actual worker artifact differs; no regeneration or replacement')
                if key not in files:
                    dest=root/'artefactos'/key;dest.parent.mkdir(exist_ok=True);shutil.copyfile(source,dest);files[key]={'file':dest.relative_to(root).as_posix(),'source':str(source),'matching_sources_in_exact_export':[str(f)for f in matches],'bytes':len(data),'sha256':q['output_sha256'],'output_name':q['output_name']}
            for v in q.values():walk(v)
        elif isinstance(q,list):
            for v in q:walk(v)
    for row in transport:
        if row['id'].startswith('fi60_')and row['result']:walk(json.loads(row['result']))
    (root/'ARTEFACTOS_REALES.json').write_text(json.dumps({'schema':'DEE.unified.sixty_minute_actual_artifacts.v1','files':list(files.values()),'scope':'Bytes copied after actual worker execution and verified against exact receipts; no worker is rerun.'},sort_keys=True,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps({'complete_uint64':sum(2*s.N**3 for s in objects.values()),'new_native_receipts':len(receipts),'actual_worker_files':len(files),'native_ticks':0}))


if __name__=='__main__':main()
