# Manual de reconstrucción

## Dependencias y aislamiento

Use CPython 3.13 x64 en Windows. El WHL oficial está incluido una sola vez. El ejecutor instala desde esa copia con `--no-index --no-deps --no-cache-dir`; no descarga ni recompila. No sitúe el directorio de resultados dentro de la extracción.

`reproduccion/desde_cero.py` verifica el manifiesto, CRC y bytes del ZIP exacto, crea un entorno nuevo, materializa las dependencias seleccionadas y ejecuta cada familia en su propio proceso. `-I -B` evita PYTHONPATH y cachés de bytecode. Un audit-hook rechaza aperturas de archivos Python fuera del paquete, el material recuperado, los resultados, el intérprete y Windows. No es un sandbox de sistema operativo; esa limitación se declara.

El materializador valida gzip, base64, tamaño y SHA-256 de todos los blobs. Rechaza rutas absolutas, `..`, unidades y colisiones. Un archivo existente diferente no se sobrescribe.

## Familias

| Familia | Contrato recuperado |
|---|---|
| cpc1 | Ocho preguntas originales CP01. C07 reutiliza C05 como diagnóstico, no añade una simulación. |
| cpc2 | Pronóstico nativo anterior al objetivo, hábitat independiente, experiencias emparejadas/omitidas/desacopladas y continuación exacta. |
| sem01 | Experiencia física, sensor actual declarado, señal sola, anticipación y uso con controles y reservas históricas. |
| cpc4 | Comunicación A/B/C/D, contraflujo fijo y control de igual aporte fuera de ruta. |
| cpc5 | Producto común continuo, adquisiciones posteriores y respaldos adquiridos, cortes selectivos y sham. |
| cpc6 | U0 original, comparación, elección preparada P/Q, comunicación, asociación adicional y lector remoto renovado. |
| cpc7 | Cuatro trayectorias originales hasta472, revisión de L03 y relaciones no modificadas. |
| mcts | Cinco mundos originales de35 soportes y131 interfaces hasta616; no se suman sus repertorios. |
| repertoire | K65 N131 separado;32+33 adquisiciones, tres rondas, revisión finita y controles adversos preservados. |
| rca | Dos mundos de72 soportes con regulación causal más corte/sham. Regula un comparador añadido, no retroactivamente el MCTS menor. |
| count | Asociación auxiliar B-only calibrada, control sin forma, reserva y restauración94→171. |
| product / product_extra | Regresiones técnicas de API y MBP4, incluidas semillas históricas declaradas. |
| policy / native_loop / central | Política finita R14 y los dos contratos originales CPC3 de vida/comparación. Las anotaciones pasivas posteriores se conservan aparte, sin inventarlas en las referencias antiguas. |
| capacity / longitudinal | CPC5 original K65 y adquisición32+33, controles sin evento/desacoplados y consulta temprana omitida. |
| ordered / stream / network | Orden AB/BA, cortes/sham, intervalos y referentes nuevos, red A1/A2/A4 y cambio de roles. |
| architectures / bridge | Cribado original CPC6 y puente físico entre memoria relativa y móvil. Se declaran recursos no igualados. |
| retain_early / retain_word / retain_late | Dieciocho continuaciones diagnósticas desde ocho padres históricos exactos CPC6, conservando estado, clocks y colas. |
| need / missing | Pregunta por comparación y perfil de ausencia preparado; no se fusionan retrospectivamente en un mismo U0. |
| qfm / l15 | Forma móvil con acceso remoto y diagnóstico causal de soporte transformado/acceso alternativo. |
| social | Cuatro vidas CTS y tres diagnósticos del mensaje formado: adquisición propia, transporte, adquisición de receptor simple y uso posterior. |
| initial_cpc8 | Cuatro vidas N131 del primer CPC8: SOC_I21, revisión L01 fuera de ruta, historia desacoplada y reserva negativa. No son el posterior MCTS N67. |
| core06 / core07 (opcionales) | Protocolos originales de arrays RAW/clocks, portados a la transición oficial4.5; requieren NumPy2.2.6 declarado. No se atribuyen colas Runtime a los experimentos originales que no las tenían. |

Los archivos `MEASUREMENTS.json`, `RESULTADOS.json`, snapshots y logs nuevos quedan en la carpeta de recuperación. El informe señala cada comando, código de salida, tiempo, comparación y ámbito. No se infiere una capacidad porque el proceso termine en cero.

El panel predeterminado ejecuta32familias en procesos separados; puede seleccionar una con `--families ordered` o una lista separada por comas. `product_persistence` es una selección técnica adicional para repetir sólo las ocho pruebas afectadas por infraestructura de guardado. La prueba completa ya incluye esas pruebas dentro de `product`.

Para las34familias, añada `--include-legacy-cores --numpy-root RUTA_SITE_PACKAGES --total-seconds 5400`. El worker de CORE06/07 importa primero el WHL4.5 aislado y verifica su extensión, luego añade la ruta NumPy explícita y comprueba versión2.2.6. Instale esa dependencia normalmente en un Python3.13x64 compatible; consulte `DEPENDENCIAS.json`. No necesita ningún dato científico externo ni ZIP histórico. El límite es relativo a cada invocación; no reutiliza el deadline de CPC9.

## Cómo interpretar un fallo

Distinga un error del entorno, un archivo ausente, un rechazo del instrumento, diferencias de metadata, una lectura indeterminada y una discrepancia física. Los uint64 no deben convertirse en floats. Una diferencia de ruta o repr del host no se oculta, pero no se equipara a una diferencia RAW/clocks.

Las correcciones de los auditores originales de esta construcción se conservan en `verificaciones/INTENTOS_TECNICOS_Y_CORRECCIONES.json`. No modificaron recetas, decoders ni estados para convertir resultados adversos en aciertos.

## Qué sustituye el Core

Únicamente los contratos aprobados en la prueba limpia pueden recuperarse sin los CPC anteriores. El almacén preserva muchas otras implementaciones y evidencias para investigación, pero no promete reconstruir cada tick, cada snapshot ni cada interpretación histórica. Consulte la matriz individual y el informe de pérdida de información antes de retirar cualquier fuente original. Esta tarea no autoriza retirar los originales.
