# CPC6 — revisión externa observacional

Este paquete permite revisar conducta y contabilidad experimental sin entregar el motor ni el estado que permitiría reconstruir los aparatos. Procede del CPC6 canónico sellado y conserva sus129 registros científicos:94 preparaciones,29 ramas diagnósticas y6 continuaciones. Las incidencias técnicas están separadas y no se suman como aprendizajes independientes.

Empiece por `DESCRIPCION_FUNCIONAL.md`, `ALCANCE_Y_CONCLUSIONES.md` y `CALCULOS.json`. Las tablas de `datos/` permiten revisar cada ensayo, incluidas condiciones de control y lecturas vacías. `CONTROLES_Y_RESERVAS.json` identifica contrastes reservados sin escogerlos por éxito. Los IDs públicos no revelan los nombres técnicos originales.

`FORMULAS_Y_DICCIONARIO.md` define los datos y denominadores. Para verificar los cálculos, basta Python estándar, sin instalar la biblioteca experimental:

```text
python RECALCULAR.py --verificar
```

Esta herramienta sólo cuenta y compara los datos exportados. No simula DEE, no obtiene nuevas respuestas y no accede al expediente privado. Los hashes están en `MANIFEST.json` y `HASHES.sha256`; el hash del ZIP se comunica fuera del contenedor.

No se han exportado código del motor, binarios, recetas, estados guardados, campos físicos internos, geometría, reglas microscópicas ni trazas de reconstrucción. Las observaciones temporales son de salidas del contrato funcional, no recorridos espaciales. Las agendas técnicas de suministro están agregadas para no entregar una receta. Los niveles de entrada se representan con códigos opacos que conservan igualdad/diferencia, no su codificación física.

La proyección no prueba por sí sola la física del mecanismo, la selectividad de las intervenciones ni la ausencia de mediación externa. Tampoco verifica independientemente que la proyección desde los primarios sea fiel: sus compromisos criptográficos permiten contrastarla si un auditor autorizado dispone del expediente privado. No constituye reproducción independiente del motor ni demostración de65 significados.
