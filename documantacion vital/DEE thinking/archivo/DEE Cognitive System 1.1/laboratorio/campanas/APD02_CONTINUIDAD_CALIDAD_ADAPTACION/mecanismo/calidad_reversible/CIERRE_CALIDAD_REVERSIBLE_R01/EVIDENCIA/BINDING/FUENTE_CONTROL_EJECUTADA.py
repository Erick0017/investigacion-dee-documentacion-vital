"""Explicit GO-only operational control: paired import, original FIFO window.

An outer bounded Job supervises each CLI stage; the unchanged original window
still owns exactly one native service and its own Job. No scientific policy.
"""
import argparse,datetime as dt,hashlib,importlib.util,json,os,sys,time
from pathlib import Path

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_bytes())
def write(p,v):Path(p).write_text(json.dumps(v,ensure_ascii=False,sort_keys=True,indent=2)+'\n',encoding='utf8')
def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

def main():
    p=argparse.ArgumentParser();p.add_argument('--config',type=Path,required=True);p.add_argument('--salida',type=Path,required=True);p.add_argument('--go-nativo-root',action='store_true');a=p.parse_args()
    if not a.go_nativo_root:raise ValueError('No native action without explicit Root GO after closed hour export')
    cfg=read(a.config);base=a.config.resolve().parent;s=Path(cfg['system_root']).resolve(strict=True)
    if cfg['status']!='BOUND_AWAITING_EXPLICIT_ROOT_NATIVE_GO':raise ValueError('Unrecognized bound control')
    checks={s/'gestionar.py':cfg['system_manager_sha256'],s/'app/importacion_emparejada.py':cfg['pair_importer_sha256'],s/'app/process_control.py':cfg['process_control_sha256'],base/cfg['protocol']:cfg['protocol_sha256'],base/cfg['window_runner']:cfg['window_runner_sha256'],Path(cfg['paired_export'])/'EXPORTACION_SERVICIO.json':cfg['pair_manifest_sha256']}
    for path,expected in checks.items():
        if sha(path)!=expected:raise ValueError('Frozen source/input changed: '+str(path))
    if(s/'estado/vidas'/cfg['life']).exists():raise FileExistsError('No retry or replacement of a used control life')
    deadline=dt.datetime.fromisoformat(cfg['campaign_deadline_utc']);left=(deadline-dt.datetime.now(dt.timezone.utc)).total_seconds()
    if left<1200:raise ValueError('Preserve final integration budget; campaign clock is not reset')
    for key in('OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS','NUMEXPR_NUM_THREADS'):os.environ[key]='1'
    pc=module('apd02_control_job',s/'app/process_control.py')
    out=a.salida.resolve();out.mkdir(parents=True,exist_ok=False);(out/'CONFIG_EJECUTADA.json').write_bytes(a.config.read_bytes());(out/'FUENTE_CONTROL_EJECUTADA.py').write_bytes(Path(__file__).read_bytes())
    result={'schema':'APD02.quality_reversal.explicit_omit_control_execution.v1','life':cfg['life'],'paired_parent_snapshot_sha256':cfg['parent_snapshot_sha256'],'max_total_wall_seconds':600,'new_main_ticks':0,'steps':[],'error':None};started=time.monotonic()
    def run(label,argv):
        remaining=600-(time.monotonic()-started)
        if remaining<=0:raise TimeoutError('Control fixed total wall600 exhausted; no retry')
        stdout=(out/(label+'.stdout')).open('x',encoding='utf8');stderr=(out/(label+'.stderr')).open('x',encoding='utf8');process=None;job=None;row={'label':label,'argv':argv,'timeout_seconds':remaining,'memory_limit_bytes':536870912}
        try:
            process,job,name=pc.spawn_owned(argv,cwd=s,stdout=stdout,stderr=stderr,memory_limit=536870912);row.update({'job_name':name,'pid':process.pid})
            process.wait(timeout=remaining);row['returncode']=process.returncode
            if process.returncode!=0:raise RuntimeError(label+' failed; reached branch/queue preserved, no retry')
        finally:
            if job is not None:
                limit=time.monotonic()+5;res=pc.job_resources(job)
                while process.poll()is not None and res.get('job_active_processes',0)and time.monotonic()<limit:time.sleep(.02);res=pc.job_resources(job)
                row['before_close']=res
                if process.poll()is None or res.get('job_active_processes',0):pc.terminate_job(job,125);row['forced_owned_job_close']=True;process.wait(timeout=30)
                row['after_close_request']=pc.job_resources(job);pc.close_job(job)
            stdout.close();stderr.close();row['elapsed_total_seconds']=time.monotonic()-started;result['steps'].append(row);write(out/'EJECUCION.json',result)
    try:
        run('01_IMPORTAR_PAR',[sys.executable,'-I','-B','-X','utf8',str(s/'gestionar.py'),'mente-unificada-importar','--paquete',cfg['paired_export'],'--vida',cfg['life']])
        card=read(s/'estado/vidas'/cfg['life']/'VIDA.json');result['imported_physical']=card['physical'];result['imported_snapshot_sha256']=card['snapshot_sha256']
        export_manifest=read(Path(cfg['paired_export'])/'EXPORTACION_SERVICIO.json')
        if card.get('parent',{}).get('encoded_sha256')!=cfg['parent_snapshot_sha256']:raise ValueError('Imported genealogy does not name the exact original paired parent')
        for key in('N','tick','RAW_sha256','clocks_sha256'):
            if card['physical'][key]!=export_manifest['physical'][key]:raise ValueError('Paired import altered physical field: '+key)
        if sha(s/card['snapshot'])!=card['snapshot_sha256']:raise ValueError('Imported complete encoded snapshot bytes disagree with VIDA')
        original_protocol=read(base/cfg['protocol']);executed_protocol=dict(original_protocol);executed_protocol['snapshot_sha256']=card['snapshot_sha256']
        # Store encodes the new document identity. Never pretend its compressed
        # snapshot SHA is the original parent's SHA, nor rewrite the original.
        postimport=out/'PROTOCOLO_EJECUTADO_POSTIMPORT.json';write(postimport,executed_protocol)
        write(out/'VINCULACION_POSTIMPORT_N0.json',{'native_ticks_during_binding':0,'original_bound_protocol_sha256':cfg['protocol_sha256'],'executed_protocol_sha256':sha(postimport),'only_documentary_protocol_change':{'path':'/snapshot_sha256','before':original_protocol['snapshot_sha256'],'after':card['snapshot_sha256']},'parent_encoded_sha256':card['parent']['encoded_sha256'],'paired_parent_physical':export_manifest['physical'],'imported_physical':card['physical'],'physical_fields_compared':['N','tick','RAW_sha256','clocks_sha256'],'scope':'Imported operational identity may alter encoded snapshot/metadata. The complete parent and exact physical fields remain preserved. This is not learning or a causal equality claim about all operational metadata.'})
        run('02_VENTANA_ORIGINAL',[sys.executable,'-I','-B','-X','utf8',str(base/cfg['window_runner']),'--sistema',str(s),'--protocolo',str(postimport),'--salida',str(out/'VENTANA_OMIT')])
    except BaseException as e:
        result['error']={'type':type(e).__name__,'detail':str(e)}
    finally:
        result['host_seconds']=time.monotonic()-started;result['source_inputs_still_exact']=all(sha(path)==expected for path,expected in checks.items());write(out/'EJECUCION.json',result)
    print(json.dumps(result,ensure_ascii=False));return bool(result['error'])
if __name__=='__main__':raise SystemExit(main())
