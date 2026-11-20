"""Reconcile completed differential proofs without changing original logs."""
from pathlib import Path
import argparse,json,sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from neutral_differential import put,sha

def read(path):return json.loads(path.read_text(encoding='utf8'))
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--validation',type=Path,required=True);parser.add_argument('--candidate',default='candidate1');parser.add_argument('--out',type=Path,required=True);a=parser.parse_args();v=a.validation
    sources=['NEUTRAL_DIFF_'+a.candidate+'.json','BASELINE_BACKEND_EQUIVALENCE.json','CANDIDATE1_BACKEND_EQUIVALENCE.json','CPC_PORT_DIFF_'+a.candidate+'.json','API_DIFF_'+a.candidate+'.json']
    records={name:read(v/name) for name in sources};cross={p.name:read(p) for p in sorted((v/'cross_process_candidate1').glob('*_CHECK.json'))}
    revision_path=v/('FINITE_REVISION_DIFF_'+a.candidate+'.json')
    if revision_path.exists():records[revision_path.name]=read(revision_path)
    failures=[]
    for name,value in records.items():
        if 'pass_count' in value:
            denominator=value.get('total',value.get('case_backend_pairs'))
            if value['pass_count']!=denominator:failures.append(name)
        elif value.get('status')!='PASS':failures.append(name)
    if len(cross)!=4 or any(x['status']!='PASS' for x in cross.values()):failures.append('cross_process_snapshot_coverage')
    original=read(v/'cpc_ports_4_0/INDEX.json');rows=[]
    for item in original['cases']:
        row=dict(item);path=v/'cpc_ports_4_0'/item['result'];recovered=path.with_name('RESULT_RECOVERED.json')
        if not path.exists() and recovered.exists():
            proof=read(recovered)
            if proof['status']!='PASS':raise ValueError('Invalid completion proof')
            row.update({'original_status':item['status'],'status':'PASS','result':recovered.relative_to(v/'cpc_ports_4_0').as_posix(),'technical_completion':'DIRECTED_PENDING_CHECKPOINT_CONTINUATION','original_error_preserved':True})
        rows.append(row)
    put(v/'cpc_ports_4_0/INDEX_COMPLETED.json',{**original,'schema':'DEE45.CPC_native_port.completed_index.v1','cases':rows,'original_index_sha256':sha(v/'cpc_ports_4_0/INDEX.json'),'original_index_preserved':True,'scope':'The single instrumental Windows JSON-replace incident was completed from the already saved pending checkpoint. No initial preparation or teaching history was restarted; original error and arrays remain.'})
    result={'schema':'DEE45.technical_differential_summary.v1','candidate':a.candidate,'status':'PASS' if not failures else 'FAIL','failures':failures,
        'proofs':{name:{'sha256':sha(v/name),'status':value.get('status','PASS' if value.get('pass_count')==value.get('total',value.get('case_backend_pairs')) else 'FAIL'),'count':value.get('total',value.get('case_backend_pairs'))} for name,value in records.items()},
        'cross_process_proofs':{name:{'sha256':sha(v/'cross_process_candidate1'/name),'status':value['status']} for name,value in cross.items()},
        'counts_are_not_independent_scientific_replicas':True,
        'instrumental_incidents':[{'kind':'native_post_trajectory_timeout','cases':2,'original_results':'differential_4_0/INDEX.json','directed_completion':'differential_4_0/INDEX_COMPLETED.json','new_preparations':0},
          {'kind':'Windows_atomic_JSON_replace_AccessDenied','cases':1,'original_result':'cpc_ports_4_0/K65_PAIRED_Q9.PROCESS.json','directed_completion':'cpc_ports_4_0/K65_PAIRED_Q9/RESULT_RECOVERED.json','new_preparations':0,'instrumentation_change':'tools/INSTRUMENTATION_CHANGES.json'}],
        'preserved_adverse_functional_results':['K65_NO_EVENT: queries rejected by occupation, not physical numeric zero','K65_UNPAIRED: late valid responses occur; not a uniformly negative control','Revision offpath controls: first relation may be outside the fixed decoder while second relation remains usable'],
        'documental_exclusions':'Only inert versioned OrganizationalWorld/consolidated descriptor envelopes are normalized in port/snapshot comparisons. RAW, clocks, tick, input payloads, queues, receipts, channels and physical readouts are not normalized away.',
        'scope':'Finite installed-software equivalence and compatibility. These counts do not establish new NSM meanings, autonomous regulation or universal functional performance.'}
    put(a.out,result);print(json.dumps({'status':result['status'],'proofs':len(records),'cross_process':len(cross)}))
    if failures:raise SystemExit(1)
if __name__=='__main__':main()
