# Solicitud condicionada y retorno físico — evidencia nueva

Una referencia adquirida cambia la emisión de una solicitud física; una fuente también adquirida cambia su retorno. El retorno modifica después otro encuentro. Todos los portadores comparten un Runtime por preparación.

## Mecanismo y controles

- F1: referencia direccional aprendida, comparación nativa70, solicitud73, fuente78, efecto82 y retorno87. Experiencia opuesta cambia la utilización con las mismas interfaces. Dense/Lazy concuerdan RAW/clocks finales.
- F2: referencia31+formato5 conserva carga36; objeto16+formato5 llega como21. La salida+X7@70 se desvía72; consulta una fuente16@77, produce23, encuentra recurso7@81 y devuelve30@86. Fuente opuesta cambia la dirección; fuente virgen/desacoplada, falta de tap o de efecto separan etapas.
- Las reservas27/9 y objetos12/39/27 incluyen igualdad física32/32: salida activa de dirección cero, distinta de ausencia.
- Cortes diagnósticos tardíos de solicitud/fuente en73 eliminan el retorno30; sus RAW-shams lo conservan. Padre, clocks y cola permanecen intactos.
- Extensión USE: retorno30 encuentra recurso13@89, produce43(0,0,-1) y se propaga90. Omitir solicitud o experiencia del proveedor elimina esa firma. Cortar el retorno ya formado87 también la elimina; sham la conserva.

## Conservación y alcance

En mundos emparejados se observa referencia36 antes de las tres comparaciones69/136/203, frente a objetos21/47/21. Las expresiones70/137/204 son +X/−X/+X. Después de otra adquisición110 y consulta180 sigue accesible la primera comparación. El lector original continúa: sólo la primera de tres solicitudes de lector fue admitida; las otras dos se registran como rejected_occupied.

La política de preguntar ante un signo concreto y los recursos son preparados. La experiencia determina la referencia y el contenido del proveedor; no se acredita curiosidad general ni los significados completos de SABER, QUERER o DECIR. F1, F2 y USE son preparaciones diferentes, no escenas concatenadas de una vida. Su eventual integración en E1 requiere una nueva prueba del contexto completo.

## Conteos y reproducción

Hay 27 preparaciones científicas, 1 reproducción técnica Dense y 10 forks diagnósticos más 3 continuaciones restauradas; no son réplicas IID. Se conservó el intento técnico con error de sintaxis previo a cargar un mundo.

Los datos exactos, recibos, hashes de fuente, recursos y denominadores están en INICIATIVA_ADQUIRIDA_Y_RETORNO.json. Cada fila remite a MEASUREMENTS.json y a sus fuentes ejecutadas. Las trayectorias previstas son rutas declaradas: no se asigna genealogía única por proximidad.

Recalcular sin evolución: `python tools/resumir_iniciativa.py`. Reejecutar en una salida nueva con el entorno instalado: `python src/iniciativa_accion/gradient_pilot.py --config configuraciones/iniciativa/GRADIENT_TAP_F2_CONFIRMACION_Y_RESERVAS.json --case GRAD_R101_NEW_VALUES_OPPOSED_SOURCE --out resultados/reproduccion_iniciativa_NUEVA`.
