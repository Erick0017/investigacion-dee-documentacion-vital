# Preflight externo y modalidad inicial R06

El núcleo histórico de 26 fuentes conserva su comando requisitos. Su ready=true basado en find_spec sólo indica que el módulo puede localizarse; no demuestra carga DLL ni ejecución Native.

Antes de preparar o importar una identidad nueva, ejecute control/preflight_carga_windows_R06_R01.py con la raíz privada y las rutas relativas efectivas de PYD, Python y lanzador. Es una inspección FS: no importa Native, no crea Store, no prepara identidades ni inicia procesos.

El helper devuelve código 2 si falta un archivo, hay un enlace/reparse point o una ruta alcanza 240 unidades UTF-16. Bloquee ahí la preparación/importación. Una salida 0 sólo significa FS_PATH_CHECK_CLEAR_LOADER_UNVERIFIED: ready y materialReady permanecen false. El umbral es preventivo; no garantiza la carga de todas las dependencias.

La ruta larga del origen falló antes de Store; el despliegue corto autorizado completó import0 sin avanzar ticks. Para un despliegue nuevo se recomienda una raíz corta como C:\DEE_SDK, conservando el runtime completo y su manifiesto. No se modifica el registro ni se mueve una instancia activa.

La modalidad inicial del piloto es local y acompañada en este PC. No se entrega el runtime privado ni se ofrece un endpoint remoto. El KIT público y la extensión preparada no acreditan servicio autónomo disponible. El propietario ejecuta el preflight real y decide el acceso.

El servicio en uso, el core congelado y las vidas previas no se modifican. No ejecute este helper como sustituto de la verificación real del cargador.
