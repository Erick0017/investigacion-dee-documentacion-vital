"""Bounded passive final-cut locator; NOT a new whole-root inventory or rollback.

Only recorded critical files are rehashed. The complete current system remains
in place. No Native, SQLite, Studio, model, live ledger or original write.
"""
from pathlib import Path
import datetime,hashlib,json,os,stat,time
ROOT=Path(__file__).resolve().parents[1]
NATIVE=ROOT/'native/MAIN';CUT=ROOT/'evidencia/MAIN_REAPERTURA_35_46_R07'
DEST=ROOT/'evidencia/PUNTO46_R07'
LIFE='ECI02_PI03_REPRO_PI04_PI05_PI07_PI10_RBX01_INTEGRAL_V3_MAIN'
PINS={'WORLD_CHECKPOINT.json':'1fa9d6e9207e0743b4459c1382142c1d5bc2dad5868183fde1363ff20f0ed6c8',
      'CONCILIACION_CIERRE_R07.json':'becd84d077c4fb01023593dbea9220fa0e5f2ebfcde8942aab63dd6b66f21a45',
      'LEDGER_AL_CIERRE.json':'98b848d3792bac28140ade66bb86221612474e4a36d5ad8f89888f7f4a845194'}
def need(x,m):
    if not x:raise ValueError(m)
def read(p):return json.loads(Path(p).read_text('utf8'))
def write(p,v):
    with Path(p).open('x',encoding='utf8')as f:json.dump(v,f,ensure_ascii=False,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
def signature(s):return(s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns,s.st_mode,getattr(s,'st_file_attributes',0))
def safe(p):
    p=Path(os.path.abspath(p))
    for q in reversed((p,*p.parents)):
        if q.exists():need(not q.is_symlink()and not getattr(q.lstat(),'st_file_attributes',0)&1024,'NO_REPARSE')
    return p
def run():
    started=time.monotonic();deadline=started+180;created=False
    def bounded():need(time.monotonic()<deadline,'PASSIVE_CRITICAL_LIMIT_180_SECONDS')
    def file(p,expected=None,copy=None):
        bounded();p=safe(p);before=p.lstat();need(stat.S_ISREG(before.st_mode),'REGULAR_FILE_ONLY')
        h=hashlib.sha256();out=None
        try:
            if copy is not None:out=copy.open('xb')
            with p.open('rb')as source:
                need(signature(os.fstat(source.fileno()))==signature(before),'OPEN_IDENTITY_CHANGED')
                count=0
                for b in iter(lambda:source.read(1048576),b''):
                    bounded();h.update(b);count+=len(b)
                    if out:out.write(b)
                need(signature(os.fstat(source.fileno()))==signature(before),'SOURCE_CHANGED_DURING_HASH')
            if out:out.flush();os.fsync(out.fileno())
        finally:
            if out:out.close()
        need(count==before.st_size and signature(p.lstat())==signature(before),'SOURCE_CHANGED_AFTER_HASH')
        actual={'path':str(p),'bytes':count,'sha256':h.hexdigest(),'copy':str(copy)if copy else None}
        if expected:need(actual['sha256']==expected['sha256']and actual['bytes']==expected['bytes'],'RECORDED_CLOSED_FILE_CHANGED')
        return actual
    try:
        safe(DEST);need(not DEST.exists(),'NEW_OUTPUT_ONLY');need(safe(NATIVE).is_dir(),'CURRENT_NATIVE_ROOT_EXISTS')
        c=read(CUT/'CONCILIACION_CIERRE_R07.json');need(c['life']==LIFE and c['owner_closed']['exit_code']==0 and c['owner_closed']['pid']==3352,'OFFICIAL_CLOSED_MAIN')
        need(c['physical_fingerprint_recorded_by_official_owner']['tick']==1019339 and c['transport']['no_pending_or_uncertain']and c['transport']['owner']['running']is False,'EXACT_DRAINED_MAIN46')
        for p in(NATIVE/'sistema/estado/ACTIVO.json',NATIVE/'sistema/estado/locks'/(LIFE+'.lock'),NATIVE/'LEASE_MIGRATION_IN_PROGRESS.json'):
            safe(p);need(not os.path.lexists(p),'NO_OWNER_OR_MIGRATION')
        DEST.mkdir();created=True;write(DEST/'IN_PROGRESS.json',{'pid':os.getpid(),'started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'Native_calls':0})
        anchors={}
        for name,pin in PINS.items():
            p=CUT/name;row=file(p,copy=DEST/name);need(row['sha256']==pin,'FROZEN_CUT_ANCHOR_CHANGED');anchors[name]=row
        critical={}
        for name in('native_card','snapshot','scope','owner_journal'):
            row=c[name];p=Path(row['path']);need(p.is_relative_to(NATIVE),'ONLY_EXACT_MAIN_ROOT')
            critical[name]=file(p,row,DEST/('CRITICAL_'+p.name))
        db=c['transport']['database'];dbp=Path(db['path']);need(dbp.is_relative_to(NATIVE),'ONLY_MAIN_QUEUE')
        for suffix in('-wal','-journal'):
            p=safe(Path(str(dbp)+suffix));need(not p.exists()or p.stat().st_size==0,'CLOSED_QUEUE_NO_NONEMPTY_SIDECAR')
        critical['closed_queue']=file(dbp,db) # no second196MB copy, no SQL connection
        card=read(c['native_card']['path']);need(card['physical']==c['physical_fingerprint_recorded_by_official_owner'],'PHYSICAL_CARD_MATCHES_CLOSED_PROOF')
        need(card['snapshot_sha256']==critical['snapshot']['sha256'],'SNAPSHOT_CARD_SHA_MATCH')
        context=NATIVE/'CONTEXTO_EJECUCION.json';critical['context']=file(context,copy=DEST/'CONTEXTO_EJECUCION.json')
        roots={name:str(p)for name,p in{'diagnostic_root':NATIVE,'system':NATIVE/'sistema','life':NATIVE/'sistema/estado/vidas'/LIFE,
          'worker_artifacts':NATIVE/'sistema/estado/servicios_locales'/LIFE,'persistent_service':NATIVE/'sistema/estado/servicios_persistentes'/LIFE}.items()}
        need(all(safe(p).is_dir()for p in roots.values()),'COMPLETE_CURRENT_ROOT_LOCALIZERS_PRESENT');bounded()
        result={'schema':'DEE.R07.MAIN46.bounded_current_localizer.R09','status':'CURRENT_ROOT_LOCALIZERS_AND_CRITICAL_CUT_VERIFIED_NO_NEW_FULL_INVENTORY',
          'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'elapsed_seconds':time.monotonic()-started,'life':LIFE,'native_tick':1019339,
          'session':c['session'],'physical':card['physical'],'roots':roots,'anchors':anchors,'critical':critical,
          'complete_current_native_system_remains_in_place':True,'all_current_files_newly_enumerated':False,'new_whole_root_manifest_created':False,
          'immutable_full_backup':False,'independent_rollback':False,'material_reopen_at46_tested':False,'Native_calls':0,'SQLite_connections':0,'MCP_calls':0,
          'global_live_ledger_read_or_written':False,'historical_cut_ledger_consumed':51612,'later_PILOT_closed_global_consumed':53176,
          'limits':['The complete root is preserved locally; uncopied current files, especially queue and environment, remain required.',
                    'No new full file inventory is claimed. Earlier PAR28/export manifests and official final close proof remain separate evidence.',
                    'Agenda, interfaces, outbox, receipts, progress and artifacts remain in the complete service/system roots; none were purged.',
                    'Shared official engine/Python and ancestral dependencies are required at their existing protected local locations, see CONTEXTO_EJECUCION and Scope.',
                    'Do not restore historical ledger51612 over the later53176 accounting. No reopening or new47 is authorized.']}
        write(DEST/'LOCALIZADORES_PAREJA_MAIN46_R09.json',result);write(DEST/'RESULTADO.json',{'status':result['status'],'elapsed_seconds':result['elapsed_seconds'],'Native_calls':0})
        (DEST/'IN_PROGRESS.json').unlink();return{'status':result['status'],'elapsed_seconds':result['elapsed_seconds'],'output':str(DEST)}
    except BaseException as e:
        if created:write(DEST/'INCOMPLETE_PRESERVED.json',{'error':repr(e),'automatic_retry':False,'Native_calls':0})
        raise
if __name__=='__main__':print(json.dumps(run(),ensure_ascii=False,indent=2))
