"""Root explicit additive stable pair preservation; no Native/owner/source writes."""
from pathlib import Path
import argparse,datetime,hashlib,json,os,shutil,sqlite3
H=Path(__file__).resolve().parent;P=H.parent;C=P.parents[2]/'DEE Cognitive 2.0'
SRC=P/'pares/REAL_PREFI_T817876';DST=C/'reproducibilidad/materiales/PI03_PI05_REAL_PREFI_T817876'
def sha(p):
    h=hashlib.sha256()
    with p.open('rb')as f:
        for b in iter(lambda:f.read(1048576),b''):h.update(b)
    return h.hexdigest()
def regular(p):
    for q in(p,*p.parents):
        if q.exists()and(q.is_symlink()or getattr(q.lstat(),'st_file_attributes',0)&1024):raise ValueError('No linked stable pair path')
def verify(root,expected):
    regular(root);index=root/'EXPORTACION_SERVICIO.json'
    if sha(index)!=expected:raise ValueError('Frozen complete pair manifest differs')
    m=json.loads(index.read_text('utf8'));seen=set();total=0
    if m['schema']!='DEE.persistent_service.paired_export.v1'or m['physical']['N']!=67 or m['physical']['tick']!=817876:raise ValueError('Exact full preFI817876 pair required')
    for row in m['members']:
        name=Path(row['file'])
        if name.is_absolute()or '..'in name.parts or row['file']in seen:raise ValueError('Unsafe/repeated paired member')
        p=(root/name);regular(p)
        if not p.resolve().is_relative_to(root.resolve())or not p.is_file()or p.stat().st_size!=row['bytes']or sha(p)!=row['sha256']:raise ValueError('Paired member differs: '+row['file'])
        seen.add(row['file']);total+=row['bytes']
    actual={p.relative_to(root).as_posix()for p in root.rglob('*')if p.is_file()and p!=index}
    if actual!=seen or not {'VIDA.deetsnap.gz','cola.sqlite3'}<=seen:raise ValueError('Incomplete or extra paired files')
    for p in root.rglob('*'):regular(p)
    if sha(root/'VIDA.deetsnap.gz')!=m['snapshot_sha256']:raise ValueError('Snapshot hash differs')
    db=root/'cola.sqlite3'
    if any(Path(str(db)+s).exists()for s in('-wal','-shm','-journal')):raise ValueError('SQLite auxiliaries not a standalone full pair')
    q=sqlite3.connect(db.resolve().as_uri()+'?mode=ro&immutable=1',uri=True)
    try:
        if q.execute('pragma integrity_check').fetchone()[0]!='ok':raise ValueError('Corrupt frozen SQLite')
        statuses=dict(q.execute('select status,count(*)from requests group by status'))
        if any(statuses.get(x,0)for x in('queued','processing','uncertain','failed_preserved')):raise ValueError('Unresolved source pair transport')
    finally:q.close()
    return m,{'members':len(seen),'bytes':total,'manifest_sha256':expected,'snapshot_sha256':m['snapshot_sha256'],'transport_status_counts':statuses}
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--aplicar',action='store_true');ar=ap.parse_args()
    request=json.loads((H/'RP_GUARDIA_PI05_R01_PREPARADA/SOLICITUD_MATERIALES.json').read_text('utf8'))
    expected=request['complete_pair']['manifest_sha256'];m,before=verify(SRC,expected)
    regular(DST)
    if not DST.resolve(strict=False).is_relative_to((C/'reproducibilidad/materiales').resolve()):raise ValueError('Exact stable RP store only')
    reused=DST.exists();action='VERIFIED_EXISTING'if reused else'PLAN_ONLY'
    if reused:after=verify(DST,expected)[1]
    elif ar.aplicar:
        DST.mkdir(parents=True,exist_ok=False)
        for base,dirs,files in os.walk(SRC,followlinks=False):
            base=Path(base);rel=base.relative_to(SRC)
            for d in dirs:(DST/rel/d).mkdir(parents=True,exist_ok=True)
            for name in files:
                source=base/name;target=DST/rel/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,target)
        after=verify(DST,expected)[1];action='COPIED_VERIFIED'
    else:after=None
    original_after=verify(SRC,expected)[1]
    if original_after!=before:raise ValueError('Original immutable pair changed; preserve destination')
    proof={'schema':'DEE.PI05.stable_RP_fullpair_preservation.R01','source':str(SRC),'destination':str(DST),'action':action,
       'Native_executed':False,'new_ticks':0,'source_before':before,'source_after':original_after,'stable_copy':after,
       'alias':'PI03_PI05_REAL_PREFI_T817876','resources_registered':False,'original_code_states_selectors_modified':False,
       'at':datetime.datetime.now(datetime.timezone.utc).isoformat()}
    out=P/'control'/('PREFI_GUARDIA_RP_PI05_'+('PRESERVADO'if ar.aplicar or reused else'PLAN')+'.json')
    if out.exists():raise ValueError('Prior stable-preservation proof protected')
    out.write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps(proof,ensure_ascii=False))
if __name__=='__main__':main()
