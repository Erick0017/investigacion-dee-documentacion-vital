"""Closed exact actual product Main pair into PI06 baseline, stdlib only and zero source writes.

The root executes this explicit preservation operation. No DEE import, owner,
tick, material query, re-execution or original metadata change is performed.
It refuses live/ambiguous owners, WAL/SHM, incomplete transport and reparse paths.
"""
from pathlib import Path
from datetime import datetime,timezone
import argparse,ctypes,hashlib,importlib.util,json,os,shutil,sqlite3

SOURCE_LIFE='ECI02_PI03_REPRO_PI04_PI05_MAIN_01'
HERE=Path(__file__).resolve().parent;CAMPAIGN=HERE.parent;PRODUCT=CAMPAIGN.parents[2]/'DEE Cognitive 2.0';RP=PRODUCT/'reproducibilidad';PARSER=RP/'observador_pasivo.py'
PARSER_SHA='dbb2a5e15d70c64112d36505197f4aebf6ff7d4092972923e17cd60c10a1c873'
ANTECEDENT={'file':'codigo/exportar_corte_PI05_R02.py','sha256':'52e25d7442f519c174e104690d3a60ced5a5ba4e2a1b12b8c29a64bae0e5ddf8'}
KEY='DEE.Cognitive.System.1.1.PERSISTENT_SERVICE.v1'
def sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb')as f:
        for b in iter(lambda:f.read(1048576),b''):h.update(b)
    return h.hexdigest()
def canon(v):return json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False)
def regular(path):
    for p in(path,*path.parents):
        if p.exists()and(p.is_symlink()or getattr(p.lstat(),'st_file_attributes',0)&1024):raise ValueError('No reparse/symlink source or destination: '+str(p))
def load_code(path,name):
    spec=importlib.util.spec_from_file_location(name,path);mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);return mod
def pid_closed(pid):
    if os.name!='nt':raise ValueError('Windows scoped process proof required')
    kernel=ctypes.WinDLL('kernel32',use_last_error=True)
    kernel.OpenProcess.argtypes=[ctypes.c_uint32,ctypes.c_int,ctypes.c_uint32];kernel.OpenProcess.restype=ctypes.c_void_p
    handle=kernel.OpenProcess(0x1000,False,pid)
    if not handle:
        err=ctypes.get_last_error()
        if err!=87:raise OSError(err,'Cannot prove cached owner PID absent')
        return {'pid':pid,'exists':False,'query':'OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION)','windows_error':err}
    try:
        code=ctypes.c_uint32()
        if not kernel.GetExitCodeProcess(ctypes.c_void_p(handle),ctypes.byref(code)):raise ctypes.WinError(ctypes.get_last_error())
        if code.value==259:raise ValueError('Cached owner PID is alive/reused; preserve source and stop')
        return {'pid':pid,'exists':True,'exited':True,'exit_code':code.value}
    finally:kernel.CloseHandle(ctypes.c_void_p(handle))
def tree(path):
    if not path.is_dir():raise ValueError('Missing complete source tree: '+str(path))
    out=[];dirs=[]
    for base,dnames,fnames in os.walk(path,followlinks=False):
        base=Path(base);regular(base)
        for n in dnames:regular(base/n)
        dirs.append(base.relative_to(path).as_posix())
        for n in sorted(fnames):
            p=base/n;regular(p)
            if not p.is_file():raise ValueError('Nonregular source member')
            out.append((p,p.relative_to(path)))
    return out,dirs
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--sistema-source',type=Path,required=True);ap.add_argument('--vida',required=True);ap.add_argument('--tick',type=int,required=True)
    ap.add_argument('--destino',type=Path);ap.add_argument('--parser',type=Path,default=PARSER)
    ar=ap.parse_args();regular(ar.sistema_source.absolute());regular(RP);regular(RP/'materiales');regular(PARSER);s=ar.sistema_source.resolve(strict=True)
    parent=(CAMPAIGN/'pares').resolve(strict=True);expected=parent/('BASE_MAIN_T'+str(ar.tick));dest=(expected if ar.destino is None else ar.destino).resolve(strict=False);regular(s);regular(dest)
    if dest!=expected or dest.parent!=parent or dest.exists():raise ValueError('Only one new exact PI06 baseline export from the actual closed product Main; no arbitrary path, intermediate or overwrite')
    if ar.parser.resolve(strict=True)!=PARSER.resolve(strict=True)or sha(PARSER)!=PARSER_SHA:raise ValueError('Exact preserved passive stdlib parser only')
    s5=(PRODUCT/'sistema').resolve(strict=True)
    if s!=s5 or ar.vida!=SOURCE_LIFE:raise ValueError('Exact actual closed product Main source only')
    if not 0<ar.tick<1000000000:raise ValueError('Explicit exact expected current tick required')
    life=s/'estado/vidas'/ar.vida;service=s/'estado/servicios_persistentes'/ar.vida;worker=s/'estado/servicios_locales'/ar.vida
    regular(life);regular(service);regular(worker)
    if (s/'estado/locks'/(ar.vida+'.lock')).exists()or(life/'FUTURO_INTERRUMPIDO.json').exists():raise ValueError('Locked or interrupted source')
    db=service/'cola.sqlite3'
    if any(Path(str(db)+x).exists()for x in('-wal','-shm','-journal')):raise ValueError('Source SQLite auxiliaries exist; no incoherent copy')
    card_path=life/'VIDA.json';history=life/'HISTORIA.jsonl';card=json.loads(card_path.read_text('utf8'));snap=(s/card['snapshot']).resolve(strict=True)
    if not snap.is_relative_to(s)or card['life_id']!=ar.vida or card['profile']!='fisica_directa':raise ValueError('Source identity/pointer mismatch')
    regular(snap);critical={str(p):sha(p)for p in(card_path,history,snap,db)}
    if critical[str(snap)]!=card['snapshot_sha256']:raise ValueError('Snapshot encoded identity differs')
    parser=load_code(ar.parser.resolve(strict=True),'PI05_passive_snapshot_parser');view=parser.snapshot_view(snap)
    if any(view['physical'][k]!=card['physical'][k]for k in('N','tick','RAW_sha256','clocks_sha256'))or view['physical']['N']!=67 or view['physical']['tick']!=ar.tick or view['pending_native']:
        raise ValueError('Only exact coherent expected full prefix')
    native=json.loads(view['metadata'][KEY])
    if native['native_tick_at_checkpoint']!=ar.tick or not native['paused']or native['uncertain_external_result']:
        raise ValueError('Source Native owner protocol not coherently paused')
    con=sqlite3.connect(db.as_uri()+'?mode=ro&immutable=1',uri=True);con.row_factory=sqlite3.Row
    try:
        if con.execute('PRAGMA integrity_check').fetchone()[0]!='ok':raise ValueError('SQLite integrity failure')
        owner=json.loads(con.execute("select value from meta where key='owner'").fetchone()[0])
        counts=dict(con.execute('select status,count(*) from requests group by status').fetchall())
        if owner['running']or owner['tick']!=ar.tick or owner.get('uncertain_external_result')or any(counts.get(x,0)for x in('queued','processing','uncertain','failed_preserved')):
            raise ValueError('No live/ambiguous/unfinished source transport')
        process=pid_closed(int(owner['pid']))
        receipt=native['last_completed_receipt'];identifier=receipt['id']
        row=con.execute('select * from requests where id=?',(identifier,)).fetchone()
        if row is None or row['status']!='completed'or row['payload_sha']!=receipt['payload_sha256']:raise ValueError('Last Native receipt not reconciled with closed SQLite')
        outbox=service/'resultados'/(identifier+'.json')
        if not outbox.is_file()or sha(outbox)!=receipt['result_sha256']:raise ValueError('Last Native outbox receipt differs')
    finally:con.close()
    report=dest.parent/(dest.name+'_PRESERVACION.json')
    if report.exists():raise ValueError('Proof destination already exists; preserve prior evidence')
    roots=[(service/'resultados',Path('resultados')),(worker,Path('artefactos_trabajador'))]
    sources=[(snap,Path('VIDA.deetsnap.gz')),(db,Path('cola.sqlite3')),(card_path,Path('procedencia/VIDA_ORIGINAL.json')),(history,Path('procedencia/HISTORIA_ORIGINAL.jsonl'))]
    directories=[]
    for root,prefix in roots:
        members,dirs=tree(root);sources.extend((p,prefix/r)for p,r in members)
        directories.extend((prefix/Path(d)).as_posix()for d in dirs)
    before={str(p):{'bytes':p.stat().st_size,'sha256':sha(p)}for p,_ in sources}
    dest.mkdir(parents=True,exist_ok=False)
    for name in directories:(dest/name).mkdir(parents=True,exist_ok=True)
    rows=[]
    for p,relative in sources:
        target=dest/relative;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,target)
        h=sha(target)
        if h!=before[str(p)]['sha256']or target.stat().st_size!=before[str(p)]['bytes']:raise ValueError('Export copy mismatch; partial destination preserved')
        rows.append({'file':relative.as_posix(),'bytes':target.stat().st_size,'sha256':h})
    after={str(p):{'bytes':p.stat().st_size,'sha256':sha(p)}for p,_ in sources}
    if before!=after or any(sha(Path(p))!=h for p,h in critical.items()):raise ValueError('Concurrent source change; partial destination preserved')
    m={'schema':'DEE.persistent_service.paired_export.v1','life_id':ar.vida,'profile':card['profile'],'backend':'mente_unificada',
       'native_snapshot':'VIDA.deetsnap.gz','snapshot_sha256':card['snapshot_sha256'],'physical':card['physical'],
       'members':rows,'queue_journal_required':True,'source_record':{'life_id':ar.vida,'world_id':card['world_id'],'parent':card.get('parent')},
       'no_engine_or_WHL':True,'not_a_new_cognitive_acquisition':True,'empty_directories_preserved':sorted(directories),
       'scope':'Closed-file exact paired preservation; no Native owner/export operation, no source metadata changes. Standard compatible paired-export schema plus explicit directories/provenance.'}
    (dest/'EXPORTACION_SERVICIO.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    proof={'schema':'DEE.PI06.actual_product_closed_paired_preservation.R01','source_system':str(s),'life_id':ar.vida,'source_tick':ar.tick,
       'destination':str(dest),'manifest_sha256':sha(dest/'EXPORTACION_SERVICIO.json'),'snapshot_sha256':card['snapshot_sha256'],
       'members':len(rows),'bytes':sum(x['bytes']for x in rows),'directories':len(directories),'process_proof':process,
       'cached_owner_observed':owner['wall_utc'],'inspection_utc':datetime.now(timezone.utc).isoformat(),
       'Native_service_last_receipt':receipt,'queue_status_counts':counts,'source_files_all_unchanged':before==after,
       'physical':view['physical'],'causal_prefix_sha256':view['causal_prefix_sha256'],'Native_executed':False,'new_ticks':0,
       'internal_snapshot_FNV':'not recalculated here; official later Native import must validate',
       'source_exporter_version':'PI06_R01_exact_product_Main_only','direct_current_product_baseline_export':True,'no_intermediate_or_second_pair_copy':True,'antecedent':ANTECEDENT,'passive_parser_sha256':PARSER_SHA,'source_sha256':critical,'source_copy_member_hashes':rows}
    report=dest.parent/(dest.name+'_PRESERVACION.json')
    if report.exists():raise ValueError('Proof destination already exists; do not overwrite')
    report.write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps({k:v for k,v in proof.items()if k!='source_copy_member_hashes'},ensure_ascii=False))
if __name__=='__main__':main()
