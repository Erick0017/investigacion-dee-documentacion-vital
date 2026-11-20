# Revisión independiente de entrada común R03B y continuación R04

Esta revisión utiliza exclusivamente los primarios existentes. No importó DEE,
no abrió un Runtime y produjo cero ticks nuevos. El recálculo reproducible es
`recalculo/recalcular_entrada_comun.py`; su referencia está en
`evidencia/campanas/MENTE_ACUMULATIVA_R02/cierre/RECALCULO_ENTRADA_COMUN.json`.

## Qué está respaldado

En cada una de tres preparaciones nuevas N67, R03B conserva un mismo mundo
desde T0 hasta T1012: tres adquisiciones, seis usos intercalados, una cuarta
adquisición y seis usos posteriores. MAIN, OPPOSITE y NOGUARD producen 12/12
respuestas únicas concordantes con sus experiencias. Las historias opuestas
invierten las doce respuestas. Son tres vidas candidatas, no una continuación
biográfica del E1 heredado ni doce adquisiciones independientes por vida.

El lector requiere exactamente los mismos ocho sitios físicos para cualquier
petición, a entrada+4. Desempaqueta RAW uint64 y acepta un único estado activo,
SEM1 y dirección Z pura ±1. No recibe el token, el signo docente ni una
respuesta esperada. Sólo después se puntúa su salida con la historia docente.
La comprobación independiente de 94,975 observaciones no encontró diferencias
entre RAW y los campos publicados, paneles y sus frames, o respuestas y decoder.

En R04, todas las ramas descienden del mismo snapshot completo MAIN T1012.
La revisión doble cambia físicamente el signo de la columna0 a − en T1075;
posteriormente se usan correctamente la referencia revisada y las otras tres:
5/5. La revisión sencilla y su sham de dosis comparable dejan Z0 en ese punto
y sólo responden a la primera relación no modificada: 1/5. Esto respalda una
actualización funcional por el protocolo doble en este dominio, no una regla
de actualización aprendida de manera autónoma.

## Qué aporta la arquitectura preparada

El tipo i de la petición selecciona desde el anfitrión una dirección del token
y las rutas de seis recursos genéricos: tres de carga7 para cada signo posible.
Es un codec y direccionamiento P0 explícito. No contiene la polaridad correcta
y la misma lectura de ocho sitios se aplica a todos los tipos; no obstante,
todavía no es selección de acceso adquirida ni una interfaz sin información de
contexto. El contenido ± depende de la experiencia docente previa, P1.

Las consultas son materiales, no pasivas. En la primera consulta, la carga16
se transforma sucesivamente en21,28,35 y42. Los frames muestran salida de la
columna original, dirección Z pura en el gate, retorno XY y restauración de Z
en la columna. Estos testigos apoyan esa transformación y recorrido local;
no certifican una identidad única de portador ni cobertura causal global.

## Controles que cambian la interpretación

| Rama | Respuestas únicas correctas | Entradas nuevas aplicadas/solicitadas |
|---|---:|---:|
| R04 QUERY_RESOURCE | 5/5 | 35/35 |
| R04 NOQUERY | 2/5 ventanas, cuatro peticiones reales | 33/34 |
| R04 NOMARKERS | 2/5 | 28/29 |
| R04 NORESTORE | 2/5 | 31/31 |
| R04 revisión doble | 5/5 | 38/38 |
| R04 revisión sencilla | 1/5 | 34/37 |
| R04 revisión sham | 1/5 | 35/38 |

Sin restauración, la primera lectura sigue siendo correcta. Dos consultas
posteriores encuentran simultáneamente el gate antiguo de0 y el nuevo de2 o1.
El lector fijo devuelve indeterminación, sin elegir la ruta favorable usando el
token. Esto delimita una utilidad causal de la restauración para evitar esos
retornos falsamente disponibles durante la ventana observada. No prueba acceso
ilimitado ni que cualquier pérdida posterior sea destrucción del contenido.

Las guardas no son necesarias para los doce aciertos observados hasta T1012:
NOGUARD también obtiene12/12. Sí tienen un efecto material: MAIN y OPPOSITE
admiten92/92 entradas, mientras NOGUARD admite80/92 y rechaza doce recursos de
las ramas opuestas no utilizadas en cuatro consultas. Esos rechazos no se
eliminan del denominador ni se interpretan como memoria perdida.

En el cribado R01, aplicado retrospectivamente, el mismo gate muestra ± en
entrada+4 para PLUS/MINUS y ninguna salida válida al omitir el marcador, omitir
la petición o retrasar un tick el marcador. Es evidencia exploratoria de una
coincidencia temporal; no es una reserva independiente del diseño posterior.

## Límites y negativos preservados

- Se demostraron cuatro asociaciones físicas de signo y su uso repetido; no
  cuatro relaciones semánticas generales ni un selector P2/R2.
- El operador decide cuándo y qué tipo consultar y cuándo enseñar o revisar.
- El futuro adverso de una rama no puede sumarse al exitoso ni borrarse.
- Los fallos de R04 son fallos del acceso publicado. Sus frames parciales no
  bastan por sí solos para declarar convergencia del estado causal completo.
- Las parejas `.json.gz` y `.R02.json.gz` de R03B son bytes duplicados de un
  único ensayo, no réplicas.
- R02 se detuvo por longitud de metadatos y R03 por un tipo tuple no admitido;
  sus revisiones y prefijos se conservan. No son fallos cognitivos ni ensayos
  terminados equivalentes a R03B.

No hay en estos datos una política de acceso aprendida por consecuencias,
una generalización temporal fuera del calendario probado, coordinación social
adaptativa ni competencia en un entorno externo. Esas afirmaciones requieren
sus propios contrastes y no se heredan del acierto de este acceso preparado.
