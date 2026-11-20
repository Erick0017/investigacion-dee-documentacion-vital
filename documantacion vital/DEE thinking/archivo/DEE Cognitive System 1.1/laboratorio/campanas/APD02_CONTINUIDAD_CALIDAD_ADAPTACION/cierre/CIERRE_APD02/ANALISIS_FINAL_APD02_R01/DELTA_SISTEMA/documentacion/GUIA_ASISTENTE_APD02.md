# Uso de APD02 en Cognitive 1.1

Universe v27 y thinking 4.5.0 siguen congelados. APD02 es una ampliación de la capa Cognitive, no otro motor.

## Para qué sirve

La vida APD02_MAIN conserva una continuidad física procedente de ASISTENTE_MAIN T361114 y su servicio emparejado. Permite usar formas numéricas aprendidas, comparación actual, consulta de un contexto indicado por el operador, acumulación secuencial renovada y elección nativa entre un cálculo nativo y una calculadora externa local. El resultado terminal es un JSON real, comprobado después de ejecutarse. La categoría de consecuencia no entrega a DEE el número ni la ruta correctos.

Hay dos formas adicionales: compara y recuerda. Su asociación física se enseña y puede revisarse. Las funciones disponibles, el codec, los recursos y el calendario están preparados. No son español libre, aritmética inventada, producción lingüística ni dominio de NSM65.

El cambio de ruta por consecuencia es local: no predice cambios ocultos del mundo ni garantiza elegir bien siempre. El control de calidad y el proveedor externo son instrumentos explícitos. Sólo se ejecuta la ruta físicamente emitida; no hay solver de respaldo silencioso.

## Abrir una copia personal completa

Desde cognitive sistem, Windows x64:

```text
INICIAR.bat preparar
INICIAR.bat investigacion APD02_MI_COPIA_01
INICIAR.bat asistente2 APD02_MI_COPIA_01 estado
```

La entrada investigacion importa el mundo, diario SQLite, outbox, archivos y progreso del alias ASISTENTE_CALIDAD. No crea un T0 ni arranca automáticamente un propietario. No reemplaza una vida personal anterior. Para otro corte, use otra identidad explícita; no fuerce el rebobinado de una copia existente.

La instalación necesita Windows x64. El paquete incluye el intérprete y el motor oficial para esta plataforma. No copie un PYD distinto ni use otro Python incompatible.

## Un propietario y peticiones con IDs nuevos

En una primera terminal:

```text
INICIAR.bat asistente2 APD02_MI_COPIA_01 iniciar --pausado --intervalo .1 --max-segundos 900
```

En otra terminal del mismo directorio:

```text
INICIAR.bat asistente2 APD02_MI_COPIA_01 reanudar --id mi_resume_01
INICIAR.bat asistente2 APD02_MI_COPIA_01 usar --texto suma --operandos 18 7 --id mi_suma_01
INICIAR.bat asistente2 APD02_MI_COPIA_01 lenguaje --texto recuerda --valor 21 --contexto beta --id mi_recuerda_01
INICIAR.bat asistente2 APD02_MI_COPIA_01 acumular --valor 2 --demora-periodos 1 --id mi_delta_01
INICIAR.bat asistente2 APD02_MI_COPIA_01 guardar --id mi_save_01
INICIAR.bat asistente2 APD02_MI_COPIA_01 detener --id mi_stop_01
```

Los números son datos de la solicitud, no respuestas predeterminadas. La suma o diferencia admiten dos enteros 0..32 en su dominio probado. La acumulación admite incrementos 0..32 y demoras adicionales 0..8 períodos compatibles; no reinicia el cursor heredado. Su renovación material es asistencia P0 y no iniciativa autónoma de mantenimiento.

estado muestra el estado operativo y la observación pasiva publicada por el propietario; no inserta una consulta material para demostrar que todo sigue accesible. Las consultas funcionales sí alteran el mundo y quedan en su historia.

Cada petición nueva requiere un ID nuevo. Para consultar una petición que ya existe use resultado, no vuelva a insertarla con otro ID. Si hay efecto incierto, preserve el estado y concilie el archivo/recibo: nunca repita automáticamente el trabajo para obtener un resultado favorable.

## Enseñanza explícita y composición asistida

Estos ejemplos y los del objetivo son ventanas alternativas de uso. Requieren un propietario iniciado y reanudado; si ya ejecutó detener en el ejemplo anterior, vuelva a iniciar esa misma vida y reanudarla, sin importar otra copia ni recrearla.

```text
INICIAR.bat asistente2 APD02_MI_COPIA_01 ensenar --texto compara --senal -1 --revision --id mi_docencia_01
INICIAR.bat asistente2 APD02_MI_COPIA_01 lenguaje --texto compara --valor 9 --contexto gamma --id mi_uso_revision_01
INICIAR.bat asistente2 APD02_MI_COPIA_01 componer --formas agrega resta --datos 4 8 3 --id mi_compuesta_01
```

La primera operación es docencia deliberada: no la cuente como retención sin reenseñanza. El signo adquirido cambia cuál de dos funciones preparadas utiliza esa forma. El operador sigue indicando el contexto de consulta.

componer recibe un orden explícito de dos o tres formas y datos crudos 0..16. Encadena los resultados reales; ese orden lo puso el operador y no prueba planificación de DEE.

## Objetivo con dato consultable

```text
INICIAR.bat asistente2 APD02_MI_COPIA_01 meta-iniciar --texto suma --operandos 16 5 --segundo-oculto --id mi_meta_01 --retorno real
INICIAR.bat asistente2 APD02_MI_COPIA_01 meta-paso --oportunidades 1 --id mi_oportunidad_01 --retorno real
INICIAR.bat asistente2 APD02_MI_COPIA_01 guardar --id mi_meta_save_01
INICIAR.bat asistente2 APD02_MI_COPIA_01 meta-paso --oportunidades 3 --id mi_oportunidades_02 --retorno real
```

El entorno conserva hechos y progreso, no un plan oculto. QUERY revela el segundo operando real; ACT sin ese dato observado falla. La selección física puede cambiar por consecuencias. La interfaz actual no demuestra que el ente perciba prospectivamente la ausencia del dato: también puede consultar de forma redundante cuando ya está visible.

Las oportunidades son ofrecidas por el operador. El decodificador de acciones y el límite de cuatro oportunidades son preparados. Una salida material 0 no significa silencio. Un objetivo agotado o fallido permanece así; no se reemplaza retrospectivamente por una ejecución favorable.

## Guardar y continuar

guardar conserva el estado completo por el protocolo del servicio. detener cierra al propietario pero no cierra el epoch ni borra la cola. iniciar vuelve a cargar esa misma vida. La secuencia exportar/detener siguiente requiere ese propietario todavía iniciado. Una copia a otra identidad requiere exportar/importar el par completo; un snapshot aislado no duplica SQLite, outbox, archivos ni progreso ambiental.

```text
INICIAR.bat asistente2 APD02_MI_COPIA_01 exportar --id mi_export_01
INICIAR.bat asistente2 APD02_MI_COPIA_01 detener --id mi_stop_02
```

No ejecute dos propietarios para el mismo mundo. El límite de proceso y el único escritor son infraestructura, no facultades cognitivas. La seguridad de rutas, el ejecutor acotado y FENCE tampoco constituyen aislamiento universal del sistema operativo.

## Alcance y referencias

El contrato contratos/APD02_CONTINUIDAD_CALIDAD.json y VIDA.json identifican el corte y el último uso acreditado. La tabla por vida distingue memoria histórica, revisión deliberada, acceso actual y resultados auxiliares. El activo global protegido no se cambia por abrir esta alternativa.

Las pruebas de una extracción distinta son pruebas en la misma computadora, salvo evidencia explícita de otro equipo. El ZIP de análisis no contiene todos los snapshots ni sustituye el paquete operativo completo. Ninguno se publica automáticamente.
