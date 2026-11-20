# Capacidades Native asistidas · EXT_R06

Estado: código preparado y verificado de forma estática. Compilación Luau y validación material pendientes del operador. El core 0.1.1/Max3 y sus 26 fuentes congeladas permanecen intactos.

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

Los dominios son luma/nara y los enteros declarados. Se mantienen los límites del servicio: hasta 12 eventos, 4.096 ticks/evento, 40.000 globales compartidos y fechas de campaña. No se escribe RAW, relojes, bancos o ley Native.

El propietario decide el acceso al runtime privado. No hay endpoint público por Internet ni licencia inventada. La evaluación externa sigue pendiente; no se contacta a terceros. Consulte RUTAS_WINDOWS_PREFLIGHT.md para la ruta operativa corta requerida por la carga DLL observada.
