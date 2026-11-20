"""Traslados reversibles dentro de DEE thinking y registro técnico único."""
from pathlib import Path
import os,sys,json,hashlib,datetime,base64,shutil,argparse
W=Path(__file__).resolve().parent
ROOT=W.parent.parent
LOG=W/'REGISTRO_REORGANIZACION.json'
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def read():return json.loads(LOG.read_text(encoding='utf8'))
def write(d):
    t=LOG.with_suffix('.tmp');t.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8');os.replace(t,LOG)
def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
    return h.hexdigest()
def inside(p):
    p=Path(p).resolve();assert p.is_relative_to(ROOT) and p!=ROOT,p;return p
def tree(p,content=False):
    p=inside(p);rows=[];errors=[]
    if p.is_file():files=[p]
    else:
        files=[]
        for folder,dirs,names in os.walk(p,followlinks=False,onerror=lambda e:errors.append(str(e))):
            for name in list(dirs):
                q=Path(folder)/name
                if q.is_symlink() or q.is_junction():
                    errors.append('reparse_point:'+str(q));dirs.remove(name)
            files.extend(Path(folder)/n for n in names)
    for f in sorted(files,key=lambda f:str(f.relative_to(p)) if p.is_dir() else f.name):
        s=f.stat();rel=f.relative_to(p).as_posix() if p.is_dir() else f.name
        row=[rel,s.st_ino,s.st_size,s.st_mtime_ns]
        if content:row.append(sha(f))
        rows.append(row)
    return {'files':len(rows),'bytes':sum(r[2] for r in rows),'metadata_identity_sha256':hashlib.sha256(json.dumps(rows,separators=(',',':')).encode()).hexdigest(),'content_sha256':hashlib.sha256(json.dumps([[r[0],r[-1]] for r in rows],separators=(',',':')).encode()).hexdigest() if content else None,'entries':rows if content else None,'errors':errors,'method':'All file identities/sizes/mtime plus SHA256 of every member' if content else 'All relative paths, NTFS file identities, sizes, mtime; atomic same-volume rename, no file rewrite'}
def baseline():
    d=read();d['inicio_utc']='2026-10-28T19:18:15+00:00'
    if 'plataforma_4_5_antes' not in d:
        d['plataforma_4_5_antes']=tree(ROOT/'4.5',True);print('4.5',d['plataforma_4_5_antes']['files'],flush=True)
    if 'estado_operativo_antes' not in d:
        d['estado_operativo_antes']=tree(ROOT/'DEE Cognitive 2.0/sistema/estado',True);print('ESTADO',d['estado_operativo_antes']['files'],flush=True)
    write(d)
def preserve_edit(path,newbytes,reason):
    path=inside(path);d=read();old=path.read_bytes()
    if old==newbytes:return
    d['cambios_activos'].append({'utc':now(),'path':str(path.relative_to(ROOT)),'motivo':reason,'antes_sha256':hashlib.sha256(old).hexdigest(),'despues_sha256':hashlib.sha256(newbytes).hexdigest(),'original_base64':base64.b64encode(old).decode()})
    write(d);tmp=path.with_name(path.name+'.reorg_tmp');tmp.write_bytes(newbytes);os.replace(tmp,path)
def move(source,target):
    source=inside(ROOT/source);target=inside(ROOT/target)
    assert source.exists() and not target.exists(),(source,target)
    assert source.drive.lower()==target.drive.lower()
    before=tree(source,source.is_file());assert not before['errors'],before['errors']
    target.parent.mkdir(parents=True,exist_ok=True)
    d=read();item={'utc':now(),'source':str(source.relative_to(ROOT)),'destination':str(target.relative_to(ROOT)),'before':before,'status':'PREPARED'};d['movimientos'].append(item);write(d)
    os.rename(source,target)
    after=tree(target,target.is_file())
    assert before['files']==after['files'] and before['bytes']==after['bytes'] and before['metadata_identity_sha256']==after['metadata_identity_sha256'],(source,target)
    if before['content_sha256']:assert before['content_sha256']==after['content_sha256']
    d=read();d['movimientos'][-1].update({'status':'MOVED_VERIFIED','after':after});d['reversion'].append({'source':str(target.relative_to(ROOT)),'destination':str(source.relative_to(ROOT)),'method':'same-volume atomic rename; only if original path is absent and no writer is active'});write(d)
    print('MOVED',source.name,before['files'],before['bytes'],flush=True)
def move_atomic_directory(source,target):
    source=inside(ROOT/source);target=inside(ROOT/target)
    assert source.is_dir() and not target.exists() and source.drive.lower()==target.drive.lower()
    def signature(p):
        st=p.stat();children=[]
        for f in sorted(p.iterdir(),key=lambda x:x.name):
            s=f.lstat();children.append([f.name,s.st_ino,s.st_size,s.st_mtime_ns,s.st_mode])
        return {'NTFS_directory_id':st.st_ino,'volume':st.st_dev,'direct_children':children,'method':'Atomic rename on the same NTFS volume; root and immediate children retain their file IDs. No descendant content is rewritten. Canonical evidence hashes and operative state are verified separately.'}
    before=signature(source);target.parent.mkdir(parents=True,exist_ok=True)
    d=read();d['movimientos'].append({'utc':now(),'source':str(source.relative_to(ROOT)),'destination':str(target.relative_to(ROOT)),'before':before,'status':'PREPARED_ATOMIC'});write(d)
    os.rename(source,target);after=signature(target)
    assert before['NTFS_directory_id']==after['NTFS_directory_id'] and before['volume']==after['volume'] and before['direct_children']==after['direct_children']
    d=read();d['movimientos'][-1].update(status='MOVED_ATOMIC_IDENTITY_VERIFIED',after=after);d['reversion'].append({'source':str(target.relative_to(ROOT)),'destination':str(source.relative_to(ROOT)),'method':'Atomic same-volume rename; verify absence of writers and original path.'});write(d)
    print('ATOMIC_MOVED',source.name,before['NTFS_directory_id'],flush=True)
if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('action',choices=['baseline','move','move-atomic']);a.add_argument('paths',nargs='*');n=a.parse_args()
    if n.action=='baseline':baseline()
    else:
        assert len(n.paths)==2
        (move_atomic_directory if n.action=='move-atomic' else move)(*n.paths)
