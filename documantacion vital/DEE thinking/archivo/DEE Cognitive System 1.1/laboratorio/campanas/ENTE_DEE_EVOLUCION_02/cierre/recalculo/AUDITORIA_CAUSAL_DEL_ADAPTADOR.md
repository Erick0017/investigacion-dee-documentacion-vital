# EO02: auditoría causal dirigida del adaptador

Revisión de fuentes realmente ejecutadas y primarios, sin nuevos ticks ni
ejecuciones de servicios. No es otra auditoría del corpus histórico.

## Frontera comprobada

En las revisiones examinadas, `cf.decode_window` transforma únicamente dos
muestras físicas fijas del motor, con retención máxima de un tick y conflicto
invalidante. Ni el target, ni el crédito ambiental, ni el éxito posterior
seleccionan el lector o el signo. La acción formada y la ejecutada se guardan
por separado; el brazo anulado no ejecuta un trabajador sustituto.

Las fuentes genéricas del retorno se programan independientemente del resultado;
los antiguos suministros j0 no se presentan. Después de la actuación real, un
contacto observado puede producir un pulso táctil de carga0 que representa la
postura efectivamente ejecutada. La actualización de `own` procede de v27, no de
una asignación Python de la referencia o de la próxima acción.

La ley de admisión calcula una condición ambiental legítima. **Calcular esa ley
no equivale a escoger la acción del participante:** el trabajador sólo ejecuta
el comando material ya seleccionado y acepta/rechaza conforme a su modelo.
Los archivos producidos y su lectura de retorno son reales, pero la restricción
de capacidad es una regla modelada, no una medición del hardware del equipo.

Se revisaron el módulo de servicio, su core, el trabajador y la excepción exacta
del guard en `gestionar.py`. El guard autoriza sólo el argv declarado del worker;
no concede una política externa adicional. Es un límite de auditoría Python,
no un sandbox de sistema operativo. Las revisiones/casos concretos se vinculan
por el índice de fuentes de cada primario, no por asumir que S actual sea igual
al código de todas las experiencias anteriores.

## Transferencia: alcance respaldado por los primeros registros

Fuente04/05/06: T2/4, U1/4, H1/4 actuaciones útiles. Los tres brazos parten del
mismo pasado EO01 y comparten edades, muestras y suministros genéricos. U no es
un individuo universalmente ingenuo: sólo se omitió esta nueva consecuencia.
T produjo2 pulsos táctiles, U0 y H3. No se afirma igualdad de dosis material
total; las actuaciones divergentes producen consecuencias legítimamente distintas.

Destino B10/11/12: T6/6, U4/6, H3/6. La primera oportunidad, antes de su retorno,
fue útil sólo en T. Esto apoya una ventaja inicial de la experiencia fuente bajo
una **representación y ley de comparación compartidas**. A/B son formalmente
isomorfos en la selección, aunque B ejecute dos servicios locales reales.
No acredita abstracción general ni transferencia sin una correspondencia preparada.

Anulación13:3/3 emisiones válidas,0/3 actuaciones externas y0/3 trabajos aceptados.
Apoya la contribución de la salida a ese efecto práctico. No es un brazo de
anulación de la adquisición fuente; ese control debe conservar su identidad EO01
si se reutiliza históricamente, sin presentarlo como ejecución EO02 nueva.

## C: conservar las dos revisiones y sus resultados adversos

R01 (`local_worker.receipt.v1`) añadió una dependencia de la actuación anterior:
primero preparar y luego usar el otro trabajador. Su verificación comprobaba una
copia ambiental `payload_base64`; **no leía el archivo de la preparación anterior**.
Había I/O real en ambas etapas, pero no una cadena de verificación de ese archivo.
La descripción correcta es transacción modelada de dos etapas y artefactos reales.

C14/15/16: T3/6 pasos aceptados, U3/6, H2/6; cada uno completó una transacción.
Ninguno cumplió el criterio prospectivo de dos transacciones en seis oportunidades.
La fase no era una observación explícita de DEE. El resultado no demuestra una
política contextual general, ni una imposibilidad de v27.

R02 (`local_worker.receipt.v2`) es una revisión distinta: conserva en el estado
ambiental los bytes exactos y el nombre/hash del output preparado; lee y verifica
el archivo antes de aceptar el commit. Si una copia de mundo carece del archivo
externo, puede rehidratar esos mismos bytes de su estado ambiental completo. Eso
es restauración de un entorno externo, no inserción de memoria en DEE. Un pendiente
R01 no se reinterpreta como R02; exige un fixture nuevo declarado.

El piloto21 con fase actual visible dio4/4 pasos y2 commits, frente a2/4 y1 commit
en22 con canal extra cero. Son pilotos en el borde R-L14, con preparación+ y
verificación-. Una evaluación reservada donde prepare- y verify+ resulta necesaria
para delimitar si la ganancia se limita a ese sesgo o utiliza de modo más amplio
la estructura secuencial. No se redefine el criterio tras ver esos contraejemplos.

## Continuidad y contexto

El regreso A17/18 dio2/3 en T y U, no recuperación perfecta. `own` es un estado
acumulativo compartido que cambia entre tareas. Un cambio de su sesgo no cuenta
como dos políticas conservadas. Los siete pilotos contextuales adicionales y sus
negativos se describen en `contexto/DIAGNOSTICO_CONTEXTO_Y_SELECTOR.md`.

La selección de dominio, el calendario, los soportes y la traducción son P0 del
aparato/operador. Hay contenido y transformaciones dependientes de historia;
no aparece por ello una elección autónoma de tarea o una regulación R2 general.

## Referencias externas, congeladas y separadas

`referencias_eo02.py` quedó congelado a21:40:33Z, SHA-256
`8fddf2a81ea6517cd8f02f3df72930b9789e3bf99a870fbdf3c6a761cc1e28cb`.
Contiene izquierda/derecha fijas, alternancia, ocho semillas1001–1008 y dos
adaptativas sencillas. El umbral empieza en12 fijado, no en el crédito oculto14;
sólo cambia tras el contacto/postura de la propia referencia. La variante
phase-aware puede usar un bit de fase únicamente cuando ese sensor está presente
y recuerda su propia preparación; su interpretación de ese protocolo es preparada.

Cada referencia conserva su propio entorno. Después de acciones distintas no se
le impone el pendiente o la fase futura de MAIN. El crédito permanece en el modelo
evaluador y nunca entra en `Policy.choose`. Ninguna referencia controla un mundo
DEE. Las métricas son aritmética de tareas archivadas, no nuevas ejecuciones
nativas, del servicio, ni benchmarks de velocidad o inteligencia.

En el primer corte MAIN, la adaptativa de umbral reprodujo2/4→6/6→3/6(un commit)
→2/3. La alternante dio3/4→5/6→6/6(tres commits)→3/3. Hay capacidades DEE locales
respaldadas, pero estos datos no sostienen superioridad general. Ocho semillas no
convierten una sola historia DEE en ocho réplicas de aprendizaje independientes.

## Qué comprueba el recálculo

`recalcular_eo02.py` rehace desde los frames el lector fijo, las acciones, efectos,
admisiones/rechazos y el orden post-acción de la consecuencia. Regenera bytes de
los workers de cada revisión y comprueba los archivos de código por contenido.
Puede verificar también las copias de outputs reales exportadas con
`exportar_artefactos.py`, sin utilizar rutas fuente para responder.

Las salidas incluyen CSV por caso, primer uso/retención, referencias y JSON de
contrastes/continuidad. Son recálculos, **no** reproducciones de la física DEE.
Los snapshots completos se conservan localmente con su genealogía; los testigos
de igualdad de cargas no sustituyen su identidad completa.

El primer corte de18 primarios/58 episodios y el segundo de22/66 comprobaron sus
archivos de código y no encontraron discrepancias en estos cálculos. Las cifras
finales deben tomarse del último corte cerrado, no extender estos recuentos a
registros todavía en curso.

## Reservas cerradas R02 y transferencia contraria: corte03

Se recalcularon49 primarios raíz/135 episodios con cinco archivos de revisión de
código, y se exportaron95 outputs reales de los workers; ningún byte difería de
su recibo. No hubo discrepancias del recálculo. El JSON de corte03 tiene SHA-256
`ec85fb7a0c0ef8f6df03031700fc01d58b5cb9c6cdd822f73bb8f0086ba24ee2`.
Este corte no incluye las ampliaciones R10 posteriores que se entregan separadas.

| Secuencia | Pasos útiles | Commits C | Primer retorno A |
|---|---:|---:|---|
| MAIN reserva1, crédito14 | 12/12 | 3 | correcto |
| ZERO, mismo prefijo y currículo1 | 8/12 | 1 | incorrecto |
| MAIN reserva2, prepare- / verify+ | 8/12 | 1 | correcto |
| MAIN reserva3, alineación4 a crédito12 | 11/15 | 3 | incorrecto al volver a14 |

La primera cumple los criterios fijados de al menos10 pasos y2 commits. La
segunda reserva MAIN no los cumple. La tercera alcanza11 pasos y3 commits, pero
falla el criterio específico de retención del contexto antiguo en la primera
respuesta. No se presenta el total favorable como dos políticas conservadas.

En26C, las acciones fueron `---+++`, con resultados verdadero/falso/falso/
verdadero/falso/falso. La fase estaba disponible; faltó una selección general
condicionada por la actuación preparatoria. El control ZERO comparte los dos
canales, número y tiempos de entradas extra, pero no las cargas0/1 de un control
de fase permutada; no demuestra por sí solo interpretación semántica de fase.

En27D los dos primeros accesos antiguos fallaron y modificaron `own408/400` a
`414/404`; el tercero7:22 era negativo tanto con criterio efectivo12 como14.
Acertarlo no demuestra por sí solo la restauración funcional del borde14. Una
interacción nueva en ese borde, antes de su feedback, se registra aparte como
uso de referencia readquirida, nunca como retención intacta de la anterior.

Fuente→C28 desde cortes emparejados: T4/4 pasos y2 commits, U2/4 y1, H0/4 y0.
La primera respuesta fue útil en T y falló en U/H, antes del retorno de destino.
Eso apoya la utilidad del criterio fuente en la tarea compuesta, con sensor de
fase preparado y sin enseñanza adicional previa a ese primer destino. No demuestra
que DEE aprendiera la regla general «usar el otro trabajador».

La relación contraria30 hace explícito el límite: T1/3 frente a U3/3. La primera
actuación T+ falla donde U- sirve. La historia relevante en un contexto puede
perjudicar bajo otra relación; no se oculta ese contraejemplo de transferencia.

Las referencias de umbral congeladas dieron12/12,8/12,11/15 en esas tres reservas,
igualando los recuentos de MAIN. La variante preparada phase-aware dio12/12,
12/12,11/15; tampoco conservó el primer uso del antiguo contexto14 en la tercera.
Cada referencia hereda sus experiencias ancestrales hasta el tick exacto de su
bifurcación; no se reinicia artificialmente al abrir un auxiliar. Esos prefijos
se marcan y no cuentan como experiencias nuevas de la rama.

Las ocho referencias aleatorias dieron rangos5–8/12,2–9/12 y3–10/15. Son ocho
semillas de un modelo convencional y no ocho réplicas independientes del ente.

El dominio B de servicios no es el participante material B de referencia61/19.
Usar A para seleccionar un servicio no constituye actualización o enseñanza social
de ese participante. Su conservación y su uso real se deben declarar por separado.

## Frente de capacidad independiente

Los57 primarios del frente de capacidad y117 episodios se recalcularon en una
extracción temporal, con raíces originales y acceso al motor/procesos/red
prohibidos. Su JSON fue byte idéntico:
`2b051f338d618ea6e8a019fcefc107e21b5d9a72332ff1c20de8efaa14234e32`.
Las16 sumas físicas adversas se conservaron como negativos científicos, no como
errores de lectura. R03 de primer uso y R10 tienen ocho contrastes de relevancia
por componente; repetición, transporte y utilidad se informan separadamente.

R10 es una preparación T0 distinta. Sus adquisiciones no se importan en MAIN y
el inicializador convencional12 usado con el pasado EO01 no equivale por sí mismo
a su historia nueva. Cualquier comparación convencional de ese perfil debe
igualar o declarar su prefijo; el contraste nativo T/U permanece por separado.
