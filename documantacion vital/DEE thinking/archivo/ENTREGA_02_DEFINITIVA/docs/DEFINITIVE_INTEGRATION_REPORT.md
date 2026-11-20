# DEE thinking 2.2.0 — informe de integración definitiva

Proyecto científico: DEE Universe  
Producto: DEE thinking  
Autor: Ivan Erick Tlaltecatl Morales  
Kernel físico: DEE v27 congelado

## Estado de este documento

Este informe describe el corte autorizado de Entrega 02. Los estados de prueba
se actualizan únicamente a partir de ejecuciones conservadas en `validation/`.
La existencia de una fila o de código fuente no equivale a una prueba aprobada.

La versión fijada para este corte es **2.2.0**. Es un incremento
minor respecto de 2.1.0 porque añade interfaces públicas H1/H2/H3/H4/F1/F2 y
el primer paquete Python nativo; el kernel continúa siendo v27. Antes del freeze,
`2.2.0` debe coincidir en CMake, metadatos Python, `__version__`, catálogo,
README y wheel. El manifest se genera al congelar el ZIP.

## Bases utilizadas y procedencia

| Paquete | SHA-256 comprobado en esta sesión | Aporte al corte |
|---|---|---|
| `DEE_thinking_ENTREGA_02_RESULTADOS.zip` | `b3d31cbee36f765456da7ee610c949193a8b888a140fa017ae3f535414218f0f` | API/runtime/composición de Entrega 02, producto 2.0.0 |
| `DEE_thinking_ENTREGA_02_CIERRE_Y_FRONTERA_RESULTADOS.zip` | `532b195e2931c693f343ea782f399fd8b546f461f2e604f7b8c2b264c63e1c80` | cierre 2.1.0: memoria temporal CORE05, fixtures microscópicos, schedulers y persistencia |
| `DEE_thinking_ENTREGA_02_PREINTEGRACION_RESULTADOS.zip` | `445aed27f692698675d8d9bcc336018cd9109bdae52b87beb68d6f9b6cffe3c8` | árbol fuente completo heredado y ports aislados H1/H2/H3/H4 |
| `DEE_thinking_ENTREGA_02_LABORATORIO_FINAL_RESULTADOS.zip` | `b2038711f0a8443bc1c155384e5bfc7fce7516be7b755a52c9cd936c9f8a14d0` | runner, configuración, controles y telemetría F1/F2; evidencia negativa F3 |

La base fuente de 2.2.0 procede del árbol completo de preintegración, no de la
biblioteca estática del laboratorio final. La evidencia F1/F2 se incorpora
como fixtures y contratos; no convierte el `.lib` histórico en dependencia del
producto nuevo. El wheel canónico `dee_universe_v27` permanece sólo como
referencia externa para dominios diferenciales, no como dependencia de
ejecución de `dee_thinking`.

Identidad física heredada:

- source canónico v27 SHA-256:
  `44a80f7863d78f596099ddf7d41c9947fa8513503f65067097f1f3b05a8207ab`;
- copia C++ portada `src/kernel_v27.cpp` heredada de preintegración y
  comprobada byte a byte en este árbol: SHA-256
  `fbd8190381ed76085f404e6578ff15fe185ab66cd48c67300d2abad61ddc7e31`;
- wheel oficial v27 SHA-256:
  `69297e6f06761c8b2f65d24a3fd7a2f16a3f67595a7f9660739ab65f47abc939`;
- `P_KERNEL=19665`; cap del reducer/DEMUX `19664`.

Los hashes `44a80f…` y `fbd819…` identifican artefactos de procedencia distintos:
el primero es la fuente canónica histórica; el segundo, la implementación C++
portada del producto. No deben intercambiarse ni presentarse como discrepancia
de la ley sin comparar sus contratos de empaquetado y envoltorio.

## Alcance autorizado

Las seis capacidades siguientes se integran con los límites documentados en
`CAPABILITY_CONTRACTS.md`:

| Línea | ID público 2.2.0 | Naturaleza | Dominio publicado |
|---|---|---|---|
| H1 | `delay_position_bank.core05.nrh05.v1` | constructor/protocolo retardo relativo → posición | banco local N=59, labels -5..5 y controles congelados |
| H2 | `destination_repertoires.core07.c7h02.v1` | protocolos de repertorio separado y solapado | K=3 y K=7 reejecutados; K=40 sólo antecedente histórico |
| H3 | `trained_redundancy_repair.core17.v1` | protocolo acoplado/diagnóstico con daño opt-in | N=31, dos geometrías y siete brazos causales |
| H4 | `accessibility.history_conditioned_finite_response.v1` | analizador finito, puro | pares baseline/challenge comparables bajo observer congelado |
| F1 | `reusable_lineage_revision.c7h03.v1` | protocolo finito de revisión suministrada | N=127, revisiones t38/t50 y consultas t34/t46/t58 |
| F2 | `environmental_demux_return.v1` | composición finita de mediación ambiental | N=127, fase preparada y cadena t39/t43/t47/t51/t55 |

F3 no se publica. En el aparato probado, dos contenidos upstream distintos
(4149 y 4151) convergieron en el mismo evento de umbral y en la misma secuencia
downstream. Esto queda como regresión negativa del aparato F2, no como una
imposibilidad general de fan-out en DEE.

## Qué permanece heredado

El corte 2.2.0 debe conservar sin cambio de significado: `Runtime` persistente,
eventos y recibos, `observe` pasivo, `probe` interventivo, pausa/reanudación,
snapshots v1/v2, forks profundos, catálogo, composición en mundo compartido,
DenseSequential/DenseParallel/Lazy, transporte, aprendizaje relacional,
actualización, memoria relativa, contexto distribuido, integración multicanal,
recurrencia finita y memoria temporal CORE05.

Los 15 targets Release aprobados en el cierre 2.1.0 son evidencia heredada. No
se presentan como una corrida nueva de 2.2.0; la integración debe volver a
ejecutar la matriz pertinente y conservar sus logs.

## Riesgos técnicos que deben cerrarse antes del freeze

1. **Coherencia de versión.** Ningún archivo de identidad activa, metadata de
   paquete, README vigente ni binario de 2.2.0 puede conservar 2.1.0 o describir
   el producto actual como «preintegración». Los informes históricos conservan
   deliberadamente sus versiones y estados originales como procedencia.
2. **Núcleo único.** Biblioteca C++ y extensión Python deben compilar los mismos
   `src/*.cpp`; el binding no puede enlazar una `.lib` histórica por ruta
   absoluta ni importar `dee_universe_v27`.
3. **Persistencia de protocolos.** H1/H2/H3/F1/F2 exponen checkpoints. Su fase,
   configuración, estado físico y entradas pendientes pertinentes deben
   sobrevivir, y H1/H2/H3/F1/F2 requieren al menos una comprobación en proceso
   nuevo.
   Un restore del `Runtime` genérico no acredita por sí solo la fase protocolar.
4. **H3 interventivo.** El daño sólo puede ejecutarse mediante opt-in explícito;
   nunca desde `advance`, `observe` o `restore`.
5. **H4 diagnóstico.** El analizador no puede editar el mundo ni convertir un
   challenge en evidencia de la trayectoria fuente.
6. **GIL y concurrencia.** Si el binding libera el GIL durante `advance`, debe
   conservar la vida del objeto y rechazar mutaciones simultáneas del mismo
   mundo. Liberar el GIL no hace thread-safe a `Runtime`.
7. **Paridad real.** Importar el wheel no basta: H1–H4/F1/F2 deben invocar C++
   real desde una instalación no editable y fuera del árbol fuente.
8. **Wheel autocontenido.** Instalarlo no debe requerir el árbol de desarrollo,
   el wheel v27 histórico ni un compilador.
9. **Cruce C++/Python.** La persistencia en ambas direcciones debe comparar el
   futuro contra una trayectoria no interrumpida, incluyendo eventos pendientes.
10. **F2 no genérico.** DEMUX aporta `+1`; el contrato no debe ofrecer un
    teacher arbitrario, autoenseñanza general ni sostenibilidad indefinida.

## Validación ejecutada del corte 2.2.0

Después de corregir y volver a compilar el wrapper de checkpoint H2-overlap, el
corte candidato del 4 de octubre de 2026 ejecutó estos recorridos:

- build Release limpio y CTest: **17/17**, 820,79 s;
- consumidor externo configurado con `find_package` contra el install tree:
  organizaciones=2, entrada posterior admitida, restore autocontenido y futuro
  de backend exacto, memoria CORE05 y H1 con checkpoint exacto, registro=6;
- wheel real
  `dee_thinking-2.2.0-cp313-cp313-win_amd64.whl`, 465.442 bytes, SHA-256
  provisional `39e6bc7cb8a6be74bfe105ae9e284eff4d3a4cc213780f410a048d3fd75301c6`;
- instalación no editable, sin índice ni dependencias, en un venv CPython 3.13
  nuevo y desde un cwd externo: import nativo 2.2.0, kernel 27, tag
  `cp313-cp313-win_amd64`, sin cargar `dee_universe_v27`;
- suite Python pública: **11/11**, 29,457 s, incluyendo el dominio H1 -5..5,
  presupuesto K=7 de H2 y los seis valores ambientales, overflow y admisión de
  F2;
- persistencia genérica C++→Python y Python→C++: RAW, clock y recibos exactos a
  tick 6 con evento pendiente;
- checkpoints H1, H2-separado, H2-solapado, H3, F1 y F2 en ambos sentidos y
  procesos separados: RAW, clock y escalares funcionales exactos frente a la
  trayectoria ininterrumpida; H3 reconstruyó la función, F1 produjo
  4149→4165→4181 y F2 24→55→62→62→67.

`validation/FINAL_VALIDATION_SUMMARY.json` conserva los estados automáticos y
los datos anteriores. El SHA citado identifica el wheel usado para formar y
probar el candidato; la copia externa definitiva y la interna se verifican
byte-idénticas al publicar, y la identidad final se emite fuera del ZIP para no
crear una referencia circular.

El cruce H2-solapado localizó un defecto de envoltorio: un checkpoint detenido
en t16 conservaba RAW/clock exactos pero capturaba la metadata funcional de
merge sólo cuando el stop coincidía con t14. Se movió exclusivamente la captura
de metadata a la frontera física t14; no cambió el kernel ni la trayectoria.
La reproducción posterior informó `exact_state=true` y `merge=true`, y todo el
panel anterior se repitió tras esa corrección. El wheel previo de 465.308 bytes
y sus corridas quedan como diagnóstico supersedido, no como artefacto del
freeze.

La auditoría de cobertura mantiene separada una suite aprobada de una inferencia
no ejecutada: el corte post-corrección recorre explícitamente H1 -5..5, K=7 y
los campos ambientales/overflow/admisión de los seis brazos F2. Esa cobertura
es la ejercitada por el test; no amplía por sí sola el dominio científico del
contrato.

## Criterio de aceptación del corte

El estado `ENTREGA 02 DEFINITIVA VERIFICADA` sólo puede escribirse después de
que toda fila obligatoria de `TEST_MATRIX_DEFINITIVE.md` tenga evidencia
ejecutada y trazable, el consumidor C++ use la instalación, el wheel se instale
limpiamente, la copia externa y la interna del wheel sean byte-idénticas, y el
ZIP se reconstruya y pruebe desde una extracción limpia.

## Verificación desde extracción limpia

El ZIP candidato se extrajo en `tests/x22f`, sin usar el árbol de desarrollo.
Desde esa extracción se reconstruyeron 49 targets; un panel dirigido CTest
informó **8/8** en 9,78 s (`kernel_whl_differential`, `runtime_contract`,
`execution_backends`, `composition_snapshot_restore`, `core05_phase_memory`,
`cross_process_persistence`, `examples_smoke` e `integrated_protocols_e2e`).
Después se instaló el árbol nativo y un consumidor externo configurado por
`find_package` confirmó H1, checkpoint exacto y registro de seis protocolos.
El mismo source extraído reconstruyó correctamente el wheel en
`tests/xwheel22f/dee_thinking-2.2.0-cp313-cp313-win_amd64.whl`.

**Estado técnico del freeze:** `VERIFIED`. Build completo 17/17, consumidor,
wheel instalado, API Python, cruces C++↔Python y reconstrucción desde ZIP tienen
evidencia favorable. La publicación calcula las identidades del ZIP y wheel
después del último cambio y no inserta un hash autorreferencial dentro del ZIP.
Este estado técnico no constituye un dictamen científico.
