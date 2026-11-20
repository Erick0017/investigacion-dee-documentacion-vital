# Guarda documental excesiva al cerrar R2

Las128ramas físicas de `relevancia_b05_r2.py` terminaron y quedaron guardadas. `RESUMEN.json` se escribió antes de la excepción final. El código ejecutado se conserva sin alteración.

La guarda final comparaba también los bytes de `MU_MAIN/VIDA.json`, un puntero **mutable**. Otro propietario autorizado continuó legítimamente MU_MAIN desde su propio estado mientras esta prueba utilizó exclusivamente el checkpoint inmutable T16634 especificado. Por eso `parent_record_unchanged` dio false y el proceso terminó con AssertionError, después de terminar los128ensayos.

Las dos comprobaciones pertinentes al origen físico y al predeterminado dieron true: `parent_snapshot_unchanged` y `active_unchanged`. Todos los forks de R2 utilizaron `MU_MAIN.T16634.ba61eac94a01.deetsnap.gz`, SHA-256 `b6c02df2e804b167b85f9e8fd849e091227b81ccfd7a49e442f67156944c71ad`, no el puntero actual de MU_MAIN.

No es un fallo físico de DEE ni autoriza certificar que MU_MAIN no evolucionó. Tampoco es razón para repetir los128ensayos. El recálculo revisa las observaciones, entradas emparejadas y lectores desde sus primarios; la continuación posterior de MU_MAIN mantiene su propia genealogía y no se atribuye a estas copias.
