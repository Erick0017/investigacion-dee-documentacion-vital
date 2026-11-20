"""Seal a compact analysis plus source delta. No simulation or life mutation.
All included original bytes are hashed. Complete omitted states remain local.
"""
from pathlib import Path
from datetime import datetime,timezone
import gzip,hashlib,importlib.util,json,shutil,time
from zipfile import ZipFile,ZIP_DEFLATED
L=Path(__file__).resolve().parent;R=L.parents[2];S=R/'sistema';E=R/'evidencia/campanas/CONSOLIDACION_EVOLUCION_E1_CICLO_02';X=E/'EXPORTACION'
WORK=Path('D:/GENESIS AI/GENESIS 5.0/simulador de universo ab-initio/dee_libreria/VERSION_27/tests')
STAGE=WORK/'_c02_stage_20261022_01'
DEST=R/'entregas/DEE_COGNITIVE_1_1_CONSOLIDACION_EVOLUCION_E1_CICLO_02_ANALISIS.zip'
budget=json.loads((L/'PRESUPUESTO.json').read_bytes());assert time.monotonic()<budget['monotonic_deadline']
if STAGE.exists()or DEST.exists():raise FileExistsError('Use a new identified candidate rather than overwriting a seal')
STAGE.mkdir();sources=[];included=set()
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(name,value):
    p=STAGE/name;p.parent.mkdir(parents=True,exist_ok=True)
    if isinstance(value,str):p.write_text(value,encoding='utf8')
    else:p.write_text(json.dumps(value,ensure_ascii=False,indent=2),encoding='utf8')
def add(p,name=None,role=None):
    p=Path(p);name=name or p.name;target=STAGE/name;target.parent.mkdir(parents=True,exist_ok=True)
    if target.exists():raise FileExistsError('Duplicate export member '+str(target))
    shutil.copy2(p,target);assert sha(p)==sha(target)
    try:origin=str(p.relative_to(R))
    except ValueError:origin=str(p)
    sources.append({'original':origin,'exported_path':str(Path(name).as_posix()),'bytes':p.stat().st_size,'sha256':sha(p),'role':role or'Original bytes copied exactly'})
    included.add(str(p.resolve()));return target
for p in X.glob('*.md'):add(p,p.name)
for p in X.glob('*.csv'):add(p,p.name)
for p in(X/'EVIDENCIA_CAUSAL/PRIMARIOS').glob('*.json.gz'):add(p,'EVIDENCIA_CAUSAL/PRIMARIOS/'+p.name,'Exact retained JSON subtree extraction; source-byte and omitted-subtree hashes are inside')
add(X/'EVIDENCIA_CAUSAL/INDICE_EXTRACCION.json','EVIDENCIA_CAUSAL/INDICE_EXTRACCION.json')
for name in('RECIBOS_OPERACIONES_EXACTOS.json.gz','REFERENCIAS_ENTORNO.json','ENCUENTROS_EXACTOS_ZERO_TICKS.json','TUBO_NEGATIVO_21118_ZERO_TICKS.json',
 'ACLARACION_CAUSAL_ESTADO_FUENTE.json','OBSERVADOR_DIAGNOSTICO_221_COMPARACION.json','OBSERVACION_LATERAL_COMPARACION_314.json',
 'COMPROBACION_OPERATIVA_FINAL_328.json','SEPARACION_INCORPORACION_PARIDAD_357.json','SEPARACION_INCORPORACION_FINAL_364.json',
 'COMPROBACION_LANZADOR_365.json','C02_ADMISION_OPERATIVA_IC01.json'):
    add(E/name,'EVIDENCIA_CAUSAL/'+name)
for p in E.glob('*PROTOCOLO*.json'):add(p,'PROTOCOLOS_CONGELADOS/'+p.name)
for name in('ACCIONES_HIPOTESIS_R2.json','DIAGNOSTICO_TARDIO_CONTINUACION_221.json','CORTE_CONSECUENCIA_DIAGNOSTICO_R2.json'):
    add(E/name,'PROTOCOLOS_CONGELADOS/'+name)
add(R/'CONTINUIDAD_CICLO02.json','CONTINUIDAD_CICLO02.json');add(E/'FICHAS_ENTES_Y_ASISTENCIA.json','FICHAS_ENTES_Y_ASISTENCIA.json')
add(E/'CALCULOS_REPETIBLES.json','RECALCULO/CALCULOS_ESPERADOS.json');add(E/'TABLAS_DATOS.json','RECALCULO/TABLAS_DATOS.json')
for name in('recalcular.py','referencias_entorno.py','verificar_exportacion.py'):add(L/name,'RECALCULO/'+name)
add(S/'capacidades/observador_causal_retrospectivo_01.py','RECALCULO/snapshot_reader.py','Previously validated passive snapshot parser, no engine import/tick API')
add(E/'VERIFICACION_TABLAS.json','RECALCULO/VERIFICACION_TABLAS.json')
for p in L.glob('*.py'):add(p,'CODIGO_EXPERIMENTAL_Y_REVISIONES/'+p.name)
add(L/'exportar_tablas.mjs','CODIGO_EXPERIMENTAL_Y_REVISIONES/exportar_tablas.mjs')
modified=['gestionar.py','capacidades/integracion_situada_01/__init__.py','capacidades/integracion_situada_01/recovery.py',
 'capacidades/integracion_situada_01/gate_world.py','capacidades/integracion_situada_01/social_guard.py',
 'capacidades/integracion_situada_01/message_detour.py','capacidades/integracion_situada_01/lateral_social.py',
 'capacidades/integracion_situada_01/support_separation.py','capacidades/CATALOGO_CAPACIDADES.json',
 'contratos/CONSOLIDACION_EVOLUCION_CICLO02.json','contratos/INTEGRACION_COGNITIVA_SITUADA_E1_01.json',
 'documentacion/USO_CAPACIDADES_ADMITIDAS_CICLO02.md']
for name in modified:add(S/name,'DELTA_SISTEMA/sistema/'+name)
for name in('ic_native_core.py','ic_external.py','ic_body.py','delayed_social.py','regression.py'):
    add(S/'capacidades/integracion_situada_01'/name,'FUENTES_INSTRUMENTALES_IC01/'+name,'Unchanged native preparation/transduction to interpret the new experiments; not a redistributed engine')
add(R/'LEER_PRIMERO.md','DELTA_SISTEMA/LEER_PRIMERO.md')
add(L/'CATALOGO_ANTES_CICLO02.json','DELTA_SISTEMA/BASES/CATALOGO_ANTES_CICLO02.json')
add(L/'CONTRATO_IC01_ANTES_CICLO02.json','DELTA_SISTEMA/BASES/CONTRATO_IC01_ANTES_CICLO02.json')
word=R/'DEE_Cognitive_System_1_1_Manual_Maestro_Continuidad_Edicion_1_6_CICLO02_SIN_VALIDACION_VISUAL.docx'
add(word,'MANUAL/Manual_Maestro_1_6_CICLO02_SIN_VALIDACION_VISUAL.docx')
for name in('CAMBIOS_MANUAL_ACTUAL.json','VALIDACION_VISUAL_WORD.json'):add(E/name,'MANUAL/'+name)
initial=json.loads((E/'INICIO_Y_PADRE.json').read_bytes())
save('IDENTIDAD_Y_PADRE.json',{k:initial[k]for k in('identity','python','platform','ticks_advanced','parent_selected_before_new_evaluation','reason','protected_default','main_id')})
add(E/'FIN_EXPERIMENTAL.json','FIN_EXPERIMENTAL.json')
# Selected, complete byte-identical physical witnesses. Not every checkpoint.
sp=importlib.util.spec_from_file_location('snapshot_only',S/'capacidades/observador_causal_retrospectivo_01.py');reader=importlib.util.module_from_spec(sp);sp.loader.exec_module(reader)
full=[]
def witness(p,role,operational=False):
    p=Path(p);x=reader.Snapshot(p);relative='EVIDENCIA_CAUSAL/SNAPSHOTS_COMPLETOS/'+role+'.deetsnap.gz';add(p,relative,'Complete original snapshot bytes; '+('normal operation boundary'if operational else'diagnostic/source physical witness, not advertised as a manager continuation boundary'))
    full.append({'role':role,'exported_path':relative,'original':str(p.relative_to(R)),'sha256':x.encoded_sha256,'bytes':x.encoded_bytes,'tick':x.tick,'N':x.N,
         'RAW_sha256':reader.sha(reader.pbytes(x.raw)),'clocks_sha256':reader.sha(reader.pbytes(x.clocks)),'pending_count':len(x.pending),
         'checksum_valid':x.checksum_valid,'manager_operation_boundary':operational})
clar=json.loads((E/'ACLARACION_CAUSAL_ESTADO_FUENTE.json').read_bytes())
witness(clar['actual_C2_social_source']['path'],'source_pre_arm',True);witness(clar['original_IC01_armed_body_source']['path'],'source_committed',True)
witness(E/'VENTANA_DIAGNOSTICA_221/PRE_T21035.deetsnap.gz','pre21035')
witness(E/'C02_DIAG_220_ACCESO_TARDIO.POST_FIRST_DEPARTURE.deetsnap.gz','post21035')
witness(E/'C02_LATDIAG_314_MATERIAL_VENTANA/PRE_T21118.deetsnap.gz','pre21118')
witness(E/'C02_LATDIAG_314_MATERIAL.POST_DEPARTURE.deetsnap.gz','post21118')
witness(E/'C02_LATDIAG_315_PASIVO_VENTANA/PRE_T21118.deetsnap.gz','pre21118_no_new_entries')
witness(E/'C02_LATDIAG_315_PASIVO.POST_DEPARTURE.deetsnap.gz','post21118_no_new_entries')
for tick in(21111,21112,21114,21115,21118):witness(E/('C02_SEPARA_330_DOS_PULSOS.T'+str(tick)+'.deetsnap.gz'),'separation330_'+str(tick))
for num,tag in((331,'SHAM'),(332,'SOLO_ELEVAR')):witness(E/f'C02_SEPARA_{num}_{tag}.T21118.deetsnap.gz','control'+str(num)+'_21118')
for num,tag in((340,'PROTEGIDO'),(341,'SHAM'),(342,'SIN_RECORD'),(343,'OPUESTO')):
    witness(E/f'C02_COMMIT_{num}_{tag}.T3363.deetsnap.gz','committed'+str(num)+'_3363')
    witness(E/f'C02_COMMIT_{num}_{tag}.T3899.deetsnap.gz','committed'+str(num)+'_3899')
c=json.loads((R/'CONTINUIDAD_CICLO02.json').read_bytes())
for name,role in(('E1_CICLO02_MAIN','current_main'),('E1_CICLO02_SEPARACION_TRIPLE_01','current_triple')):
    d=next(z for z in c['lives']if z['life_id']==name);witness(S/d['snapshot'],role,True)
save('EVIDENCIA_CAUSAL/INDICE_SNAPSHOTS_COMPLETOS.json',{'scope':'Selected complete physical witnesses. Full operative/deep history remains local; not a substitute system package. Manager boundaries are explicitly identified.','files':full})
# Historical IC01 primary evidence reused, never re-simulated or counted as C2.
old=R/'evidencia/campanas/INTEGRACION_COGNITIVA_SITUADA_E1_01'
old_names=[f'GENERIC_RECOVERY_R2_{sign}_{mode}_167.json'for sign in('PLUS','MINUS')for mode in('RECOVER','SHAM','NONE')]
old_names +=[f'COST_{kind}_{num}{suffix}.json'for kind,num in(('NATIVE',73),('RETURN_OMIT',74),('ACTION_NULL',75))for suffix in('','_COMMON')]
old_names +=['GENERIC_RECOVERY_SPEC_167.json']
for name in old_names:add(old/name,'EVIDENCIA_CAUSAL/IC01_ANTECEDENTE/'+name,'Original archived IC01 primary bytes, no new ticks/reproduction claim')
add(R/'laboratorio/campanas/INTEGRACION_COGNITIVA_SITUADA_E1_01/recalcular.py','RECALCULO/recalcular_IC01_original.py')
save('LEER_PRIMERO.md','''# Ciclo 02: análisis privado

Empiece por INFORME_CIENTIFICO.md y las cinco tablas CSV. Son datos de 239 operaciones/registros, no 239 individuos ni 239 simulaciones independientes. El catálogo reúne once entradas IC01/C2 de dominio acotado; no son once facultades generales.

La continuación complementaria de tres códigos está localmente en E1_CICLO02_SEPARACION_TRIPLE_01 T21711. MAIN tiene otro estado en el mismo tick. El predeterminado E1_SOCIAL_11 T3154 sigue protegido. Lea CONTINUIDAD_CICLO02.json antes de interactuar. No se demostró nueva iniciativa P2 ni control competente de Pendulum.

## Recálculo sin motor

Desde una extracción limpia con Python 3.12/3.13 estándar:

```
python -I -B RECALCULO/verificar_exportacion.py --root . --salida ../COMPROBACION_C02.json
```

Este comando verifica hashes, datos RAW/clocks exactos, CSV, recibos, snapshots seleccionados, modelos de referencia y estructura Word. No ejecuta DEE ni Gymnasium. La reproducción nativa requiere el sistema local original y snapshots pertinentes; no ejecute indiscriminadamente CODIGO_EXPERIMENTAL_Y_REVISIONES.

## Alcance

Los PRIMARIOS conservan subárboles exactos, no el formato/bytes originales completos. Su índice remite a cada original y a lo omitido. Los snapshots seleccionados sí son archivos originales completos, incluidos controles adversos. Un snapshot diagnóstico a mitad de una función no equivale necesariamente a una frontera operativa del gestor.

DELTA_SISTEMA no incluye el motor ni todas las bases, estados y dependencias del sistema. Las vidas completas y la telemetría profunda siguen localmente. No es respaldo íntegro ni instalación autónoma. Las fuentes experimentales incluyen revisiones fallidas y ayudas de diagnóstico, no sólo capacidades promovidas.

El Word se editó realmente a 1.6, preservando 1.5. No está validado visualmente: falta LibreOffice soffice.exe. El lanzador .ps1 fue bloqueado por la política del SO; la guía muestra el CPython ya instalado, sin cambiar esa política.
''')
save('MANUAL/CAMBIOS_MANUAL.md',f'''# Cambio editorial real

Word actualizado en la raíz: {word.name}.
SHA-256: {sha(word)}.

Se incorporó el capítulo 23, enlace de índice, identificación 1.6, encabezados/pies y campos de página conservados. Software 1.1.0 y motor congelado permanecen. La edición 1.5 se mantiene sin cambios (SHA-256 b41e424beef3b9782750f7fe6008e9ea845e9f07532ea7c835371cc71c3c36bf).

Cambios: cinco admisiones IC01, tareas escalares útiles, protección de la interfaz social, acceso finito, separación de soportes, vidas actuales y sus pérdidas, límites P0/P1/P2 y comandos. No se incorporó código ni reglas internas del kernel al texto del manual.

La comprobación ZIP/XML y los dos campos de página resultaron válidos. El intento de render del archivo exacto falló: LibreOffice soffice.exe no está en PATH. No se entregan páginas visualmente verificadas ni se presenta un MD como sustituto del Word. Véase VALIDACION_VISUAL_WORD.json.
''')
save('DELTA_SISTEMA/ALCANCE_DEL_DELTA.md','''# Delta instalado y exportado

Los miembros de sistema/ son los bytes actuales de la capa Cognitive, no otro motor. El sistema local ya los utiliza; no hace falta instalarlos de nuevo para continuar.

Para cotejar otra copia compatible, verifique primero identidad del producto, versión de la base y hashes de BASES/. Compare cada archivo antes de una sustitución; no sobrescriba cambios ajenos, ACTIVO, VIDAS, snapshots o diarios. Este delta no transporta las biografías omitidas ni transfiere conocimientos. Los mecanismos nuevos tienen precondiciones físicas y contratos explícitos. La disponibilidad del código no equivale a que una vida haya adquirido su contenido.

Las funciones IC01 sin cambios y las revisiones del código científico se incluyen para entender/reproducir los protocolos con el sistema completo. El recálculo portable es una operación distinta de la reproducción nativa.
''')
# Trace source bytes without pretending an inventory hash was an executed import.
providers={}
for q in sources:
    if q['exported_path'].endswith('.py'):providers.setdefault(q['sha256'],[]).append(q['exported_path'])
code_refs=[]
for p in(X/'EVIDENCIA_CAUSAL/PRIMARIOS').glob('*.json.gz'):
    d=json.loads(gzip.decompress(p.read_bytes()))
    if d.get('code'):
        refs=[{'file_name':n,'recorded_hash':h,'available_exact_byte_providers':providers.get(h,[])}for n,h in d['code'].items()]
        code_refs.append({'operation':d['id'],'references':refs})
save('CODIGO_EXPERIMENTAL_Y_REVISIONES/INDICE_REVISIONES.json',{'scope':'The original run.code inventory hashes ALL lab Python files present, NOT the executed import set. Empty provider lists are preserved uncertainties, never fabricated source-byte attestation. Current functions and archived exact revisions are included. Dispatcher-only edits can differ from functions actually used; no blanket claim of complete loaded-module attestation.','records':code_refs})
omitted=[]
for directory in(E,L):
    # Deliberately do not walk node_modules, stage/export directories or history corpus.
    for p in directory.rglob('*')if directory==E else directory.glob('*'):
        if not p.is_file()or 'EXPORTACION'in p.parts or str(p.resolve())in included:continue
        if p.suffix in('.py','.mjs')and p.parent==L:continue
        if p.suffix not in('.json','.jsonl','.gz','.docx','.md'):continue
        omitted.append({'path':str(p.relative_to(R)),'bytes':p.stat().st_size,'sha256':sha(p),'reason':'Deep/duplicated source or previous editorial revision remains local; original evidence is not deleted or claimed regenerated.'})
save('INDICE_FUENTES_Y_OMISIONES.json',{'scope':'This campaign and explicitly reused IC01 sources only, not a new CPC corpus audit. Exact original source bytes vs canonical extracted values are distinguished.',
 'source_bytes_copied':sources,'omitted_local_campaign_files':omitted,
 'complete_current_states':[{k:v[k]for k in('life_id','tick','snapshot','snapshot_sha256','snapshot_encoded_bytes')}for v in c['lives']],
 'loss_of_coverage':'Not all per-tick contexts, full life operation journals, initial worlds or every old primary are exported. IDs/hashes/JSON pointers locate them locally. No claim of complete lossless historical backup or independent native reproduction from this analysis ZIP.',
 'analysis_limit_compressed_bytes':16000000})
save('INDICE_AFIRMACIONES.json',{'scope':'Each row points to original-byte-hashed primaries through INDICE_EXTRACCION.json; numbers are recalculated from fields, not verdict labels.',
 'claims':[
 {'claim':'Useful action via acquired consequence reference, not learned comparison law','cases':['C02_GATE_050_RETORNO','C02_GATE_051_SIN_RETORNO','C02_GATE_052_ACCION_ANULADA','C02_GATE_053_SHAM','C02_HIST_140_DESGASTE6','C02_HIST_141_DESGASTE13','C02_HIST_142_OMIT13','C02_HIST_143_SHAM13'],'recalc':'CALCULOS_ESPERADOS.json/gate_cases and main_gate'},
 {'claim':'Protect communication with original191pending inputs','cases':['C02_COMMIT_340_PROTEGIDO','C02_COMMIT_341_SHAM','C02_COMMIT_342_SIN_RECORD','C02_COMMIT_343_OPUESTO'],'recalc':'social_cases and raw snapshot source pair'},
 {'claim':'Both acquired signs recovered through fixed generic access; no content teacher','cases':['C02_PRE_110_PLUS_RESOURCE','C02_PRE_113_MINUS_RESOURCE','C02_PRE_111_PLUS_SHAM','C02_PRE_114_MINUS_SHAM','C02_PRE_116_NO_CONTENT_RESOURCE'],'recalc':'recovery_cases; IC01_ANTECEDENTE for admitted original P0'},
 {'claim':'Two finite layers, no learned P2 initiation','cases':['C02_REPET_190_DOS_CAPAS','C02_REPET_191_UNA_CAPA','C02_REPET_192_SIN_PERDIDA_PREVIA','C02_REPET_193_SIN_CONTENIDO','C02_CAPAS_217_CONTINUACION'],'recalc':'recovery_cases/external_cases'},
 {'claim':'Two different first losses, not global erasure inferred from a port','cases':['C02_DIAG_221_CONTINUACION','C02_LATDIAG_314_MATERIAL','C02_LATDIAG_315_PASIVO'],'recalc':'diagnostic_cases and complete pre/post witnesses'},
 {'claim':'Three-code use with prepared separation, plus new scalar experience','cases':['C02_SEPARA_330_DOS_PULSOS','C02_SEPARA_331_SHAM','C02_SEPARA_332_SOLO_ELEVAR','C02_SEPOP_357_USO4','C02_SEPOP_360_NUEVA_CONSECUENCIA','C02_SEPOP_361_ANTERIORES','C02_SEPOP_362_USO_TRAS_APRENDER'],'recalc':'separation_cases/external_cases and current_triple complete witness'},
 {'claim':'Adverse new private52 and lateral expansion preserved','cases':['C02_SEPARA_330_DOS_PULSOS','C02_LATERAL_270_REAL','C02_LATERAL_280_SOPORTE'],'recalc':'separation_cases/lateral_cases'}]})
case_ids=json.loads((E/'CALCULOS_REPETIBLES.json').read_bytes())['case_inventory']
assert all(id in case_ids for claim in json.loads((STAGE/'INDICE_AFIRMACIONES.json').read_bytes())['claims']for id in claim['cases'])
manifest=[]
for p in sorted(STAGE.rglob('*')):
    if p.is_file():manifest.append({'path':p.relative_to(STAGE).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)})
save('MANIFIESTO_HASHES.json',{'schema':'DCS.C02.analysis.members.v1','scope':'Manifest excludes its own hash and the container ZIP hash. Exact container hash belongs only in the external verification.','members':manifest})
DEST.parent.mkdir(parents=True,exist_ok=True)
with ZipFile(DEST,'x',compression=ZIP_DEFLATED,compresslevel=9)as z:
    for p in sorted(STAGE.rglob('*')):
        if p.is_file():z.write(p,p.relative_to(STAGE).as_posix())
assert DEST.stat().st_size<=16000000,'Preserve candidate; do not publish oversized analysis'
with ZipFile(DEST)as z:assert z.testzip()is None;count=len(z.namelist())
out={'stage':str(STAGE),'zip':str(DEST),'bytes':DEST.stat().st_size,'sha256':sha(DEST),'members':count,'complete_selected_witnesses':len(full),'native_ticks':0,'sealed_utc':datetime.now(timezone.utc).isoformat()}
(E/'CANDIDATO_SELLADO_01.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps(out,ensure_ascii=False))
