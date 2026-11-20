# B06: cadencia y perturbación periférica — prospectivo, cero ticks al fijarlo

Origen inmutable: MU_MAIN T16634, SHA-256 `b6c02df2e804b167b85f9e8fd849e091227b81ccfd7a49e442f67156944c71ad`. Cada ensayo será una copia completa propia, no una continuación oculta del MU_MAIN actual. N67, E15/15/15, árbol B05 y frontal S con cinco stops inactivos preparados legalmente. Se conserva la referencia adquirida A6/B7 del corte, sin escribirla.

El diseño se fija antes de disponer del slot nativo. Sigue el límite B original25/10/2026 18:54:23.321598UTC y el plazo monotónico del cierre A. Un Runtime escritor por proceso, máximo512MiB de pico. Ninguna ejecución se inicia antes del aviso de liberación del slot.

## 1. Cadencia: cuatro brazos, mismo par de tramas

En cada brazo se ofrecen **dos tramas de128componentes**, nunca128consultas seriales. La primera tiene128valores0. La segunda tiene el componente0 igual a2 y los127restantes0. El par completo es idéntico en todos los brazos: misma dimensión, amplitudes, número de portadores, recursos y orden. Elegir contenido contrastado permite detectar una salida residual en vez de confundirla con una segunda respuesta correcta.

Intervalos fijos entre inyecciones de hojas: Δ=2,16,67,200ticks. La primera hoja llega siempre en16642 tras la misma preparación; la segunda en16642+Δ. Se agendan ambas tramas completas desde el principio, sin esperar ni filtrar un acierto. Los recursos0 y las tres consultas comunes se alinean por la geometría de cada trama: dato57ticks después de su hoja, consulta tres ticks antes del dato y lector **seis clases fijas en consulta+6**. Se registran ambas ventanas aunque se superpongan o la lectura sea inválida.

Todos los brazos terminan su observación pasiva en el **mismo tick17038**, calculado para incluir2N después del final de la segunda ventana del brazoΔ200. Después se realiza el mismo panel de seis asociaciones anteriores. Así se igualan edad final y dosis total; la fase y la posibilidad de encuentros/retornos cambian con el intervalo y se informan como parte del contraste, no como un efecto puro de frecuencia separado de toda fase.

Por brazo:256entradas crudas,90recursos de giro0 y6entradas de consulta/apoyo,352solicitudes antes del panel. No hay limpieza, retorno a un snapshot entre tramas ni elección de otro lector. Los rechazos forman parte del resultado. Predicción del examinador: primera respuesta− y segunda+, si ambas funciones siguen accesibles; esa predicción no entra en DEE.

Se guardará un snapshot completo con colas antes de la primera ventana y registros pasivos de E, S, C, referencias, aproximación y seis actuadores durante ambas. El código de evolución no consulta el informe ni el índice del brazo.

## 2. Ruido: cinco condiciones, una perturbación por exposición

Se reutiliza como condición sin ruido el primario ya ejecutado `B05_TREE_R1_N128/single_first.json.gz`, con el mismo corte, preparación y hoja16642. No se repite sólo para cambiarle el nombre. Los cuatro brazos nuevos reciben exactamente esa trama:128portadores crudos, componente0=2, demás0, recursos fijos y lecturaq+6.

| Condición | Entradas ajenas a la trama | Sitio | Dirección | Tick |
|---|---:|---|---|---:|
| Sin ruido, primario existente |0|—|—|—|
| Periférica0 |1, carga0|13/16/17|0/0/0|16697|
| Periférica2 |1, carga2|13/16/17|0/0/0|16697|
| Periférica32 |1, carga32|13/16/17|0/0/0|16697|
| Sham32 |1, carga32|13/20/17|0/0/0|16697|

El sitio local es el precursor periférico de S, fuera de Moore1 de E. No es un registro de memoria ni una edición del kernel. La perturbación entra mediante una interfaz SEM1state1 legal, una oportunidad antes de que el producto llegue al precursor. No se retrasa para forzar admisión. La condición sham mantiene carga, dirección, cantidad y calendario, cambiando únicamente la localización. Debe registrarse su contexto real; una distancia geométrica no certifica aislamiento causal.

Los contrastes0/2/32 cambian amplitud con **una misma cantidad/tasa de eventos**. El contraste de cadencia cambia intervalo con la dosis total del par fija. No se atribuye un efecto independiente a la frecuencia del ruido: sólo se prueba un evento periférico por exposición. La carga0 sigue siendo una entrada material, no ausencia de intervención.

Horizon de los cuatro brazos nuevos: tick16838, idéntico al control ya existente, seguido del mismo panel de seis asociaciones. El observador conserva admisión/rechazo, estado del precursor antes/después, llegada o ausencia en S, salida y efectos posteriores. Una entrada rechazada no cuenta como exposición recibida; un cambio de respuesta no demuestra por sí solo destrucción de memoria ni regulación aprendida.

## 3. Alcance y criterios comunes

Se conservan solicitado, admitido, rechazado, pendiente, emisión binaria/neutral/ausente y respuestas viejas. Los casos son bifurcaciones de un prefijo común, no aprendizajes independientes. La traducción es el lector ya congelado: no se ajustan ventanas o planos después de observar los resultados.

Un acierto bajo ruido puede depender de protección P0 o del rechazo físico del puerto. Un fallo puede proceder de ocupación transitoria, contexto, transformación o uso; no se resume como muerte o falta de memoria. Las medidas de ocupación son descriptores, no energía ni un veredicto cognitivo.
