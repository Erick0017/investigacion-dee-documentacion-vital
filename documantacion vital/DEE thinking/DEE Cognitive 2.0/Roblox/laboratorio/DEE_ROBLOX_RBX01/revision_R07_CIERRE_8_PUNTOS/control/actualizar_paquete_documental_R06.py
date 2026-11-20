"""Curate closed P07 and one verified CTRL clip; no runtime, DB or ZIP calls."""
from pathlib import Path, PurePosixPath
import ast
import datetime
import hashlib
import json

ROOT=Path(__file__).resolve().parents[1]
OLD=ROOT/'control/EXPEDIENTE_V3_PLAN_FINAL_TENTATIVO_R05.json'
NEW=ROOT/'control/EXPEDIENTE_V3_PLAN_FINAL_TENTATIVO_R06.json'
CONT=ROOT/'control/CONTINUIDAD_PAQUETE_PASIVO_R06.json'
REG=ROOT/'control/FUENTES_CERRADAS_EFECTIVAS_R07.json'
MAP=ROOT/'control/MAPA_P07_FUNCIONES_PORTABLE_R06.json'
assert not NEW.exists() and not CONT.exists() and not MAP.exists()
def sha(raw):return hashlib.sha256(raw).hexdigest()
def read(rel):return json.loads((ROOT/rel).read_text(encoding='utf-8-sig'))
def write(path,obj):path.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def metadata(path):
    raw=path.read_bytes();return dict(source=str(path.resolve(strict=True)),bytes=len(raw),sha256=sha(raw))
utc=datetime.datetime.now(datetime.timezone.utc).isoformat()
HREL='load/evidencia/CARGA3_CONTINUACION_R06/HISTORIA_REAL_CERRADA_R06.json'
history_raw=(ROOT/HREL).read_bytes()
assert len(history_raw)==296708 and sha(history_raw)=='d314048958e5cd598354e87322e606efb59ee95a7b14d63ed8fd68a9aa0d845f'
history=json.loads(history_raw)
assert history['status']=='THREE_EXISTING_LIVES_THREE_REAL_CLOSED_EPISODES_EACH'
assert history['supervisor_status']=='ALL_DECLARED_LIVES_CLOSED_AND_COMPLETE'
assert history['global_consumed']==23460 and history['global_intents']=={}
assert len(history['lives'])==3
recipe_resource=read('analisis/RECURSOS_P07_LOAD3_CERRADO_R06/REPETIR_PORTABLE.json')
assert 'LEDGER_V3.json'not in json.dumps(recipe_resource), 'Resource recipe must not depend on live ledger'

# Copy only these nine explicit closed receipts. No directory search, snapshot,
# queue, ledger, actor journal or other Native file is opened here.
copies=[]
for li,life in enumerate(history['lives']):
    assert len(life['functions'])==3 and life['final_tick']==995879 and life['whole_native_ticks']==4692
    for fi,function in enumerate(life['functions']):
        pin=function['primary'];source=Path(pin['path'])
        assert source.is_absolute() and source.name.endswith('_FUNCTION.json')
        expected_parent=ROOT/'native'/life['profile']/'sistema/estado/servicios_locales'/life['life']/'RBX07_NATIVE_INTEGRAL_V3/functions'
        assert source.parent==expected_parent
        for item in (source,*source.parents):
            assert not item.is_symlink() and not(getattr(item.lstat(),'st_file_attributes',0)&1024)
        before=source.stat();raw=source.read_bytes();after=source.stat()
        assert (before.st_size,before.st_mtime_ns)==(after.st_size,after.st_mtime_ns)
        assert len(raw)==pin['bytes'] and sha(raw)==pin['sha256']
        archive='evidencia/P07_PRIMARIOS_FUNCIONES_R06/'+life['profile']+'/'+source.name
        destination=ROOT/archive
        destination.parent.mkdir(parents=True,exist_ok=True)
        with destination.open('xb')as target:target.write(raw)
        assert destination.read_bytes()==raw
        record=json.loads(raw)
        copies.append(dict(profile=life['profile'],life=life['life'],operation_id=record['context']['operation_id'],
                           original_source=str(source),copied_source=str(destination.resolve(strict=True)),
                           archive=archive,bytes=len(raw),sha256=pin['sha256'],
                           history_pointer='/lives/'+str(li)+'/functions/'+str(fi)+'/primary'))
assert len(copies)==9 and sum(r['bytes']for r in copies)==1089488
mapping=dict(schema='DEE.R07.P07.ExactFunctionCopies.R06',utc=utc,
 history=dict(source=str((ROOT/HREL).resolve(strict=True)),archive=HREL,bytes=len(history_raw),sha256=sha(history_raw)),
 functions=copies,originals_modified=False,Native_SQLite_MCP_model_calls=0,
 alias_rule='Exact original_source is provenance only. Portable reader opens only the mapped delivered archive whose source alias is copied_source, with identical pinned bytes.',
 captured_ledger=dict(history_fields=['global_consumed','global_intents','lives/*/ledger_world'],
                     historical_consumed=23460,historical_intents={},
                     historical_source_sha256=history['ledger']['sha256'],live_ledger_opened=False),
 limits=['Nine selected function receipts only; complete snapshots/SQLite remain local and are not transported.',
         'This preserves raw LESSON admission controls and arithmetic primaries; no function or audit was re-executed.'])
write(MAP,mapping)

report_path=ROOT/'analisis/INFORME_CIERRE8_R07.md'
readme_path=ROOT/'control/LEER_PRIMERO_V3_TENTATIVO_R01.txt'
diagnostic_path=ROOT/'video/P01_DIAGNOSTICO_CAPTURA_R07.md'
before_docs={str(p.relative_to(ROOT)):sha(p.read_bytes())for p in(report_path,readme_path,diagnostic_path,REG)}
previous=report_path.read_text(encoding='utf-8-sig')
assert previous.startswith('# DEE–Roblox V3 — Cierre de ocho puntos (R07)')
current='''# DEE–Roblox V3 — Cierre de ocho puntos (R07)

**Corte documental R06: P07 cerrado 3×3 y una captura original de CTRL verificada. La campaña y el video de tres paneles siguen abiertos.**

MAIN sigue acreditado por su bloque cerrado29–34: N67/T1000571, padre R06/PAR28
T991187, 9384 ticks nuevos y21 operaciones únicas. Eligió ASK/EXIT_1 seis veces,
sin override, dentro del bucle2↔3. Tres usos de luma positiva heredada formaron
8+3=11. Hubo cero enseñanza, nara, recurso o entrega nuevos en ese bloque.
Stock final152; los acumulados3/3 no son logros nuevos. P02 no cumplió salida
sostenida:0/3 últimas posiciones fuera de{2,3}. CTRL6 está activo según el aviso
del coordinador; sus EVENTS vivos no se incorporan como fuentes cerradas.

P07 terminó con tres vidas existentes y tres episodios completos por vida.
LOAD1/2/3 cerraron en N67/T995879, cada una con4692 ticks nuevos desde PAR28;
4336 corresponden a la continuación y356 al Q1 original conservado. No se
repitió Q1. Los nueve episodios son carga focal Native, sin tres NPC ni movimiento,
recursos o entregas Roblox. Las vidas comparten el pasado anterior a PAR28 y
no se consideran nueve organismos o tres réplicas independientes.

El solapamiento común de llamadas reales adapter.execute fue2448,8191952705383s;
el de vida de propietarios,2687,8757181167603s. Incluyen anfitrión, persistencia
y validaciones. Son pruebas de intervalos de pared solapados, sin afirmar
simultaneidad de instrucciones CPU. Los seis runs cerrados, tres Q1 originales
y tres continuaciones, suman3625,140625s de CPU de Job tomando el máximo acumulado
una vez por run. No se suman muestras ni se llama a esto energía o CPU del kernel.

## Estado P01–P08 en el corte R06

| Punto | Resultado acreditado | Límite y pendiente |
|---|---|---|
| P01 — Video real | Ya opera la captura original. CTRL1 CLIP_01:15s,450 cuadros,1278×648,30fps,SAR1:1,sin audio;559802B. Decodificación450/450 y cuatro muestras muestran al NPC desde A hasta estación3. | Es CTRL1, caso29/Q2, no MAIN. No se revisó por reproducción humana cada cuadro ni existe el montaje final de tres paneles. Los fallos GDI/CaptureService/DDA_R02 se conservan como historia. |
| P02 — Oscilación | MAIN6 conserva seis transiciones2↔3 y criterio de salida sostenida incumplido. | CTRL6 sigue activo en este corte; no se puntúa ni se congelan sus journals vivos. |
| P03 — Adaptación | LOAD1 lesson4/6,A8/B7; LOAD2 lesson6/6,A4/B5; LOAD3 lesson5/6,A8/B9. Recuerdo Native seleccionó los opcodes y produjo enteros reales. | Dosis efectivas y valencia del retorno difieren. La secuencia LESSON→A→B fue preparada. No es independencia causal perfecta, agencia general ni adquisición demostrada en MAIN. |
| P04 — Persistencia | MAIN World cerrado; descriptor5831 miembros con copias críticas parciales. Lease/recovery R06 a0ticks conservados. P07 registra propietarios cerrados y cola drenada en su auditoría capturada. | Snapshots/SQLite quedan locales. No se reabrieron aquí ni se acredita rollback autónomo completo o uso material posterior de MAIN tras reapertura. |
| P05 — Movimiento y objetivos | MAIN alcanzó seis destinos sin override; la captura CTRL29 muestra movimiento real2→3. PROGRAMMED mantiene2recursos/1entrega en18, y1/1 en el prefijo común6 frente a MAIN0/0. | La captura no convierte a CTRL en MAIN ni prueba evasión cuantitativa de obstáculos. Los resultados P07 no se cuentan como movimiento/recurso Roblox. Sin ranking general entre ayudas e historias diferentes. |
| P06 — Eficiencia | Benchmark cerrado19,4693% frente al umbral20%, cero ticks y testigos iguales. | Umbral no alcanzado; caché no instalada. No es aprendizaje ni aceleración cognitiva. |
| P07 — Tres agentes | Cerrado3×3 en tres vidas existentes, N67/T995879;4692ticks cada una; nueve retornos aceptados. RAW finales distintos y clocks iguales. | Carga focal en procesos separados, no tres NPC Roblox ni organismos independientes. El pipeline y los estímulos son preparados; la divergencia física sola no prueba memoria útil. |
| P08 — Prototipo y piloto | Conector XML real, kit y otro mapa preparados. Editor piloto propio cerrado sin cambiar SHA de escena; cero Native allí. | Falta episodio real en otro mapa y validación externa. No hubo contacto con desarrolladores. |

## P07: dosis reales, recuerdo y composición observados

El anfitrión ofreció LESSON(luma,nara), CALCULATE A(6,2) y después
CALCULATE B(A_REAL,1). Los sensores, operandos y orden fueron preparados;
el resultado real de A entró en B. Native recordó el signo y seleccionó SUMA
o DIFERENCIA mediante el codec fijo; el anfitrión no calculó esos enteros como
respuesta sustitutiva.

| Vida | Oferta y admisión real de lección | Recuerdo y composición observados |
|---|---|---|
| LOAD1 | luma+1/nara−1;4/6 entradas admitidas, dos revisiones rechazadas por soporte ocupado | +1/−1;6+2=8, después8−1=7 |
| LOAD2 | luma−1/nara+1;6/6 admitidas | −1/+1;6−2=4, después4+1=5 |
| LOAD3 | luma+1/nara+1;5/6 admitidas, revisión luma rechazada por ocupación | +1/+1;6+2=8, después8+1=9 |

Los nueve Q1 fueron ASK y los nueve Q2 EXIT_1. En la carga se registraron las
rutas, sin ejecutarlas sobre Roblox. Cada vida gastó tres permisos,164→161,
incluido el ASK original. Los primeros retornos LOAD1/LOAD3 usaron
materialConsequence=true por la admisión parcial; los otros siete usaron false,
sin reinterpretar false como premio. Todas las devoluciones fueron aceptadas.
Por eso las ramas no recibieron dosis idénticas ni consecuencias equivalentes.
No hubo fusión con MAIN ni selección de un principal nuevo.

`load/evidencia/CARGA3_CONTINUACION_R06/HISTORIA_REAL_CERRADA_R06.json` conserva
la auditoría de cierre: propietario detenido, quick_check=ok y ninguna cola
queued/processing/uncertain en el corte auditado. Este trabajador no abrió
SQLite ni volvió a verificar el estado vivo. La historia capturó literalmente
ledger consumed23460, intents{} y reservasLOAD0. Ese total describe aquel corte;
el ledger global posterior ya puede avanzar con CTRL y no se leyó ni se copió.

Se transportan nueve primarios exactos de función, incluidos sus controles
LESSON y recibos de admisión, por1089488B. Las copias mantienen SHA idéntico;
el mapa portable vincula original_source absoluto con source de copia absoluto
y archive seguro. Los snapshots completos y SQLite sólo conservan localizador,
tamaño y hash capturados. El verificador portable compara esos testigos
transportados, sin reabrir originales, DB, motor o ledger.

## P01: clip CTRL original y alcance de la cámara

`video/QA_CTRL1_CLIP_01_R02/VERIFICACION.json` vincula el clip con la Q2 real
de CTRL1, caso29, EXIT_1, y conserva el hash de la línea origen. El clip original
tiene SHA25669cc1ed190b369cca9a6054075afc8d6858870296c6fc3bb61b98835e80d1a10.
La decodificación completa terminó exit0 con450 cuadros. Las muestras0/150/300/449
muestran el cuerpo preparado, desplazamiento desde CalculationA junto a un
obstáculo y llegada al anillo amarillo de estación3. El avatar marrón separado
del jugador no se atribuye a Native. La alineación de cuadros con el instante
del evento no es exacta y no se usa para inferir latencia Native instantánea.

El viewer actúa sólo sobre el cliente/cámara con un offset fijo; se distingue
del motor, lectores y decisión Native. El código del recorder R03 y sus pruebas
offline se transportan como preparación, sin ejecutar otra captura aquí. La
grabación y CTRL siguieron bajo sus responsables externos durante la interrupción
de créditos; no se reconstruye ni retrodata un resultado. El video final de tres
paneles todavía no existe. La revisión de privacidad de nuevos videos e imágenes
se hará sobre la selección final, sin limitarla al antiguo corte146.

## Fuentes, portabilidad y pendientes de entrega

El plan R06 incorpora fuentes P07 cerradas, recursos capturados, nueve funciones
y sólo el primer clip CTRL ya verificado con su QA. No incorpora EVENTS activos
de CTRL. Se preservan los cierres administrativos R06, E5 y negativos anteriores.
La receta de recursos P07 usa cuatro PRIMARIOS capturados y no necesita ledger.
La auditoría local original con SQLite no se propone como receta portable;
el verificador documental nuevo usa el mapa y manifiesto del paquete.
No se repitieron los cálculos científicos o de recursos ya validados.

R06 sigue finalized:false, sin freeze ni ZIP. Quedan cierre de CTRL, MAIN posterior34,
IA y piloto, alcance P04, montaje de tres paneles, revisión de nuevos bytes y
privacidad, protección final de los once críticos, ZIP Deflate<=15000000B y
ejecución documental desde extracción limpia. Principal PI10, ACTIVO, Manual1.40,
v27 y Thinking4.5 permanecen protegidos; no se modifican por esta curación.

## Corte R05 y antecedentes, conservados como historia

Las secciones siguientes conservan sus cortes anteriores. Sus estados «activo»,
«captura sin resolver» o «pendiente» no sustituyen el resumen R06 precedente.

'''
report_path.write_text(current+previous.split('\n',1)[1],encoding='utf-8')
readme_path.write_text('''DEE–ROBLOX V3 / R07 — EXPEDIENTE TENTATIVO R06
No es entrega final ni respaldo Native ejecutable. No se creó ZIP.

CIERRES Y ALCANCE
MAIN6: N67/T1000571, oportunidades29–34,9384ticks nuevos y21operaciones únicas.
ASK/EXIT_1 seis veces, sin override, bucle2↔3. Tres luma+ heredadas:8+3=11.
Cero enseñanza/nara/recurso/entrega nuevos; stock152. P02 no cumple salida sostenida.
Lease R06 y recuperación LOAD1/2/3 son cierres administrativos distintos de0ticks;
conservan los campos permitidos y fallos originales, sin reset ni repeticiónQ1.

P07 YA CERRÓ3×3
Tres vidas existentes LOAD1/2/3, cada una N67/T995879 y4692ticks nuevos desdePAR28.
Son nueve episodios focales Native; no tres NPC ni movimiento/recurso Roblox.
Comparten el pasado previo y no son réplicas independientes.
LOAD1: lesson4/6,A8/B7; LOAD2:6/6,A4/B5; LOAD3:5/6,A8/B9.
LESSON→A(6,2)→B(A_REAL,1) fue preparado. Native produjo los enteros por recuerdo
y opcode; no fueron respuestas calculadas por el host. Dosis y retornos difieren:
los primeros LOAD1/3 tuvieron materialConsequence=true; los otros siete,false.
No fusionar con MAIN ni afirmar independencia causal perfecta o agencia general.
RAW finales distintos y clocks iguales son testigos físicos, no prueba suficiente
de memoria útil por sí solos. Nueve Q1 ASK y nueve Q2 EXIT_1; stock164→161cadauna.
Solapamiento común:2448,819195s de llamadas de pared, incluye host/persistencia.
Seis runs cerrados:3625,140625s de CPU Job, máximos una vez por run, no por muestra.

LEDGER HISTÓRICO Y FUENTES
HISTORIA_REAL_CERRADA_R06 captura consumed23460,intents{} y reservasLOAD0 del cierre.
No describe el ledger actual, que ya avanza con CTRL. No se leyó ni se copió éste.
La receta de recursos P07 sólo necesita cuatro PRIMARIOS capturados.
Nueve JSON de función se copian exactamente,1089488B, incluidos controles LESSON.
control/MAPA_P07_FUNCIONES_PORTABLE_R06.json conserva los aliases absolutos exactos
de originales/copias y archives seguros. Snapshots/SQLite grandes quedan locales
con localizadores y hashes capturados; no son parte de un respaldo ejecutable.

P01 CAPTURA ORIGINAL DISPONIBLE, MONTAJE PENDIENTE
CTRL1 CLIP_01:15s,450cuadros,1278×648,30fps,SAR1:1,sin audio,559802B.
QA completa de decodificación450/450 y cuatro muestras visuales muestran al NPC
desde A hasta estación3. Es CTRL1, caso29/Q2, no MAIN. El avatar del jugador es
otro cuerpo. No es prueba cuantitativa de evasión de obstáculos ni video1080p.
No se revisó por reproducción humana cada cuadro ni existe video final3paneles.
El viewer de cliente/cámara y su offset fijo se separan de Native. Se conserva
el código preparado del recorder R03, sin iniciar otra captura en esta curación.
Los fallos GDI/CaptureService y el DDA_R02 vacío se conservan como antecedentes.

LO QUE SIGUE ABIERTO
CTRL6 está activo y sus EVENTS vivos no se seleccionan. MAIN posterior34, IA,
piloto real en otro mapa, ámbito P04 y video final de tres paneles siguen abiertos.
PROGRAMMED18 conserva2recursos/1entrega; en prefijo común6,1/1 frente a MAIN0/0.
No es ranking general: ayudas e historias difieren. El primer AI fue rechazo RAM
previo a World/inferencias, no18erroresdelmodelo. P06:19,4693%<20%, noinstalado.

LECTURA Y REPRODUCCIÓN
1. analisis/INFORME_CIERRE8_R07.md y protocolos prospectivos.
2. load/evidencia/CARGA3_CONTINUACION_R06/LEER_CIERRE_LOAD_R06.txt.
3. control/RECETA_PORTABLE_P07_R06.json y mapa de nueve funciones.
4. analisis/RECURSOS_P07_LOAD3_CERRADO_R06/REPETIR_PORTABLE.json.
5. E5 y MAIN6 con sus primarios completos y recetas anteriores.
6. video/QA_CTRL1_CLIP_01_R02/VERIFICACION.json y clip original.

No ejecutar auditar_historia_cerrada_LOAD_R06.py como receta portable: ese auditor
local usa SQLite/ledger/raíces locales. Usar verificar_P07_capturado_portable_R06.py
con --package-root desde la extracción, sin originales. No se repitió la auditoría
ni los cálculos de recursos en esta actualización.

Plan: control/EXPEDIENTE_V3_PLAN_FINAL_TENTATIVO_R06.json, finalized:false.
Faltan cierre de frentes, revisión de nuevos bytes y privacidad sobre la selección
final, protección de los once críticos, freeze de Root, ZIP Deflate<=15000000B real
y extracción limpia con recálculo documental. El antiguo control146 de privacidad
no certifica nuevas capturas/funciones. Principal PI10,ACTIVO,Manual1.40,v27 y
Thinking4.5 siguen protegidos. No se duplica otro Manual ni motor/pesos/SQLite.
''',encoding='utf-8')
diagnostic_path.write_text(diagnostic_path.read_text(encoding='utf-8-sig')+'''

## Corte R06: captura CTRL original verificada, montaje todavía pendiente

La captura ya opera: CTRL1 CLIP_01 original,15s/450cuadros,1278×648,30fps,SAR1:1,
sin audio,559802B. SHA25669cc1ed190b369cca9a6054075afc8d6858870296c6fc3bb61b98835e80d1a10.
QA_CTRL1_CLIP_01_R02 conserva decodificación450/450 y cuatro muestras que muestran
al NPC ir de A a estación3. Es control CTRL1 caso29/Q2, no MAIN. El viewer de
cliente/cámara es externo a Native. No es1080p, alineación exacta evento/cuadro,
prueba cuantitativa de obstáculos ni montaje final3paneles. No hubo captura nueva
por este curador. La privacidad de nuevos binarios sigue pendiente del plan final.
''',encoding='utf-8')

portable_recipe=dict(schema='DEE.R07.P07.CapturedPortableRecipe.R06',
 verification=dict(script='control/verificar_P07_capturado_portable_R06.py',
 argv=['--package-root','.','--output','P07_TESTIGOS_NUEVO.json']),
 resources=dict(recipe='analisis/RECURSOS_P07_LOAD3_CERRADO_R06/REPETIR_PORTABLE.json',
 inputs='The four delivered PRIMARIOS only; no ledger argument or original-drive access.'),
 overlap=dict(script='load/recalcular_concurrencia_v3.py',
 argv=['--workers','load/evidencia/CARGA3_CONTINUACION_R06/LOAD1','load/evidencia/CARGA3_CONTINUACION_R06/LOAD2',
       'load/evidencia/CARGA3_CONTINUACION_R06/LOAD3','--output','P07_OVERLAP_NUEVO.json']),
 historical_ledger='Use the literal global_consumed/global_intents/lives.ledger_world in the delivered closed history. Original ledger path is provenance only and MUST NOT be opened.',
 local_audit_not_portable='load/auditar_historia_cerrada_LOAD_R06.py uses immutable SQLite and original Native roots; preserved as code, not executed by this recipe.',
 final_clean_extraction_execution_pending=True,validated_science_and_resource_calculations_not_repeated=True)
write(ROOT/'control/RECETA_PORTABLE_P07_R06.json',portable_recipe)

plan=json.loads(OLD.read_bytes());assert len(plan['files'])==301 and plan['finalized']is False
items={r['archive'].casefold():r for r in plan['files']};added=[]
def member(rel,role='protocol',expected=None):
    archive=rel.replace('\\','/');path=(ROOT/archive).resolve(strict=True)
    assert path.is_relative_to(ROOT)
    raw=path.read_bytes();assert len(raw)<=2_000_000
    if expected:assert len(raw)==expected['bytes'] and sha(raw)==expected['sha256']
    if archive.casefold()in items:
        row=items[archive.casefold()];assert row['archive']==archive and Path(row['source']).resolve(strict=True)==path
        return dict(source=str(path),archive=archive,role=row['role'],bytes=len(raw),sha256=sha(raw),**({'max_bytes':row['max_bytes']}if'max_bytes'in row else{}))
    row=dict(source=str(path),archive=archive,role=role,bytes=len(raw),sha256=sha(raw))
    plan['files'].append(row);items[archive.casefold()]=row;added.append(archive);return dict(row)

p07_files=[]
for rel in ('load/evidencia/CARGA3_CONTINUACION_R06/RESULTADO_ETAPA.json',HREL,
 'load/evidencia/CARGA3_CONTINUACION_R06/OVERLAP_MATERIAL_R06.json',
 'load/evidencia/CARGA3_CONTINUACION_R06/LEER_CIERRE_LOAD_R06.txt',
 'load/evidencia/CARGA3_CONTINUACION_R06/PLAN_EJECUTADO.json',
 'control/MAPA_P07_FUNCIONES_PORTABLE_R06.json','control/RECETA_PORTABLE_P07_R06.json',
 'control/VERIFICACION_P07_PORTABLE_SINTETICA_R06.json'):
    p07_files.append(member(rel,'analysis'))
for role in ('LOAD1','LOAD2','LOAD3'):
    for name in ('RESULTADO.json','FASES.jsonl'):
        p07_files.append(member('load/evidencia/CARGA3_CONTINUACION_R06/'+role+'/'+name,'native_control_primary'))
for rel in ('analisis/RECURSOS_P07_LOAD3_CERRADO_R06/RECURSOS_RECALCULADOS.json',
 'analisis/RECURSOS_P07_LOAD3_CERRADO_R06/REPETIR_PORTABLE.json',
 'analisis/RECURSOS_P07_LOAD3_CERRADO_R06/OWNERS_POR_RUN.csv',
 'analisis/RECURSOS_P07_LOAD3_CERRADO_R06/IMPORT0_SEPARADO.csv',
 'analisis/RECURSOS_P07_LOAD3_CERRADO_R06/FASES_POR_PARTICIPANTE.csv'):
    p07_files.append(member(rel,'analysis'))
resources=read('analisis/RECURSOS_P07_LOAD3_CERRADO_R06/RECURSOS_RECALCULADOS.json')
for pin in resources['portable_primary_selection']:
    p07_files.append(member('analisis/RECURSOS_P07_LOAD3_CERRADO_R06/'+pin['archive_relative'],'native_control_primary',pin))
for row in copies:p07_files.append(member(row['archive'],'native_primary',row))
for rel in ('load/auditar_historia_cerrada_LOAD_R06.py','control/verificar_P07_capturado_portable_R06.py',
 'control/test_P07_aliases_portable_R06_offline.py'):
    p07_files.append(member(rel,'code'))
registry=read('control/FUENTES_CERRADAS_EFECTIVAS_R07.json')
basis=member(HREL,'analysis');basis.update(proof_kind='EXPLICIT_ROOT_CLOSED_CONTRACT',assertions=[
 dict(pointer='/status',equals='THREE_EXISTING_LIVES_THREE_REAL_CLOSED_EPISODES_EACH'),
 dict(pointer='/supervisor_status',equals='ALL_DECLARED_LIVES_CLOSED_AND_COMPLETE'),
 dict(pointer='/global_consumed',equals=23460),dict(pointer='/global_intents',equals={}),
 dict(pointer='/lives/0/ledger_world/cycles',equals=3),dict(pointer='/lives/1/ledger_world/cycles',equals=3),
 dict(pointer='/lives/2/ledger_world/cycles',equals=3),dict(pointer='/new_native_calls_by_audit',equals=0)])
p07_group=dict(family='LOAD',label='P07_three_existing_lives_three_closed_episodes_R06',status='CLOSED',
 root_reviewed_closure_contract=True,basis=basis,files=p07_files)
registry['groups']=[p07_group if g['family']=='LOAD'and g['status']=='PENDING'else g for g in registry['groups']]
registry['documentary_updated_utc']=utc
registry['P07_ledger_scope']='Historical literal capture consumed23460/intents{}; global ledger now advancing under CTRL is not selected or read.'
write(REG,registry)

clip_rel='video/capturas/CTRL1_SEIS_R06_EVENTOS_R02/CLIP_01.mp4'
clip_qa=read('video/QA_CTRL1_CLIP_01_R02/VERIFICACION.json')
assert clip_qa['bytes']==559802 and clip_qa['sha256']=='69cc1ed190b369cca9a6054075afc8d6858870296c6fc3bb61b98835e80d1a10'
assert clip_qa['full_decoded_frames']==450 and clip_qa['capture_is_original_not_reconstruction']is True
member(clip_rel,'technical_capture_primary',dict(bytes=clip_qa['bytes'],sha256=clip_qa['sha256']))
for rel in ('video/capturas/CTRL1_SEIS_R06_EVENTOS_R02/RESULTADO_CLIP_01.json',
 'video/QA_CTRL1_CLIP_01_R02/VERIFICACION.json','video/QA_CTRL1_CLIP_01_R02/EXTRACCION.json',
 'video/QA_CTRL1_CLIP_01_R02/DECODIFICACION_COMPLETA.json'):
    member(rel,'analysis')
for name in clip_qa['visual_sample_files']:member('video/QA_CTRL1_CLIP_01_R02/'+name,'technical_capture_primary')
for rel in ('video/recorder_eventos_R07_R03.py','video/test_recorder_eventos_R07_R03_offline.py'):
    member(rel,'code')
# Exact closed viewer/recorder metadata paths supplied by the passive video owner.
extra_video_paths=[]
for rel in extra_video_paths:member(rel,'code'if rel.endswith(('.py','.luau'))else'protocol')

changed={report_path.resolve(),readme_path.resolve(),diagnostic_path.resolve(),REG.resolve()}
for row in plan['files']:
    path=Path(row['source']);assert path.is_absolute()
    if path.resolve(strict=True)in changed:
        raw=path.read_bytes();row.update(bytes=len(raw),sha256=sha(raw))
    archive=row['archive'];p=PurePosixPath(archive)
    assert p.as_posix()==archive and not p.is_absolute() and all(x not in ('','.','..')for x in p.parts)
    assert '\\'not in archive and ':'not in archive
    assert not archive.startswith('evidencia/CTRL1_SEIS_R06/')
    assert Path(row['source']).name!='LEDGER_V3.json'
for life in history['lives']:
    for key,reason in (('snapshot','Closed complete Native snapshot remains local; captured locator/hash only.'),
                       ('transport','Closed SQLite remains local; no DB opened by this curator or portable recipe.')):
        pin=life[key]if key=='snapshot'else life['transport']['database']
        plan['omissions'].append(dict(kind='P07_complete_state',source=pin['path'],bytes=pin['bytes'],sha256=pin['sha256'],reason=reason))
plan['tentative_revision']='R06_CLOSED_P07_AND_FIRST_ORIGINAL_CTRL_CLIP'
plan['documentary_updated_UTC']=utc
plan['coverage']='TENTATIVE:MAIN6closed;P07closed3x3captured;R06lease/recovery0valid;PROGRAMMED18closed;AIprestartnegative;CTRLactive_livejournalsnotselected;firstCTRLoriginalclipverifiednotMAINandnot3panel;P04fullrollback/PILOT/remainingMAINpending.'
plan['latest_reported_status']['LOAD_continuation_R06']=dict(source=HREL,status='CLOSED_3_BY_3',profiles=['LOAD1','LOAD2','LOAD3'],
 episodes_each=3,final_tick_each=995879,whole_new_ticks_each=4692,continuation_ticks_each=4336,originalQ1_not_replayed=True,
 raw_final_distinct=True,clocks_final_equal=True,lesson_admitted=[4,6,5],lesson_offered_each=6,A=[8,4,8],B=[7,5,9],
 host_ordered_pipeline=True,Roblox_motion_or_resources_counted=False,causal_independence_claim=False,merged_with_MAIN=False,
 historical_global_consumed=23460,historical_global_intents={},actual_live_global_ledger_not_read=True,
 resource_CPU_Job_seconds_six_runs=3625.140625,common_material_call_wall_overlap_seconds=2448.8191952705383)
plan['latest_reported_status']['P01_first_original_CTRL_clip']=dict(source=clip_rel,QA='video/QA_CTRL1_CLIP_01_R02/VERIFICACION.json',
 bytes=559802,frames=450,seconds=15,width=1278,height=648,fps=30,audio=False,branch='CTRL1',case=29,phase='Q2',
 original_capture=True,three_panel_final_exists=False,full_human_playback_review=False)
plan['latest_reported_status']['CTRL6_current_notice']='ACTIVE per Root; no live EVENTS selected as closed.'
plan['pending_closed_sources']=[r for r in plan['pending_closed_sources']if r['family']!='LOAD3x3']
plan['recalculations'].append(dict(script='control/verificar_P07_capturado_portable_R06.py',
 recipe='control/RECETA_PORTABLE_P07_R06.json',function_map='control/MAPA_P07_FUNCIONES_PORTABLE_R06.json',
 status='PREPARED_DOCUMENTARY_WITNESS_VERIFICATION;existingP07science/resourcesnotrerun;finalcleanextractionpending',not_native_execution=True))
plan['privacy_extension_pending']=True
plan['privacy_scope_requirement']='Review all new/updated bytes and binaries after final selection; do not present the old146memberreview as current coverage.'
plan['selected_raw_bytes_at_listing_not_freeze']=sum(r['bytes']for r in plan['files'])
plan['large_files_needing_explicit_limit']=[r['archive']for r in plan['files']if r['bytes']>2_000_000]
plan['finalized']=False;plan['status']='TENTATIVE_DO_NOT_BUILD_ROOT_REVIEW_REQUIRED'
plan['documentary_update_basis']=dict(previous_plan=str(OLD),previous_plan_sha256=sha(OLD.read_bytes()),
 only_explicit_nine_closed_function_receipts_copied=True,original_native_sources_modified=False,
 Native_DEEimports_SQLite_MCP_Studio_model_CUA_OS_measurement_calls=0,ZIP_created=False,
 scientific_and_resource_recalculations_repeated=False,final_hash_issued=False)
assert len(plan['files'])<=750 and plan['selected_raw_bytes_at_listing_not_freeze']<=40_000_000
assert len(plan['large_files_needing_explicit_limit'])<=4
ast.parse((ROOT/'control/verificar_P07_capturado_portable_R06.py').read_text(encoding='utf-8'))
write(NEW,plan)
write(CONT,dict(schema='DEE.R07.PassivePackageContinuity.R06',utc=utc,plan=str(NEW),members=len(plan['files']),
 raw_bytes=plan['selected_raw_bytes_at_listing_not_freeze'],added_files=added,finalized=False,ZIP_created=False,final_hash_issued=False,
 written_before_credit_cut='Only R05 existed at the earlier cut; R06 source reads preceded this new prospective write; no result was backdated.',
 updated=[dict(path=str(p),sha256_before=before_docs[str(p.relative_to(ROOT))],sha256_after=sha(p.read_bytes()))for p in(report_path,readme_path,diagnostic_path,REG)],
 function_copies=dict(count=9,bytes=1089488,map=str(MAP),exact_pins_matched=True,originals_modified=False),
 ledger_review=dict(resource_recipe_needs_ledger=False,captured_history_literal_fields=True,live_global_ledger_opened=False),
 P01=dict(first_original_CTRL_clip_included=True,main_attribution=False,three_panel_final_exists=False),
 not_selected=['LiveCTRL6EVENTS','Globalledgercurrentbytes','Otherunauthorizedclips','CompleteNativeSnapshots','SQLite'],
 checks=['SyntaxASTofnewportableverifier','Exactsourcepinsforninecopies','Safeexplicitarchiveandabsolutealiasstructure'],
 pending=['ActualselectorR06verification','ClosedCTRL/remainingMAIN/AI/PILOT','Threepanelvideo','Finalnewbytesandbinaryprivacyreview',
          'FinalRootprotectionandfreeze','DeflateZIP<=15000000Bmeasured','Cleanextractionportableverificationanddocumentaryrecalculation']))
print(json.dumps(dict(plan=str(NEW),members=len(plan['files']),raw_bytes=plan['selected_raw_bytes_at_listing_not_freeze'],
 added=len(added),function_copies=9,function_bytes=1089488,large_exceptions=len(plan['large_files_needing_explicit_limit']),
 finalized=False,ZIP_created=False,final_hash_issued=False),ensure_ascii=False))
