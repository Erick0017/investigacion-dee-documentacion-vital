# Cierre de análisis APD04 — preparado, no ejecutado

Estos instrumentos adaptan el patrón de ensamblado, recálculo y extracción exacta usado en APD03. No abren un Runtime ni ejecutan el motor, no editan Word y no actualizan el Full. La selección científica y la promoción siguen siendo decisiones explícitas de Root.

## Entrada única al cierre

Root debe crear `RESULTADOS_FINAL.json` conforme a `RESULTADOS_FINAL.schema.json`, con `status: FINAL_RESULTS_APPROVED_FOR_ANALYSIS` y `native_work_closed: true` sólo tras cerrar los escritores de las fuentes incluidas. No usar el borrador científico como si fuese el resultado final.

`files` enumera archivos cerrados individuales con SHA previo. `components` admite expedientes compactos ya cerrados cuyo manifiesto enumera cada miembro real (claves `members` o `files`, nombre `file` o `path`, `bytes`, `sha256`). Se copian sólo sus miembros manifestados y el propio manifiesto. No se hace una búsqueda histórica ni una selección por fecha. Si el componente contiene un motor, una base de datos o snapshot completo, el ensamblador se detiene: preparar antes una extracción primaria exacta con su índice, sin ocultar un contraejemplo.

Conservar todos los intentos en `attempts`, incluidos R01 sin Native, timeout de supervisión, corte adverso bloqueado, reservas incompletas y controles con incidencias. `source_ids` conecta cada afirmación, intento y revisión con las fuentes seleccionadas. Los números no calculados deben permanecer `null` con su alcance, no convertirse en cero. Las revisiones ejecutadas deben conservar sus bytes congelados, no sólo el código actual.

`lives` distingue el predeterminado protegido, MAIN adverso y cada bifurcación. Un futuro no comprometido no se convierte en continuación utilizable. Un fork desde T639374 no comparte el futuro T658938. Los pares completos y las colas permanecen localmente; el análisis no es un respaldo operativo.

## Recálculos reales seleccionados

Cada `job` declara un script conservado, su base relativa, los argumentos, un resultado de referencia real y el modo de comparación. Un argumento de entrada se escribe `{"input":"RUTA_RELATIVA"}`; la salida nueva se escribe `"{output}"`. No usar rutas absolutas ni marcadores del evaluador como entrada a un ente. `comparison: bytes` exige identidad de bytes; `json_values` exige identidad de valores, y se informa como tal.

El ejecutor corre cada CLI con `-I -B`, desde un temporal ajeno al paquete, y una cerca de auditoría que rechaza lecturas históricas, escrituras dentro del paquete, red, procesos hijos, `ctypes` y motores. Sólo permite lecturas del análisis y la biblioteca estándar, y escrituras en un directorio externo nuevo. Es una comprobación de dependencias de calculadores confiables, no un sandbox de seguridad para código hostil. No ejecuta Native ni verifica el Full.

## Comandos, sólo después de autorización de Root

Desde este directorio, usando el intérprete ya instalado:

```powershell
python -I -B preparar_entrega_apd04_r01.py check-selection --results RESULTADOS_FINAL.json
python -I -B preparar_entrega_apd04_r01.py assemble --root RUTA_COGNITIVE --results RESULTADOS_FINAL.json --out RUTA_NUEVA_LAB_CIERRE --root-go APD04_ANALYSIS_CLOSED_APPROVED
python -I -B RUTA_NUEVA_LAB_CIERRE\RECALCULO\recalcular_todo.py --root RUTA_NUEVA_LAB_CIERRE --out RUTA_NUEVA_PRUEBA_ARCHIVADA
python -I -B preparar_entrega_apd04_r01.py seal --candidate RUTA_NUEVA_LAB_CIERRE --delivery RUTA_ENTREGAS --proof RUTA_NUEVA_PRUEBA_ZIP --root-go APD04_SEAL_EXACT_ANALYSIS_APPROVED
```

El sello conserva el candidato incluso si falla. No reemplaza un ZIP existente. Crea el ZIP exacto, exige máximo16,000,000 bytes, comprueba CRC/miembros/hashes, extrae ese ZIP a otra ubicación y ejecuta allí los recálculos archivados. Sólo publica una copia byte-idéntica tras la comprobación. El SHA del ZIP figura exclusivamente fuera del contenedor en `VERIFICACION_FINAL_EXTERNA.json`. Una edición posterior exige otro candidato y otro sello.

## Documentos y Full

Incluir el Word real actualizado y su comprobante estructural/editorial sólo después de la operación autorizada. Una ausencia de renderer se documenta con cero páginas verificadas; no inventar validación visual. Incluir el comprobante Full cerrado cuando exista, sin incrustar su ZIP ni confundir recálculo archivado con una adquisición Native desde la extracción Full.

No invocar estos comandos mientras los experimentos o controles que afecten fuentes seleccionadas sigan escribiendo. Las herramientas están preparadas; esta guía no autoriza por sí sola sellar, editar el Word o actualizar distribuciones.
