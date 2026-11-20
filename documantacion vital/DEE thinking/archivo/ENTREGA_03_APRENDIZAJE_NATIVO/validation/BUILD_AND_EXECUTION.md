# Registro técnico

- Baseline: DEE thinking 2.2.0, seis protocolos integrados, kernel DEE v27.
- Compilador: MSVC 19.50.35729, toolset 14.50.35717, x64.
- Build: Release, CMake 4.2.3-msvc3, Ninja.
- Binario: `bin/dee_entrega03_native_learning.exe`.
- Biblioteca baseline `dee_thinking.lib`:
  `8c60cfebb770644d07e91498d3f6fe005164e501c276830c4e544e2eaa431513`.
- SHA-256 del binario ejecutado:
  `17ffa4e611d1b46e908ee0a37854d77a015c44ec844c7dd28f677b59fcd680d5`.
- Panel final: 9 casos Lazy; 171/171 entradas admitidas; 0 rechazos.
- Confirmación DOSE_4: Lazy, DenseSequential y DenseParallel produjeron RAW y
  clock finales exactamente iguales.
- Checkpoint: proceso nuevo, consultas reservadas 4185/4189, RAW y clock
  finales exactos respecto de la referencia.
- Validador independiente de tablas: `VERIFIED`, 12 comprobaciones verdaderas.

## Comprobación desde extracción limpia

El ZIP provisional se extrajo en una ruta nueva fuera del árbol de trabajo y,
usando únicamente el contenido entregado más el toolchain declarado, se
realizaron estas comprobaciones:

- configuración y reconstrucción Release del runner C++: `PASS`;
- baseline DEE thinking 2.2.0/kernel v27: `PASS`;
- panel Lazy representativo de nueve casos: `PASS`;
- `case_summary.csv` reproducido byte a byte, SHA-256
  `26c6a4752f9b1fadd2ae0594d0b9fc76726363effecaf56ff29373484ba1f08f`;
- reanudación en proceso nuevo desde `learned_dose4_t40.deetsnap`: `PASS`,
  RAW y clock exactos frente a la trayectoria no interrumpida;
- validador sobre la extracción limpia: `VERIFIED`, 12/12 comprobaciones.

El intento inicial de invocar `py -3.13` falló porque el lanzador de Windows
no tenía registrado ese intérprete. El mismo validador se ejecutó después con
el CPython 3.13.11 funcional disponible, sin cambiar datos, código científico
ni predicciones.

La ejecución final no modificó la biblioteca 2.2.0 ni sus fuentes. El código de
esta carpeta sólo construye el aparato experimental y enlaza la biblioteca
estática incluida como baseline.
