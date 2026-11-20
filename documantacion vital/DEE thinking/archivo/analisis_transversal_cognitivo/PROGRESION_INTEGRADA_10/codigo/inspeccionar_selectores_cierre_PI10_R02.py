from pathlib import Path
import json,hashlib
H=Path(__file__).resolve().parent;C=H.parents[3]/'DEE Cognitive 2.0'
names=('CONTINUIDAD_DEE_COGNITIVE_2_0.json','sistema/estado/genesis/SELECCION_PERSONAL.json','aplicacion/GENESIS/SELECCION_CANDIDATA.json','sistema/capacidades/CATALOGO_CAPACIDADES.json')
for name in names:
 p=C/name;v=json.loads(p.read_text('utf-8-sig'));print('FILE',name,'SHA',hashlib.sha256(p.read_bytes()).hexdigest());print('KEYS',list(v))
 for k in ('selected_seed','manual','manual_current','physical_cut','latest_snapshot','identity_card','current_principal','latest_operational_use','current_cut_scope','selected_life','latest_saved_tick','selected_operational_use_pending','selected_material_function_test_pending','selected_material_function_test_executed','current_saved_tick','current_saved_snapshot_sha256','current_identity_card_sha256','manual_internal_edition','manual_current_sha256','manual_current_bytes','life_id','world_id','snapshot','snapshot_sha256','tick','source_life_id','source_tick','source_snapshot_sha256'):
  if k in v:print(k,json.dumps(v[k],ensure_ascii=False))
 if name.endswith('CATALOGO_CAPACIDADES.json'):
  for k,z in v.items():
   if isinstance(z,list):
    for i,e in enumerate(z):
     if isinstance(e,dict)and'PI10'in str(e.get('id','')):print('ENTRY',k,i,json.dumps(e,ensure_ascii=False))

