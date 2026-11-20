# Análisis privado de Integración Situada E1 01

Empiece por `INFORME_RESULTADOS.md`. Las tablas contienen recuentos separados, no una puntuación de inteligencia. Los primarios incluyen éxitos, fallos, controles y revisiones instrumentales.

Para recalcular sin motor ni nuevos ticks, desde una extracción de este ZIP:

```powershell
python CODIGO_Y_RECALCULO/recalcular.py --out CALCULOS_REPETIDOS.json --compare CALCULOS.json
python CODIGO_Y_RECALCULO/resumir_ciencia.py
```

El segundo comando escribe un resumen derivado en la carpeta de evidencia extraída; no cambia un participante. `reproducir_entorno.py` es **otra operación**: necesita la dependencia externa declarada y reproduce comandos archivados en el modelo, sin crear E1. Una reproducción nativa necesita además el motor oficial, el sistema/propietario compatible y el snapshot inicial completo correspondiente. No se finge que el ZIP de análisis sea una instalación.

`TESTIGOS_ESTADO` contiene una selección de mundos completos para examinar campos, colas y encuentros. No todos los estados históricos ni todos los archivos necesarios para continuar cualquier rama. El índice localiza lo omitido por nombre, tamaño y SHA-256.

El código de ejecución exacto de las revisiones conservadas está incluido; las referencias sin coincidencia de bytes se declaran, no se reemplazan por la versión última. Las extracciones de agregados no son bytes originales: conservan valores, localizadores y hashes; los primarios decisivos sí mantienen sus bytes.

El Word fue actualizado, pero no pudo renderizarse por falta de LibreOffice. Todo el material es privado. No hay WHL, motor, ZIP histórico ni una promesa de65significados, control competente o autonomía general.
