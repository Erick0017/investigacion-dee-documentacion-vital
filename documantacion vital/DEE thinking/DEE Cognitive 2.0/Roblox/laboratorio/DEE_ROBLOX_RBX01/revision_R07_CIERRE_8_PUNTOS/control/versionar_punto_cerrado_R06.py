"""Prepare R06 closed-point safety corrections; never copies a Native state."""
from pathlib import Path
import hashlib,json
HERE=Path(__file__).resolve().parent
OLD=HERE/'guardar_punto_mismo_root_v3_R05.py';NEW=HERE/'guardar_punto_mismo_root_v3_R06.py'
def exact(s,a,b):
    if s.count(a)!=1:raise ValueError('Exact source anchor changed:'+repr(a[:90]))
    return s.replace(a,b,1)
def main():
    before=hashlib.sha256(OLD.read_bytes()).hexdigest();s=OLD.read_text('utf-8')
    s=exact(s,"def run(a):\n    sealer=load(ROOT/'control/sellar_pareja_cerrada_v3.py','_r07_closed_point_validator')\n    boundary=sealer.check_closed(a.native_root,a.world,a.closure,a.ledger)",
      "def _run_guarded(a):\n    paths=load(ROOT.parent/'revision_R05_C02/control/path_guard_C02_R03.py','_r07_point_paths')\n    guard=paths.PathGuard(ROOT.parent)\n    native=guard.safe(a.native_root)\n    a.native_root=native\n    a.world=guard.safe(a.world);a.closure=guard.safe(a.closure);a.ledger=guard.safe(a.ledger)\n    sealer=load(ROOT/'control/sellar_pareja_cerrada_v3.py','_r07_closed_point_validator')\n    boundary=sealer.check_closed(native,a.world,a.closure,a.ledger)")
    s=exact(s,"    destination=a.destination.absolute();need(destination.is_relative_to(ROOT/'evidencia')and not destination.exists(),'FRESH_SEPARATE_POINT_DIRECTORY')\n    paths=load(ROOT.parent/'revision_R05_C02/control/path_guard_C02_R03.py','_r07_point_paths')\n    guard=paths.PathGuard(ROOT.parent);native=guard.safe(a.native_root)",
      "    evidence=guard.safe(ROOT/'evidencia')\n    destination=guard.safe(a.destination,exists=False)\n    need(destination==destination.resolve(strict=False)and destination.is_relative_to(evidence)and destination!=evidence and not destination.exists(),'FRESH_GUARDED_EVIDENCE_DIRECTORY')\n    need(not destination.is_relative_to(native)and not native.is_relative_to(destination),'OUTPUT_OUTSIDE_NATIVE_ROOT')\n    guard.recheck()")
    s=exact(s,"    bases,base_manifests=base_index();verified={};selection=[];unique={}",
      "    bases,base_manifests=base_index();verified={};selection=[];unique={};shared=sealer.resources()")
    s=exact(s,"    destination.mkdir(parents=True);objects=destination/'objects';objects.mkdir();rows=[];copied={}",
      "    destination.mkdir(parents=True);destination=guard.safe(destination)\n    objects=destination/'objects';objects.mkdir();objects=guard.safe(objects);rows=[];copied={}")
    s=exact(s,"                target=objects/(row['sha256']+'.blob');shutil.copyfile(source,target)",
      "                target=guard.safe(objects/(row['sha256']+'.blob'),exists=False);need(not target.exists(),'FRESH_CONTENT_OBJECT');shutil.copyfile(source,target)")
    s=exact(s,"        p=destination/name;shutil.copyfile(path,p);rows.append({'file':name,'bytes':p.stat().st_size,'sha256':sha(p),'locator':str(p),'storage_kind':'UNIQUE_PRESERVED_ANCHOR'})\n    again=sealer.check_closed(a.native_root,a.world,a.closure,a.ledger);need(again==boundary,'CLOSED_CRITICAL_BOUNDARY_CHANGED')\n    guard.recheck()",
      "        expected={'WORLD_CHECKPOINT.json':boundary['world_sha256'],'CIERRE_BLOQUE_ORIGINAL.json':boundary['closure_sha256'],'LEDGER_AL_CORTE.json':boundary['global_ledger_sha256']}[name]\n        p=guard.safe(destination/name,exists=False);need(not p.exists(),'FRESH_ANCHOR');shutil.copyfile(path,p)\n        need(sha(p)==expected,'ANCHOR_COPY_DIFFERS_DECLARED_BOUNDARY')\n        rows.append({'file':name,'bytes':p.stat().st_size,'sha256':expected,'locator':str(p),'storage_kind':'UNIQUE_PRESERVED_ANCHOR'})\n    need(len({row['file']for row in rows})==len(rows),'NATIVE_ANCHOR_MEMBER_NAME_COLLISION')\n    for row in rows:\n        locator=guard.safe(Path(row['locator']))\n        need(locator.is_file()and locator.stat().st_size==row['bytes']and sha(locator)==row['sha256'],'PRESERVED_LOCATOR_CHANGED')\n    for base_record in base_manifests:\n        need(sha(guard.safe(Path(base_record['path'])))==base_record['sha256'],'BASE_MANIFEST_CHANGED')\n    need(sealer.resources()==shared,'SHARED_RUNTIME_CHANGED')\n    after=paths.scan_files(native,guard,sha,30000,1500000000)\n    need(after['files']==before['files']and after['directories']==before['directories']and after['bytes']==before['bytes'],'FULL_NATIVE_SOURCE_CHANGED_DURING_POINT')\n    again=sealer.check_closed(a.native_root,a.world,a.closure,a.ledger);need(again==boundary,'CLOSED_CRITICAL_BOUNDARY_CHANGED')\n    guard.recheck()")
    s=exact(s,"'shared_read_only_runtime':sealer.resources(),","'shared_read_only_runtime':shared,'implementation_revision':'R06','full_source_hashes_and_directories_before_after_equal':True,'anchors_match_declared_boundary':True,")
    insert="""
def run(a):
    try:
        return _run_guarded(a)
    except BaseException as error:
        # Only annotate an already-created, safely scoped partial destination.
        # Never remove, replace, restore or rename either the source or output.
        if a.write_root_only and a.destination is not None:
            try:
                import os
                paths=load(ROOT.parent/'revision_R05_C02/control/path_guard_C02_R03.py','_r07_failed_point_paths')
                guard=paths.PathGuard(ROOT.parent)
                destination=guard.safe(a.destination)
                evidence=guard.safe(ROOT/'evidencia')
                if destination.is_relative_to(evidence)and destination!=evidence and destination.is_dir():
                    marker=destination/'INCOMPLETE_PRESERVED.json'
                    if not marker.exists():new(marker,{'schema':'DEE.RBX07.partial_closed_point.R06','error':type(error).__name__+': '+str(error),'originals_not_restored_or_deleted':True,'no_automatic_retry':True,'not_a_complete_backup':True})
            except BaseException:
                pass # Preserve the original failure and every existing byte.
        raise

"""
    s=exact(s,"if __name__=='__main__':",insert+"if __name__=='__main__':")
    s=s.replace('destination.mkdir(parents=True);destination=guard.safe(destination)',
                'destination.mkdir(parents=True);a._created_destination=True;destination=guard.safe(destination)')
    s=s.replace('def run(a):\n    try:', 'def run(a):\n    a._created_destination=False\n    try:')
    s=s.replace('if a.write_root_only and a.destination is not None:',
                'if a.write_root_only and a.destination is not None and a._created_destination:')
    if NEW.exists():raise ValueError('Preserve prior closed-point version')
    compile(s,str(NEW),'exec');NEW.write_text(s,encoding='utf-8',newline='\n')
    if hashlib.sha256(OLD.read_bytes()).hexdigest()!=before:raise ValueError('R05 original changed')
    print(json.dumps({'file':str(NEW),'sha256':hashlib.sha256(NEW.read_bytes()).hexdigest(),
      'R05_preserved_sha256':before,'schema_unchanged':'DEE.RBX07.ClosedPointOverlay.R05',
      'state_copies_performed':0,'Native_calls':0,'MCP_calls':0}))
if __name__=='__main__':main()
