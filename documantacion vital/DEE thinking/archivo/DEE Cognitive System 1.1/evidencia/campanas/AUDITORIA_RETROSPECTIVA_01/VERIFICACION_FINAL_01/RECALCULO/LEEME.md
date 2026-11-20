# Recálculo independiente, sin motor

Desde la carpeta extraída, con Python3.10 o posterior (verificado con3.13.11):

```powershell
python -I -B RECALCULO/recalcular.py --paquete . --salida mis_calculos.json
```

Sólo usa la biblioteca estándar. No instala DEE, no restaura vidas, no avanza ticks y no abre rutas históricas: las rutas absolutas guardadas son referencias de procedencia. Puede comprobar el resultado contra `EVIDENCIA_CAUSAL/CALCULOS.json`. No use `-O`: los assert forman parte de las verificaciones.

La comprobación de salida byte por byte se realizó en Windows/CPython3.13. En otro sistema puede cambiar la representación textual de una ruta relativa; no cambian por ello los bytes originales, hashes de campos ni métricas físicas. `recalculo_aislado.py` permite prohibir expresamente las rutas históricas y la importación del motor durante esa comprobación.

Verifica bytes originales incluidos, checksums de snapshots, campos RAW/clocks completos, lecturas y decodificadores específicos, diferencias globales de controles y los recuentos CPC9. Releer un registro no es repetir el experimento ni una nueva adquisición.

Para ver un primario concreto sin aprender el formato del archivo de objetos:

```powershell
python -I -B RECALCULO/ver_primario.py --paquete . --id AA/CAUSAL_DESTINO_42/remove_incoming --salida contraste42.json --descomprimir
python -I -B RECALCULO/ver_primario.py --paquete . --id S13/wall11 --salida wall11.deetsnap.gz
```

Se comprueba SHA-256 antes de extraer. La salida nueva no sobrescribe un archivo existente. `--descomprimir` conserva exactamente los bytes descomprimidos, sin normalizar JSON ni convertir enteros a floats. No ejecute como recálculo los protocolos científicos históricos contenidos en los archivos de objetos: ejecutarían física y requieren el sistema original. Se incluyen para examinar sus flujos de información, no para repetir campañas.

`leer_estado.py` es idéntico al observador incorporado en el sistema. Puede inspeccionar/comparar archivos extraídos sin motor. Expone diferencias de metadatos en vez de ignorarlas. El atlas y las tablas son del AUDITOR, no memoria externa del participante.

Las dos tablas CSV son planas UTF-8 con BOM y referencias a los objetos originales. `preparar_tablas.py` vuelve a calcular sus valores a partir del paquete y del resultado; `tablas_ret01.mjs` documenta la autoría mediante artifact-tool. Esa dependencia sólo se necesita para repetir esa autoría, no para comprobar los resultados físicos. Los textos largos se resumen únicamente en la celda: el primario íntegro permanece exportado. Las129 filas de comparación no representan129 entes independientes; incluyen cortes del mismo individuo y controles.

`extraer_retrospectiva.py`, `anexar_rutas_y_codigo.py` y `explorar_snapshots.py` documentan la extracción desde los originales locales. Volver a extraer requiere las rutas y estados indicados en el índice; eso no es requisito del recálculo transportable.

## Correcciones del auditor conservadas localmente

R1 distinguió posteriormente instrucciones `clock=UNCHANGED` de observaciones; R2 separó el receptor legacy del receptor inmediato dentro de una misma vida; R4 trató indebidamente la proyección candidata como si siempre fuese un progenitor. El recálculo final compara fuentes entrantes reales y clasifica603 filas tempranas como proyección sin ese progenitor. No se alteraron datos ni se reinterpretó un ensayo físico fallido como éxito. Los códigos y cálculos anteriores permanecen en el laboratorio local; no se duplican todos aquí.

El informe no depende de un resultado global PASS. Igualdad física, huella histórica, lectura útil, contenido aprendido y autonomía siguen siendo cuestiones distintas.
