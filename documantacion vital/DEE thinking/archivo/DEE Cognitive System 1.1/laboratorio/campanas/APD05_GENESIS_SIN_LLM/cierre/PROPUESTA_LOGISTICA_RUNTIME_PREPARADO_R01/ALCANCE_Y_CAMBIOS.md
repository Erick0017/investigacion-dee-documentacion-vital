# Propuesta de exportación con runtime preparado

No está aplicada. No se ejecutó el actualizador ni se creó un Full. Se inspeccionaron únicamente los filtros operativos necesarios y el runtime que ya existe en la fuente canónica. No se importó Native, no se cambió el Word y no se escribió en el sistema fuente ni en la distribución real.

## Impedimento localizado

El actualizador APD04 declara `motor/python313/site-packages/` como zona no gestionada; su exploración final también excluye esa ruta. El Full anterior incluía intérprete y WHL, pero `arrancar.prepare()` extraía el WHL al primer inicio cuando no encontraba `INSTALACION_DEE.json`. Ese comportamiento es offline, pero sigue siendo instalación al abrir y no satisface APD05 sección5.

La fuente actual ya contiene CPython embebido y `site-packages` preparado. El contraste de lectura contra todos los miembros del WHL oficial y el PYD esperado coincidió. La selección propuesta contiene68 archivos y25,951,524 bytes expandidos, incluyendo el intérprete ya existente y un comprobante descriptivo generado. No se preparó de nuevo ese runtime.

## Cambios propuestos

`actualizar.py` copia `ABRIR_GENESIS.bat` y la lista explícita de siete archivos operativos de la aplicación más `SELECCION_CANDIDATA.json` desde la fuente. Omite `aplicacion/GENESIS/pruebas/`, que conserva telemetría y pruebas locales, no dependencias operativas. Añade sólo los archivos operativos al control de cierre por fecha y copia un solo CPython relativo a `motor/`. Los miembros admitidos de `site-packages` son exactamente los del WHL congelado y el marcador ya existente. No copia paquetes extra, ganchos `.pth`, cachés ni entornos del autor. Compara los bytes antes de incorporarlos al manifiesto normal y mantiene los conflictos de modificaciones locales. Un runtime fuente ausente o diferente impide exportar; no se instala automáticamente.

Se elimina únicamente la exclusión global de `motor/python313/site-packages/` para permitir que esos miembros oficiales se gestionen. `trabajo_personal`, respaldos, conflictos y temporales continúan protegidos. En `finish()`, los miembros antiguos y la exploración del runtime receptor usan `setdefault`, de modo que no sustituyen hashes de archivos fuente nuevos ya preparados para una transacción. El resto de la copia y la aplicación incremental conserva su mecanismo anterior.

`arrancar.py` cambia la extracción inicial por `verify_prepared_runtime()` de sólo lectura. Comprueba marcador, WHL y archivos instalados, incluido PYD. Una ausencia o alteración produce error sin crear carpetas ni reparar nada. `prepare()` sólo configura después el espacio personal y variables de proceso. La GUI debe reutilizar esa verificación sin instalar; su implementación corresponde al agente GUI, no a esta propuesta.

El catálogo de vidas no necesita otro mecanismo. Antes de exportar, Root debe añadir explícitamente la vida y el alias finalmente seleccionados a la selección de distribución y conservar el par completo conforme al procedimiento existente. No se elige la candidata por tick ni se copian conocimientos entre vidas.

## Comprobación N0 y límites

`PRUEBA_N0_R03/PRUEBA_PROPUESTA_N0.json` registra ocho comprobaciones sin incidencias de la propuesta con la lista GUI acotada; R01 y R02 permanecen conservados. Se verificaron todos los bytes oficiales del runtime fuente sin modificarlos; se ensayaron en un árbol sintético la adopción de bytes ya idénticos, un conflicto local protegido y el rechazo a gestionar `trabajo_personal`. Un marcador ausente falló sin instalar ni crear el destino. No se ejecutaron `system()`, `finish()`, `main()`, `seal_zip()` ni operaciones Native sobre la distribución real.

La versión previa al ajuste de exploración final se conserva byte-exacta en `actualizar_ejecutado_antes_scan_fix_n0_r01.py`, hash04c05bc2a27fb3500d9cabfe2a9ef82c80fb4f8f3e98350d69ef021c7f111a58, correspondiente al primer ensayo. La propuesta actual tiene su hash en el segundo comprobante. La prueba real del Full exacto y el arranque de la GUI quedan pendientes del cierre, aprobación y ejecución de Root; el resultado de estas comprobaciones no los sustituye.
