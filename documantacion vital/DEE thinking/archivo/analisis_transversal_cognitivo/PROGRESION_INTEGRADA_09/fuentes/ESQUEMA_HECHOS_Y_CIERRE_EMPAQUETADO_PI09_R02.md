# Fuente editorial y selección final PI09

Este archivo prepara el cierre. No es un cierre científico, una autorización de adopción ni una prueba de Word o del ZIP. Los únicos documentos de salida son el Manual completo y el Compendio completo. La propuesta de selección sigue abierta mientras falten los resultados finales D, su reproducción, la continuidad y la publicación 1.38.

## Hechos requeridos por el actualizador 1.38

`codigo/actualizar_documentos_PI09_R02.py` acepta un JSON con estos campos:

```text
schema: DEE.PI09.final_document_facts.R02
        (también admite R01 si internal_edition es explícitamente1.38)
internal_edition: 1.38
closed_for_authoring: true, únicamente después de la revisión de Root
selected_life:
  life_id: identidad realmente seleccionada
  N: 67
  T: entero del corte real
cut_utc: fecha ISO8601 real con zona horaria
description: descripción documental del cierre efectivo
evidence:
  - path: ruta absoluta de un comprobante existente bajo PI09
    sha256: SHA256 actual de ese comprobante
front:
  edition_summary: texto de edición vigente
  principal_summary: identidad, corte y genealogía reales
  functional_summary: capacidades y límites actuales
  conservation_summary: paneles y cortes realmente comprobados
  resume_summary: acceso y reanudación exactos, con consumibles
  coverage_summary: lectura nueva frente a cobertura reutilizada
  control_table:
    Documento: valor documental actual
    Corte de liberación registrado: valor actual
    Base principal: valor actual
    Estado de esta edición: valor actual
manual_sections:
  - heading: título de subsección
    paragraphs: lista no vacía de párrafos explicados
    sources: lista opcional de localizadores textuales
compendium_sections:
  - heading: título de subsección
    paragraphs: lista no vacía de párrafos explicados
    sources: lista opcional de localizadores textuales
```

Cada colección de secciones admite entre una y diez subsecciones. El Manual añade el capítulo54; no reescribe los capítulos1–53 ni los apéndices. La nueva portada y el capítulo54 deben explicar la situación actual y distinguirla de los cortes históricos que permanecen intactos. Se pueden conservar campos adicionales de padre, snapshot, recursos y paneles en el JSON; el texto final debe usar valores efectivos, no ejemplos ni pendientes convertidos en positivos.

No deben introducirse fórmulas internas de v27 en el Manual. La explicación causal puede describir las observaciones, los controles y el alcance. El código y las notas científicas locales conservan los detalles técnicos pertinentes.

## Autoría y publicación: solamente Root

Desde `tests`:

```powershell
$pi09Code = 'documantacion vital/DEE thinking/archivo/analisis_transversal_cognitivo/PROGRESION_INTEGRADA_09/codigo'
$pi09Python = 'documantacion vital/DEE thinking/DEE Cognitive 2.0/motor/python313/python.exe'
$pi09Facts = 'documantacion vital/DEE thinking/archivo/analisis_transversal_cognitivo/PROGRESION_INTEGRADA_09/documentos/HECHOS_FINALES_1_38_PI09.json'
& $pi09Python -I -B -X utf8 "$pi09Code/actualizar_documentos_PI09_R02.py" --check-facts --facts $pi09Facts
& $pi09Python -I -B -X utf8 "$pi09Code/actualizar_documentos_PI09_R02.py" --author --facts $pi09Facts --marker-confirmed
```

`--marker-confirmed` reconoce el marcador de edición ya ejecutado por Root para estas mismas dos salidas; no ejecuta ni pide repetir otro marcador. La autoría exige los originales reales1.37 con hashes fijados y destinos nuevos. Conserva respaldo literal1.37 y escribe sólo `documentos/edicion_1_38`. La estructura, los miembros no editados y el XML histórico se comprueban al construir. Esto no equivale a revisión visual.

Después de registrar la revisión visual real o la limitación efectiva de renderizado, Root publica mediante CAS:

```powershell
& $pi09Python -I -B -X utf8 "$pi09Code/actualizar_documentos_PI09_R02.py" --publish --facts $pi09Facts
```

La salida es `documentos/PUBLICACION_EDICION_1_38_PI09.json`. No se actualizan selectores, contratos ni estados Native desde este helper. Root sincroniza las referencias documentales pertinentes por su procedimiento independiente.

## Selección del paquete

`codigo/SELECCION_PAQUETE_PI09_PROPUESTA_R02.json` es una propuesta explícita. Incluye fuentes actuales, los treinta archivos de código aprobados para el hito1 y los paquetes portables C1 y AR. Los mapas son todavía el corte que tengan sus autores; Root debe cerrar y volver a obtener sus hashes. C2 prepara los dos CSV generales, sin duplicar la matriz aritmética.

La propuesta no incluye los paquetes D intermedios para evitar duplicación. Espera el único `control/D_FINAL_PORTABLE_R03` que C2 exportará después de todos los cierres efectivos. El recálculo final D usa `RECALCULAR_D_PI09_R03.py`, con schema `DEE.PI09.D.recalculated_persistent_environment.R03`; el lector R02 antiguo no sustituye a esa revisión documental. Si Root incorpora la comparación fría D6, su comprobante y registro viajan aparte del conjunto de adquisición, con modalidades distinguidas.

Antes de expandir, Root debe:

- Crear y seleccionar la entrada legible y el informe único finales.
- Añadir el cierre real de ciencia y de escritores, la decisión de incorporación o no incorporación D, los usos y la reapertura efectivos.
- Vincular publicación1.38, hechos finales y el testigo visual o la limitación actual.
- Habilitar el paquete D final con su índice SHA real y añadir el trabajo D, copiando también su resultado de recálculo cerrado.
- Añadir el mapa real de omisiones y localizadores de estados grandes, WHL/PYD, manuales Thinking y telemetría profunda.
- Verificar qué cambios de código quedaron realmente desplegados después del hito1. Los archivos experimentales D no se denominan desplegados por aparecer en esta propuesta.

No se declara que el tamaño final vaya a caber antes de medir los miembros efectivos.

## Construir y verificar

Tras esas comprobaciones:

```powershell
& $pi09Python -I -B -X utf8 "$pi09Code/seleccionar_fuentes_PI09_R01.py" --config "$pi09Code/SELECCION_PAQUETE_PI09_FINAL.json" --salida "$pi09Code/PLAN_ENTREGA_PI09_FINAL.json"
& $pi09Python -I -B -X utf8 "$pi09Code/empaquetar_PI09_R01.py" --plan "$pi09Code/PLAN_ENTREGA_PI09_FINAL.json"
```

El segundo comando es un plan de sólo lectura: estima compresión y detecta fuentes cambiadas. No sella ni crea un ZIP. Root revisa los miembros, añade los cuatro gates de tipos exactos y fija `CLOSED_ACTUAL_FILES_READY_TO_PACKAGE`, la revisión de privacidad y el estado visual efectivo. Un gate negativo sigue siendo evidencia válida y no debe cambiarse para forzar una incorporación.

Sólo entonces:

```powershell
& $pi09Python -I -B -X utf8 "$pi09Code/empaquetar_PI09_R01.py" --plan "$pi09Code/PLAN_ENTREGA_PI09_FINAL.json" --crear-y-verificar --nombre 'DEE_PROGRESION_INTEGRADA_09_ANALISIS.zip' --comprobante 'VERIFICACION_ZIP_FINAL_PI09_R01.json'
```

El proceso exige un único Deflate de hasta15.000.000bytes, extracción nueva y corta bajo `tests`, CRC, bytes/hashes, formatos textuales y DOCX estructurales. Ejecuta C1, AR y D desde esa extracción con la barrera que impide leer el proyecto original, importar DEE/aplicación, iniciar procesos o usar red. Native local y recálculo documental son resultados distintos. Ante fallo conserva el candidato y los diagnósticos; no borra, recorta ni sustituye originales grandes.

## Protección final pasiva

`codigo/verificar_proteccion_final_PI09_R01.py` imprime por defecto el plan sin leer ni hashear estados actuales. Root puede ejecutar `--verificar` sólo después del cierre real de escritores, pasando `--cierre`, `--cierre-sha256`, `--cierre-puntero` al booleano verdadero efectivo y `--salida` nueva bajo control. Compara los hashes iniciales de A861426(card y snapshot), WHL, PYD y kernel. El registro inicial no conservó un hash de `python.exe`: el helper recoge el actual y deja la comparación histórica como no disponible. Los cambios autorizados de selección, documentación y catálogo no se confunden con daño de A.
