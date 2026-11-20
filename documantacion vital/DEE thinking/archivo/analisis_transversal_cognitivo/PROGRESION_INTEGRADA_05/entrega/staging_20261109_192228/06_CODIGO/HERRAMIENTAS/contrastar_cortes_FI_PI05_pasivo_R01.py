"""Exact closed snapshot comparison; Native payload receipts are not assumed."""
from pathlib import Path
import argparse,hashlib,json,runpy
def info(p):
    b=Path(p).read_bytes();return {'path':str(Path(p).resolve()),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--proof-a',required=True,type=Path);ap.add_argument('--proof-b',required=True,type=Path);ap.add_argument('--out',required=True,type=Path);ap.add_argument('--root',type=Path,default=Path(__file__).resolve().parent.parent);args=ap.parse_args()
    if args.out.exists():raise FileExistsError('Do not overwrite')
    p=args.root;parser=p/'codigo/contrastar_prefijos_C2C_PI05_pasivo.py';m=runpy.run_path(str(parser),run_name='pure_closed_snapshot_reader');values={};views={};sources={};preservation={}
    for arm,path in [('a',args.proof_a),('b',args.proof_b)]:
        d=json.loads(path.read_text(encoding='utf-8'))
        if not d['owner_closed_coherently']:raise ValueError('Exact closed Native proof required')
        cut=d['actual']['committed_snapshot'];snapshot=p/'estados/candidato/sistema'/cut['snapshot'];before=info(snapshot);v=m['parse'](snapshot,cut['snapshot_sha256']);after=info(snapshot)
        if before!=after:raise ValueError('Immutable snapshot changed')
        if v[0]['physical']!={k:cut['physical'][k]for k in('N','tick','RAW_sha256','clocks_sha256')}:raise ValueError('Physical cut mismatch')
        values[arm]=v;views[arm]=v[0];sources[arm]={'proof':info(path),'life':d['life_id'],'public_literal':d['public_literal'],'material_primary':d['material_primary']};preservation[arm]={'before':before,'after':after,'equal':True}
    a=values['a'];b=values['b'];rd=[];cd=[]
    for i,(x,y)in enumerate(zip(a[1],b[1])):
        if x!=y:rd.append({'site':[i//4489,(i//67)%67,i%67],'a':m['decode'](x),'b':m['decode'](y)})
        if a[2][i]!=b[2][i]:cd.append([i//4489,(i//67)%67,i%67])
    ra={r['id']:r for r in a[5]};rb={r['id']:r for r in b[5]};rc=[{'id':k,'a':ra.get(k),'b':rb.get(k)}for k in sorted(set(ra)|set(rb))if ra.get(k)!=rb.get(k)]
    meta=m['metamap'](a[6],b[6]);receipt_fields=sorted(set(k for item in a[5]+b[5]for k in item))
    result={'schema':'DEE.PI05.closed_FI_snapshots.passive_comparison.R01','mode':'COMPLETE_IMMUTABLE_NATIVE_SNAPSHOT_PARSE_NO_SQLITE_NO_DEE','Native_ticks':0,'parser':info(parser),'sources':sources,'preservation':preservation,'views':views,
      'comparison':{'GLOBAL_RAW_exact':a[7]==b[7],'GLOBAL_clocks_exact':a[8]==b[8],'RAW_difference_count':len(rd),'RAW_differences':rd,'clock_difference_count':len(cd),'clock_differences':cd,'interfaces_exact':a[3]==b[3],'agenda_exact':a[4]==b[4],'Native_receipt_history_exact':a[5]==b[5],'Native_receipt_difference_count':len(rc),'Native_receipt_differences':rc,'metadata_exact':a[6]==b[6],'metadata_differences':meta,'causal_prefix_bytes_exact':a[0]['causal_prefix_sha256']==b[0]['causal_prefix_sha256'],'execution_header':{k:{'a':a[0][k],'b':b[0][k],'equal':a[0][k]==b[0][k]}for k in ['phase','paused','next_event_id','next_sequence','backend_enum','threads']}},
      'receipt_payload_check':{'parsed_receipt_field_names':receipt_fields,'payload_field_present':any('payload'in k.lower()for k in receipt_fields),'scope':'NativeReceipt records identifiers/channels/timing/status/reason; do not assert that equal receipts preserve differing payloads.'},
      'scope':'Physical RAW/clocks equality, Native causal-prefix equality and metadata equality are reported separately. Material primaries preserve actual submitted payloads/public literals even when physical buffers converge; this script does not open their transport SQLite, live current VIDA or actor API.'}
    with args.out.open('x',encoding='utf-8')as f:json.dump(result,f,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps({'proof':info(args.out),'comparison':{k:v for k,v in result['comparison'].items()if not isinstance(v,(list,dict))},'metadata_differences':[{'key':r['key'],'fields':r['field_differences']}for r in meta],'receipt_payload_check':result['receipt_payload_check']},ensure_ascii=False)[:5000])
if __name__=='__main__':main()
