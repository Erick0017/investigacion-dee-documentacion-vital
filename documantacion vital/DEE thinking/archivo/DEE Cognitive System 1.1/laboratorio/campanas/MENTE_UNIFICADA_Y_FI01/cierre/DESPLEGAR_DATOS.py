"""Despliega un análisis solidario, sin motor, red ni ticks DEE.

Valida el contenedor y cada byte original; nunca utiliza extractall ni sigue
enlaces. El destino y el recibo deben ser nuevos y estar fuera del contenedor.
"""
from __future__ import annotations
import argparse,hashlib,json,os,stat,sys,tarfile
from pathlib import Path,PurePosixPath

OUTER_MANIFEST='MANIFIESTO_CONTENEDOR.json'
INDEX='INDICE_COMPRESION_SOLIDARIA.json'
INNER_MANIFEST='MANIFIESTO_HASHES.json'
PAYLOAD='DATOS_ANALISIS.tar.xz'

def digest_file(p):
    h=hashlib.sha256()
    with Path(p).open('rb')as f:
        for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
    return h.hexdigest()

def safe_name(name):
    if not isinstance(name,str)or not name or '\\'in name or ':'in name or any(ord(c)<32 for c in name):raise ValueError('Nombre inseguro: '+repr(name))
    p=PurePosixPath(name)
    if p.is_absolute()or p.as_posix()!=name or any(x in('','..','.')for x in p.parts):raise ValueError('Ruta no canónica: '+repr(name))
    reserved={'CON','PRN','AUX','NUL',*[f'COM{i}'for i in range(1,10)],*[f'LPT{i}'for i in range(1,10)]}
    if any(x.endswith((' ','.'))or x.split('.')[0].upper()in reserved or any(c in x for c in '<>"|?*')for x in p.parts):raise ValueError('Ruta no portable Windows: '+name)
    return p

def no_link(p):
    st=p.lstat()
    if stat.S_ISLNK(st.st_mode)or getattr(st,'st_file_attributes',0)&0x400:raise ValueError('No se admiten enlaces/reparse points: '+str(p))
    return st

def scan_tree(root):
    root=Path(root).resolve(strict=True);found={};folded=set()
    for folder,dirs,files in os.walk(root,followlinks=False):
        for name in dirs:
            p=Path(folder)/name;no_link(p);safe_name(p.relative_to(root).as_posix())
        for name in files:
            p=Path(folder)/name;st=no_link(p)
            if not stat.S_ISREG(st.st_mode):raise ValueError('Miembro no regular: '+str(p))
            rel=p.relative_to(root).as_posix();safe_name(rel)
            if rel.casefold()in folded:raise ValueError('Colisión de nombres Windows: '+rel)
            folded.add(rel.casefold());found[rel]=p
    return found

def records(manifest,self_name):
    rows=manifest.get('members')
    if not isinstance(rows,list):raise ValueError('Manifiesto sin members list')
    result={};folded=set()
    for r in rows:
        name=r['path'];safe_name(name)
        if name==self_name or name in result or name.casefold()in folded:raise ValueError('Miembro repetido/autorreferente: '+name)
        if type(r.get('bytes'))is not int or r['bytes']<0:raise ValueError('Tamaño de miembro inválido')
        h=r.get('sha256')
        if not isinstance(h,str)or len(h)!=64 or any(c not in'0123456789abcdef'for c in h):raise ValueError('SHA inválido: '+name)
        result[name]=r;folded.add(name.casefold())
    return result

def verify_tree(root,manifest_name):
    found=scan_tree(root);m=json.loads(found[manifest_name].read_bytes());expected=records(m,manifest_name)
    if set(found)!=set(expected)|{manifest_name}:raise ValueError({'missing':sorted(set(expected)-set(found)),'extra':sorted(set(found)-set(expected)-{manifest_name})})
    for name,row in expected.items():
        p=found[name]
        if p.stat().st_size!=row['bytes']or digest_file(p)!=row['sha256']:raise ValueError('Bytes distintos: '+name)
    return found,m,expected

def copy_member(tf,member,dest,row):
    p=dest/Path(*safe_name(member.name).parts)
    p.parent.mkdir(parents=True,exist_ok=True)
    for parent in p.parents:
        if parent==dest.parent:break
        no_link(parent)
    stream=tf.extractfile(member)
    if stream is None:raise ValueError('Miembro sin datos')
    h=hashlib.sha256();count=0
    with stream,p.open('xb')as out:
        for block in iter(lambda:stream.read(1024*1024),b''):
            count+=len(block)
            if count>row['bytes']:raise ValueError('Miembro excede tamaño declarado')
            h.update(block);out.write(block)
    if count!=row['bytes']or h.hexdigest()!=row['sha256']:raise ValueError('SHA/tamaño original no coincide: '+member.name)

def deploy(root,destination):
    root=Path(root).resolve(strict=True);dest=Path(destination).resolve()
    if dest.exists()or dest.is_relative_to(root):raise ValueError('El destino debe ser NUEVO y estar fuera de la extracción del contenedor')
    outer,_,_=verify_tree(root,OUTER_MANIFEST);idx=json.loads(outer[INDEX].read_bytes())
    if idx.get('schema')!='DEE.analysis.lossless_solid_container.v1'or idx['payload']['file']!=PAYLOAD:raise ValueError('Formato de contenedor incorrecto')
    payload=outer[PAYLOAD]
    if digest_file(payload)!=idx['payload']['sha256']or payload.stat().st_size!=idx['payload']['bytes']:raise ValueError('Payload alterado')
    dest.mkdir(parents=True,exist_ok=False);seen=set();total=0
    with tarfile.open(payload,mode='r|xz',ignore_zeros=True)as tf:
        iterator=iter(tf);first=next(iterator,None)
        if first is None or first.name!=INNER_MANIFEST or first.type!=tarfile.REGTYPE or first.linkname or first.issparse():raise ValueError('El primer miembro debe ser el manifiesto original regular')
        original=idx['original_manifest']
        if first.size!=original['bytes']:raise ValueError('Tamaño del manifiesto original incorrecto')
        copy_member(tf,first,dest,original);data=(dest/INNER_MANIFEST).read_bytes();expected=records(json.loads(data),INNER_MANIFEST)
        seen.add(INNER_MANIFEST);total+=first.size
        if len(expected)+1!=idx['original_file_count']:raise ValueError('Número de originales distinto del índice exterior')
        for member in iterator:
            safe_name(member.name)
            if member.type!=tarfile.REGTYPE or member.linkname or member.issparse():raise ValueError('Enlace, directorio especial o sparse no permitido: '+member.name)
            if member.name in seen or member.name not in expected:raise ValueError('Miembro extra/repetido: '+member.name)
            row=expected[member.name]
            if member.size!=row['bytes']:raise ValueError('Tamaño tar distinto del original: '+member.name)
            copy_member(tf,member,dest,row);seen.add(member.name);total+=member.size
    if seen!=set(expected)|{INNER_MANIFEST}or total!=idx['original_expanded_bytes']:raise ValueError('Extracción incompleta o miembros adicionales')
    verify_tree(dest,INNER_MANIFEST)
    return {'status':'EXACT_ORIGINAL_TREE_RESTORED','original_files':len(seen),'original_expanded_bytes':total,'original_manifest_sha256':digest_file(dest/INNER_MANIFEST),
      'payload_sha256':digest_file(payload),'destination':str(dest),'all_original_names_and_bytes_preserved':True,'native_ticks':0,
      'next_command':'python "'+str(dest/'RECALCULO/REPETIR_TODO.py')+'" --salida NUEVA_CARPETA_FUERA_DEL_ARBOL_DESPLEGADO',
      'scope':'Descompresión/validación archivada únicamente. No motor DEE, snapshots cargados, aprendizaje ni reproducción nativa.'}

def main():
    sys.stdout.reconfigure(encoding='utf8');sys.stderr.reconfigure(encoding='utf8')
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--destino',type=Path,required=True);ap.add_argument('--verificacion',type=Path);a=ap.parse_args()
    root=Path(__file__).resolve().parents[1];dest=a.destino.resolve();report=(a.verificacion or Path(str(dest)+'.VERIFICACION_EXTERNA.json')).resolve()
    if report.exists()or report.is_relative_to(root.resolve())or report.is_relative_to(dest):raise ValueError('El recibo debe ser nuevo y externo a ambos árboles')
    try:r=deploy(root,dest)
    except Exception as error:
        r={'status':'FAILED_PARTIAL_NEW_DESTINATION_PRESERVED','error':{'type':type(error).__name__,'detail':str(error)},'destination':str(dest),'native_ticks':0,'no_original_overwrite':True}
        report.parent.mkdir(parents=True,exist_ok=True);report.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps(r,ensure_ascii=False),file=sys.stderr);return 2
    report.parent.mkdir(parents=True,exist_ok=True);report.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps(r,ensure_ascii=False));return 0
if __name__=='__main__':raise SystemExit(main())
