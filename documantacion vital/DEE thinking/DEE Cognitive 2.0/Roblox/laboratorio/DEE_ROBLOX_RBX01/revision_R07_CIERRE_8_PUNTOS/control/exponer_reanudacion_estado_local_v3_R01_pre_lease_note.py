"""Describe ONLY explicitly supplied CLOSED R07 metadata. Stdlib, no DEE/DB/MCP/process API.
Does not resume, submit, replay, select, copy or promote a world.
"""
from pathlib import Path
import argparse,datetime,hashlib,json,os,sys
HERE=Path(__file__).resolve().parents[1]
MAIN='ECI02_PI03_REPRO_PI04_PI05_PI07_PI10_RBX01_INTEGRAL_V3_MAIN'
LIMIT=8_000_000

def need(value,message):
    if not value:raise ValueError(message)
def sha(raw):return hashlib.sha256(raw).hexdigest()
def safe(path):
    path=Path(path);path=(path if path.is_absolute()else HERE/path).resolve(strict=True)
    need(path.is_relative_to(HERE),'Metadata must be inside this R07/extracted dossier root')
    need(path.suffix=='.json','Only explicit JSON metadata, never SQLite/snapshot/RAW')
    for part in(path,*path.parents):
        need(not part.is_symlink()and not(getattr(part.lstat(),'st_file_attributes',0)&0x400),'Links/reparse points refused')
        if part==HERE:break
    return path
def read(path):
    path=safe(path);before=path.stat()
    need(before.st_size<=LIMIT,'Bounded metadata required')
    raw=path.read_bytes();after=path.stat()
    need((before.st_size,before.st_mtime_ns)==(after.st_size,after.st_mtime_ns),'Metadata changed while reading')
    document=json.loads(raw.decode('utf-8-sig'),parse_constant=lambda value:(_ for _ in()).throw(ValueError('NonfiniteJSON')))
    return document,{'path':str(path),'relative_path':str(path.relative_to(HERE)).replace('\\','/'),'bytes':len(raw),'sha256':sha(raw)}

def expose(closure_paths,pair_path,expected_life=MAIN,allow_fixture=False):
    need(1<=len(closure_paths)<=4,'One to four explicit closed blocks in chronological order')
    records=[];sources=[];last=None;seen_cycles=set();session=None;fixture=False
    for path in closure_paths:
        d,source=read(path);sources.append(source)
        fixture=fixture or bool(d.get('offline_fixture'))
        need(not d.get('offline_fixture')or allow_fixture,'Offline fixture is NOT a material closed result')
        need(d.get('schema')=='DEE.RBX01.R07.integrated.result.R01','Exact R07 closure schema')
        need(d.get('owner_closed')is True,'Actual owner_closed:true required; do not infer closure from file availability')
        identity=d.get('identity',{})
        need(identity.get('life')==expected_life,'Do not merge or select a different life')
        need(identity.get('participant')=='LIVE_NATIVE','Reference backend is not Native')
        need(isinstance(identity.get('session'),str)and identity['session'],'Explicit session identity')
        if session is None:session=identity['session']
        need(identity['session']==session,'Logical session differs')
        rows=d.get('rows',[]);need(isinstance(rows,list),'Rows must be a list')
        need(type(d.get('new_opportunities_completed'))is int and len(rows)==d['new_opportunities_completed'],'Actual row count differs')
        need(type(d.get('source_tick'))is int and type(d.get('final_tick'))is int,'Actual tick integers required')
        need(d['final_tick']>=d['source_tick'],'Invalid tick chronology')
        need(d.get('new_Native_ticks')==d['final_tick']-d['source_tick'],'Tick delta differs')
        if last is not None:need(d['source_tick']==last['final_tick'],'Explicit blocks do not share one consecutive physical cut')
        cycles=[r['cycle']for r in rows]
        need(all(type(c)is int for c in cycles)and cycles==sorted(cycles),'Ordered actual cycles')
        need(not(seen_cycles&set(cycles)),'Repeated prefix/alias is not new experience')
        need(len(cycles)==len(set(cycles)),'Duplicate cycles in one result')
        seen_cycles.update(cycles)
        if cycles:need(cycles[-1]==d['global_completed'],'Final cycle differs')
        need(isinstance(d.get('world_sha256'),str)and len(d['world_sha256'])==64,'Exact World hash required')
        records.append({'source':source,'identity':identity,'source_tick':d['source_tick'],'final_tick':d['final_tick'],
            'new_opportunities_completed':len(rows),'cycles':cycles,'new_Native_ticks':d['new_Native_ticks'],
            'global_completed':d['global_completed'],'world_path_reported':d.get('world_checkpoint'),
            'world_sha256_reported':d['world_sha256'],'owner_closed_reported':True})
        last=d
    pair,pair_source=read(pair_path);fixture=fixture or bool(pair.get('offline_fixture'))
    need(not pair.get('offline_fixture')or allow_fixture,'Offline pair fixture is not an executable state')
    need(pair.get('schema')=='DEE.RBX.IntegralV3.ClosedPair.R01','Exact full-pair manifest schema')
    boundary=pair.get('boundary',{})
    need(boundary.get('life_id')==expected_life and boundary.get('native_tick')==last['final_tick'],'Pair/closed-result life or cut differs')
    need(boundary.get('world_sha256')==last['world_sha256'],'Pair/finalWorld SHA differs')
    members=pair.get('members',[]);need(isinstance(members,list)and members,'Whole-pair member map required')
    names=set()
    for row in members:
        name=row.get('file')
        need(isinstance(name,str)and not Path(name).is_absolute()and '..'not in Path(name).parts and name not in names,'Safe distinct pair member required')
        names.add(name)
    need('WORLD_CHECKPOINT.json'in names and 'CIERRE_CONCILIADO.json'in names,'Native+World pair components missing from manifest')
    need(pair.get('source_all_file_hashes_before_after_equal')is True,'Actual sealer byte-preservation proof required')
    now=datetime.datetime.now(datetime.timezone.utc)
    cutoff=datetime.datetime(2026,11,16,20,0,tzinfo=datetime.timezone.utc)
    report={'schema':'DEE.R07.closed_metadata_exposition.v1','UTC':now.isoformat(),
        'status':'OFFLINE_FIXTURE_ONLY'if fixture else 'EXPLICIT_CLOSED_CUT_DESCRIBED_NOT_EXECUTED',
        'life_id':expected_life,'logical_session':session,'last_supplied_closed_tick':last['final_tick'],
        'global_completed_reported':last['global_completed'],'new_rows_in_supplied_blocks':sum(r['new_opportunities_completed']for r in records),
        'new_ticks_in_supplied_blocks_reported':sum(r['new_Native_ticks']for r in records),
        'closed_blocks':records,'pair_manifest':pair_source,
        'pair_native_source_root_reported':pair.get('native_source_root'),
        'pair_storage_directory':str(safe(pair_path).parent),'pair_members_reported':len(members),
        'N_and_physics_reported':boundary.get('native_physical'),
        'native_snapshot_sha256_reported':boundary.get('native_snapshot_sha256'),
        'world_id_reported':boundary.get('world_id'),'checkpoint_id_reported':boundary.get('checkpoint_id'),
        'scenario_sha256_reported':boundary.get('scenario_sha256'),
        'next_opportunity_reported':boundary.get('next_opportunity'),
        'whole_pair_hash_validation_reported_by_sealer':True,
        'whole_pair_members_rehashed_by_this_tool':False,'SQLite_opened_by_this_tool':False,
        'material_reopen_tested_flag_on_this_pair':pair.get('material_reopen_tested'),
        'subsequent_closed_block_after_owner_close':len(records)>1,
        'reopen_scope_note':'Consecutive closed blocks and matching ticks are metadata evidence. They do not by themselves verify every restored byte or retained function; consult actual reopen/use primaries.',
        'shared_runtime_locators_reported':pair.get('shared_read_only_runtime',[]),
        'current_live_owner_or_principal_selection_inspected':False,'automatic_resume_or_promotion':False,
        'Native_MCP_model_or_process_calls':0,'originals_modified':False,
        'window_2026_11_16_new_episode_cutoff_expired':now>=cutoff,
        'continuation_note':'Use the existing same-life coherent pair and its actual current contract. Never re-createT0, mix branches, replay ambiguous IDs or treat an old deadline as permission for new episodes.',
        'no_material_command_executed_or_auto_generated':True,
        'read_only_command_example':[sys.executable,'-I','-B',str(HERE/'control/exponer_reanudacion_estado_local_v3.py'),'--help'],
        'not_an_executable_backup':'This report and a small analysis ZIP do not contain all listed states/runtime. Large files remain at the declared local pair/runtime paths.'}
    return report

def cli():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--closure',type=Path,action='append',required=True,help='Explicit owner-closed RESULTADO JSON, chronological; repeat for closed reopen block')
    p.add_argument('--pair-manifest',type=Path,required=True)
    p.add_argument('--expected-life',default=MAIN)
    p.add_argument('--output',type=Path)
    a=p.parse_args();report=expose(a.closure,a.pair_manifest,a.expected_life)
    raw=(json.dumps(report,ensure_ascii=False,indent=2)+'\n').encode('utf8')
    if a.output:
        out=a.output.resolve();need(out.is_relative_to(HERE/'control')and not out.exists(),'NEW control output only')
        out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(raw)
    print(raw.decode('utf8'))
if __name__=='__main__':cli()
