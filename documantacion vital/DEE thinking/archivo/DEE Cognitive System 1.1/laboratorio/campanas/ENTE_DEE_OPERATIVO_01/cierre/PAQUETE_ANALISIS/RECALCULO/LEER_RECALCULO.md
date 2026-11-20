# Recálculo archivado EO01

Este instrumento no importa `dee_thinking`, no restaura snapshots y ejecuta cero ticks nativos. Repite cálculos desde los primarios exportados. No sustituye una reproducción del kernel ni una continuación operativa.

```powershell
python recalcular.py --evidencia EVIDENCIA_CAUSAL --salida RECALCULADO
```

`--primarios` es un alias de `--evidencia`. Si las fuentes ordinarias se exportan por separado, puede indicarse `--codigos CODIGO_EJECUTADO`; por defecto se verifican en `EVIDENCIA_CAUSAL/codigo_ejecutado`. Los auxiliares sociales conservan su subcarpeta original `social/codigo_ejecutado` y sus índices propios. El recálculo no abre las rutas absolutas históricas que aparecen como procedencia dentro de los registros.

Sólo requiere Python 3.10 o posterior y su biblioteca estándar. `--evidencia` debe apuntar al directorio que conserva los `.json.gz` originales; admite subdirectorios y no lee `codigo_ejecutado` como datos experimentales.

Qué vuelve a calcular:

- Integridad SHA-256 y tamaño de cada primario. Coteja el JSON analítico con su `stdout` duplicado cuando ambos existen. Cuando está incluido el archivo de fuentes ejecutadas, verifica sus miembros y el hash agregado original.
- Consistencia de RAW uint64 con los campos redundantes state y s_reg; clocks y RAW nunca se convierten a float.
- Lector fijo desde las dos muestras físicas en critical−16 y critical−15: conflicto, abstención, comando y retención máxima de un tick. No utiliza el veredicto, la calibración ni la referencia almacenada para seleccionar el comando.
- Resultado del mundo externo a partir de sus observaciones públicas, su ley archivada y la acción efectivamente ejecutada. Esta evaluación pertenece al auditor; nunca controla al ente.
- Entradas solicitadas, aplicadas, rechazadas y pendientes, conservando los denominadores. Verifica identidad de recibos y tiempos solicitados.
- Ausencia de j0 en los doce suministros genéricos registrados y posterioridad temporal de cada muestra táctil respecto de la ejecución.
- Comparación de los prefijos emparejados, de las diferencias de registros y de la primera oportunidad común posterior. Las revisiones R01 y R02 no se fusionan.
- En protocolo 3, lector B independiente desde los testigos RAW de ambos buses a critical+30: exige state positivo, SEM1, carga exactamente 5, dirección horizontal pertinente y un único paquete. Coteja el testigo duplicado de la traza, el recurso preparado no acumulable, la anulación del actuador B y el desplazamiento mecánico externo. Puntúa A con la calibración anterior a ese desplazamiento; la nueva calibración sólo corresponde a trabajos posteriores.
- Contadores FIFO de `ente-tarea`, repetición exacta del mismo trabajo pendiente, avance sólo por consecuencia útil efectivamente ejecutada, primeros intentos y pendientes reales. El calendario de reintentos pertenece al entorno. Las referencias de acción fija/alternante de la cola son cálculos descriptivos posteriores, no nuevos experimentos nativos.
- Pulsos y consultas sociales auxiliares CF anteriores en su propio inventario, sin sumarlos a las experiencias de MAIN ni confundirlos con episodios nuevos de retorno externo.
- Guardado y primera observación de la continuación en otro proceso. Separa el historial `backlog` de intentos fallidos del cursor FIFO: dos errores históricos no significan dos trabajos pendientes cuando la cola terminó.

Las salidas son métricas por caso, no una puntuación global de cognición. Una bifurcación no cuenta como aprendizaje independiente; una consulta no constituye otra réplica. Los primarios de pulsos materiales sin episodio de servicio se enumeran sin atribuirles éxito funcional.

Los controles sin retorno tienen necesariamente una muestra táctil menos: se informa esa diferencia. El brazo desacoplado conserva la dosis táctil y cambia su postura informativa. Corte y sham son intervenciones diagnósticas, no acciones autónomas del ente. La válvula social del protocolo 3 es una asistencia externa preparada sobre un mundo compartido; no equivale a una nueva actualización directa del contexto ocupado de A ni a una elección aprendida de cuándo proporcionar el recurso.

Límites: la igualdad al bifurcar se coteja mediante hashes físicos globales archivados. Entre checkpoints, las comparaciones cubren los testigos locales efectivamente registrados, no todos los sitios en cada tick. El lector y los codecs son preparación instrumental; el cambio de referencia puede depender de experiencia sin demostrar una política general de control o recuperación autónoma. La ausencia de accesos denegados en la frontera Python no equivale a una prueba formal de seguridad del sistema operativo. Los archivos de ejecución ordinaria se verifican por el índice de su carpeta `codigo_ejecutado`; los hashes de scripts auxiliares se conservan como procedencia y deben cotejarse con las fuentes auxiliares incluidas en el paquete si se necesita reproducirlos.

Si algún cálculo discrepa, el programa lo registra en `mismatches` y termina con código 1. Nunca corrige el primario ni rellena una respuesta.

La comprobación `INDEPENDENCIA_RECALCULO.json` registra una copia exportada y un proceso nuevo en otra ruta de la misma computadora. Su frontera de archivos prohíbe abrir el sistema DEE original. Produjo un JSON de recálculo idéntico byte a byte, sin importar el motor ni avanzar física. Esto no es una prueba en otro equipo ni reemplaza la comprobación independiente del paquete operativo.
