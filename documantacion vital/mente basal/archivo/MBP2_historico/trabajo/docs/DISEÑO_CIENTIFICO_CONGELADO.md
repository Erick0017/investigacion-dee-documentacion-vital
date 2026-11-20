# Diseño científico congelado antes de la campaña principal

## Organización basal común

- `O_expuesto`: `(10,10,63)`, `state=1`, `s_reg=11`, `dir=(+1,0,0)`,
  `semantic=1`.
- `O_referencia`: `(10,80,100)`, `state=1`, `s_reg=17`,
  `dir=(+1,0,0)`, `semantic=1`.
- clocks completos iniciales: cero.

No se instala una asociación de evaluación ni un teacher. La copia exacta de
esta preparación entre A/B/C es control experimental, no replicación nativa.

## Inventario B/C

- E1: `s_reg=2`, fuente `(26,121,z)`, `dir=(0,+1,0)`; B usa `z=63`, C
  usa `z=66`.
- E2: `s_reg=3`, fuente `(90,27,63)`, `dir=(0,-1,0)`; idéntico en B/C.

En B, O y E1 proponen el mismo destino en t16: resulta `s_reg=13` y
`dir=(+1,+1,0)`. Esa nueva trayectoria coincide con E2 en t80: resulta
`s_reg=16` y vuelve a `dir=(+1,0,0)`. En C no ocurre E1 y O nunca accede a
E2. La predicción se deriva de las propuestas físicas y se contrasta con RAW,
clock, dirección y carga; no se escribe como resultado.

## Lectores y consultas congeladas

El lector principal sigue la trayectoria prevista y cae a un barrido global
de candidatos si esa predicción falla, registrando ambigüedad. No escribe IDs
en el mundo.

- Q_XY: dos portadores genéricos de cargas 7 y 5 en direcciones `+y` y `-y`.
- Q_XZ (reservada): cargas 4 y 6 en direcciones `+z` y `-z`.

Ambas se preparan desde el checkpoint en forks aislados junto a un fork de la
misma historia sin consulta. Las respuestas son transformativas y no se
reincorporan al linaje principal.

## Alcance

El montaje mide contacto efectivo, modificación histórica, retención y uso
posterior bajo dos lectores. Una suma física simple puede ser funcional; no se
la denomina automáticamente aprendizaje. La campaña no prueba una regla
general de adquisición, inteligencia o consciencia.

