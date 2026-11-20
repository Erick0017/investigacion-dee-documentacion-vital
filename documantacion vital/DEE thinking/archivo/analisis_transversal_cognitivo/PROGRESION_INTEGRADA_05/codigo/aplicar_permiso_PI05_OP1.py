"""Root-only explicit CAS installation into isolated S5; no DEE imports."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,hashlib,importlib.util,json,os,sqlite3,uuid

HERE=Path(__file__).resolve().parent;P=HERE.parent;S=P/'estados/candidato/sistema';PATCH=HERE/'FUENTES_PERMISO_PI05_OP1_CANDIDATAS'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def regular(p):
    for q in(p,*p.parents):
        if q.exists()and(q.is_symlink()or getattr(q.lstat(),'st_file_attributes',0)&1024):raise ValueError('No linked patch/system path')
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--aplicar',action='store_true');args=ap.parse_args()
    regular(S);regular(PATCH)
    if not S.resolve().is_relative_to(P.resolve())or not S.is_dir():raise ValueError('Exact isolated S5 only')
    manifest=json.loads((PATCH/'MANIFIESTO_CAMBIOS_PI05.json').read_text('utf8'))
    if Path(manifest['source_system']).resolve()!=S.resolve():raise ValueError('Patch built against another system')
    sources=[]
    for row in manifest['files']:
        rel=Path(row['file'])
        if rel.is_absolute()or'..'in rel.parts:raise ValueError('Unsafe source member')
        source=PATCH/rel;target=S/rel;regular(source);regular(target)
        if sha(source)!=row['sha256']or source.stat().st_size!=row['bytes']:raise ValueError('Prepared source differs')
        old=row['source_before_sha256']
        if(old is None and target.exists())or(old is not None and(not target.is_file()or sha(target)!=old)):
            raise ValueError('S5 source CAS failed; nothing applied: '+str(rel))
        sources.append((row,source,target))
    if manifest.get('permission_activation_contract_installed')is not False:raise ValueError('This patch must not activate a principal permission')
    locks=list((S/'estado/locks').glob('*.lock'))
    if locks:raise ValueError('S5 has an owner lock; do not modify live code')
    spec=importlib.util.spec_from_file_location('PI05_closed_process_guard',HERE/'exportar_prefijo_cerrado_PI05.py');guard=importlib.util.module_from_spec(spec);spec.loader.exec_module(guard)
    process=[]
    for folder in sorted((S/'estado/servicios_persistentes').glob('*')):
        if not folder.is_dir():continue
        db=folder/'cola.sqlite3'
        if not db.is_file():continue
        regular(db)
        if any(Path(str(db)+x).exists()for x in('-wal','-shm','-journal')):raise ValueError('S5 queue auxiliaries still present')
        q=sqlite3.connect(db.resolve().as_uri()+'?mode=ro&immutable=1',uri=True)
        try:
            item=q.execute("select value from meta where key='owner'").fetchone()
            counts=dict(q.execute('select status,count(*) from requests group by status'))
            if any(counts.get(x,0)for x in('queued','processing','uncertain')):raise ValueError('S5 queue has unresolved work')
            if item:
                owner=json.loads(item[0])
                if owner.get('running')or owner.get('uncertain_external_result'):raise ValueError('S5 cached owner not closed')
                if 'pid'in owner:process.append({'life_id':folder.name,**guard.pid_closed(int(owner['pid']))})
        finally:q.close()
    proof={'schema':'DEE.PI05.dormant_permission_source_CAS_install.OP1','inspection_utc':datetime.now(timezone.utc).isoformat(),
           'system':str(S),'patch_manifest_sha256':sha(PATCH/'MANIFIESTO_CAMBIOS_PI05.json'),'files':manifest['files'],
           'scoped_process_proofs':process,'world_locks':[],'Native_executed':False,'Native_ticks':0,'applied':False,
           'protected_product_or_PI04_modified':False}
    if args.aplicar:
        # CAS all inputs again before the first code write. No world/state file
        # or selector is touched. A partial exceptional install is preserved.
        for row,source,target in sources:
            if sha(source)!=row['sha256']or(row['source_before_sha256']is not None and sha(target)!=row['source_before_sha256']):raise ValueError('Concurrent code change before install')
        for row,source,target in sources:
            temp=target.with_name(target.name+'.PI05_'+uuid.uuid4().hex+'.tmp')
            with temp.open('xb')as f:f.write(source.read_bytes());f.flush();os.fsync(f.fileno())
            os.replace(temp,target)
            if sha(target)!=row['sha256']:raise ValueError('Applied source differs')
        proof['applied']=True
    report=P/'control'/('PERMISO_PI05_OP1_'+('APLICADAS'if args.aplicar else'PLAN')+'.json')
    if report.exists():raise ValueError('A prior install/plan proof is protected')
    report.write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps({'applied':proof['applied'],'Native_ticks':0,'proof':str(report),'proof_sha256':sha(report)},ensure_ascii=False))
if __name__=='__main__':main()
