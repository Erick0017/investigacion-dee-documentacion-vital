# Mente unificada y FI01

Este ZIP contiene la evidencia de los bloques A y B de una sola campaña. El
informe distingue lo ejecutado por MU_MAIN de los controles y perfiles
auxiliares. No certifica mente general, NSM65, regulación general ni estabilidad
ilimitada.

Lea primero `INFORME_RESULTADOS.md`, `COBERTURA.json` y
`CAPACIDADES_POR_VIDA.json`. La continuidad identifica el estado completo y sus
dependencias operativas; no se puede continuar una vida con esta extracción de
análisis, porque no incluye motor ni todos sus snapshots.

## Comprobación sin motor

Desde una extracción nueva, con Python3.10 o posterior y sólo su biblioteca estándar
(comprobado aquí con CPython3.13 en Windows):

```
python RECALCULO/REPETIR_TODO.py --salida CARPETA_NUEVA_DE_RESULTADOS
```

Verifica los hashes de todos los miembros y vuelve a calcular las métricas,
lectores y controles indicados en `RECALCULO/PLAN_GLOBAL.json`. Compara los bytes
del resultado con referencias congeladas; cuando una referencia está comprimida
compara su contenido descomprimido. No ejecuta DEE, no enseña y no repite los
trabajadores externos. Recálculo archivado no equivale a reproducción nativa.

En otro sistema operativo, una serialización puede cambiar sólo los finales de
línea. La opción explícita `--allow-newline-differences` permite únicamente ese
caso, conserva ambos hashes y marca `exact_bytes_equal:false`; no reescribe los
originales ni acepta cambios de cifras, campos o resultado del calculador.
La verificación final de esta entrega utiliza el modo estricto, sin esa opción.
Una discrepancia de biblioteca zlib o de cálculo no se oculta como salto de línea.

## Código y procedencia

`CODIGO_MAIN/` conserva los protocolos y supervisores. `DELTA_SISTEMA/` contiene
los componentes operativos afectados, no otra copia del producto oficial.
`CODIGO_EJECUTADO/REVISIONES.json` mapea cada revisión realmente utilizada a sus
bytes exactos, deduplicados por SHA-256. Para materializar una revisión sin
ejecutarla:

```
python RECALCULO/EXTRAER_REVISION.py ID_REVISION CARPETA_NUEVA
```

MECANISMO, ESCALAMIENTO_B y SERVICIO conservan sus primarios, negativos y códigos
congelados. Sus índices detallan los estados profundos que permanecen localmente.
El índice global registra los archivos originales incluidos y las omisiones.
La recompresión sin pérdida no se presenta como identidad de bytes del archivo
original: los hashes se refieren explícitamente al archivo o a su contenido.

Para utilizar el sistema, abra la distribución operativa completa y su guía;
no importe desde este ZIP científico como sustituto de un estado aprendido.
Todo el material es privado.
