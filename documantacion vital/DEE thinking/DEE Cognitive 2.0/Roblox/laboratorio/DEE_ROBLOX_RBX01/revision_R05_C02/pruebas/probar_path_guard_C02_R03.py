"""Synthetic path guard/performance checks; no Native, live DB or processes."""
from pathlib import Path
import datetime,hashlib,importlib.util,json,stat,time,types
ROOT=Path(__file__).resolve().parents[1];source=ROOT/'control/path_guard_C02_R03.py'
s=importlib.util.spec_from_file_location('_path_guard_fixture',source);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ');work=ROOT/'pruebas'/('PATH_GUARD_R03_FIXTURE_'+stamp);work.mkdir()
tree=work/'source';tree.mkdir();expected=[];expected_dirs=set();started=time.monotonic()
for i in range(256):
    file=tree/('g'+str(i%16))/'deep'/'deeper'/('file_%04d.bin'%i);file.parent.mkdir(parents=True,exist_ok=True)
    raw=('synthetic-content-'+str(i)).encode();file.write_bytes(raw)
    expected.append({'file':file.relative_to(tree).as_posix(),'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()})
    expected_dirs.update(p.relative_to(tree).as_posix()for p in file.parents if p!=tree and p.is_relative_to(tree))
expected.sort(key=lambda r:Path(r['file']))
guard=m.PathGuard(work);calls=[]
def hashfile(p):calls.append(str(p));return hashlib.sha256(p.read_bytes()).hexdigest()
result=m.scan_files(tree,guard,hashfile,30000,2**32);checks=[]
assert result['files']==expected and set(result['directories'])==expected_dirs;checks.append('Full hashes/file-set/directories match independent256-file fixture')
assert len(calls)==256 and len(set(calls))==256;checks.append('Every file content hashed exactly once per scan')
assert guard.stats()['leaf_lstats']<=256+len(expected_dirs)+2;checks.append('Leaf metadata calls scale with files+directories, not repeated ancestors')
assert guard.stats()['fresh_commit_directory_rechecks']>=len(expected_dirs);checks.append('Fresh directory identity checks executed after scan')
try:guard.safe(work.parent/'outside_fixture')
except ValueError:checks.append('Outside scoped root refused')
else:raise AssertionError('Outside root accepted')
fake=types.SimpleNamespace(st_mode=stat.S_IFLNK,st_file_attributes=1024)
try:guard.safe(tree/'not_a_real_link',leaf_info=fake)
except ValueError:checks.append('Reparse/symlink leaf flag refused')
else:raise AssertionError('Reparse accepted')
old=work/'replaceable';old.mkdir();check=m.PathGuard(work);check.safe(old)
saved=work/'preserved_original_directory';assert old.resolve().is_relative_to(work.resolve())and saved.absolute().is_relative_to(work.resolve())
old.rename(saved);old.mkdir()
try:check.recheck()
except ValueError:checks.append('Fresh recheck detects replaced ancestor identity')
else:raise AssertionError('Directory replacement was missed')
report={'scope':'SYNTHETIC_PATH_GUARD_ONLY','tests':len(checks),'checks':checks,'files':256,'directories':len(expected_dirs),
        'elapsed_seconds_including_fixture_creation':time.monotonic()-started,'path_stats':guard.stats(),'fixture':str(work),
        'Native_imports':0,'Native_ticks':0,'MCP_calls':0,'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest()}
out=ROOT/'pruebas'/('PATH_GUARD_R03_SINTETICO_'+stamp+'.json');out.write_text(json.dumps(report,indent=2)+'\n',encoding='utf8')
print(json.dumps({'report':str(out),**report}))
