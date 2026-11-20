# FOCAL_R06 — ruta diagnóstica separada

Implementación preparada con pruebas de dobles/FS/AST. No se ha preparado/importado una identidad real, ni ejecutado Native, Studio o MCP por el agente. La prueba sintética no es reproducción Native ni validación física de la escena.

## Límites y procedencia

El core0.1.1/Max3 y sus26fuentes no cambian. Este perfil FOCAL tiene6oportunidades por vida, secuencia local1..12 (Native57..68), mismo actor/lector y ley local preparados. Sus3fuentesNative son idénticas byte por byte al FOCAL anterior; first/second/function/feedback/BoundedTime también coinciden porAST con el actorCore. Sólo cambia el host/scope de diagnóstico.

Dos vidas NUEVAS desde el prefijo COMPLETO PAR28, N67/T991187, stock público heredado164. No use la vida SDK avanzada, principal/ACTIVO, PILOT ni participantes antiguos como fresh. El límite GLOBAL sigue40.000ticks del ledger EXISTENTE estado_demo/LEDGER_SDK_R06.json; no existe inicializador focal. Los ciclos focales no consumen los3ciclos SDKpilot, pero sus ticks y reservas sí consumen el mismo saldo. Máximo6mundos global.

OSCILANTE y CONTROL usan los mismos sensores, feedback real, teacher omitted, local_tag, costeconsulta1 y peaje2. Sólo cambia si el paso físico verificado consume el cupón local y lo repone a época+3. No se selecciona ruta, rescata ni corrige una acción Native. Se conservan desarrollo1..4/reserva5..6 y los criterios previos. No hay herramientas/lecciones focales.

## Antes de cualquier material

Root debe haber cerrado SDK/K4 y cualquier servicio de capacidades. Este programa rechaza locks R06 SDK_SERVICE.lock/SDK_CAPABILITIES_SERVICE.lock y usa SDK_NATIVE_SERIAL_R06.lock entre los focales. Core26 no conoce ese lock nuevo: la exclusividad del operador Root sigue siendo obligatoria. Nunca borre automáticamente un lock antiguo o una transacción incierta.

Primero verifique consumo/reservas/intents cerrados y tiempo real. El pronóstico es18.768ticks para12ciclos de1.564; para la reserva de4.096 del último ciclo se necesitan21.300ticks libres bajo ese pronóstico. No es garantía. El arranque exige ese margen para OSCILANTE y11.916 para CONTROL, además del guard global real. La suma de máximos6×4.096 por dos vidas excede40k: el límite compartido puede truncar.

Use el tiempo real de las sesiones cerradas, más importación/boot/guardado, para confirmar que DOS brazos seriales completos caben y terminan con margen de cierre (recomendado30min antes del hard global). Si no caben, no inicie o declare la truncación prospectiva. Nunca se atribuye falta de tiempo/RAM/saldo a fracaso cognitivo.

## Despliegue

Copie ÚNICAMENTE backend/focal_r06 al runtime CORTO existente del propietario, verificando FUENTES_FOCAL_R06.json. No cree otra copia de420MB, no modifique Core26, SDK_SOURCES.json, PLANTILLA_SISTEMA.json ni una instancia existente. El runtime largo puede fallar DLL antes deStore; el preflight FS de PYD no garantiza carga.

En las órdenes siguientes PY es dependencias/producto/motor/python313/python.exe del runtime corto y el CWD es ese RUNTIME_PRIVADO_LOCAL. Los valores entre<> son valores REALES elegidos/registrados por Root, no literales para pegar.

1. Verificar fuentes (sóloFS):

    <PY> -I -B backend/focal_r06/verificar_fuentes_focal_R06.py

2. Sellar UNA ventana nueva (sóloFS, sin identidad ni ledger):

    <PY> -I -B backend/focal_r06/sellar_ventana_focal_R06.py --execute-fs-only

Crea configuracion/VENTANA_FOCAL_R06.json sin sobrescribir: start=ahora, duración≤6h, last/hard contenidos en la campaña ORIGINAL. Nunca supera20:37:40UTC/21:37:40UTC18Nov2026. Vincula SHA del global y de fuentes. No se resella tras resultados. Si dura menos que el global, sólo restringe el focal.

3. Root reserva dosIDs nuevos SDK_DEMO_<16HEX_MAYÚSCULAS>, OSCILANTE primero. La preparación es FS; no importa Native:

    <PY> -I -B backend/focal_r06/preparar_focal_R06.py crear --instance <ID_OSC> --condition OSCILANTE --execute-fs-only
    <PY> -I -B backend/focal_r06/preparar_focal_R06.py crear --instance <ID_CONTROL> --condition CONTROL --execute-fs-only

El registro PARTICIPANTES_FOCAL_R06.json admite exactamente esos2brazos en orden; un parcial queda preservado y no se reintenta. Cada PREPARACION_FOCAL.json devuelve contextSha256. El prefijo completo se conserva compartido; no se reconstruye un estado desde RAW/relojes.

4. Root importa UNA vez cada vida (Native administrativo0ticks, no experiencia). No ejecutar desde el agente:

    <PY> -I -B backend/focal_r06/preparar_focal_R06.py importar --instance <ID> --context-sha256 <SHA_FOCAL_REAL> --deadline-utc-epoch 1795037860 --execute-root-only

El wrapper recorta al hard focal. Exigir SDK_READY physical_equal/causal_prefix_equal y0ticks; cualquier parcial prohíbe retry ciego.

5. Crear escenas PRIVADAS nuevas (sóloFS):

    <PY> -I -B backend/focal_r06/preparar_escenas_focales_R06.py --private-root <PADRE_DEL_RUNTIME_CORTO> --output <NUEVO_JSON_PRIVADO_DE_ESCENAS>

Son DEE_FOCAL_OSC_R06_01.rbxlx y DEE_FOCAL_CONTROL_R06_01.rbxlx. El helper lee sólo el token privado autorizado, nunca lo imprime; inyecta FolderDEE_FOCAL_PrivateConnection_R06, ModeNATIVE/HTTPtrue y puertos8897/8898. NO publicar ni empaquetar las escenas privadas. Las escenas públicas aquí siguenPREVIEW/sincredenciales.

Las fuentes públicas derivan deR04 sin cambiar Main/body/motor/ley/geométría: sólo HttpTransport admite PENDING_RESOURCE y polling1800, y config usa folderR06/poll1800. La wire sigueConnector.R01/runtime0.1.0 con metadata hostRevisionFOCAL_R06; la INSTANCE interna usa0.1.1 para import0R06.

6. Root inicia OSCILANTE y después carga/ejecuta su escena en el Studio autorizado. Confirmar handshake READY/profileFOCAL/conditionOSCILANTE/offset56/local0/stock164 y preflight físico sólo lectura antes del primerPOST:

    <PY> -I -B backend/focal_r06/iniciar_focal_R06.py start --instance <ID_OSC> --minutes 180 --cycles 6 --port 8897 --validation-campaign --execute-real-native

La lease administrativa previa es0ticks, explícita y finita. No se admite --no-serve. El loop de escena registra cadaID antes de unPOST y sólo haceGET del mismoID. No modifica lectores/NativeValue. NoQuery omite datum, 0 es válido y NULL no significa abstención inteligente.

7. Esperar6completos→cierreNative→captureAgent/World→SDK_PAIR→exit0/drenado. Exportar/preservar y detener la escena sólo después. CONTROL no arranca hasta que OSCILANTE tenga6cerrados, pareja validada y reservas/intents0:

    <PY> -I -B backend/focal_r06/iniciar_focal_R06.py start --instance <ID_CONTROL> --minutes 180 --cycles 6 --port 8898 --validation-campaign --execute-real-native

Puertos distintos NO permiten dos owners simultáneos. Toda excepción conserva el serial lock y losIDs; no se hace kill/replay, ni se crea otroID/lease para eludir el plazo. Root reconcilia el estado real y cierra con prioridad. No hay continuación automática del focal agotado ni promesaK4 del aparato focal.

## Lectura científica

Sólo una consulta realmente pagada transmite el precio local aQ2 (signal+3*tag), con recibo aplicado. permissionStock/queryAvailable sólo habilitan la pregunta; el peaje solo no es retorno adverso. Si no hubo consulta, una diferenciaJSON no acredita exposición. Ambospuertos pagados es inencodable y detiene; no se falsea señal1.

Reportar denominadores reales, decisiones/NULL, peaje+consulta por actionId único, muestras locales agotadas/repuestas realmente encontradas y sus recibosNative. No repetir729trazas estáticas ni llamarlas material. Persistenteloop/noexposición/sindiferencia/parcial son resultados válidos; la diferencia de conducta no prueba aprendizaje. Son dos descendientes emparejados n=1, no réplicas independientes.
