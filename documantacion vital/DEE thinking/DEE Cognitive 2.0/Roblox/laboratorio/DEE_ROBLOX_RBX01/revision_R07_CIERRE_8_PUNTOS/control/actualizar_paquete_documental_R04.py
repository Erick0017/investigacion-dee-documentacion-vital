"""Passive R07 documentary cut. Stdlib only; no Native or ZIP execution."""
from pathlib import Path, PurePosixPath
import datetime
import hashlib
import json

ROOT = Path(__file__).resolve().parents[1]
PLAN0 = ROOT/'control/EXPEDIENTE_V3_PLAN_FINAL_TENTATIVO_R03.json'
PLAN1 = ROOT/'control/EXPEDIENTE_V3_PLAN_FINAL_TENTATIVO_R04.json'
LEDGER = ROOT/'control/CONTINUIDAD_PAQUETE_PASIVO_R04.json'
assert not PLAN1.exists() and not LEDGER.exists(), 'Fresh documentary outputs required'
utc = datetime.datetime.now(datetime.timezone.utc).isoformat()
def sha(raw): return hashlib.sha256(raw).hexdigest()
def load(path): return json.loads(path.read_text(encoding='utf-8-sig'))
def write(path, value): path.write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
def replace_once(text, old, new):
    assert text.count(old) == 1, 'Documentary anchor differs'
    return text.replace(old, new, 1)

report_path = ROOT/'analisis/INFORME_CIERRE8_R07.md'
readme_path = ROOT/'control/LEER_PRIMERO_V3_TENTATIVO_R01.txt'
registry_path = ROOT/'control/FUENTES_CERRADAS_EFECTIVAS_R07.json'
before = {str(p.relative_to(ROOT)):sha(p.read_bytes()) for p in (report_path,readme_path,registry_path)}
report = report_path.read_text(encoding='utf-8-sig')
report = replace_once(report,
'El inicio sigue siendo el 16 de noviembre de 2026 a las 15:07 UTC; el último\nepisodio nuevo permitido es el 17 a las 02:00 UTC y el cierre máximo, a las\n03:07 UTC. No se reinició el reloj ni se amplió el horizonte de 18 oportunidades.',
'En esa transacción R05 REV3, el inicio siguió siendo el 16 de noviembre de 2026\na las 15:07 UTC, con último episodio nuevo el 17 a las 02:00 UTC y cierre máximo\na las 03:07 UTC. Una renovación prospectiva posterior R06 propone 08:00/09:07 UTC\ndel 17, siempre desde el mismo inicio. En este corte sólo se acredita su decisión;\nla activación administrativa R06 permanece pendiente. No se reinició el reloj\nni se amplió el horizonte de 18 oportunidades.')
report = replace_once(report,
'Los controles, referencias, carga, piloto y continuación posterior\nal caso 34 sólo se incorporarán al informe al recibir sus cierres verificables.',
'Los controles, referencias, piloto y continuación posterior al caso 34 sólo se\nincorporarán como resultados al recibir sus cierres verificables. Las referencias\nreales se están ejecutando, sin resultado cerrado incorporado. La primera etapa\nde carga cerró con tres Q1 reales y cero episodios completos; su fallo técnico\ny el alcance del solapamiento se registran abajo.')
report = replace_once(report,
'| P07 — Tres agentes | Existen preparación y protocolo de tres vidas por tres oportunidades. | No se cuentan importaciones o propietarios abiertos como trabajo concurrente. Faltan resultados cerrados y solapamiento útil. |',
'| P07 — Tres agentes | Tres vidas ejecutaron Q1: 356 ticks cada una, T991543; sus propietarios cerraron, con cero episodios completos. Hay 280,405 s de solapamiento común de llamadas Q1 de pared. | Etapa parcial negativa: el host no descontó el permiso y Q2 fue rechazado antes de pulsos. El solapamiento incluye host y checkpoint; no acredita simultaneidad de instrucciones ni tres actuaciones útiles completas. Recuperación administrativa y continuación pendientes. |')
report = replace_once(report,
'| P08 — Prototipo y piloto | Kit, mapa y controladores preparados, con fixtures offline. | El episodio real en otro mapa y la validación externa siguen pendientes. No se contactó a desarrolladores. |',
'| P08 — Prototipo y piloto | Conector XML real, kit, mapa y controladores preparados, con fixtures offline. El editor propio del piloto cerró conservando el hash de la escena. | No hubo episodio Native en ese editor. El episodio real en otro mapa y la validación externa siguen pendientes. No se contactó a desarrolladores. |')
old_cua = '''El 16 de noviembre se autorizó una sola tentativa ordinaria de cerrar la ventana
propia `PILOTO_R07.rbxlx`, informada en Edit y sin experiencias Native. El canal
computer-use se inicializó, pero `sky.list_windows()` terminó con
`computer-use request timed out: list_windows`. No devolvió una ventana, no se
activó nada y no hubo entrada de cierre, diálogo de guardar, captura, consulta
CIM o terminación de proceso. No se reintentó por otro canal. Se conserva el
editor y no se atribuye memoria RAM recuperada ni un cambio del paisaje.
Comprobante: `control/CUA_PILOTO_R07_TENTATIVA_UNICA_R01.json`. Este incidente
es de interfaz del anfitrión, no una prueba de P01 ni una incapacidad cognitiva.'''
new_cua = '''El 16 de noviembre se autorizó una tentativa ordinaria de cerrar la ventana
propia `PILOTO_R07.rbxlx`, informada en Edit y sin experiencias Native. El canal
computer-use se inicializó, pero `sky.list_windows()` terminó con
`computer-use request timed out: list_windows`. Esa tentativa no devolvió una
ventana ni ejecutó una entrada de cierre. Su comprobante se conserva en
`control/CUA_PILOTO_R07_TENTATIVA_UNICA_R01.json`.

Después, Root cerró únicamente ese editor propio con identificación CIM y
comando exactos, y verificación MCP de Edit. El comprobante posterior
`control/CIERRE_EDITOR_PILOTO_ROOT_R01.json` registra `gracefulRequested:true`,
`forceUsed:true` y `closed:true`. El SHA-256 de la escena antes y después coincide:
`ef39c6bf193c2f26386384e564ffcb16ab2e93c29f7b8a9e071431781dbcfd92`.
El comprobante declara que no se había abierto Native en ese editor. No se
atribuye una cantidad de RAM recuperada. Este cierre del anfitrión no acredita
P01, un episodio piloto ni un resultado cognitivo.'''
report = replace_once(report, old_cua, new_cua)
report += '''

## Carga P07: Q1 reales solapadas y fallo previo a Q2

`load/evidencia/CARGA3_R01/RESULTADO_ETAPA.json` conserva la primera etapa como
`PARTIAL_OR_BLOCKED_PRESERVED`. La conciliación pasiva
`load/evidencia/CARGA3_R01/CONCILIACION_PASIVA_R06.json` distingue los ticks
físicos de los cursores del worker que habían quedado atrasados. LOAD1, LOAD2
y LOAD3 llegaron cada una de T991187 a T991543: una Q1 real ASK, 356 ticks y
cero episodios completos por vida. Los tres propietarios quedaron cerrados.

El anfitrión dejó el stock en 164 después de la consulta que debía consumir un
permiso. El guard de Q2 rechazó el contrato antes del primer submit de pulsos;
la tentativa Q2 añadió cero ticks y no contiene una lectura Q2. No es un error
de cálculo ni un fallo cognitivo de las tres vidas. La Q1 original debe
conservarse: no se reproduce para ocultar el incidente. En este corte la
recuperación administrativa de cero ticks está preparada y todavía no aplicada.

La conciliación mide 280,404993057251 s comunes entre los intervalos reales de
`adapter.execute` de Q1. El solapamiento de vida de propietarios, una medida
distinta, es 891,2787547111511 s. Las llamadas incluyen pared del host y
checkpoint: no prueban instrucciones de CPU simultáneas. No se acredita el
objetivo de tres vidas por tres episodios útiles ni se mezcla este coste con
los 9384 ticks cerrados de MAIN6.

## Recursos ya calculados y su alcance

Se conservan las salidas existentes de `analisis/RECURSOS_MAIN6_R01` y
`analisis/RECURSOS_MAIN6_Y_P06_R01`. El informe combinado tiene SHA-256
`8cf04aa56ecab4eef63deb0da6c5019efce7a980c5bde76ec340c4edc9b27974`.
Sus contadores acumulados de CPU del Job se toman una vez por propietario;
no se suman cada muestra ni se vuelve a sumar el CPU de cada pase P06.
Los máximos de memoria comprometida del Job y el WorkingSet del proceso son
medidas diferentes. La latencia heredada `S.latency` no mide estas llamadas.
El coste por entrega nueva útil es indefinido porque hubo cero entregas nuevas.
Esta actualización documental no repitió el cálculo de recursos.

La receta portable combinada exige el primario P06 R01 además de R02. El nuevo
plan tentativo incluye ambos, conservando el negativo técnico R01 completo;
el contraste derivado continúa identificado como derivación. Se incluyen los
primarios reducidos MAIN6 que la receta documental necesita, no estados Native.

## Renovación prospectiva R06 y privacidad del corte R03

`protocolo/RENOVACION_PROSPECTIVA_REANUDACION_R06.json`, decidido a las 23:13 UTC
del 16, propone último episodio nuevo a las 08:00 UTC y cierre a las 09:07 UTC
del 17. Conserva el inicio original 15:07 UTC del 16, los criterios y el
horizonte; mantiene límites de 160000 ticks, seis vidas y 536870912 bytes por
propietario. No reinicia contadores ni admite operaciones retroactivamente.
La propia decisión condiciona su aplicación a propietarios cerrados,
conciliación por rol y migración administrativa de cero ticks. No se acredita
activación R06 por la mera existencia de este documento.

`analisis/REVISION_PRIVACIDAD_PLAN_R03.json` revisó una sola vez los 146 miembros
exactos del plan R03: todos fueron leídos y hasheados, con cero candidatos
heurísticos en el texto. El plan y esos bytes permanecieron iguales durante la
revisión. Cinco archivos binarios no recibieron revisión visual por ese script.
No se imprimieron valores o credenciales, ni se modificaron los originales.
Es una revisión finita del corte R03, no una certificación de futuros miembros
ni del ZIP final. Los documentos actualizados y miembros añadidos requieren
revisión final de sus bytes. El plan R04 sigue `finalized:false`; no se creó ZIP.

### Nueva condición técnica P01: una activación, sin nueva captura

Tras un probe de metadatos de Root que devolvió una ventana visible inequívoca,
se autorizó una sola selección y activación CUA de Main. Sky devolvió el objeto
real correspondiente al título completo de `DEE_RBX01_R07_NATIVE.rbxlx` y
`activate_window` retornó éxito a las 23:27 UTC. No se enviaron entradas ni se
tomaron capturas. La consulta posterior sin texto ni imagen fue rechazada por
validación de argumentos de la API; no se repitió la activación. El comprobante
`control/CUA_MAIN_R07_ACTIVACION_UNICA_R02.json` separa ese retorno del estado
de primer plano, que este trabajador no verificó independientemente. Esta
condición nueva no acredita exposición de video ni cambia el bloqueo P01.
'''
report_path.write_text(report, encoding='utf-8')

readme = readme_path.read_text(encoding='utf-8-sig')
readme = replace_once(readme,
'Último episodio nuevo: 17 nov, 02:00 UTC. Cierre máximo: 17 nov, 03:07 UTC.\nNo reinicia el reloj ni modifica criterios, política u horizonte de 18 casos.',
'Ventana aplicada R05 REV3: último episodio nuevo 17 nov, 02:00 UTC; cierre\nmáximo 03:07 UTC. La decisión prospectiva R06 propone 08:00/09:07 UTC del 17,\ncon el mismo inicio original; en este corte su activación permanece pendiente.\nNo reinicia el reloj ni modifica criterios, política u horizonte de 18 casos.')
readme = replace_once(readme,
'Continuación 35–46, reapertura material, cierre del control emparejado,\nreferencias programada y Llama local, carga concurrente y piloto.\nSólo sus fuentes cerradas se sumarán; no se inventan resultados faltantes.\nP07 no se acredita por abrir procesos; P08 no se acredita por un fixture.',
'Continuación 35–46, reapertura material, cierre del control emparejado,\nreferencias programada y Llama local, continuación de carga y piloto.\nLas referencias reales se están ejecutando; no se presenta un resultado cerrado.\nP07 etapa1: tres Q1 reales, cada una356 ticks/T991543, cero episodios completos.\nLos tres propietarios cerraron. El stock del host no descontó el permiso; Q2\nfue rechazado antes de pulsos y añadió cero ticks. No repetir Q1. La recuperación\nadministrativa de cero ticks está preparada, todavía no aplicada en este corte.\nEl solapamiento común de llamadas Q1 fue280,405s de pared, incluidos host y\ncheckpoint; no prueba simultaneidad de instrucciones ni tres actuaciones útiles.\nSólo sus fuentes cerradas se sumarán; no se inventan resultados faltantes.\nP08 incluye conector XML real y fixtures; falta el episodio Native en otro mapa.')
readme = replace_once(readme,
'5. P06_BENCHMARK_FULL_R02, contraste técnico R01/R02 y P01_DIAGNOSTICO_CAPTURA_R07.',
'5. P06_BENCHMARK_FULL_R01/R02, contraste técnico y P01_DIAGNOSTICO_CAPTURA_R07.\n6. RECURSOS_MAIN6_R01 y RECURSOS_MAIN6_Y_P06_R01: resultados y recetas existentes.')
readme = readme.replace('--plan control/EXPEDIENTE_V3_PLAN_FINAL_TENTATIVO_R02.json', '--plan control/EXPEDIENTE_V3_PLAN_FINAL_TENTATIVO_R04.json')
readme += '''
ACTUALIZACIÓN DOCUMENTAL R04
El editor propio PILOTO_R07 cerró después del fallo inicial de CUA. El testigo
control/CIERRE_EDITOR_PILOTO_ROOT_R01.json registra cierre y SHA de escena igual
antes/después; no hubo Native en ese editor. No acredita el episodio piloto.

La revisión de privacidad R03 cubrió146 miembros,0candidatos de texto y5binarios
sin revisión visual por el script. Su reporte es un corte histórico: los nuevos
miembros y bytes documentales actualizados necesitan revisión final.
El plan actual de preparación es control/EXPEDIENTE_V3_PLAN_FINAL_TENTATIVO_R04.json.
Incluye el negativo P06 R01 completo porque la receta portable de recursos lo
necesita. Usa aliases source absolutos exactos y archive relativos seguros.
Continúa finalized:false; no se congeló ni construyó el ZIP definitivo.
La entrega deberá usar Deflate y medir <=15000000 bytes en el ZIP real.
Nueva condición P01: una activación CUA de Main retornó éxito23:27UTC,
0inputs/0capturas. No acredita captura válida; bloqueoP01 continúa en este corte.
Testigo: control/CUA_MAIN_R07_ACTIVACION_UNICA_R02.json.
'''
readme_path.write_text(readme, encoding='utf-8')

registry = load(registry_path)
for group in registry['groups']:
    if group['status'] == 'CLOSED':
        for row in [group['basis'], *group['files']]:
            p = Path(row['source'])
            row['source'] = str((p if p.is_absolute() else ROOT/p).resolve(strict=True))
    elif group['family'] == 'LOAD':
        group['reason'] = 'Stage1 closed partial negative: each of3lives completedQ1 atT991543,356ticks,0completeepisodes; Q2 host permit guard rejected before pulses. Zero-tick administrative recovery and remaining episodes not yet closed. No P07 success claimed.'
    elif group['family'] in ('PROGRAMMED','CONVENTIONAL_AI'):
        group['reason'] = 'Actual reference execution reported by Root; no selected closed result in this documentary cut.'
    elif group['family'] == 'PILOT':
        group['reason'] = 'Real XML connector/other map prepared; own editor closed with scene SHA unchanged and0Native there. Await actual closed Native episode and external evaluation.'
registry['documentary_updated_utc'] = utc
registry['new_lease_R06'] = 'Prospective decision only in this cut; activation proof pending; R05REV3 closed witness remains selected.'
write(registry_path, registry)

plan = load(PLAN0)
assert plan['finalized'] is False and len(plan['files']) == 146
privacy = load(ROOT/'analisis/REVISION_PRIVACIDAD_PLAN_R03.json')
assert privacy['selected_members'] == 146 and not privacy['findings']
assert privacy['plan_sha256'] == sha(PLAN0.read_bytes())
coverage = {r['archive']:r for r in privacy['coverage']}
changed = {report_path.resolve(),readme_path.resolve(),registry_path.resolve()}
for item in plan['files']:
    p = Path(item['source'])
    p = (p if p.is_absolute() else ROOT/p).resolve(strict=True)
    item['source'] = str(p)
    witness = coverage[item['archive']]
    if p in changed:
        raw = p.read_bytes(); item.update(bytes=len(raw), sha256=sha(raw))
    else:
        item.update(bytes=witness['bytes'], sha256=witness['sha256'])
archives = {r['archive'].casefold() for r in plan['files']}
added = []
def add(relative, role='analysis', limit=None):
    archive = relative.replace('\\','/')
    assert archive.casefold() not in archives
    p = (ROOT/archive).resolve(strict=True)
    assert p.is_relative_to(ROOT)
    raw = p.read_bytes()
    row = dict(source=str(p), archive=archive, role=role, bytes=len(raw), sha256=sha(raw))
    if limit: row['max_bytes'] = limit
    assert len(raw) <= (limit or 2_000_000)
    plan['files'].append(row); archives.add(archive.casefold()); added.append(row)

for rel in (
    'analisis/RECURSOS_MAIN6_R01/IMPORT0_SEPARADO.csv',
    'analisis/RECURSOS_MAIN6_R01/FASES_POR_PARTICIPANTE.csv',
    'analisis/RECURSOS_MAIN6_R01/OWNERS_POR_RUN.csv',
    'analisis/RECURSOS_MAIN6_R01/REPETIR_PORTABLE.json',
    'analisis/RECURSOS_MAIN6_R01/RECURSOS_RECALCULADOS.json',
    'analisis/RECURSOS_MAIN6_R01/PRIMARIOS/01_owner.jsonl',
    'analisis/RECURSOS_MAIN6_R01/PRIMARIOS/02_phases.jsonl',
    'analisis/RECURSOS_MAIN6_R01/PRIMARIOS/03_phases.jsonl',
    'analisis/RECURSOS_MAIN6_Y_P06_R01/RECURSOS_MAIN6_Y_P06.json',
    'analisis/RECURSOS_MAIN6_Y_P06_R01/RECETA_Y_FUENTES_RECURSOS_R01.json',
    'analisis/RECURSOS_MAIN6_Y_P06_R01/P06_JOBS_SEPARADOS.csv',
    'analisis/REVISION_PRIVACIDAD_PLAN_R03.json',
): add(rel)
add('analisis/RECURSOS_CORE_P06_R07.py', 'code')
add('analisis/revisar_privacidad_plan_R03.py', 'code')
add('control/CIERRE_EDITOR_PILOTO_ROOT_R01.json', 'protocol')
add('control/CUA_PILOTO_R07_TENTATIVA_UNICA_R01.json', 'protocol')
add('control/CUA_MAIN_R07_ACTIVACION_UNICA_R02.json', 'protocol')
add('protocolo/RENOVACION_PROSPECTIVA_REANUDACION_R06.json', 'protocol')
add('evidencia/P06_BENCHMARK_FULL_R01/RESULTADO_P06.json', 'native_control_primary', 8_000_000)
plan['omissions'] = [r for r in plan['omissions'] if r.get('source') != 'evidencia/P06_BENCHMARK_FULL_R01/RESULTADO_P06.json']
plan['baseline_recalculation']['source'] = str((ROOT/plan['baseline_recalculation']['source']).resolve(strict=True))
plan['tentative_revision'] = 'R04_PASSIVE_DOCUMENTARY_20261116'
plan['documentary_updated_UTC'] = utc
plan['coverage'] = ('TENTATIVE. MAIN6closed;P01blocked;P04partialcriticalcopies,nomaterialreopen;'
 'P06closed19.4693percentbelow20criterion,notinstalled;LOADstage1threeQ1atT991543,0episodes,'
 'hostQ2rejectionbeforepulses,administrativerecoverypending;R06decisionnotactivated;'
 'actualreferencesrunningbutnoclosedsources;pilotXMLprepared,Nativeepisodepending.')
plan['latest_reported_status']['delegated_handoffs'] = 'R05REV3andP06closed;CTRL/referencesawaitclosedresults;LOADstage1negativepreserved;noP06deployment.'
plan['latest_reported_status']['LOAD_stage1'] = dict(source='load/evidencia/CARGA3_R01/CONCILIACION_PASIVA_R06.json',
 owner_closed=True, lives=3, Q1_per_life=1, ticks_per_life=356, final_tick_per_life=991543,
 complete_episodes_per_life=0, Q2_native_tick_delta=0, host_permit_bug=True,
 administrative_recovery_applied=False, original_Q1_must_not_be_replayed=True,
 material_call_wall_overlap_seconds=280.404993057251,
 wall_interval_includes_host_and_checkpoint=True, selected_as_closed_P07_success=False)
plan['latest_reported_status']['R06_prospective'] = dict(
 source='protocolo/RENOVACION_PROSPECTIVA_REANUDACION_R06.json', original_start='2026-11-16T15:07:00Z',
 last_new='2026-11-17T08:00:00Z', hard_finish='2026-11-17T09:07:00Z', activation_verified=False,
 reset=False, retrospective_admission=False, native_tick_cap=160000, life_cap=6, owner_memory_bytes=536870912)
plan['latest_reported_status']['PILOT_editor_closed'] = dict(source='control/CIERRE_EDITOR_PILOTO_ROOT_R01.json',
 closed=True, forceUsed=True, scene_sha256_before_after_equal=True, Native_episodes_in_editor=0)
plan['privacy_cut_R03'] = dict(source='analisis/REVISION_PRIVACIDAD_PLAN_R03.json', sha256=sha((ROOT/'analisis/REVISION_PRIVACIDAD_PLAN_R03.json').read_bytes()),
 selected_members=146, candidates=0, binary_visual_limits=5, covers_future_or_updated_bytes=False)
plan['recalculations'].append(dict(script='analisis/RECURSOS_CORE_P06_R07.py',
 recipe='analisis/RECURSOS_MAIN6_Y_P06_R01/RECETA_Y_FUENTES_RECURSOS_R01.json',
 status='EXISTING_OUTPUTS_INCLUDED_NOT_RERUN;final_clean_extraction_pending', Native_calls=0))
plan['selected_raw_bytes_at_listing_not_freeze'] = sum(r['bytes'] for r in plan['files'])
plan['large_files_needing_explicit_limit'] = [r['archive'] for r in plan['files'] if r['bytes'] > 2_000_000]
plan['finalized'] = False
plan['status'] = 'TENTATIVE_DO_NOT_BUILD_ROOT_REVIEW_REQUIRED'
plan['static_readcheck'] = 'R04structuralcheckonly;R03privacyhashesreusedforunchangedbytes;noNative/recalculation/ZIP.'
plan['documentary_update_basis'] = dict(prior_plan_sha256=sha(PLAN0.read_bytes()), prior_members=146,
 added_members=len(added), reused_privacy_witnesses=True, final_freeze_required=True,
 Native_DB_MCP_Studio_model_OS_measurement_calls=0, ZIP_created=False)
for item in plan['files']:
    name = item['archive']; p = PurePosixPath(name)
    assert p.as_posix() == name and not p.is_absolute() and all(x not in ('','.','..') for x in p.parts)
    assert '\\' not in name and ':' not in name and Path(item['source']).is_absolute()
assert len(plan['files']) <= 750
assert plan['selected_raw_bytes_at_listing_not_freeze'] <= 40_000_000
assert len(plan['large_files_needing_explicit_limit']) <= 4
write(PLAN1, plan)
ledger = dict(schema='DEE.R07.PassivePackageContinuity.R04', utc=utc,
 scope='Documentarywork:report/readme/packageplanonly,noNative/SQLite/DEEimports/MCP/model/OSmeasurementcalls,noZIP. SeparateRootauthorizedCUAMainselection/activationonlyisrecordedexplicitly.',
 CUA_exception=dict(source='control/CUA_MAIN_R07_ACTIVACION_UNICA_R02.json',selected_returned_window=True,activation_attempts=1,activation_returned=True,input_calls=0,capture_calls=0),
 previous_plan=dict(path=str(PLAN0),sha256=sha(PLAN0.read_bytes()),members=146,untouched=True),
 privacy=dict(path=str(ROOT/'analisis/REVISION_PRIVACIDAD_PLAN_R03.json'),sha256=plan['privacy_cut_R03']['sha256'],members=146,candidates=0,binary_visual_limits=5),
 updated=[dict(path=str(p),sha256_before=before[str(p.relative_to(ROOT))],sha256_after=sha(p.read_bytes())) for p in (report_path,readme_path,registry_path)],
 output_plan=dict(path=str(PLAN1),sha256=sha(PLAN1.read_bytes()),members=len(plan['files']),raw_bytes=plan['selected_raw_bytes_at_listing_not_freeze'],finalized=False),
 added_files=added,
 portable_issue_resolved='P06R01primaryaddedbecausecombinedresource_reciperequiresit;secondexplicitlargeprimaryexception.',
 pending=['RootclosurecontractsforCTRL/references/LOADcontinuation/MAIN/PILOT','R06activationproof','materialreopen/P04fullrollbackscope',
 'reviewnewandupdatedbytesprivacy','Rootfinalfreezeandprotectionproof','finalDeflateZIP<=15000000B','cleanextractionandpassivedocumentaryrecalculation'],
 unchanged_protected_originals='Thisworker didnotopenoreditprincipal,ACTIVO,Manual1.40,v27orThinking4.5;finalelevenfilecheckbyRootpackagerrequired.')
write(LEDGER, ledger)
print(json.dumps(dict(plan=str(PLAN1),plan_sha256=sha(PLAN1.read_bytes()),members=len(plan['files']),
 raw_bytes=plan['selected_raw_bytes_at_listing_not_freeze'],added=len(added),finalized=False,
 continuity=str(LEDGER),continuity_sha256=sha(LEDGER.read_bytes()),ZIP_created=False),ensure_ascii=False))
