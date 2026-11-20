# Contexto EO02: qué se intentó y qué enlace falta

## Resultado ejecutado

Siete ramas diagnósticas exactas de **EO01_MAIN T121681**, sin avanzar EO01,
EO02 MAIN ni el predeterminado. Se conservaron todos los futuros, entradas,
rechazos, fuentes por revisión y snapshots completos locales. No se escribió
RAW, clocks o un contenido aprendido desde Python. No se preparó un nuevo T0.

**No se consiguió adquirir y conservar dos políticas contextuales.** Tampoco se
convierte el par `own` y el sesgo contextual fijo en dos políticas por sumarlos.

### R01: experiencia en el cabezal contextual existente

Tres historias: sin pulso; escalar9 con dirección `(-1,-1,1)`; escalar9 con
dirección `(1,-1,1)`. El punto de admisión fue `(6,16,12)`, ya RAW vacío. Las dos
entradas fueron aplicadas. Cada rama continuó24 ticks y recibió la oportunidad
común `10:22`, lector fijo y retorno omitido. Las tres terminaron en T122463.

Los campos contextuales siguieron **7/5**, las referencias propias terminaron
**306/298**, B conservó **61/19**, y las tres actuaciones comunes fueron `+`.
Los dos pulsos modificaron la dirección del contexto izquierdo durante un tick,
pero no su carga ni el uso posterior evaluado. Es una transformación física
transitoria, no adquisición contextual persistente.

Primarios: `AUX_EO02_CTX_R01_{none,minus,plus}.json.gz`.
Fuente exacta: `piloto_contexto_r01.py`.

### R02: dos datos directamente en los candidatos de percepción B

Una copia recibió el mismo par `10:30` primero en A, y después dos datos en
`B+(-1,-1,1)` y `B+(1,-1,1)`, con una consulta genérica de carga0 en B. A emitió
`-`; B emitió `+`. **No es prueba de dos contextos útiles**, pues los dos datos
B fueron `rejected_occupied`; sólo la consulta fue aplicada. Un sitio con
state0/SEM4 no es RAW vacío. El negativo se conserva y no se reetiqueta como
comunicación semántica o transferencia.

Primario: `AUX_EO02_CTX_R02_common10_30.json.gz`.
Fuente: `piloto_B_dos_datos_r02.py`.

### R03: única corrección periférica, fijada antes del contraste

Se sustituyeron sólo los orígenes de los dos sensores por sitios efectivamente
RAW vacíos: `(19,13,14)` dirigido `(-1,0,1)` y `(19,12,14)` dirigido `(1,1,1)`.
Los dos escalares se presentaron un tick antes de la consulta genérica fija de
B. No se leyó un target para escoger canal, ventana ni signo. El operador sigue
seleccionando la oportunidad de A y B: es asistencia **P0**, no selector aprendido.

Tres ramas exactas, con plasticidad activa:

| Par crudo | A | B | Solicitudes B aplicadas |
|---|---:|---:|---:|
| 10:30 | - | + | 3/3 |
| 0:50 | - | - | 3/3 |
| 64:50 | + | - | 3/3 |

B reaccionó al cambio de R30 a R50, pero **no** a L0→64 manteniendo R50. A sí
cambió en este último contraste. Por tanto no se cuentan dos variables relevantes
en la nueva interfaz B. La admisión del dato no demuestra percepción funcional.

El sitio B izquierdo `(18,13,15)` fue exactamente RAW
`4611686018427387904`, state0/SEM4, durante todos los44 frames de cada rama.
El sitio derecho sí mostró SEM1 con s_reg30/50. Los valores privados B61/19
permanecieron. Esto delimita una insuficiencia de ruta/sustrato de esta interfaz;
no un máximo universal de capacidad del kernel ni destrucción de la memoria B.

Primarios: `AUX_EO02_CTX_R03_{common10_30,left0_right50,left64_right50}.json.gz`.
Fuente: `piloto_B_periferico_r03.py`.

## Estado y mecanismo, sin causalidad exagerada

La inspección pasiva conservó idénticos tick, RAW y clocks de EO01 T121681. Sus
contextos tienen8 vecinos Moore vivos, frente a6 de las referencias propias.
La diferencia es un dato geométrico, **no** prueba de que el número8 sea por sí
solo la causa del bloqueo: no se retiraron anclajes ni se ejecutó ese corte.

El soporte contextual conserva una contribución previa; el retorno EO01 modifica
la referencia propia. No existe en el contrato R9 una actualización arbitraria
del contexto ocupado. El lector B reutilizable sigue preservando contenido,
pero añadir un nombre de sensor a un sustrato inerte no crea el enlace faltante.

## Fuentes dirigidas y límites de reutilización

- `ente_operativo_01_core.py`: retorno material posterior a la acción real;
  sólo `own` dispone aquí del mecanismo de actualización por consecuencias.
- `cierre_funcional_cf01.py`: geometría, testigos y lector fijo común.
- `arquitectura_distribuida_mi02_r8.py`: interfaces inmutables, admisión legal,
  fuentes de transporte y retorno. Es el adaptador realmente heredado por R9.
- `geometria_distribuida_mi02_r6/r7/r8/r9.py` e informe científico MI02:
  receptor contextual, separación de lector/referencia, huecos inertes desde T0.
  La actualización arbitraria del primer contexto no fue acreditada allí.
- `comparacion_efimera_mi02.py`: dos referencias persistentes y lector liberable
  en otra preparación N17. No se importaron a EO01 por compartir biblioteca.
- `acceso_adaptativo_01.py`, contrato AA01: selector modificado por consecuencias
  en N67 y fases/rutas concretas. No es portable a N26 mediante renombrar centros
  o sumar las capacidades de AA a EO02. No se ejecutó ni trasplantó aquí.

Las consolidaciones de CPC7/Ciclo02 orientan la pregunta, pero estos pilotos no
son reproducción de sus controles ni heredan su revisión selectiva. El informe
MI02 y los contratos dirigidos se contrastaron con el código ejecutado; no se
afirma nueva lectura de sus primarios históricos voluminosos.

## Decisión para la candidata

No se incorpora un selector contextual nuevo: no superó la prueba funcional.
Se incorpora al expediente **un límite de interfaz reproducible** y su recálculo.
Los lectores/suministros nuevos se conservan sólo en sus ramas AUX, no en MAIN.

Una revisión anatómica futura dentro de esta entrega necesitaría habilitar de
forma declarada el transporte al dato izquierdo B o un soporte alternativo y
un encuentro de selección/entrega hacia A. No basta presentar dos acumuladores
desconectados. No se encontró ni ejecutó un mecanismo v27 que retire el límite
SEM4 heredado sin edición externa, y no se retiró. Cualquier cambio de esa
preparación sería ingeniería declarada, no aprendizaje ni reparación retroactiva.

Para una prueba T/U/H válida, los brazos deben partir del prefijo anterior a la
nueva adquisición, conservar la misma anatomía y oportunidades y distinguir
retorno real, omitido y desacoplado. Una prueba A→B→C→A tiene que volver con la
misma vida y evaluar la primera actuación antes de nuevo feedback. Los presentes
pilotos no cumplen ese criterio de dos contextos y no se suman como resultado de
la secuencia principal.

## Comprobación portable

Ejecutar con Python estándar, sin motor y sin nuevos ticks:

```text
python recalcular_contexto.py --primarios RUTA/contexto --salida RECALCULO_CONTEXTO.json
```

`RECALCULO_CONTEXTO.json` contiene siete casos, hashes de primarios y fuentes,
denominadores y observaciones. `ESTADO_SOPORTES_PASIVO.json` conserva vecindades
completas locales, verificación de observación0ticks, copias de fuentes comunes
y localizadores/hashes de siete snapshots completos que permanecen localmente.

Unidades de muestra: siete bifurcaciones deterministas de un único prefijo,
no siete organismos independientes ni réplicas de aprendizaje.
