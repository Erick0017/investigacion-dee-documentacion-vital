# Actualización de referencia y alcance del ciclo nativo

## Operación efectiva ya existente

`CONSOLIDACION_1_1/continuidad_funcional.py` programó:

`a.quantity.input('quantity.reference.cue',0,2211)`

`a.quantity.input('quantity.reference.resource',11,2211)`

T2211=33*67, fase0. La referencia67 se transformó físicamente en78. El control con los mismos materiales por `quantity.other.cue`/`quantity.other.event` quedó67. Los objetos posteriores50+cue5,73+cue5 y82+cue5 contrastaron menor/igual/mayor; el antiguo comparador R36/O16 se mantuvo separado. Plan anterior: `CONTINUIDAD_FUNCIONAL_PLAN_R1.json`.

Esto es adición física adquirida a una referencia existente, NO una función que ponga arbitrariamente referencia=Q. No debe llamarse reemplazo por Q si el recurso fue Q. `experience_reference(Q)` introduce cue5+Q; no garantiza borrar el valor antiguo, especialmente en una vida distinta de la preparación original.

El soporte nuevo `referencia_ambiental.py` sólo construye y programa esta experiencia prospectiva, sin avanzar: `p=plan(a,'ID',actual_addition=11,mode='paired'); schedule(a,p)`. Usa próximo tick0mod67 con lead≥5. Variantes congeladas: paired, no_cue, unpaired(cue+1tick), offpath y no_addition. No elige después el lector ni calcula acciones. `a.quantity.input` conserva recibos en estado operativo del hijo; avanzar por `a.run_until`, guardar mediante Store.

Contrastar en los mismos ticks y con objetos nuevos idénticos: preestado; encuentro t+3; referencia posterior; primera lectura posterior; objeto nuevo; antiguo R36/O16; panel social pequeño. No-cue puede también modificar la función: cue0 tiene materia/state aunque su carga sea0. El efecto fuera de fase es resultado experimental, no un control necesariamente inocuo.

## Qué ciclo es puramente v27 y cuál no

El componente de retorno existente permite una cadena nativa B→E1:

objeto privado de B → gradiente B → portador material ±X → encuentro en hub E1 → estado adquirido → lector genérico posterior → uso/delivery.

`social_habitat.py` programa por anticipado las mismas oportunidades en ambos bancos; no consulta la salida para escribir el contenido de E1. Una diferencia posterior en E1, dependiente del objeto B y su mensaje, con omisión/desacople/corte/sham pertinentes, demostraría interacción física con cambio de disponibilidad funcional en el mismo mundo. Se conserva como hipótesis hasta ejecutarla: el estado actual puede haber perdido acceso.

Sin embargo esa cadena B→E1 por sí sola NO demuestra un ciclo actual cerrado E1→entorno→E1. La cadena completa E1A→B→E1C existe como aparato y resultado histórico en `puente_adquirible.py`, pero el puerto original de A dejó de funcionar en el dominio tardío documentado. No reutilizar su nombre como éxito actual ni inyectar en B una copia del código leído externamente para simular cierre puramente v27.

Para afirmar cierre puramente nativo con los mecanismos existentes hay que registrar un portador generado por E1 que cambie materialmente el estado de B o una región ambiental y después una consecuencia que vuelva a ser utilizada en E1, sin callback que elija la entrada útil. Las oportunidades futuras pueden estar preparadas, pero su contenido o efecto debe cambiar por el encuentro nativo. El control que interrumpe ese portador, manteniendo la producción previa y oportunidades generales, debe alterar de modo interpretable el retorno y su uso.

Si Python convierte una dirección a cambio de disponibilidad en un depósito simulado y luego codifica ese depósito en entradas, existe un entorno híbrido cerrado legítimo, NO un régimen endógeno puramente v27. Debe conservarse esa atribución, aunque la ley ambiental sea fija y ninguna decisión de la tarea se calcule fuera de DEE. Un cambio de oportunidad producido por un nuevo portador v27 dentro de B es otra clase de evidencia y debe registrarse por separado.

Este soporte no ejecutó vidas ni declaró aprendizaje nuevo.
