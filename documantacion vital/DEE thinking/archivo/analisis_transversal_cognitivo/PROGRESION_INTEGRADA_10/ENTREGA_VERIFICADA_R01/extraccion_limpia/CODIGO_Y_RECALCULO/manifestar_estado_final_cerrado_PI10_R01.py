"""Hash the exact Root-confirmed final closed state, without SQL or Native.

No copy, owner, engine import, database connection, selector or source write.
The existing Root closure proof supplies actual SQL/process checks. This tool
checks its bytes and frozen checkpoint identity, then hashes every regular
file under the three exact paired-state stores twice. No other lives or disk
census is performed. The result is a locator/manifest, not a new backup.
"""
from pathlib import Path
from datetime import datetime, timezone
import argparse, hashlib, importlib.util, json, os

LIFE='ECI02_PI03_REPRO_PI04_PI05_PI07_PI10_REAL2_01'
TICK=947395
SNAP='fd7372b7f2adc9040866fab8adfaca0d79e0bd18e997c0abc0651fe4fa3c23dc'
PROOF='0a6241949697546e497ffab62573edd9b3240c55d5cc40ec5c1b977e4767662c'

def need(ok, why):
    if not ok: raise ValueError(why)

def regular(path):
    path=Path(path).absolute()
    for p in (path,*path.parents):
        need(not p.is_symlink() and not (getattr(p.lstat(),'st_file_attributes',0)&1024), 'No symbolic/reparse state path')
    return path

def digest(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for b in iter(lambda:f.read(1048576),b''): h.update(b)
    return h.hexdigest()

def read(path): return json.loads(Path(path).read_text('utf-8-sig'))

def files_under(root):
    regular(root); need(root.is_dir(), 'Missing exact paired-state directory')
    found=[]; directories=[]
    for base,names,files in os.walk(root,followlinks=False):
        base=regular(base)
        directories.append(str(base))
        for name in names: regular(base/name)
        for name in files:
            p=regular(base/name); need(p.is_file(),'Nonregular state object')
            found.append(p)
    return found,directories

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--sistema',type=Path,required=True)
    ap.add_argument('--comprobante',type=Path,required=True)
    ap.add_argument('--salida',type=Path,required=True)
    a=ap.parse_args();s=regular(a.sistema.resolve(strict=True));p=regular(a.comprobante.resolve(strict=True))
    need(not a.salida.exists(),'No overwrite of an earlier preservation proof')
    need(digest(p)==PROOF,'Exact actual Root closed public-use/reopening proof')
    proof=read(p);closed=proof['closed_process_queue']
    need(proof['closed'] is True and proof['error'] is None and proof['life_id']==LIFE and proof['final_tick']==TICK,'Root final closure and identity required')
    need(closed['no_live_affected_writer'] is True and closed['SQLite']['integrity_check']=='ok' and closed['SQLite']['unresolved']==[] and closed['SQLite']['WAL_bytes']==closed['SQLite']['SHM_bytes']==0,'Root actual process/SQL/queue checks required; this tool never opens SQL')
    af=s/'estado/ACTIVO.json';cf=s/'estado/vidas'/LIFE/'VIDA.json'
    active=read(af);card=read(cf);snapshot=regular((s/card['snapshot']).resolve(strict=True))
    need(snapshot.is_relative_to(s) and active['life_id']==card['life_id']==card['world_id']==LIFE and active['tick']==card['physical']['tick']==TICK and card['snapshot_sha256']==active['snapshot_sha256']==digest(snapshot)==SNAP,'Current active/card/snapshot identity differs from the closed cut')
    h=Path(__file__).resolve().parent;sp=importlib.util.spec_from_file_location('PI10_pure_archived_snapshot_reader',h/'recalcular_snapshots_incluidos_PI10_R01.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
    view,_=m.parse(snapshot.read_bytes(),LIFE)
    need(all(view['physical'][k]==card['physical'][k] for k in ('N','tick','RAW_sha256','clocks_sha256')) and view['pending_Native']==0,'Frozen Native/card correspondence and agenda required')
    progress=view['PI10_progress_subset'];need(progress['ordinal']==14 and not progress['pending'] and not progress['uncertain'],'Actual14-opportunity clean progress required')
    stores=[s/'estado/vidas'/LIFE,s/'estado/servicios_persistentes'/LIFE,s/'estado/servicios_locales'/LIFE]
    files=[snapshot,regular(af)];directories=[]
    for root in stores:
        ff,dd=files_under(root);files+=ff;directories+=dd
    files=sorted(set(files))
    def scan():
        return [{'absolute_path':str(f),'relative_to_system':f.relative_to(s).as_posix(),'bytes':f.stat().st_size,'sha256':digest(f)} for f in files]
    first=scan();second=scan();need(first==second and digest(p)==PROOF,'Concurrent source modification; no final manifest certified')
    need(sorted(files_under(stores[0])[0]+files_under(stores[1])[0]+files_under(stores[2])[0]+[snapshot,af])==files,'Concurrent membership change')
    result={'schema':'DEE.PI10.final_closed_state_locator_manifest.R01','created_utc':datetime.now(timezone.utc).isoformat(),'Native_executed':False,'DEE_imported':False,'SQLite_opened':False,'sources_written':False,'life_id':LIFE,'profile':card['profile'],'physical':card['physical'],'snapshot':{'absolute_path':str(snapshot),'bytes':snapshot.stat().st_size,'sha256':SNAP},'Root_closed_proof':{'absolute_path':str(p),'sha256':PROOF},'current_selection_path':str(af),'paired_state_stores':[str(x) for x in stores],'directories_preserved_in_place':sorted(directories),'files':first,'file_count':len(first),'total_local_bytes':sum(x['bytes'] for x in first),'two_pass_file_and_membership_identity':True,'Native_interfaces':view['interfaces'],'Native_pending':view['pending_Native'],'Native_receipts':view['Native_receipts'],'PI10_progress':progress,'original_offers_used':14,'original_offers_total':18,'original_offers_remaining':4,'shared_code_and_dependencies':'Existing Cognitive and frozen Universe/Thinking/runtime plus stable reproducibility store remain separate shared dependencies; not copied here. Exact code/contract/selector proofs accompany the final continuity map.','scope':'Full current snapshot plus exact three paired-state stores, present and hashed in place after Root closure. Root actual SQL/process checks are cited, not independently repeated. This JSON and the small analysis ZIP are not an executable full-state backup. No claim that unrelated project files are immutable.'}
    with a.salida.open('x',encoding='utf8') as f: json.dump(result,f,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps({'file':str(a.salida),'sha256':digest(a.salida),'files':len(first),'local_bytes':result['total_local_bytes'],'Native':0,'SQL_opened':False}))

if __name__=='__main__': main()
