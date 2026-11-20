"""Exact-selection analysis ZIP <=15,000,000 bytes. No Native/Owner execution.

Root supplies final facts/files. Missing required content blocks sealing.
Only optional snapshot copies may be omitted for size; full local originals
remain untouched. A clean extraction validates hashes, schemas and explicitly
whitelisted pure recalculations. This is not an executable full-state backup.
"""
from pathlib import Path,PurePosixPath
from datetime import datetime,timezone
import argparse,ast,csv,hashlib,io,json,subprocess,sys,zipfile

LIMIT=15_000_000
FORBIDDEN={'.zip','.whl','.pyd','.dll','.exe','.mp4','.mp3','.aac','.wav'}
PURE={'recalcular_primarios_PI10_R02.py','recalcular_primarios_PI10_R03.py','recalcular_contactos_TC_PI10_R01.py','recalcular_contactos_TC_PI10_R02.py',
 'comparar_brazos_PI10_R02.py','comparar_real_no_fallo_PI10_R02.py','comparar_traza_cortada_sham_PI10_R02.py','referencias_offline_PI10_R02.py',
 'resumir_trayectoria_individual_PI10_R02.py','recalcular_preparacion_guardas_PI10_R02.py','recalcular_snapshots_incluidos_PI10_R01.py','recalcular_metricas_adopcion_PI10_R05_PORTABLE.py','recalcular_metricas_adopcion_PI10_R06_PORTABLE.py'}
def need(ok,why):
    if not ok:raise ValueError(why)
def sha(b):return hashlib.sha256(b).hexdigest()
def read_json(b):return json.loads(b.decode('utf-8-sig'),parse_constant=lambda x:(_ for _ in()).throw(ValueError('Non-JSON numeric constant: '+x)))
def regular(p):
    p=Path(p).absolute()
    for q in(p,*p.parents):
        if q.exists():need(not q.is_symlink()and not(getattr(q.lstat(),'st_file_attributes',0)&1024),'Linked/reparse source or destination')
    return p
def member(name):
    pp=PurePosixPath(name);need(name and not pp.is_absolute()and '..'not in pp.parts and ':'not in name and '\\'not in name,'Simple safe internal ZIP path')
    return pp.as_posix()
def dump(v):return(json.dumps(v,ensure_ascii=False,indent=2,allow_nan=False)+'\n').encode('utf8')
def validate_content(name,b):
    ext=Path(name).suffix.lower()
    if ext=='.json':read_json(b)
    elif ext=='.jsonl':
        for line in b.decode('utf-8-sig').splitlines():
            if line.strip():read_json(line.encode('utf8'))
    elif ext=='.csv':
        rows=list(csv.reader(io.StringIO(b.decode('utf-8-sig'))));need(rows and rows[0]and all(len(r)==len(rows[0])for r in rows),'Rectangular nonempty CSV: '+name)
    elif ext in('.md','.txt','.py','.srt','.bat','.ps1'):b.decode('utf-8-sig')
    if ext=='.py':ast.parse(b.decode('utf-8-sig'))
    if ext=='.docx':
        with zipfile.ZipFile(io.BytesIO(b))as doc:
            need(doc.testzip()is None and 'word/document.xml'in doc.namelist(),'Complete readable DOCX container: '+name)
            need(not any('vbaproject'in n.lower()for n in doc.namelist()),'No macro execution/content copied')

def build(config,work,zipout):
    need(config.get('schema')=='DEE.PI10.exact_analysis_selection.R01'and config.get('facts_finalized')is True,'Root-finalized exact content selection required')
    work=regular(work);zipout=regular(zipout);need(not work.exists()and not zipout.exists(),'New staging and ZIP only; no overwrite')
    need(work.parent.is_dir()and zipout.parent.is_dir(),'Existing named staging/output parents')
    planned=[];roles=[]
    def add(source,name,role,optional=False,priority=0):
        source=regular(source);need(source.is_file(),'Missing selected source: '+str(source));name=member(name)
        need(source.suffix.lower()not in FORBIDDEN,'Engine, media or nested historical ZIP not allowed: '+str(source))
        b=source.read_bytes();validate_content(name,b)
        if optional:need(role=='optional_snapshot'and source.name.endswith('.deetsnap.gz'),'Only explicitly optional standalone native snapshots may be dropped')
        planned.append({'source':source,'member':name,'role':role,'optional':optional,'priority':priority,'bytes':b,'sha256':sha(b)})
        roles.append(role)
    for f in config.get('files',[]):
        source=Path(f['source'])
        if not source.is_file()and not f.get('required',True):continue
        add(source,f['member'],f['role'],f.get('optional',False),f.get('priority',0))
    for d in config.get('closed_primary_bundles',[]):
        root=regular(d['source']);need(root.is_dir()and(root/'INDEX.json').is_file(),'Missing explicit closed primary bundle')
        idx=read_json((root/'INDEX.json').read_bytes());need(idx.get('schema')=='DEE.PI10.closed_primary_bundle.R01'and idx.get('closed')is True,'Only closed primary bundle roots')
        target=member(d['member'])
        for source in sorted(root.rglob('*')):
            regular(source)
            if source.is_file():add(source,target+'/'+source.relative_to(root).as_posix(),'primary_evidence')
    need(len({x['member']for x in planned})==len(planned),'No duplicate internal ZIP members')
    need(roles.count('manual')==1 and roles.count('compendium')==1,'Exactly one full current Manual and one Compendium')
    for role in('readme','scientific_report','continuity','capabilities_csv','coverage'):need(role in roles,'Required analysis role missing: '+role)
    manual=next(x for x in planned if x['role']=='manual');need(manual['member'].lower().endswith('.docx'),'Current complete Word, not a substitute summary')
    with zipfile.ZipFile(io.BytesIO(manual['bytes']))as doc:
        text=doc.read('word/document.xml').decode('utf8');need('DCS11' in text and 'MM' in text,'Manual identity not recognizable; Root must resolve')
    work.mkdir();content=work/'contenido';content.mkdir()
    for x in planned:
        target=content.joinpath(*PurePosixPath(x['member']).parts);target.parent.mkdir(parents=True,exist_ok=True)
        with target.open('xb')as f:f.write(x['bytes'])
    optional=sorted([x for x in planned if x['optional']],key=lambda x:x['priority'])
    selected=list(planned);omitted=[];trial=0
    while True:
        trial+=1
        omissions={'schema':'DEE.PI10.analysis_omissions.R01','not_an_executable_full_backup':True,
          'optional_snapshots_omitted':omitted,'local_large_preserved':config.get('local_large_preserved',[]),
          'scope':'Snapshots alone do not include every SQLite, environment, outbox and artifact dependency. Complete coherent local stores remain authoritative.'}
        omission_name='05_CONTROL/OMISIONES_LOCALIZADAS.json';need(omission_name not in{x['member']for x in planned},'Generated omissions member is reserved')
        omission_bytes=dump(omissions)
        hashes=[{'file':x['member'],'bytes':len(x['bytes']),'sha256':x['sha256'],'role':x['role']}for x in selected]
        hashes.append({'file':omission_name,'bytes':len(omission_bytes),'sha256':sha(omission_bytes),'role':'omissions'})
        manifest={'schema':'DEE.PI10.content_manifest.R01','created_utc':datetime.now(timezone.utc).isoformat(),'files':hashes,
          'manual_literal_source':{'path':str(manual['source']),'bytes':len(manual['bytes']),'sha256':manual['sha256']},
          'no_manifest_self_hash_or_zip_hash':True,'Native_executed_for_packaging':False}
        mb=dump(manifest);temp=work/('construccion_%02d.zip'%trial)
        with zipfile.ZipFile(temp,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=9,allowZip64=True)as z:
            for x in selected:z.writestr(x['member'],x['bytes'])
            z.writestr(omission_name,omission_bytes);z.writestr('05_CONTROL/MANIFIESTO_SHA256.json',mb)
        if temp.stat().st_size<=LIMIT:break
        need(optional,'Required literal content exceeds15,000,000 compressed bytes; preserve sources and report conflict')
        drop=optional.pop(0);selected.remove(drop);omitted.append({'source':str(drop['source']),'member':drop['member'],'bytes':len(drop['bytes']),'sha256':drop['sha256'],'reason':'Optional snapshot omitted to respect the15,000,000-byte ZIP limit; full local original preserved.'})
    extracted=work/'extraccion_limpia';extracted.mkdir()
    with zipfile.ZipFile(temp)as z:
        need(z.testzip()is None,'ZIP CRC failure');names=z.namelist();need(len(names)==len(set(names)),'Duplicate ZIP members')
        for info in z.infolist():
            name=member(info.filename);b=z.read(info);target=extracted.joinpath(*PurePosixPath(name).parts);target.parent.mkdir(parents=True,exist_ok=True)
            with target.open('xb')as f:f.write(b)
            validate_content(name,b)
        m=read_json(z.read('05_CONTROL/MANIFIESTO_SHA256.json'))
        for f in m['files']:
            b=(extracted/f['file']).read_bytes();need(len(b)==f['bytes']and sha(b)==f['sha256'],'Content hash mismatch after clean extraction')
        need((extracted/manual['member']).read_bytes()==manual['bytes'],'The current full Manual bytes were not transported intact')
    pure_runs=[]
    for run in config.get('pure_recalculations',[]):
        missing=[name for name in run.get('requires_optional_members',[])if not(extracted/member(name)).is_file()]
        if missing:
            need(run.get('skip_if_optional_evidence_omitted')is True,'Missing required evidence for archived recalc')
            pure_runs.append({'script':run['script'],'status':'NOT_RUN_OPTIONAL_EVIDENCE_OMITTED','missing_members':missing,'Native_executed':False})
            continue
        script=member(run['script']);need(Path(script).name in PURE,'Not an authorized pure analysis runner')
        sp=extracted/script;need(sp.is_file(),'Missing pure runner in extraction');source=sp.read_text('utf-8-sig');tree=ast.parse(source)
        for node in ast.walk(tree):
            module=node.module if isinstance(node,ast.ImportFrom)else None
            if isinstance(node,ast.Import):need(not any(n.name.split('.')[0]in('dee_thinking','capacidades','app')for n in node.names),'Native/operational import in purported pure script')
            if module:need(module.split('.')[0]not in('dee_thinking','capacidades','app'),'Native/operational import in purported pure script')
        args=run.get('args',[])
        for arg in args:
            need(isinstance(arg,str),'Literal pure-run argument')
            if not arg.startswith('--'):member(arg)
        result=subprocess.run([sys.executable,'-I','-B',str(sp),*args],cwd=extracted,capture_output=True,text=True,timeout=min(180,int(run.get('timeout_seconds',180))))
        need(result.returncode==0,'Pure recalculation failed: '+Path(script).name+'\n'+result.stderr[-3000:])
        output=extracted/member(run['output']);value=read_json(output.read_bytes());need(value.get('Native_executed')is False,'Pure-run output did not explicitly report Native0')
        if 'schema'in run:need(value.get('schema')==run['schema'],'Unexpected extracted recalculation schema')
        pure_runs.append({'script':script,'script_sha256':sha(sp.read_bytes()),'returncode':0,'output':run['output'],'output_sha256':sha(output.read_bytes()),'Native_executed':False})
    for x in planned:need(x['source'].read_bytes()==x['bytes'],'Selected original changed during packaging; no final seal: '+str(x['source']))
    need(not zipout.exists(),'Do not replace a concurrent prior delivery')
    with zipout.open('xb')as f:f.write(temp.read_bytes())
    need(zipout.stat().st_size<=LIMIT and sha(zipout.read_bytes())==sha(temp.read_bytes()),'Final ZIP copy/size verification')
    report={'schema':'DEE.PI10.final_analysis_archive_verification.R02','ZIP':str(zipout),'bytes':zipout.stat().st_size,'sha256':sha(zipout.read_bytes()),
      'cut_utc':datetime.now(timezone.utc).isoformat(),'standard_Deflate':True,'CRC_all_members':True,'all_content_hashes_verified':True,
      'clean_extraction':str(extracted),'literal_current_manual_verified':True,'pure_recalculations':pure_runs,'Native_executed':False,
      'sources_unchanged_in_observed_readback':len(planned),'omitted_optional_snapshots':len(omitted),'members':len(m['files'])+1,
      'scope':'Packaging/readback/pure archived-data recalculation only, not a new Native reproduction, a full executable backup or proof that every project file remained immutable.'}
    with(work/'VERIFICACION_FINAL_EXTERNA.json').open('x',encoding='utf8')as f:json.dump(report,f,ensure_ascii=False,indent=2);f.write('\n')
    return report

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--seleccion',type=Path,required=True);p.add_argument('--trabajo',type=Path,required=True);p.add_argument('--zip',type=Path,required=True);args=p.parse_args()
    print(json.dumps(build(read_json(args.seleccion.read_bytes()),args.trabajo,args.zip),ensure_ascii=False,indent=2))
if __name__=='__main__':main()
