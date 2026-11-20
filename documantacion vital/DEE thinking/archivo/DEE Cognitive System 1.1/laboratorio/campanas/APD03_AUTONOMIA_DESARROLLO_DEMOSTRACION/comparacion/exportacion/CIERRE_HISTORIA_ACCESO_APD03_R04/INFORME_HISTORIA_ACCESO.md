# Historia, sincronización docente y acceso material R04

El nuevo contraste delimita una causa física de la curva léxica anterior: la experiencia A modifica si las entradas posteriores en el soporte compartido K pueden admitirse. No demuestra una aceleración semántica de aprender a aprender. Dos historias con igual dosis docente nominal difieren en sincronización y producen diferencias de acceso verificables en ambas polaridades.

## Preparación y trayectorias

Se reutilizó, sin repetir el panel old14 ni instalar otra geometría, el prefijo completo R02 en T549343, SHA `9f3ed841280263d049ba3d08edf96c45eeeb9551c9794c5002df4472b2dfc0bf`. Es una bifurcación AUX del padre APD02 ya documentado, con dos casillas genéricas P0 vacías en K=(47,7,47), 32 puertas comunes y mecanismos anteriores. No se cambiaron N67, kernel, WHL, MAIN ni vidas protegidas. Las cuatro historias comparten este pasado y no son réplicas independientes.

Cada brazo realizó un panel material old4 (suma, resta, compara, recuerda), una docencia A, dos consultas A, una consulta B sin docencia B, una docencia B, dos consultas B y otro panel old4. A y B son las señales arbitrarias luma y nara. El signo de ambas fue −1 o +1 según el brazo. La única variante de A fue docente sincronizado frente al mismo docente retrasado 11 ticks; ambos recibieron cue5 y docente11 por las mismas interfaces. B tuvo docencia sincronizada en todos los casos.

Se añadió una quinta reproducción instrumental del primer brazo, sin registro ROI, manteniendo el mismo avance propietario de un tick. No es una quinta adquisición independiente.

## Resultados con denominadores

| A | B enseñado | Solicitudes/aplicadas/rechazadas | A después | B antes de enseñar | B después | old4 conservadas |
|---|---:|---:|---|---|---|---:|
| paired | −1 | 95/95/0 | −1,−1 | ninguna | −1,−1 | 4/4 |
| desync+11 | −1 | 95/89/6 | ninguna,ninguna | ninguna | ninguna,ninguna | 4/4 |
| paired | +1 | 95/95/0 | +1,+1 | ninguna | +1,+1 | 4/4 |
| desync+11 | +1 | 95/89/6 | ninguna,ninguna | ninguna | ninguna,ninguna | 4/4 |

Todas las ramas recorrieron T549343→T550345: 1002 ticks, con 1003 cortes consecutivos en las cuatro registradas. La quinta repitió el primer resultado (95/95, A− y B−) sin producir frames ROI. El criterio fijado de dos respuestas B correctas se alcanzó sólo en los dos brazos paired y su reproducción instrumental; no se cambió después.

Las dos entradas A se admitieron en los cuatro brazos. En desync, A terminó en T549682 frente a T549671 paired, pero las consultas posteriores comenzaron en los mismos ticks físicos. No se afirma que toda la historia fuese idéntica en edad: precisamente se intervino sobre el tiempo del docente. Sí se observó calendario posterior común y dosis nominal [5,11] comparable.

En B, los dos brazos desync solicitaron cue y docente; sólo el docente se admitió. Por tanto su B no es un caso de adquisición con ambas entradas admitidas que simplemente fracasó. Repetir «dos respuestas B incorrectas» sin ese denominador ocultaría el mecanismo de acceso. El control anterior sin A tampoco acreditaba tres docencias completas B: sus cues estaban rechazados.

## Fuente de la pérdida de acceso

En los brazos desync, la primera consulta A se rechazó en K en T549735. El registro pasivo muestra RAW exacto `1157143650732343297`: state1, SEM1, dirección X−, s_reg5. El mismo tipo de ocupación aparece en K en T549802, T549869, T549936, T550003 y T550070, coincidiendo con las otras cinco solicitudes cue rechazadas. K era RAW0 un tick antes y un tick después de cada frontera. Un snapshot tomado fuera de esa frontera puede mostrar K vacío sin demostrar que era accesible al aplicar la petición.

La traza completa detectó diez cortes no nulos en K, espaciados 67 ticks, desde T549735 hasta T550338. Los cuatro finales ocurren después de la última petición nueva a K, durante los paneles antiguos. En paired, K fue RAW0 en todos los cortes de tick registrados, aunque sus recibos documentan entradas aplicadas que se transportan durante el paso. No se infiere que la entrada no existió por no verla retenida en el sitio de inyección al final del tick.

Estos datos establecen recurrencia de una clase física y bloqueo temporal de la interfaz. **No establecen el linaje único de un portador ni un recorrido toroidal completo.** La ROI no cubre todas las posiciones intermedias: una separación de 67 por sí sola no basta para atribuir retorno del mismo portador. Tampoco se llama memoria funcional a esa recurrencia; en esta tarea perjudica la admisión.

## Encuentros y contenido

En paired, el hub A=(44,7,47) contiene en T549671 una salida pura Z±, SEM1, s_reg16, compatible con el encuentro de cue5 y docente11 admitidos. En desync, el corte del mismo T549671 muestra X−5; el docente llega después al hub en T549682 como diagonal (1,0,±1), s_reg11. El encuentro sincronizado y su transformación faltan en ese instante.

Para B=(47,4,47), paired contiene en T549939 Z±16. Desync contiene en ese mismo tick sólo la contribución diagonal (0,1,±1), s_reg11; el recibo cueB está `rejected_occupied` y el del docente B está `applied`. La diferencia no depende de cambiar un lector según el resultado: todos los ensayos utilizan las mismas 32 puertas y el mismo decodificador sin argumento target.

Los RAW y clocks de las lecturas materiales coinciden con los del registro pasivo del mismo tick. La evidencia está en `PRIMARIO.json.gz`, `ROI_TICK_A_TICK.jsonl.gz` y los `PASOS/` de cada brazo. `DIAGNOSTICO_ENCUENTROS_N0.json` es una extracción reproducible de posiciones fijas, no información adicional entregada al ente.

Los dos brazos desync tienen hashes RAW y clocks finales iguales entre sí, pero sus snapshots completos serializados **no** son idénticos (incluyen interfaces y recibos distintos). No se presenta esa igualdad parcial como destrucción de toda información causal sobre el signo enseñado.

## Alcance cognitivo e incorporación

Paired demuestra asociación adquirida y uso posterior del signo de dos señales dentro de esta preparación. Ya existían dos interacciones preparadas que ese signo puede seleccionar, comprobadas por separado en la curva R03; este R04 no repitió su uso funcional completo. Las cuatro formas antiguas muestreadas permanecen accesibles, no se extrapola a las catorce ni a NSM65.

El resultado nuevo es un límite operativo útil: consulta material de una casilla no formada y sincronización docente no equivalente pueden modificar la admisibilidad futura de la interfaz común. La docencia paired del componente operativo existente se conserva y queda mejor justificada; no es una nueva política autónoma ni arquitectura autogenerada. No se atribuyen iniciativa, P2/R2, transferencia semántica específica o nuevos algoritmos.

Estas ramas son diagnósticas AUX: sus conocimientos no se importaron en MAIN. La incorporación adecuada es el contrato de docencia/admisión y el instrumento pasivo de fuentes/puertas como herramienta del investigador. La capacidad de una vida principal se acredita con su propia trayectoria, no sumando estos brazos.

## Instrumentación, recursos y verificación

Fuentes ejecutadas: protocolo SHA `03c547ed41bc2477e324b42191c5575e1cff2647f86ea23c46ccc8afc1192632`; runner SHA `0fe24cb0067d00a158c58e3db2df62384f72332bb3cea81554d2f87a92fc7663`. Se preservaron sus bytes antes de ejecutar y los hashes de originales/copias siguieron iguales al cierre. Un único propietario por Runtime avanzó mediante `owner.run_until(t+1)`, OMP/BLAS/MKL=1 y job de 512 MiB.

El par registro ON/OFF produjo exactamente el mismo snapshot final, tanto comprimido como decodificado, SHA `af6660dbc4df251bff8d6a6bd8b3189a96a339742ea5092cfbef2b8ca601587b`, además de igualdad RAW/clocks. Esto cubre interfaces, colas, recibos y progreso serializados de ese brazo; no se limita al texto de respuesta ni certifica pasividad para cualquier futuro instrumento.

Duración real 340,1987289 s; CPU de job 146,109375 s usuario +30,078125 s kernel; pico de trabajo del trabajador 266.493.952 bytes y comprometido de job 270.770.176 bytes. Se completó dentro del guard600s y del horizonte1200ticks por rama. El guard se comprueba antes de cada rama/tick, no es una promesa de terminación instantánea durante guardado y hash. Energía: NO MEDIDA. No se infiere I/O desde campos reservados de class9.

El recálculo N0 verifica 525.862 condiciones sin discrepancias: campos RAW exactos, clocks uint64, 63 posiciones por corte, continuidad temporal, las 32 puertas, acuerdo lectura/observación, solicitudes únicas, estados de admisión y criterios. La extracción de encuentros y recurrencias se regenera por separado. No son repeticiones nativas ni nuevas adquisiciones.

Los diez snapshots completos y la telemetría original permanecen localmente en `evidencia/campanas/APD03_AUTONOMIA_DESARROLLO_DEMOSTRACION/CURVA_HISTORY_ACCESS_R04/`. El export compacto conserva todas las trazas ROI y positivos/negativos, pero no sustituye esos estados para continuar las ramas. La igualdad completa es una comprobación local con recibo/código; si los snapshots se omiten, el ZIP conserva una atestación verificable por su localizador y hash, no los bytes del mundo entero.
