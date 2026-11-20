"""Documentary synthesis. Reads completed observations; never drives a participant.

Interpretations below are authored, bounded claims, not inferred intelligence labels.
Run only after the scientific fronts have closed; manifests are built separately.
"""
import hashlib,json,shutil,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from verificar_datos import recalculate

def read(p):return json.loads((ROOT/p).read_text(encoding='utf-8'))
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
def ref(p,locator=None):
 path=ROOT/p
 r={'path':p,'sha256':sha(path),'bytes':path.stat().st_size}
 if locator:r['locator']=locator
 return r
def put(p,v):
 dest=ROOT/p;dest.parent.mkdir(parents=True,exist_ok=True)
 dest.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def md(p,s):
 dest=ROOT/p;dest.parent.mkdir(parents=True,exist_ok=True)
 dest.write_text(s.strip()+'\n',encoding='utf-8')

def main():
 for n in ('MAPA_CPC1_A_7.json','MATRIZ_CAPACIDADES_ACUMULADAS.json','INVENTARIO_FUENTES.json','PENDIENTES_RECUPERADOS.json'):
  shutil.copyfile(ROOT/'genealogia'/n,ROOT/'revision'/n)
 calc=recalculate();put('revision/CALCULOS.json',calc)
 if calc['errors']:raise RuntimeError(calc['errors'])
 mainp='resultados/semantica/SOC_I21_SOCIAL_THEN_L01_REVISION/MEASUREMENTS.json'
 social='resultados/semantica/RELACIONES_Y_COMUNICACION_RESUMEN.json'
 integration='resultados/integracion/ANALYSIS_INCREMENTAL.json'
 longitudinal='resultados/integracion/LONGITUDINAL_ANALYSIS.json'
 right='resultados/integracion/RIGHT_ACCESS_ANALYSIS.json'
 contact='resultados/semantica/CNT_P41_CONTACT_READER1/MEASUREMENTS.json'
 refs=[mainp,social,integration,longitudinal,right,contact,
       'resultados/sem01_reproduccion/HISTORICAL_PARITY.json',
       'resultados/genealogia_cp01_cp02_r1/SUMMARY.json',
       'comparadores/SUMMARY.json','revision/MATRIZ_REGRESION_ACUMULATIVA.json',
       'revision/NSM65_EVIDENCIAS.json','revision/REGULACION_ADQUIRIDA.json']
 allmeasure=[]
 for p in sorted((ROOT/'resultados').rglob('MEASUREMENTS.json')):
  try:r=json.loads(p.read_text(encoding='utf-8'))
  except Exception as e:allmeasure.append({'path':p.relative_to(ROOT).as_posix(),'parse_error':str(e)});continue
  allmeasure.append(dict(ref(p.relative_to(ROOT).as_posix()),schema=r.get('schema'),case_id=r.get('case_id',r.get('case',{}).get('id') if isinstance(r.get('case'),dict) else None),final_tick=r.get('final_tick',r.get('physical',{}).get('tick')),role='PRIMARY; not automatically an independent preparation'))
 put('revision/INDICE_EVIDENCIA.json',{'schema':'CPC8.evidence.index.v1','layers':['DATOS','CALCULOS','INTERPRETACION_PROVISIONAL'],
   'entry_points':[ref(p) for p in refs], 'all_measurements':allmeasure,
   'localizers':'JSON /field/index; JSONL one-based line; snapshot path+hash. Source bundles in each case preserve executable identity.',
   'all_outcomes':'All discovery attempts, technical failures, rejected receipts, diagnostic forks and reserves remain in resultados/ and jobs/. Index is not a positive-result filter.',
   'independence':'Different snapshots/ticks/readings do not imply independent worlds. Use each front reconciled index for preparations, continuations, forks and technical reproductions.',
   'recalculate':'python ejecutar.py verificar-datos; tools/analyse_regulation.py; src/relaciones/analyze_semantics.py; comparadores/ and tools/matriz_regresion_acumulativa.py',
   'gaps':'Local encounter neighborhoods plus full frontier states; unobserved travel segments have no asserted unique genealogy.'})
 architectures=[
  {'id':'SHARED','state':'EXECUTED','N':131,'kind':'K65 and U0 coexisting, distinct memory interfaces','result':'65/65 direct correspondences; U0 own communication uses additional prepared banks. Coexistence is not common selective access. Unpaired RIGHT can bypass via free event.'},
  {'id':'ALIAS','state':'EXECUTED','N':131,'kind':'Actual L17 support coincides with U0 LEFT','result':'Native question accesses the acquired support; 61/65 direct interfaces later covered. Neighbor interference and consumed/transformed L17 access.'},
  {'id':'RL','state':'EXECUTED_SELECTED','N':131,'kind':'Only L17 relocated at T0; other64 keep separated geometry','result':'63/65 direct; native L17 function transformed into action and retained sign. Selected on access/causality, not final load.'},
  {'id':'SOC_I21','state':'EXECUTED_MAIN','N':131,'kind':'RL plus fresh mobile social learner B in same Runtime','actual_interfaces':259,'initial_material_sites':15,'result':'E1 native information changes another region and teaches B; B repeatedly uses content with supplied context. This is not two fully validated autonomous compounds.'},
  {'id':'TEMPORAL_F3','state':'EXECUTED_SEPARATE','N':67,'kind':'Two sensory roles, physical ordering, later sign and route guards','result':'Two order-dependent emissions and retained local sign; not all participant binding or unrestricted temporal language.'},
  {'id':'CONTACT_F3_ACCESS1','state':'EXECUTED_SEPARATE','N':67,'kind':'Actor/medium encounter; identical cues, acquired directional difference, native maintenance','result':'Contact vs same-inventory offpath consequence, retained after auxiliary relation. Not part of E1 main.'},
  {'id':'TWO_THREE_FOUR_FULL_COMPOUNDS','state':'NOT_EXECUTED_IN_CPC8','reason':'No demonstrated common geometry/access preserving all essential functions within bounded exploration; previous network and serial tests preserved and covered by product regression, not relabeled as new integrated lives.'}]
 put('revision/ARQUITECTURAS_CPC8.json',{'schema':'CPC8.architectures.v1','selection_criteria':['acquired use through actual shared support','retention under added experiences','causal controls','native communication','access cost and interference'],
  'basic_buffer_formula':'32*N**3 bytes, excludes scratch/snapshots/host','N131_basic_bytes':32*131**3,'N67_basic_bytes':32*67**3,
  'families_limit':'Three physical integration families. Protocol revisions identified separately and do not silently replace their antecedents.',
  'architectures':architectures,'evidence':[ref(integration),ref(social)]})
 timeline=[
  [0,'E1 fresh physical preparation;32 corresponding experiences including L17. No trained snapshot imported.'],
  [5,'Physical order projection, not a human semantic label.'],
  [11,'Current observation reaches prepared comparison routes.'],
  [19,'Discrepancy-dependent native question; opportunity and comparison architecture prepared.'],
  [134,'Question has physically reached actual acquired L17; earlier lower queries measured.'],
  [136,'Native action reaches social path; all candidates received equal declared action opportunity.'],
  [140,'B cue meets incoming E1 product, establishing new B correspondence.'],
  [157,'First B cue-only response; no host copy of E1 answer.'],
  [161,'Contextual material interaction changes direction.'],
  [166,'Delivery with combined native content/context.'],
  [262,'Additional33 lower experiences, not copies of trained memories.'],
  [288,'Renewed B reader returns earlier acquired content.'],
  [297,'Second functional delivery, context differs; context component has residual history.'],
  [396,'63/65 original direct relations covered after additional acquisition.'],
  [524,'Explicit pedagogical revision of L01, with second teacher and declared fixed guards.'],
  [658,'Revised L01 and62 other directly available relations; original L15/L17 direct interfaces not covered.'],
  [690,'Third B use after revision and new lower acquisitions.'],
  [786,'Continuation: new RIGHT paired experience admitted; new order inputs rejected occupied, not silently cleared.'],
  [1051,'All63 previously accessible old relations still functional.'],
  [1182,'Exploratory explicit reader accesses newly acquired RIGHT; unpaired/no-cue controls yield only probe.']]
 put('revision/VIDA_PRINCIPAL.json',{'schema':'CPC8.main.life.v1','identity':'SOC_I21_SOCIAL_THEN_L01_REVISION','new_at_T0':True,'N_constant':131,
  'central_horizon':690,'continuation_horizon':1182,'timeline':[{'tick':t,'event':s} for t,s in timeline],
  'continuity':'SOC_I21_SOCIAL_THEN_L01_REVISION/T690 -> LIF_P11_NEW_AB/T1051 -> USE_P11_RIGHT_PAIRED/T1182. Other controls/forks are not concatenated into MAIN.',
  'not_integrated':['CP02 external-gate prediction','all65 NSM meanings','temporal and contact semantic apparatuses','general autonomous choice of source','consequence-optimized regulatory strategy'],
  'forbidden_edits_on_MAIN':[],'evidence':[ref(mainp),ref(longitudinal),ref(right)],
  'events':'configuraciones/demo/vida_integrada.json','matched_control_events':'configuraciones/demo/vida_control.json'})
 put('revision/APRENDIZAJE_ACUMULATIVO.json',{'schema':'CPC8.cumulative.learning.v1','scales_not_pooled':['individual E1','mobile learner B','separate temporal individual','separate contact individual','historical reference'],
  'E1':{'first_block':32,'additional_block':33,'direct_after_addition':{'covered':63,'requested':65},'selective_revision':'L01 changes with M1 protocol, others in available set preserved',
        'later_right':'Acquired786, old63/63 retained1051, newRIGHT explicit query1182 after old panel; not autonomous new query.'},
  'B':'Acquires from physical E1 emission140; uses157/166,288/297,681/690 without local answer-map injection.',
  'semantic_apparatuses':'Order and contact signs introduced after physical relation expression; retained after another acquired relation. Separate new worlds, not E1 meanings.',
  'evidence':[ref(mainp),ref(right),ref(contact),ref('revision/NSM65_EVIDENCIAS.json')]})
 put('revision/RETENCION_Y_PLASTICIDAD.json',{'schema':'CPC8.retention.v1',
  'E1_direct_original_denominator':65,'E1_available_after_integration':63,'old_available_retained1051':{'numerator':63,'denominator':63},
  'original_uncovered':['L15 interference/access','L17 original query reorganized/consumed; acquired function expressed through native U0 action/derived interface'],
  'cannot_add':'Derived L17 is not an extra66th concept. NewRIGHT is a distinct acquired correspondence, not a catalog meaning.',
  'revision_M1':'External pedagogical cue/event/second teacher; no reset. Ordinary-only and offpath same-dose can yield occupied, distinguished from wrong value.',
  'evaluation_interference':'Comparator late L01 query succeeds if previous probe omitted in auditor branch; missing later access is not a proof of physical erasure.',
  'benchmark':calc['comparison'],'evidence':[ref(integration),ref(longitudinal),ref(right),ref('comparadores/SUMMARY.json')],
  'formulas':calc['formulas'],'passive_difference_vs_function':'RAW distinction alone does not count as accessible knowledge; only emitted/useful response at fixed query is scored.'})
 put('revision/COMUNICACION_Y_APRENDIZAJE_SOCIAL.json',{'schema':'CPC8.social.v1',
  'positive':'Acquired L17 -> native question -> own acquired response -> action transport -> B cue encounter -> new B cue-only reading -> context interaction -> delivery, all within one Runtime.',
  'source':'E1 newly learned L17','receiver':'Fresh B mobile correspondence apparatus, not a separately validated complete mind',
  'first':[140,157,161,166],'renewed':[288,292,297],'later':[681,685,690],
  'context_precision':'Second renewed response retains prior context, then new context changes component to0; do not misdescribe it as simply decoding a new independent context label.',
  'controls':['source unpaired same-dose','B cue unpaired','physical message cut138','same physical sham','opposite content/context reserve','restore396 and new query in another process'],
  'evidence':[ref(mainp),ref(social)],'scope':'Causal acquisition/communication/use of directional relation. Not NSM DECIR E5, free dialogue, bilateral learned convention or65 meanings communicated.'})
 put('revision/CONSULTAS_Y_ACCESO.json',{'schema':'CPC8.access.v1','prepared':'Ports, geometry, general supply, opportunities and comparator are T0 resources.',
  'endogenous':'Question19 arises from physical comparison state under paired history; travels to actual L17.',
  'history_dependent':'Different histories/content alter accessible information and effect. General policy of when/whom to ask has not been learned from utility.',
  'explicit_instrumental':['Direct K65 form probes','Later RIGHT reader1179','Social B query windows and context supply'],
  'classes_separated':{'discrepancy':'positive bounded mechanism','insufficiency':'not integrated as general distinct detector','access_failure':'positive later occupied ports and failed reader','legitimate_absence':'separate official profile regression','exhausted_source':'no learned stopping-policy demonstration'},
  'costs':'Queries introduce material, may occupy/transform access or teach via residuals; observer-only reads do not imply learning.',
  'evidence':[ref(mainp),ref(longitudinal),ref(right),ref('revision/MATRIZ_REGRESION_ACUMULATIVA.json')]})
 put('revision/COMPOSICION_FUNCIONAL.json',{'schema':'CPC8.composition.v1','levels':[
  {'kind':'transport together','evidence':'Native emitted carrier actually traverses E1 to B; no callback copy.'},
  {'kind':'physical integration','evidence':'Content acquired in L17 and available action supply jointly affect B learning.'},
  {'kind':'functional composition','evidence':'B acquired content and context resource combine in direction and delivery; swapped context/content tested in reserves.'},
  {'kind':'semantic composition','state':'PARTIAL_OR_NOT_DEMONSTRATED','reason':'Fixed sensory roles and prepared vector operation do not prove unrestricted participant binding or productive grammar.'}],
  'order':'Temporal AB/BA distinguished by native direction, not just scalar sum; later unused cues can create extra associations. Guarded third preparation avoids this in tested window.',
  'E1_context':'Content/context operation is prepared; content depends on learned history. Do not count prepared operation as independently learned grammar.',
  'evidence':[ref(social),ref('revision/NSM65_EVIDENCIAS.json')]})
 atlas=read('revision/RELACIONES_NATIVAS_ADICIONALES_REGULACION.json')
 put('revision/RELACIONES_NATIVAS_ADICIONALES.json',{'schema':'CPC8.native.atlas.v1','regulation_front':atlas,'other_relations':[
  {'id':'NATIVE_ACCESS_REORGANIZATION','observation':'L17 direct query can disappear while its function becomes a different derived action/sign interface; equal charge is not equal function.','evidence':ref(integration)},
  {'id':'NATIVE_EVALUATION_TEACHING','observation':'A later reader or unused cue meets residual products and forms a new association, distinguishing retention from evaluation-induced learning.','evidence':ref(social)},
  {'id':'NATIVE_DIRECTIONAL_CONTACT','observation':'Same-load medium has distinct native direction after actor encounter vs same-material offpath actor; retained/read after later acquisition.','evidence':ref(contact)},
  {'id':'NATIVE_ADMISSION_VS_PHYSICS','observation':'At786 order port RAW not empty and submission rejects despite inspected kernel write gate not protected. Admission contract is not a proof of impossibility of a native encounter.','evidence':ref(longitudinal)}],
  'novelty':'New measured functional use/diagnostic in this campaign, not a new physical law or proof that the underlying v27 branch was previously unknown.'})
 controls=[]
 for p in sorted((ROOT/'configuraciones').rglob('*.json')):
  controls.append(ref(p.relative_to(ROOT).as_posix()))
 put('revision/CONTROLES_Y_RESERVAS.json',{'schema':'CPC8.controls.v1','frozen_configurations':controls,
  'coverage':['opposite history','cue omitted/unpaired','message cut vs sham','context/content swapped','timing/dose/actor reserves','selective memory/reader diagnostics','save/load and receipt equality'],
  'reserve_distinction':'A new complete training history at reserved parameters confirms robustness of acquisition protocol. It is not automatically transfer of an already trained semantic concept to a new realization without teaching.',
  'late_RIGHT':'Fixed exploratory cadence before three continuations, not retrospectively claimed confirmatory reserve.',
  'attempts':'All three integration and temporal/contact families, revisions and wrong early interpretations preserved; corrected cases have new IDs and source bundles.',
  'global_lesions':'No general meaning localized from an intervention that disables all perception/action; actuator diagnostic rescue is labeled assisted and never returned to MAIN.',
  'evidence':[ref(integration),ref(social),ref(longitudinal),ref(right)]})
 put('revision/COMPARACION_METODOS.json',{'schema':'CPC8.method.comparison.v1','primary_summary':read('comparadores/SUMMARY.json'),
  'recalculated_counts':calc['comparison'],'scope':'Opaque formID/direction continual association, not semantic comprehension or native dynamical equivalence.',
  'provisional_reading':'On this finite association task B1 and B2 achieve502/502, DEE500/502 with2uncovered late accesses and0wrong covered values. This does not show a DEE accuracy/resource advantage here.',
  'budgets':'Common ceilings1GiB and600s per job, not identical consumed compute. B2 counts replay and private independent model RNG. Query materiality and instrumentation differ.',
  'no_claim':'No executed Titans/MIRAS comparison, no energy measurement, no universal superiority.',
  'evidence':[ref('comparadores/SUMMARY.json'),ref('comparadores/INFORME.md')]})
 cps=[]
 for p in sorted((ROOT/'resultados').rglob('*.deetsnap.gz')):
  cps.append(ref(p.relative_to(ROOT).as_posix()))
 put('checkpoints/INDICE.json',{'schema':'CPC8.checkpoints.v1','storage':'Single copies beside their corresponding primary experiment; this file points to them, does not duplicate dense states.',
  'count_not_replicates':len(cps),'files':cps,'format':'Official native snapshot inside gzip, SHA of actual compressed member; per-case storage proofs include decompressed/native identities where required.'})
 put('PROVENANCE.json',{'campaign':'CPC8','author':'Ivan Erick Tlaltecatl Morales','instrument':'DEE thinking4.5.0','kernel':'DEE Universe v27 frozen',
  'official_identity':read('runtime/REFERENCE_IDENTITY.json'),'installed_identity':read('runtime/INSTALL_IDENTITY.json'),
  'budget':read('BUDGET.json'),'historical_source_inventory':ref('revision/INVENTARIO_FUENTES.json'),
  'preservation':'Original source archives/products/documents read only; selected copies in genealogia/. No new wheel or kernel build.',
  'two_scales':'47-capability recovered base is not the repertoire of E1. Historical evidence remains at original member+hash; full old archives not nested.',
  'conversations':'Only accessible threads/turns identified in ANALISIS_TRANSVERSAL were read. Truncated items/older unread pages and merely mentioned conversations are not claimed inspected.',
  'decisions':'Host prepares world and experiences, declares current sensors, exposes fixed operations. Native dynamics emits/changes state; auditor reads results only after evolution. No LLM or hidden answer-map participant.',
  'private':True,'scientific_claim_status':'Provisional bounded interpretation; technical integrity is separate from functional scientific evidence.'})
 md('revision/LIMITACIONES_Y_PENDIENTES.md',LIMITATIONS)
 md('revision/LECTURA_PROVISIONAL.md',READING)
 md('LECTURA_PROVISIONAL.md',READING)
 md('LEER_PRIMERO.md',FIRST)
 md('revision/LEER_PRIMERO.md',FIRST.replace('revision/LECTURA_PROVISIONAL.md','LECTURA_PROVISIONAL.md'))
 print(json.dumps({'summaries_written':True,'primary_measurement_files':len(allmeasure),'checkpoints':len(cps),'recalculation_errors':calc['errors']}))

FIRST='''
# CPC8: resultados para revisión privada

E1 adquirió una relación en un soporte compartido, la utilizó mediante una pregunta física condicionada por comparación y su emisión enseñó una correspondencia a B. En la misma vida incorporó otras33 relaciones, revisó una mediante un protocolo pedagógico explícito y B volvió a utilizar el contenido anterior. La continuación conserva63 de las65 interfaces directas originales y permite una nueva relación RIGHT con lectura instrumental.

No son65 significados NSM ni un sistema de conversación libre. La base recuperada contiene47 capacidades históricas; su amplitud no se atribuye automáticamente a E1. Los ensayos semánticos de orden y contacto son individuos separados y sus reservas comprueban protocolos de adquisición, no transferencia semántica universal.

Empiece por [lectura provisional](LECTURA_PROVISIONAL.md), luego `revision/VIDA_PRINCIPAL.json`, `revision/NSM65_EVIDENCIAS.json` y `revision/INDICE_EVIDENCIA.json` dentro del expediente extraído. Los datos adversos, recepciones rechazadas, controles y fuentes ejecutadas están incluidos.

Windows x64/CPython3.13: `.\\iniciar_cpc8.ps1 -Modo eventos -Archivo configuraciones/demo/vida_integrada.json`. También modo interactivo. No requiere rutas privadas ni acceso a Internet; usa el WHL oficial incluido. El control comparable es `vida_control.json`.

`python ejecutar.py verificar-datos` recalcula métricas sin importar el motor. `python ejecutar.py referencias --salida NUEVA` y `regresion --salida NUEVA` ejecutan referencias y pruebas oficiales. Véase LEEME.md para entorno y comandos.

El comprobante `VERIFICACION_FINAL_EXTERNA.json`, entregado junto al ZIP y no dentro de él, identifica los bytes exactos probados, la instalación limpia y los resultados. Integridad y reproducción son verificaciones diferentes. Paquete privado reconstructivo: no diseñado como exportación segura para terceros.
'''
READING='''
# Lectura provisional CPC8

## Capacidad integrada observada

Una memoria adquirida por experiencias después deT0 modifica una pregunta/acción de E1 y, mediante transporte v27, enseña una correspondencia nueva a un receptor B. El receptor vuelve a responder y participa en una consecuencia material. En `SOC_I21`, la cadena es pregunta19 → lectura de L17 en134 → acción136 → encuentro pedagógico140 → respuesta157 → interacción contextual161 → entrega166. Nuevas experiencias262 no eliminan el uso B288/297; la revisión dirigida de L01 en524 tampoco impide B681/685/690. La fuente, la memoria, la respuesta y el receptor coexisten en un Runtime N131: no existe callback que copie una respuesta entre mundos.

La geometría y las oportunidades estaban preparadas. La correspondencia útil depende de historia emparejada: señal/evento desacoplados y mensaje cortado eliminan la respuesta pertinente; el sham y reservas de contenido/contexto la conservan. Las trazas locales y fronteras completas sostienen los encuentros declarados, sin inventar genealogía para segmentos no observados.

## Conservación y adquisición adicional

La integración no conserva todas las interfaces originales. El cribado compartido mantiene65/65, pero no demuestra acceso común a ellas. La coincidencia directa L17/U0 permite uso nativo y reduce a61/65 el panel directo. La tercera familia mueve únicamente el soporte L17 desdeT0 y conserva63/65. L15 sufre interferencia; L17 reorganiza su acceso y función en vez de permanecer como el mismo puerto consultable. Ese resultado no equivale a borrar dos conceptos ni a65 relaciones semánticas.

En la continuación exacta de `SOC_I21/T690`, se adquiere RIGHT786. Después se consultan correctamente las63 relaciones antiguas disponibles1051 y RIGHT responde1182 con carga25 y dirección(-1,-1,0). Controles sin señal y con señal desfasada de igual dosis sólo contienen el lector9, sin valor aprendido. El acceso RIGHT es explícito, instrumental y exploratorio: no se recuperó una nueva pregunta autónoma. Los nuevos acontecimientos de orden786–788 fueron rechazados por ocupación; ese fallo queda conservado, no reparado externamente.

La actualización L01 utiliza señal, acontecimiento, segundo docente y rutas/guardas declaradas. Modifica la relación elegida manteniendo disponibles las otras62 del panel. No demuestra una decisión autónoma de qué revisar ni una política general aprendida de regulación.

## Significados y composición

Se investigaron dos clases distintas en aparatos separados: orden entre dos papeles sensoriales y consecuencia de contacto actor/medio. En ambas, la evolución física precede a la asociación del signo, la señal sola produce una respuesta y ésta se conserva después de otra adquisición. Las historias opuestas, la señal omitida/desacoplada y los shams distinguen el efecto adquirido de un simple nombre en pantalla.

Las fichas65 individuales distinguen E1/E2 positivos locales de E3 parcial. Reservas con nuevos estados, tiempos o actores comprueban el protocolo completo de adquisición en mundos nuevos; no sustituyen una prueba intraindividuo de generalización de un concepto ya aprendido a cualquier referente. No se acredita automáticamente DESPUÉS por invertir ANTES, ni HACER/YO por mover un actor, ni DECIR E5 por transportar un mensaje. La comunicación de una correspondencia direccional tiene pruebas propias, pero no convierte esa correspondencia en una primitiva lingüística general.

La dirección conserva información que una carga escalar pierde. E1/B combinan contenido adquirido y contexto en una operación física preparada; los contrastes cambian componente y consecuencia. Esto sostiene composición funcional en un dominio finito, no gramática productiva ni conservación general de todos los participantes y papeles.

## Regulación y hallazgos causales

El frente regulador independiente enlaza contacto actual → portador nativo → comparación → estado de política → intercepción → conservación de una entrega3. Omitir el actor o cortar el retorno modifica esa función y el rescate del actuador conserva la capacidad general. Las rutas, el normalizador y la regla finita de conservar/cambiar estaban preparados. Se demuestra regulación dependiente de un estado adquirido. El nivelC queda parcial: no se acreditó una regla o estrategia optimizada por utilidad. Este frente no está integrado en E1.

Un fallo reveló un encuentro prematuro entre dos portadores de carga cero: no eran ausencia física. El encuentro cancelaba una componente direccional y alteraba el retorno. Se guardaron vecindarios completos antes/después y se reconstruyeron contribuciones dirigidas. Es una nueva explicación funcional del montaje, no una ley nueva del kernel.

Otros contraejemplos importan: señales no emparejadas pueden resolver por una ruta balística; una consulta tardía puede formar una asociación nueva con residuos; un soporte puede conservarse pero no admitir otro lector; el mismo total escalar puede tener función diferente según dirección. Los intentos iniciales y correcciones siguen incluidos.

## Base acumulativa y comparación externa

Se localizan47 capacidades históricas con fuentes y estados distintos. La regresión del producto oficial completa82/82 pruebas. CP01/CP02 se ejecutaron con fuentes seleccionadas originales; CP02 conserva su barrera externa declarada, no se atribuye como una barrera nativa ni como predicción integrada en E1. SEM01 reproduce hashes físicos iniciales y finales de su referencia. CORE17 aporta una reproducción local parcial de reparación, sin inventar clocks históricos faltantes. El overlay de regresión enlaza cada afirmación operativa con pruebas y dependencias.

En el contrato externo limitado a asociaciones opacas actualizables, DEE logra500/502 respuestas correctas,0 direcciones erróneas y2 accesos no cubiertos; memoria convencional B1 y una red pequeña con replay B2 logran502/502. En estos ensayos DEE no muestra ventaja de calidad ni de coste del ordenador. La sonda material, la instrumentación y las representaciones difieren y se contabilizan; no se equiparan ticks a segundos ni carga a energía. Las dos semillas son historias independientes, los cientos de consultas no son cientos de réplicas.

## Alcance reproducible

El motor4.5/v27 oficial permanece intacto. El participante no consulta mapas de enseñanza, targets ni logs como memoria. La interfaz sólo transmite operaciones estructuradas; ENTE, INSTRUMENTO e INTERPRETACIÓN tienen procedencias separadas. La prueba de aislamiento restaura el mismo estado y elimina únicamente listas documentales en una rama diagnóstica: la evolución y la consulta siguen físicamente iguales. La reproducción final independiente y la integridad del contenedor se documentan por separado fuera del ZIP exacto.

Estos datos sostienen aprendizaje acumulativo y comunicación física con límites de acceso identificados. No sostienen65 primitivas funcionales, selección general autónoma de información ni estabilidad ilimitada. Los resultados parciales positivos quedan conservados como funciones concretas reutilizables, no rebajados a una captura de pantalla ni extrapolados a una mente universal.
'''
LIMITATIONS='''
# Límites y pendientes conservados

- E1 no ofrece acceso selectivo endógeno a todo el repertorio65. Las consultas directas reciben un puerto explícito. Se integró causalmente L17 con comparación/acción/aprendizaje social; los otros soportes permanecen disponibles mediante interfaces declaradas.
-63/65 del panel original siguen cubiertos: L15 interferido y L17 con acceso reorganizado. No se silencian esos dos casos ni se cambia el denominador a63 para afirmar65/65.
- La continuación1182 incorpora una relación nueva, pero el nuevo orden no fue admitido por ocupación. Falta un mecanismo nativo reutilizable que renueve esos accesos sin borrar RAW o clocks.
- Las fichas semánticas de orden y contacto son individuos distintos. Sus reservas de adquisición no prueban generalización conceptual intraindividuo sin nueva enseñanza. El resto del catálogo conserva E0/pregunta operacional, no significados ficticios.
- El contexto y las oportunidades de consultar/actuar están preparados. La comparación puede producir una pregunta, pero no se aprendió una política general de cuándo/a quién consultar por utilidad, ni un detector universal de insuficiencia, ausencia y fuente agotada.
- La regulación independiente depende de consecuencias actuales y estados adquiridos; regla, geometría y agenda son preparadas. No se demuestra atención aprendida general ni optimización autónoma sostenida de mantenimiento en E1.
- El aprendizaje social ensaya un receptor móvil y una correspondencia utilizable. No equivale a dos compuestos autónomos completos con65 significados compartidos; cambio de papeles y convención bilateral permanecen parciales.
- La composición funcional direccional no basta para gramática, deíxis YO/TÚ ni conservación general de referentes. Las operaciones preparadas y lo aprendido se registran separadamente.
- Las fuentes históricas completas permanecen fuera del ZIP, con localizadores y hashes. Los comandos ofrecidos como autocontenidos incluyen sus dependencias seleccionadas; no se afirma reproducción completa de cada expediente histórico.
- Sólo se leyeron conversaciones efectivamente accesibles y los turnos/localizadores registrados. Los elementos truncados y páginas antiguas no abiertas no se presentan como leídos.
- Comparadores ejecutados únicamente en contrato de correspondencias finitas; no comparación válida con Titans/MIRAS ni afirmación de ventaja universal, conciencia o equivalencia DEE-realidad.
- Memoria, horizonte, material inicial, mantenimiento y sondas son finitos. Los snapshots y reproducciones técnicas no son nuevas preparaciones independientes. No se infiere estabilidad ilimitada ni imposibilidad universal del kernel de un acceso fallido.

El estado exacto para otra ejecución autorizada, incluyendo código, configuración, checkpoints y presupuesto original consumido, está en REANUDACION.json y checkpoints/INDICE.json. No quedan simulaciones prometidas en segundo plano.
'''

if __name__=='__main__':main()
