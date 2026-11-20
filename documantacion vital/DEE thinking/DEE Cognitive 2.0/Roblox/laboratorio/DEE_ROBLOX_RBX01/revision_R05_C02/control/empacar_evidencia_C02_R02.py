"""Explicit final-export plan -> compact analysis ZIP; no DEE/MCP/HTTP execution.

Run only after Root freezes finalexport.json:
 {"schema":"DEE.RBX01.C02.final_export.R01","finalized":true,
  "files":[{"source":"evidencia/.../record.json","archive":"EVIDENCIA/record.json",
             "sha256":"<actual64hex>","role":"primary"}],
  "critical_baseline":"control/CRITICOS_ANTES_C02.json"}

--check-plan is read-only. --build additionally requires --stage NEW and --zip
NEW. Exact files only; no recursive automatic inclusion. Analysis is not a Native
backup. Private config/tokens, SQLite, models, motors, snapshots and videos are
excluded. Every source and named protected critical is hashed before/after.
"""
from pathlib import Path,PurePosixPath
import argparse,ast,csv,hashlib,io,json,re,shutil,zipfile
ROOT=Path(__file__).resolve().parents[1]
PRODUCT=ROOT.parents[2]
PROJECT=ROOT.parents[6]
LIMIT=15000000
ROLES={'readme','report','protocol','primary','control','world_checkpoint','code','recalculation','continuity','map','verification'}
TEXT_SUFFIXES={'.txt','.md','.json','.jsonl','.csv','.py','.luau','.srt'}
def need(ok,msg):
    if not ok:raise ValueError(msg)
def sha_bytes(data):return hashlib.sha256(data).hexdigest()
def sha(path):
    h=hashlib.sha256()
    with path.open('rb')as f:
        for data in iter(lambda:f.read(1048576),b''):h.update(data)
    return h.hexdigest()
def read(path):return json.loads(path.read_text('utf-8-sig'))
def safe(path,root,*,exists=True):
    path=Path(path)
    if not path.is_absolute():path=root/path
    path=path.absolute()
    for p in(path,*path.parents):need(not p.is_symlink()and not(p.exists()and getattr(p.lstat(),'st_file_attributes',0)&1024),'No linked/reparse export paths')
    path=path.resolve(strict=exists);need(path.is_relative_to(root),'Path outside explicit DEE scope');return path
def member(name):
    need(isinstance(name,str)and name and '\\'not in name and ':'not in name,'Simple POSIX archive name')
    p=PurePosixPath(name);need(not p.is_absolute()and all(x not in('','..','.')for x in p.parts),'Unsafe ZIP path')
    reserved={'CON','PRN','AUX','NUL'}|{'COM'+str(i)for i in range(1,10)}|{'LPT'+str(i)for i in range(1,10)}
    need(all(x.rstrip(' .')==x and x.split('.')[0].upper()not in reserved and not re.search(r'[\x00-\x1f]',x)for x in p.parts),'Portable non-device ZIP names required')
    need(len(name)<=220,'Bounded ZIP path');return p.as_posix()
def credential_values():
    values=[];private=ROOT/'configuracion_privada'
    if private.is_dir():
        for file in private.iterdir():
            if file.is_file()and(file.suffix.lower()=='.token'or('token'in file.name.lower()and file.suffix.lower()=='.txt')):
                raw=file.read_bytes().strip()
                if len(raw)>=24:values.append(raw)
    return values
def source_allowed(path,role):
    need(path.is_file()and path.suffix.lower()in TEXT_SUFFIXES,'Only explicit small text/code/primary records, no binaries or nested archives')
    parts={x.casefold()for x in path.parts}
    need('configuracion_privada'not in parts and 'motor'not in parts and 'python313'not in parts,'Private configuration/motor excluded')
    need(path.suffix.lower()not in('.token','.key','.pem')and path.name.lower()not in('.env','credentials.json'),'Credential material excluded')
    if path.is_relative_to(ROOT/'native'):
        relative=path.relative_to(ROOT/'native');parts_relative=relative.parts
        permitted=(len(parts_relative)==1 and path.suffix=='.py')or parts_relative[0]=='r02_bundle'
        permitted=permitted or(path.suffix=='.json'and('functions'in parts_relative or 'ensayos'in parts_relative or 'resultados'in parts_relative))
        # Exact compact actor phase journal is a causal primary, not a Native
        # system backup. No other JSONL/tree path gains permission.
        permitted=permitted or(len(parts_relative)==7 and parts_relative[1:4]==('sistema','estado','servicios_locales')
            and parts_relative[5]in('RBX02_NATIVE_C02','RBX02_NATIVE_C02_R02')and parts_relative[6]=='events.jsonl')
        need(permitted,'Full Native state/platform copy is not an analysis primary')
    need(not any(x.casefold()in('native_root','site-packages','models','modelos')for x in path.parts),'State backup/model/platform tree excluded')
    need(path.stat().st_size<=5000000,'Each exported decisive record must be <=5000000 bytes; preserve whole original locally')
def validate_text(name,data):
    text=data.decode('utf-8-sig');suffix=PurePosixPath(name).suffix.lower()
    if suffix=='.json':json.loads(text)
    elif suffix=='.jsonl':
        for line in text.splitlines():
            if line.strip():json.loads(line)
    elif suffix=='.csv':list(csv.reader(io.StringIO(text,newline='')))
    elif suffix=='.py':ast.parse(text)
    return len(text)
def protected(baseline_path):
    baseline=read(baseline_path);out=[]
    for row in baseline['files']:
        path=safe(row['path'],PROJECT);actual=sha(path)
        need(actual==row['sha256'],'Protected critical differs: '+row.get('role',path.name))
        out.append({'role':row.get('role'),'path':str(path),'bytes':path.stat().st_size,'before_sha256':row['sha256'],
                    'observed_sha256':actual,'matches':True})
    return out
def plan_check(plan_path):
    plan_path=safe(plan_path,ROOT);plan=read(plan_path)
    need(plan.get('schema')=='DEE.RBX01.C02.final_export.R01'and plan.get('finalized')is True,'Root must explicitly freeze final export plan')
    need(isinstance(plan.get('files'),list)and 1<=len(plan['files'])<=500,'Explicit bounded final file list')
    baseline=safe(plan.get('critical_baseline','control/CRITICOS_ANTES_C02.json'),ROOT)
    critical=protected(baseline);secrets=credential_values();rows=[];names=set();contents={};total=0
    for item in plan['files']:
        path=Path(item['source']);path=safe(path if path.is_absolute()else ROOT/path,PRODUCT)
        role=item['role'];need(role in ROLES,'Known analysis role required');source_allowed(path,role)
        name=member(item['archive']);need(name.casefold()not in names,'Duplicate/case-colliding ZIP member');names.add(name.casefold())
        need(name not in('CONTROL/MANIFIESTO_SHA256.json','CONTROL/PROTECCION_CRITICOS.json'),'Generated control member name is reserved')
        need(re.fullmatch('[0-9a-f]{64}',item.get('sha256','')),'Every source must have a prospective exact SHA256')
        data=path.read_bytes();actual=sha_bytes(data);need(actual==item['sha256'],'Final source changed after plan freeze: '+str(path))
        need(not any(value in data for value in secrets),'Known private bearer found in selected file; refuse without exposing it')
        validate_text(name,data)
        if actual in contents:need(isinstance(item.get('duplicate_justification'),str)and item['duplicate_justification'].strip(),'Duplicate content: share one dependency or explain its scientific necessity')
        contents[actual]=name;total+=len(data)
        rows.append({'source':str(path),'archive':name,'bytes':len(data),'sha256':actual,'role':role})
    need(total<=80000000,'Bounded compact analysis content, not a full project export')
    need(any(r['role']=='readme'for r in rows)and any(r['role']=='report'for r in rows),'Self-contained readme and report are required')
    return plan,rows,critical,baseline
def verify_zip(path):
    need(path.is_file()and path.stat().st_size<=LIMIT,'Final ZIP exceeds15000000 bytes or is absent')
    with zipfile.ZipFile(path)as archive:
        info=archive.infolist();need(len(info)<=503 and sum(x.file_size for x in info)<=81000000 and all(x.file_size<=5100000 for x in info),'Bounded analysis ZIP before decompression')
        need(archive.testzip()is None,'ZIP CRC/integrity failure')
        names=archive.namelist();need(len(names)==len(set(x.casefold()for x in names)),'Duplicate ZIP members')
        manifest=json.loads(archive.read('CONTROL/MANIFIESTO_SHA256.json').decode('utf8'))
        expected={r['archive']for r in manifest['members']}
        need(set(names)==expected|{'CONTROL/MANIFIESTO_SHA256.json'},'ZIP member set differs from manifest')
        for row in manifest['members']:
            name=member(row['archive']);data=archive.read(name)
            need(len(data)==row['bytes']and sha_bytes(data)==row['sha256'],'Member hash mismatch: '+name)
            validate_text(name,data)
        need(all(i.compress_type==zipfile.ZIP_DEFLATED for i in archive.infolist()),'Standard Deflate only')
    return {'status':'ZIP_INTEGRITY_AND_CONTENT_HASHES_VERIFIED','zip':str(path),'bytes':path.stat().st_size,
            'sha256':sha(path),'members':len(names),'limit_bytes':LIMIT,'Native_executed':False}
def build(plan_path,stage,output):
    plan,rows,critical_before,baseline=plan_check(plan_path)
    baseline_sha=sha(baseline)
    stage=safe(stage,ROOT,exists=False);output=safe(output,ROOT,exists=False)
    need(not stage.exists()and not output.exists(),'Fresh stage and ZIP only; preserve older deliveries')
    need(not stage.is_relative_to(ROOT/'native')and not output.is_relative_to(ROOT/'native')and
         not stage.is_relative_to(ROOT/'configuracion_privada')and not output.is_relative_to(ROOT/'configuracion_privada'),'Outputs separated from operational state/private config')
    stage.mkdir(parents=True);members=[]
    for row in rows:
        data=Path(row['source']).read_bytes();need(sha_bytes(data)==row['sha256'],'Source changed while staging')
        dest=stage.joinpath(*PurePosixPath(row['archive']).parts);dest.parent.mkdir(parents=True,exist_ok=True)
        with dest.open('xb')as f:f.write(data)
        members.append({k:row[k]for k in('archive','bytes','sha256','role','source')})
    critical_after=protected(baseline);need(critical_before==critical_after,'Protected files changed during staging')
    result={'schema':'DEE.RBX01.C02.protected_named_files_verified.R01','scope':'Only named baseline criticals, not whole-project immutability',
            'baseline':str(baseline),'baseline_sha256':sha(baseline),'before':critical_before,'after':critical_after}
    target=stage/'CONTROL/PROTECCION_CRITICOS.json';target.parent.mkdir(parents=True,exist_ok=True)
    data=(json.dumps(result,ensure_ascii=False,indent=2)+'\n').encode('utf8');target.write_bytes(data)
    members.append({'archive':'CONTROL/PROTECCION_CRITICOS.json','bytes':len(data),'sha256':sha_bytes(data),'role':'verification'})
    manifest={'schema':'DEE.RBX01.C02.analysis_manifest.R01','package_type':'ANALYSIS_NOT_NATIVE_BACKUP','members':members,
              'plan_sha256':sha(safe(plan_path,ROOT)),'Native_imports':0,'Native_ticks':0,'MCP_calls':0,
              'excluded':'Credentials/private configs/SQLite/motors/models/large Native snapshots/videos/platform copies; no automatic code execution.'}
    control=stage/'CONTROL/MANIFIESTO_SHA256.json';control.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    with zipfile.ZipFile(output,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=9,allowZip64=True)as archive:
        for file in sorted(stage.rglob('*')):
            if file.is_file():archive.write(file,file.relative_to(stage).as_posix())
    proof=verify_zip(output)
    extraction=stage.parent/(stage.name+'_EXTRACCION_VERIFICACION');need(not extraction.exists(),'Fresh clean extraction verification path')
    extraction.mkdir()
    with zipfile.ZipFile(output)as archive:
        for name in archive.namelist():
            name=member(name);dest=extraction.joinpath(*PurePosixPath(name).parts);dest.parent.mkdir(parents=True,exist_ok=True)
            with dest.open('xb')as f:f.write(archive.read(name))
    for row in members:
        extracted=extraction.joinpath(*PurePosixPath(row['archive']).parts)
        need(sha(extracted)==row['sha256'],'Clean extraction mismatch')
    for row in rows:need(sha(Path(row['source']))==row['sha256'],'Source changed before final signoff')
    need(protected(baseline)==critical_before,'Protected files changed before final signoff')
    need(sha(baseline)==baseline_sha,'Protected baseline changed during packing')
    return {**proof,'clean_extraction':str(extraction),'stage':str(stage),'protected_named_files':len(critical_before),
            'protected_hashes_before_after_match':True,'no_sources_modified':True}
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);mode=p.add_mutually_exclusive_group(required=True)
    mode.add_argument('--check-plan',action='store_true');mode.add_argument('--build',action='store_true');mode.add_argument('--verify-zip',type=Path)
    p.add_argument('--plan',type=Path);p.add_argument('--stage',type=Path);p.add_argument('--zip',type=Path)
    a=p.parse_args()
    if a.verify_zip:result=verify_zip(safe(a.verify_zip,ROOT))
    else:
        need(a.plan,'Explicit finalexport.json required')
        if a.check_plan:
            _,rows,critical,_=plan_check(a.plan);result={'status':'PLAN_READONLY_VERIFIED_NOT_PACKED','files':len(rows),'uncompressed_bytes':sum(r['bytes']for r in rows),'protected_named_files':len(critical),'Native_executed':False}
        else:
            need(a.stage and a.zip,'Fresh explicit stage and ZIP required');result=build(a.plan,a.stage,a.zip)
    print(json.dumps(result,ensure_ascii=False,indent=2))
