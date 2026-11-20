# Fronteras de información del perfil magnitud_social

La revisión estática de `app/experimento.py → MagnitudeCTSSession → CTS/IUE/MODE/cantidad/transferencia` no encontró una ruta operativa que consulte targets, semillas, informes, catálogo NSM o respuestas previas para decidir una respuesta nueva. Tampoco se encontró un callback que lea la salida de un participante, calcule la solución y la escriba en otro. Es un hallazgo acotado al código y hashes examinados, no una prueba universal de ausencia ni una certificación de seguridad.

El expediente exacto está en `AUDITORIA_FRONTERAS_INFORMACION.json`: hashes, símbolos y líneas, importaciones, operaciones de archivos,12 fronteras de decisión, cuatro agendas publicadas y exclusiones.

## Qué informa a cada parte

El generador o usuario presenta acontecimientos A/B, rutas actuales, magnitudes, direcciones de referencia/objetos y contexto. Elegir el puerto correspondiente a una propiedad actual es el codificador del sensor declarado; no calcula la respuesta de una comparación futura. Las condiciones paired/unpaired/omitted y on/offpath son intervenciones experimentales explícitas.

En la transferencia de magnitud, la fuente recibe una exposición propia: cue5 y valor material actual. Dos formatters0 tienen puertos y tiempos fijos, independientes del valor y de las observaciones. El portador nativo llega al receptor, donde actúa como referencia para tres objetos actuales. El currículo publicado no introduce directamente una referencia en los puertos `B.quantity.reference.*`. La igualdad entre la magnitud enseñada a esta fuente y otra referencia de E1 es una elección experimental explícita, no una copia automática de la memoria primaria.

Las oportunidades de pregunta, retorno, utilización, asociación y consulta se programan en el currículo. Los productos de Runtime determinan físicamente qué encuentran. Las observaciones se destinan a captura, presentación y guardado, no a escoger desde el host la siguiente respuesta correcta.

## Contribuciones preparadas que permanecen explícitas

- Comparadores nativos, direcciones de señal, geometría, clocks iniciales de guías, ventanas y presupuesto material son diseño.
- Los bancos candidatos se recorren todos con estímulos iguales; no los elige Python después de leer la respuesta correcta. No equivalen a una selección de interlocutor aprendida.
- Las guardas y contraflujos son regulación preparada fija; no atención o política de utilidad adquirida.
- La normalización/deduplicación de solicitudes MODE consulta sólo sitio/dirección/state/semantic/tick/payload declarados, no RAW ni la clase correcta.
- Los bucles ordenados de captura avanzan la misma Runtime por fronteras fijadas. Capturar no aporta un rollout-oráculo al participante.
- CONTACT/FREE y LIKE/DIFFERENT son traducciones fijas de predicados de lectura; no son conversación libre ni significado humano completo adquirido.

## Archivos, continuidad y excepciones

`OBSERVACIONES.jsonl` es salida append-only de la aplicación: no se relee como memoria. La vista mezcla campos físicos actuales con capturas pasivas cuyo tick coincide con el actual; una captura restaurada sigue siendo una medición registrada, no una emisión nueva. La cobertura de una consulta puede consultar su recibo/solicitud para distinguir admisión, sonda y respuesta, pero el contenido traducido procede del registro físico, no de la enseñanza.

`cargar` restaura el snapshot explícito: RAW, clocks, cola, recibos y metadatos operativos. Los metadatos seleccionan una clase de interfaz compatible; no ejecutan `create` ni repiten `curriculum`. Las envolturas auxiliares se adjuntan al mismo mundo. El adaptador instalado limita tamaño y estructura, comprueba gzip/CRC y preserva bytes; esas comprobaciones no autentican la intención de un autor adversarial y la aplicación no exige por sí sola un SHA esperado en cada carga.

`iniciativa_accion/return_use.py` contiene un `main()` de laboratorio que sí lee configuraciones y escribe resultados. La aplicación importa su constructor geométrico, no llama aquel `main()`. Los runners, índices y controles de laboratorio que leen resultados/targets quedan fuera de la cadena operativa auditada. No se afirma que todo archivo del repositorio carezca de evaluador.

El comando manual `entrada` permite intervenciones físicas expresas. Por ello, el usuario puede deliberadamente dar información adicional; esta gramática no es una barrera de seguridad que garantice ceguera en cualquier sesión posible. El alcance científico corresponde a las agendas y controles publicados, con su procedencia.

Recalcular hashes y localizadores sin ejecutar mundos:

```powershell
python -I -B revision/recalcular_auditoria_fronteras.py
```

La auditoría no modifica los fuentes operativos, datos primarios, snapshots ni el producto4.5. No aporta nuevas réplicas científicas.
