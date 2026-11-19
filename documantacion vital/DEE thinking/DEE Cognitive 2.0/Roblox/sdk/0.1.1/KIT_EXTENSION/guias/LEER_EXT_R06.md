# Capacidades Native asistidas · EXT_R06

Estado de validación local, 18 de noviembre de 2026: se ejecutaron y cerraron diez solicitudes Native del servicio R03 sobre la vida SDK autorizada. Se observaron memoria/revisión de luma, comparación con resultados +1/−1/0, suma 4+5=9 y composición asistida con intermedio real 9 y resultado 7. El cierre Native está comprobado; el recibo HTTP CLOSE se recuperó mediante GET del mismo ID, sin repetir POST ni material.

La revisión R04 del servicio añade una corrección técnica de la gracia de cierre HTTP y tiene pruebas sintéticas; no se presenta como otra ejecución material. El operador decide la solicitud y el orden de COMPOSE. Native produce los valores y el intermedio; no se acredita planificación autónoma. SOLVE se usó dentro de COMPOSE, sin un ensayo directo separado. La comunicación con un segundo participante Native no está integrada ni expuesta en este SDK.

El Core K1–K4 tiene su validación local separada. La pareja K4 cerrada en T994315 se conserva como historia; después de capacidades, esa vida Native quedó cerrada en T995895 y el World/Agent previo es PRE_CAP. No se ha restablecido un loop Core ordinario después de la extensión. El acceso inicial sigue siendo local acompañado, y la evaluación externa continúa pendiente.

Los Sources Luau/XML y los pines originales permanecen intactos. Esta revisión sólo corrige el estado de esta guía y su manifiesto; los pines documentales originales conservan su texto previo como procedencia. ESTADO_VERIFICACION.json registra los resultados y límites.

El desarrollador elige el experimento y aporta las entradas. Native produce la respuesta. Esta modalidad ASSISTED no demuestra elección autónoma de herramientas, aprendizaje por admitir una lección ni lenguaje general.

## Instalación y uso

1. Complete primero K4. El propietario prepara el servicio privado EXT sobre esa vida SDK cerrada, sin pendientes y expresamente autorizada. No use ACTIVO ni otra vida como alternativa.
2. Importe conector/DEE_SDK_CAPACIDADES_EXT_R06.rbxmx en ServerScriptService o abra ejemplos/DEE_SDK_CAPACIDADES_EXT_R06.rbxlx. Se crean una consola española y Bindables normales. No contiene SDK_Arranque ni motor de avatar. Está deshabilitado por defecto y no hace HTTP ni material al instalarse.
3. En la copia privada, el propietario configura ServerStorage/DEE_SDK_CAPABILITIES_PrivateConnection_R06 con StringValues BaseUrl, InstanceId y Token; habilita HttpService local y pone Enabled=true en Config_EXT_R06. BaseUrl sólo admite HTTP sobre 127.0.0.1. El JSON público es una plantilla: no se lee del disco automáticamente. Token fuera de Source, chat, UI, registros y ZIP.
4. Consulte GetCapabilitiesRO y compruebe instancia, sesión, versión, postK4Guard y límites. STARTING/PENDING_RESOURCE no es un resultado ni autoriza un nuevo envío.
5. Invoque SubmitCapability explícitamente. ID y cuerpo se registran antes de un único POST. Sólo se admite una operación local a la vez. GetOperationRO consulta el mismo ID. Un error incierto conserva el ID y bloquea nuevas admisiones; no hace rePOST ni genera otro ID para conseguir otra respuesta.
6. Lea el JSON bruto completo: 0 permanece 0 y NULL permanece en responseRaw. La vista puede recortarse sin truncar el registro, guardado en bloques de hasta 16.000 bytes; vea la guía API.
7. Solicite CloseCapabilities sin material pendiente y consulte su ID hasta el cierre confirmado. Tras avance Native, la pareja SDK previa queda PRE_CAP y no describe un World actual. El descriptor cerrado de capacidades no es una nueva pareja World/Agent ni habilita continuación automática del core.

## Alcance

RECALL, LESSON, NUMERIC, SOLVE, COMPOSE y COMPARE usan los mecanismos Native anunciados. Evalúe enseñanza mediante consultas posteriores reales. SOLVE acopla recuerdo y operación; COMPOSE usa el intermedio real y se detiene si falta o sale del dominio. El orden del pipeline está preparado y no prueba planificación autónoma. COMPARE no usa un comparador Python/Lua.

Los dominios son luma/nara y los enteros declarados. El protocolo admite scopes de hasta 12 eventos; esta validación selló 10 y ejecutó 10. CLOSE y GET no consumen eventos Native. Hasta 4096 ticks/evento y 40k global compartido. No se escribe RAW, relojes, bancos o ley Native.

El propietario decide el acceso al runtime privado. No hay endpoint público por Internet ni licencia inventada. La evaluación externa sigue pendiente; no se contacta a terceros. Consulte RUTAS_WINDOWS_PREFLIGHT.md para la ruta operativa corta requerida por la carga DLL observada.
