"""Read frozen full frames to check a proposed P0 guard/sham, no Native."""
from pathlib import Path
import hashlib,importlib.util,json,struct
H=Path(__file__).resolve().parent;P=H.parent
spec=importlib.util.spec_from_file_location('PI05_fixed_codec_preflight',H/'observador_global_PI05_R01.py')
codec=importlib.util.module_from_spec(spec);spec.loader.exec_module(codec)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def field(raw):
    # Frozen kernel packing: STATE32, SREG16, XYZ signed4 each, SEM4.
    ds=[(raw>>s)&15 for s in(48,52,56)]
    return {'raw':str(raw),'state':raw&0xffffffff,'s_reg':(raw>>32)&65535,
            'direction':[x-16 if x>=8 else x for x in ds],'semantic':(raw>>60)&15}
def main():
    a=P/'control/AUTOPSIA_TRANSITO_REAL_GLOBAL_R01.json';auto=json.loads(a.read_text('utf8'))
    capture=Path(auto['capture_index']['path']).parent
    primary=Path(auto['source_proof']['path']);packet=json.loads(primary.read_text('utf8'))
    actual=packet['actual']['result']['rows'][0];requests=actual['requests']
    points=[(19,53,20),(19,53,21),(21,53,20),(19,55,20),(21,55,20)]
    rows={str(p):[]for p in points}
    for f in codec.iter_frames(capture):
        for point in points:
            i=(point[0]*67+point[1])*67+point[2]
            raw=struct.unpack_from('<Q',f['raw_bytes'],8*i)[0];clock=struct.unpack_from('<Q',f['clocks_bytes'],8*i)[0]
            rows[str(point)].append({'tick':f['tick'],'clock':str(clock),**field(raw)})
    result={'schema':'DEE.PI05.P0_guard_candidate_frozen_preflight.R01','Native_executed':False,'new_ticks':0,
        'capture_index':{'file':str(capture/'INDEX.json'),'sha256':sha(capture/'INDEX.json')},
        'source_primary':{'file':str(primary),'sha256':sha(primary)},
        'candidate_points':[],
        'scope':'Observed unmodified recorded window only; not proof of future safety, causal success, learned regulation or recovery. No interpolation across gaps.'}
    for point in points:
        rr=rows[str(point)];lookup={x['tick']:x for x in rr}
        direct=[r for r in requests if r.get('site')==list(point)]
        result['candidate_points'].append({'point':list(point),'at_proposed_injection_817878':lookup.get(817878),
            'nonzero_RAW_observations':[r for r in rr if r['raw']!='0'],
            'direct_request_count_at_point':len(direct),'direct_requests':direct,
            'all_recorded_ticks_RAW0':all(r['raw']=='0'for r in rr),'sampled_ticks':len(rr)})
    out=P/'control/PROPUESTA_GUARDIA_PREFLIGHT_PASIVO_R01.json'
    if out.exists():raise ValueError('Preserve prior proposal')
    out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps({'file':str(out),'sha256':sha(out),'points':result['candidate_points']},ensure_ascii=False))
if __name__=='__main__':main()
