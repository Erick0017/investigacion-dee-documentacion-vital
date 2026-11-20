# Revisión local de una relación mientras otra sigue utilizable

Dos preparaciones nuevas consiguieron cambiar la correspondencia direccional de L01 y conservar el uso de L02 en el mismo Runtime. Cada método tuvo un piloto, un sham de igual dosis y dos reservas congeladas antes de ejecutarlo. Los seis tratamientos expresaron las dos correspondencias esperadas después de la revisión: seis lecturas nuevas de L01 y seis de L02, todas admitidas y cubiertas por el mismo decoder.

La tarea fue finita y común: adquirir dos relaciones en0; consultarlas en67→70; presentar una consecuencia opuesta para L01 en268→271; volver a consultar ambas en335→338. Las consultas anteriores modifican sus portadores; no se restauró un estado anterior para recibir la experiencia nueva. L02 no fue reenseñada. Las reservas cambiaron historia, consulta y traslación, no sólo repitieron los mismos ticks como nuevas muestras.

## Dos mecanismos distintos

M1 añadió una segunda vía de la consecuencia actual. En la experiencia nueva entraron dos docentes de carga11 y una señal de carga5. El código no leyó la clase anterior para calcular una compensación: la selección de ambas vías sólo utiliza la consecuencia presente mediante una codificación fija. El resultado es una revisión de la respuesta por un encuentro con dosis adicional. Las cargas finales de L01 fueron53,61 y69 en piloto y reservas; son distintas del método siguiente y no se presentan como mejora gratuita con recursos iguales.

M2 emitió dos contraflujos de carga cero en264, uno para cada una de las dos rutas anteriores posibles. Ambos se programaron con independencia de qué dirección hubiera adquirido el portador. En267 el registro de la ruta ocupada conservó su carga y quedó con dirección cero. En268, la **misma coordenada** estaba vacía; esto se comprobó en los vecindarios guardados, no siguiendo erróneamente una trayectoria móvil después del encuentro. Las cargas neutralizadas fueron21,25 y29. La experiencia ordinaria nueva produjo después una relación que la consulta338 utilizó con cargas21,25 y29, respectivamente.

M2 es una regulación externa programada cuyo efecto se realiza por v27, seguida de reaprendizaje local. Conserva la otra relación y la continuidad del mundo; no conserva simultáneamente el contenido antiguo y el nuevo de L01. No es una política que aprendiera por sí misma cuándo intervenir.

## Controles y reservas

Los shams conservaron dosis, direcciones y tiempos de solicitud de cada tratamiento, pero enviaron los auxiliares por otra capa vacía en esta preparación K2. En ambos, la nueva consulta de L01 fue rechazada por ocupación: el registro observado tenía dirección `[-1,0,0]` y carga37. L02 seguía admitida y utilizable con carga26. Este resultado separa la contribución de la ruta auxiliar; un acceso ocupado no se convierte en una afirmación de pérdida universal del conocimiento.

R101 invirtió la historia y la consecuencia nueva, consultó con9 y trasladó el aparato. R211 utilizó otra segunda relación, consulta13 y otra traslación. Ambos métodos conservaron dos respuestas cubiertas y correctas en las dos reservas. El decoder no cambió después de observar los pilotos.

## Telemetría y alcance

`INDEX_pilot.json` e `INDEX_reserve.json` enlazan los ocho primarios con hashes. Cada `MEASUREMENTS.json` conserva llamadas, recibos, lecturas exactas, vecindarios de los encuentros y cinco snapshots. Hay32 consultas:30 aplicadas y dos rechazadas por ocupación; los rechazos pertenecen a los shams. Hubo92 solicitudes en total,90 aplicadas. Ocho restauraciones técnicas comprobaron igualdad física y operativa en el mismo proceso; no generaron las respuestas científicas ni cuentan como ocho individuos adicionales.

La implementación pública de estos candidatos es `src/update_methods.py`. `UpdateSession.create` prepara las interfaces desdeT0, `schedule_revision` agenda entradas sin avanzar ni leer respuestas anteriores, y `save/load` preserva el estado completo de este protocolo. El runner de esta comparación restringe K a2. Una integración K16 o65 requiere mediciones nuevas; en particular, la capa offpath del sham no debe reutilizarse sin comprobar que esté libre de otros componentes.

Se comprobaron un cambio y un panel posterior por preparación. No se acredita reutilización ilimitada, selección autónoma del regulador ni dos significados NSM. El hallazgo útil es concreto: dos maneras físicas de superar la interferencia de una revisión directa, conservando acceso a otra correspondencia adquirida.

Para reproducir los pilotos en una salida nueva, desde CPC7 y mediante su supervisor:

```text
.venv\Scripts\python.exe -I -B src\supervisor.py --name repetir_metodos --timeout 600 -- .venv\Scripts\python.exe -I -B src\update_methods.py --config configuraciones\update_methods.json --out resultados\repeticion_metodos --group pilot
```

El supervisor de la campaña usa su presupuesto original. Una reproducción posterior autorizada debe utilizar el supervisor apropiado para esa ejecución; no debe reiniciar silenciosamente el plazo de este expediente.
