"""Root-only closed Native/world/bridge sealing. No owner, Native or MCP calls.

Hash an external immutable world+Native component anchor BEFORE bridge binding.
Bind only the proved closed original bridge, then copy its post-binding bytes
once into the final sealed pair. The pair manifest is never edited afterwards.
The same Native root/life remains the resume destination; no memories are moved.
"""
from pathlib import Path
import argparse,datetime,hashlib,importlib.util,json,os,sqlite3,sys
ROOT=Path(__file__).resolve().parents[1]

def need(x,message):
    if not x:raise ValueError(message)
def load(relative,name):
    spec=importlib.util.spec_from_file_location(name,ROOT/relative)
    m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m);return m
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def sha(p):
    value=hashlib.sha256()
    with Path(p).open('rb')as f:
        for block in iter(lambda:f.read(1048576),b''):value.update(block)
    return value.hexdigest()
def write(p,value):
    with Path(p).open('x',encoding='utf8')as f:
        json.dump(value,f,ensure_ascii=False,indent=2,allow_nan=False);f.write('\n');f.flush();os.fsync(f.fileno())
def utc():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def safe(p,exists=True):
    p=Path(p).absolute()
    for part in(p,*p.parents):
        need(not part.is_symlink()and not(part.exists()and getattr(part.lstat(),'st_file_attributes',0)&1024),'No linked/reparse checkpoint paths')
    p=p.resolve(strict=exists);need(p.is_relative_to(ROOT),'C02 subtree only');return p
def native_manifest(root,persistence):
    rows=[];dirs=[];total=0
    for item in sorted(root.rglob('*')):
        safe(item);relative=item.relative_to(root).as_posix()
        if item.is_dir():dirs.append(relative)
        elif item.is_file():
            size=item.stat().st_size;rows.append({'file':relative,'bytes':size,'sha256':sha(item)});total+=size
        else:raise ValueError('Nonregular Native component')
    need(len(rows)<=persistence.MAX_MEMBERS and total<=persistence.MAX_BYTES,'Finite whole-Native component bound')
    return {'schema':'DEE.RBX01.C02.closed_native_component.R01','root_locator':str(root),
            'files':rows,'directories':dirs,'bytes':total,'new_Native_ticks':0}
def bridge_semantics(path):
    """Closed immutable RO fingerprint of all scientific protocol tables."""
    con=sqlite3.connect(path.as_uri()+'?mode=ro&immutable=1',uri=True);con.row_factory=sqlite3.Row
    try:
        need(con.execute('PRAGMA integrity_check').fetchone()[0]=='ok','Closed bridge integrity')
        tables={r[0]for r in con.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        need({'session','boundary','operation','request','observation','action','tool_call','checkpoint_binding'}<=tables,'Full C02 bridge schema required')
        result={}
        for name in('session','boundary','operation','request','observation','action','tool_call'):
            rows=[dict(r)for r in con.execute('SELECT *FROM '+name+' ORDER BY rowid')]
            text=json.dumps(rows,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False)
            result[name]={'rows':len(rows),'sha256':hashlib.sha256(text.encode('utf8')).hexdigest()}
        session=con.execute('SELECT *FROM session LIMIT 1').fetchone();boundary=con.execute('SELECT *FROM boundary LIMIT 1').fetchone()
        binding=con.execute('SELECT *FROM checkpoint_binding LIMIT 1').fetchone()
        need(session and boundary,'Exact suspended session/boundary required')
        return result,dict(session),dict(boundary),dict(binding)if binding else None
    finally:con.close()

def verify(output,persistence=None):
    persistence=persistence or load('control/persistencia_C02.py','_C02_seal_verify_codec')
    output=safe(output);closure=read(output/'SELLADO_VINCULO_C02.json')
    for name,row in closure['audit_members'].items():
        file=safe(output/name);need(file.stat().st_size==row['bytes']and sha(file)==row['sha256'],'Closed sealing member changed: '+name)
    pair=persistence.verify_pair(output/'PAREJA_C02')
    need(pair['manifest_sha256']==closure['pair_manifest_sha256'],'Final pair manifest changed')
    anchor=read(output/'ANCHOR_MUNDO_NATIVE_C02.json')
    need(sha(output/'ANCHOR_MUNDO_NATIVE_C02.json')==closure['bound_checkpoint_sha256'],'Anchor changed')
    world=read(output/'PAREJA_C02/WORLD_CHECKPOINT.json')
    need(sha(output/'PAREJA_C02/WORLD_CHECKPOINT.json')==anchor['world_sha256'],'Paired world differs from external anchor')
    need(sha(output/'NATIVE_COMPONENTE_C02.json')==anchor['native_component_manifest_sha256'],'Native component manifest changed')
    component=read(output/'NATIVE_COMPONENTE_C02.json')
    for row in component['files']:
        f=safe(output/'PAREJA_C02/native_root'/row['file'])
        need(f.stat().st_size==row['bytes']and sha(f)==row['sha256'],'Native backup differs from full component anchor')
    _,session,_,binding=bridge_semantics(output/'PAREJA_C02/BRIDGE.sqlite3')
    need(binding and binding['checkpoint_id']==world['checkpoint_id']and binding['checkpoint_sha256']==closure['bound_checkpoint_sha256'],'Paired bridge binding mismatch')
    config=safe(closure['resume_config']);need(sha(config)==closure['resume_config_sha256'],'Resume config changed')
    return {'status':'SEALED_BOUND_VERIFIED_NOT_REOPENED','pair':pair,'anchor_sha256':closure['bound_checkpoint_sha256'],
            'session_id':session['id'],'server_id':session['server_id'],'resume_arguments':closure['resume_arguments'],
            'Native_imported':False,'new_Native_ticks':0,'MCP_calls':0}

def seal(args,persistence=None,bridge=None):
    need(args.root_run,'Explicit Root-only operation required')
    persistence=persistence or load('control/persistencia_C02.py','_C02_seal_codec')
    bridge=bridge or load('puente/rbx02_bridge_C02.py','_C02_seal_closed_binder')
    native,world_path,database,proof_path,config_path=map(safe,(args.native_root,args.world_file,args.bridge_database,args.close_proof,args.config))
    output=safe(args.output,exists=False);resume=safe(args.resume_config,exists=False)
    need(not output.exists()and not resume.exists(),'New output and resume config required; never overwrite')
    need(not output.is_relative_to(native)and not native.is_relative_to(output),'Pair output cannot contain/be inside operational Native root')
    need(config_path.parent==resume.parent==ROOT/'configuracion_privada','Original/new private configuration paths only')
    config=read(config_path)
    need(config.get('apiVersion')=='RBX01.C02.v1'and config.get('bind')=='127.0.0.1'and config.get('port')==8895 and
         config.get('allowControl')is False and config.get('requestsPerMinute')in range(1,61),'Closed Native C02 private config required')
    need((config_path.parent/config['databaseFile']).resolve()==database,'Resume must use exact same closed bridge database')
    token=config.get('tokenFile');need(isinstance(token,str)and Path(token).name==token,'Keep same private token basename; never copy/read bearer')
    world=read(world_path);boundary=persistence.validate_world(world);life=boundary['life']
    card=persistence.closed_native_root(native,life);persistence.check_close(read(proof_path),life)
    ledger_path=safe(args.ledger);ledger=read(ledger_path);budget_world=ledger.get('worlds',{}).get(life,{})
    need(ledger.get('schema')=='DEE.RBX01.C02.prospective_native_budget.R01'and ledger.get('limit')==200000 and
         ledger.get('max_worlds')==6 and ledger.get('intent')is None and budget_world.get('reserved')==0 and
         budget_world.get('cycles')==boundary['completed'],'Aggregate ledger is not the matching settled opportunity boundary')
    ledger_sha=sha(ledger_path)
    need(card['physical']['tick']==boundary['tick'],'Native/world tick mismatch')
    need(world['world_id']==config['worldId'],'World/config identity mismatch')
    persistence.check_sqlite(database,bridge=True)
    before,session,b,existing=bridge_semantics(database)
    need(existing is None and session['status']=='SUSPENDED_BOUNDARY'and session['phase']=='READY_QUERY','New unbound suspended bridge only')
    need(session['id']==world['bridge']['session_id']and session['server_id']==world['bridge']['server_id']and
         session['last_action_id']==world['boundary']['last_action_id']and b['completed_cycles']==boundary['completed']and
         b['next_opportunity']==boundary['next_opportunity']and b['feedback_operation_id']==world['boundary']['last_feedback_operation_id'],
         'World/Native/bridge cursor, feedback or logical IDs differ')
    need(session['ticks']==world['bridge']['native_ticks_in_session'],'Bridge tick accounting mismatch')
    component=native_manifest(native,persistence)
    output.mkdir(parents=True)
    binding=None
    try:
        write(output/'NATIVE_COMPONENTE_C02.json',component)
        write(output/'LEDGER_CORTE_NO_RESTAURAR_C02.json',ledger)
        anchor={'schema':'DEE.RBX01.C02.external_world_native_anchor.R01','checkpoint_id':world['checkpoint_id'],
                'life_id':life,'native_tick':boundary['tick'],'native_snapshot_sha256':card['snapshot_sha256'],
                'world_sha256':sha(world_path),'native_component_manifest_sha256':sha(output/'NATIVE_COMPONENTE_C02.json'),
                'bridge_before_binding_sha256':sha(database),'owner_closed_proof_sha256':sha(proof_path),
                'ledger_cut_sha256':sha(output/'LEDGER_CORTE_NO_RESTAURAR_C02.json'),
                'scenario_sha256':world['scenario_sha256'],'session_id':session['id'],'server_id':session['server_id'],
                'completed_opportunities':boundary['completed'],'next_opportunity':boundary['next_opportunity'],
                'hash_rule':'External anchor excludes post-binding DB and final pair manifest; no self-reference.',
                'Native_imported':False,'new_Native_ticks':0}
        write(output/'ANCHOR_MUNDO_NATIVE_C02.json',anchor);anchor_sha=sha(output/'ANCHOR_MUNDO_NATIVE_C02.json')
        binding=bridge.bind_checkpoint(database,world['checkpoint_id'],anchor_sha,
                                       pair_manifest_sha256=sha(output/'NATIVE_COMPONENTE_C02.json'))
        write(output/'BINDING_C02.json',binding)
        after,s2,b2,bound=bridge_semantics(database)
        need(before==after and session==s2 and b==b2,'Binding altered protocol history/identity/cursor')
        need(bound and bound['checkpoint_id']==world['checkpoint_id']and bound['checkpoint_sha256']==anchor_sha,'Closed binding mismatch')
        need(native_manifest(native,persistence)==component,'Native root changed concurrently during binding')
        pair=persistence.create_closed_system_pair(native,world_path,database,proof_path,output/'PAREJA_C02')
        need(native_manifest(native,persistence)==component,'Native root changed concurrently during pair copy')
        need(sha(ledger_path)==ledger_sha,'Aggregate ledger changed concurrently; preserve sealed files without resuming')
        # New config references original same DB/token. No session reset,
        # no counter reset, no expiry extension and no Native root transplant.
        resumed={**config,'resumeAllowed':True};write(resume,resumed)
        resume_args={'world_checkpoint':str(output/'PAREJA_C02/WORLD_CHECKPOINT.json'),
                     'world_checkpoint_sha256':sha(output/'PAREJA_C02/WORLD_CHECKPOINT.json'),
                     'bound_checkpoint_sha256':anchor_sha}
        audit={p.name:{'bytes':p.stat().st_size,'sha256':sha(p)}for p in output.iterdir()if p.is_file()}
        result={'schema':'DEE.RBX01.C02.sealed_bound_same_root.R01','utc':utc(),'status':'SEALED_BOUND_NOT_REOPENED',
                'native_root_resume_in_place':str(native),'life_id':life,'native_tick':boundary['tick'],
                'pair_manifest_sha256':pair['manifest_sha256'],'bound_checkpoint_sha256':anchor_sha,
                'resume_config':str(resume),'resume_config_sha256':sha(resume),'resume_arguments':resume_args,
                'session_id':session['id'],'server_id':session['server_id'],'next_opportunity':boundary['next_opportunity'],
                'Native_imported':False,'MCP_calls':0,'new_Native_ticks':0,'audit_members':audit,
                'material_reopen_tested':False,'global_ledger_rewound':False,
                'changed_originals':'Closed bridge only: declared checkpoint_binding/audit. Native files unchanged. New resume config, original config retained.'}
        write(output/'SELLADO_VINCULO_C02.json',result)
        verified=verify(output,persistence)
        write(output/'VERIFICACION_C02.json',verified)
        return verified
    except BaseException as error:
        write(output/'INCOMPLETE_PRESERVED_C02.json',{'error_type':type(error).__name__,'detail':str(error),
            'binding_completed':binding is not None,'binding_receipt':binding,'no_automatic_rebind_or_retry':True,
            'Native_owner_started':False,'new_Native_ticks':0})
        raise

def parser():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--root-run',action='store_true')
    p.add_argument('--verify-only',type=Path)
    p.add_argument('--ledger',type=Path,default=ROOT/'control/LEDGER_C02.json',help='Shared cumulative budget is read/copied for evidence, never rewound')
    for name in('native-root','world-file','bridge-database','close-proof','config','output','resume-config'):
        p.add_argument('--'+name,type=Path)
    return p
if __name__=='__main__':
    args=parser().parse_args()
    if args.verify_only:result=verify(args.verify_only)
    else:
        need(all(getattr(args,key)is not None for key in('native_root','world_file','bridge_database','close_proof','config','output','resume_config')),'All seven explicit paths required')
        result=seal(args)
    print(json.dumps(result,ensure_ascii=False,indent=2))
