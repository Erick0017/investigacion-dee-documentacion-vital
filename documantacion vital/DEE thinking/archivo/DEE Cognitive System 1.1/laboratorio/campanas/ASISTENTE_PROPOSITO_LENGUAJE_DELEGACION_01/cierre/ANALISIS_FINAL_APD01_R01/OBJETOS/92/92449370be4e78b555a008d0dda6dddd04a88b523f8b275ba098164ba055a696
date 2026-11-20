# Recálculo retrospectivo parcial APD01, corte P01–P15

Este documento no cierra la campaña. Usa únicamente primarios ya terminados; no crea Runtime, añade ticks, cambia vidas ni elige acciones. Los siguientes Pxx pertenecen a la investigación del escritor principal y deberán entrar en un corte posterior identificado.

## Hechos verificados

- P05: seis consultas en una copia diagnóstica del padre,42/42entradas aplicadas. Sus lecturas RAW son coherentes con el lector de doce puertas. No se consumieron consultas del padre protegido.
- P06: cuatro operaciones nativas preparadas correctas4/4 en ASISTENTE_MAIN. Dos operandos independientes alimentan el árbol128; el lector numérico usa exclusivamente C=(12,17,18), dirección(1,−1,−1), en datum_tick−2. La diferencia emplea representación afín32−derecho y decodificación carga−32: es preparación de entrada/salida, no una regla aritmética descubierta por el ente.704/704entradas aplicadas.
- P09: tres usos señal→emisión adquirida→operación nativa,3/3aritméticos y558/558entradas aplicadas. La ruta también se observa, pero este primer prototipo ejecuta el operador nativo por el signo léxico; no debe acreditarse todavía selección de procedimiento por la ruta.
- P11: tres peticiones completas en la misma vida: forma adquirida→operador nativo signado→ruta material−1→árbol nativo→resultado→uso material→archivo.3/3resultados correctos y3/3actuaciones;570/570entradas aplicadas. Los archivos tienen47,45y44bytes, exactamente resultado+32 y SHA coherente con el byte determinado por la emisión física posterior. Se localizaron y leyeron los archivos reales en el estado operativo.
- P14: diez accesos de contexto/forma en MAIN mediante un lector fijo de veinte puertas,70/70entradas aplicadas. Incluye las seis asociaciones anteriores y cuatro formas adicionales; diez accesos no equivalen a diez significados humanos ni diez procedimientos.
- P15: cuatro agregaciones correctas4/4 de dos/tres muestras de presencia0/1,704/704entradas aplicadas. El codec no cuenta primero los objetos para introducir el total: cada muestra ocupa su canal; el auditor calcula la suma únicamente para evaluar el resultado. Es conteo preparado y acotado, no cardinalidad adquirida.

El recálculo del corte incluye84,258observaciones RAW y0discrepancias entre campos enteros, decodificadores, resultados cacheados, elecciones materiales y recibos. Los denominadores se mantienen por archivo y vida; no se suman ramas divergentes como una sola trayectoria.

## Lo que depende del aprendizaje y lo que está preparado

Los contrastes léxicos R01/R02, conservados en un único componente portable separado, respaldan cuatro asociaciones nuevas de forma→signo: ambas correspondencias invertidas cambian las respuestas8/8. R02 mantiene8/8accesos anteriores incluso en los controles omitido y desacoplado; estos últimos no producen nuevas emisiones y rechazan consultas en el hub nuevo. El contenido adquirido tiene evidencia causal; la anatomía y el acceso a sectores siguen preparados.

Los operadores de suma, diferencia y conteo son mecanismos nativos preparados, no reglas aprendidas durante P06/P15. La emisión aprendida elige qué operador se usa posteriormente. La representación afín y la conversión resultado+32 son transducción explícita. El observador numérico pertenece al investigador; la actuación física posterior se conserva por separado.

La selección de procedimiento utiliza otra emisión nativa. En P11 las tres rutas son nativas y costosas bajo el entorno declarado. Hay retorno ambiental, pero este corte no acredita todavía un cambio útil de ruta por consecuencias, P2/R2, autonomía general ni iniciativa de consulta. El calendario R3P0 sigue siendo preparación externa; respetar sus fases no es regulación aprendida.

No se demuestra sintaxis ni comprensión libre de español por concatenar una forma y operandos. Se demuestra la cadena acotada que realmente se ejecutó. El cálculo externo, cuando aparezca en un Pxx posterior, debe contabilizarse como herramienta externa y no como aritmética realizada por DEE.

## Herramienta y reproducibilidad

`recalcular_primarios_apd.py` usa sólo biblioteca estándar. Lee los envoltorios gzip de supervisión, después `result.result`, y reconoce lecturas, operadores, actuación, recibos y calendarios. El evaluador calcula a+b/a−b y cardinalidad fuera del participante. Comprueba que el operador emitido provenga del signo físico y no del texto literal. Con `--artefactos` comprueba además los bytes reales conservados localmente.

Referencias parciales conservadas: `RECALCULO_ROOT_CORTE_R01.json` anterior al soporte explícito del nuevo conteo; `RECALCULO_ROOT_CORTE_R02.json` incorpora ese caso sin repetir física. La primera fuente está archivada como `recalcular_primarios_apd_R01_ANTES_CONTEO.py`. Las revisiones del instrumento no son nuevas muestras ni nuevos aprendizajes.
