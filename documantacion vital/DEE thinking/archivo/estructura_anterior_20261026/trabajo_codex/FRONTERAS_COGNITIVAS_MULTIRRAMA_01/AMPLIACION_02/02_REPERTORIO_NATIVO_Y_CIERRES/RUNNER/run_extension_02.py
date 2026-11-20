"""Finite two-process campaign, replay and atomic append without parent mutation."""
import argparse,datetime as D,hashlib,json,os,shutil,sys,time,traceback,zipfile
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor
sys.path.insert(0,str(Path(__file__).resolve().parent))
if '--dependency-root' in sys.argv:
    sys.path.insert(0,str(Path(sys.argv[sys.argv.index('--dependency-root')+1]).resolve()))
import dee_thinking as dt
from observations import dump,sha,receipt,full_hash,state_equal

PARENT_SHA='12bd795fe35e1ebda884c440bd9b2a0f7677ed6ac0594393e55093146e626e8e'
WHEEL_SHA='9aa3a69bf1d542308912dbeee0b7c89199dafe295ce09533a2a394c8bc83c6db'
SECTION='02_REPERTORIO_NATIVO_Y_CIERRES'
ZIP_NAME='DEE_thinking_3_0_0_FRONTERAS_COGNITIVAS_MULTIRRAMA_01_RESULTADOS.zip'
def utc():return D.datetime.now(D.timezone.utc).isoformat()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def ledger(root,obj):
    with open(Path(root)/'CASE_LEDGER.jsonl','a',encoding='utf-8') as f:
        f.write(json.dumps({'utc':utc(),**obj},ensure_ascii=False)+'\n');f.flush();os.fsync(f.fileno())

class Context:
    def __init__(self,root,spec,package_root=None):
        self.root=Path(root).resolve();self.spec=spec;self.package_root=Path(package_root).resolve() if package_root else None
        self.directory=self.root/('COMBINATIONS' if spec.get('combination') else 'BRANCHES')/spec['front']/spec['id']
        self.directory.mkdir(parents=True,exist_ok=True);self.started=utc()
        attempts=[int(p.name.split('_')[-1]) for p in self.directory.glob('attempt_*') if p.is_dir()]
        self.attempt=max(attempts,default=0)+1;self.attempt_dir=self.directory/f'attempt_{self.attempt:03d}'
        self.attempt_dir.mkdir();self.runtimes={};self.checkpoints=[];self.inputs=[];self.edits=[];self.parent_sources=[]
        dump(self.attempt_dir/'CASE_CONFIG.json',spec)
        self.config=read(self.root/'EXPERIMENT_CONFIG.json')
    def track(self,rt):
        if id(rt) not in self.runtimes:self.runtimes[id(rt)]=(rt,rt.current_tick)
        return rt
    def to(self,rt,t):
        if D.datetime.now(D.timezone.utc)>=D.datetime.fromisoformat(self.config['deadline_utc']):raise TimeoutError('global finite deadline')
        if t<rt.current_tick:raise ValueError('backwards progression')
        while rt.current_tick<t:rt.run_until(min(t,rt.current_tick+32))
    def cp(self,rt,label):
        p=self.root/'CHECKPOINTS'/self.spec['front']/self.spec['id']/f'attempt_{self.attempt:03d}'/(label+'.deetsnap')
        p.parent.mkdir(parents=True,exist_ok=True);rt.save_snapshot(str(p))
        item={'path':p.relative_to(self.root).as_posix(),'sha256':sha(p),'tick':rt.current_tick,'label':label,'size':p.stat().st_size}
        self.checkpoints.append(item);return item
    def data(self,name,value):dump(self.attempt_dir/(name+'.json'),value)
    def recipe(self,obj):self.data('APPARATUS',obj)
    def parent_bytes(self,name):
        entry=next(x for x in read(self.root/'PARENT_MEMBERS.json')['members'] if x['name']==name)
        if self.package_root is not None:
            p=self.package_root/name;b=p.read_bytes()
        else:
            sealed=self.root.parent/'PARENT_SEALED.zip'
            with zipfile.ZipFile(sealed) as z:b=z.read(name)
        assert hashlib.sha256(b).hexdigest()==entry['sha256'],name
        self.parent_sources.append({'member':name,'sha256':entry['sha256']});return b
    def parent_json(self,name):return json.loads(self.parent_bytes(name).decode('utf-8'))
    def parent_runtime(self,name):
        # Native loader takes a path; cache sits outside published section and is not a second evidence copy.
        data=self.parent_bytes(name);cache=self.root.parent/'SOURCE_CACHE';cache.mkdir(exist_ok=True)
        p=cache/(hashlib.sha256(data).hexdigest()+'.deetsnap')
        if not p.exists():p.write_bytes(data)
        return self.track(dt.Runtime.load_snapshot(str(p)))
    def cut_runtime(self,front,case,label='MAIN_FINAL'):
        source_root=self.root
        p=source_root/'BRANCHES'/front/case/'MEASUREMENTS.json'
        if not p.exists() and self.package_root is not None:
            source_root=self.package_root/SECTION;p=source_root/'BRANCHES'/front/case/'MEASUREMENTS.json'
        m=read(p);entry=next(x for x in m['checkpoints'] if x['label']==label)
        snap=source_root/entry['path'];assert sha(snap)==entry['sha256']
        self.parent_sources.append({'extension_case':front+'/'+case,'label':label,'sha256':entry['sha256']})
        return self.track(dt.Runtime.load_snapshot(str(snap)))
    def edit(self,rt,q,raw=None,clock=None,label='diagnostic',modality='DIAGNOSTIC'):
        from apparatus import edited
        f,item=edited(rt,q,raw,clock,label);item['modality']=modality;self.edits.append(item);return self.track(f)
    def schedule(self,rt,name,tick,load,kind='experience'):
        from apparatus import schedule
        self.track(rt);r=schedule(rt,self.inputs,name,tick,load,kind)
        self.inputs[-1]['runtime_ref']=list(self.runtimes).index(id(rt));self.inputs[-1]['payload']=load
        return r
    def finish(self,m):
        receipts=[]
        for k,(rt,t0) in enumerate(self.runtimes.values()):
            receipts.append({'runtime_ref':k,'initial_tick':t0,'tick':rt.current_tick,'events':[receipt(r) for r in rt.receipts]})
        self.data('OPERATIONS',{'external_calls':self.inputs,'research_edits':self.edits,
                  'receipts_by_runtime':receipts,'note':'Fork receipts can share a prefix; never sum inherited receipts as new calls.'})
        m.update({'worker_pid':os.getpid(),'runtime_count':len(self.runtimes),'case_id':self.spec['id'],'front':self.spec['front'],'work_type':self.spec['work_type'],
                  'role':self.spec['role'],'level':self.spec.get('level','D'),'modality':self.spec['modality'],
                  'execution_status':m.get('execution_status','MEASURED'),'started_utc':self.started,'finished_utc':utc(),
                  'checkpoints':self.checkpoints,'runtime_ticks_executed':sum(rt.current_tick-t for rt,t in self.runtimes.values()),
                  'external_calls':self.inputs,'diagnostic_writes':self.edits,'parent_evidence':self.parent_sources,
                  'attempt':self.attempt,'state_buffers_preserved':'RAW and complete uint64 clock; Runtime channels/queues/receipts in snapshots'})
        dump(self.attempt_dir/'MEASUREMENTS.json',m);dump(self.directory/'MEASUREMENTS.json',m)
        return m

def done(root,s):
    p=Path(root)/('COMBINATIONS' if s.get('combination') else 'BRANCHES')/s['front']/s['id']/'MEASUREMENTS.json'
    if not p.exists():return False
    m=read(p)
    return m.get('execution_status') in ('MEASURED','NO_CONTRAST_IN_PANEL','INCONCLUSIVE','SOURCE_NOT_RECOVERED','INSTRUMENTATION_BLOCKED') and all((Path(root)/x['path']).is_file() and sha(Path(root)/x['path'])==x['sha256'] for x in m['checkpoints'])

def worker(root,s,package_root):
    from frontiers import HANDLERS
    ctx=Context(root,s,package_root);timer=time.perf_counter()
    try:
        m=ctx.finish(HANDLERS[s['handler']](ctx,s['parameters']))
        return {'case':s['front']+'/'+s['id'],'status':m['execution_status'],'elapsed_seconds':time.perf_counter()-timer,
                'level':s.get('level','D'),'measurement_sha256':sha(ctx.directory/'MEASUREMENTS.json')}
    except Exception as ex:
        error={'class':type(ex).__name__,'message':str(ex),'traceback':traceback.format_exc(),'utc':utc()}
        ctx.data('TECHNICAL_ERROR',error)
        return {'case':s['front']+'/'+s['id'],'status':'TECHNICAL_ERROR','error':error,'attempt':ctx.attempt}

def ordered(cases):
    queues={f'P{k:02}':[s for s in cases if s['front']==f'P{k:02}'] for k in range(1,15)}
    out=[]
    while any(queues.values()):
        for q in queues.values():
            if q:out.append(q.pop(0))
    return out+[s for s in cases if s.get('combination')]

def run(root,config,package_root=None,only=None,limit=None):
    pending=[]
    for s in ordered(config['cases']):
        if only and s['front']+'/'+s['id']!=only:continue
        if done(root,s):print('SKIP_VERIFIED',s['front'],s['id'],flush=True);continue
        pending.append(s)
    if limit:pending=pending[:limit]
    cutoff=D.datetime.fromisoformat(config['deadline_utc'])-D.timedelta(minutes=20)
    # Bounded two-process batches; every Runtime remains owned by exactly one worker.
    with ProcessPoolExecutor(max_workers=2) as pool:
        for start in range(0,len(pending),2):
            if D.datetime.now(D.timezone.utc)>=cutoff:
                ledger(root,{'status':'RESOURCE_BOUND','reason':'20 minute closure reserve','pending':len(pending)-start});break
            batch=pending[start:start+2];jobs=[]
            for s in batch:
                ledger(root,{'case':s['front']+'/'+s['id'],'status':'RUNNING','spec':s})
                print('RUNNING',s['front'],s['id'],flush=True);jobs.append(pool.submit(worker,str(root),s,str(package_root) if package_root else None))
            for job in jobs:
                result=job.result();ledger(root,result);print(result['status'],result['case'],result.get('elapsed_seconds'),flush=True)
    summarize(root,config)

def summarize(root,config):
    root=Path(root);files=list((root/'BRANCHES').glob('*/*/MEASUREMENTS.json'))+list((root/'COMBINATIONS').glob('*/*/MEASUREMENTS.json'))
    all_values=[read(p) for p in files]
    values=[x for x in all_values if x.get('level')!='technical']
    summary={'campaign':config['campaign'],'parent_zip_sha256':PARENT_SHA,'updated_utc':utc(),
             'historical_cases':100,'historical_fronts':9,'new_unique_cases':len(values),
             'runtime_ticks_new_completed_cases':sum(x['runtime_ticks_executed'] for x in values),
             'case_types':{t:sum(x['work_type']==t for x in values) for t in ('A','B','C')},
             'roles':{r:sum(x['role']==r for x in values) for r in ('treatment','control','reference','reread','diagnostic')},
             'fronts':{f'P{k:02}':{'cases':sum(x['front']==f'P{k:02}' for x in values),
                                  'levels':sorted({x['level'] for x in values if x['front']==f'P{k:02}'}),
                                  'statuses':sorted({x['execution_status'] for x in values if x['front']==f'P{k:02}'})} for k in range(1,15)},
             'checkpoint_count':len(list((root/'CHECKPOINTS').rglob('*.deetsnap'))),
             'pending_cases':[s['front']+'/'+s['id'] for s in config['cases'] if not done(root,s)],
             'completion_status':'Measured finite cut; no cognitive adjudication',
             'used_native_threads':1,'native_worker_processes':2,'technical_reproductions':sum(x.get('level')=='technical' for x in all_values),
             'technical_ticks_separate':sum(x['runtime_ticks_executed'] for x in all_values if x.get('level')=='technical')}
    dump(root/'RUN_SUMMARY.json',summary);return summary

def initialize(root):
    from frontiers import FRONT_SPECS,initial_cases
    root=Path(root)
    path=root/'EXPERIMENT_CONFIG.json'
    if path.exists():return read(path)
    cfg={'campaign':'MULTIRRAMA 01 — AMPLIACIÓN 02','author':'Ivan Erick Tlaltecatl Morales','project':'DEE Universe',
         'start_utc':'2026-10-09T00:24:45+00:00','deadline_utc':'2026-10-09T04:24:45+00:00',
         'kernel':'DEE v27 frozen','library':'DEE thinking 3.0.0 frozen','parent_sha256':PARENT_SHA,
         'wheel_sha256':WHEEL_SHA,'backend':'LAZY','threads_per_worker':1,'worker_processes':2,
         'fronts':FRONT_SPECS,'cases':initial_cases(),'sealed':False,
         'discovery_limits':{'architectural_families_per_front':2,'configurations_per_front':6,'reserve_realizations':2,'extensions':1,'open_candidates':4},
         'selection_policy':'Visit all fronts before deepening. Contrasts select finite queue budget, never cognitive labels.'}
    dump(path,cfg);return cfg

def verify(path):
    with zipfile.ZipFile(path) as z:
        assert z.testzip() is None
        parent=json.loads(z.read(SECTION+'/PARENT_MEMBERS.json'))
        for entry in parent['members']:
            b=z.read(entry['name']);assert len(b)==entry['size'] and hashlib.sha256(b).hexdigest()==entry['sha256'],entry['name']
        lines=z.read(SECTION+'/HASHES.sha256').decode('utf-8').splitlines()
        for line in lines:
            h,name=line.split('  ',1);assert hashlib.sha256(z.read(SECTION+'/'+name)).hexdigest()==h,name
        assert all(n in {e['name'] for e in parent['members']} or n.startswith(SECTION+'/') for n in z.namelist())
        assert SECTION+'/RUNNER/run_extension_02.py' in z.namelist()
        return {'crc':True,'new_hashes':True,'all_parent_members_byte_exact':True,'parent_members':len(parent['members']),
                'new_hashed_members':len(lines),'members':len(z.namelist()),'sha256':sha(path)}

def reproduce(root,case,replica_out,package_root):
    """Read a sealed case; write only a new, explicitly technical replica."""
    root=Path(root).resolve();target=Path(replica_out).resolve()
    if target==root or root in target.parents:raise ValueError('Replica must be outside the evidence section')
    if target.exists():raise FileExistsError('Replica destination already exists; no evidence overwritten')
    cfg=read(root/'EXPERIMENT_CONFIG.json')
    spec=next(s for s in cfg['cases'] if s['front']+'/'+s['id']==case)
    target.mkdir(parents=True)
    cfg={**cfg,'sealed':False,'cases':[spec],'deadline_utc':(D.datetime.now(D.timezone.utc)+D.timedelta(minutes=15)).isoformat(),
         'technical_replica_of':case,'source_config_sha256':sha(root/'EXPERIMENT_CONFIG.json')}
    dump(target/'EXPERIMENT_CONFIG.json',cfg)
    shutil.copy2(root/'PARENT_MEMBERS.json',target/'PARENT_MEMBERS.json')
    if package_root is None:raise ValueError('Reproduction requires --package-root, containing the extracted inherited members')
    result=worker(str(target),spec,str(Path(package_root).resolve()))
    assert result['status'] not in ('TECHNICAL_ERROR','RESOURCE_BOUND'),result
    original=read(root/'BRANCHES'/spec['front']/spec['id']/'MEASUREMENTS.json')
    copy=read(target/'BRANCHES'/spec['front']/spec['id']/'MEASUREMENTS.json')
    original_labels={x['label']:x for x in original['checkpoints']}
    comparisons=[]
    for snap in copy['checkpoints']:
        ref=original_labels[snap['label']]
        left=dt.Runtime.load_snapshot(str(root/ref['path']))
        right=dt.Runtime.load_snapshot(str(target/snap['path']))
        equal=state_equal(left,right)
        comparisons.append({'label':snap['label'],'tick':right.current_tick,'RAW_clock_tick_equal':equal,
                            'source_sha256':ref['sha256'],'replica_sha256':snap['sha256']})
        assert equal,snap['label']
    # Early observations lack the later-added payload/runtime_ref metadata.
    # Require equality of every actually recorded field; never silently ignore a conflicting field.
    source_calls=original['external_calls'];replica_calls=copy['external_calls']
    assert len(source_calls)==len(replica_calls),'Number of physical calls differs'
    for left,right in zip(source_calls,replica_calls):
        assert all(k in right and right[k]==v for k,v in left.items()),'Recorded physical input field differs'
    if 'query_order' in original:assert copy['query_order']==original['query_order'],'Physical query payload order differs'
    original_ops=read(root/'BRANCHES'/spec['front']/spec['id']/f"attempt_{original['attempt']:03d}"/'OPERATIONS.json')
    replica_ops=read(target/'BRANCHES'/spec['front']/spec['id']/f"attempt_{copy['attempt']:03d}"/'OPERATIONS.json')
    left_receipts=[{'tick':r['tick'],'events':r['events']} for r in original_ops['receipts_by_runtime']]
    right_receipts=[{'tick':r['tick'],'events':r['events']} for r in replica_ops['receipts_by_runtime']]
    assert left_receipts==right_receipts,'Applied/rejected receipts differ'
    assert copy['diagnostic_writes']==original['diagnostic_writes'],'Diagnostic interventions differ'
    report={'case':case,'technical_replica':True,'new_scientific_case':False,'comparisons':comparisons,
            'recorded_input_fields_equal':True,'receipts_by_runtime_equal':True,'diagnostic_writes_equal':True,
            'legacy_calls_without_explicit_payload':sum('payload' not in r for r in source_calls),
            'legacy_calls_without_runtime_ref':sum('runtime_ref' not in r for r in source_calls),
            'protocol_parameters_frozen':spec['parameters'],
            'kernel_identity':dt.kernel_identity(),'runtime_module':dt.__file__,
            'native_module':__import__('dee_thinking._native',fromlist=['__file__']).__file__,
            'completed_utc':utc(),'replica_directory':str(target)}
    dump(target/'REPRODUCTION_CHECK.json',report);print(json.dumps(report,indent=2));return report

def package(root,output,publish=True):
    root=Path(root).resolve();parent=root.parent/'PARENT_SEALED.zip';assert sha(parent)==PARENT_SHA
    cfg=read(root/'EXPERIMENT_CONFIG.json')
    if not cfg.get('sealed'):cfg['sealed']=True;cfg['sealed_utc']=utc();dump(root/'EXPERIMENT_CONFIG.json',cfg)
    summarize(root,cfg)
    files=[p for p in root.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.name!='HASHES.sha256' and not p.name.endswith(('.partial','.zip'))]
    hashes={p.relative_to(root).as_posix():sha(p) for p in files}
    (root/'HASHES.sha256').write_text(''.join(f'{h}  {n}\n' for n,h in sorted(hashes.items())),encoding='utf-8')
    temp=root.parent/'extension_delivery.partial.zip'
    with zipfile.ZipFile(parent) as source,zipfile.ZipFile(temp,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as dest:
        for info in source.infolist():dest.writestr(info,source.read(info.filename))
        for rel in sorted([*hashes,'HASHES.sha256']):dest.write(root/rel,SECTION+'/'+rel)
    checks=verify(temp)
    if not publish:
        checks.update({'temporary_archive':str(temp),'published':False,'verified_utc':utc()})
        dump(root.parent/'ASSEMBLY_VERIFICATION.json',checks);print(json.dumps(checks,indent=2),flush=True);return
    output=Path(output).resolve()
    if output.exists() and sha(output)!=PARENT_SHA:
        if sha(output)==checks['sha256']:
            checks.update({'published':str(output),'idempotent_existing_archive':True})
            print(json.dumps(checks,indent=2),flush=True);return
        raise RuntimeError('Official destination differs from the verified parent; publication refused without destroying either cut')
    os.replace(temp,output)
    checks.update({'published':str(output),'sha256':sha(output),'published_utc':utc(),'bytes':output.stat().st_size})
    dump(root.parent/'PUBLICATION_VERIFICATION.json',checks);print(json.dumps(checks,indent=2),flush=True)

def main():
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1]);p.add_argument('--package-root',type=Path)
    p.add_argument('--mode',choices=['init','plan','deepen','run','resume','case','reproduce','summary','assemble','package','verify'],default='run');p.add_argument('--case');p.add_argument('--limit',type=int);p.add_argument('--output',type=Path)
    p.add_argument('--replica-out',type=Path);p.add_argument('--dependency-root',type=Path)
    a=p.parse_args();root=a.root.resolve()
    if a.mode=='verify':print(json.dumps(verify(a.output),indent=2));return
    if a.mode=='reproduce':reproduce(root,a.case,a.replica_out,a.package_root);return
    cfg=initialize(root)
    if a.mode=='init':return
    if a.mode=='deepen':
        from frontiers import followup_cases
        additions=followup_cases(root);existing={s['front']+'/'+s['id'] for s in cfg['cases']}
        additions=[s for s in additions if s['front']+'/'+s['id'] not in existing]
        cfg.setdefault('frozen_followup_batches',[]).append({'utc':utc(),'cases':[s['front']+'/'+s['id'] for s in additions],
            'config_before_sha256':sha(root/'EXPERIMENT_CONFIG.json'),'selection':'Exact measured contrasts; configurations frozen before reserved realizations. Discovery variants are explicitly D.'})
        cfg['cases'].extend(additions);dump(root/'EXPERIMENT_CONFIG.json',cfg)
        print('Added',len(additions),'finite cases');return
    if a.mode=='plan':
        from frontiers import initial_cases
        previous=cfg['cases'];cfg['cases']=initial_cases()
        dump(root/'ANALYSIS/PLAN_ADAPTATION.json',{'utc':utc(),'previous_config_sha256':sha(root/'EXPERIMENT_CONFIG.json'),
            'removed_duplicate_or_deferred_cases':[s['front']+'/'+s['id'] for s in previous if s not in cfg['cases']],
            'reason':'Reuse exact P03 histories for P07; defer P13 probes to forks of completed P14 endpoints, avoiding duplicate evidence.'})
        dump(root/'EXPERIMENT_CONFIG.json',cfg);return
    if a.mode in ('run','resume','case'):
        if cfg.get('sealed'):raise RuntimeError('Sealed cut; use a new replica directory/config')
        run(root,cfg,a.package_root,a.case,a.limit)
    elif a.mode=='summary':print(json.dumps(summarize(root,cfg),indent=2))
    else:package(root,a.output,publish=a.mode!='assemble')
if __name__=='__main__':main()
