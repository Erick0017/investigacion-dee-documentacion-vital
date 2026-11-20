# H2 — repertorios separados por fibra destino

ID candidato: `destination_repertoires.core07.c7h02.candidate.v1`  
Versión: `0.1.1-candidate`

## Constructor respaldado

El panel separado instala K pares cue/teacher sobre K fibras destino disjuntas,
espera la colisión de entrenamiento e inyecta después una consulta nueva en un
puerto inicialmente vacío. El observable exige K respuestas exactas y tres
identidades de contabilidad: una unidad de support consumida por entrenamiento,
otra por readout, y suma global de `s_reg` conservada más las consultas.

El panel de solapamiento fuerza dos memorias a una misma fibra. El reducer
produce un portador compuesto y su readout sumado, pero ninguno de los dos
decoders individuales conserva identidad. El control `off_fiber` desplaza una
ruta tres celdas con igual inventario y no debe producir el merge compartido.

## Dominio y límites

El lock y la API candidata se restringen a semantic-1, fondo periódico vacío,
tiempos ordenados, geometría sin auto-wrap durante la lectura, cargas validadas
antes de cualquier conversión a `uint16_t`, sin fuentes semantic-4, destinos
vacíos y sumas bajo cap. K=40 es sólo un límite inferior
observado de capacidad separada; no es un máximo global. La contracción
`Delta support=-sum(k_f-1)` es exacta sólo en ese sector sin nacimientos,
muertes, emisiones ni destinos preocupados. `s_reg` no se denomina energía.

## Decisión de integración

Permanece candidato: el catálogo estable carece aún de un contrato para bancos
de cardinalidad dinámica, inyección tardía K-aria y presupuesto sectorial. La
promoción requiere declarar footprint, capacidad por puerto y persistencia del
vector de canales sin convertir la geometría física en fan-out de metadatos.
