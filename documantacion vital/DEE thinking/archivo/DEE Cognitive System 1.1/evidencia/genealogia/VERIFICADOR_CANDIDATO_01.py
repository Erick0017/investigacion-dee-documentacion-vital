"""External verifier: only extracted system code executes the participant.

No scientific original is changed. This controller holds no trained answers;
its explicit audit assertions are checked after native emissions.
"""
from pathlib import Path,PurePosixPath
from datetime import datetime,timezone
import argparse,hashlib,importlib.util,json,os,struct,subprocess,sys,time,zipfile
PREFIX='DEE_COGNITIVE_SYSTEM_1_1'
def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb')as f:
        for b in iter(lambda:f.read(1048576),b''):h.update(b)
    return h.hexdigest()
def read(p):return json.loads(Path(p).read_bytes())
def put(p,x):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def extract(archive,out):
    out.mkdir(parents=True,exist_ok=False)
    with zipfile.ZipFile(archive)as z:
        names=z.namelist()
        if len(names)!=len(set(n.casefold()for n in names))or z.testzip():raise ValueError('ZIP duplicate/CRC error')
        for name in names:
            p=PurePosixPath(name)
            if p.is_absolute()or'..'in p.parts or':'in name or not name.startswith(PREFIX+'/'):raise ValueError('Unsafe ZIP name')
        z.extractall(out)
    root=out/PREFIX;m=read(root/'MANIFEST.json');expected={x['path']for x in m['files']}|{'MANIFEST.json','HASHES.sha256'};actual={p.relative_to(root).as_posix()for p in root.rglob('*')if p.is_file()}
    if expected!=actual:raise ValueError('Manifest inventory differs')
    for x in m['files']:
        p=root/x['path']
        if p.stat().st_size!=x['bytes']or sha(p)!=x['sha256']:raise ValueError('Member bytes differ: '+x['path'])
    return root,{'archive_sha256':sha(archive),'all_member_hashes_equal':True,'CRC':'PASS','members':len(actual)}

def main():
    p=argparse.ArgumentParser();p.add_argument('stage',choices=['prepare','profiles','heritage','audit']);p.add_argument('--out',type=Path,required=True);p.add_argument('--system-zip',type=Path);p.add_argument('--audit-zip',type=Path);p.add_argument('--python',type=Path);a=p.parse_args();out=a.out.resolve();out.mkdir(parents=True,exist_ok=True);rp=out/'VERIFICACION_EN_CURSO.json';report=read(rp)if rp.exists()else{'schema':'DCS1.1.final.exact_archive.verification.v1','started_utc':datetime.now(timezone.utc).isoformat(),'commands':[],'checks':{},'status':'RUNNING','historical_archives_used_by_system':False,'external_dependencies':['Windowsx64 with C++runtime','AvailableCPython3.13x64 withvenv/ensurepip'],'source_controller':str(Path(__file__)),'source_controller_sha256':sha(__file__)};start=time.perf_counter()
    def save():report['updated_utc']=datetime.now(timezone.utc).isoformat();put(rp,report)
    def check(name,value,detail=None):
        report['checks'][name]={'passed':bool(value),'detail':detail};save()
        if not value:raise AssertionError(name)
    root=Path(report['system_root'])if'system_root'in report else None;python=Path(report['isolated_python'])if'isolated_python'in report else None
    controller=None
    if root:
        spec=importlib.util.spec_from_file_location('_dcs_final_owned_process',root/'sistema/app/process_control.py');controller=importlib.util.module_from_spec(spec);spec.loader.exec_module(controller)
    def run(name,argv,timeout=300,native=False,expect=0):
        dest=out/'comandos';dest.mkdir(exist_ok=True);i=len(report['commands']);base=dest/('%03d_%s'%(i,name));env=dict(os.environ);env.pop('PYTHONPATH',None);beg=time.perf_counter();job=None
        with base.with_suffix('.stdout').open('w',encoding='utf8')as so,base.with_suffix('.stderr').open('w',encoding='utf8')as se:
            if native:
                proc,job,jobname=controller.spawn_owned(list(map(str,argv)),cwd=out,stdout=so,stderr=se,memory_limit=4*1024**3)
            else:proc=subprocess.Popen(list(map(str,argv)),cwd=out,env=env,stdout=so,stderr=se,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
            try:code=proc.wait(timeout=timeout)
            except BaseException:
                if job:controller.terminate_job(job)
                else:proc.kill()
                proc.wait();raise
            finally:
                resources=controller.job_resources(job)if job else None
                if job:controller.close_job(job)
        row={'name':name,'argv':list(map(str,argv)),'cwd':str(out),'exit_code':code,'seconds':time.perf_counter()-beg,'stdout':str(base.with_suffix('.stdout').relative_to(out)),'stderr':str(base.with_suffix('.stderr').relative_to(out)),'owned_process_waited':True,'owned_job_closed':bool(job),'job_resources':resources};report['commands'].append(row);save()
        if code!=expect:raise RuntimeError('Unexpected status: '+name+' '+str(code)+'; see '+str(base))
        return base.with_suffix('.stdout').read_text(encoding='utf8')
    def cli(*args):return json.loads(run('cli_'+str(args[0])if args else'cli_default',[python,'-I','-B','-X','utf8',root/'sistema/gestionar.py',*args],native=True))
    try:
        if a.stage=='prepare':
            if root:raise ValueError('System extraction already prepared; do not repeat')
            root,integrity=extract(a.system_zip.resolve(),out/'sistema_extraido');report['system_root']=str(root);report['system_zip']=str(a.system_zip.resolve());report['system_integrity']=integrity;report['system_sha256']=integrity['archive_sha256'];save()
            spec=importlib.util.spec_from_file_location('_dcs_final_owned_process',root/'sistema/app/process_control.py');controller=importlib.util.module_from_spec(spec);spec.loader.exec_module(controller)
            run('create_isolated_environment',[a.python,'-I','-B','-m','venv',out/'entorno'],180);python=out/'entorno/Scripts/python.exe';report['isolated_python']=str(python);save()
            run('empty_before_install',[python,'-I','-B','-c','import sys,struct,importlib.util;assert sys.version_info[:2]==(3,13)and struct.calcsize("P")==8;assert importlib.util.find_spec("dee_thinking")is None;print(sys.executable)'])
            wheel=root/'sistema/runtime/dee_thinking-4.5.0-cp313-cp313-win_amd64.whl';check('official_wheel_identity',sha(wheel)=='09e191d259fd15d321ea11b587f8cc02c12c7adfe81b7b96ca2dbebb1fb12d0c')
            run('offline_install',[python,'-I','-B','-m','pip','--disable-pip-version-check','install','--no-index','--no-deps','--no-cache-dir',wheel],180)
            version=cli('version');report['installed_identity']=version;save();status=cli();check('loaded_learned_preferred3154',status['INSTRUMENTO']['life_id']=='E1_SOCIAL_11'and status['physical']['tick']==3154,status)
            check('no_laboratory_or_evidence_in_system_extract',not(root/'evidencia').exists()and not(root/'laboratorio').exists())
            launch=run('powershell_entrypoint',['C:/WINDOWS/System32/WindowsPowerShell/v1.0/powershell.exe','-NoProfile','-ExecutionPolicy','Bypass','-File',root/'sistema/iniciar_sistema.ps1','estado','-PythonExecutable',python],native=True);check('powershell_loads_existing_life',json.loads(launch)['INSTRUMENTO']['life_id']=='E1_SOCIAL_11')
            events=cli('eventos',root/'sistema/documentacion/ejemplos/visita_1_1.eventos');report['new_interaction_events']=events;save()
            center=next(x['result']['ENTE']['quantity.center']for x in events if isinstance(x.get('result'),dict)and'ENTE'in x['result']and'quantity.center'in x['result']['ENTE']);check('new_object_native_greater_than_acquired_reference',center['active']and center['semantic']==1 and center['direction']==[-1,0,0],center)
            visit=cli('estado','--vida','VISITA_11');check('fork_continuation3221',visit['physical']['tick']==3221 and cli()['physical']==status['physical'])
            cli('entrada','--vida','VISITA_11','TM.quantity.reader','7','3287','--sonda');cli('guardar','--vida','VISITA_11');before=cli('restaurar','VISITA_11');cli('continuar','--vida','VISITA_11','--hasta','3288');after=cli('observar-componente','--vida','VISITA_11','two_memory.center');check('pending_queue_across_processes_new_interaction',before['physical']['tick']==3221 and after['ENTE']['two_memory.center']['active']and after['ENTE']['two_memory.center']['direction']==[1,0,0],after)
            check('archive_not_changed_by_continuation',sha(a.system_zip)==report['system_sha256'])
        elif a.stage=='profiles':
            run('profiles_release_C',[python,'-I','-B','-X','utf8',root/'sistema/gestionar.py','ensayar','--nivel','C','--salida',out/'PERFILES_C'],3000,native=True)
            result=read(out/'PERFILES_C/pruebas/RESULTADOS.json');report['profile_release']=result;check('all_declared_profile_release_checks',result['status']=='PASS_DECLARED_CHECKS',{'checks':len(result['checks']),'failures':result['failures']})
        elif a.stage=='heritage':
            # Both workers load only the extracted system modules and its exact
            # content-addressed source store. No historical ZIP path is passed.
            code='import sys,json;from pathlib import Path;sys.path.insert(0,sys.argv[1]);from app.legacy import run_families;r=run_families(Path(sys.argv[1]),Path(sys.argv[2]),max_workers=2,total_seconds=4200,job_seconds=1100);print(json.dumps(r["counts"]))'
            run('all34_from_closed_system',[python,'-I','-B','-X','utf8','-c',code,root/'sistema',out/'HERENCIA_FINAL'],4300,native=True)
            result=read(out/'HERENCIA_FINAL/REGRESION_HEREDADA.json');report['heritage_release']={'source':str(out/'HERENCIA_FINAL/REGRESION_HEREDADA.json'),'sha256':sha(out/'HERENCIA_FINAL/REGRESION_HEREDADA.json'),'counts':result['counts'],'families':{k:v['status']for k,v in result['family_results'].items()},'commands':result['commands']};check('all34_families_recovered_without_historical_zips',len(result['family_results'])==34 and all(x['status']=='PASS'for x in result['family_results'].values()),result['counts'])
        else:
            auditroot,integrity=extract(a.audit_zip.resolve(),out/'auditoria_extraida');report['audit_root']=str(auditroot);report['audit_zip']=str(a.audit_zip.resolve());report['audit_integrity']=integrity;report['audit_sha256']=integrity['archive_sha256'];save()
            check('no_motor_in_audit',not any(p.suffix.lower()in('.whl','.pyd','.dll','.exe')for p in auditroot.rglob('*')if p.is_file()))
            script=auditroot/'laboratorio/campanas/CONSOLIDACION_1_1/herramientas/recalcular.py';recalculated=out/'CALCULOS_AUDITORIA_EXTRAIDA.json';run('engine_free_recalculation',[python,'-I','-B','-X','utf8',script,'--root',auditroot,'--out',recalculated],180)
            expected=read(auditroot/'evidencia/informes/CALCULOS_DESDE_PRIMARIOS.json');actual=read(recalculated);keys=('K65','late_access','functional','social_causal','mobile','heritage','ontogeny','microscopic','lived_profiles');comparisons={k:actual[k]==expected[k]for k in keys};report['recalculation_comparisons']=comparisons;check('recalculation_from_audit_primary_records_equal',all(comparisons.values()),comparisons)
            report['status']='VERIFIED_BOUNDED_CONTRACTS'if all(x['passed']for x in report['checks'].values())and'heritage_release'in report and'profile_release'in report else'PARTIAL';report['not_certified']=['General mind','65humanmeanings','R2learnedstrategy','Unlimitedstability','Allhistoricaldocumentaryrowsreproduced'];check('both_exact_archives_still_identical',sha(report['system_zip'])==report['system_sha256']and sha(a.audit_zip)==report['audit_sha256']);report['completed_utc']=datetime.now(timezone.utc).isoformat()
        report['last_completed_stage']=a.stage;report.setdefault('stage_seconds',{})[a.stage]=time.perf_counter()-start;save();print(json.dumps({'stage':a.stage,'status':report['status'],'checks':len(report['checks']),'seconds':time.perf_counter()-start}))
    except BaseException as e:report['status']='FAILED';report['error']={'stage':a.stage,'type':type(e).__name__,'detail':str(e)};save();raise
if __name__=='__main__':main()
