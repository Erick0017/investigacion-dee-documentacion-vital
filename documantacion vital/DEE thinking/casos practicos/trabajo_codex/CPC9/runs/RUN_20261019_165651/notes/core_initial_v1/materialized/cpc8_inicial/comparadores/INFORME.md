# Asociación opaca: adquisición, retención y revisión

Capacidad medida: cada método recibió el mismo flujo de66 observaciones presentes (65 asociaciones y una revisión) por mundo y respondió251 consultas explícitas. Son65 formas opacas de dos clases; no65 significados NSM ni65 memorias independientes.

| Método/semilla | Nuevas | Retenidas | Revisión | Total | CPU s | Pared s | Pico job MiB | Estado final almacenado |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| DEE/402817 | 65/65 | 184/185 | 1/1 | 250/251 | 65.422 | 83.133 | 227.74 | 71119 B |
| B1/402817 | 65/65 | 185/185 | 1/1 | 251/251 | 0.047 | 0.275 | 18.74 | 1020 B |
| B2/402817 | 65/65 | 185/185 | 1/1 | 251/251 | 1.234 | 1.591 | 19.19 | 59203 B |
| DEE/591307 | 65/65 | 184/185 | 1/1 | 250/251 | 63.266 | 80.761 | 226.98 | 71064 B |
| B1/591307 | 65/65 | 185/185 | 1/1 | 251/251 | 0.031 | 0.108 | 19.16 | 1020 B |
| B2/591307 | 65/65 | 185/185 | 1/1 | 251/251 | 1.266 | 1.687 | 19.60 | 59196 B |

## Mecanismos e información

DEE conserva un único Runtime N131 hasta920, reanuda su snapshot íntegro y recibe cuatro entradas físicas públicas para la revisión tardía. Dos son contraflujos simétricos de carga cero@1044; la señal5 y el acontecimiento11 llegan@1048. La selección de esa regulación es del protocolo, no una decisión aprendida. Los paneles se emiten en131,393,655,917,1179,1310 y se leen tres ticks después. No hay borrado RAW ni reinicio de clocks. Guardar/cargar preserva RAW/clocks, tick, identidad, recibos y progreso.

B1 conserva el último par observado por forma en un diccionario actualizable. B2 es una MLP65→24tanh→logística con1609 parámetros, SGD0.08 y replay finito≤65 ejemplos:256 presentaciones por observación,16896 por trayectoria. Una revisión sustituye la etiqueta antigua sólo en su memoria de replay, por ser el nuevo acontecimiento observado. La respuesta B2 se calcula por forward de pesos, no consultando el diccionario de replay.

El descubrimiento K8 probó64 y256 presentaciones; ambos resolvieron sus paneles. Se congelaron256 para margen de retención, antes de ejecutar las dos semillas reservadas. No se ajustó el MLP frente a sus resultados K65.

La tabla principal utiliza paraB2 una inicialización/replay privada fija17890331, independiente de las semillas ambientales402817/591307. El primer intento reutilizaba el mismo número para ambos RNG, aunque no reconstruía etiquetas desde él; se conserva completo como incidencia metodológica. La repetición cambió únicamente ese bootstrap, no hiperparámetros, observaciones, decoder ni evaluación. Son réplicas del comparador sobre los mismos mundos, no nuevas reservas ciegas ni aprendizajes DEE adicionales.

## Fronteras y controles de interpretación

El helper revise de4.5 rechaza1048 porque publica la cadencia524. Quedan conservados ambos intentos y sus121 respuestas previas. La continuación fuera de ese helper usa sólo puertos existentes y se identifica como investigación, no como ampliación silenciosa de contrato.

Una restauración exacta no garantiza acceso funcional indefinido. Cuando una sonda aplicada produce sólo carga5 sin dirección cubierta, el resultado es ausente/insuficiente, no el número cero. Las respuestas restantes y la primera revisión se conservan como resultados separados.

El control causal conservó la misma revisión y las otras64 consultas, omitiendo sólo la primera sondaL01@1179. En ambos mundos, L01 volvió a responder+1 con carga21 y dirección[-1,1,0]@1313; con aquella sonda previa sólo quedaba carga5[-1,0,0] sin respuesta cubierta. Los otros64 contenidos respondieron. Esto localiza la pérdida de acceso posterior en la intervención de consulta dentro del protocoloM2 tardío, no en la restauración. No acredita destrucción completa de información ni un límite universal de memoria. Son dos forks diagnósticos, no dos aprendizajes independientes.

Las ventanas exactas27sitios de los controles muestran en1182 un registro16[0,1,0], frente al producto consultado21[-1,1,0] delMAIN guardado. La medición central+Moore26 no cubre todo el cono causal compuesto ni certifica genealogía fuera de esas ventanas; las zonas sin captura permanecen declaradas. Los clocks se conservan como enteros exactos.

Las tareas convencionales emplean consultas que no perturban su memoria; DEE recibe sondas físicas. El coste DEE incluye evolución, instrumentación completa y almacenamiento comprimido; el reloj de pared incluye contención de la máquina. El archivo final DEE está en gzip, los convencionales enJSON: sus bytes de archivo no son una comparación homogénea de memoria. SUMMARY conserva además tamaño nativo decodificado, estadoJSON compacto, buffers y memoria pico; los1609 parámetros flotantes B2 ocupan12872bytes enfloat64 antes de replay, RNG y formato. Este ensayo no mide energía ni rendimiento industrial.

La coincidencia de EVENTS se verifica por hash entre los tres métodos dentro de cada semilla. No se pasan targets futuros a query; sólo el evaluador externo adjunta expected después de obtener la emisión/forward. Los targets de entrenamiento son las consecuencias actuales que constituye la tarea.

## Datos y reproducción

`SUMMARY.json` conserva fórmulas, denominadores, recursos y rutas/hash de primarios. `OBSERVACIONES.jsonl` permite recalcular cada respuesta; RAW y clocks físicos son cadenas exactas, no floats. Los casos originales y sus continuaciones guardan fronteras completas y recibos.

Desde una extracción: instale el WHL oficial incluido en el paquete padre y ejecute `python -I -B comparadores/run_comparison.py --method B1 --seed 402817 --output NUEVO_DIRECTORIO`. B2 aislada usa `comparadores/run_mlp_private.py --method B2 --seed 402817 --output NUEVO_DIRECTORIO_B2`. Para DEE, el comando original reproduce adquisición y el rechazo contractual: la continuación posterior es `comparadores/continue_native.py --seed 402817 --output NUEVA_CONTINUACION`, leyendo el checkpoint original. Utilice el supervisor para llamadas nativas y otro nombre de job. Nunca sobreescriba casos completos.
