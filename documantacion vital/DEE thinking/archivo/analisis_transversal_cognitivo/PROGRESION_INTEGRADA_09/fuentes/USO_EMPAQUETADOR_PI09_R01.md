# Empaquetado PI09: selección explícita y verificación aislada

Este código prepara un expediente de análisis. No abre DEE, no crea propietarios, no modifica documentos y no selecciona una vida. Todavía no se ha creado ningún ZIP PI09 mediante esta herramienta.

`codigo/empaquetar_PI09_R01.py` reutiliza el procedimiento ya empleado en PI08: ZIP Deflate, extracción nueva, comprobación de bytes y recálculo con una barrera que rechaza accesos al proyecto original, imports de DEE/aplicación, procesos y red. El helper documental se conserva literalmente desde PI08; su nombre local PI09 no atribuye otra investigación ni una nueva lectura del corpus.

## 1. Decidir qué viaja

Los comandos se ejecutan desde la raíz `tests`, usando el Python oficial ya instalado:

```powershell
$pi09Code = 'documantacion vital/DEE thinking/archivo/analisis_transversal_cognitivo/PROGRESION_INTEGRADA_09/codigo'
$pi09Python = 'documantacion vital/DEE thinking/DEE Cognitive 2.0/motor/python313/python.exe'
& $pi09Python -I -B -X utf8 "$pi09Code/seleccionar_fuentes_PI09_R01.py" --candidatos --salida "$pi09Code/CANDIDATOS_PAQUETE_PI09_R01.json"
```

Esto lista sólo archivos superiores de `codigo`, `control` y `fuentes`. Son candidatos, no una aprobación para incluirlos todos. Una lista JSON opcional `--codigo-aprobado <archivo>` puede aportar las rutas exactas del código activo que Root haya aprobado: objetos con `source`, `file` (destino relativo del ZIP) y `sha256`. No se recorre el equipo ni el árbol de mundos.

Root completa una copia de `SELECCION_PAQUETE_PI09_PLANTILLA.json`. Debe seleccionar el informe único, la entrada legible, mapas/continuidad, fuentes pertinentes, cambios efectivos de código y controles decisivos, incluidos negativos y fallos técnicos. Debe añadir localizadores reales y hashes de los estados grandes, motor/WHL/PYD, manuales oficiales omitidos y telemetría profunda. Esos originales permanecen locales.

Los dos documentos se toman literalmente de sus originales actuales: Manual Cognitive completo con nombre compatible `Edicion_1_21` y Compendio completo, cuyo tamaño ya es compacto. No se sustituye ninguno por un resumen ni se incluyen sus respaldos.

Las carpetas portables C1 y AR están declaradas con sus índices actuales. Se expande exclusivamente cada carpeta finita habilitada, sin seguir enlaces. Si D se ejecuta, Root habilita su carpeta exportada real, congela su índice y añade el trabajo de recálculo D. El código D preparado no acredita ejecución. Un intento D fallido debe conservarse como tal en el paquete y en su índice.

## 2. Congelar el plan de bytes reales

Después de cerrar los archivos y publicar los documentos reales:

```powershell
& $pi09Python -I -B -X utf8 "$pi09Code/seleccionar_fuentes_PI09_R01.py" --config "$pi09Code/SELECCION_PAQUETE_PI09_FINAL.json" --salida "$pi09Code/PLAN_ENTREGA_PI09_FINAL.json"
& $pi09Python -I -B -X utf8 "$pi09Code/empaquetar_PI09_R01.py" --plan "$pi09Code/PLAN_ENTREGA_PI09_FINAL.json"
```

La expansión guarda rutas, bytes y SHA256 actuales y deja el estado `DRAFT_EXPANDED_ACTUAL_BYTES_NOT_CLOSED`. El segundo comando sólo estima tamaño comprimido y comprueba las fuentes vinculadas; no crea ZIP ni staging.

Root revisa los miembros y completa el plan:

- `status`: `CLOSED_ACTUAL_FILES_READY_TO_PACKAGE`.
- `edition`: edición realmente publicada, vinculada al testigo de publicación.
- `privacy_review`: `ROOT_APPROVED_LOCAL_ANALYSIS_SELECTION`, tras revisar los archivos elegidos. No es una afirmación automática de ausencia de todo dato privado.
- `visual_QA_status`: `VALIDATED_WITH_REAL_RENDER_WITNESS` o `NOT_VALIDATED_WITH_ACTUAL_LIMITATION`, con el testigo real incluido. CRC/XML no se presentan como revisión visual.
- Cuatro gates reales: `scientific_closure`, `operational_writer_scope`, `literal_document_publication` y `D_execution_status`. Cada gate lleva `evidence` con source/bytes/SHA256, `pointer` RFC6901 y `expected` del tipo exacto. Un resultado negativo puede y debe fijarse como `false` donde corresponda; no se fuerza un PASS científico.

Si `D_executed` es verdadero, se exige un trabajo portable con `id: D`. Si es falso, debe vincularse ese estado al cierre real. Las propiedades propuestas o preparadas no sustituyen el cierre.

El formato de cada trabajo es `id`, `script` relativo al ZIP, `argv`, `result_file`, `result_schema`, `expect` (punteros y valores) y opcional `expected_result_file`. Este último compara el JSON recalculado completo con el resultado documental cerrado incluido. Los argumentos sólo sustituyen `{EXTRACTION}` y `{OUTPUT}`.

Trabajos actuales:

```text
C1: 04_EVIDENCIAS/C1/RECALCULAR_CONSULTA_PI09_R01.py
    --raiz {EXTRACTION}/04_EVIDENCIAS/C1
    --salida {OUTPUT}/C1_RECALCULADO.json
AR: 04_EVIDENCIAS/AR/ARITMETICA_PORTABLE_PI09_R01.py recalcular
    --raiz {EXTRACTION}/04_EVIDENCIAS/AR
    --salida {OUTPUT}/AR_RECALCULADO.json
D, si existe evidencia real exportada:
    04_EVIDENCIAS/D/RECALCULAR_D_PI09_R02.py
    --raiz {EXTRACTION}/04_EVIDENCIAS/D
    --salida {OUTPUT}/D_RECALCULADO.json
```

## 3. Crear y verificar una sola entrega

Sólo Root, una vez cerrado el plan:

```powershell
& $pi09Python -I -B -X utf8 "$pi09Code/empaquetar_PI09_R01.py" --plan "$pi09Code/PLAN_ENTREGA_PI09_FINAL.json" --crear-y-verificar --nombre 'DEE_PROGRESION_INTEGRADA_09_ANALISIS.zip' --comprobante 'VERIFICACION_ZIP_FINAL_PI09_R01.json'
```

No materializa otra copia staging. Escribe directamente un candidato `.writing`, exige como máximo 15.000.000 bytes y lo extrae en una carpeta nueva corta `tests/p9vHHMMSS/x`. Verifica CRC de cada miembro, conjunto exacto, rutas, bytes/SHA256 del manifiesto, JSON/JSONL/CSV/texto UTF-8, AST Python y CRC/XML de los DOCX. Ejecuta los recálculos desde esa extracción con CWD nueva y barrera de accesos. Sólo después renombra el candidato como ZIP final y emite su prueba con bytes, SHA256 y resultados.

No se permiten archivos ZIP anidados, mundos, SQLite, snapshots, WHL/PYD o ejecutables. El manifiesto no contiene su propio hash ni el hash del ZIP; este último vive en el comprobante externo. Una declaración literal de la selección viaja automáticamente dentro del ZIP sin autorreferencia.

Un fallo conserva el candidato y los diagnósticos, sin borrar, reintentar automáticamente, truncar evidencia ni reemplazar una entrega anterior. Si excede el límite, Root revisa la selección explícitamente; los originales grandes no se reducen para que quepan. La reproducción Native local y el recálculo documental del ZIP se reportan por separado.
