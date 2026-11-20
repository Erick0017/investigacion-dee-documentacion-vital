"""Outer resource wrapper only. Default=N0; no Native without later Root GO.

Uses existing spawn_owned and existing APD04 R03 job_measure(class8). The total
Job already includes the driver, Native owners, manager clients and descendants:
never add the nested Native counters to these totals. I/O is logical OS Job I/O,
not physical disk traffic, internal DEE energy or electrical consumption.
"""
from pathlib import Path
from datetime import datetime, timezone
import argparse
import ast
import hashlib
import importlib.util
import json
import shutil
import sys
import time
import traceback

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
LAB = ROOT/'laboratorio/campanas/APD04_ECOSISTEMA_COGNITIVO'
EV = ROOT/'evidencia/campanas/APD04_ECOSISTEMA_COGNITIVO'
EXECUTOR = HERE/'ejecutar_actuador_r02_aux_r01.py'
EXECUTOR_SHA = 'fe7d35f268adc8a94da383f3168220d58b653ec3e403e873052d74b3145dbe9c'
MEASURE = LAB/'ejecucion/ejecutar_plan_apd04_r03.py'
MEASURE_SHA = '126b12f2a0974681ed025dcc5bade3aa68ea73d90010f121e634eaee35ac5b74'
PC = ROOT/'sistema/app/process_control.py'
PC_SHA = 'f3c22937694d9a0ee2b0d20aab112b9af27f57949674a32fe036c595a60ee5b4'
CRITERION = LAB/'ejecucion/CRITERIO_CONTINUACION_Y_RESERVA_R01.json'
CRITERION_SHA = '092f7dc187a55be604d7859a6741fa4f8450608afa50b18c1e9e566e8565003a'
ABSOLUTE_DEADLINE = datetime(2026,10,27,3,30,51,tzinfo=timezone.utc)
MAX_TREE_WALL_SECONDS = 2000
TREE_MEMORY_BYTES = 1073741824


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('x',encoding='utf8')as stream:
        json.dump(value,stream,ensure_ascii=False,indent=2);stream.write('\n')


def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module


def verify_dependencies_n0():
    members=[]
    for path,expected in ((EXECUTOR,EXECUTOR_SHA),(MEASURE,MEASURE_SHA),(PC,PC_SHA),(CRITERION,CRITERION_SHA)):
        actual=sha(path)
        if actual!=expected:raise ValueError('Exact closed source differs; no Native launch: '+str(path))
        ast.parse(path.read_text(encoding='utf8'))if path.suffix=='.py'else None
        members.append({'path':path.relative_to(ROOT).as_posix(),'sha256':actual,'bytes':path.stat().st_size})
    ast.parse(Path(__file__).read_text(encoding='utf8'))
    return members


def prepare_only():
    members=verify_dependencies_n0()
    out=EV/'ACTUADOR_R02_SUPERVISION_N0_R01'
    if out.exists():raise FileExistsError('N0 wrapper preparation is frozen; no overwrite')
    out.mkdir()
    for path in (Path(__file__),EXECUTOR,MEASURE,PC,CRITERION):shutil.copy2(path,out/path.name)
    result={'schema':'APD04.actuator_R02.outer_wrapper.N0.v1','wrapper_sha256':sha(Path(__file__)),
        'dependencies':members,'absolute_deadline_utc':ABSOLUTE_DEADLINE.isoformat(),
        'max_owned_total_tree_wall_seconds':MAX_TREE_WALL_SECONDS,'total_tree_memory_limit_bytes':TREE_MEMORY_BYTES,
        'Native_owner_limit_unchanged_seconds':900,'sample_every_seconds':5,
        'source':'Existing APD04 R03 job_measure uses QueryInformationJobObject class8.',
        'scope':'Outer owned Job includes the driver, Native descendants and manager clients. '
                'Never sum nested Native CPU, RAM or I/O into this total. '
                'Monitor CPU is reported separately. Job I/O is logical, not device I/O or energy.',
        'new_Native_ticks':0,'process_tree_started':False,'shared_system_modified':False,
        'execution_requires_explicit_later_Root_GO':True,
        'prospective_main':'REAL_R02 if complete identity/queue/closure are valid, regardless of utility; OMIT remains a control.'}
    write(out/'PREPARACION_WRAPPER_N0.json',result)
    print(json.dumps(result,ensure_ascii=False,indent=2))


def execute():
    members=verify_dependencies_n0()
    remaining=ABSOLUTE_DEADLINE.timestamp()-time.time()
    wall_limit=min(MAX_TREE_WALL_SECONDS,remaining-30)
    if wall_limit<1920:raise ValueError('Insufficient fixed budget for both bounded AUX and closure; no launch')
    out=EV/'ACTUADOR_R02_SUPERVISION_R01'
    if out.exists():raise FileExistsError('An outer supervision attempt already exists; no physical rerun')
    out.mkdir()
    for path in(Path(__file__),EXECUTOR,MEASURE,PC,CRITERION):shutil.copy2(path,out/path.name)
    pc=load('actuator_existing_total_tree_process_control',PC)
    driver=load('actuator_existing_class8_measurement_only',MEASURE)
    command=[sys.executable,'-I','-B','-X','utf8',str(EXECUTOR),
             '--execute-after-go','ROOT_GO_ACTUADOR_R02','--branch','both']
    write(out/'ANTES_DEL_PROCESO.json',{'command':command,'dependencies':members,
        'wrapper_sha256':sha(Path(__file__)),'started_utc':datetime.now(timezone.utc).isoformat(),
        'total_tree_memory_limit_bytes':TREE_MEMORY_BYTES,'native_owner_limit_seconds':900,
        'outer_wall_limit_seconds':wall_limit,'absolute_deadline_utc':ABSOLUTE_DEADLINE.isoformat(),
        'scope':'One total Job, including driver+Native+clients. Not a sum of nested Jobs. '
                'I/O is logical class8. Energy NO MEDIDA. No Native decisions or timing changes in this wrapper.'})
    began=time.monotonic();cpu0=time.process_time_ns();error=None;final=None;samples=0
    process=job=None;name=None;terminated_by_wrapper=False
    with(out/'STDOUT.txt').open('xb')as stdout,(out/'STDERR.txt').open('xb')as stderr:
        process,job,name=pc.spawn_owned(command,cwd=Path(sys.executable).parent,stdout=stdout,stderr=stderr,memory_limit=TREE_MEMORY_BYTES)
        try:
            while True:
                measurement=driver.job_measure(pc,job)
                sample={'wall_utc':datetime.now(timezone.utc).isoformat(),'elapsed_seconds':time.monotonic()-began,
                        'driver_exit_code':process.poll(),**measurement}
                with(out/'MUESTRAS_TOTALES_CLASS8.jsonl').open('a',encoding='utf8',newline='\n')as stream:
                    stream.write(json.dumps(sample,ensure_ascii=False,separators=(',',':'))+'\n')
                samples+=1
                if process.poll()is not None and not measurement.get('job_active_processes'):break
                if time.monotonic()-began>=wall_limit or datetime.now(timezone.utc)>=ABSOLUTE_DEADLINE:
                    error='Fixed own outer-tree wall/deadline guard, not a cognitive criterion.'
                    write(out/'INTENCION_CIERRE_PROPIO_POR_LIMITE.json',{'utc':datetime.now(timezone.utc).isoformat(),
                        'measurement_before_termination':measurement,'wall_limit_seconds':wall_limit,
                        'does_not_clear_pending_or_restore_lives':True})
                    pc.terminate_job(job,124);terminated_by_wrapper=True
                    process.wait(timeout=15);break
                time.sleep(min(5,max(.1,wall_limit-(time.monotonic()-began))))
            final=driver.job_measure(pc,job)
        except BaseException as failure:
            error=repr(failure)
            write(out/'ERROR_INSTRUMENTAL_SUPERVISION.json',{'error':error,'traceback':traceback.format_exc(),
                'scope':'Instrumentation/host failure, not an E1 result; own tree only will be closed.'})
            pc.terminate_job(job,125);terminated_by_wrapper=True
            process.wait(timeout=15)
            try:final=driver.job_measure(pc,job)
            except BaseException as measurement_failure:final={'measurement_error':repr(measurement_failure)}
        finally:
            # KILL_ON_JOB_CLOSE is never used silently while the owned tree is alive.
            last=pc.job_resources(job)
            if last.get('job_active_processes'):
                write(out/'PROCESOS_PROPIOS_RESTANTES_ANTES_DE_CERRAR_HANDLE.json',last)
                pc.terminate_job(job,125);terminated_by_wrapper=True
                process.wait(timeout=15)
                final=driver.job_measure(pc,job)
            pc.close_job(job)
    result={'schema':'APD04.actuator_R02.total_tree_resources.v1','command':command,'pid':process.pid,'job_name':name,
        'exit_code':process.returncode,'error':error,'samples':samples,'wall_seconds':time.monotonic()-began,
        'monitor_only_cpu_ns':time.process_time_ns()-cpu0,'final_total_job':final,
        'terminated_own_tree_for_host_limit_or_instrumentation':terminated_by_wrapper,
        'finished_utc':datetime.now(timezone.utc).isoformat(),'no_decisional_intervention':True,
        'I/O_scope':'OS logical I/O of the whole monitored tree; not physical disk bytes or DEE internal consumption.',
        'aggregation':'Do not add nested Native Jobs to this total. Monitor CPU is separate.','energy':'NO MEDIDA'}
    write(out/'RESULTADO_SUPERVISION.json',result)
    print(json.dumps(result,ensure_ascii=False,indent=2),flush=True)
    return 1 if error or process.returncode or terminated_by_wrapper else 0


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--execute-after-go',choices=('ROOT_GO_ACTUADOR_R02',))
    args=parser.parse_args()
    if args.execute_after_go is None:prepare_only();return 0
    return execute()


if __name__=='__main__':raise SystemExit(main())
