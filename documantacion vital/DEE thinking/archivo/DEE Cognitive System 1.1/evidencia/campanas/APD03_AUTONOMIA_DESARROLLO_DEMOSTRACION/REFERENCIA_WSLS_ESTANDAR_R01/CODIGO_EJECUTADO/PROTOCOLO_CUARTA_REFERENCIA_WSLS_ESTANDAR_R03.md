# Cuarta referencia, revisión prospectiva de la regla WSLS

Se conserva íntegro el comparador R03 ya ejecutado, cuyo nombre `wsls` corresponde exactamente a una preferencia lose-shift: después de éxito en una ruta forzada por la interfaz no actualiza su preferencia. No se modifica su evidencia ni su resultado.

Se propone una cuarta trayectoria convencional con WSLS sobre la ruta efectivamente ejecutada. Tras ACT SUCCESS conserva esa ruta; tras ACT FAILURE selecciona la otra. QUERY no selecciona un proveedor aritmético y no actualiza esta preferencia. El retorno omitido no actualiza ninguna ruta.

La única diferencia algorítmica es esta actualización. Se mantienen el programa prospectivo R02 SHA `96b6b1a82bd4a3f3bc0cb6f9650752ed8bf3506b9e0bf37de2ea6dc2c51ca599`, la máscara de magnitudes/contexto, los seis antecedentes léxicos explícitos, el presupuesto de oportunidades, ACT-only en calidad, fallback de interfaces permitidas, callbacks convencionales y verificación de archivos realmente escritos. No se leen resultados ni acciones de MAIN.

Código: `comparadores_apd03_wsls_estandar_r03.py`, copia de la implementación cegada R02 con clase `StandardWSLS`, identidad de esquema/política distinta y restauración explícita de esa preferencia. La lógica de entorno, proyección, ejecución, primarios, métricas y recálculo se mantiene sin cambios. El protocolo se fija antes de esta nueva trayectoria; no se seleccionará retroactivamente la mejor variante para ocultar las otras.

Cuatro fixtures N0, sin MAIN ni Native, verifican éxito y fracaso sobre una ruta forzada, invariancia sensorial, efecto real de archivo, omisión de retorno y restauración de preferencia. Requiere GO de Root después de leer fuente y diff. Sólo se ejecutará esta cuarta política; no se repiten las tres anteriores.

La referencia sigue siendo convencional y preparada, no una adquisición de E1; su coste aritmético no es equivalente a v27. Se conservan todos los resultados, favorables o adversos, de ambas variantes. Energía: NO MEDIDA.
