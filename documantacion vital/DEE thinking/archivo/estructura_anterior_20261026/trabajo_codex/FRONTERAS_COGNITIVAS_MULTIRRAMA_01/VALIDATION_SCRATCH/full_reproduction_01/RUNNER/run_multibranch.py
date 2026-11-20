"""Bounded/resumable experiments using the frozen installed native wheel."""
import argparse
import datetime as D
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
import traceback
import zipfile
sys.path.insert(0,str(Path(__file__).resolve().parent))
import dee_thinking as dt
from apparatus import OPTIONS, basal
from observations import *
from branches import BRANCH_SPECS, HANDLERS, initial_cases

WHEEL_SHA='9aa3a69bf1d542308912dbeee0b7c89199dafe295ce09533a2a394c8bc83c6db'
PRODUCT_SHA='9b45a8d0b05258dba3989bdf6e63ed3fd7d1c01f199673da06259d0aad946937'
KERNEL_SHA='fbd8190381ed76085f404e6578ff15fe185ab66cd48c67300d2abad61ddc7e31'
ZIP_NAME='DEE_thinking_3_0_0_FRONTERAS_COGNITIVAS_MULTIRRAMA_01_RESULTADOS.zip'

def utc(): return D.datetime.now(D.timezone.utc).isoformat()

class Case:
    def __init__(self,root,spec):
        self.root=Path(root);self.spec=spec
        self.directory=self.root/'COMBINATIONS'/spec['case'] if spec.get('combination') else self.root/'BRANCHES'/spec['branch']/spec['case']
        self.directory.mkdir(parents=True,exist_ok=True)
        self.checkpoints=[];self.runtimes={};self.begun=utc()
        dump(self.directory/'CASE_CONFIG.json',spec)
    def track(self,rt,count=True):
        if id(rt) not in self.runtimes:self.runtimes[id(rt)]=(rt,rt.current_tick,count)
        return rt
    def to(self,rt,t):
        if t<rt.current_tick:raise ValueError('backward progression forbidden')
        rt.run_until(t)
    def recipe(self,recipe):dump(self.directory/'APPARATUS.json',recipe)
    def data(self,name,value):dump(self.directory/(name+'.json'),value)
    def cp(self,rt,label):
        path=self.root/'CHECKPOINTS'/self.spec['branch']/self.spec['case']/(label+'.deetsnap')
        path.parent.mkdir(parents=True,exist_ok=True);rt.save_snapshot(str(path))
        self.checkpoints.append({'path':path.relative_to(self.root).as_posix(),'label':label,
                                  'tick':rt.current_tick,'sha256':sha(path),'size':path.stat().st_size})
    def trace(self,rt,sites,a,b,cadence=1):return trace(rt,sites,a,b,cadence)
    def effective_writes(self,rt,t0):
        return {'scheduled_calls_recorded_separately':True,
                'applied_event_batches':sum(r.status==dt.EventStatus.APPLIED and r.effective_tick is not None and r.effective_tick>=t0 for r in rt.receipts),
                'applied_physical_sites':sum(len(r.channels) for r in rt.receipts if r.status==dt.EventStatus.APPLIED and r.effective_tick is not None and r.effective_tick>=t0),
                'rejected_events':sum(str(r.status).lower().startswith('rejected') for r in rt.receipts)}
    def finish(self,result):
        result.update({'case_id':self.spec['case'],'branch':self.spec['branch'],'role':self.spec['role'],
                       'execution_status':'MEASURED','level':self.spec['level'],'started_utc':self.begun,
                       'finished_utc':utc(),'checkpoints':self.checkpoints,
                       'runtime_ticks_executed':sum(rt.current_tick-t for rt,t,count in self.runtimes.values() if count),
                       'instrumentation_scope':'local actual observations plus declared ballistic predictions, full RAW/uint64 clocks in checkpoints'})
        dump(self.directory/'MEASUREMENTS.json',result)
        return result

def append_ledger(root,item):
    with open(Path(root)/'CASE_LEDGER.jsonl','a',encoding='utf-8') as f:
        f.write(json.dumps({'utc':utc(),**item},ensure_ascii=False)+'\n');f.flush();os.fsync(f.fileno())

def init(root,product,wheel,start):
    root=Path(root);root.mkdir(parents=True,exist_ok=True)
    if (root/'CAMPAIGN_CONFIG.json').exists():return json.loads((root/'CAMPAIGN_CONFIG.json').read_text(encoding='utf-8'))
    assert sha(wheel)==WHEEL_SHA and sha(product)==PRODUCT_SHA
    assert dt.__version__=='3.0.0' and dt.kernel_identity()['kernel_version']==27
    dep=root/'SHARED_TOOLS';dep.mkdir(exist_ok=True)
    shutil.copy2(wheel,dep/Path(wheel).name)
    # Only selected reference sources, not the historical corpus or product ZIP.
    references=['README.md','docs/API_AND_SCOPE.md','source/src/kernel_v27.cpp',
                'source/include/dee_thinking/runtime.hpp','source/include/dee_thinking/integrated_protocols.hpp',
                'source/src/integrated_protocols.cpp','source/src/organization_catalog.cpp',
                'source/examples/composition_c6_later_query.cpp']
    extracted=[]
    with zipfile.ZipFile(product) as z:
        for wanted in references:
            candidates=[wanted] if wanted in z.namelist() else [name for name in z.namelist() if name.endswith('/'+wanted)]
            if len(candidates)!=1:raise ValueError(f'product reference not unique {wanted}: {candidates}')
            b=z.read(candidates[0]);dest=dep/'product_reference'/wanted
            dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(b)
            extracted.append({'member':candidates[0],'copied_as':dest.relative_to(root).as_posix(),'sha256':hashlib.sha256(b).hexdigest()})
    kernel=dep/'product_reference/source/src/kernel_v27.cpp';assert sha(kernel)==KERNEL_SHA
    startdt=D.datetime.fromisoformat(start.replace(' UTC','+00:00').replace(' ','T'))
    cfg={'campaign':'FRONTERAS COGNITIVAS NATIVAS DEE — MULTIRRAMA 01',
         'project':'DEE Universe','author':'Ivan Erick Tlaltecatl Morales','product':'DEE thinking 3.0.0',
         'kernel':'DEE v27','start_utc':startdt.isoformat(),'deadline_utc':(startdt+D.timedelta(minutes=90)).isoformat(),
         'backend':'LAZY','native_threads':1,'max_processes':2,'used_processes':1,
         'wheel_sha256':WHEEL_SHA,'product_zip_sha256':PRODUCT_SHA,'kernel_sha256':KERNEL_SHA,
         'build_info':dt.build_info(),'references':extracted,'branches':BRANCH_SPECS,
         'cases':initial_cases(),'selection_policy':'Visit one case in each branch before second pass. Finite numerical contrasts select confirmation, never cognitive verdict.',
         'budget':'90 minutes including preparation and packaging; close at <=80 minutes if runner still has queued cases',
         'sources':'Fixed pre-T0 native preparation or preregistered external inputs; declared diagnostics only in isolated forks',
         'host_boundary':'No response-adaptive stimulus, full-state input, decoder fitting, or repair',
         'sealed':False}
    dump(root/'CAMPAIGN_CONFIG.json',cfg);return cfg

def ordered(cases):
    queues={k:[s for s in cases if s['branch']==k] for k in BRANCH_SPECS};out=[]
    while any(queues.values()):
        for b in queues:
            if queues[b]:out.append(queues[b].pop(0))
    return out

def done(root,s):
    d=Path(root)/'BRANCHES'/s['branch']/s['case'];p=d/'MEASUREMENTS.json'
    if not p.exists():return False
    m=json.loads(p.read_text(encoding='utf-8'))
    return m.get('execution_status')=='MEASURED' and all((Path(root)/x['path']).is_file() and sha(Path(root)/x['path'])==x['sha256'] for x in m['checkpoints'])

def run(root,config,only=None,limit=None):
    count=0;cutoff=D.datetime.fromisoformat(config['deadline_utc'])-D.timedelta(minutes=10)
    for s in ordered(config['cases']):
        key=s['branch']+'/'+s['case']
        if s.get('skip_reason'):
            print('PRESERVED_ERROR',key,s['skip_reason'],flush=True);continue
        if only and key!=only:continue
        if done(root,s):print('SKIP_VERIFIED',key,flush=True);continue
        if D.datetime.now(D.timezone.utc)>=cutoff and not only:
            append_ledger(root,{'case':key,'status':'RESOURCE_BOUND','reason':'packaging reserve'});break
        print('RUNNING',key,flush=True);append_ledger(root,{'case':key,'status':'RUNNING','spec':s})
        ctx=Case(root,s);timer=time.perf_counter()
        try:
            r=ctx.finish(HANDLERS[s['kind']](ctx,s['spec']))
            append_ledger(root,{'case':key,'status':'MEASURED','elapsed_seconds':time.perf_counter()-timer,
                                'result_sha256':sha(ctx.directory/'MEASUREMENTS.json'),'level':s['level']})
            print('MEASURED',key,'ticks',r['runtime_ticks_executed'],flush=True)
        except Exception as e:
            detail={'type':type(e).__name__,'message':str(e),'traceback':traceback.format_exc(),'utc':utc()}
            ctx.data('TECHNICAL_ERROR',detail);append_ledger(root,{'case':key,'status':'TECHNICAL_ERROR','error':detail})
            print('TECHNICAL_ERROR',key,str(e),flush=True)
        count+=1
        if limit and count>=limit:break
    summarize(root,config)

def summarize(root,config):
    results=[json.loads(p.read_text(encoding='utf-8')) for p in sorted((Path(root)/'BRANCHES').glob('*/*/MEASUREMENTS.json'))]
    joint=[json.loads(p.read_text(encoding='utf-8')) for p in sorted((Path(root)/'COMBINATIONS').glob('*/MEASUREMENTS.json'))]
    by={b:[r for r in results if r['branch']==b] for b in BRANCH_SPECS}
    summaries={}
    for b,rows in by.items():
        measured=len(rows);vectors={json.dumps(r.get('phi'),sort_keys=True) for r in rows}
        summaries[b]={'cases_measured':measured,'levels_executed':sorted({r['level'] for r in rows}),
                       'response_signatures_across_declared_conditions':len(vectors),
                       'status':'MEASURED' if measured else 'PLANNED',
                       'coverage_pending':config.get('coverage_pending',{}).get(b),
                       'interpretation':'Counts describe frozen panel output only; not a cognitive verdict.'}
    dump(Path(root)/'RUN_SUMMARY.json',{'campaign':config['campaign'],'cut_utc':utc(),
        'total_runtime_ticks':sum(r['runtime_ticks_executed']+r.get('native_internal_tick_count',0) for r in results+joint),
        'tick_count_scope':'completed measured cases, diagnostic forks and declared H3 native internal horizons; technical checks and incomplete error attempts counted separately',
        'treatments':sum(r['role']=='treatment' for r in results),'controls':sum(r['role']=='control' for r in results),
        'calibrations':sum(r['role']=='calibration' for r in results),'cases_measured':len(results),
        'joint_cases_measured':len(joint),'joint_treatments':sum(r['role']=='treatment' for r in joint),
        'joint_controls':sum(r['role']=='control' for r in joint),
        'checkpoint_count':len(list((Path(root)/'CHECKPOINTS').rglob('*.deetsnap'))),
        'branch_reports':{b:f'BRANCHES/{b}/BRANCH_MEASUREMENTS.json' for b in BRANCH_SPECS},
        'branches':summaries,'parent_product_sha256':PRODUCT_SHA,'wheel_sha256':WHEEL_SHA,
        'kernel_sha256':KERNEL_SHA,'host_adaptive_writes':0,
        'host_adaptive_writes_basis':'Every mutable external laboratory operation is fixed by stored case specs and input/diagnostic logs; runner never chooses response content from observed outputs.',
        'pending_cases':[s['branch']+'/'+s['case'] for s in config['cases'] if not done(root,s) and not s.get('skip_reason')],
        'preserved_technical_errors':[{'case':s['branch']+'/'+s['case'],'reason':s['skip_reason']} for s in config['cases'] if s.get('skip_reason')],
        'combinations':config.get('combinations',[]),'completion_status':'MEASURED_CUT; no automatic scientific adjudication'})

def technical(root):
    w=basal();rt=w.runtime;reference=rt.fork();tracked=dt.TrackedSite();tracked.id='A';tracked.site=w.ports.a
    tr=dt.PassiveTracker([tracked],16)
    for _ in range(5):tr.capture(rt);rt.advance();reference.advance()
    obs_equal=state_equal(rt,reference)
    p=Path(root)/'CHECKPOINTS/TECHNICAL/ROUNDTRIP.deetsnap';p.parent.mkdir(parents=True,exist_ok=True);rt.save_snapshot(str(p))
    loaded=dt.Runtime.load_snapshot(str(p));load_eq=state_equal(rt,loaded)
    rt.advance(7);loaded.advance(7);continued=state_equal(rt,loaded)
    a=basal().runtime;b=a.fork();b.execution_options=dt.TickOptions(dt.Backend.DENSE_SEQUENTIAL,1)
    for _ in range(10):a.advance();b.advance()
    denseeq=state_equal(a,b)
    snapshotchecks=[]
    for branch in BRANCH_SPECS:
        picks=list((Path(root)/'CHECKPOINTS'/branch).glob('*/FINAL.deetsnap'))
        if not picks:picks=list((Path(root)/'CHECKPOINTS'/branch).glob('*/*.deetsnap'))
        if picks:
            z=dt.Runtime.load_snapshot(str(picks[0]));f=z.fork();z.advance(2);f.advance(2)
            snapshotchecks.append({'path':picks[0].relative_to(root).as_posix(),'sha256':sha(picks[0]),'restored_tick':z.current_tick-2,'future_exact':state_equal(z,f)})
    checks={'passive_observer_exact':obs_equal,'roundtrip_exact':load_eq,'save_load_future_exact':continued,
            'lazy_dense_exact':denseeq,'selected_snapshots':snapshotchecks,'tracker_frames':len(tr.frames),
            'snapshot_uint64_raw_clock':True,'public_API_regression_delta':w.observe().delta}
    dump(Path(root)/'SHARED_TOOLS/TECHNICAL_CHECKS.json',checks)
    assert obs_equal and load_eq and continued and denseeq and all(x['future_exact'] for x in snapshotchecks)
    return checks

def package(root,output):
    root=Path(root);output=Path(output)
    cfg=json.loads((root/'CAMPAIGN_CONFIG.json').read_text(encoding='utf-8'))
    if not cfg.get('sealed'):
        cfg['sealed']=True;cfg['seal_utc']=utc();dump(root/'CAMPAIGN_CONFIG.json',cfg)
    summarize(root,cfg)
    if not (root/'SHARED_TOOLS/TECHNICAL_CHECKS.json').exists():technical(root)
    files=[p for p in root.rglob('*') if p.is_file() and '__pycache__' not in p.parts
           and not any(x in p.parts for x in ('.venv','venv','b30venv','.git'))
           and 'VALIDATION_SCRATCH' not in p.parts
           and p.name not in ('MANIFEST.json','HASHES.sha256','PACKAGE_VERIFICATION.json')
           and not p.name.endswith(('.partial','.zip','.log'))]
    hashes={p.relative_to(root).as_posix():sha(p) for p in files}
    dump(root/'MANIFEST.json',{'schema':'dee-native-multibranch-cut-v1','campaign':cfg['campaign'],
                              'seal_utc':cfg['seal_utc'],'files':[{'path':k,'size':(root/k).stat().st_size,'sha256':v} for k,v in sorted(hashes.items())]})
    hashes['MANIFEST.json']=sha(root/'MANIFEST.json')
    (root/'HASHES.sha256').write_text(''.join(f'{v}  {k}\n' for k,v in sorted(hashes.items())),encoding='utf-8')
    output.parent.mkdir(parents=True,exist_ok=True)
    tmp=root/'campaign_delivery.partial.zip'
    with zipfile.ZipFile(tmp,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for k in sorted([*hashes,'HASHES.sha256']):z.write(root/k,k)
    result=verify(tmp)
    if output.exists():
        archive_parent=root/'SHARED_TOOLS'/('previous_cut_'+sha(output)+'.zip')
        shutil.copy2(output,archive_parent)  # outside the sealed manifest; not a nested published ZIP
    os.replace(tmp,output)
    result.update({'published':str(output),'sha256':sha(output),'size':output.stat().st_size})
    dump(root/'PACKAGE_VERIFICATION.json',result);print(json.dumps(result,ensure_ascii=False,indent=2),flush=True)

def verify(path):
    with zipfile.ZipFile(path) as z:
        bad=z.testzip();assert bad is None
        hashes=z.read('HASHES.sha256').decode('utf-8').splitlines()
        for line in hashes:
            digest,name=line.split('  ',1);assert hashlib.sha256(z.read(name)).hexdigest()==digest,name
        m=json.loads(z.read('MANIFEST.json'))
        for entry in m['files']:
            data=z.read(entry['path']);assert len(data)==entry['size']
            assert hashlib.sha256(data).hexdigest()==entry['sha256']
        for essential in ('RUNNER/run_multibranch.py','RUNNER/apparatus.py','RUNNER/observations.py','RUNNER/branches.py',
                          'CAMPAIGN_CONFIG.json','RUN_SUMMARY.json','CASE_LEDGER.jsonl','README_REPRODUCCION.md'):
            assert essential in z.namelist(),essential
        assert len([x for x in z.namelist() if x.startswith('BRANCHES/L')])>0
    return {'crc_verified':True,'hashes_verified':True,'manifest_verified':True,'members':len(z.namelist()),'sha256':sha(path)}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1])
    ap.add_argument('--mode',choices=['init','run','resume','case','reproduce','technical','package','verify'],default='run')
    ap.add_argument('--product',type=Path);ap.add_argument('--wheel',type=Path);ap.add_argument('--start-utc',default=utc())
    ap.add_argument('--case');ap.add_argument('--limit',type=int);ap.add_argument('--output',type=Path)
    ap.add_argument('--replica-root',type=Path)
    args=ap.parse_args()
    if args.mode=='verify':print(json.dumps(verify(args.output),indent=2));return
    if args.mode=='init':init(args.root,args.product,args.wheel,args.start_utc);return
    config=json.loads((args.root/'CAMPAIGN_CONFIG.json').read_text(encoding='utf-8'))
    if args.mode=='reproduce':
        if not args.replica_root:raise ValueError('reproduce requires a new --replica-root')
        from reproduce_cut import reproduce
        reproduce(args.root,args.replica_root,config);return
    if args.replica_root:
        if args.mode!='case' or not args.case:raise ValueError('replica-root requires --mode case --case BRANCH/CASE')
        selected=[s for s in config['cases'] if s['branch']+'/'+s['case']==args.case]
        if len(selected)!=1:raise ValueError('case not unique')
        if args.replica_root.exists():raise ValueError('replica root already exists; choose a new isolated directory')
        args.replica_root.mkdir(parents=True);config=dict(config);config['cases']=selected;config['sealed']=False
        config['reproduction_parent_root']=str(args.root);dump(args.replica_root/'CAMPAIGN_CONFIG.json',config)
        args.root=args.replica_root
    if args.mode in ('run','resume','case'):
        if config.get('sealed') and args.mode!='case':raise RuntimeError('Sealed scientific cut: use a fresh isolated --root with copied config for replication')
        run(args.root,config,args.case,args.limit)
    elif args.mode=='technical':print(json.dumps(technical(args.root),indent=2))
    else:package(args.root,args.output)

if __name__=='__main__':main()
