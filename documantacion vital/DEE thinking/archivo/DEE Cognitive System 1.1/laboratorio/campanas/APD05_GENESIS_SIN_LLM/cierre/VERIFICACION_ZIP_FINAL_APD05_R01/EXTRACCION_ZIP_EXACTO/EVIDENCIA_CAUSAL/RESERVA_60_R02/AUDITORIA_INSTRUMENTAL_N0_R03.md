# Recálculo instrumental N0 R03 — reserva integrada 60 R02

Se analizaron exclusivamente los 52 eventos existentes de `PRIMARIOS/EVENTOS.jsonl` (4,697,807 bytes; SHA-256 `5e5b67398c3d571a512d16321651a64488becb28e1654bf78b94176a639fc686`). Cero nuevos ticks, ninguna carga del motor, ninguna modificación del actor o del estado. R02 y los originales se conservan.

## Error instrumental localizado, no contradicción física

El ID Native 96375 tiene tres testigos en el evento de índice 32 (`legacy_consequence_opportunity_one`). En `$.transport.result.result.rows[0].rows[0].native_return.all_generic_resources[3].receipt` consta `applied`, requested/effective tick 669944. En `selection.all_scheduled_requests[5].receipt` y `selection.generic_only_requests[2].receipt` constan copias previas `scheduled`, effective_tick null. Coinciden ID, kind, channel `APD02.trace.R04.divert.-1` y requested_tick. El orden de recorrido de objetos JSON no es el orden físico de los recibos.

R03 agrupa los testigos del mismo ID, exige invariantes iguales y conserva el único recibo terminal frente a sus alias de programación. Dos terminales diferentes siguen produciendo error. Una prueba N0 sintética confirmó ese rechazo. Hay 18 grupos con alias scheduled/terminal; todos se exportan con sus localizadores originales en el recálculo. No se usa una regla genérica «último gana».

Una segunda incompatibilidad de esquema quedó delimitada: `suma` y `diferencia` en los eventos 33 y 38 tienen el lector histórico common24, no common36. R03 utiliza geometría common24 fija I(8)/J(4), conforme a `sistema/capacidades/lexico_apd_extendido_04.py`, y exige exactamente sus 24 posiciones y signos. Los otros lectores conservan íntegros los controles common36 de R02. No se eligieron posiciones según su acierto.

## Resultados comprobados

- 52/52 operaciones de transporte archivadas con estado completed.
- 9,604 IDs Native únicos en estos eventos: 9,600 applied y 4 rejected_occupied. Los cuatro rechazos son docentes repetidos en los eventos 5, 6, 12 y 13. No deben desaparecer del denominador ni confundirse con fallos de las consultas posteriores.
- 4,766 observaciones RAW contrastadas con sus campos decodificados usando enteros uint64 exactos.
- 40/40 selecciones de acceso con emisión única y coincidencia con el criterio de acceso a versión del protocolo preparado; 16/40 efectos ambientales marcados useful. Son 40 en este archivo, no 40 aprendizajes independientes. El prefijo ya recalculado `../MAIN_VIGENCIA_R02/RECALCULO_RAW_R02_GEOMETRIA_ESTRICTA.json` contiene otras 4/4 selecciones, episodios 31–34, T655620–T656283, con 2 efectos useful; la reserva comienza en el episodio 35. El acumulado consecutivo es por tanto **44/44 selecciones P0, 18/44 efectos useful**, sin duplicar esos episodios. La fuente EVENTOS del prefijo tiene SHA-256 `5c84ec42afb430ed23c474615c64eac689771d5184cbdbe1029bd4d0db5d339f`. El cache ambiental y el codec de versiones son P0 declarados; esto no demuestra una nueva política aprendida ni R2.
- 42/42 consultas léxicas con emisión única: clasifica 20, equilibra 7, luma 4, nara 4, alfa 2, beta 2, suma 2, diferencia 1. Estas son consultas de una misma trayectoria, no réplicas independientes ni 42 palabras adquiridas.
- Tras la docencia explícita de signo negativo, clasifica emite − en T658681 y se usa como equilibra en T659485/T659954. Tras la revisión positiva emite + en T661093. La iniciativa de enseñar/revisar es del operador; el signo posterior procede de la lectura física.
- El panel tardío conserva alfa−, beta+, luma+, nara−, clasifica+, equilibra− en T683337–T683672; los seis eventos 45–50 tienen 7/7 entradas aplicadas cada uno. No se reenseñaron las otras cinco formas para producir ese panel.
- 28 usos numéricos, de los cuales 25 tienen emisión única y 3 ninguna. La reserva del valor 20 en T682697 no tiene candidato: no es un cero físico. Otros dos casos sin candidato aparecen en T665264 y T667207. No se rellenan silencios con cero.
- Las dos oportunidades del selector histórico R04 (eventos 32 y 42, episodios 59 y 72) emiten INSPECT. Ambas tienen `new_quality:false` y `useful:false`; son **0/2 mejoras de calidad**, no dos mejoras. No confundirlas con el nuevo selector P0 de versiones.

## Archivos y reproducción

El resultado completo y sus localizadores están en `RECALCULO_RAW_R03_RECIBOS_CON_ALIAS.json`, SHA-256 `1229d97614965c25a08fe429c9134003f856f071ebc257ef41bb975bcbf0ea48` (83,537 bytes).

Código R03: `laboratorio/campanas/APD05_GENESIS_SIN_LLM/analisis/recalcular_vigencia_apd05_r03.py`, SHA-256 `0949faeaf5bd2e4c7fc5ddf77e8a0d23b4981e4dd6ede011fc4152c8c5f49d96`. Requiere el R02 intacto en la misma carpeta; su hash queda registrado dentro del JSON. Sólo biblioteca estándar.

Comando: `python -I -B recalcular_vigencia_apd05_r03.py EVENTOS.jsonl --output SALIDA_NUEVA.json`. La salida se crea exclusivamente: no sobrescribe un resultado existente. El recálculo no inicia Native, no reproduce física y no certifica una promoción ni modifica la vida activa.
