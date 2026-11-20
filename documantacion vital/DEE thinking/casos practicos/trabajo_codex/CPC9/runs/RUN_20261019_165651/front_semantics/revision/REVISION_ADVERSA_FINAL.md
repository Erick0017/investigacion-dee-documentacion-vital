# Revisión adversa final: atribución, causalidad y horizontes

Corte leído: 2026-10-19, aproximadamente 19:36 UTC. Revisión sólo de lectura;
no se modificaron archivos del responsable, participantes ni estados. No se
ejecutaron simulaciones nuevas. Se leyeron las tres matrices solicitadas, los
tres primarios de auditoría y sus programas; se contrastaron registros concretos
con el MAIN y con los controles pertinentes. No constituye una auditoría total
de todos los bytes del expediente ni sustituye la extracción limpia.

Resultado: **ninguna contradicción física bloqueante encontrada** en las
trayectorias revisadas. Hay dos ambigüedades documentales de severidad media que
conviene corregir antes de sellar. No justifican borrar resultados positivos ni
cambiar el evaluador físico.

## Hallazgos documentales

### M1 — Media: dos matrices A–J con estados distintos en cada entrada

Localizador: `revision/NSM65_EVIDENCIAS.json#/entries/*/dimensiones_A_J` frente a
`#/entries/*/dimensions_A_J`. Las 65 entradas conservan el primer bloque con
`PENDIENTE_DE_ADJUDICACION_CPC9`; el segundo contiene la adjudicación final.
Por ejemplo, TWO, entrada12, figura simultáneamente pendiente y con asociación,
uso y retención positivos. Es legítimo conservar el plan anterior, pero falta
identificar inequívocamente qué bloque es histórico y cuál es normativo actual.

Relacionado: ONE, entrada11, tiene `auxiliary_level=E2_LIMITADO`, pero el texto
genérico de `manual_assessment_scope` dice que no se reclama adquisición de
esta primitiva y `dimensions_A_J/B,D,E` contiene negaciones sin sufijo E1.
THERE_IS y NOT, entradas35/57, conservan positivos históricos asistidos con la
misma plantilla negativa no contextualizada. Los campos `E1_level` y los
dominios históricos permiten reconstruir la intención, pero una lectura plana
puede borrar esos positivos o mezclarlos con E1.

Recomendación documental: nombrar explícitamente el bloque heredado como plan
inicial y el adjudicado como dimensiones de E1-CPC9; precisar «no demostrado en
E1-CPC9» en la plantilla negativa. Conservar las adjudicaciones AUX/históricas
por separado, sin elevarlas ni eliminarlas.

### M2 — Media: localizador del catálogo no resuelto desde la raíz

Localizador: `revision/NSM65_EVIDENCIAS.json#/catalogue/path` contiene
`referencias/NSM65_CATALOGO_4_5.json`, que no existe bajo la raíz CPC9 revisada.
Sí existe `front_semantics/referencias/NSM65_CATALOGO_4_5.json`, con la identidad
esperada. La selección del paquete debe comprobar si incluye ese directorio;
no basta con que exista en el laboratorio. El catálogo también es recuperable
del WHL, pero esa alternativa debe tener un localizador explícito.

Recomendación: incluir una copia exacta única y ajustar el localizador, o
documentar el recurso exacto dentro del instrumento y su recuperación. No hay
señal de inventario NSM falso: son 65 entradas y el hash de referencia se declara.

### B1 — Baja: explicitar por qué G/H positivos no elevan el nivel resumen

Localizadores: `NSM65_EVIDENCIAS.json#/entries/42/dimensions_A_J/G`,
`#/entries/56/dimensions_A_J/G,H` y `#/summary/no_E4_E5_global_primitive_awards`.
No es una contradicción conservar G/H funcionales positivos y un E2 resumen si
faltan los contrastes de contenido, papeles o combinación reservada exigidos.
Conviene decir exactamente cuál falta. «No hay gramática productiva universal»
no sería por sí solo razón suficiente para negar una composición funcional
finita: el criterio E4 no exige universalidad. No se recomienda una promoción
automática; sí una explicación que respete las dimensiones independientes.

### B2 — Baja: enlazar los nuevos controles directamente desde la síntesis

Localizador: `revision/INTEGRACION_CAUSAL.json#/native_chains/0` remite al MAIN,
pero aún no al nuevo primario `resultados/auditoria/COMPOSICION_E1/MEDICIONES.json`.
Los testigos NSM usan además la cobertura genérica «tick/localizer described in
CALCULOS/front reports». Las rutas y hashes permiten revisión, pero añadir los
punteros concretos facilita comprobar la afirmación causal sin búsquedas largas.

## Contrastes físicos que sí sostienen las afirmaciones limitadas

### Composición nativa, no mera suma de una pantalla

Primario: `resultados/auditoria/COMPOSICION_E1/MEDICIONES.json`.
`/native_branch`, `/incoming` y `/actual_formed206` conservan dos llegadas reales
de cargas26 y30 que producen carga56, dirección[1,1,1], mediante `EMPTY_DEMUX_2`;
la reconstrucción RAW/clock coincide exactamente.

En `/rows/0` y `/rows/1`, retirar selectivamente cada llegada conserva la otra
y elimina el uso previsto: la salida conjunta posterior no es la del sham.
En `/rows/2` y `/rows/3`, conservar carga56 pero borrar X o Z también elimina
esa función. En `/rows/4`, el sham reproduce todo RAW/clocks hasta884. Por
ejemplo, el sham entrega68/[0,1,0] a214 y75/[0,1,1] a281; los cuatro controles
entregan5/[-1,1,-1] a214 y7/[0,0,1] a281. Los padres permanecen inalterados.

Esto sostiene composición física funcional y necesidad de las dos contribuciones
y de su dirección en ese aparato. No demuestra por sí solo ligamiento general
de referentes ni una gramática semántica. La atribución de cada corriente a
orden/contacto debe conservar sus fuentes y controles previos: no se infiere
genealogía exclusivamente por igualdad de carga o proximidad.

### Memoria tardía utilizada:2283, no sólo un resto visible

Primario: `resultados/auditoria/MEMORIAS_TARDIAS_2283_R1/MEDICIONES.json`.
En `/reference`, `/object` y `/reader` están los operandos36/16 y lector7 a2282.
`/rows/2` cambia sólo la carga de la referencia a5 y produce7/[-1,0,0];
`/rows/3` la cambia a16 y produce7/[0,0,0] activo; `/rows/4` conserva36 y
produce7/[1,0,0], con estado completo igual al MAIN. Los cuatro renglones
certificados reconstruyen RAW/clocks exactamente; los padres no cambian.
Esto es evidencia de utilización causal tardía de la referencia, no sólo de
que el auditor encuentra una carga antigua.

Límite importante, correctamente preservado: `/rows/1` (`cut_reader`) tiene
`branch_exact=false` y `NOT_CERTIFIED_PENDING_CURRENT_INPUT`. La sonda pendiente
a2282 se aplica al vaciar el puerto y repone el lector. No sirve para concluir
que el lector sea innecesario ni para anunciar «5/5 reconstrucciones locales».
Hay4/4 renglones certificados más1 diagnóstico con entrada actual omitida del
preestado pasivo. La V1 fallida se conserva y se explica; no se maquilló.

La referencia54→67 y los operandos36/16 son preparaciones cuantitativas distintas
dentro de E1. Ambos resultados positivos se conservan, pero la retención de los
segundos no debe citarse como única prueba de retención de la primera: ésta
tiene sus propias comparaciones reservadas1008/1075/1142.

### Nacimiento local y crecimiento de ocupación

Primario: `resultados/auditoria/CRECIMIENTO_OCUPACION/MEDICIONES.json`.
`/first_birth` reconstruye exactamente `EMPTY_XNOR` en2292 desde el vecindario
2291, y `/rows/0` elimina ese nacimiento local retirando un miembro; el sham
`/rows/1` reproduce el estado completo original a2353.

El corte **no detiene la ocupación global**: quedan297971 sitios ocupados frente
a298024 en el sham; semantic7 queda5714 frente a5768. No acredita que ese primer
nacimiento sea causa única o necesaria de toda la onda. El propio protocolo no
lo presupone. El perfil mide ocupación/semántica del kernel, no energía eléctrica,
conciencia ni un máximo universal de65 relaciones. No había entrada solicitada
a2291 en el primario MAIN consultado.

## Continuidad y alcance semántico

`VIDA_PRINCIPAL.json` distingue una preparación, seis continuaciones y siete
fases serializadas de E1, N67 fijo, con padres y estados físicos enlazados. Las
nuevas interfaces1220/1907 se declaran instrumentales, sin material añadido ni
crecimiento cognitivo nativo atribuido. No se encontró suma de individuos AUX
como si fueran conocimientos del MAIN.

La cláusula temporal final NSM es adecuada: los cinco IDs operacionales son
máximos positivos dentro de sus horizontes, **no cinco conocimientos disponibles
hasta2493**. La cola final tiene177/178 solicitudes rechazadas por ocupación y
la lectura TM final es semantic7/carga1/dirección0. Eso impide afirmar acceso
funcional tardío y no demuestra por sí solo destrucción de toda la memoria.
MORE E3 se sostiene como transferencia cuantitativa finita de referencia adquirida
y revisada frente a objetos nuevos, con comparador preparado declarado; no como
aprendizaje de la ley comparativa o dominio de la palabra MÁS.

## Identidad de los archivos revisados

Estos hashes identifican este corte; si el responsable corrige los documentos,
debe volver a comprobar las observaciones documentales aplicables. No se trata
de vetar una corrección posterior ni de modificar evidencias selladas.

- NSM65_EVIDENCIAS.json: `b8044d1fe21193087d34cc5fe7d9bdbbab78cc9f82140df5d3b7a608365ae900`.
- INTEGRACION_CAUSAL.json: `849adbfd3c88583fc1773b2a3659693abcff8b22457b5da1d75f14e00d555459`.
- VIDA_PRINCIPAL.json: `73fcb6a384854ded42b723e9a8318c38d9914bbd811d1fbeac7bd9a257ff3778`.
- COMPOSICION_E1/MEDICIONES.json: `ce8baacc95001750302ee3826d3dfc8902b1ec691f15bc5b7114b96bc84e2c54`.
- MEMORIAS_TARDIAS_2283_R1/MEDICIONES.json: `24cd63bfae676e54f4539b680023a15b1ddf645b26908f97d8058ed77e78e70b`.
- CRECIMIENTO_OCUPACION/MEDICIONES.json: `9031c85fa7d278f9adb52bce333565328c79d3414a7a25dd3288e52103594d9d`.

## Comprobación posterior de las correcciones documentales

A19:38 UTC se volvió a leer el NSM corregido, SHA-256
`671b56668679aff86ce23cc3321c78c98b1a21a2a558ccaa158d1fbf20668789`.
Los dos hallazgos medios principales quedan **resueltos**:

- Las65 filas distinguen `planned_dimensions_not_results`; no queda ninguna
  `dimensiones_A_J` pendiente confundible con la adjudicación actual.
- `catalogue.path` apunta ahora a `genealogia/NSM65_CATALOGO_4_5.json`, archivo
  existente con SHA-256 exacto
  `e0f29290d800a74150b7e386fe2437dcc92b99bbd587b6cfef8e38c80067ae7e`.

La frase genérica negativa de ONE y otros E0 aún puede precisarse como «en E1»;
con el campo E1_level y los positivos AUX/históricos separados, queda como
mejora menor de claridad, no contradicción bloqueante. No se detectó otro
bloqueante en el alcance revisado. Se preservan arriba los hallazgos originales
y sus hashes para dejar auditable la corrección.
