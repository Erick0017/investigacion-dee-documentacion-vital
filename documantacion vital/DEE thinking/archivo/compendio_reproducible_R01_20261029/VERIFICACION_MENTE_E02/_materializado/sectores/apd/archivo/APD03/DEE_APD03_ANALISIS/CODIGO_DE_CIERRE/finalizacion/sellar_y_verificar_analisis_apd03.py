"""Root-gated final APD03 analysis ZIP, exact extraction and archived recalc.

Does not execute Native, providers, comparator policies or a new Full proof.
The eight closed components remain unchanged. Only one superior member
manifest is added to the new analysis stage, without self/archive hashes.
Existing candidates, archives, extraction directories and reports are never
overwritten or removed. A failed/oversized candidate is retained, not
published under the canonical analysis filename.
"""
import argparse
from datetime import datetime,timezone
import hashlib,importlib.util,json,os,re,shutil,stat,subprocess,sys,tempfile,time,zipfile
from pathlib import Path,PurePosixPath

PREFIX='DEE_APD03_ANALISIS'
MAX_BYTES=16_000_000
MANIFEST='MANIFIESTO_FINAL_ANALISIS.json'
CLOSED=('MAIN','MECANISMO','CURVAS','R04','REFERENCIAS','WSLS_ESTANDAR','ENTRADA_UI','SERVICIO_MAIN')
FORBIDDEN=('.zip','.whl','.pyd','.dll','.sqlite','.sqlite3','.db','.deetsnap','.deetsnap.gz','.snap','.snapshot','.npy','.npz')
RESERVED={'CON','PRN','AUX','NUL',*(f'COM{i}'for i in range(1,10)),*(f'LPT{i}'for i in range(1,10))}


def read(path):return json.loads(Path(path).read_bytes())


def sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb')as stream:
        for block in iter(lambda:stream.read(1_048_576),b''):h.update(block)
    return h.hexdigest()


def emit(path,value):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('x',encoding='utf8',newline='\n')as stream:
        json.dump(value,stream,ensure_ascii=False,sort_keys=True,indent=2);stream.write('\n')


def member_name(name):
    if not isinstance(name,str)or not name or any(c in name for c in('\\',':','\x00')):raise ValueError('Unsafe member encoding')
    p=PurePosixPath(name)
    if p.is_absolute()or any(part in('','.','..')for part in p.parts)or str(p)!=name:raise ValueError('Noncanonical member path')
    for part in p.parts:
        if part.endswith((' ','.'))or any(ord(c)<32 for c in part)or part.split('.')[0].upper()in RESERVED:raise ValueError('Unsafe Windows member')
    return p


def safe(root,name):
    p=member_name(name);path=root.joinpath(*p.parts).resolve()
    if not path.is_relative_to(root.resolve()):raise ValueError('Member escapes root')
    return path


def inventory(root,exclude=()):
    rows=[];seen=set()
    for path in sorted(root.rglob('*')):
        if path.is_symlink():raise ValueError('Symlink in analysis stage')
        if not path.is_file():continue
        name=path.relative_to(root).as_posix();member_name(name)
        if name in exclude:continue
        if name.casefold()in seen:raise ValueError('Case-insensitive duplicate in stage')
        seen.add(name.casefold())
        if path.name.lower().endswith(FORBIDDEN)or'deetsnap'in path.name.lower():raise ValueError('Operational engine/database/dense state prohibited: '+name)
        with path.open('rb')as stream:
            if stream.read(16)==b'SQLite format 3\x00':raise ValueError('SQLite content prohibited: '+name)
        rows.append({'file':name,'bytes':path.stat().st_size,'sha256':sha(path)})
    return rows


def full_reference(stage,name,expected_sha):
    if not re.fullmatch('[0-9a-f]{64}',expected_sha):raise ValueError('Root must give exact lowercase Full SHA-256')
    if not name.startswith('VALIDACION_FULL/'):raise ValueError('Full reference must be a packaged closed proof')
    path=safe(stage,name);value=read(path)
    if value.get('error')is not None:raise ValueError('Full report records an error')
    if value.get('zip_sha256')!=expected_sha or type(value.get('zip_bytes'))is not int or value['zip_bytes']<=0:raise ValueError('Full archive identity differs')
    if value.get('zip_still_exact')is not True or value.get('CRC')!='all_members_checked':raise ValueError('Full CRC/unchanged proof missing')
    if type(value.get('zip_members'))is not int or value['zip_members']<=0:raise ValueError('Full member denominator absent')
    before=value.get('managed_manifest');after=value.get('managed_manifest_after')
    if not isinstance(before,dict)or before.get('members_verified',0)<=0 or not re.fullmatch('[0-9a-f]{64}',before.get('manifest_sha256',''))or before!=after:raise ValueError('Full managed hashes not confirmed before/after')
    if value.get('execution',{}).get('exit_code')!=0:raise ValueError('Full actual execution did not finish successfully')
    native=value.get('native_proof')
    if not isinstance(native,dict)or native.get('issues')!=[]:raise ValueError('Full Native proof absent or has issues')
    return {'member':name,'bytes':path.stat().st_size,'sha256':sha(path),'Full_zip_sha256':value['zip_sha256'],
        'Full_zip_bytes':value['zip_bytes'],'Full_CRC':value['CRC'],'Full_zip_members':value['zip_members'],
        'managed_hashes':before,'execution_exit_code':value['execution']['exit_code'],'native_issues':native['issues'],
        'scope':'Existing exact Full verification, not reexecuted by analysis sealing; same computer, not independent hardware.'}


def word_reference(stage):
    edition=read(stage/'MANUAL/EDICION_MANUAL_APD03.json')
    name=Path(edition['document']).name;path=safe(stage,'MANUAL/'+name)
    if path.stat().st_size!=edition['bytes']or sha(path)!=edition['sha256']:raise ValueError('Actual Word differs from its edition proof')
    return {'member':'MANUAL/'+name,'bytes':path.stat().st_size,'sha256':sha(path),
        'visual_validation':edition['visual_validation'],'geometry_preserved':edition.get('geometry_preserved'),
        'history_chapters20_33_preserved':edition.get('history_chapters20_33_preserved'),
        'limit':'Structural editorial proof is not visual page validation; no successful render is inferred.'}


def archive_inventory(archive):
    seen=set();names=[]
    for item in archive.infolist():
        name=item.filename
        if getattr(item,'orig_filename',name)!=name:raise ValueError('Truncated archive member')
        p=member_name(name)
        if not p.parts or p.parts[0]!=PREFIX or len(p.parts)<2:raise ValueError('Incorrect archive prefix')
        if item.is_dir()or stat.S_ISLNK(item.external_attr>>16)or item.flag_bits&1:raise ValueError('Directories/symlinks/encryption forbidden')
        if name.casefold()in seen:raise ValueError('Duplicate archive member')
        seen.add(name.casefold());names.append(name)
        if item.compress_type!=zipfile.ZIP_DEFLATED:raise ValueError('All analysis files must use Deflate')
    return names


def run_recalculation(package,out):
    # The included proof code provides its audited stdlib driver. Its prior
    # N0 result is not reused as the result of this exact final archive.
    tool=package/'CODIGO_DE_CIERRE/probar_analisis_portable_frontera_n0.py'
    spec=importlib.util.spec_from_file_location('analysis_archive_read_fence',tool)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    command=[sys.executable,'-I','-B','-c',module.DRIVER,str(package),str(out),module.CHILD]
    began=time.monotonic()
    run=subprocess.run(command,cwd=tempfile.gettempdir(),capture_output=True,text=True,encoding='utf8',timeout=600)
    evidence={'entry_member':'RECALCULO/recalcular_todo_apd03.py','fence_member':tool.relative_to(package).as_posix(),
        'fence_source_sha256':sha(tool),'command_kind':'Included archived CLI driver with Python read/import/process fence',
        'interpreter':sys.executable,'returncode':run.returncode,'stdout':run.stdout,'stderr':run.stderr,
        'wall_seconds_archived_recalculation':time.monotonic()-began,'new_native_ticks':0,'new_provider_calls':0}
    if run.returncode:raise ValueError('Exact archive recalculation failed: '+run.stdout+run.stderr)
    result=read(out/'RESULTADO_GLOBAL.json');fence=read(out/'FRONTERA_LECTURAS.json')
    plan=read(package/'RECALCULO/PLAN_GLOBAL.json')
    if result['jobs_executed']!=len(plan['jobs'])or result['all_byte_identical']is not True or not all(r['byte_identical']and r['exit_code']==0 for r in result['jobs']):raise ValueError('Not every actual CLI reproduced exact expected bytes')
    if fence.get('fenced_actual_calculator_processes')!=len(plan['jobs'])or fence.get('original_paths_allowed')is not False:raise ValueError('Archived read fence was not applied to every calculator')
    if result.get('new_native_ticks')!=0 or result.get('new_provider_calls')!=0:raise ValueError('Unexpected new Native/provider execution')
    evidence.update({'jobs_executed':result['jobs_executed'],'input_files_verified':result['input_files_verified'],
        'all_byte_identical':result['all_byte_identical'],'combined_report_checks':result['combined_report_checks'],
        'result_file':str(out/'RESULTADO_GLOBAL.json'),'result_sha256':sha(out/'RESULTADO_GLOBAL.json'),
        'fence':fence,'scope':'Archived recomputation from the exact extracted ZIP, not native replay or another scientific trajectory.'})
    return evidence


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--stage',type=Path,required=True)
    ap.add_argument('--zip',type=Path,required=True)
    ap.add_argument('--workspace',type=Path,default=Path.cwd())
    ap.add_argument('--extract',type=Path)
    ap.add_argument('--report',type=Path,required=True)
    ap.add_argument('--full-reference',default='VALIDACION_FULL/VERIFICACION_FULL_APD03_R02.json')
    ap.add_argument('--full-sha256',required=True)
    ap.add_argument('--sellar-root-go',action='store_true')
    args=ap.parse_args()
    if not args.sellar_root_go:raise SystemExit('Prepared only: explicit Root GO --sellar-root-go is required; no ZIP was created')
    stage=args.stage.resolve(strict=True);canonical=args.zip.resolve();report_path=args.report.resolve();workspace=args.workspace.resolve(strict=True)
    extraction=(args.extract or workspace/'_apd03_analisis_final_r02').resolve()
    if extraction.parent!=workspace or extraction.name!='_apd03_analisis_final_r02':raise ValueError('Use the exact new workspace-owned final extraction directory')
    candidate=canonical.with_name(canonical.stem+'.candidato_R02.zip')
    if any(path.exists()for path in(canonical,candidate,report_path,extraction)):raise FileExistsError('Existing precursor/output preserved; no overwrite or automatic reuse')
    if canonical.name!='DEE_APD03_AUTONOMIA_DESARROLLO_DEMOSTRACION_ANALISIS.zip':raise ValueError('Unexpected canonical analysis filename')
    if any(path.is_relative_to(stage)for path in(canonical,candidate,report_path,extraction)):raise ValueError('Outputs must remain outside the stage')
    report={'schema':'APD03.analysis.final_exact_archive_verification.R02','started_utc':datetime.now(timezone.utc).isoformat(),
        'stage':str(stage),'candidate_zip':str(candidate),'canonical_zip':str(canonical),'canonical_published':False,
        'size_limit_bytes':MAX_BYTES,'new_native_ticks':0,'new_provider_calls':0,'energy':'NO MEDIDA',
        'verification_kind':'EXACT_ZIP_ARCHIVED_RECALCULATION_NOT_NATIVE_OR_NEW_FULL'}
    try:
        report['Full_reference']=full_reference(stage,args.full_reference,args.full_sha256)
        report['Word']=word_reference(stage)
        protected={name:inventory(stage/name)for name in CLOSED}
        members=inventory(stage,exclude=(MANIFEST,))
        manifest={'schema':'APD03.analysis.member_hash_manifest.R02','status':'SEALED_ANALYSIS_MEMBERS','prefix':PREFIX,'files':members,
            'files_excluding_this_manifest':len(members),'expanded_bytes_excluding_this_manifest':sum(r['bytes']for r in members),
            'excludes_own_hash':True,'contains_own_archive_hash':False,
            'precursor_note':'CANDIDATO_NO_SELLADO.json records the preceding assembly, not the final archive verification. The exact final ZIP hash and verification receipt remain external.',
            'scope':'Essential scientific analysis; no operational Runtime, Native snapshot or SQLite. Not an autonomous life-continuation backup.'}
        manifest_path=stage/MANIFEST
        if manifest_path.exists():
            if read(manifest_path)!=manifest:raise ValueError('Existing final member manifest differs; preserve it and build another stage revision')
        else:emit(manifest_path,manifest)
        sealed_members=inventory(stage)
        report['member_manifest']={'member':MANIFEST,'sha256':sha(manifest_path),'bytes':manifest_path.stat().st_size,
            'members_without_self':len(members),'members_in_ZIP':len(sealed_members)}
        canonical.parent.mkdir(parents=True,exist_ok=True)
        with zipfile.ZipFile(candidate,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=9,allowZip64=False)as archive:
            for row in sealed_members:
                path=safe(stage,row['file']);info=zipfile.ZipInfo(PREFIX+'/'+row['file'],date_time=(2026,10,26,0,0,0))
                info.compress_type=zipfile.ZIP_DEFLATED;info.create_system=3;info.external_attr=(stat.S_IFREG|0o600)<<16
                info._compresslevel=9
                with path.open('rb')as source,archive.open(info,'w')as dest:shutil.copyfileobj(source,dest,1_048_576)
        report.update({'zip_sha256':sha(candidate),'zip_bytes':candidate.stat().st_size,'archive_files':len(sealed_members)})
        if candidate.stat().st_size>MAX_BYTES:raise ValueError('Analysis candidate exceeds16,000,000bytes; retained without canonical publication')
        extraction.mkdir(parents=True,exist_ok=False)
        expected={PREFIX+'/'+row['file']:row for row in sealed_members}
        with zipfile.ZipFile(candidate)as archive:
            names=archive_inventory(archive)
            if set(names)!=set(expected):raise ValueError('ZIP member set differs from sealed stage')
            bad=archive.testzip()
            if bad is not None:raise ValueError('ZIP CRC failure: '+bad)
            for item in archive.infolist():
                dest=safe(extraction,item.filename);row=expected[item.filename]
                if item.file_size!=row['bytes']:raise ValueError('ZIP uncompressed length differs')
                dest.parent.mkdir(parents=True,exist_ok=True)
                with archive.open(item)as source,dest.open('xb')as stream:shutil.copyfileobj(source,stream,1_048_576)
                if sha(dest)!=row['sha256']:raise ValueError('Extracted member differs from sealed source')
        package=extraction/PREFIX
        if inventory(package)!=sealed_members:raise ValueError('Exact extraction has different members/bytes')
        report['CRC']='all_members_checked';report['extracted_root']=str(package)
        report['archived_recalculation']=run_recalculation(package,extraction/'RECALCULO_EXACTO')
        if inventory(stage)!=sealed_members or inventory(package)!=sealed_members:raise ValueError('Sealed source or exact extracted package changed during verification')
        if any(inventory(stage/name)!=rows for name,rows in protected.items()):raise ValueError('A closed component changed')
        if full_reference(package,args.full_reference,args.full_sha256)!=report['Full_reference']or word_reference(package)!=report['Word']:raise ValueError('Extracted Full/Word references differ')
        if sha(candidate)!=report['zip_sha256']:raise ValueError('Candidate archive changed during verification')
        report['closed_components_unchanged']=list(CLOSED);report['zip_still_exact']=True
        # Windows rename does not replace an existing destination. There is
        # no canonical filename at all until every preceding check succeeds.
        os.rename(candidate,canonical)
        if sha(canonical)!=report['zip_sha256']:raise ValueError('Published canonical archive differs')
        report['canonical_published']=True;report['finished_utc']=datetime.now(timezone.utc).isoformat()
    except BaseException as error:
        report['error']={'type':type(error).__name__,'detail':str(error),'candidate_and_failed_extraction_preserved':True,
            'no_retry_no_Native':True}
        raise
    finally:emit(report_path,report)
    print(json.dumps({'zip':str(canonical),'zip_sha256':report['zip_sha256'],'zip_bytes':report['zip_bytes'],
        'files':report['archive_files'],'external_report':str(report_path),'new_native_ticks':0}))


if __name__=='__main__':main()
