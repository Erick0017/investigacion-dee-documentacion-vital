"""Post-run read-only primary extraction, never another native continuation."""
import argparse,gzip,hashlib,importlib.util,json,shutil
from collections import Counter
from pathlib import Path


def write_gz(path,value):
    with gzip.GzipFile(filename=str(path),mode='wb',mtime=0)as f:f.write((json.dumps(value,sort_keys=True,ensure_ascii=False,indent=2)+'\n').encode('utf8'))
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--sistema',type=Path,required=True);p.add_argument('--ensayo',type=Path,required=True);p.add_argument('--configuracion',type=Path,required=True);p.add_argument('--historia-inicial',type=Path,required=True);p.add_argument('--piloto',type=Path,required=True);p.add_argument('--interrupcion',type=Path);a=p.parse_args();root=a.ensayo;system=a.sistema
    result=json.loads((root/'RESULTADO.json').read_bytes());protocol=json.loads((root/'PROTOCOLO.json').read_bytes());before=result['before'];interrupted=json.loads(a.interrupcion.read_bytes())if a.interrupcion else None;after=interrupted['main']if interrupted else result.get('final')
    if not after:raise ValueError('No completed final pointer: do not replace it with a later favorable state')
    config=json.loads(a.configuracion.read_bytes());encoded=json.dumps(config,sort_keys=True,ensure_ascii=False,separators=(',',':'),allow_nan=False).encode('utf8')
    if hashlib.sha256(encoded).hexdigest()!=protocol['configuration_sha256']:raise ValueError('Configuration differs from the executed prospective protocol')
    if(root/'CONFIG_READY.json').exists():raise FileExistsError('Existing archived configuration preserved')
    shutil.copyfile(a.configuracion,root/'CONFIG_READY.json')
    novelty=config.get('novel_pair_selection')
    if novelty:
        source=a.configuracion.parent/novelty['file']
        if hashlib.sha256(source.read_bytes()).hexdigest()!=novelty['sha256']:raise ValueError('Prospectively frozen new-pair selection differs')
        shutil.copyfile(source,root/novelty['file'])
    if config.get('prior_executed_teaching'):
        previous=config['prior_executed_teaching'];(root/'HISTORIA_PREVIA_DE_EJECUCION.json').write_text(json.dumps(previous,sort_keys=True,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    shutil.copyfile(a.historia_inicial,root/'BASELINE_P26.json.gz')
    shutil.copyfile(a.piloto/'PILOTO_APD.json.gz',root/'PILOTO_APD.json.gz');shutil.copytree(a.piloto/'codigo',root/'PILOTO_CODIGO')
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
    write_gz(root/'CAMPOS_Y_RECIBOS_COMPLETOS.json.gz',{'schema':'DEE.APD01.sixty_minute_complete_fields.v1','snapshots':snapshots,'baseline_receipt_ids':sorted(baseline_ids),'new_receipts':receipts,'receipt_selection':'Exact event-ID set difference between complete named saved snapshots; not inferred from absolute ticks or native status labels.','native_ticks':0,'no_Runtime_restored':True})
    transport_name='REGISTROS_TRANSPORTE_POSTSTOP.json.gz'if interrupted else'REGISTROS_TRANSPORTE.json.gz';transport_path=root/transport_name
    transport=json.loads(gzip.decompress(transport_path.read_bytes()));inherited_ids={r['id']for r in protocol.get('inherited_pending_rows',[])};selected=[r for r in transport if r['id'].startswith(protocol['request_prefix'])or r['id']in inherited_ids];files={}
    write_gz(root/'REGISTROS_APD.json.gz',selected)
    (root/'PROYECCION_TRANSPORTE.json').write_text(json.dumps({'schema':'DEE.APD01.transport_projection.v1','original_file':transport_name,'original_sha256':hashlib.sha256(transport_path.read_bytes()).hexdigest(),'original_bytes':transport_path.stat().st_size,'original_rows':len(transport),'selection':'Every complete row with the prospectively frozen request_prefix OR one of the explicitly frozen inherited pending IDs; no status/result filtering','request_prefix':protocol['request_prefix'],'inherited_pending_ids':sorted(inherited_ids),'selected_rows':len(selected),'selected_file':'REGISTROS_APD.json.gz','selected_sha256':hashlib.sha256((root/'REGISTROS_APD.json.gz').read_bytes()).hexdigest(),'omitted_rows':len(transport)-len(selected),'omitted_scope':'Other inherited transport rows from earlier campaigns/epochs, not executed episodes in this reserve. Full original remains local. JSON field/value preservation is asserted, not gzip-container identity.'},sort_keys=True,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    artifact_root=(Path(interrupted['paired_export']['manifest']).parent if interrupted else Path(result['final_paired_export']['paired_export']['directory']))/'artefactos_trabajador'
    def include(name,size,digest,kind):
        if Path(name).name!=name:raise ValueError('Only declared bounded artifact names, not a path supplied by an evaluator')
        key=digest+'_'+name
        matches=[f for f in artifact_root.rglob(name)if f.is_file()and f.stat().st_size==size and hashlib.sha256(f.read_bytes()).hexdigest()==digest]
        if not matches:raise ValueError('Actual declared artifact missing from the exact paired export; do not regenerate it: '+name)
        source=matches[0];data=source.read_bytes()
        if key not in files:
            dest=root/'artefactos'/digest/name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,dest);files[key]={'file':dest.relative_to(root).as_posix(),'source':str(source),'matching_sources_in_exact_export':[str(f)for f in matches],'bytes':len(data),'sha256':digest,'output_name':name,'kinds':[kind]}
        elif kind not in files[key]['kinds']:files[key]['kinds'].append(kind)
    def walk(q):
        if isinstance(q,dict):
            if all(k in q for k in('output_name','output_bytes','output_sha256')):include(q['output_name'],q['output_bytes'],q['output_sha256'],'actual_EO02_worker_receipt')
            artifact=q.get('artifact')
            if q.get('kind')in('APD01_integrated_request','APD01_assisted_composition')and isinstance(artifact,dict):include(artifact['name'],artifact['bytes'],artifact['sha256'],q['kind'])
            for v in q.values():walk(v)
        elif isinstance(q,list):
            for v in q:walk(v)
    for row in transport:
        if(row['id'].startswith(protocol['request_prefix'])or row['id']in inherited_ids)and row['result']:walk(json.loads(row['result']))
    pilot=json.loads(gzip.decompress((a.piloto/'PILOTO_APD.json.gz').read_bytes()))
    for node in pilot['records'].values():
        if isinstance(node,dict)and isinstance(node.get('result'),str):walk(json.loads(node['result']))
    (root/'ARTEFACTOS_REALES.json').write_text(json.dumps({'schema':'DEE.APD01.sixty_minute_actual_artifacts.v1','files':list(files.values()),'scope':'Actual declared APD/DSL and EO02 worker bytes copied from the exact final paired export and verified against archived declarations. No calculator, compiler, native world or worker is rerun.'},sort_keys=True,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps({'complete_uint64':sum(2*s.N**3 for s in objects.values()),'new_native_receipts':len(receipts),'actual_worker_files':len(files),'native_ticks':0}))


if __name__=='__main__':main()
