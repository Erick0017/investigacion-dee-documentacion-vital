# Sellado final de análisis — preparado, todavía no ejecutado

El sellador `sellar_y_verificar_analisis_apd03.py` exige GO explícito de Root mediante `--sellar-root-go`. Prepararlo o analizar su sintaxis no crea un ZIP. No ejecuta DEE, proveedores, políticas ni otra prueba Full.

Requisitos de entrada:

- Nuevo stage R02 ensamblado después del cierre del actualizador y de la prueba Full exacta.
- `VALIDACION_FULL/VERIFICACION_FULL_APD03_R02.json` con la identidad Full aprobada, CRC completo, hashes gestionados iguales antes/después, `zip_still_exact=true`, ejecución real exit0 y `native_proof.issues=[]`. El R01 negativo anterior a Native se conserva como tal; no se renombra ni sustituye.
- Recálculos relativos y referencias esperadas ya incluidos. El control de lectura usa el instrumento N0 archivado; no abre originales a partir de localizadores históricos.
- Nombre canónico, candidato temporal, reporte y extracción todavía inexistentes. No hay borrados ni sobrescrituras automáticas.

Invocación pendiente, sólo después del GO:

```text
python -I -B sellar_y_verificar_analisis_apd03.py
  --stage RUTA_ABSOLUTA_AL_STAGE_R02
  --zip RUTA_ROOT/entregas/DEE_APD03_AUTONOMIA_DESARROLLO_DEMOSTRACION_ANALISIS.zip
  --workspace RUTA_ABSOLUTA_TESTS
  --report RUTA_ROOT/entregas/VERIFICACION_FINAL_EXTERNA_APD03_ANALISIS_R02.json
  --full-sha256 HASH_FULL_APROBADO_POR_ROOT
  --sellar-root-go
```

El programa añade únicamente `MANIFIESTO_FINAL_ANALISIS.json` en la raíz del stage nuevo. Sus miembros conservan tamaños y SHA-256; el manifiesto excluye su propio hash y no contiene el hash de su ZIP. Las ocho exportaciones científicas cerradas se conservan byte a byte.

Crea un candidato Deflate9 con prefijo `DEE_APD03_ANALISIS/`. Rechaza rutas inseguras, duplicados incluso por mayúsculas/minúsculas, enlaces, bases SQLite, motor, otros ZIP y snapshots densos. No publica el nombre canónico si supera 16,000,000 bytes o falla una comprobación.

Extrae el ZIP exacto a `tests/_apd03_analisis_final_r02/`. Verifica CRC y todos los tamaños/hashes contra el stage; ejecuta las CLIs archivadas desde la extracción, exige igualdad de bytes con las referencias, comprueba la frontera de lecturas y vuelve a verificar que nada cambió. Sólo entonces cambia el nombre del ZIP candidato al canónico. El SHA-256 del ZIP se escribe exclusivamente en el informe externo.

Los fallos conservan candidato, extracción parcial y comprobante externo; no se reintenta ni se declara éxito. Si una corrección afecta al stage ya manifestado, se prepara otra revisión sin borrar la anterior. La prueba es recálculo archivado del análisis, no nueva adquisición, reproducción nativa ni validación visual del Word.
