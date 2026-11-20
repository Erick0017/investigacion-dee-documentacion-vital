"""Assemble closed evidence namespaces with exact-byte content deduplication. NO ZIP operation."""
import argparse,gzip,hashlib,json,os,re,shutil,zlib
from pathlib import Path,PurePosixPath

BLOCKED_SUFFIXES={'.whl','.pyd','.dll','.exe','.so','.lib','.obj','.zip'}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,v):
    if p.exists():raise FileExistsError(str(p))
    p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,ensure_ascii=False,sort_keys=True,indent=2)+'\n',encoding='utf8')
def relative(name):
    if not isinstance(name,str)or not name or'\\'in name or':'in name:raise ValueError('Unsafe logical path')
    p=PurePosixPath(name)
    if p.is_absolute()or any(k in('.','..','')for k in p.parts):raise ValueError('Unsafe logical path')
    return p
def files(root):
    root=root.resolve(strict=True);out=[]
    for folder,dirs,names in os.walk(root,followlinks=False):
        for name in dirs+names:
            p=Path(folder)/name;st=p.stat(follow_symlinks=False)
            if p.is_symlink()or getattr(st,'st_file_attributes',0)&0x400:raise ValueError('Refuse symlink/junction/reparse source: '+str(p))
            if name in('node_modules','__pycache__'):raise ValueError('Refuse dependency/cache subtree rather than following it: '+str(p))
        out.extend(Path(folder)/name for name in names)
    return sorted(out)
def ensure_analysis(p):
    if p.name.endswith('.deetsnap.gz')or p.suffix.lower()in BLOCKED_SUFFIXES:raise ValueError('Engine, operational snapshot or archive is not analysis evidence: '+str(p))
    with p.open('rb')as f:head=f.read(8)
    if head.startswith(b'MZ')or head==b'DEETSNP1':raise ValueError('Disallowed engine/native-world binary')
    if head[:2]==b'\x1f\x8b':
        with gzip.open(p,'rb')as f:
            if f.read(8)==b'DEETSNP1':raise ValueError('Disguised dense native snapshot')
def verify_closed_tree(root,manifest_name):
    rows=files(root);m=json.loads((root/manifest_name).read_text(encoding='utf8'))
    expected={};field=None
    for row in m['members']:
        key='path'if'path'in row else'file';name=row[key];relative(name)
        if name in expected:raise ValueError('Repeated source member')
        expected[name]=row
    actual={p.relative_to(root).as_posix()for p in rows}
    if actual!=set(expected)|{manifest_name}:raise ValueError({'stage':str(root),'missing':sorted(set(expected)-actual),'extra':sorted(actual-set(expected)-{manifest_name})})
    for name,row in expected.items():
        p=root/name
        if p.stat().st_size!=row['bytes']or sha(p)!=row['sha256']:raise ValueError('Closed source changed: '+name)
    return rows
def normalize_job(job,namespace,root):
    name=job.get('case',job.get('name'));base=job.get('base','.')
    if base!='.':relative(base)
    if not isinstance(name,str)or not re.fullmatch(r'[A-Za-z0-9_.-]{1,100}',name):raise ValueError('Case name must be portable')
    script=job['script'];relative(script);local=root/base
    if not(local/script).is_file():raise FileNotFoundError(script)
    argv=list(job['args']);outputs=0
    for n,value in enumerate(argv):
        if value in('--salida','--out','--restaurar'):
            if n+1>=len(argv):raise ValueError('Missing output argument')
            argv[n+1]='{output}';outputs+=1
    if outputs!=1 or argv.count('{output}')!=1:raise ValueError('One explicit output expected')
    reference=job.get('reference')
    if reference:
        relative(reference);p=local/reference
        if not p.is_file():raise FileNotFoundError(str(p))
        digest=sha(p);size=p.stat().st_size
        if job.get('reference_sha256',digest)!=digest:raise ValueError('Declared source reference changed')
    else:digest=job['reference_sha256'];size=job['reference_bytes']
    return {'case':namespace+'__'+name,'base':namespace+('/'+base if base!='.'else''),'script':script,'args':argv,
            'reference':reference,'reference_sha256':digest,'reference_bytes':size,'timeout_seconds':job.get('timeout_seconds',180)}

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--config',type=Path,required=True);ap.add_argument('--stage',type=Path,required=True);a=ap.parse_args()
    c=json.loads(a.config.read_text(encoding='utf8'))
    if a.stage.exists():raise FileExistsError('Fresh assembly revision required')
    final=c['status']in('CLOSED_APPROVED_FOR_ANALYSIS','CLOSED_APPROVED_FOR_PACKAGING')
    if not final and'PREPARACION_NO_FINAL'not in a.stage.name:raise ValueError('Partial stages must be labelled PREPARACION_NO_FINAL')
    if final and c.get('pending_components'):raise ValueError('A final assembly cannot keep pending components')
    a.stage.mkdir(parents=True);objects={};namespaces=[];jobs=[];source_stages=[]
    def content(source,public_path=None):
        ensure_analysis(source);digest=sha(source);size=source.stat().st_size
        if digest in objects:
            if objects[digest]['bytes']!=size:raise ValueError('Hash collision/size mismatch')
            return digest,size
        dest=public_path or('OBJETOS/'+digest[:2]+'/'+digest)
        relative(dest);target=a.stage/dest;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,target)
        if sha(source)!=digest or sha(target)!=digest:raise ValueError('Source changed while copying')
        objects[digest]={'storage':dest,'bytes':size};return digest,size
    # Future public reports/manuals can be readable at the top level and still serve aliases without duplicate byte objects.
    for item in c.get('public_files',[]):content(Path(item['source']),item['to'])
    used=set()
    for st in c['stages']:
        ns=st['namespace']
        if not re.fullmatch(r'[A-Z][A-Z0-9_]{0,63}',ns)or ns in used:raise ValueError('Unique safe namespace required')
        used.add(ns);root=Path(st['source']).resolve(strict=True);rows=verify_closed_tree(root,st.get('manifest','MANIFIESTO.json'));members=[]
        for p in rows:
            digest,size=content(p);members.append({'path':p.relative_to(root).as_posix(),'sha256':digest,'bytes':size})
        namespaces.append({'id':ns,'members':members})
        subplan=json.loads((root/st.get('plan','PLAN_RECALCULO.json')).read_text(encoding='utf8'))
        original_jobs=subplan.get('cases',subplan.get('jobs'))
        if not isinstance(original_jobs,list):raise ValueError('Unknown closed-stage recalculation plan')
        for j in original_jobs:jobs.append(normalize_job(j,ns,root))
        for j in st.get('extra_cases',[]):jobs.append(normalize_job(j,ns,root))
        source_stages.append({'namespace':ns,'local_source_locator':str(root),'manifest_sha256':sha(root/st.get('manifest','MANIFIESTO.json')),'logical_members':len(members),'logical_bytes':sum(m['bytes']for m in members)})
    if len({j['case']for j in jobs})!=len(jobs):raise ValueError('Colliding global case names')
    write(a.stage/'INDICE_OBJETOS_Y_ALIASES.json',{'schema':'APD01.lossless_content_objects_and_original_namespace_aliases.v1','objects':objects,'namespaces':namespaces,
          'scope':'Only exact duplicate file contents share storage. Every original logical path, gzip byte and code revision is retained; restoration materializes separate files. This is not a delta on historical folders.'})
    write(a.stage/'PLAN_GLOBAL.json',{'schema':'APD01.global_archived_recalculation_plan.v1','status':c['status'],'native_ticks':0,'cases':jobs,'pending_components':c.get('pending_components',[])})
    write(a.stage/'ESTADO_PREPARACION.json',{'status':c['status'],'campaign_final':final,'native_ticks':0,'ZIP_generated':False,'source_stages':source_stages,'pending_components':c.get('pending_components',[]),
          'scope':'Assembly of closed subsets only. Missing final service/pilot/manual/report/delta are not claimed completed. Full snapshots remain in their original operational/evidence locations, not silently replaced by recipes.'})
    runner=Path(__file__).with_name('repetir_todo_apd_cas.py');shutil.copyfile(runner,a.stage/'REPETIR_TODO.py')
    text=('APD01 — '+('ANÁLISIS CERRADO'if final else'PREPARACIÓN NO FINAL')+'\n\n'
          'Los archivos originales están deduplicados por contenido, no eliminados. INDICE_OBJETOS_Y_ALIASES.json conserva nombres/rutas/SHA256 completos.\n'
          'Ejecute con Python estándar: python -I -B REPETIR_TODO.py --salida UNA_CARPETA_NUEVA_FUERA_DE_ESTA_EXTRACCION'+(''if final else' --permitir-preparacion')+'\n'
          'El comando reconstruye los tres namespaces en la salida, verifica todos los bytes y ejecuta los recálculos sin importar el motor. No continúa vidas.\n'
          'Los campos pendientes se enumeran en ESTADO_PREPARACION.json y PLAN_GLOBAL.json. Este directorio no es un paquete operativo ni confirma estabilidad general.\n')
    (a.stage/('LEER_PRIMERO.md'if final else'LEER_PREPARACION_NO_FINAL.md')).write_text(text,encoding='utf8')
    members=[{'path':p.relative_to(a.stage).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)}for p in files(a.stage)]
    write(a.stage/'MANIFIESTO_HASHES.json',{'members':members,'self_hash_excluded':True})
    logical=sum(x['logical_bytes']for x in source_stages);stored=sum(x['bytes']for x in objects.values());allfiles=files(a.stage)
    print(json.dumps({'status':c['status'],'namespaces':len(namespaces),'logical_files':sum(len(n['members'])for n in namespaces),'unique_objects':len(objects),
                      'logical_bytes':logical,'stored_unique_original_bytes':stored,'exact_duplicate_bytes_avoided':logical-stored,
                      'stage_files':len(allfiles),'stage_expanded_bytes':sum(p.stat().st_size for p in allfiles),
                      'deflate_estimate':sum(len(zlib.compress(p.read_bytes(),9))for p in allfiles),'cases':len(jobs),'ZIP_generated':False,'native_ticks':0}))

if __name__=='__main__':main()
