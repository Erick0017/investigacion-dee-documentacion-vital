# Matriz de aceptación definitiva — DEE thinking 2.2.0

Esta matriz distingue evidencia heredada de ejecuciones del corte 2.2.0. Una
fila sólo cambia de `PENDIENTE` a `APROBADA` o `FALLIDA` cuando existe comando,
salida y artefacto identificable bajo `validation/`.

## Resumen de estado

| Bloque | Evidencia anterior | Ejecución 2.2.0 |
|---|---|---|
| Suite C++ heredada (15 targets) | 15/15 en cierre 2.1.0 | APROBADA dentro de CTest 17/17 post-corrección (820,79 s) |
| Protocolos H1/H2/H3/H4/F1/F2 C++ | candidatos/laboratorio ejecutados por separado | APROBADA: suite integrada y coberturas dirigidas B01/B04/B16–B17 |
| Consumidor C++ instalado | aprobado en cierre 2.1.0 | APROBADA 2.2.0 por `find_package` |
| Wheel CPython 3.13 | no existía | APROBADA: wheel nativo post-corrección de 465.442 bytes |
| Instalación limpia y ejemplos Python | no existía | APROBADA: 11/11 desde venv/cwd externo, 29,457 s |
| Paridad C++/Python | no existía | APROBADA: Runtime y H1/H2/H3/F1/F2 exactos en ambos sentidos |
| Persistencia C++↔Python | no existía | APROBADA en ambos sentidos |
| Extracción limpia del ZIP | no existía para este corte | APROBADA: 49 targets, CTest 8/8, install/consumer y wheel reconstruido |

## A. Regresión nativa heredada

| ID | Prueba obligatoria | Criterio 2.2.0 | Estado |
|---|---|---|---|
| A01 | `kernel_whl_differential` | fixtures RAW+clock exactos | APROBADA, CTest post-corrección |
| A02 | `runtime_contract` | eventos, admisión, advance(0), pausa, observe/probe, fork | APROBADA, CTest post-corrección |
| A03 | `reference_organizations` | constructores heredados y controles | APROBADA, CTest post-corrección |
| A04 | `execution_backends` | Dense/Lazy/Parallel 1/2/4, primer tick discrepante ausente | APROBADA, CTest post-corrección |
| A05 | `integration_persistence` | snapshot v1/v2, cola, restore seguro y futuro | APROBADA, CTest post-corrección |
| A06 | `composition_catalog` | contratos/diagnósticos/composiciones heredadas | APROBADA, CTest post-corrección |
| A07 | `composition_snapshot_restore` | receta autocontenida y rechazos incompatibles | APROBADA, CTest post-corrección |
| A08 | `core05_phase_memory` | NRH04/NRH06, paridad y multibackend | APROBADA, CTest post-corrección |
| A09 | `cross_process_persistence` | proceso A guarda; B carga y continúa exactamente | APROBADA, CTest post-corrección |
| A10 | seis targets e2e heredados | ejemplos/consumidor/composiciones | APROBADA, CTest post-corrección |

## B. Capacidades integradas C++

| ID | Capacidad/caso | Comparación obligatoria | Estado |
|---|---|---|---|
| B01 | H1 native | once labels -5..5; hub correcto y firma exacta | APROBADA: barrido dirigido -5..5 |
| B02 | H1 controles | reversed, target absent, guardas de dominio | APROBADA |
| B03 | H1 backend | preparación idéntica Dense/Lazy: RAW+clock exactos | APROBADA |
| B04 | H2 separado | K=3 y K=7, respuestas individuales y presupuesto | APROBADA: K=3/K=7 y presupuesto explícito |
| B05 | H2 solapado | merge conjunto, pérdida de identidad individual, off-fiber | APROBADA |
| B06 | H2 persistencia | vector de canales/labels y futuro tras restore | APROBADA: separado/solapado en ambos sentidos; regresión metadata merge t14→stop t16 |
| B07 | H3 tratamiento | dos geometrías N=31, fresh function 2/2 | APROBADA |
| B08 | H3 controles | untrained, reset, absent, path cut, offpath, wrong receiver | APROBADA |
| B09 | H3 Dense/Lazy | estado y lectura funcional exactos en preparación idéntica | APROBADA |
| B10 | H3 persistencia | fase del protocolo, daño opt-in y futuro exacto | APROBADA; cruce de proceso C++↔Python |
| B11 | H4 pureza | analizar no cambia inputs ni `Runtime` alguno | APROBADA por API pura y pruebas C++/Python |
| B12 | H4 consistencia | pares comparables y procedencia; rechazos incoherentes | APROBADA |
| B13 | F1 panel | seis secuencias congeladas; checkpoints t34/38/46/50/58 | APROBADA |
| B14 | F1 controles | sham/no-trained/individual/order intermedio-terminal | APROBADA |
| B15 | F1 backend/restore | RAW+clock Dense/Lazy y continuidad desde mitad | APROBADA; cruce de proceso C++↔Python |
| B16 | F2 panel | seis cadenas y contadores overflow congelados | APROBADA: seis cadenas y overflow `{1,0,1,1,0,1}` |
| B17 | F2 causalidad | ambiente t38/t39, 23→24, corte/subumbral/no-query/sham | APROBADA: `environment_load` `{19664,15515,19664,19664,19663,19664}`, admisión `{true,true,false,true,true,true}` y 23→24 |
| B18 | F2 backend/restore | checkpoints causalmente decisivos y futuro exacto | APROBADA; cruce de proceso C++↔Python |
| B19 | F3 no exportado | catálogo/binding carecen de API fan-out; fixture 4149/4151→67/67 | APROBADA como evidencia negativa/no API |

## C. API, catálogo y compatibilidad

| ID | Prueba | Criterio | Estado |
|---|---|---|---|
| C01 | IDs/versiones | seis IDs públicos exactos y versión constructor explícita | APROBADA |
| C02 | dominio | rangos inválidos fallan antes de mutar | APROBADA en guardas ejercitadas |
| C03 | H3 opt-in | ninguna llamada inocua aplica daño | APROBADA |
| C04 | H4 modalidad | diagnóstico no aparece como órgano físico ni mutador | APROBADA |
| C05 | compatibilidad 2.x | APIs/aliases heredados conservan semántica | APROBADA por regresión 17/17 |
| C06 | snapshots legacy | v1/v2 se leen según contrato; no se inventan metadatos | APROBADA |
| C07 | corrupción/rechazo | restore fallido no daña mundo vigente | APROBADA |
| C08 | versión de protocolo | H1/H2/H3/F1/F2 rechazan checkpoint con versión ausente o incompatible; H2 conserva modo | APROBADA |

## D. Wheel y paridad Python

| ID | Prueba | Criterio | Estado |
|---|---|---|---|
| D01 | build wheel | nombre `dee_thinking-2.2.0-cp313-cp313-win_amd64.whl` real | APROBADA; 465.442 bytes post-corrección |
| D02 | instalación limpia | instala wheel no editable sin compilar | APROBADA (`--no-index --no-deps`) |
| D03 | aislamiento | import desde fuera del source; no `PYTHONPATH`; no kernel viejo | APROBADA |
| D04 | identidad | `__version__`, metadata, módulo nativo y plataforma coherentes | APROBADA |
| D05 | Runtime Python | config, events, receipts, advance/run_until, observe/probe | APROBADA, suite Python 11/11 |
| D06 | control Python | advance(0), pausa, forks, dos instancias, rechazos | APROBADA, suite Python 11/11 |
| D07 | snapshots Python | save/load/restore y errores claros | APROBADA, suite Python 11/11 |
| D08 | catálogo/composición | contratos, build compartido y entradas por puerto | APROBADA, composición funcional y snapshot |
| D09 | H1–H4 Python | tratamiento y controles representativos por API pública | APROBADA representativa |
| D10 | F1/F2 Python | paneles y checkpoints representativos por API pública | APROBADA representativa |
| D11 | exactitud C++/Python | RAW, clock, recibos y lecturas iguales | APROBADA: Runtime y H1/H2-separado/H2-solapado/H3/F1/F2 exactos en ambos sentidos |
| D12 | GIL/concurrencia | GIL retenido en llamadas Runtime; sin callbacks Python en workers; DenseParallel interno exacto | APROBADA por binding/build_info y regresión nativa |

## E. Persistencia cruzada y consumidor

| ID | Prueba | Criterio | Estado |
|---|---|---|---|
| E01 | C++→Python | C++ guarda con evento pendiente; Python carga y futuro coincide | APROBADA: RAW+clock+recibos tick 6 |
| E02 | Python→C++ | Python guarda; consumidor C++ carga y futuro coincide | APROBADA: RAW+clock+recibos tick 6 |
| E03 | consumidor instalado | headers/libs de install tree; no incluye `.cpp` ni Python | APROBADA por `find_package` |
| E04 | protocolos desde consumidor | al menos una capacidad nueva + snapshot/restore | APROBADA: H1 y checkpoint exacto |
| E05 | independencia | árbol instalado relocable, sin rutas privadas a baselines | APROBADA en consumidor instalado |
| E06 | fase protocolar en proceso nuevo | H1/H2/H3/F1/F2: checkpoint intermedio se reanuda en otro proceso y coincide con trayectoria continua | APROBADA en ambos sentidos, RAW+clock y escalares funcionales exactos |

## F. Entrega y freeze

| ID | Prueba | Criterio | Estado |
|---|---|---|---|
| F01 | wheel dual | wheel externo e interno al ZIP byte-idénticos | APROBADA por verificador definitivo |
| F02 | ZIP manifest | abre, archivos legibles y hashes internos correctos | APROBADA por verificador definitivo |
| F03 | extracción limpia | build, consumidor y wheel funcionan desde extracción | APROBADA: `tests/x22f`, 49 targets, CTest 8/8 en 9,78 s, consumidor y wheel limpio |
| F04 | source/binarios | source, binarios, wheel, docs y tests corresponden a 2.2.0 | APROBADA por reconstrucción y metadata coherente |
| F05 | kernel | identidad v27 conservada; no cambios físicos | APROBADA en source y ZIP (`fbd819…`), distinto del hash histórico canónico `44a80f…` por su procedencia |
| F06 | freeze | SHA-256 finales calculados después del último cambio | APROBADA por cierre externo: el publicador emite las identidades finales sin insertarlas de forma autorreferencial |

## Criterios que no pueden relajarse

- Una prueba no ejecutada continúa pendiente.
- Igualdad terminal no sustituye RAW+clock por tick cuando se afirma paridad.
- Un import correcto no acredita funciones H1–H4/F1/F2.
- No se desactivan asserts, controles ni comparaciones exactas para cerrar.
- Resultados heredados pueden justificar fixtures, pero no se cuentan como
  ejecución de la biblioteca 2.2.0.
- F3 sólo verifica el límite del aparato; no aparece como capacidad pública.
