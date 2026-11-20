"""Final archival preservation/resource audit only; no DEE or subprocess runs."""
from pathlib import Path
from datetime import datetime,timezone
from collections import Counter,defaultdict
import argparse,hashlib,json
ROOT=Path(__file__).resolve().parents[1]
def sha(path):
 h=hashlib.sha256()
 with path.open('rb') as f:
  for b in iter(lambda:f.read(1024**2),b''):h.update(b)
 return h.hexdigest()
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def put(path,data):path.write_text(json.dumps(data,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')
def originals(documentation=None):
 inventory=ROOT/'genealogia/INVENTARIO_FUENTES.json';frozen=load(inventory)
 if documentation is None:documentation=next((p for p in ROOT.parents if p.name=='documantacion vital'),None)
 documentation=Path(documentation).resolve() if documentation else None
 rows=[]
 for row in frozen['archives']:
  relative=row['source_path_relative_to_documentation'];p=documentation/relative if documentation else None
  r={'id':row['id'],'source_relative_to_documentation':relative,'initial_sha256':row['sha256'],
     'initial_bytes':row['compressed_file_bytes'],'current_sha256':None,'current_bytes':None,'state':'NO_LOCALIZADA'}
  if p is not None and p.is_file():
   if not p.resolve().is_relative_to(documentation):raise ValueError('Inventario sale de raíz documental')
   before=p.stat();r['current_bytes']=before.st_size;r['current_sha256']=sha(p);after=p.stat()
   r['state']='PRESERVADA_BYTE_EXACTA' if r['current_sha256']==r['initial_sha256'] and before.st_size==r['initial_bytes'] else 'DISCREPANCIA'
   r['source_changed_during_hash']=(before.st_size,before.st_mtime_ns)!=(after.st_size,after.st_mtime_ns)
   if r['source_changed_during_hash']:r['state']='CAMBIO_DURANTE_LECTURA'
  rows.append(r)
 assert len(rows)==24
 report={'schema':'CPC8.final_original_preservation.v1','checked_utc':datetime.now(timezone.utc).isoformat(),
   'operation':'Sólo lectura streaming SHA-256 de los24 archivos del inventario inicial; no ZIP fuente alterado ni reempaquetado',
   'inventory':{'path':inventory.relative_to(ROOT).as_posix(),'sha256':sha(inventory)},
   'sources':rows,'counts':dict(Counter(r['state'] for r in rows)),
   'status':'PRESERVACION_24_DE_24_VERIFICADA' if all(r['state']=='PRESERVADA_BYTE_EXACTA' for r in rows) else 'REVISAR_DISCREPANCIAS_O_FUENTES_FALTANTES',
   'source_generator_sha256':sha(Path(__file__))}
 put(ROOT/'revision/PRESERVACION_ORIGINALES.json',report)
 return {'status':report['status'],'counts':report['counts'],'sha256':sha(ROOT/'revision/PRESERVACION_ORIGINALES.json')}
def classify(argv):
 scripts=[str(a).replace('\\','/').split('/')[-1] for a in argv if str(a).endswith('.py')]
 script=scripts[-1] if scripts else ''
 coordinator=('batch' in script or 'control_batch' in script) and ('run_' not in script)
 if script in ('control_batch.py','control_batch_v2.py','ejecutar_lote.py','ejecutar_contacto_lote.py'):coordinator=True
 if coordinator:return 'COORDINADOR_SIN_MUESTRAS_PROPIAS',script
 if any(x in script for x in ('regress','install','setup','smoke','identity')):return 'INSTALACION_O_VALIDACION_TECNICA',script
 if any(x in script for x in ('analy','summary','dossier','audit','reconcil','verificar')):return 'ANALISIS_O_DOCUMENTACION',script
 if script in ('run_comparison.py','run_mlp_private.py') and '--method' in argv and argv[argv.index('--method')+1] in ('B1','B2'):
  return 'COMPARADOR_CONVENCIONAL',script
 if script=='discovery.py':return 'DESCUBRIMIENTO_COMPARADOR_CONVENCIONAL',script
 if 'demo' in script:return 'DEMOSTRACION_TECNICA',script
 return 'TRABAJO_SUPERVISADO_NO_IDENTIFICADO_COMO_MUESTRA_INDEPENDIENTE',script
def union_seconds(intervals):
 intervals=sorted(intervals);total=0.;end=None
 for a,b in intervals:
  if end is None or a>end:total+=b-a;end=b
  elif b>end:total+=b-end;end=b
 return total
def resources():
 jobs=[];incomplete=[];intervals=[];groups=defaultdict(list)
 for folder in sorted((ROOT/'jobs').iterdir()):
  if not folder.is_dir():continue
  command=folder/'COMMAND.json';start=folder/'START.json'
  if not command.is_file():
   item={'job':folder.name,'state':'SIN_CIERRE_COMMAND','START_present':start.is_file()}
   if start.is_file():item.update(start_sha256=sha(start),start=load(start))
   incomplete.append(item);continue
  d=load(command);kind,script=classify(d.get('argv',[]));has_pid=d.get('pid') is not None
  closed=(bool(d.get('owned_worker_waited')) and bool(d.get('owned_job_closed'))) if has_pid else d.get('status') not in ('RUNNING','STARTING')
  row={'job':folder.name,'command':command.relative_to(ROOT).as_posix(),'command_sha256':sha(command),
    'start':start.relative_to(ROOT).as_posix() if start.is_file() else None,'start_sha256':sha(start) if start.is_file() else None,
    'type':kind,'script':script,'status':d.get('status'),'exit_code':d.get('exit_code'),'pid':d.get('pid'),
    'elapsed_seconds':d.get('elapsed_seconds'),'peak_job_memory_bytes':d.get('peak_job_memory_bytes'),
    'peak_process_memory_bytes':d.get('peak_process_memory_bytes'),'memory_limit_bytes':d.get('memory_limit_bytes'),
    'native_slot_required':d.get('native_slot_required'),'owned_worker_closed':closed,
    'started_utc':d.get('started_utc'),'finished_utc':d.get('finished_utc'),
    'cpu_seconds':None,'cpu_scope':'COMMAND no mide CPU; no se sustituye por tiempo de pared',
    'count_as_independent_trajectory':False,'counting_reason':'Un job puede ser coordinador, repetir/restaurar una trayectoria o contener varias cohortes; independencia procede del caso, no del proceso'}
  jobs.append(row);groups[kind].append(row)
  if not closed:incomplete.append({'job':folder.name,'state':'CIERRE_NO_CONFIRMADO','command':row['command']})
  if d.get('started_utc') and d.get('finished_utc'):
   intervals.append((datetime.fromisoformat(d['started_utc']).timestamp(),datetime.fromisoformat(d['finished_utc']).timestamp()))
 storage=defaultdict(lambda:{'files':0,'stored_bytes':0});snapshots=[];primary=[]
 for path in ROOT.rglob('*'):
  if not path.is_file() or '__pycache__' in path.parts:continue
  rel=path.relative_to(ROOT).as_posix()
  if rel.startswith(('staging/','entrega/','entrega_candidata/')):continue
  if path.name in ('RECURSOS_Y_COSTES.json','PRESERVACION_ORIGINALES.json'):continue
  suffix=path.name.lower();is_snapshot=('.deetsnap' in suffix or suffix.endswith(('.deetsnap.gz','.deetsnapz')))
  category='CHECKPOINTS_FISICOS_Y_OPERATIVOS' if is_snapshot else 'WHL_UNICO' if suffix.endswith('.whl') else rel.split('/')[0] if '/' in rel else 'RAIZ_TECNICA'
  storage[category]['files']+=1;storage[category]['stored_bytes']+=path.stat().st_size
  if is_snapshot:snapshots.append({'path':rel,'stored_bytes':path.stat().st_size,'format':'gzip' if suffix.endswith('.gz') else 'native_or_declared','not_a_replica':True})
  if rel.startswith('resultados/') and path.name=='MEASUREMENTS.json':
   d=load(path)
   primary.append({'path':rel,'sha256':sha(path),'status':d.get('status'),
     'case_id':d.get('case_id',d.get('case',{}).get('id')),'individual':d.get('individual'),
     'parent':d.get('parent'),'preparations_explicit':d.get('preparations'),'diagnostic_forks_explicit':d.get('diagnostic_forks'),
     'independence_inferred_from_file':False})
 bytype={k:{'jobs':len(v),'sum_elapsed_seconds':sum(r['elapsed_seconds'] or 0 for r in v),
   'maximum_single_job_peak_bytes':max((r['peak_job_memory_bytes'] or 0 for r in v),default=0),
   'nonzero_exits':sum(r['exit_code'] not in (None,0) for r in v)} for k,v in groups.items()}
 cmp=ROOT/'comparadores/SUMMARY.json';csummary=load(cmp) if cmp.is_file() else None
 report={'schema':'CPC8.resources_and_costs.v1','checked_utc':datetime.now(timezone.utc).isoformat(),
   'scope':'Auditoría de recursos y almacenamiento desde metadatos existentes; ningún experimento ejecutado',
   'budget':load(ROOT/'BUDGET.json'),'jobs':jobs,'job_types':bytype,'unclosed_or_missing_command':incomplete,
   'totals':{'job_records':len(jobs),'job_start_without_confirmed_close':len(incomplete),
      'busy_wall_interval_union_seconds':union_seconds(intervals),
      'noncoordinator_sum_elapsed_seconds_not_cpu':sum(r['elapsed_seconds'] or 0 for r in jobs if r['type']!='COORDINADOR_SIN_MUESTRAS_PROPIAS'),
      'maximum_single_job_peak_memory_bytes':max((r['peak_job_memory_bytes'] or 0 for r in jobs),default=0),
      'primary_measurement_records_not_independent_worlds':len(primary),'snapshot_files_not_replicas':len(snapshots),
      'snapshot_stored_bytes':sum(r['stored_bytes'] for r in snapshots),'work_tree_stored_bytes_at_scan':sum(v['stored_bytes'] for v in storage.values())},
   'storage_categories':dict(storage),'snapshots':snapshots,'primary_records':primary,
   'storage_scope':'Bytes almacenados en WORK al escanear, excluidos caches/staging y los dos informes generados de recursos/preservación para evitar autorreferencia; el ZIP exacto se mide posteriormente.',
   'counting_rules':['No sumar tiempo de coordinador a sus hijos para estimar coste de trayectoria.',
     'La suma de duraciones de jobs concurrentes no es duración global; se ofrece además unión de intervalos.',
     'Los picos de RAM de jobs no se suman ni se presentan como pico simultáneo global.',
     'START conserva su estado RUNNING histórico; COMMAND posterior es el cierre. No es actividad actual por sí mismo.',
     'Archivos checkpoint, consultas, ticks, restauraciones y reproducciones no son réplicas independientes.',
     'Bytes almacenados de gzip no son tamaño nativo decodificado; no se descomprimen todos los estados para inventar memoria.',
     'Tipos de job son clasificación documental por comando, no dictamen de capacidad científica.'],
   'comparator_costs':{'path':'comparadores/SUMMARY.json','sha256':sha(cmp),'counts':csummary['counts'],'cases':csummary['cases']} if csummary else None,
   'source_generator_sha256':sha(Path(__file__))}
 put(ROOT/'revision/RECURSOS_Y_COSTES.json',report)
 return {'jobs':len(jobs),'unclosed':len(incomplete),'snapshots':len(snapshots),'primary_records':len(primary),'sha256':sha(ROOT/'revision/RECURSOS_Y_COSTES.json')}
def main():
 p=argparse.ArgumentParser();p.add_argument('mode',choices=('originals','resources','all'),default='all',nargs='?');p.add_argument('--documentation-root',type=Path);a=p.parse_args();r={}
 if a.mode in ('originals','all'):r['preservation']=originals(a.documentation_root)
 if a.mode in ('resources','all'):r['resources']=resources()
 print(json.dumps(r,ensure_ascii=False))
if __name__=='__main__':main()
