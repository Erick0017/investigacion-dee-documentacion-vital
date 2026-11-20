# Informe integrado — laboratorio final focalizado de Entrega 02

Proyecto: DEE Universe  
Producto: DEE thinking  
Autor: Ivan Erick Tlaltecatl Morales  
Kernel: DEE v27 congelado

## Alcance y procedencia

El trabajo partió del paquete
`DEE_thinking_ENTREGA_02_PREINTEGRACION_RESULTADOS.zip`, SHA-256
`445aed27f692698675d8d9bcc336018cd9109bdae52b87beb68d6f9b6cffe3c8`.
Se usó la biblioteca heredada, no se cambió el catálogo estable y no se
publicó ningún candidato.

La revisión fue dirigida. Se consultaron el informe y el código de la
preintegración, el catálogo y sus pruebas C7H03, el runner primario
`run_native_consequence_reprogramming.py`, el receptor histórico de s_reg,
las pruebas de memoria de fase CORE05 y la implementación C++ de la transición
v27. No se releyó ni reejecutó todo el corpus.

El aparato reutiliza el linaje C7H03 ya respaldado:

1. cue 4083 y teacher 19 producen 4102 en t5;
2. la consecuencia 23+17 produce 40 en t8;
3. 4102+40 produce la relación móvil 4142 en t12;
4. una consulta común de carga 7 produce 4149 en t34.

Esta herencia no se presenta como resultado nuevo.

## Modalidad experimental

Todos los portadores de cada mundo fueron admitidos en la frontera t0. Después
de esa frontera el mundo principal recibió sólo ticks v27 y observación pasiva.
Las experiencias y recursos posteriores estaban físicamente presentes desde
t0; por ello son una preparación externa declarada, no decisiones endógenas
del host ni entradas aplicadas durante la trayectoria.

El runner es C++ nativo y no usa Python. Se ejecutaron seis brazos F1 y seis
brazos F2/F3 en Lazy, más cuatro confirmaciones DenseParallel. Total final:
16 ejecuciones backend/caso terminadas y ninguna parcial científica. El tiempo
interno del runner final fue 473,339 ms.

## F1 — revisión reutilizable de una misma relación

### Pregunta

¿Puede un mismo linaje móvil recibir dos experiencias de revisión separadas,
conservarlas y utilizarlas en consultas posteriores comunes, sin reconstruir
la memoria por episodio?

### Preparación y controles

Después de la consulta común t34 se colocaron dos encuentros de revisión en
t38 y t50. Cada revisión tenía un portador on-path y un portador sham paralelo
a z+3. Tratamiento y sham conservaron posiciones de origen, estados,
direcciones y número de portadores; sólo intercambiaron qué carga viajaba por
la ruta funcional. Las consultas comunes fueron 7, 5 y 3 en t34, t46 y t58.

Se compararon:

- revisiones 11→13;
- las mismas cargas en orden 13→11;
- sólo la primera revisión;
- sólo la segunda;
- ambas cargas fuera de ruta con redirecciones on-path de carga cero;
- teacher inicial desviado, conservando el recurso pero sin formar la relación.

### Mediciones

| Brazo | respuestas t34→t46→t58 | estados después de revisión t38→t50 |
|---|---:|---:|
| REV_11_13 | 4149→4165→4181 | 4160→4178 |
| REV_13_11 | 4149→4167→4181 | 4162→4178 |
| FIRST_ONLY_11 | 4149→4165→4168 | 4160→4165 |
| SECOND_ONLY_13 | 4149→4154→4170 | 4149→4167 |
| SHAM_11_13 | 4149→4154→4157 | 4149→4154 |
| NO_TRAINED_RELATION | 7→5→3 | 11→13 |

Las dos revisiones actuaron sobre el mismo linaje. No se instaló otra memoria,
no se restauró un snapshot y no se eligió un receptor por resultado. Invertir
11 y 13 cambió la respuesta intermedia (4165 frente a 4167), pero ambos órdenes
convergieron a 4181 después de acumular la misma carga total. Por tanto, en este
aparato la respuesta intermedia conserva qué revisión llegó primero, mientras
que la lectura terminal escalar no conserva el orden una vez completadas ambas.

### Alcance

El mecanismo es una actualización reiterada acotada y un uso posterior de una
relación móvil. La información de las revisiones fue suministrada por teachers
externos preparados en t0. No muestra que el mundo derive por sí mismo los
valores 11 y 13, ni aprendizaje universal, ni memoria ilimitada.

Estado de laboratorio: **MECANISMO ACOTADO CONTRASTADO** para revisión externa
reutilizable y transformativa.

## F2 — retorno causal mediado por el ambiente

### Pregunta

¿Puede la respuesta del linaje modificar un receptor ambiental preparado,
actualizar un portador distinto mediante DEMUX y hacer que esa diferencia sea
utilizada más de una vez?

### Mecanismo y separación de ruta directa

La respuesta 4149 llegó en t38 al sitio ambiental `(73,90,63)`. Un sesgo común
15515 llegó simultáneamente. La reducción dio s_reg=19664. Seis soportes
semantic=4, idénticos en todos los brazos, fijaron el régimen local y el clock
del sitio fue preparado para que la actualización material siguiente alcanzara
19665. El overflow reinició la carga local y el postpaso DEMUX escribió un
delta de +1 en `(72,89,62)`.

Un portador independiente de carga 23 llegó a ese destino en la misma
transición t39. El postpaso lo convirtió en 24. La respuesta original no viajó
a ese destino: terminó en el receptor ambiental y quedó con carga cero tras el
overflow. Así se separó el portador directo de la modificación ambiental.

El portador actualizado participó después en una cadena común:

- t43: +31, resultado 55;
- t47: +7, resultado 62;
- t51: redirección de carga cero, retención 62;
- t55: +5, resultado 67.

### Controles

| Brazo | overflow | t39→t43→t47→t51→t55 |
|---|---:|---:|
| ENV_INTACT | 1 | 24→55→62→62→67 |
| ENV_RESPONSE_CUT | 0 | 23→54→61→61→66 |
| ENV_NO_QUERY | 1 | 0→31→7→0→5 |
| ENV_QUERY_SHAM | 1 | 0→31→7→0→5 |
| ENV_SUBTHRESHOLD | 0 | 23→54→61→61→66 |
| ENV_CONTENT_19 | 1 | 24→55→62→62→67 |

El corte desvió el teacher inicial a una ruta paralela con la misma carga;
todas las entradas siguieron admitidas en t0. El control subumbral cambió sólo
el sesgo de 15515 a 15514: el receptor quedó en 19663, no hubo overflow y la
cadena coincidió con el corte. La ausencia de query y el sham espacial
conservaron el overflow, pero el delta no actualizó la ruta funcional. Estos
contrastes separan formación de la respuesta, umbral ambiental, localización
del delta y uso posterior.

Estado de laboratorio: **MECANISMO ACOTADO CONTRASTADO** para retorno ambiental
finito con dos usos posteriores de una modificación mediada.

### Límites

El receptor y sus seis soportes estaban preparados. La carga del delta (+1)
proviene de la regla DEMUX, no codifica arbitrariamente el contenido de la
respuesta. La cadena tiene horizonte finito y recursos preposicionados; no
demuestra sostenibilidad indefinida ni enseñanza endógena general.

## F3 — indicio de fan-out/replicación

Se cambió el marcador histórico de 17 a 19. Las respuestas upstream fueron
4149 y 4151, pero ambas se saturaron a 19664 al encontrar el sesgo y ambas
produjeron exactamente 24→55→62→62→67. El sitio ambiental original perdió la
carga tras el overflow y el destino recibió sólo el delta unitario.

Este aparato implementa una compuerta de umbral y un retorno causal, no una
réplica del contenido s_reg ni dos expresiones funcionales del mismo contenido.
Estado: **CANDIDATO DESCARTADO EN ESTE APARATO** para fan-out de contenido. No
es una imposibilidad general del kernel ni invalida H3, cuyo recurso era una
copia entrenada por separado.

## Indicios seguidos

| Observación | Hipótesis | Contraste | Resultado |
|---|---|---|---|
| cargas 11 y 13 podían ocupar redirecciones ya usadas | el linaje acepta revisiones sucesivas | orden, revisiones individuales y sham | dos revisiones usadas; orden visible sólo en lectura intermedia |
| el primer sesgo no alcanzó el receptor | la ruta cruzaba soporte, no era ausencia de mecanismo | cambiar sólo la dirección de aproximación | colisión 19664 y overflow único |
| overflow dejó delta espacial | un portador independiente puede recibirlo | llegada simultánea, corte, subumbral, no-query y sham | 23→24 sólo con respuesta+umbral+ruta correcta |
| contenidos upstream 4149/4151 saturaron igual | el montaje es gate, no replicador | contenido reservado 19 | salidas idénticas; especificidad escalar perdida |

## Validación técnica

- todas las entradas de los 16 casos fueron aplicadas en t0;
- no hubo fallback de backend;
- relaciones F1 y mediación F2 coincidieron con las predicciones congeladas;
- Lazy y DenseParallel coincidieron exactamente en RAW y clock finales para
  REV_11_13, SHAM_11_13, ENV_INTACT y ENV_RESPONSE_CUT;
- el binario ejecutado fue construido en Release contra la biblioteca estática
  exacta de la preintegración;
- se conservaron snapshots en t38/t58 para F1 y t39/t55 para F2.

## Qué no se estableció

No se ejecutó una adquisición autónoma del contenido de los teachers, una
replicación funcional adquirida, fan-out general, recurrencia ilimitada,
sostenibilidad indefinida ni publicación estable. H1/H2/H3/H4 no fueron
reintegrados ni ampliados administrativamente. Entrega 03 no fue iniciada.

