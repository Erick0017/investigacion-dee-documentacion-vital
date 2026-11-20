"""Exact last recorded global frames from two dense adverse03 streams.

Read-only extraction, not a new trajectory or a claim about an unrecorded final
future. Retains original decompressed line bytes, offset and source gzip hash.
"""
from pathlib import Path
import argparse,gzip,lzma,json,hashlib,sys
p=argparse.ArgumentParser();p.add_argument('--evidence',type=Path,required=True);p.add_argument('--stage',type=Path,required=True);a=p.parse_args();sys.path.insert(0,str(Path(__file__).parent))
from recalcular_acceso import walk,frame_check
out=a.stage/'EVIDENCIA_ESENCIAL/CONTEXTOS_ADVERSOS_03';out.mkdir(parents=True,exist_ok=False);records=[]
for source in sorted(a.evidence.glob('SELECCION_E1_03/*/*.jsonl.gz')):
    if source.stat().st_size<1_000_000:continue
    offset=0;last=None
    with gzip.open(source,'rb')as f:
        for number,line in enumerate(f,1):
            if line.strip():last=(number,offset,line)
            offset+=len(line)
    number,start,b=last;data=json.loads(b);target=out/(source.parent.name+'.ultima_linea_original.json.xz');target.write_bytes(lzma.compress(b,preset=6));assert lzma.decompress(target.read_bytes())==b;checks=[]
    for loc,q in walk(data):
        if{'rows','clock_default','clock_exceptions','N','RAW_sha256','clocks_sha256'}<=q.keys()and q['clock_exceptions']is not None:
            result=frame_check(q);checks.append({'locator':loc,'result':result});assert all(result['matches'].values())and result['row_clock_match']
    records.append({'source':str(source),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'source_compressed_bytes':source.stat().st_size,'decompressed_stream_bytes':offset,'selected_line_number':number,'selected_decompressed_byte_offset':start,'selected_exact_bytes':len(b),'selected_exact_sha256':hashlib.sha256(b).hexdigest(),'included_member':target.relative_to(a.stage).as_posix(),'included_sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'included_bytes':target.stat().st_size,'selected_tick':data.get('tick'),'verified_sparse_fields':checks,'scope':'LAST_RECORDED_LINE_NOT_ASSUMED_LAST_EVOLVED_STATE; no simulation or compressed-wrapper identity claim'})
value={'schema':'AA01.exact_adverse_context_extract.v1','no_native_evolution':True,'records':records};(out/'PROCEDENCIA.json').write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps([{'file':q['included_member'],'bytes':q['included_bytes'],'checks':len(q['verified_sparse_fields'])}for q in records]))
