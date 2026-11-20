"""Root-only single administrative leaf after complete SAME-ID relocation.

Adapted from reviewed app/pi09_identidad_c2c_D_R01.py. No Native on import.
No life import, clock/RAW edit, history rewrite or acquisition is performed.
"""
from pathlib import Path
import hashlib,json,gc
LIFE='ECI02_PI03_REPRO_PI04_PI05_PI07_PI10_REAL2_01'
KEY='DEE.Cognitive.PI04.C2C.coordination.R01';SYSTEM='DEE.Cognitive.System.1.1.life.v1'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def propose_identity(metadata,target_life):
 if target_life!=LIFE:raise ValueError('Exact PI10 REAL current identity required')
 from capacidades import pi10_permiso_operativo_R02 as permission
 return permission.propose_C2C_identity(metadata)
def rebind_moved_C2C_identity(store,target_life,relocation_map_path,relocation_map_sha256):
 if target_life!=LIFE:raise ValueError('Only exact prospective PI10 REAL main')
 file=Path(relocation_map_path).resolve(strict=True)
 if sha(file)!=relocation_map_sha256:raise ValueError('Verified relocation map changed')
 mapping=json.loads(file.read_text('utf-8-sig'))
 if mapping.get('same_life_id')!=LIFE or mapping.get('same_world_id')!=LIFE or Path(mapping['target_system']).resolve()!=store.root.resolve()or mapping.get('not_a_new_life_or_import')is not True:raise ValueError('Actual same-ID relocation provenance required')
 active=store.state/'ACTIVO.json'
 if active.exists()and json.loads(active.read_text('utf-8-sig')).get('life_id')==LIFE:raise ValueError('Map only before selection')
 original_import=store.state/'servicios_persistentes'/LIFE/'IMPORTACION.json';import_before=sha(original_import)if original_import.is_file()else None
 from app.pi05_identidad_c2c import _view
 from dee_thinking.persistence import decode_metadata
 from capacidades import pi04_coordinacion_central_C2C as component
 with store.writer(LIFE):
  a=None
  try:
   record,a=store.load(LIFE);before_path=store.snapshot(record);before=_view(before_path);entries=dict(a.world.runtime.snapshot_metadata_entries)
   if json.loads(entries[SYSTEM])['life_id']!=LIFE or record['world_id']!=LIFE:raise ValueError('Exact complete current system/world identity required')
   old=decode_metadata(entries[KEY]);new,leaf=propose_identity(old,target_life)
   if old['life_id']==LIFE:return {'schema':'DEE.PI10.C2C.same_identity_relocation.mapping.R02','changed':False,'already_current':True,'source_life_id':LIFE,'target_life_id':LIFE,'metadata_old_life_id':LIFE,'metadata_new_life_id':LIFE,'new_ticks':0,'leaf':leaf,'historical_import_unchanged_sha256':import_before}
   component._save(a,new)
   operation={'kind':'EXPLICIT_ADMINISTRATIVE_C2C_CURRENT_IDENTITY_AFTER_SAME_ID_MOVE_PI10','new_native_ticks':0,'leaf':leaf,'relocation_map_sha256':relocation_map_sha256,'source_and_target_world_identity_unchanged':True,'original_import_history_preserved':True}
   after_record=store.commit(record,a,operation,activate=False);after_path=store.snapshot(after_record);after=_view(after_path)
  finally:a=None;gc.collect()
 if before['physical']!=after['physical']or before['causal_prefix_sha256']!=after['causal_prefix_sha256']:raise RuntimeError('Administrative mapping changed physical/agenda/interfaces/receipts')
 changed=[k for k in set(before['metadata'])|set(after['metadata'])if before['metadata'].get(k)!=after['metadata'].get(k)]
 if set(changed)-{SYSTEM,KEY}or json.loads(after['metadata'][KEY])!=new:raise RuntimeError('Unrelated metadata changed')
 if import_before is not None and sha(original_import)!=import_before:raise RuntimeError('Historical import provenance changed')
 return {'schema':'DEE.PI10.C2C.same_identity_relocation.mapping.R02','changed':True,'source_life_id':LIFE,'target_life_id':LIFE,'metadata_old_life_id':old['life_id'],'metadata_new_life_id':LIFE,'new_ticks':0,'leaf':leaf,'before_snapshot':str(before_path),'after_snapshot':str(after_path),'physical_before':before['physical'],'physical_after':after['physical'],'causal_prefix_before':before['causal_prefix_sha256'],'causal_prefix_after':after['causal_prefix_sha256'],'changed_metadata_keys':changed,'allowed_C2C_changed_leaves':['life_id'],'historical_import_unchanged_sha256':import_before,'not_a_new_acquisition_or_import':True}
