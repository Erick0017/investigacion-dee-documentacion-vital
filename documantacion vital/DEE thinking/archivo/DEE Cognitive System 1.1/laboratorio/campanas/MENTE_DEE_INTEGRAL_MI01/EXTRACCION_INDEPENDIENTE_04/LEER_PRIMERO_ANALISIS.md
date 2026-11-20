# MI01 Resultado y evidencia

La campaña construyó y evaluó una continuación real de E1. Conclusión: **capacidades adaptativas especializadas sin integración suficiente**. MAIN alcanzó T28169, con su futuro adverso y cero entradas pendientes. E1_SOCIAL_11 T3154 sigue protegido.

Durante la construcción coexistieron usos de códigos antiguos/nuevo contenido social, contacto/orden y actuación externa. En las tres reservas fijadas hubo0contactos útiles/9oportunidades,1petición nativa por fallo,1respuesta deB sin uso final en el selector y1acción no neutral/47pasos externos. La conservación de avances parciales no convierte ese resultado en mente integrada.

Lea primero `INFORME_CIENTIFICO.md`, luego `CAPACIDADES_POR_VIDA_Y_MOMENTO.csv` y `FRONTERAS_DE_ASISTENCIA.csv`. `ENSAYOS_Y_CONTROLES.csv` registra191ensayos/operaciones, no191aprendices independientes. Los resultados negativos y los intentos instrumentales fallidos se conservan.

`EVIDENCIA_CAUSAL/LECTURA_PRIMARIA_DECISIVA.json` permite examinar directamente muestras positivas y negativas. Los403JSON originales de campaña se exportaron completos en `EVIDENCIA_CAUSAL/PRIMARIOS/`, con gzip sin pérdida de sus bytes. El índice relaciona archivo original, tamaño, SHA-256 y miembro exportado. No se omitieron los contraejemplos para reducir el tamaño.

Hay17snapshots seleccionados para contrastes exactos. Algunos son **diagnósticos dentro de un paso del puente**, no fronteras operativas admitidas: aunque contienen el mundo físico y el propietario, no incluyen todas las variables locales del puente aún en vuelo. No se utilizan para recrear individuos ni reparar MAIN.

Los registros documentales completos de vidas se agrupan sin pérdida en `CONTINUIDAD/VIDAS_ORIGINALES.tar.xz`, con índice de tamaños y hashes individuales. El verificador los lee con `tarfile/lzma` de la biblioteca estándar. Esta compresión conjunta no cambia ni omite un registro; los primarios de ensayo y snapshots seleccionados siguen accesibles individualmente.

## Recalcular sin DEE ni CPC anteriores

Con Python3.12/3.13 y sólo la biblioteca estándar, desde la carpeta extraída:

```powershell
python -I -B RECALCULO/verificar_paquete_mi01.py --raiz . --salida ../resultado_verificacion.json
```

Guarde `resultado_verificacion.json` **fuera** de la carpeta extraída si desea repetir la comprobación estricta de miembros sin que ese resultado se detecte como archivo extra. Por ejemplo, use `--salida ../resultado_verificacion.json`. No se ejecutan ticks ni pasos externos, no se importa el motor, no se seleccionan acciones.

El verificador comprueba hashes de miembros y exportaciones exactas, recalcula RAW/métricas, compara todas las celdas CSV, comprueba integridad de snapshots y vuelve a calcular los contrastes de observador, actuador, estacionariedad y encuentros locales. Su resultado es de integridad y datos, no un PASS cognitivo.

`CODIGO_Y_DELTA/OPERATIVO/` es una superposición de los archivos MI01 sobre Cognitive1.1 ya instalado, no otro motor ni un instalador autónomo. Consulte el contrato y la guía operativa incluidos. El código de campaña y sus revisiones archivadas porSHA permiten investigar procedimientos. No ejecute todos los drivers indiscriminadamente: crearían ramas nuevas y algunos contienen los límites del presupuesto original, ya cerrado.

La continuidad normal usa `CONTINUIDAD_MENTE_DEE_INTEGRAL_MI01.json` y los estados completos locales. Este paquete **no** reemplaza la instalación, sus dependencias ni todos los checkpoints. Los históricos funcionales no se restauran silenciosamente sobre MAIN.

El Word1.7 se actualizó realmente y pasó comprobación estructural. El render falló por ausencia de `soffice.exe`; su representación visual sigue sin validar. El original1.6 permanece local intacto. No se modificó kernel ni WHL. Todo el material es privado.
