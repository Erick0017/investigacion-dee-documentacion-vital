# Sensor R04: dos pares balanceados, sin evaluación Native todavía

La candidata añade una preparación sensorial P0 a una bifurcación completa,
no a MAIN ni al padre protegido. Mantiene N=67, el selector R04 existente,
sus tres lectores/actuadores históricos y el retorno genérico por traza.

O=(25,13,53). Los dos puertos existentes en O+(-1,0,+/-1) reciben rawTag.
Dos puertos nuevos en O+(+1,0,+/-1) reciben rawGoal. Los cuatro se programan
en q+3. El query lleva siempre5. No se calcula igualdad, relevancia,
comparación de tags ni acción correcta en Python. Hay dos variables binarias
independientes, cuatro combinaciones posibles y cuatro señales materiales;
no son cuatro variables independientes ni cuatro conocimientos adquiridos.

En R03, goal estaba en el payload5/7 de la salida y el actuador histórico
usaba sólo la dirección. R04 permite que goal contribuya mediante otra
vecindad al encuentro nativo. Que esto produzca una selección contextual,
y mucho menos que esa selección mejore por consecuencias, sigue sin probar.

El observador de nueve sitios se conserva como diagnóstico externo. Nunca
sustituye el lector de tres sitios para escoger una acción retrospectivamente.
Los otros seis sitios no crean seis acciones nuevas.

El preflight offline del par completo APD04_MAIN T639374 comprobó RAW=0
exacto en las cuatro fuentes, no sólo state=0. Las dos fuentes nuevas no
contienen interfaces ya declaradas; no se encontraron intersecciones exactas
con los soportes R04 conocidos ni con las dieciocho formas léxicas actuales.
Esto comprueba admisibilidad en ese corte, no aislamiento causal ni vacancia
en un futuro. La futura admisión deberá volver a rechazar si el preestado
real ya está ocupado; nunca se limpiará ni se sustituirá materia.

R04 solicita16 entradas por ventana frente a14 de R03. El número de señales
es distinto aunque la suma de payloads elementales coincida para cada par.
Debe informarse esta diferencia: no son dosis materiales idénticas.

Fuente exacta: sensor_dos_pares_balanceados_apd04_r04.py.
SHA-256:9159ca59bdacc0e5d0cc5d1d01f30296df3f3467d58f969ba2fffab59159759d.
Preflight: evidencia/campanas/APD04_ECOSISTEMA_COGNITIVO/PREFLIGHT_SENSOR_R04_N0.json.
Hasta este documento: cero Runtime instanciados y cero ticks por R04.
