"""Full CLOSED Native-root + World pair, no Native/runtime/export operation.

Default check-only may read CLOSED SQLite immutable/query-only after the exact
owner-close proof and absence of life locks. Only Root --seal-root-only copies.
One physical copy, hash manifests and empty directories; shared motor stays out.
"""
from pathlib import Path
import argparse,collections,hashlib,importlib.util,json,os,shutil,sqlite3,sys,time
ROOT=Path(__file__).resolve().parents[1];PRODUCT=ROOT.parents[2]
LIFE='ECI02_PI03_REPRO_PI04_PI05_PI07_PI10_RBX01_INTEGRAL_V3_MAIN'
def need(ok,msg):
    if not ok:raise ValueError(msg)
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb')as f:
        for block in iter(lambda:f.read(1048576),b''):h.update(block)
    return h.hexdigest()
def load(path,name):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m);return m
def new_json(p,value):
    with p.open('x',encoding='utf8')as f:json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
def resources():
    paths=['motor/DEPENDENCIAS_DISTRIBUCION_ORIGEN.json','motor/python313/python.exe','motor/python313/python313.dll',
           'motor/python313/python313.zip','motor/python313/site-packages/dee_thinking/_native.cp313-win_amd64.pyd',
           'motor/python313/site-packages/dee_thinking-4.5.0.dist-info/METADATA','reproducibilidad/propietario_diagnostico.py']
    return [dict(path=str(PRODUCT/name),bytes=(PRODUCT/name).stat().st_size,sha256=sha(PRODUCT/name))for name in paths]
def check_closed(native,world_file,closure_file,ledger_file):
    native=native.resolve(strict=True)
    need(native==ROOT/'native/MAIN','Only the isolated R07 MAIN root; never product/principal or another root')
    world,closure,ledger=map(read,(world_file,closure_file,ledger_file))
    need(closure.get('schema')=='DEE.RBX01.R07.integrated.result.R01'and closure.get('owner_closed')is True,'Actual closed block result required')
    need(closure['identity']['life']==LIFE and closure['world_sha256']==sha(world_file),'Closure/World exact identity and bytes')
    validation=load(ROOT.parent/'revision_R05_C02/control/persistencia_C02.py','_r06_closed_world_validator')
    boundary=validation.validate_world(world)
    need(boundary['life']==LIFE and boundary['tick']==closure['final_tick'],'Same complete Native/World cut')
    need(ledger.get('limit')==160000 and ledger.get('max_worlds')==6 and isinstance(ledger.get('intents'),dict),'Actual global R07 ledger')
    need(not ledger['intents'],'Pending Native intents cannot be sealed as closed')
    system=native/'sistema';card_path=system/'estado/vidas'/LIFE/'VIDA.json';card=read(card_path)
    need(card['life_id']==card['world_id']==LIFE and card['physical']['tick']==boundary['tick'],'Native current card identity/tick')
    need(not(system/'estado/ACTIVO.json').exists(),'Selected systems refused')
    need(not(card_path.parent/'FUTURO_INTERRUMPIDO.json').exists()and not(system/'estado/locks'/(LIFE+'.lock')).exists(),'Live/interrupted future or writer lock preserved')
    snapshot=system/card['snapshot'];need(snapshot.resolve().is_relative_to(system),'Snapshot inside isolated system')
    need(snapshot.is_file()and sha(snapshot)==card['snapshot_sha256'],'Complete current snapshot/card match')
    history=card_path.parent/'HISTORIA.jsonl'
    if history.exists():
        last=None
        for line in history.read_text(encoding='utf8').splitlines():
            if line.strip():last=json.loads(line)
        need(last and last.get('snapshot_sha256')==card['snapshot_sha256'],'Last saved history and snapshot pointer differ')
    started=None;closed=None
    with(native/'ENSAYOS.jsonl').open(encoding='utf8')as f:
        for line in f:
            if not line.strip():continue
            row=json.loads(line)
            if row.get('kind')=='OWNER_STARTED'and row.get('life')==LIFE:started=row;closed=None
            elif row.get('kind')=='OWNER_CLOSED'and row.get('life')==LIFE:closed=row
    need(started is not None and closed is not None and started['run']==closed['run']and started['pid']==closed['pid'],'Latest exact owner has no subsequent unmatched start')
    cache=closed.get('final_status',{})
    need(closed.get('exit_code')==0 and cache.get('running')is False and cache.get('uncertain_external_result',False)is False,'Owner cleanly exited and future certain')
    need(cache.get('life_id')==LIFE and cache.get('tick')==boundary['tick'],'Owner cache matches paired life/tick')
    queue=system/'estado/servicios_persistentes'/LIFE/'cola.sqlite3'
    wal=Path(str(queue)+'-wal');need(not wal.exists()or wal.stat().st_size==0,'Nonempty WAL: preserve and use coherent closed checkpoint mechanism before sealing; do not ignore/discard frames')
    before=sha(queue)
    con=sqlite3.connect(queue.resolve().as_uri()+'?mode=ro&immutable=1',uri=True)
    try:
        con.execute('PRAGMA query_only=ON');need(con.execute('PRAGMA quick_check').fetchone()[0]=='ok','Closed queue integrity')
        counts=dict(con.execute('SELECT status,count(*) FROM requests GROUP BY status'))
        need(not any(counts.get(x,0)for x in('queued','processing','uncertain')),'Closed queue still contains pending/uncertain requests')
        entry=con.execute("SELECT value FROM meta WHERE key='owner'").fetchone();need(entry is not None,'Closed Native owner cache absent')
        actual=json.loads(entry[0]);need(actual.get('running')is False and actual.get('life_id')==LIFE and actual.get('tick')==boundary['tick']and actual.get('uncertain_external_result',False)is False,'Immutable queue cache does not match close proof')
    finally:con.close()
    need(sha(queue)==before,'Read-only closed queue bytes changed concurrently')
    return dict(life_id=LIFE,native_tick=boundary['tick'],completed_opportunities=boundary['completed'],next_opportunity=boundary['next_opportunity'],
        checkpoint_id=world['checkpoint_id'],scenario_sha256=world['scenario_sha256'],world_id=world['world_id'],
        native_snapshot_sha256=card['snapshot_sha256'],native_physical=card['physical'],
        last_owner_close=closed,queue=dict(path=str(queue),sha256=before,status_counts=counts,immutable_read=True),
        global_ledger_sha256=sha(ledger_file),world_sha256=sha(world_file),closure_sha256=sha(closure_file),
        Native_imports=0,new_ticks=0,MCP_calls=0,closed_SQLite_only=True)
def verify_pair(directory):
    directory=directory.resolve(strict=True);record=read(directory/'PAREJA_INTEGRAL_V3.json')
    need(record['schema']=='DEE.RBX.IntegralV3.ClosedPair.R01','Exact paired manifest')
    seen=set()
    for row in record['members']:
        name=row['file'];need(not Path(name).is_absolute()and '..'not in Path(name).parts and name not in seen,'Safe unique member');seen.add(name)
        path=directory/name;need(path.is_file()and path.stat().st_size==row['bytes']and sha(path)==row['sha256'],'Pair member differs: '+name)
    paths=load(ROOT.parent/'revision_R05_C02/control/path_guard_C02_R03.py','_r06_pair_verify_paths');guard=paths.PathGuard(directory)
    found=paths.scan_files(directory,guard,sha,30000,1500000000)
    need({x['file']for x in found['files']}==seen|{'PAREJA_INTEGRAL_V3.json'},'Pair has missing/extra files')
    need({x for x in found['directories']if x.startswith('native_root/')}=={'native_root/'+x for x in record['native_directories']},'Empty directory set differs')
    return dict(status='FULL_FILES_HASHED_NOT_MATERIAL_REOPEN',life_id=record['boundary']['life_id'],native_tick=record['boundary']['native_tick'],
        members=len(seen),manifest_sha256=sha(directory/'PAREJA_INTEGRAL_V3.json'),new_Native_ticks=0)
def run(a):
    if a.verify:return verify_pair(a.verify)
    need(all((a.native_root,a.world,a.closure,a.ledger)),'Explicit closed sources required')
    started=time.monotonic();boundary=check_closed(a.native_root,a.world,a.closure,a.ledger)
    if not a.seal_root_only:return dict(status='CLOSED_PREFLIGHT_ONLY_NO_COPY',boundary=boundary)
    need(a.destination is not None,'Fresh pair destination required')
    destination=a.destination.absolute();need(destination.resolve().is_relative_to(ROOT/'evidencia')and not destination.exists(),'Fresh evidence pair outside operational Native root')
    paths=load(ROOT.parent/'revision_R05_C02/control/path_guard_C02_R03.py','_r06_closed_paths');guard=paths.PathGuard(ROOT)
    native=guard.safe(a.native_root);source=paths.scan_files(native,guard,sha,30000,1500000000)
    shared=resources();destination.mkdir(parents=True);copied=[]
    try:
        (destination/'native_root').mkdir()
        for name in source['directories']:(destination/'native_root'/name).mkdir(parents=True,exist_ok=True)
        for row in source['files']:
            src=native/row['file'];dest=destination/'native_root'/row['file'];dest.parent.mkdir(parents=True,exist_ok=True)
            shutil.copyfile(src,dest);need(sha(dest)==row['sha256'],'Closed copy differs; partial pair preserved')
            copied.append(dict(file='native_root/'+row['file'],bytes=row['bytes'],sha256=row['sha256']))
        for path,name in((a.world,'WORLD_CHECKPOINT.json'),(a.closure,'CIERRE_BLOQUE_ORIGINAL.json'),(a.ledger,'LEDGER_V3_AL_CORTE.json')):
            dest=destination/name;shutil.copyfile(path,dest);copied.append(dict(file=name,bytes=dest.stat().st_size,sha256=sha(dest)))
        proof=destination/'CIERRE_CONCILIADO.json';new_json(proof,boundary);copied.append(dict(file=proof.name,bytes=proof.stat().st_size,sha256=sha(proof)))
        source_after=paths.scan_files(native,guard,sha,30000,1500000000)
        need(source_after['files']==source['files']and source_after['directories']==source['directories'],'Source changed during seal; do not reopen/overwrite partial pair')
        again=check_closed(native,a.world,a.closure,a.ledger);need(again==boundary,'Closed Native/World/ledger boundary changed during seal')
        need(resources()==shared,'Shared official runtime changed during seal')
        guard.recheck()
        record=dict(schema='DEE.RBX.IntegralV3.ClosedPair.R01',storage_mode='FULL_CLOSED_NATIVE_ROOT_NO_ENGINE_DUPLICATE',
            boundary=boundary,native_source_root=str(native),native_source_bytes=source['bytes'],native_directories=source['directories'],members=copied,
            shared_read_only_runtime=shared,transport='DIRECT_ROOT_MCP_NO_HTTP_BRIDGE_DATABASE',
            included='Whole experimental root: snapshots, clocks encoded by snapshot, queues/SQLite+present auxiliaries, interfaces, agenda, receipts,outbox/results,artifacts,contracts,source scopes and empty directories; whole World contains RNG,environment,pose,products,cursors and action dedup.',
            restore_rule='Use same existing life/root continuation with its coherent pair. This backup does not grant an automatic relocated importer or rewinding global budget. No full-root copy is needed for every later reopen.',
            source_all_file_hashes_before_after_equal=True,Native_imports=0,new_Native_ticks=0,MCP_calls=0,
            material_reopen_tested=False,elapsed_seconds=time.monotonic()-started,path_checks=guard.stats())
        new_json(destination/'PAREJA_INTEGRAL_V3.json',record)
        return verify_pair(destination)
    except BaseException as error:
        if not(destination/'INCOMPLETE_PRESERVED.json').exists():new_json(destination/'INCOMPLETE_PRESERVED.json',dict(error=type(error).__name__+': '+str(error),no_automatic_retry=True,originals_modified=False))
        raise
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--seal-root-only',action='store_true');p.add_argument('--verify',type=Path)
    p.add_argument('--native-root',type=Path);p.add_argument('--world',type=Path);p.add_argument('--closure',type=Path);p.add_argument('--ledger',type=Path);p.add_argument('--destination',type=Path)
    print(json.dumps(run(p.parse_args()),ensure_ascii=False,indent=2))
