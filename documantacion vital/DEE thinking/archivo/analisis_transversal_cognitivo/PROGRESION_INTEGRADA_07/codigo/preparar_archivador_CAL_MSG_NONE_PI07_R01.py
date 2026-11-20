"""Derive a bounded Root-only inactive calibration archiver, no archive/move."""
from pathlib import Path
import ast,hashlib,json,re,sqlite3
P=Path(__file__).resolve().parents[1];H=P/'codigo';S=P/'estados/candidato/sistema';LIFE='ECI02_PI03_REPRO_PI04_PI05_PI07_VIAB_MSG_NONE'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 source=H/'archivar_R02_28_y_cal_MSG_PULSE_PI07_R01.py';text=source.read_text('utf8');owner=P/'control/PI07_VIAB_MSG_NONE_R01.json';card=S/'estado/vidas'/LIFE/'VIDA.json';db=S/'estado/servicios_persistentes'/LIFE/'cola.sqlite3'
 if db.with_name(db.name+'-wal').exists()and db.with_name(db.name+'-wal').stat().st_size:raise ValueError('Nonempty WAL prevents even qualifying closed source')
 before=sha(db);con=sqlite3.connect(db.resolve().as_uri()+'?mode=ro&immutable=1',uri=True)
 try:cached=json.loads(con.execute("SELECT value FROM meta WHERE key='owner'").fetchone()[0])
 finally:con.close()
 if sha(db)!=before or cached.get('running')is not False or cached.get('life_id')!=LIFE:raise ValueError('Closed exact calibration only')
 pid=cached['pid'];closed=[]
 for line in(P/'ENSAYOS.jsonl').read_text('utf8').splitlines():
  event=json.loads(line)
  if event.get('kind')=='OWNER_CLOSED'and event.get('life')==LIFE and event.get('pid')==pid:closed.append(event)
 if not closed or closed[-1].get('exit_code')!=0:raise ValueError('Exact historical owner close missing')
 closeproof=P/'control/CIERRE_CAL_MSG_NONE_PI07_PARA_ARCHIVO_R01.json'
 if closeproof.exists():raise FileExistsError('Preserve prior source witness')
 closeproof.write_text(json.dumps({'owner_closed_record':closed[-1],'cached_owner':{k:cached[k]for k in('life_id','pid','running','paused','last_saved_tick','uncertain_external_result')},'original_owner_proof':{'path':str(owner),'sha256':sha(owner)},'SQLite_unchanged_after_immutable_read_sha256':before,'Native_executed':False},ensure_ascii=False,indent=2)+'\n',encoding='utf8')
 replacements={
 'archive one inactive RP copy and one closed calibration\'s sidecars':'archive ONLY one closed calibration\'s sidecar and worker',
 'three exact authorized directories':'two exact authorized directories',
 "LIFE='ECI02_PI03_REPRO_PI04_PI05_PI07_VIAB_MSG_PULSE'":"LIFE='"+LIFE+"'",
 "PAIR_NAME='PI07_TRAYECTORIA_R02_28_T846517';PAIR=RP/'materiales'/PAIR_NAME\n":'',
 'PI07_R02_28_Y_CAL_MSG_PULSE_CERRADOS_R01.zip':'PI07_CAL_MSG_NONE_CERRADO_R01.zip',
 'PI07_ARC_R28_CAL01':'PI07_ARC_MSGNONE01',
 'ARCHIVO_R02_28_Y_CAL_MSG_PULSE_PI07_R01.json':'ARCHIVO_CAL_MSG_NONE_PI07_R01.json',
 'PI07_VIAB_MSG_PULSE_R01.json':'PI07_VIAB_MSG_NONE_R01.json',
 "OWNER_SHA='ced7674673135b572f433a724064c8573f1fba2de9e6f02fa90d0c7571152390'":"OWNER_SHA='"+sha(owner)+"'",
 "CARD_SHA='fdc5b37cdde20d9e4f8a9eac02baab5276ed9045074c2c20eb8e1a18e029915c'":"CARD_SHA='"+sha(card)+"'",
 "PAIR_MANIFEST_SHA='e5b56aeea7dc5058008fca6e9fe2facd7c92f1e8dfb8e2ac9888a7255ef6460a'\n":'',
 '(PAIR_NAME,LIFE)':'(LIFE,)',
 "    require(sha(PAIR/'EXPORTACION_SERVICIO.json')==PAIR_MANIFEST_SHA,'Frozen RP28 manifest changed')\n":'',
 "    roots=[{'name':'RP_R02_28','source':PAIR,'retire':True},\n           {'name':'CAL_SERVICIO_PERSISTENTE'":"    roots=[{'name':'CAL_SERVICIO_PERSISTENTE'",
 "    native_pair=h['native_and_sqlite'](PAIR);native_cal=cal_validation(SIDE,snap,card,parser)":"    native_cal=cal_validation(SIDE,snap,card,parser)",
 "          'RP28_Native_SQLite':native_pair,'calibration_Native_SQLite':native_cal":"          'calibration_Native_SQLite':native_cal",
 "    require(h['native_and_sqlite'](VERIFY/'RP_R02_28')==native_pair,'Extracted RP28 state differs')\n":'',
 "      'RP28_Native_SQLite':native_pair,'calibration_Native_SQLite':native_cal":"      'calibration_Native_SQLite':native_cal",
 'Only RP28 duplicate and exact VIAB_MSG_PULSE sidecar/worker retired':'Only exact VIAB_MSG_NONE sidecar/worker retired',
 'Unresolved current dependency; preserve RP28 and closed calibration':'Unresolved current dependency; preserve closed calibration',
 }
 for old,new in replacements.items():
  if old not in text:raise ValueError('Exact prior reviewed fragment missing: '+old)
  text=text.replace(old,new)
 # Remove paired-export-only validation, retaining complete calibration Native
 # snapshot/card, immutable SQLite and every file/empty-directory verification.
 first=text.index("        declared=json.loads((PAIR/'EXPORTACION_SERVICIO.json')")
 last=text.index("        manifest=",first);text=text[:first]+text[last:]
 text=re.sub(r'(?<![0-9A-Za-z])4232(?![0-9A-Za-z])',str(pid),text).replace('PID4232','PID'+str(pid))
 # Additional exact owner-close witness pinned before any archival action.
 needle="    require(sha(OWNER)==OWNER_SHA and sha(CARD)==CARD_SHA,'Frozen calibration evidence changed')"
 inserted=needle+"\n    closeproof=P/'control/CIERRE_CAL_MSG_NONE_PI07_PARA_ARCHIVO_R01.json'\n    require(sha(closeproof)=='"+sha(closeproof)+"','Exact owner-close witness changed')\n    closed_record=json.loads(closeproof.read_text(encoding='utf8'))['owner_closed_record']\n    require(closed_record.get('pid')=="+str(pid)+" and closed_record.get('exit_code')==0,'Closed historical owner differs')"
 text=text.replace(needle,inserted)
 text=text.replace('inactive_RP28_and_calibration','inactive_MSG_NONE_calibration')
 ast.parse(text)
 if 'PAIR/'in text or 'native_pair'in text or 'PAIR_NAME'in text:raise ValueError('Unqualified extra target left')
 out=H/'archivar_CAL_MSG_NONE_PI07_R01.py'
 if out.exists():raise FileExistsError('Preserve prior prepared helper')
 out.write_text(text,encoding='utf8');print(json.dumps({'helper':str(out),'sha256':sha(out),'exact_pid':pid,'closure':str(closeproof),'closure_sha256':sha(closeproof),'Native_executed':False,'archive_or_retire_executed':False}))
if __name__=='__main__':main()
