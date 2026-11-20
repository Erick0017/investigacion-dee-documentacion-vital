# Recalcular y localizar evidencia

## Revisar sin motor ni rutas históricas

Desde la raíz extraída, con Python 3.10 o posterior:

```powershell
python CODIGO_Y_RECALCULO/extraer_registros.py --root . --report DATOS_VERIFICADOS.json
python CODIGO_Y_RECALCULO/recalcular_analisis.py --root . --out RECALCULO_REHECHO.json
python CODIGO_Y_RECALCULO/recalcular_analisis.py --root . --out CAMPOS_REHECHOS.json --deep
```

El primer comando verifica SHA-256, tamaños y miembros del archivo de datos, sin escribir todo su contenido. El segundo desempaqueta RAW exactos, vuelve a calcular los decodificadores fijos, revisa cabeceras de padres y reproduce el factorial. No utiliza las palabras esperadas para elegir una respuesta; sólo las compara después para calcular indicadores del auditor. `--deep` reconstruye los arrays RAW/clocks de cada campo global registrado y contrasta sus hashes. Las líneas de ruta que no son campos globales se cuentan por separado.

El resultado sin `--deep` debe coincidir con `ATLAS_CAUSAL/RECALCULO_DATOS.json`. El informe de campos y el comprobante externo documentan la comprobación profunda realizada. Las repeticiones son recálculos técnicos, no individuos ni adquisiciones nuevas.

## Extraer un experimento concreto

```powershell
python CODIGO_Y_RECALCULO/extraer_registros.py --root . --out CONSULTA --prefix primarios/LECTOR_POST_TRANSFORMACION_41/full/
```

Se verifica todo el contenedor, pero sólo se escriben los miembros cuyo prefijo se solicitó. No se aceptan rutas que salgan del destino, enlaces ni código incrustado. `INDICE_REGISTROS.json` distingue hash/tamaño del archivo local original y hash/tamaño de su payload transportado. En JSON primario son los mismos bytes; en trazas gzip se preservó exactamente el JSONL descomprimido, no la cabecera comprimida original.

`EVIDENCIA_ESENCIAL/EXTRACTOS_DECISIVOS.json` ofrece valores legibles para comenzar. Cada extracción tiene miembro, SHA del primario, JSON Pointer y SHA canónico de su valor. Es una extracción de valores, no una falsa afirmación de identidad de serialización con el archivo entero. Ese archivo original íntegro está en el contenedor de datos.

## Código y revisiones

`REVISIONES.json` enlaza los nombres originales con objetos `.py` por contenido. Se conservan los bytes de las revisiones relevantes capturadas antes de ejecutar y las correcciones técnicas. Capturar un archivo no demuestra que todas sus funciones se ejecutaran. Los scripts de recálculo aquí expuestos son los de uso directo; los drivers científicos y sus dependencias de la capa 1.1 se localizan mediante ese índice.

Las fuentes actuales, los cambios de interfaces y sus alcances no son un nuevo producto 4.5. No se incluye ni se reconstruye el kernel. Las revisiones fallidas se conservan como texto de genealogía, no como programas que deban ejecutarse ni archivos cuya sintaxis se anuncie válida.

## Continuar física o repetir un control nativo

Requiere el entorno oficial CPython 3.13 x64, DEE thinking 4.5.0 y el estado completo local que indica la ficha de continuidad. Los primarios y arrays de este análisis no sustituyen esa sesión. No se importa código desde `entregas/` en el funcionamiento normal del sistema.

Los dos archivos `*_SOLO_DIAGNOSTICO.deetsnap.gz` incluyen el Runtime nativo previo a un encuentro y su cola, pero no el progreso Python refrescado de la sesión. Permiten analizar el paso nativo con el instrumento oficial y los drivers de diagnóstico conservados; no son una vida aprendida que pueda restaurarse silenciosamente como E1.

Las recetas nuevas N11/N17 y N67/N83 y los controles quedan en sus drivers exactos. Las ramas E1 requieren sus checkpoints completos externos explícitos. No se afirma que el ZIP de análisis sea un respaldo operativo autosuficiente ni que todos los cuerpos heredados pertenezcan a una sola vida.
