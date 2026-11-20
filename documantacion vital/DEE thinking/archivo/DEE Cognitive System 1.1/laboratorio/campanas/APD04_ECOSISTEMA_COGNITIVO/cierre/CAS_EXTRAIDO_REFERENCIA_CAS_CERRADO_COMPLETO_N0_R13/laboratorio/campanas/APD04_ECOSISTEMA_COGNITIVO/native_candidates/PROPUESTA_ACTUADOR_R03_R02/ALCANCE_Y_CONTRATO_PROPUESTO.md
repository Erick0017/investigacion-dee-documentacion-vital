# ACT_R03: única propuesta P0; todavía no incorporada

La preparación propuesta conserva el mismo mundo, lector histórico de tres
puertas, sensor R03 y mecanismos nativos de retorno. Cambia el transductor fijo:
−1→INSPECT, 0 coherente y único→WAIT, +1→USE. La ausencia o ambigüedad de emisión
no se traduce como WAIT. No hay nueva geometría, selección por respuesta esperada,
copia de conocimientos ni modificación de RAW o clocks.

La configuración explícita `configurar-actuador-ecosistema R03` prepara el enum y
el contrato ambiental `APD04.posteffect_quality.relevant_gain_or_irrelevant_formed_wait.R03.v1`.
No enseña por sí misma la selección de WAIT. R01 y R02 siguen disponibles con
sus mapas, fórmula de utilidad y retorno anteriores; no se recalifican sus datos.

Para R03 se registran por separado:

- `old_work_gain`: la utilidad del examen anterior; WAIT vale cero.
- `new_quality`: para INSPECT/USE coincide con `old_work_gain`; para WAIT exige
  cero único formado, fuente irrelevante al objetivo actual y ningún cambio de
  los objetos ambientales o las cargas durante esa oportunidad.
- `counters.useful`: sigue contando el criterio antiguo; `quality_success`
  cuenta aparte los resultados del contrato nuevo.

La firma exacta incluye todos los objetos con id, tag, valor, versión, caché y
bin, y las cargas. Excluye cursor, episodio, contadores y diario: su avance
preparado no es aprendizaje ni alteración del objeto. La evolución física DEE
continúa durante WAIT; no se afirma que el universo permanezca sin cambios.

La relevancia sólo se calcula después de la emisión y del efecto, como parte
del verificador ambiental. El actor no recibe el bit «correcto», una ruta, un
target ni la firma completa. Recibe la misma transducción sensorial elemental
y, posteriormente, la consecuencia genérica existente. SUCCESS conserva el
comportamiento previo: no introduce un nuevo puerto de refuerzo positivo.

El dominio propuesto es `actuator=closed`. Un uso R03 con actuador anulado se
devuelve explícitamente fuera de dominio, sin respuesta cero fabricada ni
feedback válido. No se extrapola a ese control una ventaja de WAIT.

Una mejora de `new_quality` no reemplaza ni debilita retrospectivamente el
examen antiguo. Deben mostrarse ambos resultados y distinguir trabajo relevante,
inhibición correcta, emisiones válidas y ausencia de respuesta. Ninguna mejora
numérica acredita por sí misma P2/R2, atención aprendida o iniciativa autónoma.

La propuesta contiene tres fuentes base, tres fuentes propuestas, diff y pruebas
N0 de lógica/transporte. Esas pruebas no ejecutan Native ni demuestran equivalencia
física. El plan de dos ramas y su autorización corresponden a Root y al expediente
de controles; la reserva R02 actualmente activa no se modifica.
