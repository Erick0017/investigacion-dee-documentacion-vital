# Focal R04 / TRANSPORT_R02

Use las escenas DEE_FOCAL_CONSUME_RECHARGE_R04.rbxlx y DEE_FOCAL_NONCONSUMING_CONTROL_R04.rbxlx; exportDEEConnector_FOCAL_R04.rbxmx. Mantiene todo R03 excepto HttpTransport: IDs ya validados viajan literales, sin UrlEncode. Misma wire0.1.0, perfilFOCAL,condición yley. R03 se preserva.

Las copias privadas actualizadas están indicadas en PARTICIPANTES_FOCAL_PRIVADOS_01_TRANSPORT_R02.json; mantienen IDs/contextos y las conexiones privadas anteriores sin exponer el token. No se ejecutó Native, Studio, MCP, import0 ni lease al crearlas.

Siguen vigentes los preflightRO ycriterios anteriores. Resultadosestáticos anteriores son históricos; el nuevo testtransporte está en VALIDACION/TRANSPORTE_R02. No hay reinicio del servicio/backend para este arreglo.
