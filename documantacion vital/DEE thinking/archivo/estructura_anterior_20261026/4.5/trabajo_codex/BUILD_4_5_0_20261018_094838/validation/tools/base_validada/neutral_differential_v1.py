"""Version-neutral Runtime/native-recipe recorder and exact differential checker.

Use separate installed interpreter processes for4.0 and4.5. This instrument
never imports historical lab modules, never selects a native answer and never
constructs a cognitive session. All uint64 values remain integers/strings/bytes.
"""
from __future__ import annotations
from array import array
import argparse,gzip,hashlib,importlib.resources,json,os,subprocess,sys,time,traceback
from pathlib import Path

HERE=Path(__file__).resolve().parent
DEFAULT_CONFIG=HERE/'neutral_config.json'


def sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda:f.read(1048576),b''):h.update(block)
    return h.hexdigest()


def put(path,value):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    temp=path.with_name(path.name+'.pending.'+str(os.getpid()))
    temp.write_text(json.dumps(value,ensure_ascii=False,indent=2),encoding='utf-8');os.replace(temp,path)


def native(expected):
    import dee_thinking as package
    from dee_thinking import _native as d
    if package.__version__!=expected:raise AssertionError('Wrong installed library version')
    if sys.version_info[:2]!=(3,13) or sys.maxsize<2**32:raise AssertionError('CPython3.13x64 required')
    if not Path(package.__file__).resolve().is_relative_to(Path(sys.prefix).resolve()):raise AssertionError('Module outside isolated installation')
    if 'dee_universe_v27' in sys.modules:raise AssertionError('Unexpected historical kernel dependency')
    result={'library':package.__version__,'python':sys.executable,'prefix':sys.prefix,'package':package.__file__,
        'native':d.__file__,'native_sha256':sha(d.__file__),'build_info':d.build_info(),
        'kernel_modulus':d.KERNEL_MODULUS,'reducer_cap':d.REDUCER_CAP,
        'cognitive_session_factories_called':0,'historical_lab_imports':[]}
    if expected=='4.0.0' and result['native_sha256']!='20d7c764dbc22d1f110ba255f92073b4f64c744c91f6980335a4e08dd61fe066':raise AssertionError('Not official4.0PYD')
    if (d.KERNEL_MODULUS,d.REDUCER_CAP)!=(19665,19664):raise AssertionError('Kernel constants differ')
    return d,result


def index(q,n):return q[0]*n*n+q[1]*n+q[2]


def exact_array(values,path):
    values=array('Q',values)
    if sys.byteorder!='little':values.byteswap()
    data=values.tobytes()
    with gzip.GzipFile(filename=str(path),mode='wb',mtime=0) as f:f.write(data)
    return {'path':path.name,'encoding':'gzip(little-endian uint64)','elements':len(values),'bytes':len(data),
            'sha256_uncompressed':hashlib.sha256(data).hexdigest(),'sha256_compressed':sha(path)}


def receipt(r):
    return {'id':str(r.id),'kind':str(r.kind),'status':str(r.status),'requested_tick':str(r.requested_tick),
            'effective_tick':None if r.effective_tick is None else str(r.effective_tick),'channels':list(r.channels),'reason':r.reason}


def operative(runtime):
    return {'tick':str(runtime.current_tick),'dimension':runtime.dimension,'paused':runtime.paused,
            'protocol_phase':runtime.protocol_phase,'channels':list(runtime.channel_names),
            'receipts':[receipt(r) for r in runtime.receipts],'snapshot_metadata':dict(runtime.snapshot_metadata_entries)}


def observation(runtime,q,d):
    o=runtime.observe(d.Coordinate(*q));r=o.record
    return {'site':list(q),'tick':str(o.tick),'raw':str(o.raw),'clock':str(o.clock),'state':r.state,'s_reg':r.s_reg,
            'direction':[r.dx,r.dy,r.dz],'semantic':r.semantic,'raw_present':r.raw_present,'occupied':r.occupied}


def hashes(runtime):
    return {'tick':str(runtime.current_tick),'raw':hashlib.sha256(array('Q',runtime.raw_copy()).tobytes()).hexdigest(),
            'clock':hashlib.sha256(array('Q',runtime.clock_copy()).tobytes()).hexdigest()}


def create(case,backend,d):
    if case['kind']=='runtime':
        n=case['N'];raw=[0]*(n**3);clocks=[0]*(n**3);sites=[]
        for placement in case['placements']:
            q=placement['site'];i=index(q,n)
            if q in sites:raise ValueError('Duplicate initial placement')
            sites.append(q);raw[i]=d.pack_record(*placement['record']);clocks[i]=int(placement['clock'])
        r=d.Runtime.import_research_state(n,int(case.get('start_tick','0')),raw,clocks)
        for item in case.get('channels',[]):
            c=d.ChannelSpec();c.name=item['name'];c.injection_site=d.Coordinate(*item['site']);c.state=1
            c.direction=d.Direction(*item['direction']);c.semantic=1;c.allow_experience=item.get('experience',True);c.allow_probe=item.get('probe',True)
            r.register_channel(c)
        r.execution_options=d.TickOptions(getattr(d.Backend,backend),2 if backend=='DENSE_PARALLEL' else 1)
        r.protocol_phase='neutral_differential/'+case['id'];r.set_snapshot_metadata('neutral.uint64',str((1<<63)+7))
        return r,None,sites
    seed=str(importlib.resources.files('dee_thinking').joinpath('data/OBP_FRESH_VALIDATED_T32.deetsnap'))
    if case['recipe']=='mobile_pair':rec=d.OrganizationRecipe.mobile_pair()
    elif case['recipe']=='phase':rec=d.OrganizationRecipe.phase(1)
    elif case['recipe']=='relational':rec=d.OrganizationRecipe.relational(seed,d.BasalHistory.AB,False)
    elif case['recipe']=='cascade2':rec=d.OrganizationRecipe.cascade(2)
    else:raise ValueError('Unrecognized frozen recipe')
    rec.execution=d.TickOptions(getattr(d.Backend,backend),2 if backend=='DENSE_PARALLEL' else 1)
    w=d.OrganizationalWorld.create(rec);r=w.runtime
    sites=[]
    for oid in w.organization_ids:
        for q in w.view(oid).spec.ports.values():
            site=[q.x,q.y,q.z]
            if site not in sites:sites.append(site)
    return r,w,sites


def call(spec,r,w,d):
    if spec['kind']=='batch':
        inputs=[]
        for name,load in spec['inputs']:
            item=d.InputRequest();item.channel=name;item.s_reg=load;inputs.append(item)
        return r.experience_batch(inputs,spec['at'])
    if w is None:return getattr(r,spec['kind'])(spec['port'],spec['at'],spec['payload'])
    return getattr(w,spec['kind'])(spec['port'],spec['payload'],spec['at'])


def run_one(case,backend,out,expected,config_hash):
    out=Path(out);out.mkdir(parents=True,exist_ok=False);started=time.monotonic();d,engine=native(expected)
    r,w,sites=create(case,backend,d);start=int(r.current_tick)
    frontiers=[start+t if case.get('relative_frontiers') else t for t in case['frontiers']]
    mid=start+case['snapshot_tick'] if case.get('relative_frontiers') else case['snapshot_tick']
    schedule=case.get('calls',[]);ticks=sorted(set(frontiers+[x['call_tick'] for x in schedule]));frames=[];calls=[];snapshot=None;passive=[]
    put(out/'CONFIG.json',{'case':case,'backend':backend,'config_sha256':config_hash,'source_sha256':sha(__file__),'engine':engine})
    for tick in ticks:
        (w.run_until(tick) if w is not None else r.run_until(tick))
        for spec in schedule:
            if spec['call_tick']==tick:
                result=call(spec,r,w,d);calls.append({'spec':spec,'receipt_at_request':receipt(result)})
        if tick not in frontiers:continue
        before=hashes(r)
        for _ in range(3):
            r.observe_many([d.Coordinate(*q) for q in sites[:12]]);r.metrics()
            if sites:d.inspect_write_gate(r,d.Coordinate(*sites[0]),True)
        if hashes(r)!=before:raise AssertionError('Passive observer mutated state')
        passive.append({'tick':str(tick),'unchanged':True})
        frame={'tick':str(tick),'raw':exact_array(r.raw_copy(),out/f'T{tick}.raw.u64.gz'),
            'clock':exact_array(r.clock_copy(),out/f'T{tick}.clock.u64.gz'),'operative':operative(r),
            'observations':[observation(r,q,d) for q in sites[:64]]}
        if w is not None:
            frame['world']={'ids':list(w.organization_ids),'external_operations':list(w.external_operations),
                'protocols':[{'id':p.id,'next_capture':p.next_capture} for p in w.protocols]}
        frames.append(frame)
        if tick==mid:
            path=out/'PENDING.deetsnap'
            (w.save_snapshot(str(path)) if w is not None else r.save_snapshot(str(path)))
            snapshot={'path':path.name,'sha256':sha(path),'tick':str(tick),'kind':case['kind']}
        put(out/'PROGRESS.json',{'complete_frontiers':len(frames),'last_tick':str(tick),'frames':frames,'calls':calls})
    final=hashes(r);op=operative(r)
    # Fork is deep; mutating its future may not change the original state/queue.
    child=w.fork() if w is not None else r.fork();cr=child.runtime if w is not None else child
    cr.advance(1)
    if hashes(r)!=final or operative(r)!=op:raise AssertionError('Fork aliases parent')
    path=out/snapshot['path']
    loaded=d.OrganizationalWorld.load_snapshot(str(path)) if w is not None else d.Runtime.load_snapshot(str(path))
    lr=loaded.runtime if w is not None else loaded
    (loaded.run_until(int(final['tick'])) if w is not None else lr.run_until(int(final['tick'])))
    if hashes(lr)!=final:raise AssertionError('Pending snapshot continuation changed physics')
    # Organization serialization metadata may refresh its wrapper envelope.
    normalize=lambda x:{**x,'snapshot_metadata':{k:v for k,v in x['snapshot_metadata'].items() if not k.startswith('dee_thinking.organizational.')}}
    if normalize(operative(lr))!=normalize(op):raise AssertionError('Pending snapshot continuation changed operational state')
    report={'schema':'DEE45.neutral_differential.case.v1','case_id':case['id'],'backend':backend,'library':expected,
        'status':'PASS','engine':engine,'config_sha256':config_hash,'source_sha256':sha(__file__),'frames':frames,'calls':calls,
        'snapshot':snapshot,'final':final,'final_operative':op,'technical':{'passive':passive,'fork_parent_unchanged':True,
            'pending_snapshot_continuation_RAW_clock_tick_equal':True,'pending_snapshot_operative_equal':True},
        'elapsed_seconds':time.monotonic()-started}
    put(out/'RESULT.json',report);print(json.dumps({'case':case['id'],'backend':backend,'status':'PASS','seconds':report['elapsed_seconds']}),flush=True)


def suite(args):
    config=json.loads(args.config.read_text(encoding='utf-8'));out=args.out;out.mkdir(parents=True,exist_ok=True);rows=[]
    for case in config['cases']:
        for backend in config['backend_names']:
            target=out/(case['id']+'_'+backend);result=target/'RESULT.json'
            if result.exists():
                r=json.loads(result.read_text(encoding='utf-8'))
                if r['config_sha256']!=sha(args.config) or r['library']!=args.expected_version:raise ValueError('Existing result identity differs')
            else:
                argv=[sys.executable,'-I','-B',str(Path(__file__).resolve()),'case','--config',str(args.config.resolve()),
                    '--case-id',case['id'],'--backend',backend,'--out',str(target.resolve()),'--expected-version',args.expected_version]
                began=time.monotonic()
                try:
                    p=subprocess.run(argv,capture_output=True,text=True,timeout=180 if case.get('recipe')=='cascade2' else 60)
                    r={'status':'PASS' if p.returncode==0 and result.is_file() else 'FAIL','exit_code':p.returncode,'stdout':p.stdout,'stderr':p.stderr,
                        'elapsed_seconds':time.monotonic()-began}
                except subprocess.TimeoutExpired as e:r={'status':'TIMEOUT','elapsed_seconds':time.monotonic()-began,'error':str(e)}
                put(out/(target.name+'.PROCESS.json'),r)
            rows.append({'case_id':case['id'],'backend':backend,'status':r['status'],'result':target.name+'/RESULT.json'})
            put(out/'INDEX.json',{'schema':'DEE45.neutral_differential.index.v1','library':args.expected_version,'config_sha256':sha(args.config),'cases':rows})
    if any(r['status']!='PASS' for r in rows):raise SystemExit(1)


def compare(args):
    a=json.loads((args.before/'INDEX.json').read_text(encoding='utf-8'));b=json.loads((args.after/'INDEX.json').read_text(encoding='utf-8'))
    if a['config_sha256']!=b['config_sha256']:raise AssertionError('Configurations differ')
    cases=[]
    for left,right in zip(a['cases'],b['cases']):
        key=(left['case_id'],left['backend'])
        if key!=(right['case_id'],right['backend']):raise AssertionError('Case identity/order differs')
        x=json.loads((args.before/left['result']).read_text(encoding='utf-8'));y=json.loads((args.after/right['result']).read_text(encoding='utf-8'))
        checks=[]
        for fx,fy in zip(x['frames'],y['frames']):
            raw_equal=fx['raw']['sha256_uncompressed']==fy['raw']['sha256_uncompressed']
            clocks_equal=fx['clock']['sha256_uncompressed']==fy['clock']['sha256_uncompressed']
            operative_equal=fx['operative']==fy['operative']
            # The JSON paths/module versions are intentionally outside physical frames.
            checks.append({'tick':fx['tick'],'RAW_full_equal':raw_equal,'clock_full_equal':clocks_equal,
                           'operative_equal':operative_equal,'observations_equal':fx['observations']==fy['observations'],
                           'world_protocol_equal':fx.get('world')==fy.get('world')})
        passed=len(x['frames'])==len(y['frames']) and all(all(v for k,v in c.items() if k!='tick') for c in checks)
        cases.append({'case_id':key[0],'backend':key[1],'status':'PASS' if passed else 'FAIL','frontiers':checks,
                      'before_result_sha256':sha(args.before/left['result']),'after_result_sha256':sha(args.after/right['result'])})
    report={'schema':'DEE45.neutral_differential.comparison.v1','before':a['library'],'after':b['library'],'cases':cases,
            'case_backend_pairs':len(cases),'passed':sum(c['status']=='PASS' for c in cases),
            'scope':'Version and native binary identities differ; full physical uint64 arrays and operative fields are compared without lossy scalar RAW arithmetic.'}
    put(args.out,report)
    if len(a['cases'])!=len(b['cases']) or any(c['status']!='PASS' for c in cases):raise SystemExit(1)
    print(json.dumps({'compared':len(cases),'passed':report['passed']}))


def main():
    p=argparse.ArgumentParser();sub=p.add_subparsers(dest='mode',required=True)
    for mode in ('suite','case'):
        s=sub.add_parser(mode);s.add_argument('--config',type=Path,default=DEFAULT_CONFIG);s.add_argument('--out',type=Path,required=True)
        s.add_argument('--expected-version',required=True)
        if mode=='case':s.add_argument('--case-id',required=True);s.add_argument('--backend',required=True)
    s=sub.add_parser('compare');s.add_argument('--before',type=Path,required=True);s.add_argument('--after',type=Path,required=True);s.add_argument('--out',type=Path,required=True)
    args=p.parse_args()
    if args.mode=='suite':suite(args)
    elif args.mode=='compare':compare(args)
    else:
        config=json.loads(args.config.read_text(encoding='utf-8'));case=next(c for c in config['cases'] if c['id']==args.case_id)
        run_one(case,args.backend,args.out,args.expected_version,sha(args.config))

if __name__=='__main__':main()
