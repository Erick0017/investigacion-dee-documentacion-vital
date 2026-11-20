"""Root-only resume of the preserved verified archive, no rearchive/extract.

R01 PID-only refusal remains evidence. Current PID14068 is acceptable only
when absent OR actually named TiWorker, corroborating that it is not the
historical officially launched python.exe whose close exited0. No process is
stopped; no creation time or global absence is invented.
"""
from pathlib import Path,PurePosixPath
import argparse,datetime,hashlib,json,runpy,subprocess,zipfile
P=Path(__file__).resolve().parents[1];H=P/'codigo';R01=H/'archivar_CAL_MSG_NONE_PI07_R01.py'
R01_SHA='5b29963b8714a56493671429f5f8881fd4c7571116e7ddb4c67f004362e02529';LIFE='ECI02_PI03_REPRO_PI04_PI05_PI07_VIAB_MSG_NONE';PID=14068
PROOF=P/'control/ARCHIVO_CAL_MSG_NONE_PI07_REANUDADO_R02.json'
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb')as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def need(v,s):
 if not v:raise ValueError(s)
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def probe():
 code="try { $p=[System.Diagnostics.Process]::GetProcessById(14068); @{id=14068;present=$true;name=$p.ProcessName} | ConvertTo-Json -Compress } catch [System.ArgumentException] { @{id=14068;present=$false;name=$null} | ConvertTo-Json -Compress } catch { throw }"
 q=subprocess.run(['powershell.exe','-NoProfile','-NonInteractive','-Command',code],capture_output=True,text=True,encoding='utf8',timeout=30,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
 need(q.returncode==0,'Ambiguous exact PID identity query; preserve all');v=json.loads(q.stdout.strip())
 need(v.get('id')==PID and(type(v.get('present'))is bool),'Incomplete PID identity')
 need(v['present']is False or v.get('name')=='TiWorker','Current PID is Python/another/unknown image; preserve all without stopping it')
 return{'queried_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'result':v,'classification':'ABSENT'if not v['present']else'PID_REUSED_OTHER_IMAGE_TiWorker','creation_time':'UNAVAILABLE_NOT_CLAIMED','only_scoped_PID_queried':True}
def main(a):
 need(sha(R01)==R01_SHA,'Preserved R01 source changed');g=runpy.run_path(str(R01),run_name='static_R01_archive_functions_only');h=g['support']();listing=h['listing'];safe=h['safe_root'];remove=h['remove_exact']
 need(not PROOF.exists(),'Prior completed R02 preserved; no repeated retirement')
 ZIP=g['ZIP'];VERIFY=g['VERIFY'];SIDE=g['SIDE'];WORK=g['WORK'];CAL=g['CAL'];CARD=g['CARD'];SNAP=(g['S']/read(CARD)['snapshot']).resolve(strict=True)
 need(ZIP.is_file()and VERIFY.is_dir()and SIDE.is_dir()and WORK.is_dir(),'Only existing retained R01ZIP/extraction/originals; no new extraction')
 need(sha(g['OWNER'])==g['OWNER_SHA']and sha(CARD)==g['CARD_SHA'],'Frozen calibration provenance differs')
 closure=read(P/'control/CIERRE_CAL_MSG_NONE_PI07_PARA_ARCHIVO_R01.json');closed=closure['owner_closed_record'];run=closed['run']
 need(closed['life']==LIFE and closed['pid']==PID and closed.get('exit_code')==0,'Original exact Python close missing')
 started=[]
 for line in(P/'ENSAYOS.jsonl').read_text('utf8').splitlines():
  row=json.loads(line)
  if row.get('kind')=='OWNER_STARTED'and row.get('run')==run and row.get('life')==LIFE and row.get('pid')==PID:started.append(row)
 need(len(started)==1 and Path(started[0]['command'][0]).name.casefold()=='python.exe','Original exact official Python image proof missing')
 need(Path(started[0]['command'][0]).resolve()==(g['C']/'motor/python313/python.exe').resolve(),'Historical executable differs from official Python')
 for marker in(g['S']/'estado/locks'/(LIFE+'.lock'),CAL/'FUTURO_INTERRUMPIDO.json'):
  need(not marker.exists(),'Calibration lock/interrupted marker remains')
 dep=g['dependencies'](h);need(dep['clear'],'An active operational dependency needs these originals')
 zip_hash=sha(ZIP);before=g['budget'](h);need(before<=g['LIMIT'],'Current fixed5.5GBbudget exceeded; preserve all')
 with zipfile.ZipFile(ZIP)as z:
  need(z.testzip()is None,'Existing ZIP CRC failure');manifest=json.loads(z.read(g['MANIFEST']));members=manifest['members'];names=[i.filename for i in z.infolist()]
  need(len(names)==len(set(names)),'Duplicate ZIP members')
  for i in z.infolist():
   p=PurePosixPath(i.filename);need(not p.is_absolute()and'..'not in p.parts,'Unsafe archive member')
  need(set(r['name']for r in manifest['roots'])=={'CAL_SERVICIO_PERSISTENTE','CAL_TRABAJADOR_LOCAL','CAL_VIDA_HISTORIA'},'Extra root is not authorized')
  expected_roots={'CAL_SERVICIO_PERSISTENTE':SIDE,'CAL_TRABAJADOR_LOCAL':WORK,'CAL_VIDA_HISTORIA':CAL}
  for root in manifest['roots']:
   need(Path(root['source']).resolve()==expected_roots[root['name']].resolve(),'Root mapping changed')
   need(bool(root['retire'])==(root['name']!='CAL_VIDA_HISTORIA'),'VIDA/history retirement forbidden')
  for row in members:
   extracted=VERIFY.joinpath(*PurePosixPath(row['file']).parts);source=Path(row['source']);safe(extracted);safe(source)
   need(source.is_file()and extracted.is_file()and source.stat().st_size==extracted.stat().st_size==row['bytes']and sha(source)==sha(extracted)==row['sha256'],'Original/extracted SHA or size changed')
   digest=hashlib.sha256()
   with z.open(row['file'])as f:
    for b in iter(lambda:f.read(1048576),b''):digest.update(b)
   need(digest.hexdigest()==row['sha256'],'ZIP member SHA differs')
  need((VERIFY/g['MANIFEST']).read_bytes()==z.read(g['MANIFEST']),'Extracted manifest differs')
  for root in manifest['roots']:
   need(all((VERIFY/root['name']/d).is_dir()for d in root['directories']),'An empty directory was lost')
 expected_files={r['file']for r in members}|{g['MANIFEST']};actual_files,actual_dirs=listing(VERIFY)
 need({r['relative']for r in actual_files}==expected_files,'Extra/unindexed extracted content')
 inventories={}
 for root in manifest['roots']:
  files,dirs=listing(expected_roots[root['name']]);expected={r['relative']:(r['bytes'],r['sha256'])for r in members if r['root']==root['name']}
  need({r['relative']for r in files}==set(expected)and dirs==root['directories'],'Source members/directories changed')
  need(all((r['bytes'],sha(expected_roots[root['name']]/r['relative']))==expected[r['relative']]for r in files),'Fresh source listing differs')
  inventories[root['name']]={'files':files,'directories':dirs}
 parser_path=P.parent/'PROGRESION_INTEGRADA_05/codigo/contrastar_prefijos_C2C_PI05_pasivo.py';need(sha(parser_path)=='5d84e2a21d6650f1dd69d3c677eb32db0aa9da9f0ae0ed315bb2d0992852124b','Passive parser revision changed');parser=runpy.run_path(str(parser_path),run_name='resume_calibration_passive_parser_only');card=read(CARD)
 original=g['cal_validation'](SIDE,SNAP,card,parser);extracted=g['cal_validation'](VERIFY/'CAL_SERVICIO_PERSISTENTE',VERIFY/'CAL_SNAPSHOT'/SNAP.name,card,parser);need(original==extracted==manifest['calibration_Native_SQLite'],'Native/SQLite mismatch')
 retired=sum(sum(r['bytes']for r in inventories[name]['files'])for name in('CAL_SERVICIO_PERSISTENTE','CAL_TRABAJADOR_LOCAL'))
 if not a.aplicar:
  print(json.dumps({'mode':'READ_ONLY_RESUME_PLAN','ZIP_sha256':zip_hash,'all_source_ZIP_and_existing_extracted_members_match':True,'logical_before':before,'logical_original_bytes_to_retire':retired,'no_new_archive_or_extract':True,'current_PID_identity_will_be_checked_only_on_apply':True,'Native_ticks':0}));return
 pbefore=probe();protected={str(f):sha(f)for f in[*sorted(CAL.rglob('*')),*sorted((g['S']/'estado/checkpoints').glob(LIFE+'.*'))]if f.is_file()}
 need(g['dependencies'](h)==dep and sha(ZIP)==zip_hash,'Current dependency or ZIP changed');pafter=probe()
 need(all(sha(Path(p))==v for p,v in protected.items()),'Protected life/history/checkpoint changed')
 removed=[]
 for name,root in(('CAL_SERVICIO_PERSISTENTE',SIDE),('CAL_TRABAJADOR_LOCAL',WORK)):
  remove(root,root,inventories[name]);removed.append(str(root.resolve()))
 remove(VERIFY,VERIFY,{'files':actual_files,'directories':actual_dirs})
 need(all(sha(Path(p))==v for p,v in protected.items()),'Protected Native history changed')
 with zipfile.ZipFile(ZIP)as z:need(z.testzip()is None,'Post-retirement ZIP CRC failure')
 need(sha(ZIP)==zip_hash,'Retained ZIP changed')
 marker={'schema':'DEE.PI07.closed_calibration_transport.archived.R02','status':'ARCHIVADO','life_id':LIFE,'native_life_history_global_checkpoints_preserved':True,'latest_tick':card['physical']['tick'],'archive':str(ZIP),'archive_sha256':zip_hash,'restore_exact_members_before_any_owner':{'persistent_service':'CAL_SERVICIO_PERSISTENTE/','worker':'CAL_TRABAJADOR_LOCAL/'},'original_R01_refusal_preserved':True,'new_Native_ticks':0};g['MARKER'].write_bytes(g['enc'](marker))
 result={'schema':'DEE.PI07.calibration_archive.resume.R02','status':'ARCHIVED_VERIFIED_EXACT_SIDE_WORK_REMOVED','at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'archive':{'path':str(ZIP),'bytes':ZIP.stat().st_size,'sha256':zip_hash},'R01_source':{'path':str(R01),'sha256':R01_SHA},'R01_PID_only_refusal_preserved':True,'PID_identity_rule_revision':'Current scoped PID absent OR exact processNameTiWorker; original officialpython.exe OWNER_STARTED and CLOSEDexit0 corroborated. No process stopped, no unavailable creationtime invented.','original_python_owner_started':started[0],'original_python_owner_closed':closed,'process_before':pbefore,'process_after':pafter,'removed_exact_directories':removed,'logical_original_bytes_retired':retired,'free_disk_space_recovered_not_measured':True,'all_members_ZIP_original_extraction_SHA_verified_again':True,'archive_members':len(members),'SQLite_Native':original,'dependencies':dep,'logical_before_resume':before,'logical_after':g['budget'](h),'fixed_budget':g['LIMIT'],'no_new_archive_or_extraction':True,'verification_temporary_removed':not VERIFY.exists(),'original_protected_files_before_after':protected,'new_Native_ticks':0,'selected_principal_unchanged':True}
 PROOF.write_bytes(g['enc'](result));print(json.dumps({'proof':str(PROOF),'sha256':sha(PROOF),'archive':result['archive'],'retired_logical_bytes':retired,'Native_ticks':0}))
if __name__=='__main__':
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--aplicar',action='store_true');main(ap.parse_args())
