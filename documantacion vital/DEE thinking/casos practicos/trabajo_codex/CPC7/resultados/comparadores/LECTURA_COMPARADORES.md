# Comparadores convencionales: resultado finito y revisable

Los dos comparadores adquirieron correspondencias de demostraciones observadas y se evaluaron sobre los mismos flujos reservados. B1 conservó y actualizó las claves ensayadas; B2 mostró el intercambio entre mantener lo anterior y cambiar una relación. No se suministraron las respuestas reservadas a sus métodos de predicción.

## Qué se ejecutó

54 trayectorias de modelos: 12 pilotos y 42 reservadas. Son 24 flujos de entrada distintos realmente ejecutados, 18 de reserva. Los mismos flujos se compararon entre modelos: no son54 historias ambientales independientes. Se realizaron además dos restauraciones técnicas en procesos distintos y un self-test de gradientes; éstos no añaden preparaciones científicas.

B1 mantiene la última consecuencia emparejada por clave observable. Su representación de clave y la invariancia a un intervalo positivo en la tarea de orden son decisiones explícitas del programador. No conoce la correspondencia de cada señal antes de la experiencia.

B2 es un MLP convencional de24 unidades tanh y una salida sigmoide, implementado con Python estándar. Recibe identidades one-hot, contexto observable y, para el frente de orden, dos slots con acontecimientos y tiempos. Usa96 actualizaciones de8 ejemplos por experiencia, tasa0.2 y memoria FIFO32 con muestreo uniforme. El brazo sin replay conserva el mismo presupuesto de ejemplos de gradiente, repitiendo únicamente el ejemplo corriente. No reproduce un gran benchmark neuronal.

## Reservas emparejadas

| Tarea y denominador | B1 | B2 replay | B2 sin replay |
|---|---:|---:|---:|
| Asociación directa,80 consultas en2 historias |80|78|48|
| Asociación condicionada por contexto,80 en2 historias |80|79|53|
| Orden/contexto,12 en2 historias |12|11|8|

Son conteos de consultas correctas, no réplicas independientes ni número de significados. La cobertura fue completa en estos brazos emparejados. En los controles virgen y desacoplado B1 devolvió ausencia, mientras B2 continuó emitiendo clases desde su inicialización: esos aciertos parciales se conservan y no se denominan aprendizaje.

En asociación directa, B1 retuvo las ocho relaciones iniciales después de añadir otras ocho, actualizó L01 y conservó las otras15 en ambas historias. B2 con replay retuvo esas ocho y luego las otras15, pero respondió con la asociación anterior a L01 tras su revisión en las dos reservas. No se ocultó ese resultado en el78/80 agregado. El brazo sin replay actualizó L01 en ambas historias y retuvo19/30 de las otras15, frente a30/30 con replay. La tarea contextual permitió a B2 actualizar L01 y expresar16/16 en el panel final de ambas historias; antes hubo un error de retención en una de ellas. El frente de orden prueba un dominio de dos tokens y dos contextos, no razonamiento temporal universal.

## Presupuesto y continuidad

Las exposiciones nuevas, repeticiones de gradiente y muestras de replay tienen contadores separados. En cada historia directa emparejada B2 procesa17 exposiciones,1632 actualizaciones y13056 ejemplos de gradiente; no son13056 experiencias del entorno. La memoria del proceso se midió con PeakWorkingSetSize de Windows, aproximadamente20–21MiB en estos trabajadores, incluido el intérprete. Los tiempos CPU de trabajos muy pequeños tienen resolución limitada y la carga simultánea afecta al tiempo de pared. No se infieren consumos energéticos ni ventajas de hardware.

Tras restaurar cada modelo desde la frontera anterior a la revisión, las16 consultas siguientes y todo el estado final coincidieron exactamente con la trayectoria original. La restauración conservó pesos, tabla, buffer, RNG y progreso; no volvió a enseñar las correspondencias.

## Datos y reproducción

`COMPARADORES_CALCULOS.json` contiene el registro explícito, hashes, medidas por caso, recursos, paneles y fórmulas. Cada subcarpeta de perfil conserva `TRAJECTORY.json`, `EVALUATION.json` y checkpoints. Las predicciones se guardaron antes de abrir el evaluador. Los fixtures y sus objetivos separados están en `configuraciones/comparadores/fixtures_v1`; su inventario se generó antes de los pilotos. `PILOT_DECISION.json` conserva la selección de dos configuraciones y todos sus errores.

Desde CPC7, un nuevo recorrido puede ejecutarse con Python estándar3.13 mediante `src/comparadores/batch.py --split RESERVED --model B2 --profile REPRODUCCION_B2 --config configuraciones/comparadores/B2_FINAL_V1.json`. El nombre de perfil debe ser nuevo. La supervisión usa el presupuesto vigente de la campaña; fuera de una campaña autorizada puede ejecutarse `run.py` por caso con un timeout propio. Los comparadores no importan DEE ni carpetas históricas.

## Antecedentes que guiaron el diseño

[Dohare et al., Nature2024](https://www.nature.com/articles/s41586-024-07711-7) separan la plasticidad para adquirir tareas nuevas de la conservación de conocimientos previos. Este ensayo corto no acredita ni refuta su resultado de largo horizonte. [Prabhu et al.,2023](https://arxiv.org/abs/2303.11165) motivan registrar el cómputo real y contrastar una memoria muestreada uniformemente; su clasificación empírica de métodos no se traslada automáticamente a DEE.

La comparación con DEE se hará sólo en los segmentos cuyos acontecimientos, información y ventanas realmente se hayan ejecutado. Distinta admisión, consultas que alteran al individuo y recursos físicos diferentes son resultados que deben permanecer visibles. Estas cifras no deciden por sí solas una superioridad general.
