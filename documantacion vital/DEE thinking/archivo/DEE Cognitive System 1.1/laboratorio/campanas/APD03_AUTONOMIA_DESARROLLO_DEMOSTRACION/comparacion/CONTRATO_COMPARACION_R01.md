# Comparación APD03 — contrato prospectivo R01

Este instrumento ejecuta referencias convencionales separadas. No se importa el motor, no se avanza una vida y ningún resultado vuelve al ente.

## Información común

Cada oportunidad entrega al decisor una copia JSON de `observation`: literal, operandos visibles (segundo puede ser null), contexto observable, recursos públicos y acciones permitidas. No incluye operación objetivo, valor de referencia, ley privada, fallo del proveedor, semilla, futuro, identidad del ensayo ni calificación privada. El identificador de tarea se mantiene en el ejecutor; no se usa en la política.

La docencia explícita puede entregar una asociación literal→operación; debe ser la misma ofrecida al individuo. La interfaz de feedback entrega sólo `SUCCESS` o `FAILURE`, después de comprometer y verificar la acción. Una consulta elegida revela un dato real del entorno; no entrega una operación, una ruta ni una respuesta calculada.

Las acciones son `QUERY`, `ACT(operation, procedure)` y `WAIT`. Cada objetivo admite como máximo cuatro oportunidades. No se consulta el resultado de ambas rutas ni se permite fallback. Cada acción `ACT` efectúa una sola llamada y un archivo sintético real; se reutiliza el evaluador postacción APD02 sin editarlo.

## Referencias ejecutadas

1. `fijo`: memoria de docencia literal; pregunta una vez por objetivo y usa siempre la ruta nominal native. La consulta fija es preparación explícita, no aprendizaje.
2. `tabla_contextual`: misma memoria docente; consulta si falta un operando; tabla finita por contexto público y ruta con éxitos/intentos. Prueba rutas aún no observadas y luego elige mayor tasa empírica de éxito; desempate fijo native. La tabla no conoce leyes ocultas.
3. `wsls`: misma memoria docente; consulta si falta un operando; conserva una ruta global y la cambia después de FAILURE de un ACT. Una consulta incompleta no cambia la ruta. Es una estrategia adaptativa convencional, no un mecanismo DEE.

Las rutas nominales native/external conservan precios, disponibilidades y fallos del entorno compartido, pero **ambos callbacks de estas referencias calculan aritmética convencional**. No son ejecuciones nativas DEE y sus tiempos no estiman el costo de ejecutar v27. Se separan costo de decisión y costo total con archivos/evaluación. Las referencias no controlan al ente.

## Unidad y cobertura

La unidad es una trayectoria completa desde una memoria inicial declarada, no cada consulta. Varias semillas o historias se reportan separadas. Un mismo prefijo no constituye réplica independiente. Sin un programa y observaciones compartidos con MAIN, el resultado es una prueba del comparador y no una comparación de desempeño con E1.

## Recursos

Relojes monótonos, CPU del proceso, working set y pico del proceso Windows, I/O de proceso, tiempos de decisión y fase. Inicio, aprendizaje, ejecución, verificación e instrumentación/guardado se distinguen cuando la resolución permite. El proceso es exclusivo de una referencia durante su ejecución; no se atribuye al decisor CPU de trabajadores inexistentes. Energía: NO MEDIDA. Costos de la ley son unidades sintéticas, no dinero ni joules.

## Reservas y salidas

El programa compartido, preparación inicial y políticas se sellan antes de ejecutar reservas. Se conservan todas las oportunidades, incluyendo abstenciones, rechazos lógicos, fallos y archivos incorrectos. La tabla de métricas incluye solicitado, admitido por el ejecutor, respondido, correcto, incorrecto, abstención, ausencia, consultas y efectos. La admisión del ejecutor convencional no es admisión de un puerto DEE.

No se declara ventaja energética, autonomía general ni equivalencia de microfísica. La demostrabilidad se decidirá desde los contrastes realmente obtenidos.
