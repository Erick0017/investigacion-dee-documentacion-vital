"""ROOT only: archive one inactive RP copy and one closed calibration's sidecars.

Default PLAN reads metadata and current dependency text only. --aplicar performs
lossless local archival, a clean extraction, all-file hashes and SQLite/Native
validation before removing ONLY the three exact authorized directories. Native
life, history and global snapshots remain in place. No DEE imports or ticks.
"""
from pathlib import Path,PurePosixPath
import argparse,datetime,hashlib,json,os,runpy,shutil,sqlite3,subprocess,zipfile

P=Path(__file__).resolve().parents[1];R=P.parents[2];W=P.parents[4]
C=R/'DEE Cognitive 2.0';RP=C/'reproducibilidad';S=P/'estados/candidato/sistema'
LIFE='ECI02_PI03_REPRO_PI04_PI05_PI07_VIAB_MSG_PULSE'
PAIR_NAME='PI07_TRAYECTORIA_R02_28_T846517';PAIR=RP/'materiales'/PAIR_NAME
CAL=S/'estado/vidas'/LIFE;SIDE=S/'estado/servicios_persistentes'/LIFE
WORK=S/'estado/servicios_locales'/LIFE;CARD=CAL/'VIDA.json'
OWNER=P/'control/PI07_VIAB_MSG_PULSE_R01.json';LIMIT=5_500_000_000
A=P/'archivo';ZIP=A/'PI07_R02_28_Y_CAL_MSG_PULSE_CERRADOS_R01.zip'
VERIFY=W/'PI07_ARC_R28_CAL01';PROOF=P/'control/ARCHIVO_R02_28_Y_CAL_MSG_PULSE_PI07_R01.json'
MARKER=CAL/'ARCHIVADO_PI07_R01.json';MANIFEST='MANIFIESTO_ARCHIVO.json'
SUPPORT=P/'codigo/archivar_copias_RP_08_12_PI07_R01.py'
SUPPORT_SHA='53a57e0ff1a2daeceaf98fe9749a12a5f37500ef4abfc48dc7c0c9db6d89f6a6'
OWNER_SHA='ced7674673135b572f433a724064c8573f1fba2de9e6f02fa90d0c7571152390'
CARD_SHA='fdc5b37cdde20d9e4f8a9eac02baab5276ed9045074c2c20eb8e1a18e029915c'
PAIR_MANIFEST_SHA='e5b56aeea7dc5058008fca6e9fe2facd7c92f1e8dfb8e2ac9888a7255ef6460a'


def require(v,message):
    if not v:raise ValueError(message)


def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb')as f:
        for block in iter(lambda:f.read(1048576),b''):h.update(block)
    return h.hexdigest()


def enc(d):return(json.dumps(d,ensure_ascii=False,indent=2)+'\n').encode('utf-8')


def support():
    require(sha(SUPPORT)==SUPPORT_SHA,'Reviewed static support changed')
    return runpy.run_path(str(SUPPORT),run_name='archive_only_static_support')


def dependencies(h):
    rows=h['dependencies']()['checked'];hits=[]
    for row in rows:
        text=Path(row['path']).read_text(encoding='utf-8-sig')
        found=[n for n in(PAIR_NAME,LIFE)if n.casefold()in text.casefold()]
        if found:hits.append({'file':row['path'],'exact_names':found})
    return{'checked':rows,'blocking_current_references':hits,'clear':not hits}


def budget(h):
    total=h['scoped_bytes']()
    if VERIFY.exists():total+=sum(f['bytes']for f in h['listing'](VERIFY)[0])
    return total


def process_absent():
    # The original owner PID is corroborated by its closed run and journal.
    # This query never inspects, stops or selects any other running process.
    command=['powershell.exe','-NoProfile','-NonInteractive','-Command',
      "$p=Get-Process -Id 4232 -ErrorAction SilentlyContinue; if ($null -eq $p) { '{\"pid\":4232,\"present\":false}' } else { '{\"pid\":4232,\"present\":true}' }"]
    q=subprocess.run(command,capture_output=True,text=True,encoding='utf-8',timeout=30,
                     creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
    require(q.returncode==0,'Process query failed; preserve all')
    d=json.loads(q.stdout.strip());require(d=={'pid':4232,'present':False},'Original PID exists or query ambiguous; preserve all')
    return{'queried_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
           'command':command,'actual_result':d,'scope':'Only historical owner PID4232; not a global no-process claim.'}


def cal_validation(root,snapshot,card,parser):
    # All members are frozen files, never a live SQLite backup or Native owner.
    native=parser['parse'](snapshot,card['snapshot_sha256'])[0]
    require(all(native['physical'][k]==card['physical'][k]for k in('N','tick','RAW_sha256','clocks_sha256')),'Calibration snapshot differs from card')
    require(native['pending_count']==0,'Unsettled Native events; no retirement')
    db=root/'cola.sqlite3';wal=Path(str(db)+'-wal')
    require(not wal.exists()or wal.stat().st_size==0,'Nonempty WAL; no retirement')
    before=sha(db);con=sqlite3.connect(db.resolve().as_uri()+'?mode=ro&immutable=1',uri=True)
    try:
        require(con.execute('PRAGMA integrity_check').fetchall()==[('ok',)],'Calibration SQLite integrity failure')
        statuses=dict(con.execute('SELECT status,COUNT(*) FROM requests GROUP BY status'))
        require(set(statuses)<={'completed','rejected_invalid'},'Nonterminal calibration transport request')
        owner=json.loads(con.execute("SELECT value FROM meta WHERE key='owner'").fetchone()[0])
        require(owner.get('life_id')==LIFE and owner.get('running')is False and owner.get('paused')is True
                and owner.get('uncertain_external_result')is False and owner.get('last_saved_tick')==825403
                and owner.get('pid')==4232,'Closed calibration owner cache differs')
    finally:con.close()
    require(sha(db)==before,'Read-only SQLite bytes changed')
    return{'physical':native['physical'],'snapshot_sha256':card['snapshot_sha256'],
      'Native_interfaces':native['interfaces_count'],'Native_pending':native['pending_count'],
      'Native_receipts':native['receipts_count'],'SQLite_sha256':before,'SQLite_integrity':'ok',
      'SQLite_status_counts':statuses,'cached_owner':{k:owner[k]for k in('life_id','pid','running','paused','last_saved_tick','uncertain_external_result')},
      'cache_is_historical_not_instantaneous':True}


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--aplicar',action='store_true');args=ap.parse_args()
    h=support();safe=h['safe_root'];listing=h['listing'];remove=h['remove_exact']
    require(not any(f.exists()for f in(ZIP,ZIP.with_name(ZIP.name+'.writing'),VERIFY,PROOF,MARKER)),'Prior attempt/marker exists; preserve it, do not rerun blindly')
    require(sha(OWNER)==OWNER_SHA and sha(CARD)==CARD_SHA,'Frozen calibration evidence changed')
    require(sha(PAIR/'EXPORTACION_SERVICIO.json')==PAIR_MANIFEST_SHA,'Frozen RP28 manifest changed')
    card=json.loads(CARD.read_text(encoding='utf-8'));owner=json.loads(OWNER.read_text(encoding='utf-8'))
    require(owner['status']=='CLOSED'and owner['closed']is True and owner['life_id']==LIFE
            and owner['final_tick']==825403 and owner['final_snapshot_sha256']==card['snapshot_sha256'],'Original owned close does not match')
    snap=safe(S/card['snapshot']);require(snap.parent==safe(S/'estado/checkpoints'),'Global snapshot location differs')
    require(sha(snap)==card['snapshot_sha256'],'Frozen calibration snapshot changed')
    dep=dependencies(h)
    roots=[{'name':'RP_R02_28','source':PAIR,'retire':True},
           {'name':'CAL_SERVICIO_PERSISTENTE','source':SIDE,'retire':True},
           {'name':'CAL_TRABAJADOR_LOCAL','source':WORK,'retire':True},
           {'name':'CAL_VIDA_HISTORIA','source':CAL,'retire':False}]
    total=0;retired=0;count=1
    for row in roots:
        row['files'],row['directories']=listing(row['source']);b=sum(f['bytes']for f in row['files'])
        row['logical_bytes']=b;total+=b;count+=len(row['files'])
        if row['retire']:retired+=b
    total+=snap.stat().st_size
    if not args.aplicar:
        print(json.dumps({'mode':'READ_ONLY_PLAN','roots':[{'path':str(r['source']),'retire':r['retire'],'files':len(r['files']),'bytes':r['logical_bytes']}for r in roots],
          'extra_snapshot_preserved_source':str(snap),'archive_uncompressed_bytes':total,'retirement_logical_bytes':retired,
          'archive_files':count,'dependency_clear':dep['clear'],'blocking_references':dep['blocking_current_references'],
          'archive':str(ZIP),'writes':0,'Native_ticks':0,'fixed_limit':LIMIT},ensure_ascii=False));return
    require(dep['clear'],'Unresolved current dependency; preserve RP28 and closed calibration')
    process_before=process_absent();before=budget(h);require(before<=LIMIT,'Already beyond5.5GB')
    require(before+int(total*1.01)+count*128+8_000_000<=LIMIT,'No room for bounded lossless archive')
    protected={str(p):sha(p)for p in[OWNER,*sorted(CAL.rglob('*')),*sorted((S/'estado/checkpoints').glob(LIFE+'.*'))]if p.is_file()}
    parser_path=P.parent/'PROGRESION_INTEGRADA_05/codigo/contrastar_prefijos_C2C_PI05_pasivo.py'
    require(sha(parser_path)=='5d84e2a21d6650f1dd69d3c677eb32db0aa9da9f0ae0ed315bb2d0992852124b','Pure parser changed')
    parser=runpy.run_path(str(parser_path),run_name='pure_archive_snapshot_parser')
    native_pair=h['native_and_sqlite'](PAIR);native_cal=cal_validation(SIDE,snap,card,parser)
    safe(A);A.mkdir(exist_ok=True);part=ZIP.with_name(ZIP.name+'.writing');members=[]
    with zipfile.ZipFile(part,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=9,allowZip64=False)as z:
        for root in roots:
            for d in root['directories']:z.writestr(root['name']+('/'+d if d else'')+'/',b'')
            for row in root['files']:
                f=root['source']/row['relative'];s=f.stat();require((s.st_size,s.st_mtime_ns)==(row['bytes'],row['mtime_ns']),'Frozen source changed')
                member=root['name']+'/'+row['relative'];d=hashlib.sha256()
                with f.open('rb')as src,z.open(member,'w')as dst:
                    for chunk in iter(lambda:src.read(1048576),b''):d.update(chunk);dst.write(chunk)
                end=f.stat();require((end.st_size,end.st_mtime_ns)==(s.st_size,s.st_mtime_ns),'Frozen source changed during hash')
                members.append({'file':member,'root':root['name'],'relative':row['relative'],'source':str(f.resolve()),'bytes':row['bytes'],'sha256':d.hexdigest()})
        m='CAL_SNAPSHOT/'+snap.name;z.write(snap,m);members.append({'file':m,'root':'CAL_SNAPSHOT','relative':snap.name,'source':str(snap),'bytes':snap.stat().st_size,'sha256':card['snapshot_sha256']})
        declared=json.loads((PAIR/'EXPORTACION_SERVICIO.json').read_text(encoding='utf-8'))
        indexed={r['relative']:r for r in members if r['root']=='RP_R02_28'}
        require(all(m['file']in indexed and all(indexed[m['file']][k]==m[k]for k in('bytes','sha256'))for m in declared['members']),'Original RP28 paired manifest differs')
        manifest={'schema':'DEE.PI07.inactive_RP28_and_calibration.archive.v1','members':members,
          'roots':[{'name':r['name'],'source':str(r['source'].resolve()),'retire':r['retire'],'directories':r['directories']}for r in roots],
          'RP28_Native_SQLite':native_pair,'calibration_Native_SQLite':native_cal,'source_owner_proof':{'path':str(OWNER),'sha256':OWNER_SHA},
          'self_hash_and_ZIP_hash_excluded':True,'Native_ticks':0,'scope':'Closed copies only; Native life/history/global checkpoints remain at original S7 paths.'}
        z.writestr(MANIFEST,enc(manifest))
    with zipfile.ZipFile(part)as z:require(z.testzip()is None,'ZIP CRC failure')
    part.rename(ZIP);zip_hash=sha(ZIP);before_extract=budget(h)
    require(before_extract+total+8_000_000<=LIMIT,'No room for clean extraction; originals and ZIP preserved')
    VERIFY.mkdir()
    with zipfile.ZipFile(ZIP)as z:
        for info in z.infolist():
            n=PurePosixPath(info.filename);require(not n.is_absolute()and'..'not in n.parts,'Unsafe archive path')
            dst=VERIFY.joinpath(*n.parts);require(dst.resolve().is_relative_to(VERIFY.resolve()),'Extraction escape')
            if info.is_dir():dst.mkdir(parents=True,exist_ok=True);continue
            dst.parent.mkdir(parents=True,exist_ok=True)
            with z.open(info)as src,dst.open('xb')as out:shutil.copyfileobj(src,out,1048576)
    peak=budget(h);require(peak<=LIMIT,'Actual staging beyond5.5GB; preserve all')
    for row in members:
        src=Path(row['source']);dst=VERIFY.joinpath(*PurePosixPath(row['file']).parts)
        require(src.stat().st_size==dst.stat().st_size==row['bytes']and sha(src)==sha(dst)==row['sha256'],'Original/extracted member differs')
    require(h['native_and_sqlite'](VERIFY/'RP_R02_28')==native_pair,'Extracted RP28 state differs')
    extracted_snap=VERIFY/'CAL_SNAPSHOT'/snap.name
    require(cal_validation(VERIFY/'CAL_SERVICIO_PERSISTENTE',extracted_snap,card,parser)==native_cal,'Extracted calibration state differs')
    require(all(sha(f)==v for f,v in protected.items())and dependencies(h)==dep,'Protected files or active dependencies changed')
    process_after=process_absent();require(sha(ZIP)==zip_hash,'Verified ZIP changed')
    removed=[]
    for root in roots:
        if root['retire']:
            remove(root['source'],root['source'],{'files':root['files'],'directories':root['directories']});removed.append(str(root['source'].resolve()))
    expected=[{'relative':m['file'],'bytes':m['bytes']}for m in members]
    expected.append({'relative':MANIFEST,'bytes':(VERIFY/MANIFEST).stat().st_size});remove(VERIFY,VERIFY,{'files':expected})
    require(all(sha(f)==v for f,v in protected.items()),'Life/history/global checkpoints unexpectedly changed')
    with zipfile.ZipFile(ZIP)as z:require(z.testzip()is None,'Post-retirement ZIP CRC failure')
    require(sha(ZIP)==zip_hash,'Post-retirement ZIP changed')
    marker={'schema':'DEE.PI07.closed_calibration_transport.archived.v1','status':'ARCHIVADO',
      'life_id':LIFE,'native_life_history_and_global_snapshots_preserved':True,'latest_tick':825403,
      'latest_snapshot_sha256':card['snapshot_sha256'],'archive':str(ZIP),'archive_sha256':zip_hash,
      'restore_exact_members_before_any_future_owner':{'persistent_service':'CAL_SERVICIO_PERSISTENTE/','worker':'CAL_TRABAJADOR_LOCAL/'},
      'not_current_principal':True,'Native_ticks':0}
    MARKER.write_bytes(enc(marker))
    result={'schema':'DEE.PI07.inactive_RP28_and_calibration.retirement.v1','status':'ARCHIVED_VERIFIED_EXACT_INACTIVE_DIRECTORIES_REMOVED',
      'at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'archive':{'path':str(ZIP),'bytes':ZIP.stat().st_size,'sha256':zip_hash},
      'removed_exact_directories':removed,'logical_original_bytes_retired':retired,'free_disk_space_recovered_not_measured':True,
      'original_protected_files_before_after':protected,'calibration_marker':{'path':str(MARKER),'sha256':sha(MARKER)},
      'all_archived_member_hashes_original_before_after_and_extracted_equal':True,'archive_members':len(members),
      'RP28_Native_SQLite':native_pair,'calibration_Native_SQLite':native_cal,'dependency_check':dep,
      'process_before':process_before,'process_after':process_after,'logical_before':before,'logical_before_extract':before_extract,
      'logical_peak_with_verification':peak,'logical_after':budget(h),'fixed_budget':LIMIT,'verification_temp_removed':not VERIFY.exists(),
      'Native_ticks':0,'no_other_world_or_current_principal_modified':True,
      'scope':'Only RP28 duplicate and exact VIAB_MSG_PULSE sidecar/worker retired. Historical byte sources remain mapped inside ZIP; life/history/global snapshots remain literal. No memory merge, restoration or experimentation.'}
    PROOF.write_bytes(enc(result));print(json.dumps({'proof':str(PROOF),'archive':result['archive'],'logical_bytes_retired':retired,'Native_ticks':0},ensure_ascii=False))


if __name__=='__main__':main()
