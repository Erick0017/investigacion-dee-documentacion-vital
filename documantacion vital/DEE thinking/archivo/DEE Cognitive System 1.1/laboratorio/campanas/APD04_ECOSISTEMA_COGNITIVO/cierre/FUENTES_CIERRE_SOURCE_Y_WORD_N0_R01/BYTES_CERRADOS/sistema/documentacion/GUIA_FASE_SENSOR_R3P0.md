# Protección sensorial de fase R3P0

Es una asistencia temporal preparada, explícita y limitada; no una regulación aprendida de E1. R16 contrastó su beneficio físico en una ventana emparejada sin docente ni edición de campos. No está activada globalmente por defecto ni modifica el motor oficial. La nueva candidata `MU_MAIN_FASE_R3` cerró su reserva propia R17 en T104472: 3684.0006458 segundos operativos no pausados, 4097/4097 entradas aplicadas, 120/120 lecturas de memoria y 12/12 tramas128 con salida única. Se verificaron 101 usos del calendario P0. El panel antiguo final fue observado en T102782, antes del tramo ocioso final. La reserva R11 queda preservada; las agendas posteriores no fueron gemelas por diferencias de admisión, y la atribución causal del calendario procede de R15/R16.

```text
mente-unificada-importar --paquete PAQUETE_EMPAREJADO_CERRADO --vida COPIA_IDENTIFICADA
mente-unificada-finalizar-protocolo --vida COPIA_IDENTIFICADA
unificada-proteger-fase --vida COPIA_IDENTIFICADA
unificada-estado --vida COPIA_IDENTIFICADA
```

Estos comandos son subcomandos del mismo `sistema/gestionar.py`. La finalización
de protocolo es explícita, con el propietario detenido, y no avanza el mundo:
cierra el epoch emparejado antes de una mutación ordinaria. No sustituye un
guardado ni una reparación. No ejecute el cierre mientras un propietario sigue
trabajando. Después puede abrirse un nuevo epoch con el servicio habitual.
Para una vida con FIFO, artefactos y protocolo persistente no utilice
`bifurcar` como sustituto de la importación emparejada: un snapshot aislado no
transporta todo ese estado. En la distribución se abre una copia mediante
`INICIAR.bat abrir MENTE_UNIFICADA MI_COPIA`; si ya tiene el flag, no hace falta
admitirlo nuevamente ni cerrar su protocolo para utilizar el servicio.

La admisión exige N67, interfaz sensorial actual ya preparada y clocks locales A/B alineados con el tick del mundo. No avanza ticks ni cambia memorias. Después, `unificada-sesion` con `modo:dato` o `modo:crudos` desplaza el protocolo sensorial completo entre0 y10ticks cuando su ventana crítica inclusiva q−1..q+8 contiene un múltiplo391. El calendario se decide antes de introducir las entradas y no recibe el valor observado, el target ni la respuesta esperada.

El lector, la geometría, la cuantización y los workers se conservan. En `crudos`, todos los componentes y recursos se desplazan juntos, no sólo la consulta. Cada recibo identifica q solicitado/efectivo, espera y ventana crítica. El uso ordinario del selector, las experiencias y los accesos a asociaciones no cambian. Sin activación explícita permanece exactamente el calendario físico R2.

Esta protección no edita clocks, no repara un futuro ni reenseña información. Esperar también puede cambiar otros encuentros; no se garantiza estabilidad general o retención por la sola activación. Conserva los futuros anteriores y trabaja sobre una copia identificada.

La candidata MU_MAIN_FASE_R3 recibió además una única experiencia B0 declarada
para revisar su referencia antigua D−21→−20. Esa operación material es distinta
del flag de calendario y no se presenta como recuperación sin reenseñanza.
