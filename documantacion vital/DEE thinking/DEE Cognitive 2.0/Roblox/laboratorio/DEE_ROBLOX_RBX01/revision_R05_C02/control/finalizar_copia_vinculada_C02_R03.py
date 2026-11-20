"""Root-only finalization of a completely copied, already-bound closed pair.

Never stops a process, binds again, overwrites a manifest, copies a Native root,
opens an owner or contacts MCP. Root must first establish/record the earlier
sealer's termination. Every original and copied Native file is hashed in full.
"""
from pathlib import Path
import argparse,ctypes,datetime,importlib.util,json,os,sys,time
ROOT=Path(__file__).resolve().parents[1]
def load(relative,name):
    s=importlib.util.spec_from_file_location(name,ROOT/relative);m=importlib.util.module_from_spec(s);sys.modules[name]=m;s.loader.exec_module(m);return m
base=load('control/sellar_vincular_C02.py','_C02_partial_finish_preserved_base')
paths=load('control/path_guard_C02_R03.py','_C02_partial_finish_fast_guard')
def process_stopped(pid):
    k=ctypes.WinDLL('kernel32',use_last_error=True)
    k.OpenProcess.argtypes=[ctypes.c_ulong,ctypes.c_int,ctypes.c_ulong];k.OpenProcess.restype=ctypes.c_void_p
    k.WaitForSingleObject.argtypes=[ctypes.c_void_p,ctypes.c_ulong];k.WaitForSingleObject.restype=ctypes.c_ulong
    k.CloseHandle.argtypes=[ctypes.c_void_p]
    handle=k.OpenProcess(0x100000|0x1000,False,pid)
    if not handle:
        code=ctypes.get_last_error();base.need(code==87,'Cannot establish previous sealer exit Win32='+str(code));return {'pid':pid,'running':False,'method':'OpenProcess invalid PID87'}
    try:
        base.need(k.WaitForSingleObject(handle,0)==0,'Previous sealer still running; finalizer never stops it')
        return {'pid':pid,'running':False,'method':'Process handle signalled'}
    finally:k.CloseHandle(handle)
def finish(args,persistence=None,process_check=None):
    base.need(args.root_run,'Explicit Root-only finalization')
    previous=(process_check or process_stopped)(args.sealer_pid)
    p=persistence or load('control/persistencia_C02.py','_C02_partial_finish_preserved_codec')
    guard=paths.PathGuard(ROOT);start=time.monotonic()
    output=guard.safe(args.output);config_path=guard.safe(args.config);resume=guard.safe(args.resume_config,exists=False)
    base.need(not(output/'SELLADO_VINCULO_C02.json').exists()and not(output/'PAREJA_C02/PAREJA_C02.json').exists()
              and not resume.exists(),'Final metadata already exists; never overwrite/reclassify it')
    component_path=output/'NATIVE_COMPONENTE_C02.json';anchor_path=output/'ANCHOR_MUNDO_NATIVE_C02.json'
    component,anchor,binding=map(base.read,(component_path,anchor_path,output/'BINDING_C02.json'))
    anchor_sha=base.sha(anchor_path);base.need(binding['checkpoint_sha256']==anchor_sha and binding['checkpoint_id']==anchor['checkpoint_id'],'Known binding/anchor mismatch')
    base.need(base.sha(component_path)==anchor['native_component_manifest_sha256'],'Native component manifest changed')
    if'ledger_cut_sha256'in anchor:base.need(base.sha(output/'LEDGER_CORTE_NO_RESTAURAR_C02.json')==anchor['ledger_cut_sha256'],'Historical ledger cut changed')
    native=guard.safe(component['root_locator']);pair=guard.safe(output/'PAREJA_C02')
    expected_root_names={'native_root','WORLD_CHECKPOINT.json','BRIDGE.sqlite3','OWNER_CLOSED.json'}
    base.need({x.name for x in pair.iterdir()}==expected_root_names,'Partial pair shape is incomplete or has unexplained extra entries')
    world=base.read(pair/'WORLD_CHECKPOINT.json');boundary=p.validate_world(world);life=boundary['life']
    base.need(base.sha(pair/'WORLD_CHECKPOINT.json')==anchor['world_sha256'],'World bytes changed')
    base.need(base.sha(pair/'OWNER_CLOSED.json')==anchor['owner_closed_proof_sha256'],'Owner proof bytes changed')
    original_safe=p.safe
    def scoped(path,root=p.ROOT,*,exists=True):
        if Path(root)!=p.ROOT:return original_safe(path,root=root,exists=exists)
        return guard.safe(path,exists=exists)
    p.safe=scoped
    try:
        card=p.closed_native_root(native,life);p.check_close(base.read(pair/'OWNER_CLOSED.json'),life)
        base.need(card['snapshot_sha256']==anchor['native_snapshot_sha256']and card['physical']['tick']==boundary['tick'],'Current Native source differs from known anchor')
        actual=paths.scan_files(native,guard,base.sha,p.MAX_MEMBERS,p.MAX_BYTES)
        base.need(actual==component,'Full original Native file-set/hash differs from anchor')
        copied=paths.scan_files(pair/'native_root',guard,base.sha,p.MAX_MEMBERS,p.MAX_BYTES)
        base.need(copied['files']==component['files']and copied['directories']==component['directories']and copied['bytes']==component['bytes'],'Full Native copied file-set/hash differs')
        config=base.read(config_path);database=guard.safe(ROOT/'configuracion_privada'/config['databaseFile'])
        base.need(config_path.parent==resume.parent==ROOT/'configuracion_privada'and config.get('allowControl')is False and config.get('port')==8895,'Same Native private bridge config required')
        p.check_sqlite(database,bridge=True);p.check_sqlite(pair/'BRIDGE.sqlite3',bridge=True)
        base.need(base.sha(database)==binding['database_after_sha256']==base.sha(pair/'BRIDGE.sqlite3'),'Current bound bridge or copied bridge changed')
        semantics,session,b,bound=base.bridge_semantics(database)
        base.need(bound and bound['checkpoint_sha256']==anchor_sha and bound['checkpoint_id']==world['checkpoint_id']and
                  session['id']==anchor['session_id']==world['bridge']['session_id']and
                  session['server_id']==anchor['server_id']==world['bridge']['server_id']and
                  session['status']=='SUSPENDED_BOUNDARY'and session['phase']=='READY_QUERY'and
                  b['completed_cycles']==boundary['completed']and b['next_opportunity']==boundary['next_opportunity'],
                  'Bound session/sequence/cursor mismatch')
        members=[{'file':'native_root/'+r['file'],'bytes':r['bytes'],'sha256':r['sha256']}for r in copied['files']]
        for name in('WORLD_CHECKPOINT.json','BRIDGE.sqlite3','OWNER_CLOSED.json'):
            file=guard.safe(pair/name);members.append({'file':name,'bytes':file.stat().st_size,'sha256':base.sha(file)})
        members.sort(key=lambda row:Path(row['file']))
        guard.recheck()
        record={'schema':p.SCHEMA,'storage_mode':'CLOSED_NATIVE_ROOT','checkpoint_id':world['checkpoint_id'],
                'life_id':life,'native_tick':boundary['tick'],'world_id':world['world_id'],'scenario_sha256':world['scenario_sha256'],
                'completed_opportunities':boundary['completed'],'next_opportunity':boundary['next_opportunity'],
                'native_source_root_locator':str(native),'native_snapshot_sha256':card['snapshot_sha256'],
                'native_physical':card['physical'],'native_directories':copied['directories'],'members':members,
                'Native_imported':False,'new_native_ticks':0,'restoration_status':'BACKUP_VERIFIED_NOT_MATERIAL_REOPEN_TESTED',
                'shared_dependencies':'Official installed motor and source scopes remain shared/read-only; no absolute source remapping.',
                'budget_rule':'Global cumulative Native budget is not restored or rewound.',
                'technical_finalization':'R03 continued a complete already-bound file copy after its old hash-only sealer was stopped; no rebinding or recopy.'}
        p.write_json(pair/'PAREJA_C02.json',record)
        verification=p.verify_pair(pair)
        resumed={**config,'resumeAllowed':True};base.write(resume,resumed)
        resume_args={'world_checkpoint':str(pair/'WORLD_CHECKPOINT.json'),'world_checkpoint_sha256':base.sha(pair/'WORLD_CHECKPOINT.json'),'bound_checkpoint_sha256':anchor_sha}
        recovery={'schema':'DEE.RBX01.C02.partial_copy_finalization.R03','utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
                  'previous_sealer_process':previous,'new_Native_ticks':0,'MCP_calls':0,'rebound':False,'Native_root_recopied':False,
                  'full_original_files_hashed':len(actual['files']),'full_copied_files_hashed':len(copied['files']),
                  'bridge_scientific_semantics':semantics,'elapsed_seconds':time.monotonic()-start,'path_checks':guard.stats()}
        base.write(output/'CIERRE_RECUPERADO_R03.json',recovery)
        audit={x.name:{'bytes':x.stat().st_size,'sha256':base.sha(x)}for x in output.iterdir()if x.is_file()}
        closure={'schema':'DEE.RBX01.C02.sealed_bound_same_root.R01','utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
                 'status':'SEALED_BOUND_NOT_REOPENED','native_root_resume_in_place':str(native),'life_id':life,'native_tick':boundary['tick'],
                 'pair_manifest_sha256':verification['manifest_sha256'],'bound_checkpoint_sha256':anchor_sha,
                 'resume_config':str(resume),'resume_config_sha256':base.sha(resume),'resume_arguments':resume_args,
                 'session_id':session['id'],'server_id':session['server_id'],'next_opportunity':boundary['next_opportunity'],
                 'Native_imported':False,'MCP_calls':0,'new_Native_ticks':0,'audit_members':audit,
                 'material_reopen_tested':False,'global_ledger_rewound':False,'technical_recovery':'CIERRE_RECUPERADO_R03.json; source original interrupted sealer output retained.'}
        guard.recheck();base.write(output/'SELLADO_VINCULO_C02.json',closure)
        result={'status':'SEALED_BOUND_VERIFIED_NOT_REOPENED','pair':verification,'anchor_sha256':anchor_sha,
                'resume_arguments':resume_args,'Native_imported':False,'new_Native_ticks':0,'MCP_calls':0,
                'elapsed_seconds':time.monotonic()-start,'path_checks':guard.stats()}
        base.write(output/'VERIFICACION_C02.json',result);return result
    finally:p.safe=original_safe
def parser():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--root-run',action='store_true',required=True)
    p.add_argument('--sealer-pid',type=int,required=True)
    for name in('output','config','resume-config'):p.add_argument('--'+name,type=Path,required=True)
    return p
if __name__=='__main__':print(json.dumps(finish(parser().parse_args()),ensure_ascii=False,indent=2))
