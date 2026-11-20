"""Post-recording exact binary comparisons and isolated snapshot continuation.

No historical outcomes are supplied to a participant. Comparison modes import
no native module; only resume mode loads an installed library and evolves.
"""
from pathlib import Path
import argparse,gzip,json,sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from neutral_differential import native,exact_array,operative,put,sha,hashes


def read(path):return json.loads(Path(path).read_text(encoding='utf-8'))


def read_index(directory):
    completed=directory/'INDEX_COMPLETED.json'
    return read(completed if completed.exists() else directory/'INDEX.json')


def binary_equal(a,b):
    size=0
    with gzip.open(a,'rb') as x,gzip.open(b,'rb') as y:
        while True:
            left=x.read(1048576);right=y.read(1048576)
            if left!=right:return False,size
            size+=len(left)
            if not left:return True,size


def frame_compare(x,y,leftdir,rightdir):
    rows=[]
    if len(x['frames'])!=len(y['frames']):return [{'frame_count_equal':False}]
    for a,b in zip(x['frames'],y['frames']):
        raw,nraw=binary_equal(leftdir/a['raw']['path'],rightdir/b['raw']['path'])
        clock,nclock=binary_equal(leftdir/a['clock']['path'],rightdir/b['clock']['path'])
        rows.append({'tick':a['tick'],'tick_equal':a['tick']==b['tick'],'RAW_binary_equal':raw,
                     'clock_binary_equal':clock,'RAW_bytes_compared':nraw,'clock_bytes_compared':nclock,
                     'operative_equal':a['operative']==b['operative'],'observations_equal':a['observations']==b['observations'],
                     'world_protocol_equal':a.get('world')==b.get('world')})
    return rows


def passed(rows):
    for row in rows:
        for name,value in row.items():
            if name.endswith('_equal') and not value:return False
    return bool(rows)


def backends(args):
    idx=read_index(args.suite);groups={};results=[]
    for item in idx['cases']:groups.setdefault(item['case_id'],{})[item['backend']]=item
    for case,items in groups.items():
        first=items['DENSE_SEQUENTIAL'];x=read(args.suite/first['result'])
        for backend in ('DENSE_PARALLEL','LAZY'):
            other=items[backend];y=read(args.suite/other['result'])
            rows=frame_compare(x,y,(args.suite/first['result']).parent,(args.suite/other['result']).parent)
            results.append({'case':case,'reference':'DENSE_SEQUENTIAL','other':backend,'status':'PASS' if passed(rows) else 'FAIL','frontiers':rows})
    put(args.out,{'schema':'DEE45.backend_binary_comparison.v1','library':idx['library'],'comparisons':results,
        'pass_count':sum(r['status']=='PASS' for r in results),'total':len(results),'binary_streams_compared':True,
        'excluded':'Host execution timing and scheduling counters, not physical RAW/clocks or receipt state.'})
    if any(r['status']!='PASS' for r in results):raise SystemExit(1)
    print(json.dumps({'backend_comparisons':len(results),'pass':len(results)}))


def versions(args):
    before=read_index(args.before);after=read_index(args.after)
    if before['config_sha256']!=after['config_sha256']:raise AssertionError('Different neutral configurations')
    a={(x['case_id'],x['backend']):x for x in before['cases']};b={(x['case_id'],x['backend']):x for x in after['cases']}
    if set(a)!=set(b):raise AssertionError('Differing case coverage')
    rows=[]
    for key,item in a.items():
        other=b[key];x=read(args.before/item['result']);y=read(args.after/other['result'])
        frames=frame_compare(x,y,(args.before/item['result']).parent,(args.after/other['result']).parent)
        rows.append({'case':key[0],'backend':key[1],'status':'PASS' if passed(frames) else 'FAIL','frontiers':frames,
                     'before_result_sha256':sha(args.before/item['result']),'after_result_sha256':sha(args.after/other['result'])})
    put(args.out,{'schema':'DEE45.version_binary_comparison.v1','before':before['library'],'after':after['library'],
        'case_backend_pairs':len(rows),'pass_count':sum(r['status']=='PASS' for r in rows),'cases':rows,
        'comparison':'Every complete little-endian uint64 array is decompressed and compared by streaming bytes; no sampling and no uint64→float conversion.'})
    if any(r['status']!='PASS' for r in rows):raise SystemExit(1)
    print(json.dumps({'version_comparisons':len(rows),'pass':len(rows)}))


def resume(args):
    d,engine=native(args.expected_version);args.out.mkdir(parents=True,exist_ok=False)
    if args.kind=='runtime':w=None;r=d.Runtime.load_snapshot(str(args.snapshot))
    else:w=d.OrganizationalWorld.load_snapshot(str(args.snapshot));r=w.runtime
    initial=hashes(r)
    if args.target_tick<int(r.current_tick):raise ValueError('Cannot rewind during restoration')
    (w.run_until(args.target_tick) if w is not None else r.run_until(args.target_tick))
    report={'schema':'DEE45.cross_process_snapshot_resume.v1','engine':engine,'source_snapshot_sha256':sha(args.snapshot),
        'source_snapshot':args.snapshot.name,'kind':args.kind,'initial':initial,'final':hashes(r),
        'raw':exact_array(r.raw_copy(),args.out/'FINAL.raw.u64.gz'),'clock':exact_array(r.clock_copy(),args.out/'FINAL.clock.u64.gz'),
        'operative':operative(r),'initial_factory_calls':0,'new_experiences':[]}
    if w is not None:report['world']={'ids':list(w.organization_ids),'external_operations':list(w.external_operations),
                'protocols':[{'id':p.id,'next_capture':p.next_capture} for p in w.protocols]}
    put(args.out/'RESUME.json',report);print(json.dumps({'restored_version':args.expected_version,'kind':args.kind,'final_tick':report['final']['tick']}))


def resume_check(args):
    resumed=read(args.resumed/'RESUME.json');reference=read(args.reference/'RESULT.json');last=reference['frames'][-1]
    raw,nraw=binary_equal(args.resumed/resumed['raw']['path'],args.reference/last['raw']['path'])
    clock,nclock=binary_equal(args.resumed/resumed['clock']['path'],args.reference/last['clock']['path'])
    normalize=lambda x:{**x,'snapshot_metadata':{k:v for k,v in x['snapshot_metadata'].items() if not k.startswith('dee_thinking.organizational.')}}
    checks={'RAW_binary_equal':raw,'clock_binary_equal':clock,'tick_equal':resumed['final']['tick']==last['tick'],
            'operative_equal_excluding_wrapper_envelope':normalize(resumed['operative'])==normalize(last['operative']),
            'world_protocol_equal':resumed.get('world')==last.get('world')}
    put(args.out,{'schema':'DEE45.cross_process_snapshot_check.v1','checks':checks,'RAW_bytes_compared':nraw,
        'clock_bytes_compared':nclock,'source_snapshot_sha256':resumed['source_snapshot_sha256'],
        'resuming_library':resumed['engine']['library'],'reference_library':reference['library'],
        'initial_factory_calls':0,'status':'PASS' if all(checks.values()) else 'FAIL',
        'metadata_scope':'Versioned OrganizationalWorld serialization envelopes are inert; compare mutable operational fields and receipts apart from the load/save wrapper.'})
    if not all(checks.values()):raise SystemExit(1)
    print(json.dumps({'snapshot_cross_process':'PASS'}))


def recover(args):
    """Finish technical checks of a completely recorded path, never reprepare."""
    cfg=read(args.case/'CONFIG.json');progress=read(args.case/'PROGRESS.json')
    if progress['last_tick']!=str(cfg['case']['frontiers'][-1]):raise ValueError('Main trajectory has not recorded its terminal frontier')
    if len(progress['frames'])!=len(cfg['case']['frontiers']):raise ValueError('Missing original trajectory frontiers')
    d,engine=native(args.expected_version);kind=cfg['case']['kind'];args.out.mkdir(parents=True,exist_ok=False)
    source=args.case/'PENDING.deetsnap'
    w=d.OrganizationalWorld.load_snapshot(str(source)) if kind=='recipe' else None
    r=w.runtime if w is not None else d.Runtime.load_snapshot(str(source))
    r.execution_options=d.TickOptions(getattr(d.Backend,cfg['backend']),2 if cfg['backend']=='DENSE_PARALLEL' else 1)
    start=hashes(r);last=progress['frames'][-1]
    (w.run_until(int(last['tick'])) if w is not None else r.run_until(int(last['tick'])))
    raw=exact_array(r.raw_copy(),args.out/'FINAL.raw.u64.gz');clock=exact_array(r.clock_copy(),args.out/'FINAL.clock.u64.gz')
    raw_equal,nraw=binary_equal(args.out/raw['path'],args.case/last['raw']['path'])
    clock_equal,nclock=binary_equal(args.out/clock['path'],args.case/last['clock']['path'])
    normalize=lambda x:{**x,'snapshot_metadata':{k:v for k,v in x['snapshot_metadata'].items() if not k.startswith('dee_thinking.organizational.')}}
    op=operative(r);oper_equal=normalize(op)==normalize(last['operative'])
    if not(raw_equal and clock_equal and oper_equal):raise AssertionError('Continuation differs from recorded terminal arrays/operations')
    before=hashes(r);child=w.fork() if w is not None else r.fork();child.advance(1)
    parent_equal=hashes(r)==before and operative(r)==op
    if not parent_equal:raise AssertionError('Fork mutated recovery parent')
    checks={'RAW_binary_equal':raw_equal,'clock_binary_equal':clock_equal,'operative_equal_excluding_envelope':oper_equal,
        'fork_parent_unchanged':parent_equal,'RAW_bytes_compared':nraw,'clock_bytes_compared':nclock,
        'continued_from_tick':start['tick'],'continued_to_tick':last['tick'],'new_preparations':0,
        'source_snapshot_sha256':sha(source),'engine':engine,'status':'PASS'}
    put(args.out/'RECOVERY.json',checks)
    original_engine=cfg['engine']
    report={'schema':'DEE45.neutral_differential.case.v1','case_id':cfg['case']['id'],'backend':cfg['backend'],
        'library':args.expected_version,'status':'PASS','engine':original_engine,'config_sha256':cfg['config_sha256'],
        'source_sha256':cfg['source_sha256'],'frames':progress['frames'],'calls':progress['calls'],
        'snapshot':{'path':'PENDING.deetsnap','sha256':sha(source),'kind':kind},
        'final':before,'final_operative':last['operative'],'technical':checks,
        'completion_provenance':'Original direct main trajectory completed and saved all arrays. Its post-trajectory technical checks timed out. This independent process resumed its pending checkpoint and verified byte-exact continuation plus fork isolation; the timeout record is retained.',
        'recovery_evidence':str((args.out/'RECOVERY.json').resolve()),'original_timeout_preserved':True}
    put(args.case/'RESULT_RECOVERED.json',report)
    print(json.dumps({'technical_completion':'PASS','case':cfg['case']['id'],'backend':cfg['backend'],'new_preparations':0}))


def reconcile(args):
    original=read(args.suite/'INDEX.json');rows=[];recovered=0
    for item in original['cases']:
        row=dict(item);candidate=(args.suite/item['result']).with_name('RESULT_RECOVERED.json')
        if item['status']=='TIMEOUT' and candidate.exists():
            result=read(candidate)
            if result['status']!='PASS' or not result['original_timeout_preserved']:raise ValueError('Invalid directed completion proof')
            row.update({'original_status':'TIMEOUT','status':'PASS','technical_completion':'DIRECTED_PENDING_CHECKPOINT_CONTINUATION',
                'result':candidate.relative_to(args.suite).as_posix()});recovered+=1
        rows.append(row)
    put(args.suite/'INDEX_COMPLETED.json',{**original,'schema':'DEE45.neutral_differential.completed_index.v1','cases':rows,
        'original_index_sha256':sha(args.suite/'INDEX.json'),'original_index_preserved':True,'directed_completions':recovered,
        'scope':'No preparation restarted. Original direct-trajectory arrays and timeout logs remain; post-trajectory checks completed from pending physical/operative snapshots in separate processes.'})
    print(json.dumps({'cases':len(rows),'directed_completions':recovered,'pass':sum(x['status']=='PASS' for x in rows)}))


def main():
    p=argparse.ArgumentParser();sub=p.add_subparsers(dest='mode',required=True)
    s=sub.add_parser('backends');s.add_argument('--suite',type=Path,required=True);s.add_argument('--out',type=Path,required=True)
    s=sub.add_parser('versions');s.add_argument('--before',type=Path,required=True);s.add_argument('--after',type=Path,required=True);s.add_argument('--out',type=Path,required=True)
    s=sub.add_parser('resume');s.add_argument('--snapshot',type=Path,required=True);s.add_argument('--kind',choices=['runtime','recipe'],required=True)
    s.add_argument('--expected-version',required=True);s.add_argument('--target-tick',type=int,required=True);s.add_argument('--out',type=Path,required=True)
    s=sub.add_parser('resume-check');s.add_argument('--resumed',type=Path,required=True);s.add_argument('--reference',type=Path,required=True);s.add_argument('--out',type=Path,required=True)
    s=sub.add_parser('recover');s.add_argument('--case',type=Path,required=True);s.add_argument('--expected-version',required=True);s.add_argument('--out',type=Path,required=True)
    s=sub.add_parser('reconcile');s.add_argument('--suite',type=Path,required=True)
    args=p.parse_args();{'backends':backends,'versions':versions,'resume':resume,'resume-check':resume_check,'recover':recover,'reconcile':reconcile}[args.mode](args)

if __name__=='__main__':main()
