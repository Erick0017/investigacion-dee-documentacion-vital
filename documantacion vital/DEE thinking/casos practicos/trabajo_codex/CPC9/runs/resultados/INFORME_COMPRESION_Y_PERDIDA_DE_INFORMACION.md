# Compresión y pérdida de información

Los ZIP CPC3–CPC7 examinados suman 125,442,378 bytes comprimidos y 25,497,667,043 bytes expandidos. CPC1/2 están dentro de la genealogía CPC3.
Se conservan 8,933 nombres lógicos en 4,357 blobs únicos. Los bytes seleccionados suman 1,413,434,981; tras deduplicar, 1,344,237,249. El almacén gzip ocupa 78,200,945 bytes.

## Conservado

Código y variantes ejecutadas, configuraciones y parámetros, identidad del instrumento, catálogo NSM de origen, telemetría terminal original con controles/errores/reservas, fuentes de las56filas históricas de la matriz final, pruebas actuales y once semillas/checkpoints MBP4, ocho padres diagnósticos CPC6 y un padre L15 indispensables. Los miembros se recuperan por sus nombres y hashes exactos. No hay ZIP antiguos completos anidados. La corrección editorial47→56 se registra en ERRATAS_EDITORIALES_EXTERNAS.json; no cambia los ZIP sellados.

## Excluido

Entornos, toolchains, vídeos, gráficos repetidos, logs repetidos, mayor parte de snapshots densos y temporales. En CPC3–CPC7 los snapshots `.deetsnap` no seleccionados representan 24,230,806,827 bytes. Las variantes únicas de código ejecutado sí se conservan por hash.

## Consecuencias

La reproducción ejecuta las trayectorias de los contratos seleccionados y vuelve a generar estados/observaciones. El estado físico y los campos primarios se comparan con referencias inmutables. No se afirma regeneración byte-exacta de todos los contenedores: versiones, rutas, identificadores documentales y nombres de intentos pueden diferir sin cambiar RAW/clocks.

Los snapshots históricos no seleccionados de dominios no reproducidos NO se declaran recuperables. Su trayectoria fina no puede revisarse desde este Core sin el archivo original. Su código y evidencia terminal permanecen. La matriz deja esas capacidades pendientes y no las llama sustituidas operativamente. No se autoriza borrar los originales.

El tamaño del ZIP final, su tamaño expandido real y el hash exacto se informan fuera del ZIP. Los bytes lógicos materializados del almacén no deben confundirse con el tamaño expandido del contenedor.

Las copias archivadas CPC3–CPC8 (incluidas las dos campañas CPC8) suman 229,971,007 bytes comprimidos y 26,518,414,628 bytes expandidos. No es un recuento de información única.
El índice final conserva 20 nombres de snapshots/checkpoints esenciales. Las exclusiones volumétricas iniciales no incluyen las excepciones comprimidas añadidas después; COMPRESION.json enumera cada excepción.

## Correcciones conservadas

Los informes iniciales de auditoría que no coincidían se conservan. En orden, la antigua bandera de metadata de sesión falsa se separa de los RAW/clocks y ahora se exige restauración efectiva. En bucle/comparación CPC3, los campos pasivos añadidos posteriormente no se inventan en la referencia antigua. En flujo CPC5 se recuperó la fuente ejecutada original por SHA en lugar de comparar una versión posterior. Ninguna corrección cambia el motor, la experiencia, la política, el decoder ni convierte un caso funcional negativo en positivo.

## Artefactos sellados de esta entrega

DEE_COGNITIVE_CORE_CPC01_A_CPC08.zip: 73601685 bytes comprimidos; 95481181 bytes expandidos; SHA256 `412a6819e36203a0086790003301a13722bd14fd3a3213b03681d827f7cca1a2`.

CPC9_ONTOGENIA_SEMANTICA_NATIVA65_RESULTADOS.zip: 65870122 bytes comprimidos; 722011116 bytes expandidos; SHA256 `917a559b917388fc63a6948762d73c3e87a00c30199c5b65c635a8d39bf96bad`.

CPC9 es evidencia nueva, no parte del porcentaje de reducción histórico del Core. Sus primarios/adversos/checkpoints se conservan. Los duplicados exactos menores se mantienen si quitar rutas exigiría un nuevo contrato; no se atribuye la reducción a compresión sin pérdida de TODO el corpus.
