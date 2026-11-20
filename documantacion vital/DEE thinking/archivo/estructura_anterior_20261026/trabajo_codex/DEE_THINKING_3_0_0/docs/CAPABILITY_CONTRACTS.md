# Contratos de capacidades integradas — DEE thinking 2.2.0

Namespace C++: `dee::thinking::protocols`  
Header público: `dee_thinking/integrated_protocols.hpp`

Estas capacidades son protocolos/constructores/diagnósticos acotados sobre la
misma dinámica v27. No introducen etiquetas administrativas en RAW, state,
clock o s_reg. «Construido», «alcanzado» y «adquirido» son metadatos de
procedencia, no nuevos estados físicos.

## H1 — retardo relativo a posición

- ID: `delay_position_bank.core05.nrh05.v1`.
- Entrada pública: `run_delay_position`.
- Continuación: `save_delay_position_checkpoint` y
  `resume_delay_position_checkpoint`; el checkpoint conserva configuración,
  labels, RAW, clock, tick y progreso de observación del banco.
- Fuente: CORE05 NRD05/NRH05 (`run_bank`).
- Relación: para label `j`, probe llega al hub en `L+j` y target en
  `L+delta`; el kernel produce la firma conjunta exclusivamente en `j=delta`.
- Lectura: firma exacta state=1, semantic=1, dirección reducida y s_reg bajo cap;
  una llegada aislada no cuenta como coincidencia.
- Dominio 2.2.0: N=59, `L=12`, labels enteros -5..5, frame cardinal ortogonal,
  fondo vacío, trayectorias positivas, sin auto-wrap durante la lectura y sin
  saturación.
- Controles obligatorios: calibración correcta, invertida, target ausente y
  guardas de dominio.
- Recursos de referencia: 22 portadores para once labels; el presupuesto,
  labels, puertos y política de solapamiento son parte del resultado.
- No afirma: tiempo físico continuo, interpolación, fondo denso ni metrología
  universal.

## H2 — repertorios separados y solapamiento

- ID: `destination_repertoires.core07.c7h02.v1`.
- Entradas públicas: `run_separated_repertoire` y
  `run_overlap_repertoire`.
- Continuación: pares `save_*_checkpoint`/`resume_*_checkpoint` para panel
  separado y solapado; la receta serializa canales/labels y fase del protocolo,
  no sólo los buffers terminales.
- Fuente: CORE07 C7H02.
- Panel separado: K pares cue/teacher entrenan K fibras destino disjuntas; una
  consulta posterior comprueba cada relación individual.
- Panel solapado: dos memorias comparten destino, producen portador/readout
  compuesto y pierden identidad bajo los decoders individuales.
- Dominio 2.2.0: panel separado reejecutado para K=3 y K=7; panel solapado en
  N=71; semantic=1, fondo vacío, tiempos ordenados, sumas bajo cap y lectura
  antes de auto-wrap. K=40 permanece antecedente histórico, no promesa de este
  build ni máximo universal.
- Controles: off-fiber con inventario comparable, identidad individual,
  presupuesto y guardas de dominio.
- Lectura transformativa: los recursos consumidos no se restauran mediante
  copias ocultas.
- No afirma replicación ni fan-out de una relación adquirida.

## H3 — reparación desde redundancia entrenada

- ID: `trained_redundancy_repair.core17.v1`.
- Entrada pública: `run_trained_redundancy_repair`.
- Continuación: `save_trained_redundancy_repair_checkpoint` y
  `resume_trained_redundancy_repair_checkpoint`, incluyendo geometría, brazo,
  autorización de daño, fase y resultados parciales.
- Modalidad registrada: `ProtocolModality::Diagnostic`; la preparación usa
  entrenamiento acoplado y el daño es una intervención diagnóstica explícita
  opt-in.
- Fuente: CORE17 C17E02/C17E03.
- Preparación: dos fuentes redundantes presentes desde t0 reciben aprendizaje
  mediante secuencias propias; no se copia RAW entre ellas.
- Intervención: la primera política transferida se daña de forma declarada; la
  segunda fuente entrenada viaja por un corredor y reconstruye función en un
  receptor compatible.
- Lectura: consulta fresh SENSOR con dirección ACTION1 transformada; función
  recuperada no implica identidad RAW microscópica.
- Dominio 2.2.0: N=31, dos geometrías transformadas y siete brazos.
- Controles: treatment, backup_untrained, backup_direction_reset, no_backup,
  path_cut, offpath_cut y wrong_receiver.
- Recursos: ambas fuentes entrenadas fueron consumidas en el aparato probado;
  persistencia/reutilización de la copia no fue demostrada.
- Daño nunca ocurre implícitamente desde `advance`, `observe`, `restore` o una
  carga de snapshot.
- No afirma: reparación espontánea local, replicación adquirida de copy2 desde
  copy1 ni autonomía sin intervenciones.

## H4 — accesibilidad finita dependiente de historia

- ID: `accessibility.history_conditioned_finite_response.v1`.
- Entrada pública: `analyze_accessibility`.
- Naturaleza: analizador puro; no es organización física ni `make_reachable`.
- Fuente: Ingenierías 03–04.5/POST, con evidencia NRD02 V1/V2/V3 y corrección
  POST P01R.
- Unidad: bajo aparato y observer congelados, comparar el efecto de un challenge
  con el baseline de **la misma historia**, no sólo estados finales de mundos
  previamente distintos.
- Entradas: pares de observaciones baseline/challenge comparables, procedencia,
  historia y definición del observer.
- Salida: contrastes y checks de comparabilidad/procedencia; no modifica un
  `Runtime` ni atribuye challenges de clones a la trayectoria fuente.
- Dominio: diagnóstico finito de la evidencia suministrada; POST conserva
  acoplamiento remoto condicionado por historia (periodo 1 frente a 2), pero no
  reinstancia la clase funcional fuente.
- No afirma: reachability universal, RW3, `refractario→competente`, planificación
  de ruta ni adquisición sólo porque dos respuestas difieren.

## F1 — revisión reutilizable de relación móvil

- ID: `reusable_lineage_revision.c7h03.v1`.
- Entrada pública: `run_reusable_revision`.
- Continuación: `save_reusable_revision_checkpoint` y
  `resume_reusable_revision_checkpoint`; conserva cola t0, recibos, fase y
  lecturas parciales para no reconstruir otra historia al reanudar.
- Fuente: laboratorio final sobre linaje C7H03.
- Modalidad: preparación externa completa en t0; después, kernel y lecturas
  pasivas. Los teachers contienen las revisiones; no son derivados por el mundo.
- Aparato: N=127; relación inicial C7H03; revisiones en t38/t50; consultas
  transformativas de carga 7/5/3 en t34/t46/t58.
- Brazos y fixtures:

| Brazo | Respuestas t34→t46→t58 |
|---|---:|
| `REV_11_13` | 4149→4165→4181 |
| `REV_13_11` | 4149→4167→4181 |
| `FIRST_ONLY_11` | 4149→4165→4168 |
| `SECOND_ONLY_13` | 4149→4154→4170 |
| `SHAM_11_13` | 4149→4154→4157 |
| `NO_TRAINED_RELATION` | 7→5→3 |

El orden aparece en la lectura intermedia (4165/4167); la lectura terminal
converge a 4181 tras la misma carga total. Los fixtures pertenecen a las
pruebas, nunca a la implementación del resultado.

- No afirma streaming arbitrario, autoenseñanza, derivación endógena de 11/13,
  memoria ilimitada ni aprendizaje universal.

## F2 — mediación ambiental DEMUX

- ID: `environmental_demux_return.v1`.
- Entrada pública: `run_environmental_return`.
- Continuación: `save_environmental_return_checkpoint` y
  `resume_environmental_return_checkpoint`; conserva fase, cola, overflow
  acumulado y checkpoints ya observados.
- Fuente: laboratorio final F2.
- Modalidad: preparación completa en t0; fase, sesgo, receptor y soportes son
  condiciones iniciales declaradas.
- Aparato: N=127; respuesta upstream, sesgo 15515, seis soportes semantic=4 de
  carga cero, clock/fase preparados, destino DEMUX y portador independiente 23.
- Mecanismo: la respuesta lleva el receptor a 19664; la transición siguiente
  alcanza overflow y DEMUX aplica `+1` al portador independiente (23→24). El
  portador se usa luego en t43/t47/t51/t55.
- Fixtures:

| Brazo | overflow | Cadena t39→t43→t47→t51→t55 |
|---|---:|---:|
| `ENV_INTACT` | 1 | 24→55→62→62→67 |
| `ENV_RESPONSE_CUT` | 0 | 23→54→61→61→66 |
| `ENV_NO_QUERY` | 1 | 0→31→7→0→5 |
| `ENV_QUERY_SHAM` | 1 | 0→31→7→0→5 |
| `ENV_SUBTHRESHOLD` | 0 | 23→54→61→61→66 |
| `ENV_CONTENT_19` | 1 | 24→55→62→62→67 |

`ENV_RESPONSE_CUT` desvía el teacher inicial; no es un corte tardío de una
respuesta ya formada. El control subumbral cambia el sesgo a 15514. No-query y
sham conservan overflow, pero no actualizan la ruta funcional.

- No afirma teacher arbitrario, conservación universal de s_reg, cierre
  indefinido, sostenibilidad ilimitada ni autoenseñanza general.

## F3 — evidencia conservada, no API pública

F3 no tiene ID ni función pública de replicación. En el aparato F2, contenidos
upstream 4149 y 4151 saturaron en el mismo umbral y produjeron la misma salida
24→55→62→62→67. El resultado controla la pérdida de especificidad de contenido
en ese gate; no prohíbe otras arquitecturas DEE.

## Cobertura técnica ejecutada

| Contrato | Ejecución del corte 2.2.0 | Límite de la cobertura |
|---|---|---|
| H1 | C++ native/reversed/target-absent, once delays -5..5, Dense/Lazy, checkpoint; wheel Python native+checkpoint; consumidor instalado; cruce bidireccional exacto | fuera de -5..5 no se publica como validado localmente |
| H2 | C++ K=3/K=7 con presupuesto, solapamiento/off-fiber, Dense/Lazy y checkpoints de ambos modos; wheel Python y cruce bidireccional exacto | K>7 no se publica como validado localmente |
| H3 | dos geometrías × siete brazos C++ Dense/Lazy; opt-in; checkpoint; wheel y persistencia C++↔Python | no prueba creación de la copia redundante a partir de la primaria |
| H4 | comparabilidad/pureza C++ y diagnóstico Python | analiza evidencia suministrada; no ejecuta de nuevo 03–04.5/POST |
| F1 | seis brazos C++, DenseParallel/Lazy, checkpoint; wheel y persistencia bidireccional | teachers preparados en t0; no autoenseñanza |
| F2 | seis cadenas C++, `environment_load`, overflow y admisión por brazo, DenseParallel/Lazy, checkpoint; wheel y persistencia bidireccional | preparación de fase y DEMUX +1 finito; no teacher arbitrario ni sostenibilidad indefinida |
| F3 | fixture 4149/4151→67/67 y ausencia de ID/API pública | evidencia negativa de este gate, no capacidad exportada ni imposibilidad general |

La suite nativa completa informó 17/17 y la suite del wheel 11/11. Esta tabla
describe qué ejercitaron, no amplía los dominios científicos anteriores.

## Contrato común de errores y estado

- Parámetros, cargas, signos, dimensión, labels y tiempos se validan antes de
  mutar un mundo.
- H3 restringe su API estable a las dos geometrías N=31 congeladas y siete
  brazos enumerados. En F1/F2, el identificador del brazo y su tupla física
  forman una sola configuración: una combinación válida con etiqueta
  contradictoria se rechaza para impedir telemetría mal rotulada.
- Un rechazo de dominio es una excepción clara; un rechazo ordinario de una
  experiencia sigue representado por `EventReceipt`.
- uint64 de RAW/clock no pasa por `float` en el binding Python.
- Los resultados contienen telemetría calculada por C++; Python no recalcula la
  dinámica ni elige retrospectivamente un receptor.
- `integrated_protocol_descriptors()` y `find_integrated_protocol(id)` exponen
  versión 1.0.0, modalidad, fuente, dominio, límites, presupuesto, puertos y
  labels. Es un registro público de protocolos; H4 no se hace pasar por una
  organización física del `OrganizationCatalog`.
- Los protocolos finitos devuelven sus brazos, controles y checkpoints; no
  convierten una salida favorable en dictamen científico global.
