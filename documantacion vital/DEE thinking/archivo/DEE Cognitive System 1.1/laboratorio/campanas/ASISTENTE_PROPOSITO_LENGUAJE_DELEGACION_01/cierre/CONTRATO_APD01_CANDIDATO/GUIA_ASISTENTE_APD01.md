# APD01 — guía operativa candidata

**BORRADOR DE CIERRE.** Comandos cotejados con el gestor y esquemas actuales, sin ejecutar ticks. El corte final, snapshot, par de exportación y resultados de la reserva deben completarse por Root antes de publicar. No interpretar este archivo como confirmación de que terminó la reserva.

## Qué ofrece y qué no

APD01 continúa `ASISTENTE_MAIN` en un único mundo N67. Conserva mecanismos heredados y añade asociaciones de señales, aritmética preparada, selección física de procedimiento y uso de herramientas. No crea una mente nueva al iniciar ni convierte la calculadora externa en una habilidad aritmética DEE.

Hay hasta **seis formas APD**: `suma`, `diferencia`, `agrega`, `resta`, `total`, `quita`. Se añaden a seis contextos anteriores (`alfa`…`zeta`): máximo doce asociaciones físicas en esta preparación, no doce facultades ni65 significados. El nombre español transporta una forma; su signo adquirido se obtiene de la respuesta física. No se selecciona una operación porque Python interprete la palabra. Una forma desconocida se rechaza, no se adivina.

La suma nativa preparada recibe dos enteros0..32. La diferencia usa una representación afín diseñada y da−32..32. El conteo agrega dos/tres muestras independientes0/1; no demuestra cardinalidad adquirida. La composición recibe dos/tres formas y un orden fijado por el operador; transporta los resultados intermedios reales. No es un planificador aprendido.

El selector O2 tiene anatomía y calendario P0, pero su referencia y respuesta pueden cambiar por experiencias. Un retorno costoso común no selecciona A/B desde Python. La reversión real N5/E1 no produjo la nueva ruta barata: no hay regulación bidireccional general demostrada. La asignación A/B del protocolo histórico R01 era asistencia del host y no debe rebautizarse P2.

El desplazamiento adquirido de CORE06 se utilizó cinco veces con controles y preservación de asociaciones anteriores. El cursor consumió las cinco oportunidades programadas: esto no acredita borrado físico ni un límite universal de cinco. No se ensayó una sexta interacción física y no existe modo `apd-delta` en esta interfaz.

## 1. Elegir una vida sin cambiar el activo

Sitúese en `sistema/`, con el CPython3.13 x64 del entorno que ya contiene thinking4.5 oficial. En los comandos, `python` significa ese intérprete, no otra instalación elegida por parecido de nombre.

```
python -I -B -X utf8 gestionar.py version
python -I -B -X utf8 gestionar.py estado --vida ASISTENTE_MAIN
```

La selección aquí es el argumento `--vida`; **no ejecute `activar` ni `promover`** para seguir estos ejemplos. Conserve el original. Antes de experimentar, importe una copia completa emparejada bajo una identidad propia.

Corte a completar: vida `ASISTENTE_MAIN`; tick **PENDIENTE**; snapshot/SHA256 **PENDIENTES**; carpeta de exportación emparejada/SHA del manifiesto **PENDIENTES**; última operación y epoch **PENDIENTES**.

## 2. Hacer una copia continuable de verdad

Una exportación persistente contiene `EXPORTACION_SERVICIO.json`, `VIDA.deetsnap.gz`, `cola.sqlite3`, resultados y artefactos necesarios. No extraiga únicamente el snapshot ni sustituya la cola por otra vacía.

Use el par cerrado por la campaña indicado en la ficha de continuidad:

```
python -I -B -X utf8 gestionar.py mente-unificada-importar --paquete "CARPETA_DEL_PAR_COMPLETO" --vida APD_MI_COPIA
```

El destino debe ser una identidad nueva. La importación conserva su parentesco y los IDs de transporte; no enseña conocimientos nuevos y no inicia el servicio automáticamente. Para otra réplica use otro nombre y vuelva a importar el mismo par, sin fusionar sus experiencias.

`bifurcar` existe para mundos nativos, pero por sí solo **no copia el diario SQLite ni los artefactos persistentes**. No es el procedimiento de clonación del servicio APD, incluso cuando el snapshot indique un epoch cerrado. Tampoco `importar-estado` sustituye a la importación emparejada.

## 3. Iniciar un propietario y observar su estado

En una primera terminal:

```
python -I -B -X utf8 gestionar.py mente-unificada-iniciar --vida APD_MI_COPIA --backend mente_unificada --pausado --intervalo 0.5 --ticks-ocio 1 --guardar-cada 15 --max-segundos 600
```

Permanece ejecutándose en primer plano. No inicie otro propietario de esa vida. La pausa inicial permite inspeccionar antes de avanzar. El límite600s es una elección operativa del ejemplo, no un resultado científico ni una garantía de estabilidad.

En otra terminal, con el mismo intérprete y carpeta:

```
python -I -B -X utf8 gestionar.py mente-unificada-estado --vida APD_MI_COPIA
python -I -B -X utf8 gestionar.py mente-unificada-reanudar --vida APD_MI_COPIA --id reanudar-001 --esperar 120
```

`estado` lee una publicación del propietario: informa su antigüedad y no es un reloj nativo instantáneo. Mientras está pausado, las peticiones materiales esperan; por eso se reanuda antes de usarlas. Después, los intervalos libres avanzan realmente DEE según la cadencia declarada. Esa evolución también puede cambiar accesos: no es un congelador de memorias.

## 4. Petición literal desde un archivo JSON

Guarde `solicitud.json` UTF8 con este contenido, sin respuestas, operación calculada, ruta favorable ni campos ocultos:

```json
[{"modo":"apd","texto":"suma","operandos":[11,6]}]
```

El gestor recibe **JSON literal**, no un nombre de archivo en `--situaciones`. Para leer el archivo conservando sus comillas en Windows, use esta llamada al mismo gestor mediante una lista de argumentos:

```
python -I -B -X utf8 -c "import pathlib,subprocess,sys; contenido=pathlib.Path('solicitud.json').read_text(encoding='utf-8-sig'); raise SystemExit(subprocess.call([sys.executable,'-I','-B','-X','utf8','gestionar.py','mente-unificada-pedir','--vida','APD_MI_COPIA','--situaciones',contenido,'--id','uso-001','--esperar','120']))"
```

Este pequeño lector no interpreta ni resuelve el problema; sólo entrega los bytes JSON al comando existente. No es otro gestor. El signo físico adquirido de la palabra selecciona SUMA/DIFF; el signo de O2 selecciona nativa/externa/ayuda. Si falta una salida válida, se registra su ausencia; no se proporciona la respuesta esperada.

Compruebe `request.status` y el resultado, no sólo el código de salida del cliente. Si aparece `waiting_or_processing`, la acción puede seguir en curso. No repita con otro ID:

```
python -I -B -X utf8 gestionar.py mente-unificada-resultado --vida APD_MI_COPIA --id uso-001
```

Reutilizar el mismo ID sirve para observar/deduplicar; no autoriza repetir un efecto incierto. Estados `uncertain`, `failed_preserved` o `rejected_invalid` exigen examinar la evidencia conservada. Un rechazo o timeout no equivale a una pérdida cognitiva.

## 5. Otros archivos de petición admitidos

Conteo preparado:

```json
[{"modo":"apd-conteo","presencias":[1,0,1]}]
```

Composición asistida, no frase libre ni planificación nativa:

```json
[{"modo":"apd-componer","formas":["suma","diferencia"],"datos":[7,3,2]}]
```

Las formas se envían sin convertirlas externamente a instrucciones. Su función depende del estado adquirido actual; no se promete un resultado por su ortografía. El orden sí lo proporciona el operador. Un intermedio negativo, ausente o mayor que32 detiene la siguiente etapa; no hay reparación silenciosa.

Una configuración ambiental es una petición separada y explícita:

```json
[{"modo":"apd-ambiente","configuracion":{"precios":[1,5],"demora":[0,0],"disponibilidad":[true,true],"presupuesto":2}}]
```

Los precios son reglas del entorno simulado, no energía del ente o coste real de CPU. Precios0..28 y penalidad fija4 por ausencia de artefacto mantienen el retorno0..32. No mezcle esta configuración ni docencia con una evaluación en la misma petición.

Docencia deliberada, nunca oculta en una consulta:

```json
[{"modo":"apd-docencia","texto":"suma","senal":-1,"revision":true}]
```

Este último ejemplo es una **revisión docente explícita** en su copia personal; cambia lo que se espera de esa palabra y no se presenta como retención ni nueva adquisición espontánea. El docente proporciona el signo: es asistencia declarada. La primera enseñanza de `total`/`quita` sólo corresponde a un corte anterior a sus experiencias; no se repite como si fueran nuevas en la vida final. Una palabra arbitraria como `multiplica` no se vuelve válida por enviarla con `senal`: primero requiere arquitectura/interfaz nueva y comprobación propia. R04 no admite revisión de sus dos formas nuevas mediante `revision:true`. No restablezca metadatos o clocks para convertir una reenseñanza en primera adquisición.

El transporte acepta1..8 situaciones y hasta8192 bytes por petición; la docencia, configuración y calibración de ruta deben ir solas. Los operandos APD son dos enteros0..32; composición usa dos/tres formas y un dato más que formas, cada dato0..16.

## 6. Guardar, exportar y detener

Con el propietario todavía activo:

```
python -I -B -X utf8 gestionar.py mente-unificada-guardar --vida APD_MI_COPIA --id guardar-001 --esperar 120
python -I -B -X utf8 gestionar.py mente-unificada-exportar --vida APD_MI_COPIA --id exportar-001 --esperar 120
```

Espere a confirmar `completed`. El resultado de exportación da `paired_export.directory`; su ruta normal es `estado/servicios_persistentes/<world_id>/exportaciones/exportar-001/`. Conserve la carpeta entera y su manifiesto. El límite de espera no cancela una exportación que siga trabajando.

```
python -I -B -X utf8 gestionar.py mente-unificada-detener --vida APD_MI_COPIA --id detener-001 --esperar 120
```

Espere `running:false` y la salida del primer proceso. No borre locks ni mate procesos ajenos. Guardar y detener no cierran por sí solos el epoch técnico.

Para continuar en otro proceso, puede reiniciar **la misma vida y su mismo diario** con `mente-unificada-iniciar`. Para transferir o crear una rama en otro sistema, importe la carpeta emparejada con un nombre nuevo y luego iníciela. No repita solicitudes ya completadas ni resuelva una incertidumbre enviando otra acción.

## 7. Finalización técnica opcional

Sólo si necesita continuar mediante operaciones ordinarias fuera del propietario persistente, y después de detenerlo limpiamente:

```
python -I -B -X utf8 gestionar.py mente-unificada-finalizar-protocolo --vida APD_MI_COPIA
```

Exige cola sin trabajos pendientes/inciertos y protocolo sincronizado. Cierra metadata del epoch sin ticks ni modificaciones RAW/clocks. Conserva un par **anterior al cierre documental** consistente; ese par no debe mezclarse con el snapshot posterior cuyo SHA cambia por metadata. Una nueva apertura explícita del servicio preserva IDs y abre el epoch siguiente. La finalización no arregla daños, no borra peticiones y no sustituye la importación completa.

## 8. Qué conservar y qué no atribuir

Mantenga snapshot completo, cola, outbox, progreso, artefactos y genealogía de cada copia. Los archivos del investigador, semillas y respuestas de evaluación no deben alimentar al actor. No mezcle recuerdos de ramas distintas.

Las verificaciones de éxito del corte final, sus pérdidas, literalidades actualmente utilizables y snapshot exacto se completarán en la ficha de continuidad. Una capacidad histórica o un codec instalado no garantizan conocimiento accesible actual. No atribuya65 significados, R2 general, español libre ni planificación autónoma a esta guía.
