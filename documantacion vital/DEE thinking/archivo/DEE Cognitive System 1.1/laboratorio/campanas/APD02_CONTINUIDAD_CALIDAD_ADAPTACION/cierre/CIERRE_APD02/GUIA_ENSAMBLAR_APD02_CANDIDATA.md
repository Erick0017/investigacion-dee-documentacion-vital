# Ensamblaje APD02: uso previsto, todavía no autorizado como cierre

Los tres helpers nuevos se derivan de los instrumentos APD01, cuyos originales no cambian. El algoritmo conserva exactamente los gzip, fuentes y primarios: deduplica archivos completos por SHA256, no normaliza su contenido ni transforma registros científicos. `INDICE_OBJETOS_Y_ALIASES.json` permite materializar todos los nombres originales sin depender de las carpetas de investigación de Erik.

`CONFIG_PREPARACION_APD02_R03.json` fija 14 stages cerrados y 15 casos actuales, e identifica componentes futuros. Incluye el contexto sensorial fallido, su ROI pasiva N0 y el objetivo pendiente/reapertura. El caso de lanzador es una prueba N0 de transporte con mocks, no una ejecución Full. El adverso físico MAIN R03 es un namespace propio. Las revisiones N0 sustituidas se conservan en fuentes/índices locales o en los stages preferidos; no se cuentan como historias físicas adicionales.

Preparación (no entregar como final):

```text
python -I -B ensamblar_analisis_apd02_cas.py --config CONFIG_PREPARACION_APD02_R03.json --stage NUEVA_PREPARACION_NO_FINAL
python -I -B NUEVA_PREPARACION_NO_FINAL/REPETIR_TODO.py --salida OTRA_CARPETA_NUEVA --permitir-preparacion
```

No se han repetido aquí los quince recálculos reales ya acreditados. Sólo se validaron sus manifiestos, dependencias relativas, CLI y hashes. `PRUEBA_TECNICA_N0_R02` verifica con fixtures propios la deduplicación, restauración, dos esquemas de manifiesto, nombres/outputs omitidos por subplanes antiguos y rechazo de rutas/archivos peligrosos. No es una campaña ni resultado DEE. El primer fixture falló por el límite Windows del cwd de CreateProcess; se conservan su prueba y las preimágenes. El child ahora arranca en el directorio de Python y cambia al mismo namespace desde dentro; los scripts/argumentos científicos permanecen iguales.

Para tres subplanes originales sin nombre y sin `--output`, sólo el plan global deriva el nombre del script y añade el output cuando el AST declara exactamente una opción reconocida. No se modifica el subplan ni su referencia. El runner bloquea imports de los módulos de motor/sistema/numpy en el proceso de recálculo y ejecuta con Python aislado; esto no se presenta como un sandbox universal del sistema operativo.

Antes de cualquier ensamblaje final, Root debe crear otra configuración, añadir únicamente stages realmente cerrados y documentos definitivos con SHA fijado; actualizar el número de casos; retirar `future_components_are_not_completed`; poner `pending_components:[]`, `status:CLOSED_APPROVED_FOR_ANALYSIS` y autorización explícita. El Word, tablas e identidad de la vida final no se inventan ni se toman de la preparación. El delta operativo se captura después de congelar sus fuentes reales; no se copia una base SQLite viva.

Sólo después de ese GO, el sellador puede invocarse con cinco rutas nuevas y el número real de casos:

```text
python -I -B sellar_probar_zip_analisis_apd02.py --stage CARPETA_FINAL --zip ANALISIS.zip --extraction EXTRACCION_NUEVA --results RESULTADOS_NUEVOS --proof COMPROBANTE_EXTERNO.json --expected-cases NUMERO_REAL --autorizado-por-raiz
```

El sellador no admite sobreescritura, verifica todos los bytes/CRC del ZIP exacto, extrae en otra ubicación y exige todos los recálculos byte a byte sin motor. El comprobante del SHA del ZIP queda fuera, para evitar autorreferencia. Si supera16,000,000B conserva el intento y detiene el cierre: no recorta evidencia ni escoge sólo éxitos. `ZIP_generated:false` en el stage describe el evento anterior al sellado, no un estado posterior del ZIP.
