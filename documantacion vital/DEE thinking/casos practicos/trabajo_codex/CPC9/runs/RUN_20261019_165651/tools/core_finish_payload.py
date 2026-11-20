"""Derived technical docs and immutable current recovery evidence, no engine."""
from pathlib import Path
from collections import Counter
import ast,csv,hashlib,json,shutil,zipfile
RUN=Path(__file__).resolve().parents[1];CORE=RUN/'core/DEE_COGNITIVE_CORE';notes=RUN/'notes/core_audit'
def put(p,o):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def sha(p):
 h=hashlib.sha256()
 with p.open('rb')as f:
  for b in iter(lambda:f.read(1024**2),b''):h.update(b)
 return h.hexdigest()
proofs={'CP01_RECALCULADO.json':notes/'CP01_RECALCULADO.json','CP02_RECOVERY.json':notes/'CP02_v1/RECOVERY.json','SEM01_RECALCULADO.json':notes/'SEM01_RECALCULADO.json','CPC4_v1_RECOVERY.json':notes/'CPC4_v1/RECOVERY.json','CPC5_v1_RECOVERY.json':notes/'CPC5_v1/RECOVERY.json','CPC6_v1_RECOVERY.json':notes/'CPC6_v1/RECOVERY.json','CPC7_RECOVERY.json':notes/'CPC7_v1/RECOVERY.json','MCTS_RECOVERY.json':notes/'MCTS_v1/RECOVERY.json','K65_RECALCULADO.json':notes/'K65_RECALCULADO.json','PRODUCT45_v1_RECOVERY.json':notes/'PRODUCT45_v1/RECOVERY.json','PRODUCT45_EXTRA_v1_RECOVERY.json':notes/'PRODUCT45_EXTRA_v1/RECOVERY.json','RCA_RECOVERY.json':notes/'RCA_v1/RECOVERY.json','COUNT_RECOVERY.json':notes/'COUNT_v1/RECOVERY.json'}
ext=RUN/'notes/core_extension_v2'
for name,relative in {
 'ORDERED_RECALCULADO.json':('audit','ORDERED_RECALCULADO.json'),
 'NATIVE_LOOP_RECALCULADO.json':('audit','NATIVE_LOOP_RECALCULADO.json'),
 'CENTRAL_RECALCULADO.json':('audit','CENTRAL_RECALCULADO.json'),
 'STREAM_RECOVERY.json':('ext','STREAM_v2/RECOVERY.json'),
 'NETWORK_RECOVERY.json':('ext','NETWORK_v1/RECOVERY.json'),
 'ARCHITECTURES_RECOVERY.json':('ext','ARCHITECTURES_v1/RECOVERY.json'),
 'BRIDGE_RECOVERY.json':('ext','BRIDGE_v1/RECOVERY.json'),
 'CAPACITY_RECOVERY.json':('ext','CAPACITY_v1/RECOVERY.json'),
 'LONGITUDINAL_RECOVERY.json':('ext','LONGITUDINAL_v1/RECOVERY.json'),
 'POLICY_RECOVERY.json':('ext','POLICY_v1/RECOVERY.json'),
 'QFM_RECOVERY.json':('ext','QFM_v1/RECOVERY.json'),
 'L15_RECOVERY.json':('ext','L15_v1/RECOVERY.json'),
 'NEED_RECOVERY.json':('ext','NEED_v2/RECOVERY.json'),
 'MISSING_RECOVERY.json':('ext','MISSING_v1/RECOVERY.json'),
 'RETENTION_EARLY_RECOVERY.json':('ext','RETENTION_EARLY_v1/RECOVERY.json'),
 'RETENTION_WORD_RECOVERY.json':('ext','RETENTION_WORD_v1/RECOVERY.json'),
 'RETENTION_LATE_RECOVERY.json':('ext','RETENTION_LATE_v1/RECOVERY.json'),
 'SOCIAL_RECOVERY.json':('ext','SOCIAL_v1/RECOVERY.json')}.items():
 proofs[name]=(notes if relative[0]=='audit'else ext)/relative[1]
for name,p in proofs.items():
 v=json.loads(p.read_text(encoding='utf8'));assert v['status']=='PASS',(name,v['status']);dest=CORE/'verificaciones'/name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,dest)
for label,p in(('CP01_AUDITOR_INICIAL',notes/'CP01_v2/RECOVERY.json'),('K65_AUDITOR_INICIAL',notes/'K65_v1/RECOVERY.json'),('SEM01_AUDITOR_INICIAL',notes/'SEM01_v1/RECOVERY.json')):shutil.copyfile(p,CORE/'verificaciones'/(label+'.json'))
for label,p in(
 ('CORE15_17_RECALCULADO',notes/'CORE15_17_RECALCULADO.json'),
 ('CORE15_17_RECALCULADO_ATTEMPT1',notes/'CORE15_17_RECALCULADO_ATTEMPT1.json'),
 ('ORDERED_AUDITOR_INICIAL',ext/'ORDERED_v4/RECOVERY.json'),
 ('STREAM_SOURCE_EVOLUTION_INITIAL',ext/'STREAM_v1/RECOVERY.json'),
 ('NATIVE_LOOP_AUDITOR_INICIAL',ext/'NATIVE_LOOP_v1/RECOVERY.json'),
 ('CENTRAL_AUDITOR_INICIAL',ext/'CENTRAL_v1/RECOVERY.json'),
 ('CENTRAL_AUDITOR_RECALC_ATTEMPT1',notes/'CENTRAL_RECALCULADO_ATTEMPT1.json'),
 ('STORE_APPEND_REPAIR',notes/'STORE_APPEND_REPAIR.json')):
 if p.exists():shutil.copyfile(p,CORE/'verificaciones'/(label+'.json'))
attempts={'schema':'DEE_CORE.technical_attempts.v1','physics_or_decoder_modified':False,'attempts':[{'id':'inventory_in_memory','result':'Ownbuilderstoppedafter~1.5GiBRAM; noengine/nohistoricalwrites. Replacedbystreaminggzipwithoneblobrecordatatime.'},{'id':'CP01_launch_relative','result':'Supervisorcwdresolvedrelativefilewrong; pre-engineexit2. Repairedwithexplicitabsolutecommandpaths.'},{'id':'CP01_auditor','result':'TuplevsJSONarrayandattemptfilenameerroneouslycomparedasphysicaldifferences. CorrectedneutralJSONandseparatedmetadata; actualunchangedallstate/observationcomparisonsPASS.'},{'id':'K65_auditor','result':'Assumednegativecontrolanswerswerewrong. Preservedactual32→65→65learningduringqueriesand63/64offpathretention; reproductioncomparesimmutablehistoricalnativeobservations,notatuneddecoder.'},{'id':'SEM01_auditor','result':'Legacystr(object)hostmemoryaddressesdiffer. Comparetype/countseparatelyfromexactphysicalpre/post/usefields; actualnativeobservationsunchanged.'}], 'original_failed_reports_included':True,'scientific_scope':'No scientific failedcasewasremovedorrelabeledasfunctionalcomprehension. Initialauditorfailuresaretechnicalclassificationerrors.'}
put(CORE/'verificaciones/INTENTOS_TECNICOS_Y_CORRECCIONES.json',attempts)
idx=json.loads((CORE/'documentacion/INDICE_MIEMBROS.json').read_text(encoding='utf8'));rows=idx['paths'];by=Counter();logical=0;unique={}
for n,r in rows.items():by[n.split('/')[0]]+=1;logical+=r['bytes'];unique[r['sha256']]=r['bytes']
inv=json.loads((CORE/'documentacion/INVENTARIO_SELECCION.json').read_text(encoding='utf8'));historical_expanded=sum(r['expanded_bytes']for r in inv['historical_archives']);historical_compressed=sum(r['compressed_bytes']for r in inv['historical_archives'])
corpus={'schema':'DEE_CORE.compression.v1','historical_CPC3_to7_archives':inv['historical_archives'],'historical_CPC3_to7_expanded_bytes':historical_expanded,'historical_CPC3_to7_compressed_bytes':historical_compressed,'content_paths':len(rows),'unique_blobs':len(unique),'selected_logical_unpacked_bytes':logical,'unique_unpacked_bytes':sum(unique.values()),'dedup_saved_bytes':logical-sum(unique.values()),'store_gzip_bytes':(CORE/'mecanismos/RECUPERACION_POR_HASH.jsonl.gz').stat().st_size,'store_sha256':sha(CORE/'mecanismos/RECUPERACION_POR_HASH.jsonl.gz'),'path_groups':dict(by),'raw_snapshot_exclusion_CPC3_to7_bytes':inv['excluded_bytes_by_suffix'].get('.deetsnap',0),'exact_seed_snapshots_retained':11,'historical_ZIPs_nested':0,'wheel_count':len(list((CORE/'runtime').glob('*.whl'))),'count_scope':'CPC3containsCP01/CP02; the archive-sumcountsitsstoredcontentsincludinghistoricalcopies,notuniquescientificinformation. CPC8protectedZIPsizesreportedseparatelybelow.'}
for label,p in(('CPC8_reconstructed',RUN.parents[3]/'trabajo_codex/CPC8/runs/resultados/CPC8_ORGANIZACION_COGNITIVA_NATIVA_APRENDIZAJE65_RESULTADOS.zip'),('CPC8_initial',RUN.parents[3]/'trabajo_codex/CPC8/runs/historico/CPC8_ORGANIZACION_COGNITIVA_NATIVA_APRENDIZAJE65_RESULTADOS__65164c939621464c7d4faa800240bb1c2e25538ba9d878a65863016f57387c00.zip')):
 if p.is_file():
  with zipfile.ZipFile(p)as z:corpus[label]={'compressed_bytes':p.stat().st_size,'expanded_bytes':sum(i.file_size for i in z.infolist()),'sha256':sha(p)}
checkpoint_members=[{'path':n,**r}for n,r in rows.items()if n.endswith(('.deetsnap','.deetsnap.gz'))]
corpus['exact_seed_snapshots_retained']=len(checkpoint_members)
corpus['checkpoint_members']=checkpoint_members
corpus['all_historical_archive_copies_compressed_bytes']=historical_compressed+sum(corpus[k]['compressed_bytes']for k in('CPC8_initial','CPC8_reconstructed')if k in corpus)
corpus['all_historical_archive_copies_expanded_bytes']=historical_expanded+sum(corpus[k]['expanded_bytes']for k in('CPC8_initial','CPC8_reconstructed')if k in corpus)
corpus['excluded_scope']='La exclusión inicial de snapshots sin comprimir tiene excepciones posteriores explícitas: ocho padres comprimidos CPC6 y el padre L15, además de once semillas MBP4. La lista final de checkpoints retenidos es autoritativa.'
put(CORE/'documentacion/COMPRESION.json',corpus)
matrix=json.loads((CORE/'documentacion/MATRIZ_CAPACIDADES.json').read_text(encoding='utf8'))
# Requested CSV is a plain machine-readable scientific table, not a workbook.
csvpath=CORE/'MATRIZ_CAPACIDADES.csv'
with csvpath.open('w',encoding='utf-8-sig',newline='')as f:
 fields=('id','CPC_origin','mechanism','domain','controls','limits','current_recovery_status','current_status_explanation','source_bytes_recovered','source_count','source_hashes_json','recovery_proof','integrated_in_CPC9_E1')
 w=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore');w.writeheader()
 for row in matrix['rows']:
  value={**row,'source_hashes_json':json.dumps([{'source_member':s.get('member'),'sha256':s.get('member_sha256'),'recovered_path':s.get('recovered_core_path')}for s in row.get('historical_source_identities',[])],ensure_ascii=False,separators=(',',':'))}
  if isinstance(value.get('recovery_proof'),list):value['recovery_proof']=json.dumps(value['recovery_proof'],ensure_ascii=False,separators=(',',':'))
  w.writerow(value)
md=['# Matriz de capacidades recuperadas','','Las clasificaciones son filas de procedencia, no conceptos ni réplicas. La prueba limpia determina la sustitución operativa. Ninguna fila se integra automáticamente en E1 de CPC9.','','| ID | Estado | Dominio y alcance actual |','|---|---|---|']
for r in matrix['rows']:md.append('| '+r['id']+' | '+r['current_recovery_status']+' | '+r['current_status_explanation'].replace('|','/')+' |')
(CORE/'MATRIZ_CAPACIDADES.md').write_text('\n'.join(md)+'\n',encoding='utf8')
compression=['# Compresión y pérdida de información','',f"Los ZIP CPC3–CPC7 examinados suman {historical_compressed:,} bytes comprimidos y {historical_expanded:,} bytes expandidos. CPC1/2 están dentro de la genealogía CPC3.",f"Se conservan {len(rows):,} nombres lógicos en {len(unique):,} blobs únicos. Los bytes seleccionados suman {logical:,}; tras deduplicar, {sum(unique.values()):,}. El almacén gzip ocupa {corpus['store_gzip_bytes']:,} bytes.",'','## Conservado','','Código y variantes ejecutadas, configuraciones y parámetros, identidad del instrumento, catálogo NSM de origen, telemetría terminal original con controles/errores/reservas, fuentes de las47filas históricas, pruebas actuales y once semillas/checkpoints MBP4 indispensables. Los miembros se recuperan por sus nombres y hashes exactos. No hay ZIP antiguos completos anidados.','','## Excluido','','Entornos, toolchains, vídeos, gráficos repetidos, logs repetidos, mayor parte de snapshots densos y temporales. En CPC3–CPC7 los snapshots `.deetsnap` no seleccionados representan '+f"{corpus['raw_snapshot_exclusion_CPC3_to7_bytes']:,} bytes."+' Las variantes únicas de código ejecutado sí se conservan por hash.','','## Consecuencias','','La reproducción ejecuta las trayectorias de los contratos seleccionados y vuelve a generar estados/observaciones. El estado físico y los campos primarios se comparan con referencias inmutables. No se afirma regeneración byte-exacta de todos los contenedores: versiones, rutas, identificadores documentales y nombres de intentos pueden diferir sin cambiar RAW/clocks.','','Los snapshots históricos no seleccionados de dominios no reproducidos NO se declaran recuperables. Su trayectoria fina no puede revisarse desde este Core sin el archivo original. Su código y evidencia terminal permanecen. La matriz deja esas capacidades pendientes y no las llama sustituidas operativamente. No se autoriza borrar los originales.','','El tamaño del ZIP final, su tamaño expandido real y el hash exacto se informan fuera del ZIP. Los bytes lógicos materializados del almacén no deben confundirse con el tamaño expandido del contenedor.']
compression=[s.replace('once semillas/checkpoints MBP4 indispensables','once semillas/checkpoints MBP4, ocho padres diagnósticos CPC6 y un padre L15 indispensables')for s in compression]
compression+=['',f"Las copias archivadas CPC3–CPC8 (incluidas las dos campañas CPC8) suman {corpus['all_historical_archive_copies_compressed_bytes']:,} bytes comprimidos y {corpus['all_historical_archive_copies_expanded_bytes']:,} bytes expandidos. No es un recuento de información única.",f"El índice final conserva {len(checkpoint_members)} nombres de snapshots/checkpoints esenciales. Las exclusiones volumétricas iniciales no incluyen las excepciones comprimidas añadidas después; COMPRESION.json enumera cada excepción.",'','## Correcciones conservadas','','Los informes iniciales de auditoría que no coincidían se conservan. En orden, la antigua bandera de metadata de sesión falsa se separa de los RAW/clocks y ahora se exige restauración efectiva. En bucle/comparación CPC3, los campos pasivos añadidos posteriormente no se inventan en la referencia antigua. En flujo CPC5 se recuperó la fuente ejecutada original por SHA en lugar de comparar una versión posterior. Ninguna corrección cambia el motor, la experiencia, la política, el decoder ni convierte un caso funcional negativo en positivo.']
(CORE/'INFORME_COMPRESION_Y_PERDIDA_DE_INFORMACION.md').write_text('\n'.join(compression)+'\n',encoding='utf8')
put(CORE/'organizaciones/CONTRATOS.json',{'scientific_factories':['RepertoireSession.create(count<=65)','IntegratedSession.create(untrained)','MagnitudeCTSSession.create','CoupledMagnitudeCTSSession.create','BranchCountSignSession.create'],'locators':'documentacion/INDICE_MIEMBROS.json and recovered cpc8/src or installed official4.5','architecture_identity':'N,physicalresourcesandhistoryperindividualarefixed; independentworldsnevermerged','untested_historical_sources':'Preservedinertly,notautomaticwhitelistedoperativecapabilities'})
put(CORE/'observadores/CONTRATOS.json',{'passive':'ExactRAW,clock,fieldsandfullphysicaldigests; candidateviewsarecheckedwithoutphysicaladvance','material_probes':'Queriesarephysicaleventsandcanmodifyhistory; firstandlaterqueriesretained','auditor':'Expectedresults/primariesreadonlyaftereachtrajectory, notpassedtoparticipantpolicy','exact_integer_contract':'Pythonintegers/uint64arrays/decimalstrings; neverfloatRAW/clocks'})
put(CORE/'controles/CONTRATOS.json',{'executed_panels':'Frozeninputs in configuraciones/RECUPERACION_CONGELADA.json; separateparticipant/host/auditor scopes in eachsource','controls':['omittedexperience','oppositehistory','unpairedexperience','same-doseoffpath','route/messagecut','sham','historicalreserve','continuationwithoutreteaching'],'negative_results':'UnpairedK65laterlearning,offpath63/64retentionandcountrepresentationlimitsremainobservable','no_classical_benchmarks_executed':True})
for p in CORE.rglob('*.py'):ast.parse(p.read_text(encoding='utf8'),filename=str(p))
put(CORE/'verificaciones/VALIDACION_SINTAXIS.json',{'status':'PASS','files':len(list(CORE.rglob('*.py'))),'scope':'SyntaxofpublicCoretools/examplesonly; scientificvaliditycomesfromnativerecovery,notthischeck'})
print(json.dumps({'payload_ready':True,'matrix_counts':matrix['counts'],'files_before_manifest':len([p for p in CORE.rglob('*')if p.is_file()]),'store_bytes':corpus['store_gzip_bytes']}))
