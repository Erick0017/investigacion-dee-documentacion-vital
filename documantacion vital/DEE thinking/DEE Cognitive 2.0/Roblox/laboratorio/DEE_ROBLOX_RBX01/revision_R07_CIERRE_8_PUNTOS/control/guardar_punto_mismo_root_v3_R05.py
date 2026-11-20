"""Closed current-pair descriptor + content overlay, no Native/runtime.

Reopening means the SAME operative root. An optional complete file-level overlay
reuses byte-verified immutable BASE objects and copies only unique new bytes.
If new bytes exceed the finite copy cap, status is explicitly descriptor-only;
it is never called an immutable rollback backup. No automatic restoration exists.
"""
from pathlib import Path
import argparse,hashlib,importlib.util,json,shutil,time
ROOT=Path(__file__).resolve().parents[1]
def need(v,m):
    if not v:raise ValueError(m)
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb')as f:
        for b in iter(lambda:f.read(1048576),b''):h.update(b)
    return h.hexdigest()
def load(path,name):
    s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def new(p,v):
    with p.open('x',encoding='utf8')as f:json.dump(v,f,ensure_ascii=False,indent=2);f.write('\n')
def base_index():
    result={};records=[]
    pairs=[(ROOT.parent/'revision_R06_INTEGRAL_V2/evidencia/PAR28','PAREJA_INTEGRAL_V2.json','c4638b02ea660f2e32d13c015637e817a28d471e96c3bee0284918f1d55cf2c2'),
      (ROOT/'persistencia/PREFIJO_PAR28_COMPLETO','EXPORTACION_SERVICIO.json','fb3fdada9423eb890c8b0a466be74f60568c2464c8cfc004bf32c3b8950f3e7e')]
    for folder,name,want in pairs:
        p=folder/name;need(sha(p)==want,'EXACT_ALREADY_PRESERVED_BASE_MANIFEST');m=read(p)
        records.append({'path':str(p),'bytes':p.stat().st_size,'sha256':want,'Native_or_database_opened':False})
        for row in m['members']:
            name=row['file'];need(not Path(name).is_absolute()and'..'not in Path(name).parts,'SAFE_BASE_MEMBER')
            result.setdefault((row['sha256'],row['bytes']),folder/name)
    return result,records
def run(a):
    sealer=load(ROOT/'control/sellar_pareja_cerrada_v3.py','_r07_closed_point_validator')
    boundary=sealer.check_closed(a.native_root,a.world,a.closure,a.ledger)
    if not a.write_root_only:return {'status':'CLOSED_PREFLIGHT_NO_COPY','boundary':boundary,'Native_calls':0}
    destination=a.destination.absolute();need(destination.is_relative_to(ROOT/'evidencia')and not destination.exists(),'FRESH_SEPARATE_POINT_DIRECTORY')
    paths=load(ROOT.parent/'revision_R05_C02/control/path_guard_C02_R03.py','_r07_point_paths')
    guard=paths.PathGuard(ROOT.parent);native=guard.safe(a.native_root)
    before=paths.scan_files(native,guard,sha,30000,1500000000)
    bases,base_manifests=base_index();verified={};selection=[];unique={}
    for row in before['files']:
        key=(row['sha256'],row['bytes']);base=bases.get(key)
        if base is not None:
            if key not in verified:
                p=guard.safe(base);verified[key]=p.is_file()and p.stat().st_size==key[1]and sha(p)==key[0]
            if not verified[key]:base=None
        if base is None:unique.setdefault(key,native/row['file'])
        selection.append((row,base))
    unique_bytes=sum(k[1]for k in unique);complete=unique_bytes<=a.max_new_bytes
    destination.mkdir(parents=True);objects=destination/'objects';objects.mkdir();rows=[];copied={}
    critical={str((native/'sistema/estado/vidas'/boundary['life_id']/'VIDA.json').relative_to(native)),
      str(Path(boundary['queue']['path']).relative_to(native))}
    card=read(native/'sistema/estado/vidas'/boundary['life_id']/'VIDA.json');critical.add(str(Path('sistema')/card['snapshot']))
    for row,base in selection:
        source=native/row['file'];key=(row['sha256'],row['bytes']);kind='IMMUTABLE_BASE_VERIFIED'if base is not None else'CURRENT_ROOT_NOT_FROZEN'
        locator=base if base is not None else source
        if base is None and(complete or str(Path(row['file']))in critical):
            if key not in copied:
                target=objects/(row['sha256']+'.blob');shutil.copyfile(source,target)
                need(target.stat().st_size==row['bytes']and sha(target)==row['sha256'],'CLOSED_OBJECT_COPY_SHA')
                copied[key]=target
            locator=copied[key];kind='UNIQUE_PRESERVED_OBJECT'
        rows.append({**row,'locator':str(locator),'storage_kind':kind})
    for path,name in((a.world,'WORLD_CHECKPOINT.json'),(a.closure,'CIERRE_BLOQUE_ORIGINAL.json'),(a.ledger,'LEDGER_AL_CORTE.json')):
        p=destination/name;shutil.copyfile(path,p);rows.append({'file':name,'bytes':p.stat().st_size,'sha256':sha(p),'locator':str(p),'storage_kind':'UNIQUE_PRESERVED_ANCHOR'})
    again=sealer.check_closed(a.native_root,a.world,a.closure,a.ledger);need(again==boundary,'CLOSED_CRITICAL_BOUNDARY_CHANGED')
    guard.recheck()
    record={'schema':'DEE.RBX07.ClosedPointOverlay.R05','boundary':boundary,'native_source_root':str(native),'native_source_bytes':before['bytes'],
      'native_directories':before['directories'],'members':rows,'shared_immutable_base_manifests':base_manifests,'shared_read_only_runtime':sealer.resources(),
      'storage_mode':'COMPLETE_FILE_LEVEL_CONTENT_OVERLAY'if complete else'COMPLETE_CURRENT_ROOT_DESCRIPTOR_WITH_CRITICAL_MUTABLE_COPIES_ONLY',
      'immutable_all_members':complete,'copied_unique_bytes':sum(k[1]for k in copied),'unique_new_bytes_required':unique_bytes,'copy_cap_bytes':a.max_new_bytes,
      'restore_rule':'P04 test reopens the SAME current root. Complete overlay can reconstruct bytes only while all BASE locators remain preserved and SHA-valid; material rollback/relocated import is NOT tested. Never restore an old ledger over later accounting.',
      'RW_root_after_continuation_is_not_frozen_34_backup':True,'Native_calls':0,'new_ticks':0,'closed_SQLite_RO_only':True,
      'coverage':'All Native-root files indexed by actual SHA in one closed scan. Every reused BASE object SHA verified. Unique copied objects SHA verified. Full operative root remains local; no engine duplicate.'}
    manifest=destination/'PAREJA_INTEGRAL_V3.json';new(manifest,record)
    return {'status':record['storage_mode'],'path':str(destination),'manifest_sha256':sha(manifest),'members':len(rows),'native_tick':boundary['native_tick'],
      'complete_file_level_preservation':complete,'copied_unique_bytes':record['copied_unique_bytes'],'Native_calls':0}
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--write-root-only',action='store_true');p.add_argument('--native-root',type=Path,required=True);p.add_argument('--world',type=Path,required=True);p.add_argument('--closure',type=Path,required=True);p.add_argument('--ledger',type=Path,required=True);p.add_argument('--destination',type=Path);p.add_argument('--max-new-bytes',type=int,default=150000000);a=p.parse_args()
    need(0<a.max_new_bytes<=150000000 and(not a.write_root_only or a.destination is not None),'FINITE_NEW_COPY_BUDGET')
    print(json.dumps(run(a),ensure_ascii=False,indent=2))
