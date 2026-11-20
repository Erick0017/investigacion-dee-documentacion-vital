"""Read-only directed comparison of archived U0 origin and thinking4.5 port.

Parses only the documented v2 snapshot header+RAW/clocks; no Native imports.
The original snapshot hash is verified against the primary record. No missing
tick is reconstructed. Source observations stay separate from the4.5 records.
"""
from pathlib import Path
import gzip,hashlib,json,struct

OUT=Path(__file__).resolve().parent
THINK=OUT.parents[2]
ORIGIN=THINK/'casos practicos/trabajo_codex/CPC7/resultados/integrated_revision/IR_P01_GUARDED_M1'
PORT=THINK/'4.5/DEE_thinking_4_5_0/validation/cpc_ports_4_5_final6/IR_P01_GUARDED_M1'
def sha(b):return hashlib.sha256(b).hexdigest()
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def meta(p):b=p.read_bytes();return {'path':str(p),'bytes':len(b),'sha256':sha(b)}
def points(x):
    if isinstance(x,dict):
        if all(k in x for k in ('site','raw','clock')):return [x]
        return [p for v in x.values()for p in points(v)]
    if isinstance(x,list):return [p for v in x for p in points(v)]
    return []
def snapshot_buffers(path,expected):
    b=path.read_bytes();assert sha(b)==expected
    b=gzip.decompress(b)if b[:2]==b'\x1f\x8b'else b
    i=0
    def take(n):
        nonlocal i
        q=b[i:i+n];assert len(q)==n;i+=n;return q
    def unpack(fmt):return struct.unpack(fmt,take(struct.calcsize(fmt)))[0]
    assert take(8)==b'DEETSNP1'and unpack('<I')==2
    n=unpack('<I');tick=unpack('<Q');take(1+8+8)
    take(unpack('<I'));total=unpack('<Q');assert total==n**3
    raw=take(total*8);clock=take(total*8)
    return n,tick,raw,clock
def main():
    op=ORIGIN/'BASE338_MEASUREMENTS.json';pp=PORT/'RESULT.json';cp=PORT/'CONFIG.json'
    o=load(op);p=load(pp);cfg=load(cp)
    comparisons=[]
    for tick in [0,70,75,142,338]:
        s=next(s for s in o['snapshots']if s['physical']['tick']==tick)
        path=ORIGIN/s['path'];n,t,a,b=snapshot_buffers(path,s['sha256'])
        f=next(f for f in p['frames']if int(f['tick'])==tick)
        raw=gzip.decompress((PORT/f['raw']['path']).read_bytes())
        clock=gzip.decompress((PORT/f['clock']['path']).read_bytes())
        comparisons.append({'tick':tick,'N':n,'snapshot':meta(path),
            'original_metadata_hashes_match_parsed_bytes':sha(a)==s['physical']['raw_sha256']and sha(b)==s['physical']['clock_sha256'],
            'RAW_bytes_equal':a==raw,'clock_bytes_equal':b==clock,
            'original_RAW_sha256':sha(a),'port_RAW_sha256':sha(raw),
            'original_clock_sha256':sha(b),'port_clock_sha256':sha(clock)})
    rows=[]
    for tick in [3,5,11,15,19,70,72,75,139,142]:
        os=next((f for f in o['rows']if f['tick']==tick),None)
        pf=next((f for f in p['frames']if int(f['tick'])==tick),None)
        if os is None or pf is None:
            rows.append({'tick':tick,'source_retained':os is not None,'port_retained':pf is not None});continue
        a={tuple(v['site']):(str(v['raw']),str(v['clock']))for v in points(os)}
        b={tuple(v['site']):(str(v['raw']),str(v['clock']))for v in points(pf)}
        common=sorted(a.keys()&b.keys())
        rows.append({'tick':tick,'common_site_count':len(common),
                     'different_common_sites':[list(k)for k in common if a[k]!=b[k]],
                     'original_only_sites':[list(k)for k in sorted(a.keys()-b.keys())]})
    keys=['guard_mode','revision_mode','history','actual','bank_values','name_query_payload','new_sign']
    config_equal={k:o['case'][k]==cfg['case'][k]for k in keys}
    origin_requests=[(q['port'],q['payload'],int(q['tick']),'experience'if q['kind']=='submit'else q['kind'])for q in o['requests']if int(q['tick'])<=70]
    port_requests=[(q['port'],q['payload'],int(q['at']),q['kind'])for q in p['calls']if int(q['at'])<=70]
    # Initial metadata and receipt IDs are instrument-specific; preserve order
    # and compare the physical channel/payload/boundary/kind requests separately.
    requests_equal=origin_requests==port_requests
    hubrow=next((i,r)for i,r in enumerate(o['rows'])if r['tick']==15)
    doc={'schema':'DEE.R12.U0.directed_origin_comparison.R01','sources':[meta(op),meta(pp),meta(cp)],
       'new_native_ticks':0,'source_life':'CPC7 IR_P01_GUARDED_M1',
       'port_life':'thinking4.5 closed port IR_P01_GUARDED_M1; a technical preparation, not the same execution',
       'configuration_fields_equal':config_equal,'full_buffer_comparisons':comparisons,
       'T19_full_original_snapshot_retained':any(s['physical']['tick']==19 for s in o['snapshots']),
       'retained_common_local_reads':rows,
       'physical_input_request_sequence_until70_equal':requests_equal,
       'kind_normalization':'Original submit is the ordinary experience API call; the port labels this experience. Probe remains probe. Port/payload/tick/order are compared exactly.',
       'origin_request_count_until70':len(origin_requests),'port_request_count_until70':len(port_requests),
       'source_comparison_hubs_T15':{'source':meta(op),'pointer':'/rows/'+str(hubrow[0])+'/comparison_hubs','observations':hubrow[1]['comparison_hubs']},
       'limit':'No complete originalT19 was retained. T15comparison hubs belong to the separately identified original execution; do not claim a new observation of the4.5port or interpolate its missing microscopic motion. Full boundary equivalence and common local reads are reported as measured, not assumed.'}
    q=OUT/'COTEJO_ORIGEN_U0_R12.json'
    with q.open('x',encoding='utf8')as f:json.dump(doc,f,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps({'output':meta(q),'full_buffer_comparisons':comparisons,
          'configuration_fields_equal':config_equal,'retained_common_local_reads':rows,
          'physical_input_request_sequence_until70_equal':requests_equal,
       'kind_normalization':'Original submit is the ordinary experience API call; the port labels this experience. Probe remains probe. Port/payload/tick/order are compared exactly.',
          'T19_full_original_snapshot_retained':doc['T19_full_original_snapshot_retained']},ensure_ascii=False))
if __name__=='__main__':main()
