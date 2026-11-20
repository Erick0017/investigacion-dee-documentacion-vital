"""R05 documentary selection only. Never imports experiment code or builds ZIP."""
from pathlib import Path, PurePosixPath
import datetime
import hashlib
import json

ROOT = Path(__file__).resolve().parents[1]
OLD = ROOT/'control/EXPEDIENTE_V3_PLAN_FINAL_TENTATIVO_R04.json'
NEW = ROOT/'control/EXPEDIENTE_V3_PLAN_FINAL_TENTATIVO_R05.json'
CONT = ROOT/'control/CONTINUIDAD_PAQUETE_PASIVO_R05.json'
REG = ROOT/'control/FUENTES_CERRADAS_EFECTIVAS_R07.json'
assert not NEW.exists() and not CONT.exists(), 'Fresh documentary outputs required'
def sha(raw): return hashlib.sha256(raw).hexdigest()
def read(rel): return json.loads((ROOT/rel).read_text(encoding='utf-8-sig'))
def write(path, value): path.write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n',encoding='utf-8')
utc = datetime.datetime.now(datetime.timezone.utc).isoformat()
lease = read('control/LEASE_R06_TX/RESULTADO.json')
recovery = read('control/RECUPERACION_LOAD_R06_TX/RESULTADO.json')
e5 = read('analisis/E5_MAIN6_PROGRAMMED18_RECALCULO_R01/E5_CIERRE_REAL_R06.json')
assert lease['status'] == 'CLOSED_LEASE_RENEWAL_COMPLETE' and lease['new_native_ticks'] == 0
assert len(lease['results']) == 6 and lease['accounting_unchanged'] is True
assert recovery['status'] == 'THREE_KNOWN_ZERO_ADMISSION_GUARDS_RECOVERED'
assert recovery['new_native_ticks'] == recovery['Native_requests_submitted'] == 0
assert [r['role'] for r in recovery['results']] == ['LOAD1','LOAD2','LOAD3']
assert recovery['consumed_unchanged'] == 10452 and recovery['reserved_each_unchanged'] == 3740
assert e5['PROGRAMMED']['closed'] is True and e5['PROGRAMMED']['actual_new_opportunities'] == 18
assert e5['CONVENTIONAL_AI']['actual_new_opportunities'] == e5['CONVENTIONAL_AI']['inference_requests_by_campaign'] == 0

report_path = ROOT/'analisis/INFORME_CIERRE8_R07.md'
readme_path = ROOT/'control/LEER_PRIMERO_V3_TENTATIVO_R01.txt'
diagnostic_path = ROOT/'video/P01_DIAGNOSTICO_CAPTURA_R07.md'
before = {str(p.relative_to(ROOT)):sha(p.read_bytes()) for p in (report_path,readme_path,diagnostic_path,REG)}
previous = report_path.read_text(encoding='utf-8-sig')
anchor = '## Antecedente: lectura de las oportunidades 29–30'
assert previous.count(anchor) == 1
history = previous[previous.index(anchor):]
current = '''# DEE–Roblox V3 — Cierre de ocho puntos (R07)

**Corte documental R05: hay cierres parciales y resultados negativos; la campaña continúa.**

MAIN permanece cerrado en N67, T1000571, después de las seis oportunidades
29–34 de ECI02_PI03_REPRO_PI04_PI05_PI07_PI10_RBX01_INTEGRAL_V3_MAIN,
sesión R07_MAIN_adc933c82cc74fb0bb19, padre R06/PAR28 T991187. Acumuló
9384 ticks nuevos y 21 operaciones Native únicas. Eligió ASK/EXIT_1 seis veces
y alternó entre 2 y 3, sin override. Tres contactos usaron luma positiva heredada
y formaron 8 + 3 = 11. No hubo enseñanza nueva, nara, recurso o entrega nueva
en MAIN6. Stock final152; sus acumulados3/3 pertenecen al pasado.
La salida sostenida de P02 no se cumplió:0/3 últimas posiciones fuera de{2,3}.

La lease R06 ya quedó aplicada mediante una transacción administrativa de cero
ticks para los seis roles: MAIN y las tres vidas LOAD cambiaron sólo su testigo
de alcance; CTRL1 y PILOT conservaron sus importaciones0 por archivos, sin crear
un Native propio en esa transacción. Se conservaron N/T/RAW/clocks, política,
contadores, sesión, secuencia, pendientes, fallos e historia. La lease no reparó
la incertidumbre de LOAD. Esa reparación fue una transacción posterior separada,
también de cero ticks, limitada a LOAD1/2/3 y al flag uncertain True→False.

La ventana R06 conserva el inicio original16nov15:07UTC: último episodio nuevo
17nov08:00UTC y cierre máximo09:07UTC. No reinicia contadores ni retroaprueba
operaciones. Mantiene160000ticks, seis vidas y536870912B por propietario, con
criterios, codecs y horizontes iguales. Una renovación administrativa no es una
experiencia ni acredita por sí sola una reapertura material útil de MAIN.

PROGRAMMED terminó18/18 oportunidades y cerró en el ciclo global46. Produjo
ocho enteros correctos para sus opcodes, dos recursos nuevos y una entrega nueva.
En el prefijo común29–34, PROGRAMMED consiguió1recurso/1entrega; Native MAIN6,
0/0. Se conservan ambos denominadores. El programa usa estrategia, asociaciones
y aritmética Python preparadas; la historia física y entrada escalar de Native
no prueban un prior semántico equivalente. Estos datos no establecen un ranking
general de capacidad o eficiencia.

El primer intento de CONVENTIONAL_AI fue rechazado antes de abrir World o
política:3333148672B físicos disponibles frente al mínimo prospectivo3758096384B.
Hubo cero oportunidades y cero inferencias de campaña. No se puntúa como18fallos
del modelo. El daemon R05 cerró normalmente; la infraestructura R06 siguiente
está preparada por archivos, sin resultado ejecutado en este corte. Root reinició
una vez una herramienta NodeJS antigua del anfitrión, no DEE; no se atribuye un
efecto RAM medido a ese reinicio.

La continuación de carga sigue ACTIVA según aviso de Root: LOAD1/2/3 habían
completado2/3 episodios cada una, T994315. Sus fuentes vivas no se seleccionan
como cerradas ni se congelan. La primera etapa negativa y la recuperación
administrativa permanecen completas y separadas de la continuación.

## Estado P01–P08 en el corte R05

| Punto | Resultado comprobado o aviso identificado | Alcance y pendiente |
|---|---|---|
| P01 — Video real | El fallo GDI y CaptureService sigue conservado. La nueva activación CUA de Main retornó éxito; el probe posterior expuso cliente1280×648. DDA_R02 terminó con0bytes por ancho impar1279 rechazado por libx264. | Ese fallo nuevo es del encoder, no NoDeviceSupport. El clip vacío se excluye. DDA_R03 corrige ROI par y clamp, pero no tiene resultado validado incorporado. P01 sigue abierto y sin video final de tres actuaciones. |
| P02 — Oscilación | MAIN6:6/6 transiciones2↔3 y0/3 últimas fuera; selección y ejecución coinciden. PROGRAMMED recorrió su propia referencia cerrada. | MAIN no cumple salida sostenida. El control Native emparejado todavía no tiene cierre incorporado; PROGRAMMED no lo sustituye. |
| P03 — Adaptación | MAIN6 sólo usó luma+ heredada. Aviso preliminar de LOAD episodio2: resultados A2 de LOAD1/2/3=8/4/8; LOAD2 usó luma−,6−2=4. | LOAD1/3 tuvieron NativePartialAdmission en lesson1; LOAD2 registró experience admitted. Es evidencia preliminar de ramas distintas, sin cierre3×3 ni independencia causal perfecta. No se atribuye a MAIN ni se fusionan memorias. |
| P04 — Persistencia | World MAIN cerrado y descriptor PUNTO34_R06 de5831miembros, copias críticas parciales y raíz completa local. Lease/recovery R06 conservaron proyección física y metadatos permitidos a0ticks. | No todos los miembros son copias inmutables. La validación administrativa no demuestra rollback autónomo completo ni uso material posterior de MAIN tras reapertura. |
| P05 — Movimiento y objetivos | MAIN alcanzó sus seis destinos sin override y calculó tres productos correctos, con0recursos/0entregas nuevos. PROGRAMMED:2/1 en18;1/1 en el prefijo común6. | El cuerpo y puertos son preparados. Aritmética correcta, navegación útil y objetivos de misión son medidas distintas; sin ranking entre ayudas/historias no equivalentes. |
| P06 — Eficiencia | Benchmark cerrado BASE/PROTO/BASE, cero ticks, testigos iguales y reducción19,4693% frente a la base más rápida. | No alcanzó el20% prospectivo y no se instaló caché. Es instrumentación externa, no aprendizaje, energía o aceleración cognitiva. El negativo R01 permanece completo. |
| P07 — Tres agentes | Etapa inicial cerrada: tres Q1 reales de356ticks, T991543,0episodios completos; solapamiento común280,405s de llamadas de pared. Recuperación posterior0ticks aplicada. Aviso Root: continuación2/3 episodios por vida,T994315,activa. | No se declara cerrado el objetivo3×3. El solapamiento incluye host/checkpoint y no acredita instrucciones CPU simultáneas. Las fuentes de continuación no integran la selección cerrada. |
| P08 — Prototipo y piloto | Conector XML real, kit, mapa y controladores preparados; editor piloto propio cerrado con SHA de escena igual. | No hubo Native en ese editor. Falta episodio real en otro mapa y validación externa; no se contactó a desarrolladores. |

## E5: dos rechazos de puerta con causas conservadas

`analisis/E5_MAIN6_PROGRAMMED18_RECALCULO_R01/E5_CIERRE_REAL_R06.json` y
`EXPLICACION_DOS_RECHAZOS_PROGRAMMED_R01.json` separan los hechos de la
interpretación. En36, PROGRAMMED llegó sin llave ni código después de la entrega34:
faltaron prerrequisitos; los campos Lua nil ausentes no significan cero material.
En41 llevaba la tupla9/2/1 obtenida en38 y el productoB10, formado correctamente
según los opcodes anteriores. El entorno cambió los signos y esperaba8 sobre esa
misma tupla retenida: falló el objetivo vigente, no la aritmética ni la historia.
El programa recibió los signos nuevos en Archive43, formó9−2=7 en44 y7+1=8 en45,
y el contacto46 aceptó8 y recogió el segundo recurso. Una entrega posterior de
ese recurso no se ejecutó ni se puntúa dentro del horizonte18. La tupla7/3/2
configurada desde41 no fue adquirida, así que no se afirma transferencia a ella.
Los expectedCode privados se leyeron para este análisis; no fueron entrada de
selección de acciones. La actualización del diccionario de PROGRAMMED es Python,
no adquisición física DEE.

## Lease y recuperación R06: dos cierres administrativos

Fuentes: `control/LEASE_R06_TX/RESULTADO.json` y
`control/RECUPERACION_LOAD_R06_TX/RESULTADO.json`, con sus planes prospectivos,
testigos por rol y código fijado por los freezes R06. El primer cierre conserva
pending/failure/uncertain y sólo cambia el testigo de alcance. La segunda
transacción afecta únicamente a LOAD1/2/3: retira uncertain técnico después de
comprobar que el rechazoQ2 precedía a todo pulso. Preserva literalmente fase,
pending, failure, recibos, secuencia, ciclos y política; RAW/clocks/N/T siguen
iguales. Cambian los bytes de snapshots por metadatos técnicos, sin declarar
identidad binaria. No modifica MAIN, CTRL1 o PILOT para reparar flags.

El ledger archivó las tres admisiones fallidas como conocidas de cero ticks;
consumed quedó10452 y la reserva3740 por vida, sin reinicio. El permiso externo
de la Q1 real se corrigió164→163 y la continuación usa un nuevo ID Q2 declarado,
conservando la Q1 original y su recibo. No hay repeticiónQ1, aprendizaje autónomo
ni nueva experiencia en esas transacciones. Las lecciones y funciones de la
continuación activa son operaciones posteriores y mantienen su propio ámbito.

## P01: condición nueva y fallo concreto del encoder

`control/CUA_MAIN_R07_ACTIVACION_UNICA_R02.json` conserva la selección de un
objeto Window real devuelto por Sky y una sola activación, sin inputs/capturas.
El probe de Root y `video/capturas/PRUEBA_DDA_REAL_ROOT_R02/PREFLIGHT.json`
documentan el cliente1280×648. El stderr R02 indica width not divisible by2
para1279×648; `RESULTADO.json` registra CAPTURE_FAILED y0bytes. Se transportan
stderr y metadatos originales, excluyendo ese MP4 vacío. Este negativo difiere
del NoDeviceSupport anterior de CaptureService. `video/prueba_DDA_R03.py` prepara
ROI de dimensiones pares y clamp; su comprobación AST no demuestra una captura
ni resuelve P01. No se ha fabricado un video de actuaciones.

## Recursos, privacidad y preparación portable

Los recursos MAIN6/P06 ya calculados se conservan sin repetición: no se suman
cada muestra CPU del Job ni otra vez los pases; compromiso de memoria, WorkingSet,
pared y latencia heredada son magnitudes distintas. Con cero entregas nuevas de
MAIN, su coste por entrega útil es indefinido. No se añade el coste vivo de LOAD.

La revisión de privacidad R03 sigue siendo el corte de146miembros,0candidatos
textuales y5binarios sin revisión visual por el script. No se repitió. R05 añade
fuentes y actualiza documentos: su revisión final de bytes y privacidad está
pendiente. Source conserva aliases absolutos exactos y archive relativos seguros.
E5 incluye sus primarios completos y la receta portable, sin volver a ejecutar el
recálculo verificado. El plan R05 sigue finalized:false, sin freeze ni ZIP.
La entrega deberá medir<=15000000B en el ZIP Deflate real y recalcular desde
una extracción limpia. Principal PI10, ACTIVO, Manual1.40, v27 y Thinking4.5
permanecen protegidos; este trabajador no los modifica.

## Cortes documentales anteriores, conservados como historia

Los apartados siguientes describen sus cortes históricos. Sus frases «pendiente»
o «no aplicada» no sustituyen los hechos del resumen R05 anterior.

'''
report_path.write_text(current+history,encoding='utf-8')
readme = '''DEE–ROBLOX V3 / R07 — EXPEDIENTE TENTATIVO R05
No es entrega final ni respaldo Native ejecutable. No se creó ZIP.

CORTE CERRADO MAIN6
MAIN N67/T1000571, padreR06/PAR28 T991187; seis oportunidades29–34.
9384ticks nuevos,21operaciones únicas, seisASK/EXIT1 sinoverride, bucle2↔3.
Tres luma+ heredadas:8+3=11.0enseñanzas/0nara/0recursos/0entregas nuevos.
Stock152; acumulados3/3 antiguos. P02 no cumple salida sostenida0/3 últimas fuera.

NUEVOS CIERRES
LeaseR06 aplicada0ticks a seisroles; sólo testigo de alcance. CTRL1/PILOT import0
intactos por archivos. Conserva N/T/RAW/clocks/pending/failure/uncertain/política.
Recuperación separada0ticks sóloLOAD1/2/3: uncertainTrue→False, demás campos
literales y fallo conservado. Ledger archiva3rechazosQ2 de0ticks; consumed10452,
reserva3740cadauno, sinreset. Q1 original no se repite. Permiso externo164→163.
Ventana aplicada: inicio16nov15:07UTC; lastnew17nov08:00UTC; hard17nov09:07UTC.

PROGRAMMED cerró18/18;2recursos/1entrega;8/8enteros correctos para su opcode.
Prefijo común6:PROGRAMMED1/1 frente MAIN0/0. No es ranking de capacidad:
el programa recibe estrategia/semántica/aritmética Python; ayudas e historias
no son equivalentes. Rechazos36sinprerrequisitos y41signocambiado/tupla9/2/1
retenida; no se describen como fallos aritméticos. Archive43→A7/B8→Gate46aceptado.
No se adquirió la tupla7/3/2. Segundo recurso no fue entregado dentrodelhorizonte.

CONVENTIONAL_AI primer intento: rechazo de RAM previo a World/política,
3333148672B<3758096384B;0oportunidades/0inferencias. No son18fallosdelmodelo.
DaemonR05 cerrado. InfraestructuraR06 preparadaFS, sin resultado incorporado.
Root reinició una herramientaNodeJSantigua, noDEE; no se atribuyeefectoRAM.

P07 EN CURSO, SIN FUENTES VIVAS CONGELADAS
Etapa1 cerrada:3Q1 reales,356ticks cadauna,T991543,0episodios; Q2rechazado
antesdepulsosporpermisonodescontado. Solapamientocomún280,405s de pared de
llamadas,incluyehost/checkpoint; no prueba instruccionesCPU simultáneas.
Despuésdela recuperación, Root informa continuaciónACTIVA2/3episodioscadauna,
T994315. A2preliminar8/4/8:LOAD2luma−6−2=4 tras experienceadmitted;
LOAD1/3lesson1NativePartialAdmission. No fusionarLOAD2conMAIN ni afirmar
independenciacausalperfecta o cierre3×3. No se seleccionan archivosvivos.

P01 SIGUE ABIERTO
Se conservan GDIblanco y CaptureServiceNoDeviceSupport. NuevaCUA activóMain
real sininputs/capturas; probeclient1280×648. DDA_R02fallóporencoder1279impar,
0bytes:excluirMP4vacío, conservarstderr/metadatos. R03corrigeROIpar/clamp,
sinresultadoverificadoenestecorte. No hayvideo final válido detresactuaciones.

P04/P06/P08
P04:descriptorPUNTO34_R06,5831miembros,copiascríticasparciales,raízlocalcompleta;
noimmutableallmembers ni rollbackautónomo/materialreopenútilMAINprobado.
P06:19,4693%<20%;0ticks,testigosiguales,cachéNOinstalada; negativoR01incluido.
P08:conectorXMLreal,mapa/controladorespreparados;editorpiloto cerróconSHAigual,
0Nativeallí. Episodio real en otro mapa/validaciónexterna pendientes.

LECTURA Y REPRODUCCIÓN
1. analisis/INFORME_CIERRE8_R07.md y protocolosprospectivos.
2. MAIN6:analisis/RECALCULO_MAIN6_R01 y primarios exactos.
3. E5:analisis/E5_MAIN6_PROGRAMMED18_RECALCULO_R01 y primarios completos.
4. control/RECETA_PORTABLE_E5_R05.json:recálculodocumental en extracciónlimpia.
5. RECURSOS_MAIN6_R01/RECURSOS_MAIN6_Y_P06_R01 y sus recetasexistentes.
6. LEASE_R06_TX/RECUPERACION_LOAD_R06_TX:planes previos+resultados, noexperiencias.

Plan actual:control/EXPEDIENTE_V3_PLAN_FINAL_TENTATIVO_R05.json,finalized:false.
Registro:control/FUENTES_CERRADAS_EFECTIVAS_R07.json. El selector verifica sólo
archivos explícitos/pins/afirmacionesdecierre; noabreSQLite/DEE/Studio/modelos.
Sourceabsolutoexacto y archiverelativoseguro sostienen losaliasesportables.
No ejecutar cerrar_y_recalcular_E5_R06.py enextracción:esinstrumentodecierrelocal;
usarRECALCULO_CIERRE8_R07_R02.py con--package-root yla recetaR05.

PENDIENTES ANTES DE ENTREGAR
CierresMAINposterior34/CTRL/LOAD3×3/IA/piloto, ámbitoP04, revisiónnuevosbytesy
privacidad,proteccióndelos11críticos,freezeRoot,ZIPDeflate<=15000000B real,
extracciónlimpia yrecálculodocumental. No interpretar un fixturecomoreproducción.
La revisiónprivacidadR03cubrió146miembros,0candidatostextuales,5binariossinvisual;
no certificanuevosmiembrosR05. PrincipalPI10/ACTIVO/Manual1.40/v27/Thinking4.5
siguenprotegidos y no se duplicaotroManualni pesos/SQLite/estadosNativecompletos.
'''
readme_path.write_text(readme,encoding='utf-8')
diagnostic = diagnostic_path.read_text(encoding='utf-8-sig')
diagnostic += '''

## Corte R05: DDA R02 y corrección preparada R03

La activación única de la ventana Main retornó éxito por Sky, sin inputs ni
capturas CUA. El probe de Root expuso cliente1280×648. La prueba DDA_R02 de
`video/capturas/PRUEBA_DDA_REAL_ROOT_R02` falló al abrir libx264 porque recibió
1279×648: ancho no divisible por2. Es fallo del encoder, distinto del
NoDeviceSupport anterior. RESULTADO registra0bytes; el MP4 vacío no se selecciona.
Se conservan INTENT/PREFLIGHT/RESULTADO y stderr originales. DDA_R03 prepara
dimensiones pares y clamp; AST correcto no demuestra una captura. P01 continúa
sin video final válido de tres actuaciones en este corte.
'''
diagnostic_path.write_text(diagnostic,encoding='utf-8')

recipe = dict(schema='DEE.R07.E5.PortableDocumentaryRecipe.R05',
 script='analisis/RECALCULO_CIERRE8_R07_R02.py',
 argv=['--inputs','analisis/INPUTS_E5_MAIN6_PROGRAMMED18_R06.json','--package-root','.', '--output','RECALCULO_E5_NUEVO'],
 run_from='Fresh final extraction root; output directory must be new.',
 source_resolution='Exact original absolute aliases in inputs resolve only through CONTROL/MANIFIESTO_SHA256.json to delivered safe archive paths; no original-drive fallback.',
 delivered_science_outputs='analisis/E5_MAIN6_PROGRAMMED18_RECALCULO_R01',
 closure_summary='E5_CIERRE_REAL_R06.json and gate-rejection explanation are preserved closure/analysis witnesses; pure recalculator regenerates numeric tables, not host actions or historical daemon lifecycle.',
 never_execute_for_portable_recalculation='analisis/cerrar_y_recalcular_E5_R06.py; it is a one-shot local closure instrument with local-path/existence checks.',
 existing_recalculation_not_repeated_by_this_update=True, final_clean_extraction_execution_pending=True,
 Native_DB_MCP_Studio_model_calls=0)
write(ROOT/'control/RECETA_PORTABLE_E5_R05.json',recipe)

plan = read('control/EXPEDIENTE_V3_PLAN_FINAL_TENTATIVO_R04.json')
assert plan['finalized'] is False and len(plan['files']) == 165
items = {r['archive'].casefold():r for r in plan['files']}
added = []
def member(rel, role='protocol', limit=None, expected=None):
    archive = rel.replace('\\','/')
    p = (ROOT/archive).resolve(strict=True)
    assert p.is_relative_to(ROOT), 'Explicit campaign source only'
    raw = p.read_bytes()
    if expected: assert len(raw) == expected['bytes'] and sha(raw) == expected['sha256'], 'Source differs from prospective code pin'
    if archive.casefold() in items:
        row = items[archive.casefold()]
        assert Path(row['source']).resolve(strict=True) == p and row['archive'] == archive
        return dict(source=str(p),archive=archive,role=row['role'],bytes=len(raw),sha256=sha(raw), **({'max_bytes':row['max_bytes']} if 'max_bytes'in row else {}))
    assert len(raw) <= (limit or 2_000_000), 'Large source requires explicit exception'
    row = dict(source=str(p),archive=archive,role=role,bytes=len(raw),sha256=sha(raw))
    if limit: row['max_bytes'] = limit
    plan['files'].append(row); items[archive.casefold()] = row; added.append(archive)
    return dict(row)

registry = read('control/FUENTES_CERRADAS_EFECTIVAS_R07.json')
def basis(rel, proof_kind, assertions, role='protocol', limit=None):
    row = member(rel,role,limit);row.update(proof_kind=proof_kind,assertions=assertions);return row
def claim(pointer, equals): return dict(pointer=pointer,equals=equals)
def group(family,label,files,closure,root_reviewed=False):
    g=dict(family=family,label=label,status='CLOSED',basis=closure,files=files)
    if root_reviewed:g['root_reviewed_closure_contract']=True
    return g

lease_files = []
for rel in ('control/CONGELADO_NATIVE_R07_LEASE_R06.json','control/LEASE_R06_TX/RESULTADO.json',
 'control/LEASE_R06_TX/PLAN.json','control/LEASE_R06_TX/PRE_APPLY_READONLY.json',
 'control/FUENTES_LEASE_R06_PREPARADAS.json','control/COPIAS_LEASE_R06_VERIFICACION_FS.json'):
    lease_files.append(member(rel))
for row in read('control/CONGELADO_NATIVE_R07_LEASE_R06.json')['files']:
    lease_files.append(member(row['file'],'code' if row['file'].endswith('.py') else 'protocol',expected=row))
for role in ('MAIN','CTRL1','LOAD1','LOAD2','LOAD3','PILOT'):
    for name in ('NATIVE_RESULT.json','CLOSED_PREFLIGHT.json','OLD_RBX07_NATIVE_SCOPE_INTEGRAL_V3.json',
                 'OLD_HOST_INTEGRAL_V3.json','NEW_SCOPE.json','NEW_HOST.json'):
        lease_files.append(member('control/LEASE_R06_TX/'+role+'/'+name))
registry['groups'].append(group('LEASE','R06_applied_scope_only_zero_ticks',lease_files,
 basis('control/LEASE_R06_TX/RESULTADO.json','ADMINISTRATIVE_COMPLETE',[
 claim('/status','CLOSED_LEASE_RENEWAL_COMPLETE'),claim('/new_native_ticks',0),
 claim('/accounting_unchanged',True),claim('/no_experiences_or_policy_written',True),
 claim('/results/0/role','MAIN'),claim('/results/5/role','PILOT') ])))

recovery_files=[]
for rel in ('control/CONGELADO_RECUPERACION_LOAD_R06.json','control/RECUPERACION_LOAD_R06_TX/RESULTADO.json',
 'control/RECUPERACION_LOAD_R06_TX/PLAN.json','control/RECUPERACION_LOAD_R06_TX/RESUMEN_PLAN_PARA_REVISION.json',
 'control/RECUPERACION_LOAD_R06_TX/PRE_APPLY_READONLY.json','control/RECUPERACION_LOAD_R06_TX/ARCHIVED_FAILED_ADMISSIONS.json',
 'control/VERIFICACION_RECUPERACION_DATOS_CERRADOS_R06.json','control/PRUEBA_PIDS_LOAD_CERRADOS_R06.json',
 'load/evidencia/CARGA3_R01/RESULTADO_ETAPA.json','load/evidencia/CARGA3_R01/CONCILIACION_PASIVA_R06.json'):
    recovery_files.append(member(rel))
for row in read('control/CONGELADO_RECUPERACION_LOAD_R06.json')['files']:
    recovery_files.append(member(row['file'],'code' if row['file'].endswith('.py') else 'protocol',expected=row))
for role in ('LOAD1','LOAD2','LOAD3'):
    for name in ('NATIVE_RESULT.json','FAILED_Q2_ORIGINAL.json','META_OWN_ANTES_EXACTO.json',
                 'META_ORIGINAL_FAILED_RECEIPT.json','ENVIRONMENT_PLANNED.json','ENVIRONMENT_VALIDATED.json'):
        recovery_files.append(member('control/RECUPERACION_LOAD_R06_TX/'+role+'/'+name))
    for name in ('RESULTADO.json','FASES.jsonl'):
        recovery_files.append(member('load/evidencia/CARGA3_R01/'+role+'/'+name,'native_control_primary'))
registry['groups'].append(group('LOAD','LOAD1_2_3_known_zero_admission_technical_recovery_only',recovery_files,
 basis('control/RECUPERACION_LOAD_R06_TX/RESULTADO.json','EXPLICIT_ROOT_CLOSED_CONTRACT',[
 claim('/status','THREE_KNOWN_ZERO_ADMISSION_GUARDS_RECOVERED'),claim('/new_native_ticks',0),
 claim('/Native_requests_submitted',0),claim('/consumed_unchanged',10452),
 claim('/reserved_each_unchanged',3740),claim('/remaining_intents',{}),
 claim('/no_learning_or_autonomous_repair_claim',True)]),True))

program_files=[]
for rel in ('evidencia/PROGRAMMED_R06_BLOQUE_01/RESULTADO.json',
 'evidencia/PROGRAMMED_R06_BLOQUE_01/EVENTS.jsonl',
 'comparadores/PROGRAMMED_R06/POLICY_STATE_V3.json','comparadores/PROGRAMMED_R06/POLICY_EVENTS_V3.jsonl'):
    program_files.append(member(rel,'native_control_primary'))
program_files.append(member('evidencia/PROGRAMMED_R06_BLOQUE_01/WORLD_CHECKPOINT.json','native_control_primary',4_000_000))
for name in ('HECHOS_CIERRE8_R07.json','E5_CIERRE_REAL_R06.json','EXPLICACION_DOS_RECHAZOS_PROGRAMMED_R01.json',
 'TODAS_OPORTUNIDADES_R07.csv','COMPARACION_R07.csv','LEER_RECALCULO_R07.txt'):
    program_files.append(member('analisis/E5_MAIN6_PROGRAMMED18_RECALCULO_R01/'+name,'analysis'))
for rel in ('analisis/INPUTS_E5_MAIN6_PROGRAMMED18_R06.json','control/RECETA_PORTABLE_E5_R05.json'):
    program_files.append(member(rel,'analysis'))
program_files.append(member('analisis/cerrar_y_recalcular_E5_R06.py','code'))
program_files.append(member('protocolo/CONGELADO_REFERENCIAS_RAM_R06.json'))
for row in read('protocolo/CONGELADO_REFERENCIAS_RAM_R06.json')['members']:
    program_files.append(member(row['file'],'code',expected=row))
program_group=group('PROGRAMMED','PROGRAMMED_R06_18_closed_actual',program_files,
 basis('evidencia/PROGRAMMED_R06_BLOQUE_01/RESULTADO.json','OWNER_CLOSED',[
 claim('/owner_closed',True),claim('/new_opportunities_completed',18),claim('/global_completed',46)] ,'native_control_primary'))
registry['groups']=[program_group if g['family']=='PROGRAMMED'and g['status']=='PENDING' else g for g in registry['groups']]

ai_files=[member('analisis/E5_MAIN6_PROGRAMMED18_RECALCULO_R01/E5_CIERRE_REAL_R06.json','analysis'),
 member('evidencia/CONVENTIONAL_AI_R06_BLOQUE_01/PREFLIGHT_RAM_REJECTED.json'),
 member('evidencia/CONVENTIONAL_AI_R06_BLOQUE_01/HOST_MEMORY_SAMPLES.jsonl'),
 member('comparadores/SERVIDOR_MODELO_V3_R05.jsonl')]
registry['groups'].append(group('CONVENTIONAL_AI','AI_first_prestart_RAM_rejection_daemon_R05_closed',ai_files,
 basis('analisis/E5_MAIN6_PROGRAMMED18_RECALCULO_R01/E5_CIERRE_REAL_R06.json','EXPLICIT_ROOT_CLOSED_CONTRACT',[
 claim('/CONVENTIONAL_AI/status','PRESTART_HOST_RAM_REJECTED_NOT_A_COGNITIVE_TRIAL'),
 claim('/CONVENTIONAL_AI/actual_new_opportunities',0),claim('/CONVENTIONAL_AI/inference_requests_by_campaign',0),
 claim('/CONVENTIONAL_AI/policy_or_World_opened',False),claim('/daemon/closed/server_exit_code',0)],'analysis'),True))
for g in registry['groups']:
    if g['family']=='LOAD'and g['status']=='PENDING':
        g['reason']='Root reports continuation ACTIVE,2/3episodes each atT994315; final3x3 closure absent. No live continuation file selected. Initial negative and zero-tick recovery are separate closed technical groups.'
    elif g['family']=='CONVENTIONAL_AI'and g['status']=='PENDING':
        g['label']='CONVENTIONAL_AI_R06_retry_prepared_not_executed_in_this_cut'
        g['reason']='First attempt was prestartRAMrejected,0World/0inferences,daemonR05closed. R06new infrastructure preparedFS; no actual new result incorporated.'
registry['documentary_updated_utc']=utc
registry['new_lease_R06']='APPLIED_ZERO_TICKS_SCOPE_ONLY_6ROLES; separateLOAD1/2/3technicaluncertaintyrecovery0ticks; closedwitnessesselected.'
write(REG,registry)

for rel in ('control/E5_LEASE_R06_CONGELADO.json','control/E5_LEASE_R06_PREPARADO.json'):
    member(rel)
infra=read('control/E5_LEASE_R06_CONGELADO.json')
for row in infra['new_files']:
    member(row['new'],'code',expected=dict(bytes=row['bytes'],sha256=row['new_sha256']))
for row in infra['extra_source_pins']:
    member(row['file'],'code',expected=row)
for rel in ('video/PROBE_METADATA_DDA_R01.json',
 'video/capturas/PRUEBA_DDA_REAL_ROOT_R02/RESULTADO.json',
 'video/capturas/PRUEBA_DDA_REAL_ROOT_R02/PREFLIGHT.json',
 'video/capturas/PRUEBA_DDA_REAL_ROOT_R02/INTENT.json',
 'video/capturas/PRUEBA_DDA_REAL_ROOT_R02/stderr.txt',
 'video/capturas/PRUEBA_DDA_REAL_ROOT_R02/stdout.txt','video/PRUEBA_DDA_R03_AST.json'):
    member(rel)
for rel in ('video/prueba_DDA_R02.py','video/prueba_DDA_R03.py'):
    member(rel,'code')
assert not any('PRUEBA_DDA_REAL_ROOT_R02.mp4' in r['archive'] for r in plan['files'])

changed={report_path.resolve(),readme_path.resolve(),diagnostic_path.resolve(),REG.resolve()}
for row in plan['files']:
    p=Path(row['source']); assert p.is_absolute()
    if p.resolve(strict=True) in changed:
        raw=p.read_bytes();row.update(bytes=len(raw),sha256=sha(raw))
    n=row['archive'];q=PurePosixPath(n)
    assert q.as_posix()==n and not q.is_absolute() and all(x not in ('','.','..')for x in q.parts)
    assert '\\'not in n and ':'not in n
    assert 'CARGA3_CONTINUACION_R06'not in n
plan['tentative_revision']='R05_PASSIVE_CLOSED_ADMIN_E5_WITH_ACTIVE_LOAD_NOTICE'
plan['documentary_updated_UTC']=utc
plan['coverage']='TENTATIVE:MAIN6closed;R06lease0ticks6rolesapplied;LOADtechnicalrecovery0ticks3rolesclosed;PROGRAMMED18closed;firstAIprestartRAMrejected0World0inferences;LOAD2of3eachreportedactive_notselected;P01DDA_R02encoderoddwidth0bytes,R03preparednoproof;P04materialuse/PILOT/CTRL/remainingMAINpending.'
plan['latest_reported_status']['R06_prospective'].update(activation_verified=True,activation_source='control/LEASE_R06_TX/RESULTADO.json',new_native_ticks=0)
plan['latest_reported_status']['LOAD_stage1'].update(administrative_recovery_applied=True,recovery_source='control/RECUPERACION_LOAD_R06_TX/RESULTADO.json')
plan['latest_reported_status']['LOAD_continuation_R06']=dict(provenance='Rootnotificationonly;notlivefileinspection',status='ACTIVE',complete_episodes_each=2,target_each=3,reported_tick_each=994315,selected_live_files=False,
 preliminary_A2=[8,4,8],LOAD2_luma_negative_6_minus_2_equals4=True,LOAD1_LOAD3_lesson1='NativePartialAdmission',LOAD2_lesson1='experienceadmitted',branches_not_merged_with_MAIN=True,perfect_causal_independence_claim=False)
plan['latest_reported_status']['E5_PROGRAMMED_R06']=e5['PROGRAMMED']
plan['latest_reported_status']['E5_AI_prestart']=e5['CONVENTIONAL_AI']
plan['latest_reported_status']['P01_DDA_R02']=dict(source='video/capturas/PRUEBA_DDA_REAL_ROOT_R02/RESULTADO.json',status='CAPTURE_FAILED',bytes=0,encoder_odd_width=1279,source_client=[1280,648],empty_MP4_selected=False,R03='PREPARED_NO_VALIDATED_RESULT_IN_THIS_CUT')
plan['latest_reported_status']['delegated_handoffs']='R06leaseandrecoveryactualclosed;PROGRAMMED18closed;AIprestartnegativepreserved;LOADcontinuationactive;noP06deployment.'
plan['pending_closed_sources']=[r for r in plan['pending_closed_sources'] if r['family']!='PROGRAMMED_and_actual_Llama']
plan['pending_closed_sources'].append(dict(family='actual_Llama_R06_retry',source=None,required='Actualboundedexecutionclosedresults/rawownmodeloutputs/quota/configorprecisefinalblocker;preparedFScodenotactualinference.'))
plan['recalculations'].append(dict(script='analisis/RECALCULO_CIERRE8_R07_R02.py',inputs='analisis/INPUTS_E5_MAIN6_PROGRAMMED18_R06.json',
 recipe='control/RECETA_PORTABLE_E5_R05.json',status='EXISTING_E5_MAIN6_PROGRAMMED18_OUTPUTS_INCLUDED_NOT_RERUN;finalcleanextractionpending',not_native_execution=True))
plan['selected_raw_bytes_at_listing_not_freeze']=sum(r['bytes']for r in plan['files'])
plan['large_files_needing_explicit_limit']=[r['archive']for r in plan['files']if r['bytes']>2_000_000]
plan['static_readcheck']='R05explicitclosedpinsandstructureonly;offlinefixturesnotrerun;privacy146notrepeated;newbytesreviewpending.'
plan['finalized']=False
plan['status']='TENTATIVE_DO_NOT_BUILD_ROOT_REVIEW_REQUIRED'
plan['documentary_update_basis']=dict(previous_plan=str(OLD),previous_plan_sha256=sha(OLD.read_bytes()),
 added_members=len(added),current_load_notice_is_not_closure=True,Native_DB_DEEimports_MCP_Studio_model_CUA_OS_measurement_calls=0,
 privacy_extension_pending=True,ZIP_created=False,final_hash_not_issued=True)
assert len(plan['files'])<=750 and plan['selected_raw_bytes_at_listing_not_freeze']<=40_000_000
assert len(plan['large_files_needing_explicit_limit'])<=4
write(NEW,plan)
continuity=dict(schema='DEE.R07.PassivePackageContinuity.R05',utc=utc,plan=str(NEW),members=len(plan['files']),raw_bytes=plan['selected_raw_bytes_at_listing_not_freeze'],
 finalized=False,ZIP_created=False,final_hash_issued=False,closed_added=['R06lease6rolesScopeOnly0ticks','LOAD1/2/3technicaluncertaintyrecovery0ticks','PROGRAMMED18','AIfirstprestartRAMrejectiondaemonR05closed'],
 active_not_selected=['CARGA3_CONTINUACION_R06;Root2/3episodesperlifeT994315','anynewAIexecution','DDA_R03unvalidatedcapture'],
 updated=[dict(path=str(p),sha256_before=before[str(p.relative_to(ROOT))],sha256_after=sha(p.read_bytes()))for p in(report_path,readme_path,diagnostic_path,REG)],
 added_files=added,portable=dict(E5_primary_result_world_events_all_selected=True,World_PROGRAMMED_large_exception=4_000_000,
 large_exception_count=len(plan['large_files_needing_explicit_limit']),absolute_aliases_preserved=True,
 recipe='control/RECETA_PORTABLE_E5_R05.json',one_shot_local_closer_not_portable=True,actual_clean_extraction_execution_pending=True),
 privacy='R03exact146reviewretainednotrerun;newandupdatedbytesextensionpending',
 limitations=['P01unresolved;R02emptyclipomitted;stderrrecordsencoderoddwidthnotdevicefailure',
 'P03LOAD2preliminarybranchresultnotMAINorperfectcausalindependence','P04fullrollback/materialMAINuseunproven',
 'PROGRAMMED18andcommon6separate;noequivalentpriororuniversalranking','AI0World0inferenceshostrejectionnot18modelerrors',
 'Noofflinefixturesorresource/scientificrecalculationsrepeated','NoNative/DB/MCP/Studio/model/CUA/OSmeasurementactionsbythisR05update'],
 pending=['Rootclosedremainingfronts','updateactualdenominators','reviewnewbytesprivacy','finalRootprotectionandfreeze','realDeflateZIP<=15000000B','cleanextractionrecalculation'])
write(CONT,continuity)
print(json.dumps(dict(plan=str(NEW),members=len(plan['files']),raw_bytes=plan['selected_raw_bytes_at_listing_not_freeze'],
 added=len(added),large_exceptions=len(plan['large_files_needing_explicit_limit']),finalized=False,ZIP_created=False,
 continuity=str(CONT),final_hash_issued=False),ensure_ascii=False))
