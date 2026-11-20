# Evaluador posterior de calidad APD02

`evaluate_committed` recibe la petición original privada al evaluador, el recibo terminal de la única acción ya elegida y una raíz explícita de archivos sintéticos. No calcula qué acción debe realizar DEE ni ejecuta una alternativa. La operación esperada procede del objetivo original congelado, nunca de la emisión que se está evaluando.

El JSON real debe declarar `schema`, `task_id`, `operation`, `operands`, `value` y `procedure`. Se comprueban bytes/SHA, esquema, pertenencia al directorio autorizado, operación pertinente, resultado, coste y demora por separado. Un artefacto correcto pero caro es trabajo válido con incumplimiento de recursos; un artefacto barato con el operador equivocado no es solución válida.

Sólo `actor_feedback(report)` —un objeto con la clave `category`— puede volver a la física. `private_audit` contiene la referencia y es exclusivamente del auditor. El código de selección no debe recibir el informe completo. La proyección binaria está disponible con `binary=True`; tampoco revela la corrección exacta. Pendientes, procesamiento y efectos inciertos rechazan la evaluación, sin reintentos.

Los proveedores de prueba llaman una sola función ya seleccionada. El callback nativo real debe obtener su valor de DEE; las pruebas puras suministran explícitamente datos sintéticos y no acreditan cómputo ni aprendizaje nativo. Las fallas son perturbaciones declaradas del proveedor/archivo, nunca ediciones de memoria.

Prueba pura, sin importar thinking ni avanzar mundos:

```text
python -I -B probar_calidad_apd02.py --salida DIRECTORIO_NUEVO
```

Los controles incluyen archivo existente con número incorrecto, operador barato equivocado, operación correcta con fallo de escritura, ruta externa no disponible sin fallback, JSON inválido/duplicado, SHA incongruente, límites y rutas inseguras. Los tiempos de evaluación externa se registran aparte y no se llaman energía interna. La validación de archivos no es aislamiento del sistema operativo.
La entrada operativa `evaluate_literal_committed` recibe sólo `{task_id,text,operands}`. Resuelve la convención privada de las seis formas únicamente después de comprobar un efecto terminal. El mapa no interviene en el codec, el selector ni el proveedor. La API de referencia explícita se mantiene para controles con historias opuestas.

El proveedor de pruebas marca `synthetic_fixture=True` por defecto. Una integración con callback nativo real debe declarar `synthetic_fixture=False`; esta declaración del llamador no sustituye comprobar los ticks/recibos físicos reales. No se ejecuta una segunda ruta al fallar la seleccionada.

R04 registra fases `planned → before_compute → computed → opened → written → fsynced → readback`. Una excepción desde `opened` conserva `state=uncertain`, el localizador del posible archivo y ninguna confirmación de bytes/hash. El evaluador rechaza ese estado; no se inventa una consecuencia éxito/fallo ni se reintenta. El fallo inyectado anterior a abrir el archivo sigue siendo `failed` conocido. Los callbacks deben limitar su efecto externo al valor: un callback nativo puede haber avanzado DEE antes de cualquier error, sin que ello autorice repetirlo.

R03 y su incorporación inicial se preservan sin reescritura. Su proveedor capturaba genéricamente excepciones como `failed`; no se observó en los primarios de esa ejecución un error real posterior a escritura. Este límite de infraestructura se delimita prospectivamente con R04 y sus archivos parciales reales, no se atribuye como fallo cognitivo ni se corrige el pasado.
