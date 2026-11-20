# Alcance científico y límites de interpretación

## Qué implementa esta entrega

DEE thinking Entrega 01 implementa una herramienta experimental nativa para:

- evolucionar el estado completo `(RAW, clock)` con la regla v27;
- mantener el mismo mundo entre interacciones;
- aplicar experiencias o sondas por canales declarados;
- observar sin intervención;
- comparar ramas independientes;
- persistir una frontera y comprobar su futuro restaurado;
- ejecutar organizaciones de referencia con controles causales acotados.

Esto permite formular resultados como operaciones medibles: una entrada fue o
no admitida, un registro cambió, una relación quedó disponible en una consulta,
un corte alteró una trayectoria, o una continuación restaurada reprodujo RAW y
clock.

## Familias E1–E4

### E1 — Transporte e integración

Portadores preparados recorren el toro y encuentran destinos mediante la regla
v27. La familia distingue carga cero de ausencia e incluye destino ocupado.
Mide transporte, admisión e interacción; no implica por sí sola aprendizaje.

### E2 — Reprogramación

Una secuencia de interacciones escribe/modifica una relación de un linaje y una
consulta posterior usa el estado resultante. El control omite el enlace de
escritura. El aparato implementa una capacidad acotada, no aprendizaje
universal ni lectura no destructiva.

### E3 — Historia y respuesta

Preparaciones HA/HB contienen inventario comparable con orden temprano/tardío
intercambiado. Se examinan a edad común y con consulta común. Una diferencia
indica dependencia del estado histórico presente; no contradice el determinismo
de la regla ni exige una variable de historia externa a `(RAW, clock)`.

### E4 — Recurrencia multicanal

Contribuciones A/B/C preparadas interactúan con un paisaje histórico y recursos
persistentes. Un corte declarado contrasta el enlace causal. El alcance es una
recurrencia finita y abastecida; no constituye cierre ambiental indefinido ni
creación autónoma de recursos.

Los resultados numéricos sólo deben citarse después de ejecutar los tests y
consultar `validation/`. Los contratos de los constructores no son resultados
por sí mismos.

## Distinciones obligatorias

- `raw != 0` (soporte) no equivale a `state != 0` (ocupación).
- `s_reg == 0` en un portador no equivale a ausencia del portador.
- El avance común de clock no constituye por sí solo actividad adaptativa.
- Una diferencia microscópica persistente no implica uso funcional.
- Igualdad bajo un observer parcial no implica igualdad causal completa.
- Igualdad completa de `(RAW, clock)` bajo el mismo protocolo sí fija el mismo
  futuro determinista.
- Una sonda sobre el mundo es una intervención; una observación pasiva no lo es.
- Una consulta física puede alterar el estado y no se rotula como lectura no
  destructiva.
- Un fork intervenido diagnostica capacidad o causalidad; su evento no ocurrió
  en el mundo principal.
- Una geometría, fuente o recurso preparado se declara como tal y no se atribuye
  a generación autónoma del mundo.

## Lo que no demuestra Entrega 01

Esta entrega no establece:

- consciencia, mente, AGI o pensamiento en sentido humano;
- autonomía indefinida, autopoiesis o sostenibilidad ilimitada;
- memoria de capacidad infinita o gestión automática del cap;
- una ley térmica, identificación de `s_reg` con energía o termodinámica
  completa;
- generalización universal de un aparato;
- equivalencia universal entre el núcleo derivado y todo estado posible v27;
- funcionamiento en tiempo real, aceleración o portabilidad no medida;
- seguridad del snapshot frente a adversarios;
- control robótico, actuadores, servidor, interfaz gráfica o producto
  comercial.

Tampoco convierte metadatos del runtime en causalidad DEE. Nombres de canales,
ids de eventos, recibos y fases de protocolo no se escriben en el microestado.

## Relación con futuras entregas

Entrega 02 queda reservada para ampliar el catálogo de organizaciones y sus
contratos de composición, apoyándose en evidencia concreta. Entrega 03 queda
reservada para operación prolongada, capacidad, adaptadores y mantenimiento.

Esta Entrega 01 no exporta stubs de esas capacidades. Una ampliación futura
debe distinguir cambios de constructor/protocolo de modificaciones de la regla
v27.

## Cómo reportar una anomalía

Ante una divergencia entre biblioteca, WHL o telemetría:

1. preserve estado inicial, RAW/clock esperados y obtenidos;
2. registre plataforma, compilador, tamaño y tick del primer desacuerdo;
3. verifique versión, packing, convención temporal y admisión de eventos;
4. reduzca el caso sin cambiar el resultado de referencia;
5. no relaje una comparación exacta ni modifique el original para hacerla pasar.

Una anomalía reproducible puede ampliar la interpretación científica, pero no
autoriza alterar el kernel congelado dentro de esta entrega.

