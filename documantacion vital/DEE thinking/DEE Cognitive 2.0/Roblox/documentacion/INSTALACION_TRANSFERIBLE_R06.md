# Instalar la distribución privada de investigación

## Componentes suministrados

El payload `dependencias/DEE_ROBLOX_RUNTIME_PRIVADO_R06.zip`, comprobable mediante `MANIFIESTO_RUNTIME_R06.json`, conserva backend, puentes Core/EXT y sus versiones necesarias, Python embebido 3.13 x64, Thinking 4.5.0 con kernel v27 incorporado, herramientas Cognitive mínimas, dependencias, prefijo PAR28 completo, instancia experimental cerrada T995895 y su ledger. No incluye proyectos completos Universe/Thinking/Cognitive, su principal, credenciales ni autorización activa.

No hay que buscar componentes en la computadora de origen. Las fuentes activas están en `laboratorio/DEE_ROBLOX_RBX01`; el artefacto instalado contiene las dependencias operativas propias. Los constructores históricos sirven para estudiar/regenerar con sus contratos, no son una etapa obligatoria del instalador R06.

## Requisitos

Windows x64 compatible con CPython 3.13 y las DLL incluidas; permisos ordinarios para crear una carpeta corta nueva y espacio libre para el payload expandido más margen. Roblox Studio se instala por su canal oficial y requiere cuenta/autenticación propias. No se suministran cuentas ni sesiones. La ABI en otra plataforma no está validada. No se instalan paquetes desde Internet.

## Instalación física, sin sesión Native

Transferir la selección privada completa. En PowerShell, desde la carpeta recibida:

```powershell
.\instalacion\INSTALAR.bat 'C:\DEE_RBX_RT'
```

El destino debe ser nuevo y corto. No se sobrescribe un runtime ni se reanuda una instalación incompleta automáticamente. El bootstrap verifica SHA-256 mediante certutil, extrae con tar de Windows y ejecuta el Python incluido para verificar todos los miembros. La comprobación previa de rutas usa órdenes PowerShell de lectura; no ejecuta archivos .ps1 ni cambia políticas de seguridad. Instalar_Roblox.ps1 queda como alternativa cuando la política del equipo permite scripts; el primer intento local fue bloqueado y se conservó su registro. No exige un Python preinstalado. Si una política del sistema impide ejecutar el script, debe respetarse; alternativamente, un Python 3.13 x64 ya autorizado puede ejecutar:

```powershell
python -I -S -B .\instalacion\instalar_runtime.py --destino 'C:\DEE_RBX_RT'
```

Los destinos de ejemplo son configurables, nunca rutas de respaldo silencioso. El runtime local original se conserva donde funcionaba, sin reconstruirlo ni tocarlo.

## Comprobar sin actuar

```powershell
& 'C:\DEE_RBX_RT\dependencias\producto\motor\python313\python.exe' -I -S -B .\instalacion\instalar_runtime.py --destino 'C:\DEE_RBX_RT' --verificar
& 'C:\DEE_RBX_RT\dependencias\producto\motor\python313\python.exe' -I -S -B .\instalacion\verificar_abi_sin_mundo.py --runtime 'C:\DEE_RBX_RT'
& 'C:\DEE_RBX_RT\dependencias\producto\motor\python313\python.exe' -I -S -B .\instalacion\plan_sesion.py --runtime 'C:\DEE_RBX_RT'
```

La prueba ABI importa sólo biblioteca/metadatos, sin crear Runtime, World ni propietario; no acredita funcionamiento material. La instalación deja `CONEXION_PRIVADA.json.template`, sin clave válida. Nunca copiar una conexión antigua. `proveer_conexion.py --help` explica la provisión explícita de una clave suministrada por el responsable autorizado; no genera claves ni renueva sesiones. No ejecutarlo con credenciales de otro investigador.

## Emparejar posteriormente

El responsable debe autorizar un protocolo prospectivo, duración, presupuesto, instancia y emparejamiento. La ventana antigua está caducada. Hay que conciliar estado Native/ledger y mundo antes de abrir un escritor; Core T994315 no es la pareja actual de CAP T995895. No borrar pendientes, reimportar T0, reiniciar contadores ni relabelar una pareja antigua para eludir este límite. La provisión de una clave HTTP por sí sola no autoriza ticks.
