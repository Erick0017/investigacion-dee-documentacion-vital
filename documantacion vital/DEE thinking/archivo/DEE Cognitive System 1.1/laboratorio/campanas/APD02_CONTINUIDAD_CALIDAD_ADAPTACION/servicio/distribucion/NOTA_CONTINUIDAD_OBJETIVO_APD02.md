# Continuidad de objetivos APD02: hechos operativos, no memoria sustituta

El estado `goal_pending` conserva el objetivo externo, la observación pública, el segundo operando privado del ambiente, el número de oportunidades, la incertidumbre y los bytes de artefactos ya producidos. Son hechos del entorno y del transporte. Su serialización no demuestra que DEE recuerde el operando ni constituye un plan de acción.

La fuente actual de `additional_operational_state` incluye esos hechos completos en el testigo de dependencias operativas. La continuidad exige el snapshot nativo completo **y** su diario/colas/recursos emparejados; comparar solamente un hash de RAW no prueba identidad de todo el protocolo. Un resultado no confirmado permanece bloqueado y nunca se reintenta automáticamente.

`meta-iniciar --segundo-oculto` prepara una condición externa. `meta-paso` ofrece oportunidades; la salida física escoge ACT o QUERY. Sólo QUERY revela el dato al ambiente público; un ACT prematuro falla sin que Python lo sustituya por QUERY ni fabrique un operando. La parada al completar el archivo verificado y el máximo de cuatro oportunidades son asistencia preparada, no planificación general adquirida.

Las pruebas nuevas de distribución usarán una copia emparejada personal del corte final autorizado. Un proceso la guardará con objetivo materialmente iniciado y no terminado; otro proceso continuará **esa misma copia**, sin T0, sin repetir ids ya completados, sin descartar colas y sin convertir los diarios del investigador en entradas de respuesta. Los resultados, incluso silencios, rechazo o agotamiento de las cuatro oportunidades, se conservarán.

Este documento es una preparación de distribución. No acredita una prueba Full ejecutada ni reemplaza el corte final real, sus recibos o la autorización de cierre.
