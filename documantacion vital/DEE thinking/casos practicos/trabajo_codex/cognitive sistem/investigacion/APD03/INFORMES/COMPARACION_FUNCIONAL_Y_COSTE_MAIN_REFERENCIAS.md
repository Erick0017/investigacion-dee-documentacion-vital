# MAIN frente a cuatro referencias: función y coste con alcances separados

MAIN y WSLS estándar completaron **10/11 tareas compartidas**, con 8/8 objetivos de consulta/acción y 2/3 pruebas de calidad/disponibilidad. Esto no demuestra equivalencia cognitiva, eficiencia equivalente ni superioridad de DEE. Las tres referencias iniciales completaron 9/11 en ese mismo subconjunto; se conservan sus errores, y la variante original `wsls` se identifica como preferencia lose-shift, no como WSLS estándar sobre la acción efectivamente realizada.

## Contraste funcional comprobado

| Trayectoria | Goals sólo-native | Calidad/disponibilidad | Total | Oportunidades comparables | QUERY | ACT |
|---|---:|---:|---:|---:|---:|---:|
| MAIN nativo | 8/8 | 2/3 | 10/11 | 17 | 6 | 11 |
| Procedimiento fijo convencional | 8/8 | 1/3 | 9/11 | 19 | 8 | 11 |
| Tabla convencional, contexto cegado | 8/8 | 1/3 | 9/11 | 15 | 4 | 11 |
| Preferencia lose-shift convencional | 8/8 | 1/3 | 9/11 | 15 | 4 | 11 |
| WSLS estándar convencional | 8/8 | 2/3 | 10/11 | 15 | 4 | 11 |

Los 17 usos comparables de MAIN son **14 oportunidades de goals y tres acciones de calidad**, no 17 individuos ni toda la actividad material. Los 14 goals incluyen ocho ACT con archivo correcto y seis QUERY: cuatro revelaron hechos nuevos y dos fueron redundantes. En los tres casos de calidad, MAIN eligió native/external/native y obtuvo fallo/éxito/éxito, igual secuencia de efectos que WSLS estándar. El primer error no fue una suma nativa incorrecta: el cálculo nativo produjo 23 y la ley ambiental declarada `wrong_value_delta=1` transformó el archivo en 24.

El JSON asociado contrasta directamente los primarios MAIN (incluidos los dos resultados nuevos de la UI ordinaria), el recálculo cerrado y las cuatro trayectorias convencionales. Sus 362 comprobaciones sin discrepancias incluyen operandos, formas, orden real de tareas, visibilidad inicial del segundo dato, observaciones posteriores, límites y omisión de retorno. No se repitió el recálculo nativo, la campaña ni los proveedores.

Programa común congelado SHA-256: `96b6b1a82bd4a3f3bc0cb6f9650752ed8bf3506b9e0bf37de2ea6dc2c51ca599`. En orden: suma8/5; diferencia22/9; suma12/7 inicialmente incompleta; diferencia28/13 incompleta; calidad suma15/8; calidad diferencia30/12; agrega10/11; disponibilidad resta25/9; resta31/12; total14/15 incompleta sin retorno; suma17/9 incompleta conservada entre invocaciones. Cada goal admite como máximo cuatro oportunidades ACT/QUERY; cada caso de calidad tiene una sola acción ACT y dos procedimientos admitidos. Los límites de precio2 y demora8 se mantienen, sin seleccionar otra ruta según el resultado esperado.

La última tarea conserva el presupuesto de invocaciones [1,3]. MAIN la continuó por el mismo ID pendiente en otra UI/proceso. Las referencias conservaron su estado ambiental y de política mediante serialización entre esas invocaciones, pero dentro del mismo proceso: **no** se les atribuye la prueba operativa entre procesos que sí realizó MAIN.

## Qué información llega a cada selección

La selección nativa recibe una señal de la forma matemática adquirida y el bit bruto `second is None`. El contexto0/1 existe en la API, pero no se transduce al selector nativo de este candidato; los operandos numéricos se utilizan después de ACT para el cálculo. Por eso las referencias ejecutadas usan una proyección más restrictiva que la descripción ancestral del programa: `left=None`, `second=0/None` y contexto constante0. Los valores reales sólo llegan al ejecutor convencional después de comprometer la acción. Las leyes cambiantes de calidad/disponibilidad son privadas del entorno y no se entregan a la política.

Las seis asociaciones matemáticas anteriores se proporcionaron explícitamente como pasado preparado a los comparadores; no se equipara su coste de adquisición al de la historia nativa. Las referencias no adquirieron luma/nara, no conservaron soportes MA, no realizaron los paneles físicos ni la composición asistida, y no evolucionaron durante una hora en v27. Esas funciones adicionales de MAIN tienen evidencia propia pero quedan **fuera de este marcador de once tareas**. Los hechos revelados por QUERY permanecen públicos en el estado ambiental externo: completar el archivo después no demuestra por sí solo memoria nativa del número consultado.

Ambas rutas de los comparadores calculan convencionalmente; `native` es allí el nombre de la interfaz nominal, no una llamada a v27. Ninguna referencia controló E1 ni entregó su respuesta a MAIN. El retorno es binario y posterior al efecto comprometido; se omite donde lo exige el programa.

## Recursos: valores medidos, no cocientes engañosos

La supervisión exterior completa de MAIN registró **1881,90625 s de CPU** (1349,1875 usuario +532,71875 kernel), **356.691.968 bytes de pico de memoria comprometida del job** y 3936,8713883 s de reloj supervisado. La ventana ambiental habilitada fue 3600,0005902 s. La supervisión incluyó driver, clientes, trabajos Native y continuación: 352 procesos lanzados no son 352 entes. El pico comprometido no es una medición de memoria residente idéntica al working set de un solo trabajador.

Los costes de las referencias son intervalos cortos de un trabajador convencional, sin evolución basal de una hora y antes de la escritura final de su resumen:

| Referencia | CPU del intervalo (s) | Reloj del intervalo (s) | Pico working set de trabajador (bytes) |
|---|---:|---:|---:|
| Fijo | 0,1875 | 0,3511932 | 24.010.752 |
| Tabla | 0,125 | 0,1777311 | 23.805.952 |
| Preferencia lose-shift | 0,09375 | 0,1237923 | 24.047.616 |
| WSLS estándar | 0,140625 | 0,1967104 | 23.740.416 |

Los números anteriores tienen ámbitos diferentes: no se divide la hora/CPU total de MAIN por una decisión clásica para declarar un factor de eficiencia. MAIN también ejecutó aprendizaje léxico, conservación, paneles, estado continuo y carga del servicio; las referencias no. Tampoco se suman al TOTAL exterior el CPU del driver ni el de los jobs Native anidados: ya son subconjuntos. No existe aquí una medición aislada de latencia decisional host MAIN con el mismo alcance que las muestras de decisión clásicas; ese campo queda `null`, no cero. Los tiempos cortos están afectados por granularidad del contador y carga del equipo; no establecen un ranking estable.

## I/O y energía

MAIN dispone de contadores Windows class8 de dos jobs Native cerrados, acumulados desde la creación de cada job. El primero registró 363.380.956.293 bytes lógicos leídos y 7.173.196.582 escritos; el segundo 972.315.071 y 211.912.731. El observador se conectó después de comenzar el primero: los acumulados conservan el trabajo anterior, pero no existe resolución class8 para todas las fronteras de fase previas a su conexión. Los valores representan transferencias lógicas OS/cache del job y sus trabajadores, **no** sectores físicos, desgaste del disco ni energía.

Las referencias utilizaron `GetProcessIoCounters` del trabajador, no class8 del árbol MAIN: fijo48.038/75.050; tabla47.722/68.312; preferencia lose-shift47.722/66.892; estándar48.042/67.515 bytes leídos/escritos en su intervalo instrumentado. Son medidas reales pero de ámbitos distintos. Los antiguos ceros de `class9.IoInfo`, que es reservado, son **NO MEDIDO**, no ausencia de I/O. Un delta cero real sólo indica que ese contador no avanzó durante esa muestra. Los tamaños exactos de archivos son una medición distinta y no sustituyen estos contadores.

Energía de MAIN y referencias: **NO MEDIDA**. No se convierte TDP, ocupación, s_reg ni duración de CPU en consumo energético de DEE.

## Conclusión acotada

MAIN sostuvo el mismo objetivo final y utilidad de archivo que la referencia estándar en estas once tareas, con dos consultas redundantes más. Además realizó funciones físicas intercaladas excluidas de la comparación. Se demuestra una organización nativa funcional dentro de contratos preparados y una comparación externa ejecutada, no ventaja universal, entrenamiento equivalente ni una política de propósito general. Cada fila es una trayectoria; consultas y tareas son usos dependientes, no muestras independientes para una inferencia estadística de inteligencia.

Los localizadores, SHA-256, primarios enlazados, controles de proyección y recursos exactos están en `COMPARACION_FUNCIONAL_Y_COSTE_MAIN_REFERENCIAS.json`. El generador N0 `generar_comparacion_funcional_n0.py` sólo lee esos expedientes cerrados y no modifica sistema ni resultados originales.
