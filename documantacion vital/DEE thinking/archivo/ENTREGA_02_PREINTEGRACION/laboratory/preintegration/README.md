# Laboratorio focal de preintegración

Este árbol contiene evidencia experimental acoplada y no amplía el catálogo
estable. Un mismo `Runtime` recibe entrenamiento a `t=0` y tres consultas
externas admitidas en `t=6,40,74`, sin reset. Los readouts son `t=11,45,79`.

El brazo intacto y el sham producen `s_reg 25→38→51`. El corte físico aplicado
en `t=27` produce `25→13→13`. Por tanto, los productos observados en `t=11` y
`t=45` participan después en usos físicos del mismo aparato. El producto final
de `t=79` no tiene otro uso medido dentro del horizonte.

La prueba separa admisión y efecto: todas las consultas y el soporte común se
aplican en los tres brazos. El sham iguala los readouts declarados, no el estado
global completo. La ejecución es `ACOPLADA`; consultas y soporte de fase son
entradas del host. No se atribuyen aprendizaje nuevo, autoenseñanza, autonomía,
fan-out, generalización ni sostenibilidad indefinida.
