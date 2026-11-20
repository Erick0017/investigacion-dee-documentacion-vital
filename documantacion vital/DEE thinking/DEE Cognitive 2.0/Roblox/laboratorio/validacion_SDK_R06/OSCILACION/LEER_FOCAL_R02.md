# Focal separado: disponibilidad local — código R02

No modifica KIT_DESARROLLADOR ni VERSION0.1.0. No se ha ejecutado Studio ni Native. PROTOCOLO_FOCAL.json fija la hipótesis,4oportunidades de desarrollo+2de reserva y el único mecanismo. Los artefactos R02 completan el enlace ambiental sin volver a enumerar las729trazas ni cambiar la regla.

## Entradas

- DEE_FOCAL_CONSUME_RECHARGE_R02.rbxlx: brazo con cupón físico por puerto que se consume al paso verificado y repone tras3épocas ambientales.
- DEE_FOCAL_NONCONSUMING_CONTROL_R02.rbxlx: misma geometría, cuerpo, encoder y contacto; el cupón no se consume.
- DEEConnector_FOCAL_R02.rbxmx: paquete importable del primer brazo.
- CONFIG_SDK_FOCAL_*.json y Config_*_R02.luau: copias públicas, sin secretos, Mode=PREVIEW.

Ambas escenas conservan Main, Bootstrap, HttpLoop, HttpTransport y MotorPathfinding del KIT sin cambios. El nuevo MapaFocal reutiliza grafo/posiciones deR07; FocalAdapters aplica exclusivamente la salida Native al puerto anatómico correspondiente y verifica contacto físico de llegada. No hay anti-loop, lista de estaciones no visitadas ni cálculo de ruta correcta. Pathfinding sólo lleva al destino ya seleccionado.

## Orden de Root, sin ejecución por este preparador

1. Abrir UNA copia focal y ejecutar Preview. Construye seis zonas,12recursos de paso, paneles yNPC. El stock18dePreview es un contador técnico, no un valor Native ni pruebaK2.
2. Root puede ejecutar PREFLIGHT_ESCENA_SOLO_LECTURA_R02.luau en el servidor preparado: verifica cuenta, contacto, paneles y anatomía sin HTTP, Native ni movimiento.
3. Cerrar Preview. Preparar dos copias Native completas equivalentes desde el mismo PAR28T991187 y dos identidades/scopes focales nuevos, max6ciclos cada una; no reutilizar el SDKdemo ni las vidas históricas. La fábrica privadaSDKactual max3 necesita configuración/epoch focal propio. Este documento no cambia ese backend.
4. El límite agregado autorizado por Root es40000ticks, incluyendo el SDK3y ambos brazos. El límite global prevalece sobre6+6; no admitir un ciclo si su reserva excede el presupuesto/resto de la ventana. No cambiar lectores/bancos/calendarios ni el feedback deR07 para crear el scope.
5. Root inyecta sólo en su copia privada ServerStorage/DEE_FOCAL_PrivateConnection (BaseUrl,InstanceId,Token), habilita HTTP del PLACE local y fija Mode=NATIVE. XMLno serializa HttpService.HttpEnabled=true. PermisosMCP/allowlist son otra autorización: una denegación no se elude.
6. El mismo HttpLoop espera READY y ejecuta hasta6ciclos con IDs previos al POST/GETporID. Control ytratamiento usan el mismo taglocal y el mismo sensor/codec. Root hace el preflight Native real; este código no lo acredita.
7. Se conserva cada salida, incluso0válido/SAFE_WAIT/NULL, coste, ACK yretorno. No repetir para conseguir escape. Cerrar, exportar y conciliar antes del siguiente brazo; un único escritor.

Disponibilidad sólo entra al Native por el stationSignal pagado ya instalado. numberA/B y otros sensores se conservan del estado público heredado; no se usan como alias de disponibilidad. El módulo de ley publica Gate.TollCost_C02 y Panel.EncodedSignal_C02 desde los recursos físicos. El coste se aplica al puerto elegido antes del motor según el contrato R07; el cupón se consume sólo tras llegada verificada. Los peajes solos no son retorno adverso genérico en este actor; no se añade castigo.

Captura focal incluye estado público, historial local, disponibilidad con deadlines/IDs,pose de12componentes, motor ydispositivo. No es un volcado completo de todas las Instances. Continuar exige además el estado Native completo emparejado, igual queSDK; no se prometeK4focal.

## Comprobación offline acotada

    python verificar_enlace_focal_R02.py --output PREFLIGHT_ENLACE_R02.json

Sólo XML/fuentes/configuración y hashes. No repite las729trazas y no importa Native, SQLite ni Roblox. La compilaciónLuau y las exposiciones reales quedan pendientes deRoot. PERSISTE_BUCLE/SIN_EXPOSICION/PARCIAL/BLOQUEADO son resultados válidos; no afectan la aceptación del SDK.
