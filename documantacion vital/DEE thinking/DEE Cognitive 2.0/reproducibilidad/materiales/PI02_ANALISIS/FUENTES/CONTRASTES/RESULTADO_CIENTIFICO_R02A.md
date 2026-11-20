# PI02 R02A: solicitudes por retorno físico y selección por consecuencias

Resultado científico de etapa, separado de adopción. Este texto no modifica el principal operativo ni certifica las etapas B/C. Se basa en las cuatro ejecuciones registradas y en el recálculo independiente `codigo/RECALCULAR_PI02.py`, que sólo lee evidencia congelada con Python estándar. El recálculo no importa DEE ni produce ticks.

## Qué cambió frente a PI01

La misma preparación N67 heredada de PI01 continúa sin instalar otro portador inicial. Una llegada A/B al origen[0,5,20], observada mediante flanco, activa un trabajo sin una orden individual de oportunidad. Un transductor fijo continúa llamando MA/alfa paraA y FI128 paraB; sus respuestas físicas producen comandos sobre un banco finito externo de recursos64bytes. La consecuencia negativa de un comando aplicado vuelve por un canal legal, con un eco de la ruta realmente utilizada, y puede cambiar la dirección de los retornos siguientes.

El operador dio una única petición `vivir4500` por brazo. No se añadieron los pulsos **SENSOR y NORMALIZER de oportunidad de PI01**. Esto no significa ausencia de consultas materiales: los accesos MA/FI siguen suministrando sus entradas y recursos de lectura. La recurrencia67, el filtro de flanco, busy308, el retraso de feedback268 y el mapa MA/FI son preparados. No se adquirió un calendario nuevo ni se descubrió todavía una interfaz de efecto desconocido.

## Ejecución y denominadores

Cuatro ramas comparten el prefijo físico de PI01 T735843. Cada una avanzó4500ticks y llegó aT740343. No son cuatro adquisiciones independientes ni una suma de conocimientos del principal. En cada brazo hubo67firmas de retorno detectadas:12trabajos admitidos,48retornos descartados por busy y7retornos posteriores al agotamiento del banco. Los descartes son contrapresión P0 del dispositivo, no abstenciones aprendidas. Las12respuestas por brazo fueron físicamente válidas y se conservaron los doce casos, incluidos fallos.

| Brazo | AccesosMA/FI | Recursos reales | Entradas nuevas solicitadas/aplicadas/rechazadas | Valencia solicitada/aplicada |
|---|---:|---:|---:|---:|
|MAIN, retorno real|6/6|10/12|1100/1100/0|2/2|
|OMIT, sin valencia negativa|12/0|7/12|84/84/0|0/0|
|SHAM, aporte fuera de la ruta|12/0|7/12|89/85/4|5/1|
|NULLED, actuación anulada después de formarse|6/6|0/12|1110/1110/0|12/12|

El recuento usa sólo las secciones canónicas de solicitudes de cada acceso y sus recibos finales, con IDs mayores que112829. No suma los recibos heredados ni las copias de un mismo recibo que aparecen en otros campos. MAIN utiliza42entradasMA,1056entradasFI y2valencias. Los signos se decodifican de RAW con el conjunto fijo de12gates MA o E/q+4 paraFI, preservando cero frente aNULL. Sólo después se evalúa la utilidad contra la condición ambiental. Los24archivos64bytes efectivamente recolectados entre los brazos se leyeron y compararon por tamaño/hash con sus recibos; no se aceptó como efecto un simple incremento de contador.

El protocolo fijó antes de las reservas un mínimo9recursos en MAIN, ventaja mínima2frente aOMIT ySHAM, cero recursos con actuación anulada y12respuestas válidas. Los recuentos observados satisfacen esas condiciones numéricas. Eso no produce automáticamente promoción ni un veredicto de autonomía: la calidad del sham y la conservación posterior se analizan por separado.

## Enlace causal y límite del sham

MAIN empezó usando A/MA−. Después del primer fracaso, episodio3, el aporte negativo se aplicó enT737142 y actuó sobre el retorno previstoT737143. La siguiente solicitud admitida, T737210, utilizóB/FI. OMIT no recibió esa entrada y conservóA. SHAM recibió su primer aporte en la misma fase pero fuera de la ruta decisiva y conservóA. La nueva selección precede a las entradas del acceso FI: éstas no explican retrospectivamente esa primera elección distinta.

MAIN obtuvo una respuestaFI negativa útil en el episodio8 aunque seguía enB; la utilidad pertenece al comando formado, no a que B sea siempre la opción positiva. Después del fracaso9, la segunda consecuencia modificó la política y las oportunidades10–11 volvieron aMA− con recursos. La respuesta anulada formó decisiones y lecturas pero no liberó archivos, separando actividad de efecto externo.

**SHAM no es un control repetido de dosis perfectamente igualada.** Solicitó cinco aportes y sólo el primero se admitió; cuatro fueron rechazados por ocupación. Esos rechazos permanecen en el denominador. El primer contraste admitido es informativo para la primera divergencia, pero no permite afirmar que toda la ventaja final se verificó bajo exposición material total igual. La evolución posterior también requiere más entradas cuando MAIN usaFI. No se interpreta baja ocupación global como ausencia de interferencia local ni se presupone un linaje toroidal del ocupante del puerto sham sin seguimiento suficiente.

## Comparación con reglas externas sencillas

Las referencias se calcularon fuera de DEE con los mismos pares públicos, condición ambiental y doce oportunidades. No controlaron al participante. WSLS empieza enA y sólo cambia de ruta después de un resultado negativo; el cálculo del signo del comparador en esa referencia es clásico y no se atribuye a DEE. Resultados:WSLS10/12, siempreA7/12, siempreB6/12 y alternancia fija7/12. La secuencia de rutas, signos y utilidad de MAIN coincide conWSLS en estos casos.

Esta igualdad acota la interpretación: hay selección física modificada por consecuencias y reducción de pulsos individuales, no evidencia de una política más compleja que la regla binaria preparada. No invalida el uso integrado de memoria/comparación ni la utilidad del nuevo disparo físico. Tampoco justifica superioridad frente a otros métodos ni generalización fuera de ese vocabulario de dos rutas.

## Coste anfitrión observado

| Brazo | CPU usuario/kernel acumulada máxima(s) | Pico working-set(bytes) | Pico compromiso Job(bytes) | Vida del propietario registrada(s) |
|---|---:|---:|---:|---:|
|MAIN|63.25/9.234375|292024320|308195328|74.72495359997265|
|OMIT|66.375/11.734375|289939456|304537600|80.67802470002789|
|SHAM|73.640625/12.6875|289665024|305647616|89.99397189996671|
|NULLED|62.40625/11.921875|291745792|308088832|76.4248020000523|

El límite Job registrado fue536870912bytes. Los cuatro propietarios cerraron con código0 según su diario. Son medidas de bajo coste del proceso anfitrión; la CPU es acumulada y se tomó su máximo, no la suma de muestras. Estos intervalos de alrededor de un minuto no verifican ni descartan el reporte Mac de80–90minutos, una fuga general o una ley de reinicio45minutos. RAM del host no se presenta como memoria cognitiva ni la seguridad del Job como autorregulación aprendida.

## Recálculo y alcance

El núcleo inicial se exportó en `entrega/EXPEDIENTE`, con índice de rutas relativas, los ocho primariosR01/R02A, sus24recursos, protocolo, códigoR02Bcongelado, diario de ejecución y los dos checkpoints históricos de observación. Ejecutar allí el verificador estándar con `--root` de esa carpeta y salida exterior produjo los mismos resultados, sin acceder a carpetas originales para leer la evidencia. Los dos checkpoints permiten volver a comparar el prefijo causal completo deR01; no constituyen el par operativo completo de una vida Cognitive.

Los fallos de desarrollo, las ejecuciones4×4500ticks y los controles son hechos distintos de esta repetición documental. Esta etapa muestra menor asistencia por oportunidad y uso útil de la historia binaria en una continuación. Aún no demuestra temporización aprendida, selección de cuándo recuperar una memoria, uso descubierto de una válvula, aviso anticipatorio adquirido o regulación contextual. La incorporación y el estado final requieren el cierre completo de la campaña y su conservación/reapertura, no este archivo por sí solo.
