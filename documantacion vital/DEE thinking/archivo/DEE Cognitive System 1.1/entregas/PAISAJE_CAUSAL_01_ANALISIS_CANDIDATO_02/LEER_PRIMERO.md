# Paisaje Causal 01

Se ejecutó la campaña sobre DEE Cognitive System 1.1 existente, con DEE thinking 4.5.0 y v27 sin cambios. El resultado más útil es que una influencia puede perjudicar un lector y habilitar otro: cortar toda actividad residual no es una solución general.

El panel amplio protegido conservó comparación, espacio y contacto/trayecto libre en su horizonte finito. Otras ramas adquirieron un contexto nuevo con pérdidas. Una rama alternativa reutilizó una influencia transformada mediante un lector material preparado y continuó en procesos separados. No se demostró P2, comprensión lingüística general ni 65 significados.

Lea `INFORME_RESULTADOS.md`, `CAMBIOS_INCORPORADOS.md` y las cuatro imágenes de `ATLAS_CAUSAL/`. `FICHAS_ENTES.json` y `ENSAYOS_Y_CONTROLES.json` separan vidas, preparaciones, controles y fallos. `TABLA_TODOS_LOS_USOS.csv` contiene lecturas y denominadores; no una puntuación de mente.

## Datos que puede comprobar

Se incluyen los 159 archivos primarios de este corte, todos los campos efectivamente registrados y los logs de ejecución. El archivo sólido interno contiene 906 miembros verificados, con 526,903,956 bytes de payload expandido. Se conservan sus bytes científicos; las cabeceras de los gzip originales quedan localmente referenciadas por hash. Eso no equivale a conservar todos los microestados de todos los ticks.

El ZIP externo es pequeño porque esos datos contienen mucha repetición. No necesita expandir los más de 526 MB para leer este resumen, las tablas o los mapas. El recálculo puede procesar el archivo interno por streaming.

```powershell
python CODIGO_Y_RECALCULO/extraer_registros.py --root . --report VERIFICACION_DATOS_REHECHA.json
python CODIGO_Y_RECALCULO/recalcular_analisis.py --root . --out RECALCULO_REHECHO.json
```

Python 3.10 o posterior y su biblioteca estándar bastan para esas operaciones; no ejecutan física ni importan el motor. `--deep` añade la reconstrucción y hash de todos los campos globales registrados y puede tardar varios minutos. Las instrucciones detalladas están en `CODIGO_Y_RECALCULO/REPRODUCCION.md`.

## Lo que no es este paquete

No contiene motor, WHL, ZIP históricos ni la mayoría de snapshots completos. Los dos snapshots nativos incluidos son diagnósticos, sin el progreso Python necesario para continuar E1 como sesión. El sistema local conserva los estados operativos completos identificados en `CONTINUIDAD_PAISAJE_CAUSAL_01.json`.

El predeterminado permanece en E1_SOCIAL_11 T3154. La continuidad alternativa PC01_NORMALIZADO45 T41318 no borra la rama fallida E1_PAISAJE_01 T44300 ni sustituye automáticamente al predeterminado. Una asociación, un código conservado y la interpretación de una situación nueva se evalúan por separado.

El Manual Maestro recibido sigue íntegro. Se incluye el addendum consolidado; su integración editorial al Word permanece pendiente de render validado. Todo este material es privado. No es una autorización para publicar fuentes, geometrías o estados.
