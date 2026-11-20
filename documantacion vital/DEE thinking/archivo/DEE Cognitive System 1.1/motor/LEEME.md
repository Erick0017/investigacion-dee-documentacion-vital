# Intérpretes recuperados, no otro motor DEE

`python313` procede byte por byte de la distribución `cognitive sistem` archivada. `INICIAR.bat` lo utiliza para ejecutar el gestor original, cuyo almacén sigue en `sistema/estado`. La autoridad del motor es el WHL oficial único en `sistema/runtime`; `python313/site-packages` es su instalación local de ejecución, no otra versión ni una recompilación.

`python312` y `VC_redist.x64.exe` también se conservaron como complementos portables existentes; no se instalaron ni se ejecutó el instalador. El contrato histórico de hábitat externo todavía utiliza su Python3.12 ya verificado en la caché de Codex. Ese destino externo no se movió; no se cambió de intérprete silenciosamente ni se repitieron simulaciones externas.

Las dependencias numéricas y del hábitat están en `sistema/runtime/optional_numeric` y `sistema/runtime/habitat_externo_deps`. No se copiaron nuevamente a `motor`. `DEPENDENCIAS_DISTRIBUCION_ORIGEN.json` es una copia identificada del inventario de la distribución anterior: sus referencias a aquella distribución son procedencia, no un nuevo contrato operativo.
