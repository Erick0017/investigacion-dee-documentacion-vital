# Inicio y requisitos

## Core

Abra KIT_DESARROLLADOR/ejemplos/DEE_SDK_PILOTO_0_1_1.rbxlx, o importe KIT_DESARROLLADOR/conector/DEEConnector_SDK_0_1_1.rbxmx en ServerScriptService. Use una entrada, no ambas. Los nombres y Sources son los congelados. Mode=PREVIEW construye el aparato/NPC y no abre Native; no satisface K2/K3.

Para Native, el propietario debe proporcionar una vida diagnóstica completa, lease vigente, servicio privado local y autorización real. El propietario configura HTTP del Place local y la conexión en ServerStorage; Token nunca en Source, chat, guía o archivo público. No se tocan ajustes globales ni se eluden denegaciones. Si falta el backend, se informa el bloqueo: no hay FakeNative fallback.

Core conserva MaxOpportunities3/MaxActions6/RunCycles1; un cierre y una continuación son explícitos, nunca una renovación infinita. El contratoK4 previo está en KIT_DESARROLLADOR/guias/CONTRATO_K4_R06.json. Su texto fija criterios, no sustituye el resultado Root actual. Tras un cambio de geometría/sensores/bindings se necesita validación propia; no cambie lector/bancos para adaptar el mapa.

## EXT

Importe KIT_EXTENSION/conector/DEE_SDK_CAPACIDADES_EXT_R06.rbxmx en una escena aparte o abra su ejemplo. Enabled=false y NoAutomaticMaterial=true. La consola es ilustración hasta que el propietario autorice/configure el servicio separado y habilite su copia privada. Primero GetCapabilitiesRO; SubmitCapability es MATERIAL, explícito, iniciado por el desarrollador. Native devuelve el valor literal; 0 es válido y NULL no se rellena. El cliente registra ID antes de unPOST y sólo consulta el mismoID.

EXT no dirige ni coordina el avatar. Sus capacidades asistidas no prueban elección autónoma de herramienta. Después de avance Native, la pareja SDK anterior es PRE_CAP y no representa un World actual: una escena de archivo debe rotularse como preparación. No reactive el loopCore sobre esa pareja sin un protocolo autorizado nuevo.

## Backend y Windows

El acceso inicial es local acompañado; ni el runtime privado ni un endpoint remoto se distribuyen aquí. El propietario decide futuras modalidades/accesos. No se inventa licencia ni promesa de instalación en3min o respuesta inmediata. Use un runtime autorizado en raíz corta, por ejemplo C:\DEE_SDK: localizar el PYD con find_spec NO demuestra cargaDLL. El preflightFS inspecciona rutas y tampoco acredita carga material; el propietario debe verificar el cargador real antes de preparar una identidad. Nunca mueva una vida activa o recopie sólo RAW/relojes.

Las esperas son finitas, aceptan PENDING_RESOURCE y preservan IDs. Ante incertidumbre, no rePOSTee ni cree otroID para obtener otra respuesta. Mantenga un solo escritor Native. No publique escenas privadas, tokens o estados. Consulte KIT_EXTENSION/guias/API_DESARROLLADOR_ES.md para las seis solicitudes y lectura íntegra por bloques.
