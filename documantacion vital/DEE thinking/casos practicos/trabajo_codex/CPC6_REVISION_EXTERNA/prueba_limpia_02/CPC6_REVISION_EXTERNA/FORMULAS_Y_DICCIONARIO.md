# Datos, fórmulas y límites de recálculo

## Tablas

- `ENSAYOS.jsonl`: un registro por ensayo científico, familia pública, modalidad, condiciones, genealogía declarada, duración y compromiso criptográfico del primario privado. La ausencia de vínculo público unívoco no se sustituye por una genealogía supuesta.
- `ENTRADAS.jsonl`: solicitudes agrupadas por función externa, nivel opaco, tiempo solicitado/aplicado, operación, admisión y procedencia heredada. `cantidad` es el peso de la fila. El suministro técnico no detallado conserva sus cantidades y admisiones, pero omite agenda y codificación.
- `RESPUESTAS.jsonl`: lecturas de decoders ya publicados o mediciones instrumentales reportadas. Una lista vacía significa que ese decoder no produjo una respuesta clasificada en esa lectura. No equivale a respuesta numérica cero, ausencia de memoria o ausencia de actividad.
- `PREDICCIONES_TEMPORALES.jsonl`: emisión y objetivo relativos cuando están registrados. No se exporta una interpretación nueva de emisiones físicas para inventar valores predictivos.
- `INCIDENCIAS_Y_REPRODUCCIONES.jsonl`: errores y controles técnicos, sin comandos, rutas privadas ni traceback. No son ensayos científicos adicionales.

Los valores `null`, lectura no publicada, lista vacía, rechazo y ambigüedad tienen significados distintos. No deben colapsarse en un único fallo. Los códigos de nivel sólo permiten comparar igualdad/diferencia, no hacer aritmética de intensidad. Los valores de clase son convenciones de lectura externas, no campos microscópicos.

## Recuentos

Número de ensayos = número de IDs públicos únicos en ENSAYOS. Preparaciones, ramas y continuaciones se suman por separado. El recuento esperado del índice fuente es129=94+29+6. Los diez ensayos de componentes son parte de las94 preparaciones, no se agregan otra vez. Las familias son grupos documentales, no capacidades ni réplicas estadísticas.

Solicitudes registradas por ensayo = suma de `cantidad`. Solicitudes nuevas = la misma suma sólo cuando `heredada_del_padre` es falsa. Las solicitudes heredadas pueden aparecer en varias ramas y no deben sumarse como experiencias independientes.

Fracción aplicada entre finalizadas nuevas = aplicadas nuevas / total de nuevas con estado distinto de programada. Si el denominador es cero, el resultado es nulo. Los estados no habituales permanecen como otra categoría registrada; no se reclasifican como aplicados.

Latencia de admisión = tiempo aplicado menos tiempo solicitado, sólo para entradas aplicadas con ambos tiempos exportados. La media ponderada divide la suma de latencias multiplicadas por `cantidad` entre el número correspondiente de solicitudes. No incluye agendas técnicas omitidas ni mide latencia de respuesta.

## Respuestas y retención

Por variable se cuentan filas observadas y ensayos únicos con medida numerable o alguna salida. No se usan los múltiples instantes de una trayectoria como muestras independientes. La presencia de salida no equivale a acierto; una medición instrumental de disponibilidad no equivale a una respuesta semántica.

En el panel reservado se revisan tres ventanas públicas: primera forma, segunda forma y consulta posterior de la primera. El testigo de secuencia exige salida clasificada de ambas formas y la misma clase de la primera en su consulta posterior. Sólo FORMA_01 y FORMA_01_REMOTA revisada comparten el codominio operacional declarado para esta comparación. FORMA_02 y FORMA_01_REMOTA_ORIGINAL no se equiparan a él. Los tiempos y IDs utilizados aparecen en los datos y en CONTROLES_Y_RESERVAS; no son constantes de la ley del modelo.

El denominador de ese panel son los cinco testigos reservados y controles explícitos. No es una estimación poblacional de retención ni de significados dominados. Se conserva también la omisión deliberada de consulta y la enseñanza desacoplada.

En cada contraste se comparan los conjuntos de clases de la variable y ventana declaradas. Un conjunto vacío no se sustituye por una clase. Una lectura no publicada produce comparación nula. El factor del contraste fue asignado experimentalmente; la exportación no certifica que fuera la única diferencia física.

Horizonte predictivo = objetivo relativo menos emisión relativa. Puede comprobarse que la emisión precedió al objetivo. El acierto predictivo no se recalcula cuando no hay valor predictivo decodificado publicado en la proyección. No se infiere a partir del contexto o de la respuesta posterior.

`RECALCULAR.py` implementa estas operaciones, escribe CALCULOS y COMPARACIONES o verifica su igualdad textual mediante `--verificar`. Requiere Python estándar3.10 o posterior. No modifica entradas ni interpreta estados del participante. Puede ejecutarse con `python -I -S RECALCULAR.py --verificar`, sin cargar paquetes instalados.
