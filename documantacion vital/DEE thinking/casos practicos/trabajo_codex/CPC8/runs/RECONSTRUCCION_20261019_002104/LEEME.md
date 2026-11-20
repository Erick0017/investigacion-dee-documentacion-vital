# Ejecución y reproducción de CPC8

Instrumento oficial: DEE thinking4.5.0, CPython3.13x64 para Windows, kernelv27. No se recompiló ni modificó. Las preparaciones nuevas son investigación externa sobre su Runtime.

## Inicio sencillo

Abra PowerShell en la carpeta extraída `CPC8`:

```powershell
powershell -File .\iniciar_cpc8.ps1
powershell -File .\iniciar_cpc8.ps1 -Interactivo
```

El lanzador no cambia el Python global. Requiere que `py -3.13` encuentre un intérprete compatible. Si usa otro ejecutable3.13x64, cree un entorno con él e instale el WHL local:

```powershell
py -3.13 -m venv .entorno_cpc8
.\.entorno_cpc8\Scripts\python.exe -I -m pip install --no-index --no-deps .\runtime\dee_thinking-4.5.0-cp313-cp313-win_amd64.whl
.\.entorno_cpc8\Scripts\python.exe -I -B ejecutar.py identidad
.\.entorno_cpc8\Scripts\python.exe -I -B ejecutar.py demo --eventos configuraciones\demo_magnitud_social.jsonl --salida SESION_NUEVA
```

Use un destino nuevo: no se sobrescriben estados guardados. Los ejemplos instalados ejecutan física, no respuestas precalculadas. N67 requiere `32*67^3 = 9,624,416` bytes básicos, más scratch, interfaces, metadatos, estados y anfitrión. Las medidas reales están en `revision/RECURSOS_Y_PRESUPUESTO.json`.

## Gramática realmente implementada

Perfiles: `magnitud_social` (principal), `contacto_social`, `integrada`, `basica`. Son preparaciones diferentes, no etapas intercambiables de una misma vida.

En el modo interactivo:

```text
crear MI_E1 magnitud_social
puertos
ver
explicar
```

`crear` prepara posibilidades físicas, sin ejecutar la enseñanza del currículo. Para reproducir la vida completa, use los acontecimientos del JSONL publicado. El comando JSON `curriculo` programa experiencias declaradas; no representa una iniciativa del ente. También hay operaciones estructuradas para acontecimientos de orden, cantidades actuales, asociación posterior de formas, consultas, contexto, entradas físicas explícitas, avance, guardado y carga. Los nombres de operación reconocen el contrato, no resuelven el significado.

Ejemplos de operaciones humanas, en las ventanas admisibles de su preparación:

```json
{"op":"ver"}
{"op":"consultar","relacion":"compuesta","t":613,"carga":13}
{"op":"avanzar","t":616}
{"op":"guardar","archivo":"mi_estado.deetsnap.gz"}
{"op":"cargar","archivo":"mi_estado.deetsnap.gz"}
```

La consulta613 sólo es pertinente después de la adquisición publicada; no convierte un cuerpo nuevo en uno entrenado. La interfaz envía el mismo estímulo a bancos candidatos fijos, no consulta una tabla de respuestas. `entrada` permite intervenciones humanas explícitas: no es un mecanismo de seguridad que impida al operador alterar un experimento.

Las líneas se identifican como ENTE (lectura/emisión física), ENTORNO (experiencia), INSTRUMENTO (entrada, admisión, medida) o AUDITOR (explicación). No hay conversación libre ni LLM dentro del participante. Una lectura ocupada, indeterminada o fuera de dominio se conserva como tal.

## Contrastes y reservas

Eventos principales y controles: `configuraciones/demo_magnitud_social*.jsonl`, `demo_contacto_social*.jsonl`, `demo_integrada.jsonl`, `demo_e1.jsonl`. La historia11 cambia la referencia del emisor; la reserva17 cambia cantidades; el control omite la experiencia fuente. Son vidas nuevas, no modificaciones de MAIN. Guardar y restaurar, en cambio, continúa exactamente el mismo individuo con sus entradas pendientes.

Los ensayos completos se repiten con los ejecutores de `src/` y las configuraciones congeladas; véanse los comandos de cada informe específico. Los mundos auxiliares, forks y reproducciones técnicas no cuentan como aprendizaje de MAIN.

## Revisar sin ejecutar mundos

`revision/OBSERVACIONES.jsonl` reúne observaciones por ensayo y localizadores. Los primarios mantienen entradas, recibos, respuestas, campos exactos y fronteras causales. `CALCULOS.json` explica denominadores y fórmulas; `INDICE_EVIDENCIA.json` enlaza los archivos, hashes y roles de ejecución.

Los scripts de auditoría no son módulos cognitivos: `tools/indexar_campana.py`, `tools/auditar_cantidad_completa.py`, `tools/auditar_qfm.py`, `src/relaciones/analyze_contact_cardinality.py`, `revision/recalcular_auditoria_fronteras.py`. Consulte `--help` cuando exista; algunos análisis escriben informes, por lo que para preservar los bytes de la entrega se recomienda trabajar en otra extracción.

## Comprobación limpia

`reproduccion/verificar_candidato.py --python RUTA_PYTHON_INSTALADO --out NUEVA_RUTA_EXTERNA --artifact RUTA_ZIP_EXACTO` verifica el contenedor, identidad instalada, cuatro referencias CPC7, vidas y controles nuevos, guardado/carga en otro proceso y equivalencia física/operativa. Todas sus escrituras quedan fuera de la extracción. El informe externo identifica el ZIP exacto; no debe confundirse con un desarrollo anterior o con una comprobación de CRC únicamente.

El ZIP es autocontenido para este recorrido central y las referencias seleccionadas. Las campañas históricas extensas son dependencias documentales referenciadas por miembro y hash, no bytes íntegros incluidos. No se promete reproducir todo CPC1–7 desde este solo ZIP.
