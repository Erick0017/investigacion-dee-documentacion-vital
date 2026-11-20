# Controles de continuidad, consulta y trabajo: alcance final

Esta nota de cierre reutiliza el recálculo cerrado `evidencia/campanas/APD05_GENESIS_SIN_LLM/controles/REPOSO_Y_ACCESO_PORTABLE_N0_R02`. No ejecuta Native ni añade experiencias. En el cierre N0 se verificaron de nuevo los 123 miembros declarados del manifiesto sin discrepancias (el recálculo interno verifica 121 fuentes; el manifiesto final incluye también índice y golden). El componente sellado conserva 124 archivos, 6,011,330 bytes; no se ha modificado.

## Panel común y denominadores

El panel son **ocho consultas funcionales limitadas**, no ocho primitivas NSM: alfa−, beta+, luma+, nara−, clasifica+, equilibra−; clasificación escalar de 27 respecto de la referencia heredada 20; balance de [3,7] bajo el sesgo por operando preparado. Cada panel completo solicita exactamente **222 entradas materiales Native = 6×7 léxicas + 4 escalares + 176 de balance**. Las consultas son interacciones materiales y pueden modificar el estado.

| Corte real | Edad de comparación | Panel | Coincidencias RAW nominales | Coincidencias con todas las entradas aplicadas | Aplicadas / rechazadas |
|---|---:|---:|---:|---:|---:|
| PREV_REST_R03 | 8192 | 8 | 8/8 | 8/8 | 222/0 |
| PREV_ORD_OMIT_R03 | No alcanzada | No ejecutado | No evaluado | No evaluado | No panel |
| PREV_ORD_REAL_R03 | Futuro no confirmado | No ejecutado | No evaluado | No evaluado | No panel |
| PREV_OMIT_CONT_R04 | 8192 | 8 | 1/8 | 0/8 | 1/221 |
| PREV_ORD_REAL_R04 | 8192 | 8 | 1/8 | 0/8 | 4/218 |
| REC_REST_R04 | 4096 | 8 | 0/8 | 0/8 | 3/219 |
| REC_ORD_REAL_R04 | 4096 | 8 | 0/8 | 0/8 | 3/219 |

Los nombres abreviados corresponden a vidas `APD05_CTL_…`. No se suman como una vida ni como réplicas independientes. OMIT_CONT_R04 es descendiente del corte OMIT_R03: sus tres experiencias son las mismas, no tres repeticiones nuevas. La coincidencia nominal 1/8 de los dos brazos ordinarios es el signo de balance; sus entradas fueron mayoritariamente rechazadas. No acredita un nuevo uso causado por esa consulta ni una recuperación conservada de 1/8 funciones. La cifra conservadora 0/8 significa que ninguna respuesta nominal correcta tuvo todos sus insumos solicitados aplicados; no demuestra por sí sola destrucción del contenido.

## Qué se conserva y qué no se demostró

REST es retirada **externa** de las tareas dinámicas durante el intervalo fijado, no descanso seleccionado o aprendido por E1. No se retiraron el mundo heredado, su materia, los suministros ya presentes ni la agenda del servicio; no se limpió RAW ni se reiniciaron clocks. El entorno externo de tareas no evoluciona mediante nuevas llamadas de trabajo durante REST. En el brazo saludable, tras 8192 ticks el panel completo seguía funcionando: conservación acotada sin reenseñanza y con posterior uso material. El mundo no estuvo congelado: cambiaron RAW en 56 sitios y clocks en todos los 300763 sitios entre el padre y el fin del intervalo.

Los brazos de tres tareas ordinarias REAL/OMIT se comparan con ese mismo horizonte ancestral. En el episodio 32, con igual observación actual y entradas sensoriales 3/3 aplicadas en ambos, la acción cambia WAIT (OMIT) frente a USE (REAL), pero la consecuencia REAL fue incorrecta, no útil y sin mejora de calidad. El contraste muestra cambio acotado de actuación dependiente de historia, **no aprendizaje de una política competente**. Las dosis totales no son iguales: REAL solicita 62 entradas durante el trabajo y OMIT 42, debido al retorno y sus operaciones posteriores. No se puede atribuir todo efecto a un único portador ni aislar una causa única del deterioro con esta comparación.

En el estado ya denso, REST y ORD_REAL terminan con RAW/clocks idénticos al mismo tick; no son estados causales completos idénticos: recibos, contadores de entradas, metadatos y entorno difieren. Además, las 17/17 entradas del trabajo ordinario fueron rechazadas, incluidas las 3/3 sensoriales. Por tanto, ese brazo no demuestra aprendizaje fallido después de recibir una experiencia comparable: demuestra falta de admisión en este dominio. La igualdad parcial no prueba borrado de memoria, convergencia causal global ni ausencia de información distribuida.

## Límites de los cortes y de las exportaciones

OMIT_R03 cerró por un límite de calendario prospectivo: la tercera tarea duró 2141 ticks y terminó 93 ticks después del inicio ya fijado para la cuarta. No se desplazó oportunistamente esa cuarta tarea ni se convirtió el panel ausente en 0/8. REAL_R03 conserva un prefijo confirmado y un segundo trabajo interrumpido no confirmado; no se reanudó ni se inventó su desenlace.

REAL_R04 sí terminó todas sus operaciones Native, panel, guardado, STOP y cierre correcto en T663722. El timeout posterior truncó la exportación del sistema de archivos, no la trayectoria Native. Se conservan el snapshot completo de cierre, diario y testigos verificados; falta la exportación emparejada oficial terminada. No se presenta como futuro Native incierto ni como paquete emparejado completo. No se hizo una reexportación Native para cerrar esta limitación.

Las fotos globales y marcos locales no registran cada encuentro del universo. La primera entrada rechazada observada no demuestra el nacimiento exacto del fenómeno ni su causa única. Ni ocupación ni s_reg equivalen a energía, muerte o capacidad semántica.

## Recálculo portátil y sellos

El recálculo es biblioteca estándar, sin motor ni caminos históricos:

`python -I -B CODIGO/exportar_recalcular_controles_reposo_n0_r02.py --root CARPETA_COMPONENTE --out SALIDA_NUEVA.json`

La comprobación aislada existente está en `controles/PRUEBA_PORTABLE_N0_R02/CERCA_Y_RESULTADO.json`: verificó sólo lecturas del componente y produjo el golden byte por byte, sin importar Native. La subcarpeta de prueba BUNDLE es una copia de comprobación y no debe duplicarse en la entrega.

- `MANIFIESTO.json`: `edc5a73ee902168c6bbc7333e93c9875ea34577bb083493e66200e23082926a8`
- `RECALCULO_N0.json`: `991a1a443d2a3f32bc38e3550480beafaffcf3162151027f50fa46d2a1f25759`
- `INDICE.json`: `3858ccd758a08e78cf71da89a6cbbf9c66816f99c8d6e2c81fc02af6cef1c8c5`

El componente de análisis no contiene todos los snapshots operativos ni reemplaza sus pares completos locales. Preserva resultados favorables, adversos, cortes no ejecutados y el futuro interrumpido con su alcance diferenciado.
