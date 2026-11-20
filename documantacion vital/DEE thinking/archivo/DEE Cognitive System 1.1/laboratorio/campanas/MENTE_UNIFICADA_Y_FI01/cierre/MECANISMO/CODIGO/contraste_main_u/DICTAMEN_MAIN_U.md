# Contraste retrospectivo MAIN/U — cero ticks

Se cargó como máximo un Runtime simultáneo, sólo para copiar estado y observar sus interfaces. No hubo advance/run_until, restauración de clocks, edición de RAW, nueva experiencia o modificación de ninguna vida. Las identidades se resolvieron desde seis primarios concretos y sus SHA de snapshot; no se buscó un pasado por igualdad de carga.

| Corte | Registros de origen | Diferencias RAW completas | Diferencias clocks completas |
|---|---|---|---:|
| T14892 | A33 fallo guardado / A41 consulta emparejada U | Ninguna | 0 |
| T16033 | A42 dos consecuencias / A44 U igual edad | A(14,14,15): MAIN5 frente U7; además MAIN contiene portador SEM1,+Y,carga5 en(15,52,15), ausente en U | 0 |
| T16066 | A45 reservas MAIN / A46 reservas U | Sólo A(14,14,15): MAIN5 frente U7 | 0 |

La edad T14892 del control fue comprobada en su primario y en el snapshot, no manipulada. En todos los pares coinciden interfaces, canales y protocolos públicos. Todos contienen dos rechazos históricos `rejected_occupied`; son terminales, no colas pendientes. No quedan recibos públicos pendientes en estos seis cortes. El historial de recibos difiere legítimamente después de las dos señales de retorno; los metadatos de vida, contadores y algunos datos organizacionales también difieren. Esto NO establece identidad causal total de mundos externos o de toda la capa operativa a partir de RAW/clocks.

## El portador adicional y su contexto

La salida centralY de A42, consulta15255, fue registrada en(15,17,15),T15261 con carga5. Avance rectilíneo+Y módulo67 sitúa esa clase de trayectoria en(15,52,15),T16033 y luego enE=(15,15,15),T16063. Es compatibilidad geométrica, no una genealogía única: el intervalo largo no contiene una traza íntegra que descarte todos los encuentros o antecedentes alternativos.

Los frames existentes de A45 sí muestran, en la tercera reserva, un portador+Y,carga5 en(15,12,15)T16060, (15,13,15)T16061 y(15,14,15)T16062. EnT16062 E ya está ocupado por la nueva consulta+Z,carga5. EnT16063 E gira hacia−X,+Y manteniendo5; el lectorT16065 también registra5, no10. No se observó suma de cargas en la salida. El portador anterior puede participar en el contexto de gradiente/ocupación del procesamiento, pero estos registros no contienen un corte selectivo que mida su efecto funcional.

Por tanto, «sólo cambió A después de las consecuencias» es falso enT16033 y verdadero para los campos físicos comparados enT16066. Tampoco corresponde atribuir exclusivamente a A toda la causalidad de la tercera respuesta sólo por encontrar una diferencia final. Se conservan tanto el uso útil registrado como esta limitación causal; no se modifica retrospectivamente la trayectoria.

## Datos y recálculo

`MAIN_U_COMPLETO_FINAL.json.gz` incluye los seis arrays RAW/clocks completos, uint64 exactos, las interfaces y protocolos públicos, todos los recibos, metadatos exactos de snapshot y extracción crítica de los frames originales. Tamaño285697bytes; SHA-256 `f34b4a1120fe1646876fe03731d630fe477c8c85115a0c0c044df12c7968f373`.

`recalcular_main_u.py --evidencia MAIN_U_COMPLETO_FINAL.json.gz --salida resultado.json` usa sólo la biblioteca estándar. Verifica3609156 valores uint64 y720 observaciones críticas, lectores, coordenadas, diferencias, denominadores de recibos y compatibilidad toroidal. Cero discrepancias. Referencia `RECALCULO_MAIN_U_FINAL.json`, SHA-256 `766ff18144e37630d890739207d0e4491946d79f6db90cc3fa6e97fa2d463f78`.

La primera extracción reflejó recursivamente miembros de clases enum, aumentando innecesariamente el volumen. Se conserva localmente junto con su fuente y hash. La revisión compacta serializa cada enum por su tipo/nombre/valor y preserva todos los campos de instancia. El normalizador posterior corrige únicamente la clasificación terminal de rechazos y añade los frames archivados; no ejecuta el motor. El conjunto compacto no sustituye los seis snapshots completos cuyos localizadores y SHA contiene.
