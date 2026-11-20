# Alcance científico y límites de interpretación — Entrega 02

## Qué aporta técnicamente

La entrega permite instanciar y conectar organizaciones respaldadas por fuentes
DEE dentro de un único mundo persistente. El consumidor puede seleccionar un
descriptor, validar parámetros y puertos, presentar experiencias, continuar el
mismo estado, observar, guardar, restaurar y cambiar de agenda equivalente.

Las dos composiciones demostrativas ejercitan:

- aprendizaje/actualización/consulta posterior con control sin actualización,
  corte físico y valores reservados;
- historia relativa, contexto distribuido, contribuciones multicanal,
  recurrencia y controles de canal ausente frente a portador de carga cero.

Los builders preparan geometría, soportes y recursos declarados. El kernel
produce los encuentros y estados posteriores. Una prueba de composición no
implica que el mundo haya originado autónomamente sus recursos.

## Optimización y fidelidad

`DenseSequential`, `DenseParallel` y `Lazy` son agendas host para la misma
transición v27. No son observadores ni estados DEE. La validación compara RAW y
clock completos por tick; los contadores de trabajo pueden diferir. Lazy sigue
recorriendo el volumen para clocks y el postpaso, por lo que no se afirma
complejidad completamente dispersa ni ahorro energético.

La batería exacta es finita. Respalda únicamente los fixtures, trayectorias,
tamaños, configuraciones de hilos y plataforma ejecutados. No demuestra
equivalencia universal de todo microestado representable.

## Distinciones obligatorias

- `state == 0`, `raw == 0` y `clock == 0` no son equivalentes.
- Carga cero no es ausencia de portador.
- Una consulta puede transformar el mundo; sólo `observe()` es pasivo.
- Igualdad bajo un observer parcial no prueba igualdad causal completa.
- Una diferencia RAW persistente no prueba por sí sola uso funcional.
- Un fork intervenido diagnostica; su intervención no ocurrió en el mundo
  principal.
- Metadatos de catálogo, nombres de canales y manifiestos no se escriben en el
  microestado y no constituyen causalidad DEE.
- Una región declarada no crea una barrera física en el toro.

## Qué no establece

La entrega no establece consciencia, mente humana, AGI, aprendizaje universal,
autonomía indefinida, gestión automática de capacidad, ley térmica, identidad
de `s_reg` con energía, aceleración en todos los dominios, seguridad adversarial
del snapshot ni compatibilidad ABI entre toolchains no probados.

No incluye Entrega 03: no borra ni migra historia, no normaliza `s_reg`, no
incorpora supervisor adaptativo, GPU/FPGA, GUI, servidor, robot ni Rosetta
industrial.

## Cómo conservar una anomalía

Ante una divergencia, conserve estado inicial, RAW/clock esperado y observado,
backend, hilos, plataforma y primer tick discrepante. Distinga source, WHL,
fixture, preparación y protocolo. No cambie tolerancias enteras ni la ley v27
para hacer coincidir un resultado.
