# PI03 — Extensión útil R02, posterior a la calibración mecánica

Estado: propuesta ejecutable parcial; **sin ejecución Native ni prueba del dispositivo por su autor**. No modifica R01 sellado. Código separado: `codigo/pi03_dispositivo_diferido_R02_PROPUESTA.py` (sólo biblioteca estándar). El ejecutor puede adoptar, recortar o rechazar esta extensión antes de congelar la reserva; el resultado de calibración decide si su enlace físico existe.

## Tarea central

Dos actuadores binarios fijos abren dos conducciones materiales del mismo dispositivo. En cada bloque sólo una conducción está conectada al receptor. Una actuación coloca una cápsula comprimida real en la conducción elegida. Después de una demora fija, el receptor conectado la transforma en un producto descomprimido real, verificable por contenido y SHA-256; la otra conducción termina en un depósito de rechazos. Una ausencia de acción tiene depósito propio y no obtiene producto.

El dispositivo no elige una actuación. Recibe exclusivamente la salida física decodificada de DEE, aplicada por un transductor fijo. Su ley de conexión es un estado privado del entorno, fijado antes de evaluar, que cambia entre bloques. No se entrega al participante el signo conectado, la semilla, el índice del caso, una respuesta deseada ni el futuro. El resultado genérico de su actuación anterior sí es información perceptible suficiente para distinguir historias. No se exige anticipar la primera inversión no señalada: la primera pérdida tras ella es informacionalmente inevitable.

Se mide producto útil real, no un contador de recompensa. La cápsula de 64 bytes es un recurso externo del montaje, no energía, alimento o termodinámica de DEE. La descompresión es una operación mecánica del dispositivo, no una capacidad cognitiva atribuida a E1. El aprendizaje que se busca es **seleccionar una conducción funcional mediante consecuencias diferidas**.

## Ciclo y cronología exacta

1. El query fijo del nuevo R06 produce una salida en q+6. Cero material se traduce al actuador fijo −1 de arranque según R01; NULL no actúa. La consulta y el momento de oportunidad son asistencia P0.
2. El actuador lleva la cápsula al depósito `inflight_minus`, `inflight_plus` o `inflight_silence`. Éste es un efecto material inmediato, que todavía no es un producto útil.
3. Un tick después se inyecta la copia eferente inversa R01. La elegibilidad recorre físicamente N=67 sitios por vuelta mientras el mundo continúa.
4. En `outcome_injection_tick−1` el dispositivo ejecuta su consecuencia diferida: producto real si la conducción está conectada, rechazo real si no. La cápsula de devolución contiene `failed: bool` y medidas del producto; **no contiene motor, ruta ni banco**.
5. Ese `failed` selecciona únicamente uno de los dos puertos genéricos ya congelados. Se programa la entrada en la frontera futura `outcome_injection_tick`, se observa la composición en E y el contacto en la referencia. No se usa la actuación pasada para escoger el puerto de penalización.
6. La oportunidad posterior utiliza la nueva salida física. Si la historia material cambió la elección y ésta produce más productos frente a controles, hay selección adquirida útil dentro de este dominio.

Para k vueltas, la eferencia llega al hub 67·k ticks después de su admisión; la consecuencia ambiental ocurre 67·k−1 ticks después de leer/aplicar la actuación. El retorno llega al hub dos ticks después de la consecuencia. Esta convención debe conservarse en los recibos; no se presentan todas las latencias como un único número ni como respuesta instantánea.

`DelayedFeeder.begin(actual_motor,action_tick,ready_tick)` mueve la cápsula. `complete_due(tick)` exige el plazo exacto y sólo devuelve una consecuencia genérica. El estado externo conserva su conducción pendiente porque una interfaz física tiene estado; ese dato no es una tabla cognitiva ni se consulta para asignar un banco al retorno. El puente de crédito recibe únicamente `complete_due(...)["failed"]`.

El código protege estados inciertos antes de efectos de archivos y rechaza reintentos. No borra cápsulas: conserva las comprimidas consumidas, los productos y los rechazos. No accede a red, shell, secretos ni rutas aportadas por el participante. Todo permanece bajo el directorio diagnóstico escogido por el ejecutor.

La consecuencia queda además en `feedback_pending` hasta conciliar su recibo Native exacto. `mark_feedback_scheduled(id,tick)` registra un ID ya creado, sin volver a enviarlo; `reconcile_feedback(receipt)` sólo acepta ese recibo. Un rechazo bloquea oportunidades nuevas y se conserva. La cápsula de devolución no guarda la actuación anterior. El propietario existente debe guardar coherentemente entorno, agenda/recibos Native y transporte SQLite; este helper no sustituye ese contrato ni reenvía una operación ambigua tras reapertura.

## Desarrollo y reserva proporcionados

Tras calibrar y congelar la polaridad física, se propone un desarrollo breve de seis oportunidades: tres con conexión +1 y tres con conexión −1. Demora de una/dos vueltas. La elección inicial fija −1 queda inicialmente desfavorecida para evitar una demostración basada sólo en haber acertado por preparación.

La misma candidata continúa, sin restablecer referencias, a una reserva de ocho oportunidades: cuatro con una conexión y cuatro con la opuesta, con tres/cuatro vueltas. El orden de conexiones y las demoras deben fijarse antes de inspeccionar la reserva. Un intervalo o cambio de contingencia nuevo es transferencia local de esta regla, no generalización universal.

Como mínimo: candidata con devolución real; control emparejado que recibe siempre la consecuencia no punitiva/disposal (misma cantidad de entradas y elegibilidad consumida); actuación anulada después de formar salida. El control sin eferencia y el desacoplado de R01 son mecánicamente importantes, pero sus residuos impiden tratarlos como una condición limpia renovable sin observarlo: no reutilizar sus futuros como si se hubieran limpiado.

Referencias externas separadas, con las mismas oportunidades y observación de consecuencias: siempre −1, siempre +1, alternancia fija y mantener tras acierto/cambiar tras fallo. Nunca controlan DEE. Su aritmética se puede recalcular documentalmente después. Una regla simple puede igualar o superar a DEE y debe informarse; no impide reconocer un mecanismo local útil.

## Criterios propuestos, que el ejecutor debe congelar antes de la reserva

- Mecánica: el mismo retorno genérico modifica bancos distintos según eferencias opuestas; se mide la dirección/contacto, no sólo un hash diferente. La lectura fija cambia de modo coherente en copias comparables.
- Función: cada éxito corresponde a un producto existente con longitud y hash correctos. NULL, rechazos de entradas, acciones inválidas y cápsulas agotadas tienen denominadores separados.
- Historia: después de una pérdida real, la selección posterior cambia más que en el control disposal y obtiene una consecuencia útil. Se registra por episodio, no se suman clones como réplicas independientes.
- Retención: después de varios éxitos, la conducción continúa utilizable sin volver a entregar la selección correcta. Cambiar por repetición del calendario sin dependencia de retorno no satisface el criterio.
- Reserva: beneficio acumulado frente a mantener una actuación fija y frente al control sin crédito; desglose por bloques y demora, falsas retiradas, intentos perdidos y coste de adquisición. No exigir una superioridad estadística imposible con ocho oportunidades, ni ocultar resultados adversos.
- Conservación/adopción: panel heredado proporcional y uso nuevo después de guardar/cerrar/reabrir en el corte real. Una regresión material del contrato principal impide promover, aunque el mecanismo científico se conserve como receta.

Presupuesto orientativo máximo: 1.500 ticks por oportunidad, sin búsquedas indefinidas; seis de desarrollo + ocho de reserva + dos controles de seis oportunidades ≈39.000 ticks, antes de paneles. Esto es un techo de planificación, no ticks ejecutados. Puede reducirse a cerrar el mecanismo central si la calibración consume tiempo o falla.

## Integración con funciones anteriores, sin fingir composición descubierta

Una extensión opcional permite que una operación aritmética heredada produzca el contenido real de la cápsula. Se ejecuta el protocolo publicado sobre la misma candidata y se transporta **su resultado observado**, por ejemplo una codificación fija del entero efectivamente formado. Si ese resultado es NULL o fuera del dominio, la cápsula no se crea: queda prohibido reemplazarla por el número esperado o por una fixture favorable.

Después, la nueva selección de conducción debe transportar y conservar esos bytes en el producto real. Una copia diagnóstica con el enlace de datos cortado debe impedir formar ese producto o cambiarlo de manera interpretable. Esto acreditaría integración asistida entre un producto Native anterior, selección adquirida y consecuencia externa. El operador sigue solicitando la operación y ofreciendo la oportunidad; no se anuncia un plan descubierto por DEE.

`aritmetica_directa_eci02.execute` ya usa `aritmetica_apd_01.native_pair` y `percepcion_cruda_fi01.frame`, que conserva dos vueltas de retorno después del lector. No se debe insertar esa ejecución sin calcular su horizonte: puede sobrepasar la ventana de elegibilidad. Preparar el producto de datos **antes** de lanzar el nuevo query/efecto, o hacer una adaptación asincrónica versionada y validada, evitando un salto del propietario o del lector. `fi_async_R04` existente no es un decodificador numérico genérico: su códec está fijado para comparación y no se rebautiza como suma.

Una segunda ampliación de composición preparo→sello puede ser interesante, pero una alternancia fija resolvería ese problema. No conviene hacerla la afirmación central ni atribuirle planificación autónoma. Primero debe cerrarse crédito diferido útil y reproducible.

## Atribución y límites

Preparados: geometría, copia inversa, decodificador, cero→actuador inicial, query, ventanas de fase, conducciones, ley de conexión, existencias, demoras y regla de descompresión. Adquirido sólo si se prueba: diferencia nativa de referencias y selección posterior dependiente de consecuencias. El anfitrión deja de escoger el banco de retorno de la actuación pasada; no deja de ofrecer oportunidades ni de instalar el cuerpo.

La versión mínima aprende una contingencia global vigente a partir de la historia. No mantiene dos políticas contextuales simultáneas ni recibe un sensor específico del contexto actual. No debe presentarse como respuesta a contextos perceptualmente distintos, iniciativa, descubrimiento espontáneo de anatomía, regulación de todo el organismo, dolor o planificación. Si la contingencia no resulta aprendible con la dinámica real, se conserva el negativo.

Fuentes dirigidas adicionales leídas para esta propuesta: `aritmetica_directa_eci02.py` completo; función `native_pair` de `aritmetica_apd_01.py`; `percepcion_cruda_fi01.py:frame` y `fi_async_R04.py` (start/observe/finish). No se ejecutó ninguna de ellas. El código R02 es una propuesta externa separada y no afecta a R01 sellado, al producto instalado o al ente.
