"""Small explicit provisional export list; no ZIP/build, runtime or report edits.

The template is finalized:false. Root must add actual AI closure/evidence and
LEER_PRIMERO, refresh the final report hashes and then freeze a NEW final plan.
Archive paths retain campaign-relative layout for the existing passive recalcs.
"""
from pathlib import Path
import argparse,datetime,hashlib,importlib.util,json,sys
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def run(a):
 out=Path(a.output);out=out if out.is_absolute()else ROOT/out
 if out.exists()or not out.resolve().is_relative_to(ROOT):raise ValueError('Fresh C02 template only')
 spec=importlib.util.spec_from_file_location('_C02_export_source_rules',ROOT/'control/empacar_evidencia_C02_R02.py')
 pack=importlib.util.module_from_spec(spec);sys.modules[spec.name]=pack;spec.loader.exec_module(pack)
 rows=[];missing=[];omissions=[];seen=set()
 def add(name,role,why):
  p=ROOT/name
  if not p.is_file():missing.append(dict(source=name,role=role,reason='Not present at template cut; do not invent'));return
  if name in seen:return
  try:pack.source_allowed(p,role)
  except ValueError as error:
   omissions.append(dict(source=name,bytes=p.stat().st_size,reason=str(error)));return
  raw=p.read_bytes();pack.validate_text(name,raw)
  rows.append(dict(source=name,archive=name,sha256=hashlib.sha256(raw).hexdigest(),role=role,selection_reason=why));seen.add(name)
 def direct(folder,role,why,suffixes=('.json','.csv','.jsonl')):
  base=ROOT/folder
  if base.is_dir():
   for p in sorted(base.iterdir()):
    if p.is_file()and p.suffix.lower()in suffixes:add(p.relative_to(ROOT).as_posix(),role,why)
 add('analisis/INFORME_C02.md','report','Root report; provisional hash must be refreshed after actual AI closure')
 add('entrega/LEER_PRIMERO_C02.txt','readme','Root entry and exact R09/recalculation commands; provisional state must be updated at final closure')
 add('capacidades/CONTINUIDAD_C02.json','continuity','Root maintained actual Native/PROGRAMMED closures and separate AI attempts; refresh at final closure')
 add('fuentes/LOCALIZADORES_REPERTORIO_BASE.json','map','Thirteen source rows with actual partial/static coverage; not integral Manual or Compendium reading')
 add('fuentes/MATRIZ_REPERTORIO_BASE.csv','map','Pre-C02 repertoire baseline; available mechanisms are distinct from a new C02 result')
 add('control/CRITICOS_DESPUES_CIENCIA_C02.json','verification','Root science-close comparison of eleven named protected files; not whole-project immutability')
 add('control/OMISIONES_LOCALIZADAS_C02.json','map','Explicit local omitted states, model weights, runtime, Manual and trace/staging coverage; null folder hashes are intentional')
 for name in('RECALCULO_COMPARATIVA_C02.py','RECALCULO_COMPARATIVA_C02_R02.py','RECALCULO_FUNCIONES_Y_MUNDO_C02.py','RECALCULO_ENLACE_NUMERICO_AMBIENTAL_C02_R04.py','RECALCULO_RECURSOS_MODELO_C02_R01.py',
              'COMPARAR_CONTROLES_MEMORIA_C02.py','COMPARAR_PRIMERA_LECCION_R01_R02.py','RESUMIR_MAIN_R02_FINAL_C02.py'):
  add('analisis/'+name,'recalculation','Existing passive calculations / declared portable adaptation, not Native reproduction')
 for folder in('MAIN_R02_FINAL_RECALCULO_R01','DEV_FUNCIONES_Y_MUNDO_RECALCULO_R01','CONTROL_ENLACE_NUMERICO_RECALCULO_R02',
                'CONTROL_MEMPAIR_RECALCULO_R01','PRIMERA_LECCION_R01_R02_CONTRASTE_R01','CIERRE_RECUPERADO_R01',
                'COMPARATIVA_FINAL_C02_R02','RECURSOS_MODELO_FINAL_C02_R01','HECHOS_FINALES_TRES_BRAZOS_C02_R01'):
  direct('analisis/'+folder,'verification','Completed passive calculation, including negatives and denominator coverage',('.json','.csv'))
 for name in('MAIN_PRIMERA_LECCION_ADMISION_R01.json','CORTE_CIENTIFICO_DEV4_Y_R01_PRE_R02.json'):
  add('analisis/'+name,'control','Decisive partial-admission / distinct-future interpretation')
 for name in('MAPA_ESTADO_FINAL_NATIVE_C02_R01.json',):add('evidencia/'+name,'continuity','Complete final local Native file hash map; not a state backup')
 add('evidencia/INDICE_CONTINUIDAD_AI02_C02_R02.json','continuity','Final same logical AI02 history across5/6/12/18; one history, not independent replicas')
 add('fuentes/MATRIZ_REPERTORIO_C02_FINAL_TRES_BRAZOS_R01.csv','continuity','Final source-backed three-arm repertoire; separates demonstrated use, assistance and missing evidence')
 for folder in('MAIN_R02_PERIODO_02','PROGRAMMED_PERIODO_02'):
  world='WORLD_FINAL.json'if folder.startswith('MAIN')else'WORLD_CHECKPOINT.json'
  add('evidencia/'+folder+'/'+world,'world_checkpoint','Whole final actual18 history, events, poses, S and geometry')
  for name in('RESULTADO.json','SOURCE_OWNER_CLOSED.json','COMPARATOR_CLOSED.json','WORLD_RESTORE_COMPARISON.json'):
   if(ROOT/'evidencia'/folder/name).is_file():add('evidencia/'+folder+'/'+name,'verification','Actual final closure / saved-reopened continuity witness')
 for folder in('MAIN_R02_PERIODO_01','MAIN_R02_RECUPERACION_R05','DEV_REAPERTURA_R04','PROGRAMMED_PERIODO_01'):
  for name in('WORLD_CHECKPOINT.json','WORLD_FINAL.json','RESULTADO.json','SOURCE_OWNER_CLOSED.json'):
   if(ROOT/'evidencia'/folder/name).is_file():add('evidencia/'+folder+'/'+name,'world_checkpoint'if name.startswith('WORLD_')else'verification','Actual intermediate prefix or executed technical control; not another independent life')
 for name in('ANCHOR_MUNDO_NATIVE_C02.json','BINDING_C02.json','SELLADO_VINCULO_C02.json','VERIFICACION_C02.json'):
  add('evidencia/MAIN_R02_SELLADO_R01/'+name,'continuity','Actual closed Native/World/bridge binding and verification, large state kept local')
 for folder in('CONTROL_MEMPAIR_R01','MAIN_V1_CIERRE_CONOCIDO_R01'):
  direct('evidencia/'+folder,'control','Preserved Native paired control / known partial failure, no adverse result omitted')
 for arm in('INTACT','CUT_B'):
  add('evidencia/CONTROL_ENLACE_NUMERICO_'+arm+'_R02/RESULTADO_AMBIENTAL_REPLAY_C02.json','control','Whole actual environment-only replay; no new Native action or learning')
 for name in('WORLD_CHECKPOINT.json','WORLD_FINAL.json'):
  p='evidencia/DEV_SELLADO_R02/PAREJA_C02/'+name
  if(ROOT/p).exists():add(p,'world_checkpoint','Original environmental-replay prefix; archived Native remainsT950523')
 # Full compact Native functions and actor phase journals, sharing prefix history
 # but never treating aliases as independent experiences.
 lives={'MAIN_R02':('ECI02_PI03_REPRO_PI04_PI05_PI07_PI10_RBX01_C02_MAIN_R02','RBX02_NATIVE_C02_R02'),
        'DEV':('ECI02_PI03_REPRO_PI04_PI05_PI07_PI10_RBX01_C02_DEV','RBX02_NATIVE_C02'),
        'MAIN':('ECI02_PI03_REPRO_PI04_PI05_PI07_PI10_RBX01_C02_MAIN','RBX02_NATIVE_C02'),
        'MEMPAIR':('ECI02_PI03_REPRO_PI04_PI05_PI07_PI10_RBX01_C02_MEMPAIR','RBX02_NATIVE_C02')}
 for branch,(life,actor)in lives.items():
  base=f'native/{branch}/sistema/estado/servicios_locales/{life}/{actor}'
  if(ROOT/base).is_dir():
   direct(base+'/functions','primary','Whole Native function primary including real receipts/raw values/admission status',('.json',))
   add(base+'/events.jsonl','primary','Exact compact Native actor phase journal; actual decisions/feedback, not platform logs')
 direct('comparadores/PROGRAMMED_R02_01','primary','Own closed PROGRAMMED history and actual policy journal; no Native attribution',('.json','.jsonl'))
 for name in('ESTADO_ADVERSO_NO_CONTINUABLE.json','ROOT_RECONCILIADO_CERRADO_NO_CONTINUABLE.json',
              'ROOT_RO_RECONCILIACION_MAILBOX.json','ROOT_STOP_CONOCIDO_INTENT.json','ROOT_STOP_CONOCIDO_RESULTADO.json',
              'relay.summary.json','RESULTADO.json'):
  add('evidencia/CONVENTIONAL_AI_R06_PERIODO_01/'+name,'control','AI01 technical transport failure: formed ASK preserved, zero actual actions/opportunities; not a resumable pair')
 direct('comparadores/CONVENTIONAL_AI_R06_01','control','Closed AI01 own cache/model journal preserved separately; never merged into fresh AI02',('.json','.jsonl'))
 direct('comparadores/CONVENTIONAL_AI_R06_02','primary','Final closed AI02 own policy cache/journal and exact runner identity, one continuous history',('.json','.jsonl'))
 add('comparadores/SERVIDOR_IA_C02_R03.jsonl','verification','Closed owned local model daemon lifecycle and resource measurements; no model weights')
 # Only current/executed source versions, never whole folders or engines.
 code=['control/empacar_evidencia_C02_R02.py','control/verificar_zip_y_recalculos_C02.py','control/mapa_estado_final_C02.py','control/preparar_omisiones_C02.py','control/preparar_plantilla_export_C02.py',
  'control/orquestar_C02_R02.py','control/orquestar_C02_R04.py','control/orquestar_comparador_C02_R02.py','control/orquestar_comparador_C02_R04.py','control/orquestar_comparador_C02_R06.py','control/orquestar_comparador_C02_R07.py','control/orquestar_comparador_C02_R08.py','control/orquestar_comparador_C02_R09.py','control/orquestar_comparador_C02_R10.py',
  'control/adjuntar_propietario_sin_material_C02_R05.py','control/adjuntar_comparador_sin_decisiones_C02_R03.py',
  'control/studio_mailbox_relay_C02_R03.py','control/studio_mailbox_relay_C02_R04.py','control/studio_mailbox_relay_C02_R05.py','control/studio_mailbox_relay_C02_R06.py','control/studio_mailbox_relay_C02_R07.py','control/mcp_operator_C02.py',
  'control/persistencia_C02.py','control/sellar_vincular_C02.py','control/sellar_vincular_C02_R03.py','control/path_guard_C02_R03.py',
  'control/transporte_checkpoint_C02_R02.py','control/decodificar_checkpoint_capturado_C02.py','control/decodificar_AI02_B05_root_C02.py','control/CAPTURA_AI02_B05_ROOT_C02.luau','control/CAPTURA_AI02_B12_ROOT_C02.luau','control/normalizar_y_sellar_comparador_C02.py','control/normalizar_y_sellar_comparador_C02_R02.py','control/instalar_host_C02.py',
  'control/control_memoria_reservado_C02.py','control/replay_enlace_numerico_C02_R02.py',
  'puente/rbx02_bridge_C02.py','puente/run_live_native_C02_R02.py','puente/run_comparador_C02_R02.py','puente/run_comparador_C02_R04.py',
  'native/rbx02_adapter_C02_R02.py','native/preparar_descendiente_C02_R02.py','native/rbx02_import0_C02_R02.py',
  'native/r02_bundle/rbx02_native_C02.py','native/r02_bundle/rbx02_identity_C02.py','native/r02_bundle/c02_funciones_native.py',
  'fuentes/rbx02_owner_support_C02_R02.py','fuentes/servicio_eventos_C02.py','fuentes/cache_fuentes_C02.py',
  'comparadores/adaptadores_C02.py','comparadores/cliente_ia_local_C02.py','comparadores/servidor_ia_local_C02_R03.py',
  'control/cerrar_AI01_conocido_root_C02.py']
 for name in code:add(name,'code','Executed/new declared C02 interface/observer/persistence/model wrapper; no motor binary')
 for name in('Config_C02.luau','Body_C02.luau','Controller_C02.server.luau','Bridge_mailbox_C02.luau','EstadoPareja_C02.luau','ExportarRegistros_C02.luau'):
  add('mundo/'+name,'code','Shared actual C02 world/transport source; R02 overrides are included separately, original branches preserved')
 for name in('PROTOCOLO_REPLAY_ENLACE_C02.json','PAYLOAD_REPLAY_ENLACE_C02.json'):
  for revision in('R01','R02'):
   add('evidencia/CONTROL_ENLACE_NUMERICO_PREPARADO_'+revision+'/'+name,'protocol','Prospectively prepared environment-only replay, exact sources and historical numeric result; not new DEE learning')
 for arm in('INTACT','CUT_B'):
  add('evidencia/CONTROL_ENLACE_NUMERICO_'+arm+'_R02/INTENCION_UNICA_REPLAY.json','protocol','Actual single replay admission intent, preserving no-Native and no-retry scope')
 # Closed AI02 prefixes: metadata and literal Worlds only, never live SQLite.
 for folder in('CONVENTIONAL_AI_R06_02_PERIODO_01','CONVENTIONAL_AI_R06_02_PERIODO_02','CONVENTIONAL_AI_R06_02_PERIODO_03','CONVENTIONAL_AI_R06_02_PERIODO_04','CONVENTIONAL_AI_R06_02_PERIODO_05'):
  for name in('RESULTADO.json','COMPARATOR_CLOSED.json','WORLD_CHECKPOINT.json','WORLD_RESTORE_COMPARISON.json','ROOT_RESTAURACION_ABORTADA.json','WORLD_CHECKPOINT.root_provenance.json','TRANSPORTE_ROOT_META.json'):
   if(ROOT/'evidencia'/folder/name).is_file():add('evidencia/'+folder+'/'+name,'world_checkpoint'if name.startswith('WORLD_CHECKPOINT')else'verification','Same AI02 history; checkpoints5/6 or explicit pre-owner restore failure, never an extra independent arm')
  # The single known parser error is decisive; successful raw chunk echoes are omitted.
  name='02_restore_chunk_0001.json'
  if folder.endswith('PERIODO_02')and(ROOT/'evidencia'/folder/name).is_file():add('evidencia/'+folder+'/'+name,'control','Explicit Luau parser failure before restore apply/owner; zero new policy calls')
 for folder in('AI02_SELLADO_FRONTERA5_R02','AI02_SELLADO_FRONTERA6_R01','AI02_SELLADO_FRONTERA12_R01'):
  for name in('NORMALIZACION_Y_SELLADO_COMPARADOR.json','BINDING_COMPARATOR_C02.json','RESUMIR_COMPARADOR.json'):
   if(ROOT/'evidencia'/folder/name).is_file():add('evidencia/'+folder+'/'+name,'continuity','Actual same-history closed World/policy/bridge checkpoint; large/live SQLite kept local')
  pair='evidencia/'+folder+'/PAIR_COMPARATOR_C02'
  for name in('PAIR_COMPARATOR_C02.json','ANCHOR_COMPARATOR_C02.json','CIERRE_COMPARADOR.json','POLICY_STATE_C02.json','RUNNER_IDENTITY_C02.json'):
   if(ROOT/pair/name).is_file():add(pair+'/'+name,'continuity','Sealed component hashes and identity; preserve both5 and6 without merging futures')
 for p in sorted((ROOT/'mundo').glob('*C02*R02*.luau')):add(p.relative_to(ROOT).as_posix(),'code','Versioned physical world or environmental replay source')
 for name in('CODE_SCOPE_C02_R02.json','FUENTES_CONGELADAS_EVALUACION_R03.json','PROTOCOLO_EVALUACION_C02_R04.json','PRESUPUESTO_C02_R04.json','ESCENARIO_CONGELADO_C02_R03.json','CONTROL_MEMORIA_RESERVA_C02.json','PRESUPUESTO_AI_C02_R05.json','PRESUPUESTO_AI_C02_R06.json',
              'FUENTES_REANUDACION_AI_C02_R05.json','FUENTES_ACTUALES_AI_C02_R07.json'):
  add('protocolo/'+name,'protocol','Frozen Native sources / prospective scenario and honestly resumed AI budget')
 direct('protocolo/correcciones_pre_native/cierre_final_etiqueta_boundary_R02','verification','Counter-field erratum with original source preserved, not a policy rewrite',('.json',))
 add('control/LEDGER_C02.json','primary','Actual aggregate Native ledger, preserved failed reservation; ticks are not independent cognitive trials')
 for name in('comparadores/CUOTA_LLM_C02.json','comparadores/MODELO_LOCAL_PREPARADO_C02.json'):
  add(name,'primary','Actual shared model quota / fixed local model metadata; refresh quota hash only after AI closes, never reset reservations')
 # Byte-identical before/after/copy aliases are identified, not packaged twice
 # or counted as distinct events. Root can cite this omission map at closure.
 unique=[];by_hash={};aliases=[]
 for row in rows:
  if row['sha256']in by_hash:
   aliases.append(dict(omitted_source=row['source'],same_bytes_as=by_hash[row['sha256']]['source'],sha256=row['sha256'],
    reason='Byte-identical content alias preserved locally; one full copy is selected, not a new event or omitted divergent result.'))
  else:by_hash[row['sha256']]=row;unique.append(row)
 rows=unique
 value=dict(schema='DEE.RBX01.C02.final_export.R01',finalized=False,prepared_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
  files=rows,critical_baseline='control/CRITICOS_ANTES_C02.json',
  pending_before_finalization=[
   'Final18 Native/PROGRAMMED/AI02 Worlds, own closures, policy states and model journal are selected; verify Root final conclusions and video/QC additions before freeze.',
   'Refresh INFORME_C02.md and CONTINUIDAD_C02.json after Root final closure edits. Preparer never edits these files.',
   'LEER_PRIMERO now describes actual18/18/18 and portable recalculation; reconcile against the final report before freeze.',
   'Root freezes a NEW finalized:true plan after inspecting negatives, omissions and all source hashes.'],
  missing_at_template_cut=missing,excluded_by_rules=omissions,content_aliases_not_duplicated=aliases,
  omission_policy='Motor/models/fullNativeRoot/SQLite/videos/MCPchunk duplicates remain local; final Native hash map supplies exact paths and component hashes.',
  projected_content_files=len(rows),projected_uncompressed_bytes=sum((ROOT/r['source']).stat().st_size for r in rows),
  exact_zip_limit_bytes=15000000,analysis_not_executable_backup=True,Native_calls=0,MCP_calls=0,model_calls=0)
 with out.open('x',encoding='utf8')as f:json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n')
 return dict(template=str(out),sha256=sha(out),files=len(rows),raw_bytes=value['projected_uncompressed_bytes'],missing=len(missing),omissions=len(omissions),finalized=False)
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);print(json.dumps(run(p.parse_args()),indent=2))
