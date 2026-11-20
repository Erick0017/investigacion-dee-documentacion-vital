"""Portable verification of complete equal-age MAIN/U prepared-chain fields."""
import argparse,base64,gzip,hashlib,json,struct
def sha(b):return hashlib.sha256(b).hexdigest()
def array_hash(vs):
    h=hashlib.sha256()
    for v in vs:
        n=int(v)
        if not 0<=n<2**64:raise ValueError('Not uint64')
        h.update(struct.pack('<Q',n))
    return h.hexdigest()
def main():
    from pathlib import Path
    ap=argparse.ArgumentParser();ap.add_argument('--evidencia',type=Path,required=True);ap.add_argument('--salida',type=Path,required=True);a=ap.parse_args()
    b=a.evidencia.read_bytes();o=json.loads(gzip.decompress(b));u=o['worlds']['U'];m=o['worlds']['MAIN'];errors=[];worlds=[]
    for name,w in[('U',u),('MAIN',m)]:
        raw,clock=list(u['raw']),list(u['clock'])
        if name=='MAIN':
            for key,field,base,target in[('raw_delta','raw','base_raw',raw),('clock_delta','clock','base_clock',clock)]:
                for d in w[key]:
                    if target[d['index']]!=d[base]:errors.append('Delta base mismatch')
                    target[d['index']]=d[field]
        okay=(array_hash(raw)==w['raw_sha256']and array_hash(clock)==w['clock_sha256']and len(raw)==len(clock)==67**3 and w['tick_before']==w['tick_after']==31765)
        if not okay:errors.append(name+' reconstruction mismatch')
        worlds.append({'world':name,'snapshot_sha256':w['snapshot_sha256'],'all_uint64_fields':len(raw)+len(clock),'all_hashes_and_ticks_exact':okay})
    c=o['comparison'];p_u,p_m=c['external_pending_U'],c['external_pending_MAIN'];same=p_u==p_m
    if same!=c['external_pending_exact_equal']:errors.append('Pending equality mismatch')
    artifact=base64.b64decode(p_m['prepared_output_base64']);payload=base64.b64decode(p_m['payload_base64'])
    artifact_valid=sha(artifact)==p_m['prepared_output_sha256']and sha(payload)==p_m['payload_sha256']
    if not artifact_valid:errors.append('Prepared external bytes mismatch')
    result={'schema':'MUFI01.chain_prepared.recalculation.v1','native_ticks_executed':0,'primary_name':a.evidencia.name,'primary_sha256':sha(b),'worlds':worlds,
      'raw_delta_exact':m['raw_delta'],'clock_delta_exact':m['clock_delta'],'interfaces_equal':u['interfaces']==m['interfaces'],'protocols_equal':u['protocols']==m['protocols'],
      'unfinished_equal':u['unfinished_receipts']==m['unfinished_receipts'],'pending_exact_equal':same,'prepared_by':p_m['prepared_by'],'actual_pending_bytes':len(artifact),
      'pending_artifact_valid':artifact_valid,'errors':errors,'scope':'All physical fields plus exposed context compared; legitimate documentary histories may differ. No total causal-state identity or unique inverse past asserted.'}
    a.salida.parent.mkdir(parents=True,exist_ok=True);a.salida.write_text(json.dumps(result,ensure_ascii=False,sort_keys=True,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'uint64':sum(x['all_uint64_fields']for x in worlds),'raw_differences':len(m['raw_delta']),'clock_differences':len(m['clock_delta']),'pending_equal':same,'errors':errors,'sha256':sha(a.salida.read_bytes())}))
    if errors:raise SystemExit(1)
if __name__=='__main__':main()
