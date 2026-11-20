"""Deduplicate repeated parent operation-results; restore exact original bytes.

Only exported metadata is deduplicated. Original evidence, lives, fields,
agendas and protocol source stay unchanged. The two referenced R02 primaries
are already in the same scientific package. No native imports or ticks.
"""
import argparse,gzip,hashlib,json
from pathlib import Path
def read(p):
    b=p.read_bytes();return json.loads(gzip.decompress(b)if p.suffix=='.gz'else b)
def sha(b):return hashlib.sha256(b).hexdigest()
def encode(z):return(json.dumps(z,ensure_ascii=False,sort_keys=True,indent=2)+'\n').encode('utf8')
def compact(original,r02,prefix):
    data=read(original);parents=[];refs=[]
    for pi,parent in enumerate(data['parents']):
        p=dict(parent);ops=[]
        case='reversed'if parent['life_id'].endswith('_reversed')else'paired'
        source=r02/(case+'_01_PRIMARY.json.gz');primary=read(source)
        for oi,operation in enumerate(parent['operations']):
            op=dict(operation)
            if'result'in op:
                if op['result']!=primary['result']:raise ValueError('Parent operation is not the already included R02 primary')
                refs.append({'parent_index':pi,'operation_index':oi,'reference':prefix+'/'+source.name,
                             'reference_sha256':sha(source.read_bytes()),'JSON_pointer':'$.result'})
                op['result']=None
            ops.append(op)
        p['operations']=ops;parents.append(p)
    result={**data,'parents':parents,'_deduplication':{'schema':'APD01.lossless_parent_result_dedup.R1','original_name':original.name,
        'original_local':str(original),'original_bytes':original.stat().st_size,'original_sha256':sha(original.read_bytes()),
        'serialization':'UTF8 json.dumps ensure_ascii=False,sort_keys=True,indent=2 plus one LF','references':refs,
        'scope':'Repeated scientific parent operation-results only; no physical state is omitted from the primary files.'}}
    return result
def restore(data,base):
    meta=data['_deduplication'];out={k:v for k,v in data.items()if k!='_deduplication'};parents=[]
    # Copy only the small edited dictionaries. Existing field values stay exact.
    for parent in out['parents']:
        p=dict(parent);p['operations']=[dict(op)for op in parent['operations']];parents.append(p)
    out['parents']=parents
    for ref in meta['references']:
        path=(base/ref['reference']).resolve(strict=True)
        if sha(path.read_bytes())!=ref['reference_sha256']:raise ValueError('Referenced primary changed')
        out['parents'][ref['parent_index']]['operations'][ref['operation_index']]['result']=read(path)['result']
    encoded=encode(out)
    if sha(encoded)!=meta['original_sha256']or len(encoded)!=meta['original_bytes']:
        raise ValueError('Exact original byte reconstruction failed')
    return encoded
def main():
    p=argparse.ArgumentParser();p.add_argument('--original',type=Path);p.add_argument('--r02',type=Path)
    p.add_argument('--prefijo-r02',default='LENGUAJE/EVIDENCIA/R02');p.add_argument('--compacto',type=Path,required=True)
    p.add_argument('--base',type=Path);p.add_argument('--restaurar',type=Path)
    a=p.parse_args()
    if a.original:
        if a.r02 is None:p.error('--r02 required for compaction')
        data=compact(a.original,a.r02,a.prefijo_r02)
        # Check reconstruction using an explicit map into the actual originals.
        expected=read(a.original)
        for ref in data['_deduplication']['references']:
            recovered=read(a.r02/Path(ref['reference']).name)['result']
            if recovered!=expected['parents'][ref['parent_index']]['operations'][ref['operation_index']]['result']:
                raise ValueError('Reconstructed parent differs')
        if encode(expected)!=a.original.read_bytes():raise ValueError('Source uses another serializer; do not claim byte preservation')
        with a.compacto.open('xb')as f:f.write(encode(data))
        print(json.dumps({'compact_bytes':a.compacto.stat().st_size,'compact_sha256':sha(a.compacto.read_bytes()),
                          'original_bytes':a.original.stat().st_size,'original_sha256':sha(a.original.read_bytes()),
                          'references':len(data['_deduplication']['references']),'native_ticks':0}))
    else:
        if a.base is None or a.restaurar is None:p.error('--base and --restaurar required for exact reconstruction')
        encoded=restore(read(a.compacto),a.base)
        with a.restaurar.open('xb')as f:f.write(encoded)
        print(json.dumps({'restored_bytes':len(encoded),'restored_sha256':sha(encoded),'native_ticks':0}))
if __name__=='__main__':main()
