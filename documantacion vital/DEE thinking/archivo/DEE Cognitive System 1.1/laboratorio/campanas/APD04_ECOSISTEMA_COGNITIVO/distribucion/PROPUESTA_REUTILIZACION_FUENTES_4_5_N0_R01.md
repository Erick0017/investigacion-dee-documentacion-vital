# Propuesta logística N0: reutilizar fuentes 4.5 verificadas

Estado: PROPUESTA NO APLICADA. No se modificó ni interrumpió el actualizador 14650, ni se ejecutó Native. No es investigación científica ni cambio del motor.

## Inspección dirigida

Archivo ejecutado examinado: `casos practicos/trabajo_codex/cognitive sistem/actualizaciones/actualizar.py`, función `Build.documentation()`.

La función selecciona nueve rutas del índice Core bajo `cpc8/genealogia/product45/`, con extensiones `.cpp/.hpp/.h/.json/.md/.txt`. Construye `wanted` por SHA y recorre `RECUPERACION_POR_HASH.jsonl.gz` completo. No interrumpe el bucle cuando `wanted` queda vacío. El gzip mide 78,200,945 bytes comprimidos. No se volvió a abrir ni descomprimir para esta comprobación N0.

No hay una copia de la cápsula en esta función: es un recorrido/descompresión/parseo de líneas. `Build.add()` ya detecta que los destinos idénticos existen y evita escribirlos, pero sólo después de haber recuperado sus bytes desde la cápsula.

Las nueve rutas ya distribuidas suman 223,954 bytes. Las nueve coinciden simultáneamente en SHA-256 con el índice Core, en SHA con `ARCHIVOS_GESTIONADOS.json` y en tamaño con el manifiesto. No hay colisiones de basename en esta selección.

| Destino `fuentes/thinking_4_5/` | SHA-256 del índice y destino |
|---|---|
| BUILD_INFO.json | 07cd4dffccac15bdb4e4a00473c2c80e64350bb40b7de0a69fa9de5be3d08ee1 |
| consolidated.cpp | b6ebc96e9bf41711b511367e881058b869bef32e0b3d3f1f74fdbff47cb26f06 |
| kernel_v27.cpp | fbd8190381ed76085f404e6578ff15fe185ab66cd48c67300d2abad61ddc7e31 |
| MATRIZ_CAPACIDADES_CPC.json | feb944aaa56c71eeb1b2d70389090a2d10212ffee5a414bda6c66b45d97f99d6 |
| MATRIZ_SUPERSESIONES.json | b3461e2e32a822eff1aec8e2f300054cb70ef68bf7fc06b06311b091fccd47a4 |
| PRODUCT_CONTRACT.json | b8bde9d8ef4385a38085a94ff52ac3e860108799d443f34faa55c9d2534cce75 |
| VALIDATION_REPORT.json | 4ee18d224b90c08cfb7621cdfeff596d8d7e1f7bef789e6cbe7029fdd334b7f2 |
| informative.cpp | d5ee928096106c8f656ee0c8089b5b585cc79dd14e37f62bc345626cad39cd7a |
| PROVENANCE.json | 537e6b3eb44da309779cd30f9c102614eecf7ab65af235f6a5ae5fc806872b8d |

## Cambio mínimo propuesto para una futura actualización, no para el proceso vivo

1. Construir la misma selección íntegra desde `INDICE_MIEMBROS.json`. Rechazar colisiones de basename con SHA distintos; no aceptar una selección parcial.
2. Para cada destino existente comprobar: miembro gestionado previo; SHA esperado del índice igual al del miembro previo; tamaño y SHA reales iguales. No usar fechas ni sólo el nombre.
3. En caso válido, leer esos pocos bytes y llamar al mismo `self.add(nombre, bytes, 'Core::'+original)` para conservar validaciones, miembros y procedencia existentes. Eliminar sólo ese SHA cubierto de `wanted`.
4. Si todos están cubiertos, no abrir el gzip. Si faltan, recorrerlo por el método actual y verificar SHA del contenido Base64; interrumpir al quedar `wanted` vacío. Mantener el error final cuando falten fuentes.
5. No saltar la lógica de conflictos para archivos locales modificados o no gestionados. Esos casos deben continuar por recuperación normal y `Build.add()`, que preserva la variante local y registra el conflicto.

La verificación final del paquete/manifiesto sigue siendo obligatoria. El cambio sólo evita recuperar fuentes inmutables ya verificadas; no altera kernel, WHL, vidas, índices científicos ni contenidos distribuidos.

## Pruebas logísticas prospectivas (todavía no ejecutadas)

- Nueve destinos intactos: cero apertura de cápsula; nombres, hashes, tamaños y orígenes finales idénticos.
- Un destino ausente: recuperar sólo ese SHA y conservar la identidad de los otros ocho.
- Un destino modificado por el colaborador: misma protección de conflicto, sin sobrescritura silenciosa.
- Índice con fuente nueva o SHA diferente: no reutilizar el archivo antiguo; recuperar y validar.
- Fuente requerida ausente de la cápsula o corrupta: mismo error explícito, no paquete aparentemente completo.

Esta propuesta no demuestra que el proceso 14650 esté detenido o averiado: sólo localiza trabajo redundante en el código. No se utilizaron sus tiempos para inferir un fallo cognitivo.
