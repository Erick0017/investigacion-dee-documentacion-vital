# Revisión previa del diseño R02A

Esta revisión se basa en la descripción prospectiva del responsable y en la lectura textual del código PI01 instalado. No revisa todavía bytes de un protocolo R02A congelado ni acredita una ejecución. No se importó DEE ni se avanzaron ticks.

## Pregunta y contribución evaluable

La propuesta deja circular el portador heredado, observa sus retornos en O y permite que una llegada física dispare un trabajo mediante un transductor estable. Retira las entradas SENSOR y NORMALIZER por oportunidad. El contenido de la dirección puede cambiar después de una consecuencia negativa genérica. Una sola orden exterior ofrece un horizonte de evolución; no hay una petición individual «actúa ahora» por trabajo.

La reducción de asistencia es evaluable: cantidad de llamadas y entradas de oportunidad frente al aparato PI01, preservando respuestas útiles y consecuencias físicas. El ciclo de recurrencia, sitio de lectura, transductor A/B→MA/FI y ventana refractaria siguen preparados. Si no cambia la fase/periodicidad, no hay evidencia de iniciativa temporal aprendida, exploración abierta ni descubrimiento de nuevos actuadores. «Solicitud activada por una recurrencia nativa» es una atribución más precisa que «decidió libremente cuándo actuar».

## Firmas y tiempo que deben quedar congelados

- Sin SENSOR, las firmas de política A=(1,0,0) y B=(0,1,0) son distintas de ACTION0=(0,0,1) y ACTION1=(−1,1,1), que utilizaba PI01 después de su encuentro con el sensor. El nuevo contrato debe declararlas antes de puntuar reservas. Una dirección no prevista es inválida; no buscar otra ventana o traducirla según la utilidad.
- La valencia genérica5 puede transducirse con un eco de la acción realmente formada. Elegir una dirección de entrada a partir del comando emitido es asistencia fija declarada; elegirla a partir de la ruta que habría tenido éxito suministraría una solución.
- Fijar de qué instante se calcula el retorno4N y el busy4N+40: detección, inicio del método o efecto actuador no son intercambiables. Si el acceso sobrepasa el deadline, conservar ese futuro y registrar fallo; no retardar adaptativamente el feedback para rescatarlo.
- La indisponibilidad busy es una propiedad preparada del dispositivo. Los retornos ignorados por ella no son decisiones aprendidas de abstención, ahorro ni regulación del ente.

## Riesgo instrumental decisivo

`use_selected_access` de PI01 llama a `run_until` dentro de los accesos MA/FI. Un lector instalado sólo en el bucle exterior no observa necesariamente los retornos que ocurren durante esas llamadas. Para declarar observación de todos los retornos, la instrumentación debe acompañar el avance del propietario en esos intervalos o registrar cobertura incompleta. No se pueden contar como retornos perdidos conocidos eventos que no fueron observados.

El registrador pasivo no debe añadir sondas ni procesar tareas durante una llamada anidada. Registrar y después contar esos eventos es distinto de reentrar el despachador, que puede crear un segundo protocolo material. Deben comprobarse igualdad de estado físico, agenda y recibos con/sin el registro, dentro de un caso representativo del nuevo mecanismo. No basta comparar la salida textual.

## Controles y denominadores

Los controles propuestos son pertinentes para la pregunta: retorno negativo omitido, sham de misma dosis fuera de las rutas decisivas y actuación anulada después de formarse. El sham necesita evidencia de admisión y de no interceptar otra función; su nombre no lo garantiza. Si el número de consecuencias negativas diverge después de que divergen las actuaciones, la dosis total posterior puede diferir legítimamente: registrar el coste, sin afirmar igualdad total de entrada.

Por cada trayectoria, contar retornos detectados, descartes busy, trabajos admitidos, respuestas válidas/NULL, comandos aplicados, recursos ejecutados, entradas solicitadas/aplicadas/rechazadas/pendientes y ventanas no observadas. Un trabajo correcto producido después de varias lecturas materiales no es la misma primera respuesta que una retención sin consulta.

Una referencia WSLS o repetición fija debe permanecer separada de E1, recibir la misma información y oportunidades y no alimentar su decisión. Si WSLS iguala el resultado, no invalida la reducción de entradas del nuevo mecanismo, pero impide presentar aquella utilidad como evidencia de una política más compleja que la alternancia preparada. En un entorno cuya evolución futura dependa de cada acción, la referencia necesita su propia evolución ambiental; no imponerle el futuro producido por E1.

## Criterios mínimos sugeridos para congelar antes de la reserva

1. Repetidos trabajos activados desde llegadas físicas, sin nuevas entradas de oportunidad individuales ni selección retrospectiva del lector.
2. Uso de MA/FI cuyo contenido determine un comando y un recurso externo real, no sólo un contador de acciones.
3. Cambio de la siguiente elección después de una consecuencia pertinente y comparación con omisión/sham de la misma oportunidad común.
4. Ventaja útil o reducción explícita de asistencia frente al antecedente, con los errores incluidos. No hace falta superioridad universal.
5. Conservación material proporcional y reapertura desde el estado completo. La futura B/C debe partir del mismo estado sucesivo si se le atribuye una adquisición acumulada.

Estos son criterios propuestos, no resultados ni aprobación automática. El diseño R02A responde a la dimensión A con una reducción acotada de asistencia; por sí solo no acredita advertencia aprendida, protección contextual, iniciativa temporal adquirida o una estrategia general. Esas preguntas requieren sus propios enlaces y controles en la misma genealogía.

## Revisión estática posterior del prototipo R02 escrito

Se leyó `codigo/progresion_integrada_02_R02.py`, además de los accesos heredados que invoca. `Tap.run_until` descompone el avance en pasos del propietario, observa O y registra flancos A/B; MA delega sus avances a ese objeto y el `_EarlyAdapter` FI también delega al objeto base. La instrumentación, por tanto, no queda restringida al bucle exterior. `Tap` no ejecuta trabajos de manera reentrante mientras MA/FI están ocupados.

No se encontró un target transmitido al acceso: `use_selected_access` recibe la ruta física y los operandos públicos; `effect` compara después la respuesta real con el cierre ambiental privado. El código conserva incertidumbre si el acceso sobrepasa el deadline o una operación queda incompleta. No hay sustitución de NULL, búsqueda de otro lector favorable ni edición RAW/clock en ese módulo.

Quedan dos cautelas del propio prototipo: `native_requested_work=len(events)` incluye flancos descartados por busy, límite final o banco agotado, de modo que debe describirse como firmas físicas detectadas y no trabajos ejecutados. Además, comprobar RAW0 en las dos celdas de inyección sham no demuestra que su recorrido sea inocuo; hay que contrastar la ruta o sus efectos antes de utilizarlo como control causal. El hecho de que la operación quede bajo una sola petición exterior no elimina las decisiones P0 del puente ni convierte su busy en regulación adquirida.

Esta lectura estática no aprueba una reserva todavía no inspeccionada ni acredita la pasividad global de cualquier observador futuro. Sus bytes revisados se registran en el control de código correspondiente, separado de los resultados físicos R01.
