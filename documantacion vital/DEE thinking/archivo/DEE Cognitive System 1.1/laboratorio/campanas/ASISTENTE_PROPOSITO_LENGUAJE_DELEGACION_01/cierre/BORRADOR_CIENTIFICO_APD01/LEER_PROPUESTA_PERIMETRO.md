# Corrección propuesta de descripción, no aplicada

La revisión 0ticks encontró que `app/access_guard.py` permite leer dentro de `sistema/estado`, incluidos registros operativos VIDA/HISTORIA y resultados. `Store.load` los usa para identidad y consistencia. Los módulos APD revisados no los consultan para resolver signo, ruta o resultado. Una ruta permitida no demuestra una lectura efectiva y una lectura técnica de continuidad no equivale a memoria externa decisional.

La marca histórica `no_lab_evidence_or_history_reads_allowed: true` mezcla la restricción real de fuentes externas no declaradas con una garantía universal que no implementa. El patch propone deprecar esa afirmación combinada, dejarla falsa explícitamente y añadir dos afirmaciones precisas: bloqueo de LAB/evidencia externos no declarados y ausencia de bloqueo universal de los diarios operativos. Mantiene el aviso de que el hook no es un sandbox del sistema operativo.

No cambia permisos del hook, geometría, lectores, rutas, RAW, clocks, kernel ni estados. No ha sido aplicado ni ensayado. No debe aplicarse mientras corra el servicio congelado. Después del cierre requiere actualizar los consumidores que exigen la antigua marca verdadera, especialmente piloto/reserva y sus comprobantes. Los primarios históricos deben conservar la marca original y corregir su interpretación, nunca reescribirla retrospectivamente.

La comprobación proporcional futura debe verificar únicamente que el metadata nuevo es preciso y que la misma política de archivos/procesos permanece, sin repetir ciencia ni avanzar una vida para una corrección documental. La representación del resultado y sus hashes técnicos cambiará legítimamente si se adoptan nuevos campos; no se debe reclamar igualdad de bytes con los resultados antiguos.
