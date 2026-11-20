"""Continue a saved ordered MAIN and physically query its retained supports.

No teaching map or expected-result file is opened. The caller supplies a new
query payload and a fixed absolute tick within the published toroidal phase.
"""
from pathlib import Path
import argparse
import json
import sys
import time

HERE=Path(__file__).resolve().parent;sys.path.insert(0,str(HERE))
from common import put,sha,identity,digest,operational,record,local_context,gate
from ordered_composition import OrderedSession


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--snapshot',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--payload',type=int,default=11);p.add_argument('--query-tick',type=int,default=134)
    p.add_argument('--case-id',default='ORDERED_CONTINUE_AB_NEW_QUERY')
    args=p.parse_args();started=time.monotonic();engine=identity()
    if not 0<=args.payload<=65535:raise ValueError('uint16 query payload required')
    if args.query_tick!=134:raise ValueError('This continuation test publishes the next known return phase134 only; other phases require research')
    args.output.mkdir(parents=True,exist_ok=False)
    session=OrderedSession.load(args.snapshot);initial=digest(session.world)
    if initial['tick']!=73:raise ValueError('Continuation requires the measured T73 frontier')
    before_calls=len(session.state['calls']);rows=[];snapshots=[]
    put(args.output/'CONFIG.json',{'case_id':args.case_id,'parent_snapshot':str(args.snapshot),
        'parent_snapshot_sha256':sha(args.snapshot),'source_sha256':sha(__file__),
        'new_query_payload':args.payload,'query_tick':args.query_tick,
        'criterion':'No re-teaching. Load same physical/operative frontier, wait, query declared backup ports and record native response. Current input and geometry, not targets, determine operation.'})
    for item in session.spec['backups']:
        session.submit(item['name']+'.backup.probe',args.payload,args.query_tick,True,'NEW_USER_QUERY_AFTER_SAVE_LOAD_AND_WAIT')
    for tick in (133,134,136,137,140):
        session.run_until(tick)
        row={'tick':tick,'backup_centers':{item['name']:record(session.world,item['hub'])for item in session.spec['backups']}}
        if tick in (136,137):row['contexts']={item['name']:{'neighborhood':local_context(session.world,item['hub']),
              'gate':gate(session.world,item['hub'])}for item in session.spec['backups']}
        rows.append(row)
        if tick in (134,137,140):snapshots.append(session.save(args.output/('T'+str(tick)+'.deetsnap')))
        put(args.output/'INCREMENTAL.json',{'last_tick':tick,'rows':rows,'snapshots':snapshots})
    result={'schema':'CPC5.extension.ordered-continuation.v1','case':{'id':args.case_id,'phase':'CONTINUATION'},
            'status':'MEASURED','source_sha256':sha(__file__),'engine':engine,'preparations':0,'continuations':1,
            'parent_snapshot':str(args.snapshot),'parent_sha256':sha(args.snapshot),'initial':initial,
            'new_calls':session.state['calls'][before_calls:],'receipts':operational(session.world)['receipts'],
            'rows':rows,'snapshots':snapshots,'final':digest(session.world),'operative_final':operational(session.world),
            'same_runtime_from_restored_frontier':True,'new_teaching_inputs':0,'host_RAW_clock_writes':0,
            'elapsed_seconds':time.monotonic()-started,'scope':'Second-process continuation with a new physical query at a known access phase. Does not imply phase-independent or unbounded access.'}
    put(args.output/'MEASUREMENTS.json',result)
    print(json.dumps({'case_id':args.case_id,'initial_tick':initial['tick'],'final':result['final'],
                     'response':next(r for r in rows if r['tick']==137),'elapsed_seconds':result['elapsed_seconds']},ensure_ascii=False))


if __name__=='__main__':main()
