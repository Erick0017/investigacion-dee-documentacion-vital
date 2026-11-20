# Tamaños y compactación1.1

Medición real por categorías (bytes, no RAM): sistema 621,076,218, laboratorio 16,473,823, evidencia 5,258,281,405. El sistema de trabajo incluye una caché heredada materializada que NO se entrega. El detalle de extensiones está en RECURSOS_Y_TAMANOS.json. Las carpetas históricas se midieron sólo mediante stat, sin afirmar lectura de todos sus archivos.

Los cuatro ZIP fuente efectivamente abiertos suman 170,995,993 bytes comprimidos y 3,044,769,490 bytes de miembros externos expandidos. No es una cifra deduplicada de todo DEE ni la expansión completa de archivos anidados.

SISTEMA incluye un único WHL oficial, la dependenciaNumPy opcional con avisos, el almacén por hashes, constructores y snapshots completos de las nueve vidas admitidas. Se excluyen venvs, toolchain, caché regenerable y vidas diagnósticas no admitidas. No hay cadenas de deltas externas. El estado completo actual se restaura por sí mismo.

AUDITORIA conserva todos los nuevos primarios, planes, controles, fallos, snapshots diagnósticos y testigos microscópicos. También conserva los JSON primarios de las34familias heredadas. No duplica WHL/PYD/motor. Excluye los grandes snapshots densos generados de esas reproducciones y copias de código idénticas al almacén, que permanecen intactos en evidencia/. Sus tamaños y hashes se listan en EXCLUSIONES_DEL_PAQUETE.json.

No se afirma que cada JSON de salida sea byte-idéntico tras una reproducción: rutas, recursos y tiempos del anfitrión cambian. Se comparan por separado bytes de snapshots regenerados, transiciones físicas y resultados. El comprobante de regeneración distingue cada modalidad. La reproducción técnica no añade réplicas científicas.

La comprobación final comparó1.082estados:984contenedores idénticos y98con metadatos distintos. En los98coinciden RAW/clocks y el Runtime serializado sin metadatos en copias diagnósticas; ambos contenedores completos se preservan mediante gzip sin pérdida verificada. No se descarta su estado organizacional porque una lectura escalar coincida. El índice VERSIONES_RUNNERS_1_1.json distingue también los cortes de código exactos recuperados de un corte anterior de runner no localizado; no se presenta la adaptación actual como sus bytes originales.

Pérdida de cobertura en el ZIP compacto: no se puede abrir cualquier snapshot denso histórico generado desdeAUDITORIA solamente. Se puede revisar su observación primaria, localizar el hash original y reconstruir conSISTEMA. Los testigos locales no son una genealogía microscópica exhaustiva de todos los portadores. Las16filas documentales pendientes no se transforman en capacidades operativas.

Las partes de transporte se calculan por el tamaño comprimido final. Cada segmento tiene menos de16,000,000bytes y se verifica su unión completa. Separar carpetas o comprimir no reduce la ocupación nativa del mundo ni representa ahorro energético medido.
