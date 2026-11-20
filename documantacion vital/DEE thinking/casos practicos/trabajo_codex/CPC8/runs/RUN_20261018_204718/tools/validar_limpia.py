"""External clean functional gate for a sealed CPC8 candidate, never a packager.

Run with installed CPython313/official4.5, cwd and --out outside this extraction.
The public app executes fresh worlds. Scientific references are read only by
the auditor after each trajectory. Child processes load newly produced state.
"""
from __future__ import annotations
import argparse
from array import array
from copy import deepcopy
from datetime import datetime,timezone
import gc
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import platform
import re
import struct
import subprocess
import sys
import sysconfig
import time
import traceback
ROOT=Path(__file__).resolve().parents[1]
WHEEL='dee_thinking-4.5.0-cp313-cp313-win_amd64.whl'
WHEEL_SHA='09e191d259fd15d321ea11b587f8cc02c12c7adfe81b7b96ca2dbebb1fb12d0c'
PYD_SHA='17f827341530f66816ec146af085b00a5f7b3d34d645bcd407f1279e8ac6c50d'
KERNEL_SHA='fbd8190381ed76085f404e6578ff15fe185ab66cd48c67300d2abad61ddc7e31'
sys.dont_write_bytecode=True


def sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb')as f:
        for block in iter(lambda:f.read(1048576),b''):h.update(block)
    return h.hexdigest()


def encoded(value):return json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False).encode('utf8')
def digest(value):return hashlib.sha256(encoded(value)).hexdigest()
def put(path,value):
    path=Path(path);temp=path.with_name(path.name+'.pending.'+str(os.getpid()));temp.write_bytes(encoded(value)+b'\n');os.replace(temp,path)


def app_class():
    spec=importlib.util.spec_from_file_location('cpc8_clean_public_console',ROOT/'app/consola.py')
    module=importlib.util.module_from_spec(spec);sys.modules[spec.name]=module;spec.loader.exec_module(module)
    return module.Console


def physics(world):
    r=world.runtime
    return{'tick':int(r.current_tick),'RAW_sha256':hashlib.sha256(array('Q',r.raw_copy()).tobytes()).hexdigest(),
        'clocks_sha256':hashlib.sha256(array('Q',r.clock_copy()).tobytes()).hexdigest()}


def operative(session):
    from dee_thinking.consolidated import exact_receipt
    receipts=[exact_receipt(r)for r in session.world.runtime.receipts]
    pending=[r for r in receipts if r['status']=='scheduled']
    state=deepcopy(session.state)
    return{'tick':session.tick,'identifier':session.identifier,'channels':sorted(session.world.runtime.channel_names),
        'state':state,'runtime_receipts':receipts,'pending_receipts':pending,
        'state_sha256':digest(state),'runtime_receipts_sha256':digest(receipts),
        'queue_scope':'All pending native receipt IDs plus payload/ports/ticks in the unchanged Session journal and full native snapshot. Decoded snapshot identity additionally covers serialized native queue.'}


class AccessGuard:
    def __init__(self,allowed):
        self.allowed=Path(allowed).resolve();self.active=False;self.events=[];self.denied=[]
        sys.addaudithook(self.hook)
    def hook(self,event,args):
        if not self.active or event!='open'or not args or not isinstance(args[0],(str,bytes)):return
        try:path=Path(os.fsdecode(args[0])).resolve()
        except(ValueError,OSError):return
        if path.is_relative_to(self.allowed):return
        if path.is_relative_to(ROOT):
            first=path.relative_to(ROOT).parts[0]
            if first in('resultados','revision','genealogia','configuraciones','comparadores'):
                self.denied.append(str(path));raise PermissionError('Participant phase refuses external teaching/results/reference files')
        self.events.append(str(path))


def public_summary(c):
    s=c.need();return{'physical':physics(s.world),'operative':operative(s),
        'lower_readouts':deepcopy(s.state.get('reads',[])),'social_captures':deepcopy(s.state.get('social_captures',[]))}


def child_run(mode,snapshot,out):
    out.mkdir(parents=True,exist_ok=False);Console=app_class();guard=AccessGuard(out.parent);c=Console();guard.active=True
    try:
        c.execute('cargar "'+str(snapshot)+'"');loaded=public_summary(c)
        if mode=='resume':c.execute('avanzar 690')
        elif mode=='query396':
            c.execute('social consultar 1 416 11 7');c.execute('avanzar 428')
        else:raise ValueError('Unknown internal child mode')
        final=public_summary(c);saved=c.execute('guardar "'+str(out/'FINAL.deetsnap.gz')+'"')
    finally:guard.active=False
    result={'status':'EXECUTED','mode':mode,'loaded':loaded,'final':final,'snapshot_storage':saved['prueba'],
        'denied_accesses':guard.denied,'access_guard_scope':'Python open audit only; not all native OS reads. Product binary identity/source provenance are separate checks.'}
    put(out/'CHILD.json',result);print(json.dumps({'child':mode,'status':'EXECUTED','final_tick':final['physical']['tick']}),flush=True)


def subprocess_checked(command,cwd,out,timeout):
    started=time.monotonic();completed=subprocess.run(command,cwd=cwd,capture_output=True,text=True,encoding='utf8',errors='replace',timeout=timeout)
    (out.with_suffix('.stdout.log')).write_text(completed.stdout,encoding='utf8');(out.with_suffix('.stderr.log')).write_text(completed.stderr,encoding='utf8')
    row={'argv':[str(x)for x in command],'cwd':str(cwd),'exit_code':completed.returncode,'elapsed_seconds':time.monotonic()-started,
        'stdout':out.with_suffix('.stdout.log').name,'stderr':out.with_suffix('.stderr.log').name}
    if completed.returncode:raise RuntimeError('Owned subprocess failed: '+json.dumps(row))
    return row


def run_public_events(path,out,*,with_checkpoints):
    # This is the environmental generator, not the participant.
    config=json.loads(path.read_text(encoding='utf8'));commands=config['commands']
    Console=app_class();guard=AccessGuard(out);c=Console();snapshots={};summaries={}
    out.mkdir(parents=True,exist_ok=False);guard.active=True
    try:
        with(out/'DIALOGO.jsonl').open('x',encoding='utf8')as transcript:
            def execute(line):
                response=c.execute(line);transcript.write(json.dumps({'request':line,'response':response},ensure_ascii=False)+'\n');transcript.flush();return response
            for line in commands:
                if with_checkpoints and line.strip()=='avanzar 690':
                    execute('avanzar 657');summaries[657]=public_summary(c)
                    snapshots[657]=execute('guardar "'+str(out/'PENDING_T657.deetsnap.gz')+'"')['prueba']
                execute(line)
                if with_checkpoints and line.strip()=='avanzar 396':
                    summaries[396]=public_summary(c);snapshots[396]=execute('guardar "'+str(out/'T396.deetsnap.gz')+'"')['prueba']
            final=public_summary(c)
            snapshots[690]=execute('guardar "'+str(out/'FINAL_T690.deetsnap.gz')+'"')['prueba']
    finally:guard.active=False
    result={'configuration':path.relative_to(ROOT).as_posix(),'configuration_sha256':sha(path),'commands':len(commands),
        'final':final,'boundaries':summaries,'snapshot_storage':snapshots,'denied_accesses':guard.denied,
        'app_source_sha256':sha(ROOT/'app/consola.py')}
    put(out/'APP_RESULT.json',result);c.session=None;del c;gc.collect();return result


def physical_readouts(reads):
    return[{'tick':r['tick'],'kind':r['kind'],'responses':[{'name':x['name'],'physical':x['physical'],'coverage':x['coverage'],'value':x['value'],
        'status':x['status'],'receipt_status':x['receipt']['status'],'receipt_requested_tick':x['receipt']['requested_tick'],
        'receipt_effective_tick':x['receipt']['effective_tick'],'receipt_channels':x['receipt']['channels']}for x in r['responses']]}for r in reads]


def social_physical(captures,*,after=0,through=None):
    return[{'tick':r['tick'],'stage':r['stage'],'observations':r['observations'],
        'decoded':[{'location':x['location'],'physical':x['physical'],'content_class':x['content_class'],'context_class':x['context_class'],'context_role':x['context_role']}for x in r['decoded']]}
        for r in captures if r['tick']>after and(through is None or r['tick']<=through)]


def without_instrument_time(value):
    if isinstance(value,dict):return{k:without_instrument_time(v)for k,v in value.items()if k not in('monotonic_ns','wall_utc')}
    if isinstance(value,list):return[without_instrument_time(x)for x in value]
    return value


def validate(a):
    out=a.out.resolve()
    if out.exists():raise FileExistsError('Existing output protected: '+str(out))
    if out.is_relative_to(ROOT)or Path.cwd().resolve().is_relative_to(ROOT):raise ValueError('cwd and output must be outside the extracted candidate')
    out.mkdir(parents=True);started=time.monotonic();checks=[];commands=[];errors=[]
    report={'schema':'CPC8.clean-functional-validation.v1','artifact_sha256':a.artifact_sha256.lower(),'candidate':str(a.artifact)if a.artifact else None,
        'candidate_identity_mode':'SEALED_BYTES_VERIFIED'if a.artifact else'CALLER_SUPPLIED_EXACT_SEALED_CANDIDATE_HASH',
        'root':str(ROOT),'cwd':str(Path.cwd()),'started_utc':datetime.now(timezone.utc).isoformat(),'development':a.development,
        'state':'DEVELOPMENT'if a.development else'SEALED_CANDIDATE','validator_sha256':sha(Path(__file__)),
        'identity_only':a.identity_only,
        'checks':checks,'commands':commands,'errors':errors,'status':'RUNNING','passed':False,
        'scientific_scope':'Technical reproduction and continuation only; no independent scientific samples or new semantic claims.'}
    def check(name,passed,details=None):checks.append({'name':name,'passed':bool(passed),'details':details});put(out/'VALIDACION_LIMPIA.json',report)
    def attempt(name,function):
        try:return function()
        except BaseException as error:
            errors.append({'step':name,'error_type':type(error).__name__,'error':str(error),'traceback':traceback.format_exc()});check(name,False,'See preserved error and logs');return None
    def identity():
        import dee_thinking as dee
        from dee_thinking import _native as native
        wheel=ROOT/'runtime'/WHEEL;kernel=ROOT/'genealogia/product45/kernel_v27.cpp'
        data={'version':dee.__version__,'python':sys.executable,'python_version':sys.version,'implementation':sys.implementation.name,'platform':platform.platform(),
            'pointer_bytes':struct.calcsize('P'),'gil_disabled':sysconfig.get_config_var('Py_GIL_DISABLED'),'module':dee.__file__,'native':native.__file__,
            'native_sha256':sha(native.__file__),'wheel':wheel.relative_to(ROOT).as_posix(),'wheel_sha256':sha(wheel),'build_info':dee.build_info(),
            'kernel_source':kernel.relative_to(ROOT).as_posix(),'kernel_source_sha256':sha(kernel),
            'isolated_flag':sys.flags.isolated,'ignore_environment_flag':sys.flags.ignore_environment,
            'PYTHONPATH_environment_present':bool(os.environ.get('PYTHONPATH')),'PYTHONPATH_effect':'Ignored by CPython -I/ignore_environment; no content of the environment variable is logged',
            'isolated_sys_path_at_identity':list(sys.path)}
        valid=sys.implementation.name=='cpython'and sys.version_info[:2]==(3,13)and struct.calcsize('P')==8 and platform.system()=='Windows'and not data['gil_disabled']
        valid=valid and dee.__version__=='4.5.0'and Path(dee.__file__).resolve().is_relative_to(Path(sys.prefix).resolve())and Path(native.__file__).resolve().is_relative_to(Path(sys.prefix).resolve())
        valid=valid and data['native_sha256']==PYD_SHA and data['wheel_sha256']==WHEEL_SHA and data['kernel_source_sha256']==KERNEL_SHA
        valid=valid and data['build_info']['kernel_source_sha256']==KERNEL_SHA and sys.flags.isolated==1 and sys.flags.ignore_environment==1 and ''not in sys.path
        if a.artifact:valid=valid and sha(a.artifact)==a.artifact_sha256.lower()
        check('official_installed_identity_and_sealed_hash',valid,data)
        runtime=native.Runtime(11);empty={'dimension':runtime.dimension,'tick':int(runtime.current_tick),'active_RAW':sum(bool(x)for x in runtime.raw_copy()),'nonzero_clocks':sum(bool(x)for x in runtime.clock_copy())}
        check('direct_Runtime_empty_not_pretrained',empty['tick']==0 and empty['active_RAW']==0 and empty['nonzero_clocks']==0,empty);del runtime
        if not valid:raise AssertionError('Incorrect installed instrument; trajectories not authorized')
        return data
    instrument=attempt('identity',identity)
    if instrument and not a.identity_only:
        def references():
            target=out/'references';command=[sys.executable,'-I','-B','-X','utf8',str(ROOT/'base_validada/reproducir_cp01_cp02.py'),'--out',str(target)]
            commands.append(subprocess_checked(command,out,out/'reference_command',600))
            rows=[]
            for name in('CP01.json','CP02.json','CP01_CONTINUATION.json','SUMMARY.json'):
                fresh=json.loads((target/name).read_text(encoding='utf8'));reference=ROOT/'resultados/genealogia_cp01_cp02_r1'/name
                old=json.loads(reference.read_text(encoding='utf8'));rows.append({'name':name,'fresh_sha256':sha(target/name),'reference_sha256':sha(reference),
                    'equal_without_wall_monotonic_log_stamps':without_instrument_time(fresh)==without_instrument_time(old)})
            check('CP01_CP02_historical_references',all(r['equal_without_wall_monotonic_log_stamps']for r in rows),rows)
        attempt('references_execution',references)
        integrated=attempt('public_integrated_execution',lambda:run_public_events(ROOT/'configuraciones/demo/vida_integrada.json',out/'vida_integrada',with_checkpoints=True))
        control=attempt('public_control_execution',lambda:run_public_events(ROOT/'configuraciones/demo/vida_control.json',out/'vida_control',with_checkpoints=False))
        # The auditor starts here; these files were unavailable during app evolution.
        if integrated:
            def compare_integrated():
                reference=ROOT/'resultados/semantica/SOC_I21_SOCIAL_THEN_L01_REVISION/MEASUREMENTS.json';old=json.loads(reference.read_text(encoding='utf8'))
                comparisons={'full_final_RAW_clocks_tick':integrated['final']['physical']==old['final_physical'],
                    'native_lower_readouts':physical_readouts(integrated['final']['lower_readouts'])==physical_readouts(old['native_readouts']),
                    'social_physical_readouts':social_physical(integrated['final']['social_captures'])==social_physical(old['social_captures'])}
                check('public_integrated_vs_scientific_I21',all(comparisons.values()),{'reference':reference.relative_to(ROOT).as_posix(),'sha256':sha(reference),'comparisons':comparisons})
                pending=integrated['boundaries'][657]['operative']['pending_receipts'];check('T657_contains_future_native_queue',len(pending)>0,{'scheduled':pending,'pending_source':'Native runtime receipts; payload and protocols preserved in snapshot'})
                command=[sys.executable,'-I','-B','-X','utf8',str(Path(__file__).resolve()),'--child','resume','--snapshot',str(out/'vida_integrada/PENDING_T657.deetsnap.gz'),'--out',str(out/'hijo657')]
                commands.append(subprocess_checked(command,out,out/'child657_command',300));child=json.loads((out/'hijo657/CHILD.json').read_text(encoding='utf8'))
                comparisons={'physical_loaded657':child['loaded']['physical']==integrated['boundaries'][657]['physical'],
                    'operative_loaded657':child['loaded']['operative']==integrated['boundaries'][657]['operative'],
                    'physical_final690':child['final']['physical']==integrated['final']['physical'],
                    'operative_final690':child['final']['operative']==integrated['final']['operative'],
                    'decoded_full_snapshot690':child['snapshot_storage']['decoded_sha256']==integrated['snapshot_storage'][690]['decoded_sha256'],
                    'no_forbidden_reference_reads':not child['denied_accesses']and not integrated['denied_accesses']}
                check('new_process_restore657_continue690',all(comparisons.values()),comparisons)
                command=[sys.executable,'-I','-B','-X','utf8',str(Path(__file__).resolve()),'--child','query396','--snapshot',str(out/'vida_integrada/T396.deetsnap.gz'),'--out',str(out/'hijo396')]
                commands.append(subprocess_checked(command,out,out/'child396_command',300));child=json.loads((out/'hijo396/CHILD.json').read_text(encoding='utf8'))
                reference=ROOT/'resultados/semantica/SOC_I17_RESTORED_NEW_QUERY/MEASUREMENTS.json';old=json.loads(reference.read_text(encoding='utf8'))
                comparisons={'loaded396_physical':child['loaded']['physical']==integrated['boundaries'][396]['physical'],
                    'loaded396_operative':child['loaded']['operative']==integrated['boundaries'][396]['operative'],
                    'physical428_vs_I17':child['final']['physical']==old['final_physical'],
                    'new419_423_428_physical_readouts':social_physical(child['final']['social_captures'],after=396)==social_physical(old['social_captures'],after=396),
                    'no_forbidden_reference_reads':not child['denied_accesses']}
                check('new_process_restore396_new_query416',all(comparisons.values()),{'reference':reference.relative_to(ROOT).as_posix(),'sha256':sha(reference),'comparisons':comparisons})
            attempt('auditor_integrated_and_new_processes',compare_integrated)
        if control:
            def compare_control():
                reference=ROOT/'resultados/semantica/SOC_I12_L17_SOURCE_UNPAIRED/MEASUREMENTS.json';old=json.loads(reference.read_text(encoding='utf8'))
                got=social_physical(control['final']['social_captures'],through=166);expected=social_physical(old['social_captures'],through=166)
                check('public_control_early_vs_scientific_unpaired',got==expected,{'reference':reference.relative_to(ROOT).as_posix(),'sha256':sha(reference),
                    'scope':'Compare the shared initial social task through166, not unequal global worlds/horizons; later demo continuation remains observable.',
                    'control_new_social_stages':len(got),'reference_social_stages':len(expected),'no_reference_reads_during_app':not control['denied_accesses']})
            attempt('auditor_control',compare_control)
        modules={name:str(Path(mod.__file__).resolve())for name,mod in sys.modules.items()if getattr(mod,'__file__',None)and name.startswith(('dee_thinking','integracion','comunicacion'))}
        valid=all(Path(path).is_relative_to(Path(sys.prefix).resolve())if name.startswith('dee_thinking')else Path(path).is_relative_to(ROOT/'src')for name,path in modules.items())
        check('no_hidden_legacy_product_or_lab_imports',valid,modules)
    report.update(elapsed_seconds=time.monotonic()-started,finished_utc=datetime.now(timezone.utc).isoformat(),
        passed=bool(checks)and all(x['passed']for x in checks)and not errors)
    report['status']=('DEVELOPMENT_PASS'if a.development else'PASS')if report['passed']else'FAIL'
    put(out/'VALIDACION_LIMPIA.json',report);print(json.dumps({'status':report['status'],'passed':report['passed'],'checks':len(checks),'elapsed_seconds':report['elapsed_seconds'],'report':str(out/'VALIDACION_LIMPIA.json')}),flush=True)
    return 0 if report['passed']else 1


def main():
    if hasattr(sys.stdout,'reconfigure'):sys.stdout.reconfigure(encoding='utf8')
    if hasattr(sys.stderr,'reconfigure'):sys.stderr.reconfigure(encoding='utf8')
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--out',type=Path,required=True);p.add_argument('--artifact-sha256');p.add_argument('--artifact',type=Path);p.add_argument('--development',action='store_true')
    p.add_argument('--identity-only',action='store_true',help='Development identity smoke only; never a publication gate')
    p.add_argument('--child',choices=('resume','query396'));p.add_argument('--snapshot',type=Path);a=p.parse_args()
    if a.child:
        if not a.snapshot:p.error('Internal child requires snapshot')
        child_run(a.child,a.snapshot.resolve(),a.out.resolve());return 0
    if not a.artifact_sha256 or not re.fullmatch(r'[0-9a-fA-F]{64}',a.artifact_sha256):p.error('--artifact-sha256 requires the exact sealed candidate SHA-256')
    if not a.development and not a.artifact:p.error('Publication validation requires --artifact exact sealed ZIP, not only a caller hash')
    if a.identity_only and not a.development:p.error('--identity-only is development-only and cannot approve publication')
    return validate(a)


if __name__=='__main__':raise SystemExit(main())
