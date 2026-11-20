# Compactación y cobertura

Se incluyen sin cambiar sus bytes todos los registros no binarios de ensayo de ESPANOL_FUNCIONAL_01: controles, fracasos, recursos, respuestas y errores técnicos. La compresión ZIP es sin pérdida; no se eliminó un contraejemplo para cumplir el tamaño.

Se excluyen motor, WHL, fuente congelada, ZIP anterior y checkpoints completos; ARCHIVOS_OMITIDOS.json conserva ruta, bytes y SHA-256. Las colas y metadatos necesarios para continuar siguen en los snapshots operativos locales. Los arrays y observaciones del análisis no los reemplazan.

Las fuentes experimentales y componentes actuales están incluidos. COBERTURA_CODIGO.json distingue hashes registrados de revisiones antiguas cuyos bytes exactos no están todos archivados. Por ello no se afirma autosuficiencia para reproducir todas las revisiones históricas ni transportar vidas. El recálculo de las mediciones incluidas sí es independiente del motor.
