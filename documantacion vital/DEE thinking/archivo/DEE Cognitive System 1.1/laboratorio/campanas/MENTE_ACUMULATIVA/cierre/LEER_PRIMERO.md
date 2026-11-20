# MENTE_ACUMULATIVA — análisis de una ejecución finita

Consulte primero [INFORME_RESULTADOS.md](INFORME_RESULTADOS.md), [CAPACIDADES_ANTES_DESPUES.json](CAPACIDADES_ANTES_DESPUES.json) y [DECISIONES_INCORPORACIONES.md](DECISIONES_INCORPORACIONES.md). El informe distingue las funciones de la línea principal de las preparaciones nuevas, las bifurcaciones y los instrumentos del investigador. Una consulta no equivale a un individuo independiente y una función disponible en otro perfil no se suma a los conocimientos de la vida seleccionada.

`EVIDENCIA_CAUSAL/` conserva los primarios nuevos incluidos, positivos y negativos, con los códigos y protocolos correspondientes. `INDICE_FUENTES_Y_OMISIONES.json` identifica sus originales mediante tamaño y SHA-256, así como los estados completos que permanecen localmente. El paquete no es un respaldo operativo íntegro ni contiene el motor o todos los snapshots.

Para repetir únicamente los cálculos archivados, desde la extracción ejecute:

```bat
python -I -B -X utf8 RECALCULO\verificar_analisis_final.py
```

Este recálculo usa la biblioteca estándar, compara bytes con las referencias incluidas y no añade ticks, reproduce DEE ni ejecuta trabajadores. Opcionalmente puede añadir `--prohibir-raiz RUTA` varias veces para bloquear explícitamente instalaciones originales. La comprobación final archivada utiliza ese bloqueo para ambas raíces reales.

La ejecución nativa requiere la distribución completa `cognitive_sistem_colaborador.zip`, sus dependencias declaradas y los snapshots completos seleccionados. La verificación de distribución corresponde a otra ruta de la misma computadora, no a un segundo equipo. `DELTA_OPERATIVO/` registra fuentes incorporadas; no debe aplicarse ciegamente sobre otra versión ni sustituye un estado aprendido.

El Manual Maestro incluido es una edición del documento vigente, no otra autoridad metodológica. Su comprobación estructural y el alcance de la validación visual se indican en los recibos editoriales; no se presupone que disponer de un DOCX equivalga a haberlo renderizado.
