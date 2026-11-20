# Cambios del Manual Maestro ENTE02

La edición documental 1.11 actualiza el Word real de la raíz de DEE Cognitive System 1.1. No cambia Cognitive 1.1.0, DEE thinking 4.5.0 ni Universe v27.

Archivo vigente:
`DEE_Cognitive_System_1_1_Manual_Maestro_Continuidad_Edicion_1_11_ENTE02_SIN_VALIDACION_VISUAL.docx`

Tamaño: 112302 bytes. SHA256:
`4213141eeef8740a6acb4be0ed4214dab7eadca6022243d19258eec5d8e07851`

## Contenido modificado

Se actualizan portada, control de edición, corte vigente, autoridad entre cortes, identificación de perfiles, registro de versiones y encabezado/pie. Se añade el capítulo 28 y su entrada en el índice estático.

El capítulo nuevo describe las funciones ejecutables, comandos, asistencia y límites de EO02_MAIN T169383 y EO02_SENSORIAL_R10_T0 T40353. Incluye capacidad conjunta frente a serialización, transferencias positivas y perjudiciales, las tres reservas, readquisición frente a retención, comprobación real de archivos y continuidad entre procesos. No atribuye a MAIN las ocho entradas de R10, ni declara dos políticas contextuales retenidas, P2/R2 o nuevas primitivas NSM65.

## Preservación e integridad

La edición 1.10 se conserva sin cambios, SHA256 `c9b962d1efa14145b6c7d93d3695892475dc4ca0ba52c66731c86b07de33abf5`.

La comprobación final verificó CRC, ausencia de miembros duplicados, XML legible, 15 de 19 miembros idénticos, geometría de sección y campos conservados, capítulos históricos 26 y 27 íntegros y apéndices iguales. Sólo cambiaron `docProps/core.xml`, `word/document.xml`, `word/header1.xml` y `word/footer1.xml`.

Los campos PAGE y NUMPAGES se preservan y `w:updateFields=true` permanece. No se recalcularon sus resultados mediante Word. El índice estático no contiene números de página que se hayan inventado.

## Límite de comprobación visual

Se ejecutó una sola vez el renderizador canónico con Python del bundle autorizado y PATH restringido a ese bundle. Falló al resolver LibreOffice:

`FileNotFoundError: LibreOffice soffice.exe was not found on PATH`

No se generó PDF ni páginas PNG y no se hizo inspección visual. La estructura comprobada no sustituye esa inspección. El nombre del Word conserva explícitamente SIN_VALIDACION_VISUAL. No se usó LibreOffice desktop ni se instaló otra herramienta.

Comprobantes locales:
- `EDICION_MANUAL_1_11_ENTE02.json`
- `verificacion_final/VERIFICACION_MANUAL_ENTE02.json`
- `RESULTADOS_MANUAL_ENTE02_FINAL.json`
- `MARCADOR_EDITORIAL_ENTE02.json`

La distribución de colaboración incorporará estos mismos bytes mediante su actualizador; no se crea otra edición Word en paralelo. Esta tarea editorial no ejecutó ticks ni modificó vidas o snapshots.
