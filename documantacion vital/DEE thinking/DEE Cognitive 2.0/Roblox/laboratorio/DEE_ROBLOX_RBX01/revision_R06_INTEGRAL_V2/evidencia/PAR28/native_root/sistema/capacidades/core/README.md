# Núcleo recuperado dentro de DEE Cognitive System 1.1

Esta copia adapta únicamente la entrada operativa y dependencias del Core histórico. Use el gestor 1.1 que sigue. El antiguo ejecutor autónomo `desde_cero.py` no se distribuye aquí como entrada, porque esperaba la estructura del ZIP Core original. Su procedencia queda preservada en el expediente histórico y el índice por hashes. El WHL está una sola vez en `sistema/runtime/`.

Paquete privado de recuperación sobre DEE thinking 4.5.0 oficial y v27 congelado. Contiene el instrumento, las implementaciones recuperadas, sus configuraciones, fuentes genealógicas y evidencia primaria seleccionada. No contiene ZIP históricos completos ni cambia el producto.

Hay dos alcances distintos:

1. Preservación por identidad de bytes. El índice registra los miembros originales, sus hashes y la implementación recuperada. La matriz distingue lo documentado de lo ejecutado nuevamente.
2. Recuperación operativa comprobada. Únicamente los contratos que superen `PRUEBA_RECUPERACION_DESDE_CERO.json` pueden considerarse sustituidos operativamente por este paquete. Los resultados auxiliares no se suman como conocimientos de un E1.

## Recuperación desde una extracción limpia

Requiere Windows x64 con CPython 3.13 x64 disponible. No requiere los ZIP ni las carpetas CPC anteriores. En una carpeta nueva, extraiga este ZIP y ejecute con ese intérprete:

```text
python -I -B sistema/gestionar.py probar-herencia --familias cpc1,cpc2,sem01,cpc4,cpc5,cpc6,cpc7,mcts,repertoire,rca,count,product,product_extra,ordered,stream,network,architectures,bridge,capacity,longitudinal,policy,native_loop,central,qfm,l15,need,missing,retain_early,retain_word,retain_late,social,initial_cpc8,core06,core07 --salida RECUPERACION_NUEVA --segundos 5400
```

Primero instale con `sistema/instalar_sistema.ps1` en una extracción limpia. El gestor materializa sólo los archivos requeridos y ejecuta los contratos en procesos propios supervisados. Los resultados se escriben en la salida nueva; la caché regenerable se crea en `sistema/estado/cache_heredada/`. No se leen ZIP históricos. El informe externo identifica el ZIP exacto probado.

La persistencia oficial 4.5 necesita un directorio temporal nativo ASCII. El ejecutor genera uno exclusivo bajo el TEMP/TMP accesible del sistema y declara su ruta en cada recibo; las rutas de extracción, resultados y snapshots comprimidos pueden conservar Unicode. Si TEMP/TMP ya contienen caracteres no ASCII, configure primero una ubicación temporal ASCII disponible. No se altera el WHL para evitar esta condición. El primer candidato conservado falló por asignar incorrectamente TEMP a la salida con Ñ: se mantiene su evidencia y sólo se corrige la infraestructura de archivos.

Para recuperar únicamente miembros archivados sin ejecutar nada:

```text
python -I -B sistema/capacidades/core/scripts/materializar.py --out FUENTES_RECUPERADAS --prefix historico/CPC3/genealogia/CP01_C08/
```

Sin `--prefix` se recuperan todos los miembros indexados, con un coste de disco mayor que el tamaño comprimido. Se verifican todos los blobs del almacén incluso cuando sólo se materializa un subconjunto.

## Qué se ejecuta

El panel incluye los casos originales CP01 C01–C08, predicción prospectiva CP02, SEM01, red A/B/C/D con contraflujo, compuesto con respaldos adquiridos, dos formas y lector renovado CPC6, U0 CPC7, la vida MCTS CPC8, K65, regulación causal RCA y adquisición auxiliar B-only. Incluye controles, historias opuestas, realizaciones reservadas históricas, consultas que también enseñan y restauraciones. Estas repeticiones son reproducciones técnicas de contratos conocidos, no nuevas muestras independientes ni nuevas reservas de descubrimiento.

Las regresiones de API se distinguen de los ensayos científicos. La información detallada está en `documentacion/MATRIZ_CAPACIDADES.json` y en los informes de `verificaciones/`.

El panel predeterminado tiene 32 familias ejecutables. Añade los contratos originales de comparación y política CPC3; K65 y adquisición 32+33 CPC5; orden AB/BA, flujo secuencial y redes de roles; arquitecturas, puente y retención causal CPC6; discrepancia y ausencia CPC7; forma móvil y diagnóstico L15; transmisión social CTS con corte, sham y contenido modificado; y cuatro historias del primer CPC8. Una continuación del SOC_I21 regenerado adquiere RIGHT, conserva 63/63 asociaciones en T1051 y consulta posteriormente en T1182. Sus cinco continuaciones/ramas no se cuentan como nuevos individuos independientes. Son aparatos diferenciados; su cobertura conjunta no convierte sus funciones en conocimientos simultáneos de un E1.

Dos familias adicionales, CORE06 y CORE07 de arrays físicos directos, usan NumPy 2.2.6 incluido explícitamente con sus avisos en `sistema/runtime/optional_numeric/`. Sólo esos trabajadores lo cargan y verifican. No se presenta ese contrato de transición como compatibilidad de colas Runtime históricas. El panel completo tiene 34 familias; el informe del ZIP exacto distingue sus resultados individuales.

Las capacidades amplias CORE/Ingenierías/Procesos que sólo conservan documentación y fuentes siguen en estado D. No se afirma que la ejecución de una realización R14 o de un observador pequeño reproduzca todo el dominio de su publicación original. El paquete sustituye operativamente sólo los contratos cuya ejecución limpia figure aprobada, no toda la historia científica.

## Límites que se conservan

- K65 acredita correspondencias físicas de formas, no 65 significados NSM. En el control no emparejado las consultas posteriores producen adquisiciones: 32/65, 65/65 y 65/65. El control de revisión fuera de ruta conserva 63/64 relaciones no revisadas, no 64/64.
- El aparato N131 K65 no se fusiona documentalmente con U0/MCTS N67.
- Las reglas de comparación, oportunidades de consulta y rutas de regulación están preparadas. La regulación RCA tiene dependencia causal de consecuencias físicas, pero no demuestra una política general que aprenda qué estrategia conviene.
- El resultado ONE B-only depende de unidades materiales y umbral calibrados. No prueba cardinalidad general, un vocabulario conjunto ONE/TWO ni pertenencia al E1 de CPC9.
- Los campos RAW/clocks y sus hashes se conservan sin conversión a floats. Las direcciones de memoria del host y los nombres de archivos de intentos no son estado físico DEE.
- Las entradas del inventario que no pasen la recuperación limpia conservan su código/evidencia, pero no reciben una afirmación de autosuficiencia operativa.

El almacén contiene también variantes históricas de código, incluidas herramientas de mantenimiento y comparadores antiguos. Son genealogía inerte. El ejecutor sólo utiliza una lista explícita de familias. No ejecute limpiadores históricos ni interprete su presencia como parte de CPC9.

No se declara conciencia, inteligencia general, dominio lingüístico humano ni superioridad universal.
