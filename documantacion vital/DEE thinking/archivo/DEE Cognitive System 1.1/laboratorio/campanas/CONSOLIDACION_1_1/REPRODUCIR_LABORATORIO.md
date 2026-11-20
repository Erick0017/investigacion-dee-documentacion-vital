# Reproducir el laboratorio1.1

Extraiga SISTEMA y AUDITORIA_ESENCIAL en la misma carpeta. Comparten la raíz `DEE_COGNITIVE_SYSTEM_1_1/`. Sus manifiestos tienen nombres distintos: MANIFEST.json y MANIFEST_AUDITORIA.json. Los miembros comunes deben tener exactamente el mismo hash; no acepte sobrescrituras diferentes. La verificación externa registra esa compatibilidad.

El sistema ordinario sigue sin leer laboratorio/ ni evidencia/. Sólo las operaciones explícitas de investigación utilizan esas carpetas. Use el intérprete aislado instalado desde el WHL incluido; no los scripts de inventario/recuperación forense, que documentan el trabajo sobre las fuentes originales.

Recálculo sin motor ni evolución:

```powershell
python -I -B -X utf8 laboratorio/campanas/CONSOLIDACION_1_1/herramientas/recalcular.py --root . --out CALCULOS_NUEVOS.json
```

Control causal seleccionado, exclusivamente en copias diagnósticas:

```powershell
python -I -B -X utf8 laboratorio/campanas/CONSOLIDACION_1_1/controlar_puente.py --out NUEVA_PRUEBA_CAUSAL
```

Este control utiliza los snapshots completos T2042/T2115 del experimento LIFE_R1_MAIN incluidos en evidencia/, conserva los sham y las intervenciones, y no devuelve soluciones a la vida activa.

Microscopio de expansión:

```powershell
python -I -B -X utf8 laboratorio/campanas/CONSOLIDACION_1_1/microscopio_expansion.py --out NUEVO_MICRO
```

Reconstruye desde el snapshot completo T1912 incluido, conserva RAW/clocks exactos y compara los estados primarios. Es reproducción técnica de un diagnóstico, no nueva réplica independiente.

Para un diagnóstico que necesite una vida auxiliar no admitida en el paquete operativo:

```powershell
python -I -B -X utf8 laboratorio/campanas/CONSOLIDACION_1_1/herramientas/preparar_auxiliares.py --sistema sistema --vidas R65_SHAM_11_R2
python -I -B -X utf8 laboratorio/campanas/CONSOLIDACION_1_1/microscopio_revision.py --out NUEVO_MICRO_REVISION
```

La recuperación auxiliar copia estados completos y registros exactos con hashes; no activa perfiles, no sobreescribe vidas diferentes y no atribuye aprendizaje nuevo. La vida R65_REVISION_11 ya está incluida en SISTEMA. Los otros auxiliares disponibles se enumeran en laboratorio/candidatos/ESTADOS_AUXILIARES/INDICE.json. No restaure todos como si fueran el repertorio deE1.

Los planes congelados y sus hashes identifican la preparación. Cada nueva ejecución necesita una salida e identidad nuevas: un error por directorio o vida existente no autoriza borrar o reiniciar los resultados anteriores. Las trayectorias que creen automáticamente identificadores fijos deben ejecutarse en otra extracción de laboratorio o con una nueva revisión explícita del plan, nunca sobre la vida preferente.
