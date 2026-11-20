# Uso operativo MA02: revisión independiente de los registros01–12

El cálculo `recalculo/recalcular_servicio_01.py` comprobó los primarios ya
producidos, sin cargar mundos vivos ni ejecutar trabajadores. Referencia:
`evidencia/campanas/MENTE_ACUMULATIVA_R02/cierre/RECALCULO_SERVICIO_01.json`.

## Uso y continuidad demostrados

El snapshot completo R04 T1414 se importó como MA02_MAIN; admitir su contrato
operativo no cambió N, tick, RAW ni clocks. El panel inicial, trabajos, panel
posterior y continuación desde otro proceso utilizaron consecutivamente el
mismo individuo. Los cuatro signos se utilizaron antes del servicio, después y
tras guardar/cargar: 4/4 en cada panel, hasta T2486. No es la vida heredada E1.

Los24 usos físicos de seis sesiones —incluidas las dos ramas de control—
coinciden con el decodificador independiente de los ocho gates. Se comprobaron
27,844 observaciones RAW sin discrepancias. MAIN admitió36/36 entradas en su
bloque de trabajo:28 de consulta y8 de retorno. Las otras sesiones admitieron
28/28, sin rechazos. Las ocho operaciones instrumentadas registraron cero
denegaciones de la valla de I/O de Python y ocho procesos externos exactos.
Esta valla no es un sandbox del sistema operativo.

## Servicio real y retorno físico

MAIN seleccionó trabajadores +,−,+,− desde las emisiones materiales de gamma y
beta. Los dos primeros realizaron operaciones acotadas; los dos últimos
prepararon y verificaron una transacción. Fueron4/4 aceptados y un commit. El
control OMIT también obtuvo4/4 y un commit; el control NULLED produjo los mismos
cuatro comandos nativos, pero no lanzó trabajadores ni produjo sus archivos.

Los ocho archivos existentes de MAIN/OMIT se copiaron como evidencia exacta,
176 bytes en total. Se reconstruyeron determinísticamente sus bytes de zlib o
SHA, entradas, hashes, artefacto preparado y ley de aceptación: todo coincide.
El trabajador aplica una ley del entorno y nunca cambia el signo que recibió.

El retorno real utiliza únicamente el número de bytes efectivamente escritos y
leídos —12 o32—, no la bandera de aceptación. Dos pulsos simétricos de esa
carga incrementaron la carga nativa en24 o64, preservando el signo observado.
Los recibos de ambos pulsos fueron aplicados. Este ciclo demuestra acción,
efecto externo y transformación física posterior; no muestra aún una decisión
posterior más útil aprendida por ese retorno.

## Frontera de la atribución

- El operador selecciona el contexto solicitado, el calendario, los trabajos y
  las rutas genéricas. Los cuatro signos provienen del pasado físico.
- Las magnitudes públicas de cada trabajo se entregan al trabajador, no al
  sensor DEE de este contrato. Por tanto, los aciertos no acreditan comparación
  adquirida de esas observaciones externas nuevas.
- La misma acción persiste con retorno real, omitido o anulado. No hay evidencia
  aquí de política modificada por utilidad, selección autónoma de consulta o P2.
- El estado transaccional externo conserva los bytes del archivo preparado.
  Es estado legítimo del entorno, no una respuesta consultada para elegir el
  siguiente trabajador.
- MAIN termina el bloque enT1952 y OMIT/NULLED enT1950 porque faltan los dos ticks
  del retorno. La desigualdad final no es un contraste de edad emparejada. Los
  testigos locales de carga y ventanas de consulta sí tienen tiempos definidos.
- Las igualdades verificadas de continuidad son de N/tick/RAW/clocks, no de todos
  los metadatos, cabeceras, interfaces o bytes de snapshots diferentes.

El recálculo se repitió desde otra ubicación con sólo los doce primarios,
ocho archivos y dos fuentes necesarias; produjo exactamente los mismos bytes.
Es recálculo archivado portable, no reproducción nativa ni otra adquisición.
