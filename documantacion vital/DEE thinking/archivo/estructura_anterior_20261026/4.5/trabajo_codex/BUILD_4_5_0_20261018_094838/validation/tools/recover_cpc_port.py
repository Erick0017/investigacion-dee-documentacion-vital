"""Continue an interrupted Q9 validation from its pending physical checkpoint.

Prior observations are audit data only. The only new inputs are the frozen
ordinary probes of rounds2/3. No history is recreated or response map consulted.
"""
from pathlib import Path
import argparse,json,sys,time
sys.path.insert(0,str(Path(__file__).resolve().parent))
from neutral_differential import native,put,sha,exact_array,operative,receipt,observation
from neutral_checks import binary_equal
from cpc_port import directional


def main():
    p=argparse.ArgumentParser();p.add_argument('--case',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    cfg=json.loads((a.case/'CONFIG.json').read_text(encoding='utf-8'));case=cfg['case']
    if case['id']!='K65_PAIRED_Q9' or case['query_payload']!=9 or case['N']!=131:raise ValueError('This recovery is limited to the preserved Q9 writer incident')
    pending=a.case/'PROGRESS.json.pending.9760';prior=json.loads(pending.read_text(encoding='utf-8'))
    if prior['last_tick']!='265':raise ValueError('Expected complete surviving frontier265')
    d,engine=native('4.0.0');a.out.mkdir(parents=True,exist_ok=False);start=time.monotonic()
    source=a.case/'PENDING_T131.deetsnap';w=d.OrganizationalWorld.load_snapshot(str(source));r=w.runtime
    r.execution_options=d.TickOptions(d.Backend.LAZY,1)
    if r.current_tick!=131:raise AssertionError('Wrong physical checkpoint')
    intermediate=[];new_calls=[];last_rows=[]
    forms=cfg['geometry']['forms']
    for tick in (134,262,265,393,396):
        w.run_until(tick)
        if tick in (262,393):
            last_rows=[]
            for form in forms:
                result=w.probe(form['name']+'.signal',9,tick)
                new_calls.append({'id':str(result.id),'port':form['name']+'.signal','payload':9,'at':str(tick),'call_tick':str(tick),'kind':'probe'})
                last_rows.append((form,int(result.id)))
        if tick in (134,265):
            raw=exact_array(r.raw_copy(),a.out/f'T{tick}.raw.u64.gz');clock=exact_array(r.clock_copy(),a.out/f'T{tick}.clock.u64.gz')
            req,nraw=binary_equal(a.out/raw['path'],a.case/f'T{tick}.raw.u64.gz');ceq,nclock=binary_equal(a.out/clock['path'],a.case/f'T{tick}.clock.u64.gz')
            if not(req and ceq):raise AssertionError('Restored intermediate differs from saved primary frontier')
            intermediate.append({'tick':tick,'RAW_binary_equal':req,'clock_binary_equal':ceq,'RAW_bytes_compared':nraw,'clock_bytes_compared':nclock})
    old_second=[x for x in prior['calls'] if x['call_tick']=='262']
    replayed_second=[x for x in new_calls if x['call_tick']=='262']
    if old_second!=replayed_second:raise AssertionError('Repeated fixed round2 requests/IDs differ from prior ledger')
    raw=exact_array(r.raw_copy(),a.case/'T396.raw.u64.gz');clock=exact_array(r.clock_copy(),a.case/'T396.clock.u64.gz')
    frame={'tick':'396','forms':{f['name']:observation(r,f['hub'],d) for f in forms},'raw':raw,'clock':clock,'operative':operative(r)}
    reads=list(prior['readouts'])
    for form,identifier in last_rows:
        physical=observation(r,form['hub'],d);rr=receipt(r.receipt(identifier))
        reads.append({'form':form['name'],'panel':'ROUND3','tick':'396',**directional(physical,rr,9)})
    calls=prior['calls']+[x for x in new_calls if x['call_tick']=='393']
    target=a.case/'PENDING_T396.deetsnap';w.save_snapshot(str(target));loaded=d.OrganizationalWorld.load_snapshot(str(target))
    if loaded.runtime.raw_copy()!=r.raw_copy() or loaded.runtime.clock_copy()!=r.clock_copy() or loaded.runtime.current_tick!=396:raise AssertionError('Recovery final snapshot differs')
    recovery={'schema':'DEE45.CPC_port.IO_recovery.v1','status':'PASS','source_checkpoint_sha256':sha(source),
        'surviving_pending_JSON_sha256':sha(pending),'intermediate_binary_comparisons':intermediate,
        'round2_input_ledger_and_identifiers_equal':True,'new_preparations':0,'new_teaching_experiences':0,
        'original_writer_error_preserved':True,'continued_from_tick':131,'continued_to_tick':396,
        'new_future_probe_requests':'65 at393; round2 at262 repeated only to verify the exact already recorded physical continuation',
        'source_sha256':sha(__file__),'elapsed_seconds':time.monotonic()-start}
    put(a.out/'RECOVERY.json',recovery)
    result={'schema':'DEE45.CPC_native_port.measurements.v1','case_id':case['id'],'kind':case['kind'],'library':'4.0.0','status':'PASS',
        'engine':engine,'config_sha256':cfg['config_sha256'],'constructor_sources':cfg['constructor_sources'],'source_sha256':cfg['source_sha256'],
        'frames':prior['frames']+[frame],'readouts':reads,
        'calls':[{**c,'final_receipt':receipt(r.receipt(int(c['id'])))} for c in calls],'final_operative':operative(r),
        'checkpoints':[{'path':source.name,'tick':'131','sha256':sha(source)},{'path':target.name,'tick':'396','sha256':sha(target)}],
        'technical':{'save_load_RAW_clocks_tick_equal':True,'candidate_historical_lab_imports':None,'recovery':recovery},
        'preparations':1,'elapsed_seconds':time.monotonic()-start,
        'scope':'Original preparation continued from131, with intermediate134/265 bit-exact verification and original Windows writer failure retained. This is a technical completion, not a new independent cognitive replicate.'}
    put(a.case/'RESULT_RECOVERED.json',result)
    print(json.dumps({'case':case['id'],'status':'PASS','new_preparations':0,'queries':len(reads),'covered':sum(x['covered'] for x in reads)}))

if __name__=='__main__':main()
