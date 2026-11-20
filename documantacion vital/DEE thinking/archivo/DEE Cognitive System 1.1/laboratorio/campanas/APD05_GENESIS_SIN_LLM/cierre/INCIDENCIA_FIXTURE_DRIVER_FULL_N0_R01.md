# Incidencia de construcción del fixture de archivo

La primera prueba sintética `probar_driver_full_genesis_n0_r01.py` terminó con código1 y `ValueError: Unsafe archive accepted`. No abrió GUI, no extrajo un Full ni importó Native.

El caso previsto como nombre ZIP con barra inversa fue normalizado por `ZipInfo` en Windows antes de escribirse. El archivo producido tenía una ruta relativa segura con barras normales: su aceptación no demostraba que el verificador aceptara el nombre inseguro que pretendía ensayarse.

Se conservó R01 y su carpeta. R02 cambia sólo el generador sintético: fija explícitamente `ZipInfo.filename` y `orig_filename` para que los bytes archivados contengan el nombre deliberadamente inválido. El driver no cambió por este incidente. Las once comprobaciones R02 concluyeron sin discrepancias, incluidos los archivos inseguros, uint64 como cadenas y rechazo de protocolos no aprobados.

Es una corrección del instrumento de prueba, no un resultado físico, una adquisición o una repetición de un ensayo DEE. La prueba operativa real del Full sigue pendiente de autorización y protocolo cerrado.
