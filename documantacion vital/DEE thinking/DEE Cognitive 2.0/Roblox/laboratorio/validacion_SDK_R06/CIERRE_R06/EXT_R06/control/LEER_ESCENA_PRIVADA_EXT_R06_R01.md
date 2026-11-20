# Escena privada EXT R06

Helper FS/XML, no Native/HTTP/Studio. Crea un archivo nuevo y rechaza sobrescribir. No modifica el KIT congelado ni la escena Core original.

Requiere la escena privada Core exacta SHA28a5bd308b07abfed1696b2e4e0bf4bf702858616ac76f75ff38e34edab5fb7e y el modelo EXT público congelado SHAaa6807c530f662ce11e21f107008978f9bf9ee003f28416c0f85a22fd3b107bb. La conexión CAP debe proceder del helper privado autorizado; no se pega el token en órdenes/chat.

La preparación:
- verifica que Core y CAP correspondan a la MISMA InstanceId;
- desactiva sólo la ejecución del Script SDK_Arranque (Source y módulos Core intactos);
- añade el paquete EXT con Config.Enabled=true, sin admisión automática;
- añade la conexión privada CAP y HttpEnabled local;
- rotula el uso ASSISTED y que la escena de archivo NO es el World físico actual K4;
- no coordina ni mueve el avatar, ni crea una pareja World actual tras avanzar Native.

El helper sólo prepara. La vida Native Core2 ya cerrada no se clona/reinicia. Root instala/inicia CAP aparte, tras sus guardas post-K4 y copia cerrada. El SDK_PAIR anterior pasa a PRE_CAP después del avance de capacidades.

Comando de Root (CWD=tests, ejemplo con rutas completas ya conocidas):

    <PY_STDLIB> -I -B "<SDK>/VALIDACION/CIERRE_R06/EXT_R06/control/preparar_escena_ext_privada_R06_R01.py" --source-scene "<SHORT>/DEE_SDK_CORE_R06_02.rbxlx" --private-connection-xml "<SHORT>/RUNTIME_PRIVADO_LOCAL/configuracion/INYECCION_CAPABILITIES_R06_SDK_DEMO_3666B1B0A4134233.rbxmx" --extension-model "<SDK>/VALIDACION/CIERRE_R06/EXT_R06/KIT_EXTENSION/conector/DEE_SDK_CAPACIDADES_EXT_R06.rbxmx" --output "<SHORT>/DEE_SDK_CAPACIDADES_R06_01.rbxlx" --instance SDK_DEMO_3666B1B0A4134233

SHORT es D:\GENESIS AI\GENESIS 5.0\simulador de universo ab-initio\dee_libreria\VERSION_27\tests\_sdk_r06_valid_20261118. SDK es el directorio DEE_ROBLOX_SDK_PILOTO existente. PY_STDLIB puede ser el Python autorizado de Root: este helper no carga el binario DEE.

Salida estándar: sólo rutas/hashes/flags eID; nunca Token. La escena resultante contiene credenciales privadas: no publicar, compartir ni incluirla en ZIP público.

Root abre/ejecuta la nueva escena y confirma SDK_Arranque inactivo. EXT crea sólo consola/Bindables; GetCapabilitiesRO consulta guardas/instancia antes de un SubmitCapability explícito. Un resultado de la prueba sintética no acredita compilación Luau, disponibilidad del servicio ni ejecución Native real.
