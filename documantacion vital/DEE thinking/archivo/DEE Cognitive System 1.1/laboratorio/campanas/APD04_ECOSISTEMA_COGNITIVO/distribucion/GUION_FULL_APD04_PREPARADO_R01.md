# Prueba Full APD04 — guion preparado, no ejecutado

Reutiliza el lanzador y la entrada existentes. No instala otra plataforma, no escribe S y no modifica el Full o el Word mientras el freeze esté activo. La reserva de60 minutos continúa pendiente; preparar este guion no la cumple.

## Antes del sello, sólo tras GO

Root selecciona un corte APD04 completo y detenido después de la reserva, con genealogía y capacidades actuales verificadas, no por ser el de mayor tick. Esta revisión de la prueba requiere que el par seleccionado no tenga peticiones heredadas pendientes; si las tiene, se prepara una revisión que las resuelva por sus mismos IDs, no se las ignora o elimina. El guion sí crea y conserva un nuevo pendiente exacto en su propia copia Full.

Se actualiza **el mismo** `sistema/contratos/ENTRADA_SENCILLA_APD03.json`: `status=CLOSED_SELECTED_FOR_USE`, par completo/hash real en la fuente canónica y `source_alias` del catálogo Full. No se reemplaza ACTIVO. El actualizador debe materializar ese alias y exactamente ese snapshot+servicio; la interfaz no puede caer silenciosamente al padre APD03. Conservar antes los bytes originales del contrato. La corrección del texto antiguo APD03 en `iniciar_local.py --help` es exclusivamente documental y se hace sólo al cerrar el freeze, preservando su revisión anterior.

Los instrumentos preparados aquí se incorporan al Full como `actualizaciones/probar_full_apd04_entrada_r01.py`; no se copian adaptadores de distribución a S. El verificador exterior reutiliza la extracción/CRC/manifiesto/importación incluida del comprobador APD03 y llama únicamente al helper dentro del ZIP extraído. El helper debe ser miembro del ZIP exacto antes de sellarlo; no se lo inyecta después a la extracción para aparentar independencia.

## Qué adquisición autoriza hoy la entrada

`ensenar-ecosistema clasifica -1 --revision --docente paired --retorno omit` se transporta literalmente a `apd04-docencia`: señal explícita, docente de signo declarado y recurso de revisión Native. Está limitado a los dos slots admitidos `clasifica/equilibra`. No asigna desde Python la nueva respuesta: una consulta posterior `palabra-ecosistema clasifica --retorno omit` no contiene el signo correcto y debe formarlo mediante la historia física. No crear otro puerto por resultado ni readmitir el slot para limpiarlo.

La prueba propuesta revisa la asociación `clasifica+` heredada a `clasifica−`. Es aprendizaje nuevo de una asociación en la copia Full, **no** un significado español nuevo ni adquisición espontánea de la operación nombrada. `equilibra−` y las16 formas anteriores/6 consultas MA se usan como testigos de conservación. Si el padre final no conserva la línea base prevista, no se cambia el signo después de mirar: se registra el fallo o se declara otro protocolo prospectivo antes de ejecutar.

Las nuevas mediciones43 y9/3 yel pendiente47 entran por `evento` con el contrato existente `apd04-calibrar`. Son datos físicos explícitos, no respuestas correctas. Los resultados se verifican desde los seis RAW del lector numérico. Este frente prueba uso y continuidad de entradas nuevas; no pretende que presentar43 enseñe por sí mismo una referencia o política.

## Secuencia real prevista en una sola vida personal

1. Extraer el ZIP exacto a una ruta nueva y comprobar todos los miembros. Iniciar mediante `INICIAR.bat usar --help`; importar la extensión incluida y comprobar que procede de ese motor, no de la instalación original.
2. `INICIAR.bat usar --nueva APD04_FULL_PERSONAL_R01 --guion BASELINE_GUION.json`: importa una vez el par elegido, consulta ambas señales yel panel heredado, guarda ySTOP. No T0, no Source S, no cambio del activo original.
3. Nueva sesión del **mismo** individuo con `--vida`: una docencia opuesta declarada, primera consulta, testigos ymediciones nuevas. Guardar ySTOP. No repetir enseñanza para mejorar una respuesta.
4. Abrir el mismo Supervisor existente en otra sesión, propietario en pausa. Insertar una sola vez `apd04_full_exact_pending_r01` con la medición47. Conservar ID+payloadSHA, guardar ySTOP con la petición en cola. El wait0.25s es sólo espera de transporte local, no cambio físico ni edición del contrato.
5. Nuevo proceso: abrir la misma vida, comprobar fingerprint físico yID+payloadSHA, consultar el **mismo ID** sin reinsertarlo, reanudar yesperar su resultado con plazo genérico. Consultar señales ypanel otra vez, guardar ySTOP. Un timeout no crea otra vida ni otro put.

El helper usa el mismo `usar_dee.Supervisor` únicamente para la parte de cola/poll que una lista CLI fija no puede expresar robustamente. Las fases de línea base ydocencia se ejecutan mediante el bat real. Los logs conservan cada petición, rechazo, salida, código de proceso yestado, sin convertir un fallo de proceso en veredicto cognitivo. Todo queda bajo `trabajo_personal` de la extracción; no se borra ni actualiza el trabajo del colaborador.

## Comando exterior, únicamente tras cerrar protocolo y ZIP

```powershell
python -I -B verificar_full_apd04_exacto_r01.py --zip RUTA_ZIP_FULL --zip-sha256 SHA_EXACTO --destino RUTA_CORTA_NUEVA --protocolo PROTOCOLO_FULL_APD04_CERRADO.json --salida VERIFICACION_FULL_APD04_EXTERNA.json --ejecutar-native
```

Root rellena `PROTOCOLO_FULL_APD04_PLANTILLA_R01.json` y sólo entonces cambia su estado a `CLOSED_FOR_EXACT_FULL_APD04_PROOF`. El verificador no reutiliza una extracción previa, no busca otra vida si falla yno permite un alias de respaldo. En ningún momento esta preparación constituye evidencia de ejecución Native, Full correcto, reserva prolongada oretención futura.
