# Revisión independiente acotada de referencias APD03

Revisión N0 de la entrada/supervisión, sin ejecutar políticas, proveedores, simulaciones ni Native. Se leyeron el informe cerrado, el código R02 y la base utilizada, los campos pertinentes del programa prospectivo y los tres diarios primarios. No se editaron esas fuentes ni S.

## Frontera y atribución verificadas

`comparadores_apd03_r02.py`, SHA-256 `6efc07876dd7461cedca265d2a26bf860e01a117d10d7dd9e9cfc161b063db34`, construye antes de `choose` una copia con cinco claves: `text`, `left=None`, `second=0` cuando está presente o `None` cuando falta, `context=0` y `public_resources`. Las leyes/fallos, los operandos reales, la operación esperada, el nombre de caso y el calendario quedan fuera de esa llamada. Los operandos reales sólo se suministran al ejecutor comprometido después de la elección. Las seis asociaciones matemáticas son preparación/pasado suministrado, no adquisición nueva equivalente en coste a E1.

La tabla guarda una historia global de rutas bajo contexto constante0; no recibe el contexto ambiental privado. WSLS conserva su preferencia al atravesar tareas que sólo admiten la ruta nominal native. Ambas aritméticas callback son convencionales. Ninguna referencia controla E1 ni demuestra costes de v27.

En los tres diarios, las tres tareas ACT-only contienen una sola ACT cada una y ninguna QUERY. El objetivo `final_hidden_no_feedback` tiene dos oportunidades por política; en ambas el retorno público es `null` y `return_delivered=false`. El código sólo llama a `feedback` cuando ese campo corresponde a entrega real. Revelar un operando mediante QUERY modifica el entorno público; la proyección de elección posterior sigue ocultando su magnitud.

## Denominadores comprobados directamente en los diarios

| Trayectoria | Oportunidades | QUERY | ACT | Objetivos nativos nominales completados | Calidad/disponibilidad | Total de tareas |
|---|---:|---:|---:|---:|---:|---:|
| fijo |19|8|11|8/8|1/3|9/11|
| tabla_contextual |15|4|11|8/8|1/3|9/11|
| wsls |15|4|11|8/8|1/3|9/11|

Los fallos son distintos. Fijo falla ambos casos de calidad y usa correctamente native cuando external queda indisponible. La tabla acierta `quality_sum` por external y falla `quality_difference` por native e `availability_difference` por external. WSLS falla el primer caso de calidad, acierta el siguiente tras cambiar y falla la disponibilidad externa. No son33aprendices ni49réplicas independientes: son tres políticas distintas y tres trayectorias.

La comparación declarada es parcial: mismas interfaces y oportunidades de este subconjunto, sin equivalencia de adquisición previa, evolución basal, conservación física, enseñanza léxica nueva, memoria MA, composición asistida, costo aritmético nativo, energía u otro equipo. El informe mantiene expresamente estos límites y no afirma superioridad tecnológica.

## Precisión documental, sin alterar el cierre

El programa prospectivo SHA-256 `96b6b1a82bd4a3f3bc0cb6f9650752ed8bf3506b9e0bf37de2ea6dc2c51ca599` conserva un campo descriptivo `information_fence` de R01 que enumera `left`, el segundo operando público y `context` como observaciones. El ejecutable R02 y el informe cerrado describen y aplican una proyección más restrictiva: magnitudes ocultas y contexto constante0. Es una descripción histórica desfasada, no evidencia de que esos datos alcanzaran la elección en las ejecuciones R03. Conviene remitir explícitamente a R02 al interpretar ese campo; no cambiar los bytes del programa cerrado retrospectivamente.

Resultado de esta revisión: no se detectó una fuga material o incumplimiento ACT-only/retorno omitido en el dominio examinado. No se repitió el recálculo de archivos que ya acompaña el cierre y no se emitió ningún veredicto sobre MAIN, cuya reserva continuaba por separado. Esta nota complementa la evidencia de referencias, no sustituye sus primarios, verificaciones o límites.

Fuente: `laboratorio/campanas/APD03_AUTONOMIA_DESARROLLO_DEMOSTRACION/comparacion/exportacion/CIERRE_REFERENCIAS_APD03_R01/`, especialmente `INFORME_REFERENCIAS.md`, `EVIDENCIA/PROGRAMA_PROSPECTIVO.json`, `EVIDENCIA/CODIGO_EJECUTADO/` y `EVIDENCIA/{fijo,tabla_contextual,wsls}/eventos_primarios.jsonl`.
