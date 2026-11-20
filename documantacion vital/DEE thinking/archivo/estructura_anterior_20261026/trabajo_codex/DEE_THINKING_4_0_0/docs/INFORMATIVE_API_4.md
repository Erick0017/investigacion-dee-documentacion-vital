# Sesiones informativas nativas de DEE4

Las dos sesiones son clases C++20 de `DEE::thinking`, expuestas por el mismo
binario en Python. No importan runners del laboratorio ni leen resultados
guardados para contestar. Cada sesión posee un `OrganizationalWorld` y continúa
su Runtime; crear otra sesión inicia otra preparación.

## Dos dominios distintos

| Sesión | Preparación | Recorrido físico publicado | Límites |
|---|---|---|---|
| `FinitePolicySession` | N67, tick0, política inicial P | acción1 → dato de P2 → comparación6 → política10 → acción P/Q11 → dato14 | Una revisión finita; regla conservar P si coincide/cambiar Q si discrepa preparada; Q es complemento binario de P |
| `NativeInformationSession` | N47, semilla T32, cuerpo H0 | experiencias A/B32–33 → sonda34 → emisión37 → comparación47 → ruta51 → dato56 → sonda común61 → uso64 | Recursos finitos, distancia10; no demuestra aprendizaje general de utilidad ni reescritura posterior de A/B |

No son órganos fusionados de un individuo universal. El segundo aparato no es
una reinstalación dentro de `CognitiveSession`.

Los orígenes son coordenadas toroidales dentro de la dimensión de cada receta.
La carga informativa admite el campo representable `uint16`; el recorrido
funcional de referencia se midió con23 y41, no con todas las cargas. Fuera de
ese dominio puede haber saturación, otra transformación o ausencia de lectura
admisible; no se sustituye por una respuesta calculada. `history` admite AB, BA
y H0 en esta interfaz. `distance` se mantiene en10; otra geometría se estudia
mediante `OrganizationalWorld` de investigación, no modificando este contrato.

## Modalidades y entradas

- `create`: preparación declarada antes de evolucionar. Instala todas las
  rutas, mediadores y alternativas de consulta; no instala la respuesta final.
- `advance`/`run_until`: evolución v27 y protocolo de entradas previamente
  declarado. `run_until` recibe tick absoluto; `advance` recibe cantidad.
- `process_boundary`: programa, sin avanzar, las entradas debidas en la frontera
  actual. Permite guardar una cola pendiente y continuarla después.
- `submit_actual(-1|1)`: sensor externo explícito en la frontera2 o43. Son dos
  códigos físicos presentes, no un timeout que invente ausencia. El mismo
  informe se codifica en dos rutas fijas; no son dos experiencias independientes.
- `observe`: observación pasiva de registros actuales. `compare`, `source` y
  `sense` avanzan solamente hasta sus ventanas físicas declaradas. No recuperan
  una respuesta terminal de una caché cuando esa ventana ya pasó.
- `fork`: copia operativa independiente, explícita. `diagnostic_fork(edits,
  authorize=True)` aplica intervenciones identificadas sólo a la copia. Nunca
  se devuelve un fork a MAIN automáticamente.

La clase del entorno y los papeles P/Q se eligen como configuración inicial.
El informe real posterior es una entrada externa declarada; el host no calcula
discrepancia, penalización ni fuente elegida para escribirla en la organización.
La política preparada de N67 no se presenta como regla adquirida desde cero ni
como solución para fuentes arbitrarias. Los costes físicos de codificar P y Q
no son iguales en todos los signos; no se afirma una ventaja de recursos.

Cada entrada tiene un recibo Runtime. `Scheduled` no implica `Applied`. Una
entrada rechazada no se repara ni reintenta silenciosamente. La primera
observación de política informa `ACTUAL_REPORT_OMITTED`,
`EXTERNAL_CURRENT_ACTUAL_REPORT_APPLIED`, `ACTUAL_REPORT_PARTIALLY_APPLIED` o
`ACTUAL_REPORT_NOT_APPLIED` según los recibos reales.

## Ejemplo Python

```python
import dee_thinking as d

p = d.FinitePolicyParameters()
p.roles = d.SourceRole.Q_INFORMATIVE
p.actual_class = 1
s = d.FinitePolicySession.create(p)
print(s.sense().as_dict())       # informe externo actual y recibos
print(s.compare().as_dict())     # producto físico6
print(s.source().as_dict())      # acción física11: no elección desde metadata
s.set_interface_metadata("alias_externo", "fuente opaca")
s.save_snapshot("policy_t11.deetsnap")
loaded = d.FinitePolicySession.load_snapshot("policy_t11.deetsnap")
print(loaded.sense().as_dict())  # dato que llega por la ruta en14

p = d.NativeInformationParameters()
p.seed_path = d.reference_seed_path()
p.history = d.BasalHistory.BA
p.context = 0
p.actual_class = 1
s = d.NativeInformationSession.create(p)
s.run_until(43)
s.process_boundary()            # recibos pendientes, todavía no aplicados
s.save_snapshot("information_pending.deetsnap")
s = d.NativeInformationSession.load_snapshot("information_pending.deetsnap")
print(s.run_until(56).as_dict())  # información física recibida
print(s.run_until(64).as_dict())  # uso posterior por la misma dinámica
```

El parámetro `history` del segundo recorrido selecciona el protocolo de
acontecimientos físicos A/B aplicado a H0 en32–33; no escribe delta ni carga
histórica directamente. `H0` omite esos acontecimientos. Las sondas pueden
transformar su contexto; no equivalen a observación pasiva.

## Persistencia y captura

`save_snapshot` conserva Runtime físico, clocks, tick, canales, entradas
pendientes, recibos, receta, vistas, progreso del protocolo, journal y metadata
de interfaz. `load_snapshot` valida formato y restaura; no vuelve a preparar ni
lee la semilla original para rehacer la historia. Los enteros64 no pasan por
float. La metadata se guarda en bloques acotados de512KiB.

La metadata de interfaz es externa e inerte: hasta128 claves, clave1024bytes,
valor65536bytes, total512KiB. No se ejecutan funciones serializadas. El journal
captura hasta8192 operaciones; al alcanzar su límite continúa el Runtime y
`journal_truncated=True` declara la cobertura incompleta. No resetea ni detiene
la organización. El contenedor operativo de sesión admite hasta2MiB de metadata
binaria antes de su codificación; estos límites son compatibles con los nombres
internos fijos y el máximo de la interfaz. La traza opcional del mundo mantiene
su propio contrato de captura.

Las clases no son copiables implícitamente en C++; mover conserva propiedad y
`fork()` es la copia profunda explícita. Las vistas Python conservan al dueño
mediante `reference_internal`; varias vistas de una sesión comparten Runtime.
Modificar directamente `.world` es una intervención explícita del usuario y
debe examinarse también en `world.external_operations`/`diagnostic_edits`.

Pruebas reproducibles:

```powershell
python -I -B source/tests/python/test_informative4.py
python -I -B validation/compare_informative40.py --python-reference RUTA_35_PYTHON --python-new RUTA_4_PYTHON --evidence-root evidence/CPC3 --output validation/informative_parity
```

El ejemplo C++ `source/examples/informative_public.cpp` recibe la semilla y un
directorio de salida. Utiliza sólo headers y biblioteca del producto. Los
oráculos numéricos aparecen exclusivamente en tests y nunca deciden las
respuestas nativas.
