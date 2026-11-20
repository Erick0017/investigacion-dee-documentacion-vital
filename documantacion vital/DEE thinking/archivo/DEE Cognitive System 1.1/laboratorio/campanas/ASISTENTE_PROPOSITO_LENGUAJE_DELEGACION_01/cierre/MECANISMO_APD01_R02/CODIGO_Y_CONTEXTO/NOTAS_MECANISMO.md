# APD01: realización aritmética propuesta desde el estado existente

Lectura dirigida, cero ticks nuevos. El prompt adjunto se leyó completo. Se
consultaron los contratos/código FI01 actuales, los primarios numéricos CORE06/07,
y las extracciones ya indexadas de Procesamiento Nativo y OBP2.1, incluido su
cierre. No se afirma una nueva lectura íntegra de los DOCX.

## Primera realización sin nueva anatomía

El árbol FI01 ya reúne aportes separados en `C=(12,17,18)` y transporta el
registro a `S=(14,15,16)`. Los primarios históricos contienen cargas nativas19
y21 al presentar19 y19+2, con dirección fija `(1,-1,-1)` en C dos ticks antes
del datum. La propuesta no altera esos puertos ni consulta la respuesta esperada:
un lector numérico fijo obtiene `s_reg` en ese encuentro. Esto convierte un
mecanismo preparado y ejecutado en una función aritmética de dominio declarado,
pero sus nuevas reservas todavía no se han ejecutado.

`suma(a,b)` aporta cada operando por un canal fijo. `diferencia(a,b)` utiliza
el mismo agregado con representaciones independientes `a` y `32-b` y lector
afín `s_reg-32`. Se declara toda esta transducción; no se presenta el complemento
de un operando ni la resta de un fondo como descubrimiento de DEE.

No se necesitan nuevos sitios físicos. Una inspección **sin Runtime** del
snapshot padref389… confirmó RAW0 y clock104472 en C, S y `(13,17,19)`, además
de cola nativa vacía. Eso no garantiza vacancia futura ni elimina contexto:
los recursos siguen sujetos a admisión y al paisaje durante la nueva ejecución.

## Qué internalización respalda el antecedente y qué no

CORE06 y Procesamiento Nativo, nodos253–283, describen la escritura nativa de
un desplazamiento: entradas separadas `B-x` y `y` forman `B+delta`; una consulta
nueva suma `n` y el lector retira el fondoB. Los nodos308–333 documentan una
segunda composición y un relay material de carga0; CORE07 también conserva
reprogramación positiva y pérdidas bajo daños. La identidad de esta familia es
una traslación aprendida dentro de un sector, no aritmética universal ni
recuperación de contenido realmente destruido. No se puede contar el árbol
preparado R1 como operación adquirida mediante docente.

Los controles CORE06/07 recuperados usan adaptadores de arrays e intervenciones
externas identificadas. No se reutilizarán esas escrituras como experiencias
legales de la vida nueva. Una adaptación por interfaces exige demostrar
coincidencia, ruta y reutilización, y declarar consumo/desplazamiento de memoria.

OBP2.1 (nodos445–599 de la extracción dirigida) separa relación conservada,
estado de expresión y plasticidad por contexto/fase. El cierre retira una
atribución anterior al retorno remoto: no se importará esa explicación como
un mecanismo confirmado de internalización. Soporte, suministro y adquisición
se contabilizan por separado.

## Código y localizadores reutilizados

- `sistema/capacidades/percepcion_cruda_fi01.py`: geometry, frame y transporte.
- `sistema/capacidades/mente_unificada_01.py`: query_timing R3P0, propietario.
- `sistema/capacidades/core/verificaciones/CORE06_PRIMARY_TRANSITIONS.json`.
- `sistema/capacidades/core/verificaciones/CORE07_PRIMARY_TRANSITIONS.json`.
- `evidencia/genealogia/LECTURA_DIRIGIDA/FUENTES_ABIERTAS.json`: extracciones
  PN fuente SHA d619b530658d2d352a24051508f3d49df555846afc475e3532e47a368a458ddb;
  OBP2.1 fuente SHA c9cd0f515e35982ea9fb726ccddfd0a61464a04fa6c2a630a0039c170f1f978f.

El módulo candidato no construye Runtime, no carga snapshots y no mantiene
respuestas. Su importación/inspección no ejecuta ticks; sólo `native_pair` llama
al protocolo material del propietario que entregue el gestor.
