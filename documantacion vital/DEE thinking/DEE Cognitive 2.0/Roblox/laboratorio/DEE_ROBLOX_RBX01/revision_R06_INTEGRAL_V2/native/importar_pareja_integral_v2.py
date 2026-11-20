"""Root-only explicit material LOAD, zero ticks; no world is opened on import."""
from pathlib import Path
import argparse,hashlib,importlib.util,json,sys
sys.dont_write_bytecode=True

def main():
 p=argparse.ArgumentParser();p.add_argument('--contexto',required=True);a=p.parse_args();context_path=Path(a.contexto).resolve(strict=True)
 c=json.loads(context_path.read_text('utf8'));dest=context_path.parent;system=Path(c['system']).resolve(strict=True)
 if system!=dest/'sistema'or not c['life'].startswith('ECI02_PI03_REPRO_PI04_PI05_PI07_PI10_RBX01_INTEGRAL_V2_'):
  raise ValueError('Only explicit prepared integral descendant')
 if (system/'estado/ACTIVO.json').exists()or(dest/'IMPORTACION_DIAGNOSTICA.json').exists():raise ValueError('No selected/existing import destination')
 product=Path(c['product']).resolve(strict=True)
 for pin in c['tool_sources']:
  path=product/'reproducibilidad'/pin['file']
  if hashlib.sha256(path.read_bytes()).hexdigest()!=pin['sha256']:raise ValueError('Official importer/observer changed')
 prefix=Path(c['prefix']).resolve(strict=True)
 if hashlib.sha256((prefix/'EXPORTACION_SERVICIO.json').read_bytes()).hexdigest()!=c['prefix_manifest_sha256']:raise ValueError('Complete prefix manifest changed')
 sys.path[:0]=[str(system),str(system/'app'),str(product/'reproducibilidad')]
 from app.lives import Store
 from app.importacion_emparejada import import_pair
 from app.native_tools import atomic_json
 from observador_pasivo import snapshot_view,compare_native
 store=Store(system);result=import_pair(store,prefix,c['life'])
 record=store.record(c['life']);initial_snapshot_sha=record['snapshot_sha256']
 # Bind explicit genealogy using the existing official Store.commit API.
 # This changes administrative SYSTEM metadata only, not RAW/clocks/history.
 with store.writer(record['world_id']):
  record,adapter=store.load(c['life'])
  record['parent']={'life_id':c['source_life_id'],'snapshot_sha256':c['source_snapshot_sha256'],'tick':c['source_tick'],
    'historical_parent':json.loads(Path(c['source_record']).read_text('utf8')).get('parent'),
    'source_pair_manifest_sha256':c['prefix_manifest_sha256']}
  record=store.commit(record,adapter,{'kind':'BIND_EXPLICIT_COMPLETE_DEV4_LINEAGE','new_native_ticks':0,
      'parent_life_id':c['source_life_id'],'parent_tick':c['source_tick'],'no_cognitive_content_written':True},activate=False)
 comparison=compare_native(snapshot_view(prefix/'VIDA.deetsnap.gz'),snapshot_view(system/record['snapshot']))
 if record['physical']['tick']!=953651 or (system/'estado/ACTIVO.json').exists():raise ValueError('Import changed the physical cut/selection')
 result.update(snapshot_sha256=record['snapshot_sha256'],physical=record['physical'],explicit_parent=record['parent'])
 mapping=system/'estado/servicios_persistentes'/c['life']/'IMPORTACION.json'
 mapped=json.loads(mapping.read_text('utf8'));mapped.update(initial_imported_snapshot_sha256=initial_snapshot_sha,
  imported_snapshot_sha256=record['snapshot_sha256'],explicit_parent=record['parent'],lineage_binding_ticks=0)
 atomic_json(mapping,mapped)
 with(dest/'IMPORTACION_DIAGNOSTICA.json').open('x',encoding='utf8')as f:
  json.dump({'result':result,'comparison':comparison,'new_native_ticks':0,'source_parent':str(prefix),
    'life':c['life'],'principal_selected':False,'source_life_id':c['source_life_id'],'source_tick':c['source_tick']},f,ensure_ascii=False,indent=2);f.write('\n')
 print(json.dumps({'life':c['life'],'physical':record['physical'],'parent':record['parent'],'new_native_ticks':0}))
if __name__=='__main__':main()
