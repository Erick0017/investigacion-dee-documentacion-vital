"""Root-only archive of exactly two closed duplicate pairs. Default plan only.

No DEE import/Native execution. --aplicar creates one lossless local ZIP,
extracts and checks every byte, Native buffers and read-only SQLite, then may
retire only the two exact original copies and its own verified extraction.
"""
from pathlib import Path,PurePosixPath
import argparse,datetime,hashlib,json,os,runpy,shutil,sqlite3,zipfile

P=Path(__file__).resolve().parents[1];R=P.parents[2];W=P.parents[4]
C=R/'DEE Cognitive 2.0';RP=C/'reproducibilidad';M=RP/'materiales'
NAMES=('PI07_ADQUIRIDO_08_T830877','PI07_ADQUIRIDO_12_T834005')
TARGETS=tuple(M/name for name in NAMES);LIMIT=5_500_000_000
A=P/'archivo';ZIP=A/'PI07_COPIAS_ADQUIRIDAS_08_12_CERRADAS_R01.zip'
VERIFY=W/'PI07_ARC_V08_12_R01';PROOF=P/'control/ARCHIVO_COPIAS_08_12_PI07_R01.json'
MANIFEST='MANIFIESTO_ARCHIVO.json'


def require(v,message):
    if not v:raise ValueError(message)


def sha_file(p):
    h=hashlib.sha256()
    with Path(p).open('rb')as f:
        for block in iter(lambda:f.read(1048576),b''):h.update(block)
    return h.hexdigest()


def encoded(value):return(json.dumps(value,ensure_ascii=False,indent=2)+'\n').encode('utf-8')


def safe_root(p):
    p=Path(p).absolute();require(p.resolve().is_relative_to(W.resolve()),'Outside exact workspace')
    for q in(p,*p.parents):
        if q.exists():
            s=q.lstat();require(not q.is_symlink()and not(getattr(s,'st_file_attributes',0)&1024),'Reparse ancestor:'+str(q))
        if q==W:break
    return p.resolve()


def listing(root):
    """One root/ancestor check; one lstat per entry, not per-entry ancestors."""
    root=safe_root(root);files=[];dirs=[''];stack=[root]
    while stack:
        directory=stack.pop()
        with os.scandir(directory)as entries:
            for e in entries:
                s=e.stat(follow_symlinks=False)
                require(not e.is_symlink()and not(getattr(s,'st_file_attributes',0)&1024),'Reparse member:'+e.path)
                p=Path(e.path);rel=p.relative_to(root).as_posix()
                if e.is_dir(follow_symlinks=False):dirs.append(rel);stack.append(p)
                else:require(e.is_file(follow_symlinks=False),'Nonregular member');files.append({'relative':rel,'bytes':s.st_size,'mtime_ns':s.st_mtime_ns})
    return files,sorted(dirs)


def scoped_bytes():
    roots=[P]
    if VERIFY.exists():roots.append(VERIFY) # Short-path extraction still counts.
    for parent in(RP/'materiales',RP/'codigo_preservado',RP/'recetas',RP/'verificaciones'):
        for entry in parent.iterdir():
            if entry.name.startswith(('PI07_','pi07_')):roots.append(entry)
    total=0
    for root in roots:
        if root.is_file():safe_root(root);total+=root.stat().st_size
        else:files,_=listing(root);total+=sum(f['bytes']for f in files)
    return total


def strings(value):
    if isinstance(value,str):yield value
    elif isinstance(value,dict):
        for key,v in value.items():yield key;yield from strings(v)
    elif isinstance(value,list):
        for v in value:yield from strings(v)


def dependencies():
    paths=[RP/'RECURSOS.json',C/'PROYECTO.json',C/'CONTINUIDAD_DEE_COGNITIVE_2_0.json',
      C/'sistema/estado/ACTIVO.json',C/'sistema/estado/genesis/SELECCION_PERSONAL.json',
      C/'sistema/capacidades/CATALOGO_CAPACIDADES.json']
    paths+=sorted((RP/'recetas').glob('*.json'))
    s7=P/'estados/candidato/sistema'
    for parent,pattern in((s7/'capacidades','pi07*.py'),(s7/'capacidades','PROTOCOLO_PI07*.json'),(s7/'contratos','PI07*.json')):
        paths+=sorted(parent.glob(pattern))
    result=[];hits=[]
    for p in dict.fromkeys(paths):
        b=p.read_bytes();text=b.decode('utf-8-sig')
        # Historical preservation witnesses and campaign prose are not in this
        # current-operational allowlist. Exact pair-name hits block retirement.
        found=[name for name in NAMES if name.casefold()in text.casefold()]
        if found:hits.append({'file':str(p),'targets':found})
        result.append({'path':str(p),'sha256':hashlib.sha256(b).hexdigest()})
    return{'checked':result,'blocking_references':hits,'clear':not hits}


def native_and_sqlite(root):
    manifest=json.loads((root/'EXPORTACION_SERVICIO.json').read_text(encoding='utf-8'))
    snap=(root/manifest['native_snapshot']).resolve(strict=True)
    require(snap.is_relative_to(root.resolve()),'Native snapshot escape')
    parser=P.parent/'PROGRESION_INTEGRADA_05/codigo/contrastar_prefijos_C2C_PI05_pasivo.py'
    require(sha_file(parser)=='5d84e2a21d6650f1dd69d3c677eb32db0aa9da9f0ae0ed315bb2d0992852124b','Reviewed pure snapshot parser changed')
    module=runpy.run_path(str(parser),run_name='pure_archived_snapshot_reader')
    native=module['parse'](snap,manifest['snapshot_sha256'])[0]
    for key in('N','tick','RAW_sha256','clocks_sha256'):
        require(native['physical'][key]==manifest['physical'][key],'Native manifest mismatch:'+key)
    databases=[]
    for db in sorted(root.rglob('*.sqlite3')):
        wal=Path(str(db)+'-wal')
        require(not wal.exists()or wal.stat().st_size==0,'Nonempty WAL needs another coherent contract; preserve originals')
        con=sqlite3.connect(db.resolve().as_uri()+'?mode=ro&immutable=1',uri=True)
        try:
            integrity=[x[0]for x in con.execute('PRAGMA integrity_check')];require(integrity==['ok'],'SQLite integrity failure')
            tables=[x[0]for x in con.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")]
            counts={name:con.execute('SELECT COUNT(*) FROM "'+name.replace('"','""')+'"').fetchone()[0]for name in tables}
        finally:con.close()
        databases.append({'file':db.relative_to(root).as_posix(),'sha256':sha_file(db),'integrity':'ok','table_rows':counts})
    require(databases,'Expected complete paired SQLite not found')
    return{'manifest_sha256':sha_file(root/'EXPORTACION_SERVICIO.json'),
      'physical':native['physical'],'interfaces':native['interfaces_count'],
      'pending_native':native['pending_count'],'Native_receipts':native['receipts_count'],
      'snapshot_sha256':manifest['snapshot_sha256'],'SQLite':databases}


def remove_exact(root,approved,expected=None):
    root=safe_root(root);require(root==approved.resolve()and root not in(W.resolve(),R.resolve(),RP.resolve(),M.resolve(),P.resolve()),'Unsafe recursive target')
    files,dirs=listing(root) # Fresh no-reparse validation, no symlink following.
    if expected is not None:
        old={x['relative']:(x['bytes'],x.get('mtime_ns'))for x in expected['files']}
        new={x['relative']:(x['bytes'],x.get('mtime_ns')if old.get(x['relative'],(None,None))[1]is not None else None)for x in files}
        require(new==old,'An unarchived or changed file appeared; no recursive removal')
        if'directories'in expected:require(dirs==expected['directories'],'Directory structure changed before removal')
    shutil.rmtree(root)
    require(not root.exists(),'Exact directory still exists after removal')


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--aplicar',action='store_true')
    ap.add_argument('--owner-proof',type=Path);args=ap.parse_args()
    require(not A.exists()or A.is_dir(),'PI07 archive location is not a directory')
    require(all(t.parent.resolve()==M.resolve()and t.name==n for t,n in zip(TARGETS,NAMES)),'Exact immutable target names required')
    require(not ZIP.exists()and not VERIFY.exists()and not PROOF.exists(),'Prior archive attempt exists; preserve and inspect it rather than blindly rerunning')
    dep=dependencies();inventories={};raw=0;count=0
    for target in TARGETS:
        require(target.is_dir(),'Exact copy missing:'+str(target))
        files,dirs=listing(target);inventories[target.name]={'files':files,'directories':dirs}
        raw+=sum(x['bytes']for x in files);count+=len(files)
    if not args.aplicar:
        print(json.dumps({'mode':'READ_ONLY_PLAN','targets':[str(t)for t in TARGETS],
          'files':count,'logical_source_bytes':raw,'dependency_clear':dep['clear'],
          'blocking_references':dep['blocking_references'],'archive':str(ZIP),
          'verification':str(VERIFY),'archive_directory_exists':A.is_dir(),'fixed_budget':LIMIT,'writes':0,'Native_ticks':0},ensure_ascii=False));return
    require(dep['clear'],'Unresolved current dependency; no copies retired')
    require(args.owner_proof is not None,'Actual current owned-run closure proof required')
    owner_path=safe_root(args.owner_proof.resolve(strict=True));ob=owner_path.read_bytes();owner=json.loads(ob)
    require(owner.get('closed')is True and owner.get('status')=='CLOSED','Actual owned runner must be closed')
    before=scoped_bytes();require(before<=LIMIT,'Already beyond fixed5.5GB; preserve all')
    # Worst-case archive bound first. Extraction starts only after actual ZIP
    # size and a new metadata count prove there is room for its exact contents.
    require(before+int(raw*1.01)+count*128+8_000_000<=LIMIT,'No room for bounded lossless archive creation')
    safe_root(A);A.mkdir(exist_ok=True)
    roots=[];part=ZIP.with_name(ZIP.name+'.writing')
    require(not part.exists(),'Prior partial archive exists')
    with zipfile.ZipFile(part,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=9,allowZip64=False)as z:
        for target in TARGETS:
            inv=inventories[target.name];entries=[]
            for d in inv['directories']:z.writestr(target.name+('/'+d if d else'')+'/',b'')
            for file in inv['files']:
                p=target/file['relative'];stat=p.stat();require(stat.st_size==file['bytes']and stat.st_mtime_ns==file['mtime_ns'],'Source changed before archiving')
                member=target.name+'/'+file['relative'];h=hashlib.sha256()
                with p.open('rb')as source,z.open(member,'w')as destination:
                    for block in iter(lambda:source.read(1048576),b''):h.update(block);destination.write(block)
                end=p.stat();require((end.st_size,end.st_mtime_ns)==(stat.st_size,stat.st_mtime_ns),'Source changed during archiving')
                entries.append({'file':member,'relative':file['relative'],'bytes':file['bytes'],'sha256':h.hexdigest()})
            declared=json.loads((target/'EXPORTACION_SERVICIO.json').read_text(encoding='utf-8'))
            actual={f['relative']:f for f in entries}
            for item in declared['members']:
                require(item['file']in actual,'Paired manifest member missing')
                require(all(actual[item['file']][key]==item[key]for key in('bytes','sha256')),'Paired manifest member differs:'+item['file'])
            roots.append({'original':str(target.resolve()),'name':target.name,'files':entries,'directories':inv['directories'],
                          'native_and_SQLite_original':native_and_sqlite(target)})
        archive_manifest={'schema':'DEE.PI07.two_closed_copy_archive.v1','roots':roots,
          'Native_ticks':0,'not_a_principal_backup':True,'self_hash_and_ZIP_hash_excluded':True}
        z.writestr(MANIFEST,encoded(archive_manifest))
    with zipfile.ZipFile(part)as z:require(z.testzip()is None,'Archive CRC failure')
    part.rename(ZIP);zip_hash=sha_file(ZIP);before_extract=scoped_bytes()
    require(before_extract+raw+8_000_000<=LIMIT,'No room for clean extraction within fixed5.5GB; keep originals+ZIP')
    VERIFY.mkdir()
    with zipfile.ZipFile(ZIP)as z:
        for member in z.infolist():
            name=PurePosixPath(member.filename);require(not name.is_absolute()and'..'not in name.parts,'Unsafe archive member')
            dest=VERIFY.joinpath(*name.parts);require(dest.resolve().is_relative_to(VERIFY.resolve()),'Extraction escape')
            if member.is_dir():dest.mkdir(parents=True,exist_ok=True);continue
            dest.parent.mkdir(parents=True,exist_ok=True)
            with z.open(member)as source,dest.open('xb')as output:shutil.copyfileobj(source,output,1048576)
    maximum_observed=scoped_bytes();require(maximum_observed<=LIMIT,'Actual temporary extraction exceeds5.5GB; do not retire')
    verifications=[]
    for entry,target in zip(roots,TARGETS):
        extracted=VERIFY/entry['name']
        for file in entry['files']:
            src=target/file['relative'];dst=extracted/file['relative']
            require(src.stat().st_size==dst.stat().st_size==file['bytes']and sha_file(src)==sha_file(dst)==file['sha256'],'Original/extracted member mismatch')
        require(all((extracted/d).is_dir()for d in entry['directories']),'Directory structure lost')
        check=native_and_sqlite(extracted);require(check==entry['native_and_SQLite_original'],'Native/SQLite extraction validation differs')
        verifications.append({'original':str(target),'archive_directory':entry['name']+'/',
          'files':len(entry['files']),'bytes':sum(f['bytes']for f in entry['files']),
          'all_member_hashes_original_before_after_and_extraction_match':True,
          'Native_and_SQLite':check})
    require(dependencies()==dep and owner_path.read_bytes()==ob,'Operational reference or owned closure witness changed')
    require(sha_file(ZIP)==zip_hash,'Verified ZIP changed')
    # Deletions are the sole explicitly authorized Root action; no other tree,
    # originals in S7, selected Main or protected preacquisition pair is touched.
    removed=[]
    for target in TARGETS:remove_exact(target,target,inventories[target.name]);removed.append(str(target))
    verify_files=[{'relative':f['file'],'bytes':f['bytes']}for root in roots for f in root['files']]
    verify_files.append({'relative':MANIFEST,'bytes':(VERIFY/MANIFEST).stat().st_size})
    remove_exact(VERIFY,VERIFY,{'files':verify_files})
    with zipfile.ZipFile(ZIP)as z:require(z.testzip()is None,'Preserved ZIP CRC failed after retirement')
    require(sha_file(ZIP)==zip_hash,'Preserved archive changed after retirement')
    result={'schema':'DEE.PI07.two_closed_copies.archived_and_retired.v1','status':'ARCHIVED_VERIFIED_EXACT_COPIES_REMOVED',
      'at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'archive':{'path':str(ZIP),'bytes':ZIP.stat().st_size,'sha256':zip_hash},
      'roots':verifications,'dependency_check':dep,'owner_closure':{'path':str(owner_path),'sha256':hashlib.sha256(ob).hexdigest()},
      'removed_exact_directories':removed,'verification_temp_removed':not VERIFY.exists(),
      'logical_original_copy_bytes_retired':raw,'free_disk_space_recovered_not_measured':True,
      'logical_accounted_before':before,'logical_accounted_before_extraction':before_extract,
      'logical_accounted_with_verification':maximum_observed,'logical_accounted_after':scoped_bytes(),
      'fixed_budget':LIMIT,'Native_ticks':0,'scope':'Only08/12closedRPcopies. S7originalsnapshots/journals and currentMain/P0/R03pairs remain; original historical paths retained insidearchive and mapped here.'}
    PROOF.write_bytes(encoded(result));print(json.dumps({'proof':str(PROOF),'archive':result['archive'],
      'logical_original_bytes_retired':raw,'Native_ticks':0},ensure_ascii=False))


if __name__=='__main__':main()
