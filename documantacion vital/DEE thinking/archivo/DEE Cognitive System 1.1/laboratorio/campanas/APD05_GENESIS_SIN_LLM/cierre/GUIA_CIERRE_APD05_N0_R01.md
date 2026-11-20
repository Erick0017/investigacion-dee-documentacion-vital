# Cierre APD05 preparado sin resultados anticipados

Estos instrumentos reutilizan el ensamblado, la cerca de dependencias y el sello exacto de APD04. Prepararlos no ejecuta Native ni acredita la aplicación, una adquisición, el visor o el Full. No importan módulos del motor. Todas las pruebas físicas y GUI requieren sus propios primarios y alcance.

## Selección única al cierre

Root cerrará los escritores pertinentes y aprobará `RESULTADOS_FINAL.json` conforme a `RESULTADOS_FINAL.schema.json`. No se rellenan éxitos supuestos. Las tablas conservan todos los intentos, incluidos errores del instrumento y futuros inciertos. Cada afirmación enlaza IDs de fuentes cerradas con hash exacto. `null` no significa cero. Las ramas no se suman a MAIN.

La selección debe distinguir software probado, capacidades del individuo, instrumentos externos y escenas grabables. Incluir el informe integrado, tabla por vida y momento, cobertura de botones/comandos y protocolos, historia de adquisición/revisión, resultados de la reserva, contraste visor activado/desactivado, grabación/replay, costos con alcance, revisión ejecutada de aplicación/actor, Word vigente, continuidad y evidencia negativa decisiva. Si algún frente no se ejecuta, conservar su dependencia concreta y no inventar primarios.

Las fuentes voluminosas pueden viajar como componentes con manifiesto o CAS por SHA idéntico. El índice conserva rutas originales y objetos; cada byte seleccionado se verifica. Una extracción esencial no contiene estados completos ni reemplaza el Full. Sólo se excluyen duplicados exactos o detalle explícitamente localizado; nunca se eliminan contraejemplos para favorecer la interpretación.

## Comandos de ensamblado y sello

Desde esta carpeta, con el Python compatible existente:

```text
python -I -B validar_y_normalizar_seleccion_apd05_n0_r01.py --selection RESULTADOS_FINAL.json --schema RESULTADOS_FINAL.schema.json --out VALIDACION_NUEVA
python -I -B preparar_entrega_apd05_r01.py check-selection --results VALIDACION_NUEVA/RESULTADOS_FINAL.json
python -I -B preparar_entrega_apd05_r01.py assemble --root RAIZ_COGNITIVE --results VALIDACION_NUEVA/RESULTADOS_FINAL.json --out CANDIDATO_NUEVO --root-go APD05_ANALYSIS_CLOSED_APPROVED
python -I -B CANDIDATO_NUEVO/RECALCULO/recalcular_todo.py --root CANDIDATO_NUEVO --out RECALCULO_NUEVO_FUERA_DEL_CANDIDATO
python -I -B preparar_entrega_apd05_r01.py seal --candidate CANDIDATO_NUEVO --delivery RAIZ_COGNITIVE/entregas --proof PRUEBA_NUEVA_FUERA_DEL_CANDIDATO --root-go APD05_SEAL_EXACT_ANALYSIS_APPROVED
```

Los dos argumentos GO corresponden a una decisión real de Root, no son autorización automática de este documento. El sello rechaza sobrescribir un ZIP publicado, calcula CRC y hashes de todos los miembros, extrae el ZIP exacto y repite los recálculos archivados. El máximo es 16,000,000 bytes. El hash del ZIP se registra fuera del contenedor.

## Full y aplicación

El Full se exporta por el actualizador existente sólo después de fijar el corte seleccionado y el Word. Debe contener `ABRIR_GENESIS.bat`, aplicación y dependencias locales, código del sistema, motor una vez y el par completo elegido. No modifica `trabajo_personal` ni la vida protegida. Sus pruebas físicas y de GUI desde una extracción nueva son independientes del recálculo N0 del análisis. Otra carpeta no equivale a otra computadora ni a aislamiento del sistema operativo.

Antes de abrir una copia personal desde el Full, fijar vida, padre, snapshot/par, casos, IDs de petición, criterio y límites. Comprobar una operación nueva, enseñanza o revisión real y retención con el mismo estado; guardar/cerrar/reabrir el mismo pendiente sin otro PUT. La interfaz y sus recursos deben cargarse de la extracción, no de la fuente original. Registros/replay son material archivado, nunca una ejecución nueva en vivo.

## Manual

El instrumento `../manual/actualizar_manual_apd05_r01.py` inspecciona sin editar con `--inspect`. La única edición del mismo DCS11-MM-001 exige prosa final aprobada, identidad exacta 1.18→1.19, GO y exactamente una marca de autoría de Root inmediatamente antes de ejecutar `--edit`. Conserva historia y apéndices, ajusta portada/índice/encabezado/pie y archiva la edición anterior sin borrarla. El render sólo usa dependencias empaquetadas; XML válido no acredita revisión visual. No usar LibreOffice de escritorio si falta el empaquetado.
