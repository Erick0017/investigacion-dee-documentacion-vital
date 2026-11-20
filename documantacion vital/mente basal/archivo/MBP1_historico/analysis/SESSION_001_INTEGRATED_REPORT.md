# Mente Basal — sesión 001, corte T_ref

## Identidad y alcance

Mundo principal: `MENTE-BASAL-001`. Sesión: `SESSION-001-20261005T035032Z`. Motor: DEE thinking 2.2.0 sobre el kernel DEE v27 congelado. El corte científico es T_ref = 64, publicado a `2026-10-05T03:53:20.552+00:00` (`2026-10-04T21:53:20.552-06:00`). X0 fue guardado antes de programar entradas. Después se conservó una sola trayectoria principal; pilotos y controles permanecieron en mundos independientes.

El proceso propietario fue reiniciado una vez, pausado en la frontera T64, para que el source activo incorporara dos correcciones puramente operativas anteriores al paquete: tolerancia a una lectura concurrente de `status.json` y validación no destructiva de IDs de recolección. El checkpoint mantuvo RAW, clock, tick, colas y recibos. No se cambió la transición v27 ni se reinyectaron experiencias.

## Hábitat y experiencias

La retícula toroidal N=127 contiene un linaje C7H03 preparado, cuatro encuentros ambientales de fase con soportes semantic=4, un portador de actualización reutilizado, una ruta de materia móvil con encuentro 31+37 y una segunda ruta contextual con suministro 29. Todo pertenece al mismo Runtime.

Se admitieron 23 de 23 entradas, sin rechazos: 19 preparadas en t0 y cuatro acopladas explícitamente en t40. El segundo bloque mantuvo la continuidad del primer bloque; no hubo reset de clocks, limpieza del paisaje ni reconstrucción del linaje.

## Evolución medida

Los cuatro encuentros ambientales modificaron el mismo portador en pasos 23→24→25→26→27. El encuentro de materia móvil produjo 68 en t16. El linaje expresó 4149 en t34; la consecuencia ambiental 27 llegó a la revisión de t38 y produjo 4176; las consultas comunes produjeron 4181 en t46 y 4184 en t58. En la ruta contextual separada, la entrada tardía 11 se encontró con el suministro 29 y produjo 40 en t48.

Los controles diagnósticos fijaron el mecanismo en mundos separados. Al retirar las ocho fuentes ambientales, el portador quedó en 23 y la revisión en 4172: diferencia 4 respecto del tratamiento. Al retirar sólo la experiencia contextual tardía, el hub quedó en 29 en vez de 40: diferencia 11. El control contextual no cambió la cadena principal hasta t58, lo que mantiene separadas ambas lecturas en este aparato.

Esto reproduce una mediación ambiental preparada y su uso posterior finito. No demuestra que el hábitat haya descubierto autónomamente la regularidad, que haya aprendido a generar teachers, ni que el valor contextual 40 haya sido retenido y utilizado más adelante. La nueva ruta contextual queda como interacción causal observada, no como aprendizaje contrastado.

## Perfil de aprendizaje prudente

- Adquisición: no establecida en este corte; interfaces, rutas y relación base fueron preparadas.
- Dosis: 19 entradas t0 y 4 entradas t40 efectivamente admitidas.
- Retención/uso: la contribución ambiental +4 siguió disponible en la revisión y dos usos posteriores de la misma familia.
- Especificidad: el corte ambiental eliminó exactamente esa contribución; el corte contextual eliminó 11 en el hub separado.
- Transferencia: no ensayada fuera de esta geometría y familia de consultas.
- Revisión/interferencia: no se presentó una regularidad conflictiva.
- Uso causal pendiente: no se ejecutó una segunda interacción que utilizara el nuevo contenido 40.

## Validación técnica

La batería A–H verificó continuidad exacta frente a guardar/cerrar/cargar, replay sin duplicar entradas, entrada y recibo, pausa sin ticks, archivo no destructivo, aislamiento de ramas, rechazo de checkpoint inválido y observación pasiva. RAW y clock en T64 coincidieron entre Lazy y DenseSequential.

La batería operativa aislada I–L verificó la separación del worker del Job destructivo del lanzador, corte vivo con segmento nuevo, parada segura por presupuesto reducido y exclusión de segundo escritor. Una extracción limpia instaló el WHL incluido, reprodujo 23 entradas con igualdad exacta de RAW/clock/tick/recibos y continuó un tick en un linaje de prueba aislado.

En T_ref el proceso usaba aproximadamente 96.8 MB de working set. El checkpoint completo medía 32,777,521 bytes. Los 64 ticks contabilizaron 2.0207362 s de kernel (≈31.57 ms/tick). Un guardado completo medido tardó 1.098 s (≈28.47 MiB/s, incluyendo coordinación y verificación). El archivo del mundo e historia ocupaba 229,514,924 bytes y quedaban 858,711,576,576 bytes libres.

## Continuación autorizada

El corte es inmutable. El mismo linaje abre un segmento posterior en T64. La liberación autónoma fija una sola vez un máximo de 16 horas y un límite de 900,000 ticks desde T_ref, además de 1 GiB de working set, 1.5 GB de archivo, reserva de disco y un hilo. Después de agotarse los eventos preparados, el estado se rotula como evolución libre; horas adicionales no constituyen por sí mismas aprendizaje.

La continuidad sólo está comprobada mientras Windows permanezca encendido y sin suspensión, la unidad D: esté disponible y el proceso no sea terminado. No se instaló servicio, arranque tras reinicio ni acceso de red. La recolección posterior está implementada y corta archivos inmutables sin devolver ramas diagnósticas al mundo principal.
