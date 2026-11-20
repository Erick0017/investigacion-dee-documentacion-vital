# Observador causal retrospectivo — uso privado

Es una herramienta del **AUDITOR**, no una habilidad aprendida por el ente. Lee archivos guardados; no restaura mundos ni avanza ticks. El motor y las vidas no se modifican.

Desde `sistema/`, usando el intérprete existente:

```powershell
python gestionar.py inspeccionar-snapshot 'RUTA_COMPLETA_AL_SNAPSHOT'
python gestionar.py inspeccionar-snapshot 'SNAPSHOT_A' --comparar 'SNAPSHOT_B'
```

También puede ejecutarse el módulo independiente, sólo con biblioteca estándar:

```powershell
python -I -B capacidades/observador_causal_retrospectivo_01.py 'SNAPSHOT_A' --comparar 'SNAPSHOT_B'
```

Admite el formato guardado v2 conocido, directo o gzip. Un formato desconocido, una extracción RAW incompleta o un checksum incorrecto no crea un universo alternativo. La comparación presenta diferencias físicas y operativas separadamente. No descarta metadatos desconocidos para fabricar una igualdad.

Observe especialmente RAW/clocks completos, entradas pendientes, interfaces y progreso del propietario. Dos campos iguales no bastan para declarar idénticos dos futuros. Dos archivos distintos por un diario tampoco demuestran una memoria accesible al participante.

El comando del gestor permite leer únicamente los archivos explícitos proporcionados para esta operación de auditoría. No abre de forma general el acceso a `evidencia/` desde experiencias o guiones de vida normales. Se comprobó el rechazo de esa lectura indirecta.

No se traduce una diferencia física como conocimiento ni una ausencia como NO. No se reconstruye linaje a partir de igual carga. La interpretación funcional requiere las experiencias y controles originales.

E1_SOCIAL_11 sigue en T3154; MAIN AA01 sigue en T47146. Las ramas listas AA01 siguen en T45857, con sus nueve entradas pendientes. Para utilizarlas físicamente después de esta auditoría, siga la guía AA01 y bifurque explícitamente desde el snapshot completo. Este observador no consume ni sustituye esas operaciones.

Contrato: `contratos/OBSERVADOR_CAUSAL_RETROSPECTIVO_01.json`. Evidencia: `evidencia/campanas/AUDITORIA_RETROSPECTIVA_01/`. El ZIP de análisis no es un respaldo operativo completo.
