# Aprendizaje nativo DEE

## Definición usada

Aprendizaje nativo significa que una historia de experiencias ordinarias modifica persistentemente estado/organización/fase/routing y cambia funcionalmente la respuesta posterior, con transferencia a situaciones no idénticas. No se exigieron pesos, gradientes ni sinapsis.

## Mecanismo descubierto

Dos portadores —cue y teacher— llegan sincrónicamente a un destino vacío. El reducer escribe un portador memoria cuya dirección es la suma-signo y cuyo `s_reg` es la suma capada. Ese linaje se desplaza. Más tarde una consulta entra por un puerto ordinario y colisiona con la memoria en el punto causal previsto. La salida conjunta es la respuesta aprendida.

La experiencia no edita un estado oculto ni escribe el output final. Entrada, entrenamiento y consulta usan los mismos canales de transporte/colisión del kernel.

## Escalera adjudicada

| Nivel | Resultado |
|---|---|
| memoria | confirmada: el linaje persiste y es recuperable |
| plasticidad | confirmada: experiencia cambia respuesta futura |
| asociación | confirmada: cue+teacher sincrónicos producen respuesta; inputs aislados no |
| contexto/historia | confirmada: separar teacher un tick o barajar label elimina la regla esperada |
| generalización de clase | 69/69 direcciones de consulta no vistas |
| inversión/reaprendizaje | 6/6 casos completos en holdout; discovery incluyó extinción y reacquisición |
| regla aritmética | traslación entera y successor confirmados en dominio congelado |
| composición | dos traslaciones aprendidas compuestas en ambos órdenes |
| suma/carry aprendidos | no promovidos; un reducer no entrenado más simple ya los resuelve |

## Confirmaciones

### C6H01 — asociación/plasticidad

- Entrenados: 20/20; Wilson 95% inferior 0.8389.
- Controles nucleares untrained/history-shuffled/label-shuffled: 60/60 neutrales.
- También pasaron cue-only, teacher-only, matched exposure, reset, memory ablation, query absent y off-channel.
- Incluyó nuevos tamaños/marcos, tokens `state/clock`, `s_reg`, timings y demora a través de un wrap toroidal.

### C6H02 — clase e inversión

- Transferencia a inputs direccionales no vistos: 69/69; Wilson inferior 0.9473.
- Controles: 207/207 neutrales.
- Inversión/reacquisición completas: 6/6.

### C6H03 — regla de traslación

- 24/24 mundos entrenados y 96/96 canales exactos.
- SUCCESSOR: 6/6.
- 144/144 mundos de control no resolvieron la regla; 0/576 canales de control acertaron.

### C6H04 — composición

- 30/30 mundos exactos; 15/15 en cada orden causal.
- 270/270 controles parciales, barajados o ablacionados fallaron la composición completa.

## Interpretación

El aprendizaje reside en una historia distribuida materializada como linaje móvil y routing futuro, no en un parámetro global. Es memoria episódica operativa con álgebra de composición en el sector no saturado. La generalización proviene de que el reducer aplica la misma operación a valores/direcciones nuevos.

## Límites

- No se demuestra aprendizaje universal, inducción de programas, multiplicación ni transferencia arbitraria de bit-width.
- La representación numérica fue congelada y label-blind respecto al holdout, pero fue diseñada para interrogar la operación nativa de suma capada.
- La composición probada es conmutativa para traslaciones; no implica composición general de funciones.
- El efecto depende de que la memoria encuentre causalmente la consulta; sin ese linaje/routing no existe readout.
