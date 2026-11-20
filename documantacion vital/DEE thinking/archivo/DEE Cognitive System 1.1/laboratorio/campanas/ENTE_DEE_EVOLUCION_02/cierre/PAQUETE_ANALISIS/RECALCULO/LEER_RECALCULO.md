# Recálculo EO02 sin motor

Requiere Python estándar3.10 o posterior. No importa DEE, no avanza ticks,
no inicia workers ni consulta respuestas en el sistema operativo.

Ejemplo con los directorios exportados:

```text
python recalcular_eo02.py --primarios EVIDENCIA_RAIZ --codigos CODIGO_EJECUTADO --artefactos ARCHIVOS_SERVICIOS --indice-artefactos INDICE_ARTEFACTOS.json --salida RECALCULADO
```

`--artefactos` y `--indice-artefactos` son opcionales, pero deben ir juntos.
Sin ellos se regeneran los bytes previstos de los recibos; no se afirma haber
contrastado archivos de output exportados. `--codigos` por defecto es
`EVIDENCIA_RAIZ/codigo_ejecutado`.

Resultados:

- `RECALCULO_EO02.json`: lector reconstruido desde los frames, consecuencias,
  inputs, código, continuidad, resultados de servicios y referencias independientes.
- `RESUMEN_CASOS.csv`: numeradores y denominadores por primario.
- `PRIMER_USO_Y_RETENCION.csv`: primera actuación antes de su feedback y estados.
- `REFERENCIAS_POR_CASO.csv`: las referencias fijas, alternante, ocho aleatorias y
  adaptativas. Sus futuros ambientales pertenecen a cada política, no a MAIN.

Las políticas/semillas están congeladas en `referencias_eo02.py` y
`SELLO_REFERENCIAS.json`. El adaptador de modelo del recálculo representa la ley
efectiva de los workers y las sumas ambientales. La política recibe observaciones
crudas; no recibe crédito oculto, respuesta correcta o pendiente de MAIN.

El recálculo contextual separado está en `contexto/recalcular_contexto.py`:

```text
python recalcular_contexto.py --primarios PRIMARIOS_CONTEXTO --salida RECALCULO_CONTEXTO.json
```

`exportar_artefactos.py` es una herramienta local de cierre: copia únicamente
outputs ya producidos, verificando recibos y hashes. No es una instrucción para
que un colaborador acceda al equipo original. El paquete de análisis exporta
esos archivos pequeños y su índice para comprobarlos sin esa dependencia.

Nada de esto sustituye una reproducción física con el WHL oficial ni una prueba
del paquete operativo. El recálculo sólo prueba lo que contienen sus primarios.
