"""Root-only bounded FS copy continuation after the SINGLE old FS writer ended.

No Native imports/owner/experiences. Four I/O threads, every source and copy
SHA checked. Never run concurrently with preparar_par28_v3.py --shared-only.
Incomplete new R07 copies are preserved outside the official paired prefix.
"""
from pathlib import Path
import argparse,concurrent.futures,ctypes,hashlib,importlib.util,json,os,sqlite3,sys,threading,time
ROOT=Path(__file__).resolve().parents[1]
def need(v,m):
    if not v:raise ValueError(m)
def absent(pid):
    need(os.name=='nt'and type(pid)is int and pid>0,'Exact Windows old FS PID')
    k=ctypes.WinDLL('kernel32',use_last_error=True);k.OpenProcess.restype=ctypes.c_void_p
    handle=k.OpenProcess(0x1000,False,pid)
    if not handle:
        need(ctypes.get_last_error()==87,'Cannot prove old FS process absent');return
    try:
        code=ctypes.c_ulong();need(k.GetExitCodeProcess(ctypes.c_void_p(handle),ctypes.byref(code)),'Old writer status')
        need(code.value!=259,'OLD_FS_WRITER_STILL_ACTIVE_NO_SECOND_WRITER')
    finally:k.CloseHandle(ctypes.c_void_p(handle))
def run(a):
    absent(a.old_writer_pid)
    spec=importlib.util.spec_from_file_location('_r07_frozen_fs_preparer',ROOT/'native/preparar_par28_v3.py')
    m=importlib.util.module_from_spec(spec);sys.modules[spec.name]=m;spec.loader.exec_module(m)
    need(m.START<=time.time()<m.LAST,'Prospective scope expired')
    record,rows=m.source_record();base=ROOT/'persistencia/PREFIJO_PAR28_COMPLETO'
    need(base.is_dir()and not(base/'EXPORTACION_SERVICIO.json').exists(),'Only partial declared shared export may be resumed')
    out=ROOT/'persistencia/REANUDACION_FS_R02';need(not out.exists(),'One new copy continuation proof only');out.mkdir()
    (out/'SINGLE_WRITER_GUARD.json').write_text(json.dumps({'old_fs_pid':a.old_writer_pid,'proved_not_active':True,'new_fs_pid':os.getpid(),'threads':4,'Native_calls':0,'utc_epoch':time.time()},indent=2),encoding='utf8')
    system='native_root/sistema/';card_rel=system+'estado/vidas/'+m.SOURCE+'/VIDA.json';card=m.read(m.PAIR/card_rel)
    need(m.sha(m.PAIR/card_rel)==rows[card_rel]['sha256']and card['snapshot_sha256']==m.SNAPSHOT,'SOURCE_CARD')
    service=system+'estado/servicios_persistentes/'+m.SOURCE+'/';worker=system+'estado/servicios_locales/'+m.SOURCE+'/'
    sources=[(system+card['snapshot'],'VIDA.deetsnap.gz')]
    for name,row in rows.items():
        if name.startswith(worker):sources.append((name,'artefactos_trabajador/'+name[len(worker):]))
        elif name.startswith(service):
            rel=name[len(service):];need(rel!='IMPORTACION_EN_CURSO.json','No pending import')
            if rel in('cola.sqlite3-wal','cola.sqlite3-journal'):need(row['bytes']==0,'No live WAL')
            sources.append((name,rel))
    lock=threading.Lock();counts={'verified_existing':0,'copied_missing':0,'preserved_partial':0};partial=[]
    def one(item):
        src,rel=item;target=base/m.relative(rel);want=rows[src];m.safe(target)
        if target.exists():
            need(target.is_file(),'Existing copy must be a regular file')
            if target.stat().st_size==want['bytes']and m.sha(target)==want['sha256']:
                with lock:counts['verified_existing']+=1
                return
            current=m.sha(target);preserved=out/'FALLOS_COPIA'/m.relative(rel);preserved.parent.mkdir(parents=True,exist_ok=True)
            need(not preserved.exists(),'Preserve unique partial file');os.replace(target,preserved)
            with lock:
                counts['preserved_partial']+=1;partial.append({'file':rel,'preserved':str(preserved),'bytes':preserved.stat().st_size,'sha256':current,'expected_sha256':want['sha256']})
        m.copy_checked(m.PAIR/src,target,want)
        with lock:counts['copied_missing']+=1
    with concurrent.futures.ThreadPoolExecutor(max_workers=4)as pool:
        list(pool.map(one,sources))
    empty=[]
    for directory in record['native_directories']:
        name='native_root/'+directory
        if name.startswith(worker):rel='artefactos_trabajador/'+name[len(worker):]
        elif name.startswith(service):rel=name[len(service):]
        else:continue
        if rel:
            p=base/m.relative(rel);p.mkdir(parents=True,exist_ok=True)
            if not any(p.iterdir()):empty.append(rel)
    con=sqlite3.connect((base/'cola.sqlite3').resolve().as_uri()+'?mode=ro&immutable=1',uri=True)
    try:
        need(con.execute('PRAGMA quick_check').fetchone()[0]=='ok','Closed copied DB integrity')
        need(con.execute("SELECT COUNT(*) FROM requests WHERE status IN('queued','processing','uncertain')").fetchone()[0]==0,'No ambiguous pending future')
    finally:con.close()
    m.recheck_directories();absent(a.old_writer_pid)
    manifest={'schema':'DEE.persistent_service.paired_export.v1','life_id':m.SOURCE,'profile':'fisica_directa','backend':'mente_unificada','native_snapshot':'VIDA.deetsnap.gz',
      'snapshot_sha256':m.SNAPSHOT,'physical':card['physical'],'members':[{'file':rel,'bytes':rows[src]['bytes'],'sha256':rows[src]['sha256']}for src,rel in sources],
      'queue_journal_required':True,'source_record':{'life_id':m.SOURCE,'world_id':m.SOURCE,'parent':card.get('parent')},'empty_directories_preserved':empty,
      'source_PAR28_manifest_sha256':m.PAIR_SHA,'source_PAR28_path':str(m.PAIR),'new_Native_ticks':0,'scope':'Full closed current service; filesystem copy resumed under one writer, four bounded I/O threads; every source/copy SHA verified.'}
    m.new(base/'EXPORTACION_SERVICIO.json',manifest)
    result={'status':'FULL_SHARED_PREFIX_COMPLETE','members':len(sources),'bytes':sum(rows[src]['bytes']for src,_ in sources),'counts':counts,'partials':partial,'manifest':str(base/'EXPORTACION_SERVICIO.json'),'manifest_sha256':m.sha(base/'EXPORTACION_SERVICIO.json'),'Native_calls':0}
    m.new(out/'RESULTADO.json',result);print(json.dumps(result,ensure_ascii=False))
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--root-only-resume-fs',action='store_true');p.add_argument('--old-writer-pid',type=int,required=True);a=p.parse_args()
    need(a.root_only_resume_fs,'Explicit Root FS action only');run(a)
