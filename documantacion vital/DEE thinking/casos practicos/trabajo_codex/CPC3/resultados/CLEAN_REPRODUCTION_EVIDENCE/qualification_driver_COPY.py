"""Bounded independent CPC3 reproduction and dependency audit.

No publication or deletion. The original campaign budget remains authoritative.
The generated clean venv audit observes Python opens/imports/subprocesses and
explicit native path arguments; it does not pretend to be a kernel-level OS
filesystem monitor. Native answers are produced by actual evolution.
"""
import argparse
import atexit
from datetime import datetime,timezone
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import runpy
import shutil
import sys
import tempfile
import time
import zipfile

WHEEL='dee_thinking-3.5.0-cp313-cp313-win_amd64.whl'
WHEEL_SHA='721d4ad1610d6efc7e7101b49b9d68c6925efdcf596361aca09aabd0e315bcaa'
NATIVE_SHA='3b864bf8c5d4cee6940e3bb99bb647443548851def72df3c3b60ed69b4308585'
EXCLUDED={'staging','__pycache__','.venv','venv','.git','ACTIVE','sesion_usuario'}
AUDIT=None


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_json(path,value):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True);tmp=path.with_name(path.name+'.tmp')
    tmp.write_text(json.dumps(value,indent=2,ensure_ascii=False),encoding='utf-8');os.replace(tmp,path)


class ForbiddenDependency(PermissionError):pass


class FileAudit:
    def __init__(self,configuration):
        self.configuration=configuration;self.phase='SELF_TEST';self.open_count=0;self.import_count=0
        self.violations=[];self.native_paths=[];self.tests=[];self.processes=[]
        self.installation_verified=False
        self.forbidden=[self.key(p) for p in configuration['forbidden_paths']]
        self.folder=Path(configuration['audit_directory']);self.folder.mkdir(parents=True,exist_ok=True)
        self.events_path=self.folder/(str(os.getpid())+'.events.jsonl')
        self.fd=os.open(self.events_path,os.O_CREAT|os.O_WRONLY|os.O_APPEND,0o600)
        sys.addaudithook(self.callback);atexit.register(self.finish)

    @staticmethod
    def key(value):
        if isinstance(value,int):return None
        try:value=os.fsdecode(value)
        except TypeError:return None
        if not value or value.startswith('<'):return None
        try:return str(Path(value).resolve()).replace('\\?\\','').replace('\\','/').casefold().rstrip('/')
        except (OSError,ValueError):return None

    def denied(self,value):
        key=self.key(value)
        return key and any(key==p or key.startswith(p+'/') for p in self.forbidden)

    def log(self,item):
        os.write(self.fd,(json.dumps({'pid':os.getpid(),'phase':self.phase,**item},ensure_ascii=True)+'\n').encode())

    def check(self,path,operation):
        if self.denied(path):
            v={'operation':operation,'path':os.fsdecode(path),'phase':self.phase};self.violations.append(v)
            self.log({'event':'FORBIDDEN_DEPENDENCY',**v});raise ForbiddenDependency('CPC3_DEPENDENCY_FIREWALL: '+str(path))

    def callback(self,event,args):
        if event=='open':
            path=args[0];self.check(path,'open');self.open_count+=1
            if not isinstance(path,int):self.log({'event':'open','path':os.fsdecode(path)})
        elif event=='import':
            self.import_count+=1
            if len(args)>1 and args[1]:self.check(args[1],'import')
        elif event=='subprocess.Popen':
            executable,args0,cwd=args[:3]
            self.check(executable,'subprocess executable')
            if cwd:self.check(cwd,'subprocess cwd')
            for value in args0 if isinstance(args0,(list,tuple)) else [args0]:
                if isinstance(value,(str,bytes)) and Path(os.fsdecode(value)).is_absolute():self.check(value,'subprocess argument')
            self.processes.append({'executable':str(executable),'argv':list(args0) if isinstance(args0,(tuple,list)) else str(args0),'cwd':str(cwd)})

    def self_test(self):
        # Rejected BEFORE an old file is opened. Deliberate self-tests are not
        # confused with dependencies attempted by the reproduction itself.
        for path in self.configuration['five_old_paths']:
            before=len(self.violations)
            try:
                with open(path,'rb'):pass
            except ForbiddenDependency:pass
            else:raise AssertionError('Dependency firewall did not reject '+path)
            assert len(self.violations)==before+1
            self.tests.append({'path':path,'rejected_before_open':True})
        self.phase='RUN'

    def native_path(self,path,operation):
        self.check(path,'explicit native '+operation)
        self.native_paths.append({'path':str(Path(path).resolve()),'operation':operation})

    def finish(self):
        try:
            self.phase='FINALIZE';modules=[];bad=[]
            for name,module in sorted(list(sys.modules.items())):
                path=getattr(module,'__file__',None)
                if path:
                    item={'module':name,'path':str(path)};modules.append(item)
                    if self.denied(path):bad.append(item)
            actual=[v for v in self.violations if v['phase']=='RUN']
            report={'pid':os.getpid(),'python':sys.executable,'cwd':str(Path.cwd()),
                    'five_path_firewall_tests':self.tests,'open_events':self.open_count,'import_events':self.import_count,
                    'actual_forbidden_access_count':len(actual),'actual_forbidden_accesses':actual,
                    'forbidden_module_origins':bad,'module_origins':modules,'native_path_arguments':self.native_paths,
                    'child_processes':self.processes,'completed_at_exit':True,'installation_verified':self.installation_verified,
                    'coverage':'Python audit open/import/subprocess + explicit native path arguments. Not an OS-wide C++ syscall trace.'}
            write_json(self.folder/(str(os.getpid())+'.summary.json'),report)
        finally:self.phase='POST_FINALIZE'  # descriptor belongs to this process; OS closes it on exit


def install_audit(configuration_path):
    """Loaded by sitecustomize in EVERY clean interpreter, including UI owner."""
    global AUDIT
    if AUDIT is not None:return
    config=json.loads(Path(configuration_path).read_text(encoding='utf-8'))
    AUDIT=FileAudit(config);AUDIT.self_test()
    # Verify install/seed provenance before any Runtime is prepared. A seed
    # path is not a predicted outcome, and is never supplied by an old lab.
    import dee_thinking as d
    assert d.__version__=='3.5.0'
    assert d.kernel_identity()['kernel_version']==27
    assert Path(d.__file__).resolve().is_relative_to(Path(sys.prefix).resolve())
    assert 'site-packages' in str(Path(d.__file__).resolve())
    assert sha(d._native.__file__)==NATIVE_SHA
    AUDIT.native_path(d.reference_seed_path(),'bundled seed')
    AUDIT.installation_verified=True


def child(mode,package,output):
    global AUDIT
    root=Path(package).resolve();out=Path(output).resolve();out.mkdir(parents=True,exist_ok=True)
    if AUDIT is None:AUDIT=getattr(sys.modules.get('cpc3_clean_audit'),'AUDIT',None)
    assert AUDIT is not None and AUDIT.installation_verified,'Audit bootstrap must precede project imports'
    import dee_thinking as d
    identity={'version':d.__version__,'kernel':d.kernel_identity(),'module':d.__file__,
              'native_module':d._native.__file__,'native_sha256':sha(d._native.__file__),
              'python':sys.executable,'cwd':str(Path.cwd())}
    if mode=='inherited':
        sys.path.insert(0,str(root/'genealogia/CP02_B/src'))
        from predictor import PredictorSession,build,PersistentTransportHabitat,AuditLog,physical
        s=PredictorSession(build(),PersistentTransportHabitat(True,80));s.experience_past_results()
        log=AuditLog(out/'PREDICCIONES.jsonl');em=s.predict([60,100],log,'CPC3_CLEAN_INHERITED')
        a=s.evaluate(60,log,'CPC3_CLEAN_INHERITED');b=s.evaluate(100,log,'CPC3_CLEAN_INHERITED')
        assert em['emission_tick']==37 and em['prediction_set']==[True]
        assert [a['absolute_error_binary'],b['absolute_error_binary']]==[0,1]
        result={'identity':identity,'inherited_reference_reproduced':True,
                'emission':em,'errors':[0,1],'physical_final':physical(s.world),
                'scope':'One inherited short witness; original error after environmental flip preserved.'}
    elif mode=='main':
        sys.path.insert(0,str(root/'src'))
        from core.entity import Entity
        e=Entity.create(initial_open=False,change_tick=80);e.event_sink=out/'PREDICCIONES.jsonl'
        e.sense();emissions=[e.predict(30)]
        for tick in (163,292,554,812,945):
            event=e.sense();assert event['tick']==tick+1
            if tick!=292:emissions.append(e.predict(30))
            if tick==812:
                e._advance_to(843);middle=out/'RESUME_T843.deetsnap';AUDIT.native_path(middle,'save');e.save(middle)
        e._advance_to(1032);e.advance(0);final=e.physical_digest()
        primary=json.loads((root/'experimentos/continuidad/RESULTADOS.json').read_text(encoding='utf-8'))
        expected=next(c for c in primary['cases'] if c['case']['id']=='BA_FULL')['final_snapshot']['physical']
        assert final==expected,{'expected':expected,'actual':final}
        file=out/'REPRODUCED_MAIN_FINAL.deetsnap';AUDIT.native_path(file,'save');e.save(file)
        result={'identity':identity,'new_result_reproduced':True,'final_physical':final,'expected_physical':expected,
                'emissions':[{'tick':x['emission_tick'],'target':x['target_tick'],'set':x['prediction_set'],'physical':x['physical_output'],'memory':x['memory_panel']} for x in emissions],
                'receipts':[x['receipt'] for x in e.events if x['kind']=='EXPERIENCE'],
                'snapshot':str(file),'snapshot_sha256':sha(file),'scope':'One continuous trajectory, no operational descendant readout.'}
    elif mode=='main_new_question':
        sys.path.insert(0,str(root/'src'))
        from core.entity import Entity
        file=out.parent/'main/RESUME_T843.deetsnap';AUDIT.native_path(file,'load');e=Entity.load(file)
        assert e.tick==843;e.event_sink=out/'PREDICCIONES.jsonl';before=e.physical_digest();em=e.predict(30)
        assert em['emission_tick']==843 and em['target_tick']==873
        evaluation=e.advance(30)['evaluations'][-1]
        assert e.tick==873 and evaluation['target_tick']==873 and evaluation['error']==0
        new=out/'CONTINUED_NEW_QUESTION.deetsnap';AUDIT.native_path(new,'save');e.save(new)
        result={'identity':identity,'snapshot_new_question':True,'before':before,'emission':em,
                'evaluation':evaluation,'after':e.physical_digest(),'snapshot':str(new),'snapshot_sha256':sha(new),
                'actual_future_evolution_ticks':30,'not_a_terminal_response_lookup':True}
    elif mode=='comparison_prepare':
        sys.path.insert(0,str(root/'src'))
        from core.comparison_entity import CentralComparisonEntity
        e=CentralComparisonEntity.create();e.event_sink=out/'PREDICCIONES.jsonl';e.sense();em=e.predict()
        assert em['emission_tick']==37 and em['target_tick']==83
        file=out/'PENDING_EXPECTATION.deetsnap';AUDIT.native_path(file,'save');e.save(file)
        result={'identity':identity,'emission':em,'snapshot':str(file),'snapshot_sha256':sha(file),
                'stage':'pending; consequence not yet observed or encoded'}
    elif mode=='comparison_resume':
        sys.path.insert(0,str(root/'src'))
        from core.comparison_entity import CentralComparisonEntity
        file=out.parent/'comparison_prepare/PENDING_EXPECTATION.deetsnap';AUDIT.native_path(file,'load')
        e=CentralComparisonEntity.load(file);e.event_sink=out/'PREDICCIONES.jsonl';before=e.physical_digest();record=e.compare()
        assert before['tick']==37 and e.tick==84
        assert record['status']=='CURRENT_NATIVE_COMPARISON_MEASURED'
        assert record['comparison_decoder']['presentation']=='discrepancia_direccional'
        assert record['input_receipt']['status']=='applied'
        count=len(e.predictions);limited=e.predict();assert limited['status']=='OUTSIDE_FORECAST_DOMAIN' and len(e.predictions)==count
        dest=out/'COMPARED_MAIN.deetsnap';AUDIT.native_path(dest,'save');e.save(dest)
        result={'identity':identity,'new_comparison_reproduced':True,'before':before,'comparison':record,
                'post_comparison_request':limited,'after':e.physical_digest(),'snapshot':str(dest),'snapshot_sha256':sha(dest),
                'scope':'Physical expectation survives save/load in another process, meets present consequence, not decoded as a new forecast.'}
    elif mode=='public_ui':
        events=out/'EVENTOS.txt';events.write_text('Instancia nueva\nObserva otra vez\nPredice antes de observar\nGuarda la sesión\nContinúa desde la sesión guardada\nCompara esto con lo anterior\n¿Qué pasará después?\nSalir\n',encoding='utf-8')
        argv=[str(root/'conversar.py'),'--perfil','comparacion','--eventos',str(events),'--sesion',str(out/'session'),'--transcripcion',str(out/'DIALOGOS.jsonl')]
        old=sys.argv;sys.argv=argv
        try:runpy.run_path(argv[0],run_name='__main__')
        finally:sys.argv=old
        rows=[json.loads(x) for x in (out/'DIALOGOS.jsonl').read_text(encoding='utf-8').splitlines()]
        assert len(rows)==8 and not any(x['response'].get('error') for x in rows)
        assert any(x['response'].get('comparison_presentation')=='discrepancia_direccional' for x in rows)
        assert rows[-2]['response']['new_prediction_emitted'] is False
        assert len({x['engine_pid'] for x in rows})==1
        result={'identity':identity,'public_ui_reproduced':True,'commands':len(rows),'single_owner_pid':rows[0]['engine_pid'],
                'transcript_sha256':sha(out/'DIALOGOS.jsonl'),'current_comparison_not_forecast':True}
    else:raise ValueError(mode)
    write_json(out/'PROOF.json',result);print(json.dumps({'mode':mode,'proof':str(out/'PROOF.json')},ensure_ascii=True),flush=True)


def copy_cut(root,destination):
    inventory={};root=Path(root).resolve();destination=Path(destination)
    for folder,dirs,names in os.walk(root,followlinks=False):
        dirs[:]=[name for name in dirs if name not in EXCLUDED and not (Path(folder)/name).is_symlink() and not (Path(folder)/name).is_junction()]
        for name in names:
            p=Path(folder)/name;rel=p.relative_to(root)
            if p.is_symlink() or p.suffix in ('.pyc','.tmp','.zip','.lock') or name in ('MANIFEST.json','HASHES.sha256'):continue
            assert p.resolve().is_relative_to(root)
            data=p.read_bytes();q=destination/rel;q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(data)
            inventory[rel.as_posix()]={'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()}
    return inventory


def extract_cut(archive,destination):
    destination=Path(destination).resolve();destination.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(archive) as z:
        assert z.testzip() is None
        for member in z.infolist():assert (destination/member.filename).resolve().is_relative_to(destination)
        z.extractall(destination)
    root=destination/'CPC3';assert root.is_dir()
    manifest=json.loads((root/'MANIFEST.json').read_text(encoding='utf-8'))
    for rel,record in manifest['files'].items():assert sha(root/rel)==record['sha256'],rel
    return root,manifest['files']


def orchestrate(root,package=None):
    root=Path(root).resolve();sys.path.insert(0,str(root/'compartido'))
    from supervise import Budget,run_job
    budget=Budget(root);started=time.monotonic();deadline=started+1800
    assert budget.remaining()>2400,'Preserve the existing global closure reserve'
    clean=Path(tempfile.mkdtemp(prefix='cpc3_clean_'));outside=clean/'outside';outside.mkdir()
    report={'verified':False,'temporary_directory':str(clean),'started_utc':datetime.now(timezone.utc).isoformat(),
            'campaign_budget_original':budget.data,'jobs':[],'scope':'Technical reproduction, not new independent scientific samples.'}
    report_path=root/'resultados/CLEAN_REPRODUCTION.json';write_json(report_path,report)
    try:
        if package:
            copied,inventory=extract_cut(package,clean/'extraction');report['package_sha256']=sha(package)
        else:
            copied=clean/'extraction/CPC3';copied.mkdir(parents=True)
            inventory=copy_cut(root,copied)
        assert sha(copied/'runtime'/WHEEL)==WHEEL_SHA
        report['copied_root']=str(copied);report['cut_inventory_sha256']=hashlib.sha256(json.dumps(inventory,sort_keys=True).encode()).hexdigest()
        # Exactly the five user-authorized cleanup targets, plus the current
        # source workspace: the copied execution cannot import from either.
        migration=json.loads((copied/'MIGRACION_Y_LIMPIEZA.json').read_text(encoding='utf-8'))
        old=[x['absolute_path'] for x in migration['cleanup_targets']];assert len(old)==5
        audit_dir=clean/'audit';audit_dir.mkdir();config=clean/'AUDIT_CONFIG.json'
        write_json(config,{'five_old_paths':old,'forbidden_paths':old+[str(root)],'audit_directory':str(audit_dir)})
        env=clean/'env';outputs=clean/'outputs';outputs.mkdir()
        def job(name,argv,timeout=180):
            remaining=deadline-time.monotonic()
            assert remaining>30,'30 minute reproduction cap reached'
            row=run_job(root,'resultados','clean_'+name,list(map(str,argv)),timeout=min(timeout,remaining-10),
                        kind='independent_qualification',cwd=outside,reserve=1200)
            report['jobs'].append(row);write_json(report_path,report)
            assert row['status']=='COMPLETED',row
            return row
        job('create_venv',[sys.executable,'-I','-B','-m','venv',env],240)
        py=env/'Scripts/python.exe'
        job('offline_install',[py,'-I','-B','-m','pip','install','--no-index','--no-deps',copied/'runtime'/WHEEL],180)
        # Standard venv site-packages is independent of the original product.
        site=env/'Lib/site-packages';assert site.is_dir()
        bootstrap=("import importlib.util,os,sys\n"
                   "p=os.environ.get('CPC3_AUDIT_CONFIG')\n"
                   "if p:\n"
                   " import json\n"
                   " c=json.load(open(p,encoding='utf-8'))\n"
                   " s=importlib.util.spec_from_file_location('cpc3_clean_audit',c['audit_script'])\n"
                   " m=importlib.util.module_from_spec(s);sys.modules[s.name]=m;s.loader.exec_module(m);m.install_audit(p)\n")
        cfg=json.loads(config.read_text(encoding='utf-8'));cfg['audit_script']=str(copied/'compartido/clean_reproduction.py');write_json(config,cfg)
        (site/'sitecustomize.py').write_text(bootstrap,encoding='utf-8')
        previous=os.environ.get('CPC3_AUDIT_CONFIG');os.environ['CPC3_AUDIT_CONFIG']=str(config)
        try:
            for mode in ('inherited','main','main_new_question','comparison_prepare','comparison_resume','public_ui'):
                job(mode,[py,'-I','-B',copied/'compartido/clean_reproduction.py','--child',mode,'--root',copied,'--output',outputs/mode],240)
        finally:
            if previous is None:os.environ.pop('CPC3_AUDIT_CONFIG',None)
            else:os.environ['CPC3_AUDIT_CONFIG']=previous
        proofs={mode:json.loads((outputs/mode/'PROOF.json').read_text(encoding='utf-8'))
                for mode in ('inherited','main','main_new_question','comparison_prepare','comparison_resume','public_ui')}
        audits=[json.loads(p.read_text(encoding='utf-8')) for p in sorted(audit_dir.glob('*.summary.json'))]
        assert len(audits)>=7,'Each supervised interpreter and public MAIN owner needs an exit audit'
        assert all(len(x['five_path_firewall_tests'])==5 for x in audits)
        assert all(x['installation_verified'] for x in audits)
        assert all(x['actual_forbidden_access_count']==0 and not x['forbidden_module_origins'] for x in audits)
        assert sum(x['open_events'] for x in audits)>0 and sum(x['import_events'] for x in audits)>0
        qualified={}
        for rel in inventory:
            if rel.startswith(('src/core/','src/lenguaje/','src/habitat/')) and rel.endswith('.py') or rel in ('conversar.py','compartido/clean_reproduction.py','runtime/'+WHEEL,'experimentos/continuidad/RESULTADOS.json'):
                qualified[rel]=sha(copied/rel)
        stable=all((root/rel).is_file() and sha(root/rel)==digest for rel,digest in qualified.items())
        destination=root/'resultados/CLEAN_REPRODUCTION_EVIDENCE';destination.mkdir(parents=True,exist_ok=True)
        for mode in proofs:
            target=destination/mode;target.mkdir(exist_ok=True)
            for path in (outputs/mode).iterdir():
                if path.is_file() and path.suffix in ('.json','.jsonl','.txt','.deetsnap'):shutil.copy2(path,target/path.name)
        for path in audit_dir.glob('*.summary.json'):shutil.copy2(path,destination/path.name)
        shutil.copy2(config,destination/'AUDIT_CONFIG.json')
        report.update({'verified':bool(stable),'inherited_reference_reproduced':proofs['inherited']['inherited_reference_reproduced'],
                       'new_result_reproduced':proofs['main']['new_result_reproduced'] and proofs['comparison_resume']['new_comparison_reproduced'],
                       'snapshot_new_question':proofs['main_new_question']['snapshot_new_question'],
                       'no_old_path_dependency':all(x['actual_forbidden_access_count']==0 and not x['forbidden_module_origins'] for x in audits),
                       'source_witnesses_unchanged':stable,'qualified_source_hashes':qualified,
                       'proofs':proofs,'audit_processes':len(audits),'audit_open_events':sum(x['open_events'] for x in audits),
                       'audited_import_events':sum(x['import_events'] for x in audits),
                       'audit_coverage':'Python open/import/subprocess, module origins, explicit Native seed/save/load paths; not an OS-wide C++ syscall monitor.',
                       'installation':'fresh non-editable CPython3.13 venv; offline included official wheel only',
                       'elapsed_seconds':time.monotonic()-started,'campaign_elapsed_seconds':budget.elapsed(),
                       'evidence_directory':str(destination),'no_publication_or_cleanup_performed':True})
        assert all(report[k] for k in ('verified','inherited_reference_reproduced','new_result_reproduced','snapshot_new_question','no_old_path_dependency')),report
        write_json(report_path,report);print(json.dumps({k:report[k] for k in ('verified','inherited_reference_reproduced','new_result_reproduced','snapshot_new_question','no_old_path_dependency','elapsed_seconds')},indent=2))
    except Exception as exc:
        report.update({'verified':False,'error':repr(exc),'elapsed_seconds':time.monotonic()-started,'temporary_cut_preserved':True})
        write_json(report_path,report);raise


def main():
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);p.add_argument('--package',type=Path)
    p.add_argument('--child',choices=['inherited','main','main_new_question','comparison_prepare','comparison_resume','public_ui'])
    p.add_argument('--output',type=Path);a=p.parse_args()
    if a.child:child(a.child,a.root,a.output)
    else:orchestrate(a.root,a.package)


if __name__=='__main__':main()
