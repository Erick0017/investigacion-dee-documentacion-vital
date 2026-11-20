# Observadores CORE15–17: recálculo, no nueva simulación

Los datos originales, los desafíos y los cierres quedan preservados por SHA-256. El comando `reproduccion/recalcular_observadores.py` usa sólo esos miembros materializados; no crea ningún Runtime ni utiliza resultados como memoria de un participante. Las familias amplias continúan en estado D, porque recalcular sus observaciones no equivale a repetir sus experimentos.

## Datos y cálculos

- CORE15: 48/48 positivos y44/48 canarios discriminantes. Los cuatro fallos de C15XC02 permanecen identificados individualmente. Una retirada temporal no cambia el observable de suma ya saturada; eso limita el canario, no demuestra ausencia de toda función temporal.
- CORE16: 24/24 mundos y118pasos del operador concuerdan en RAW/clocks; 32/32 transferencias,6/6 guardas y6/6 regeneraciones satisfacen sus criterios originales. Las576ramas observadas coinciden con una ley determinista, y7/8 pares de medidas cambian su distribución. Las24composiciones AB/BA no conmutan en el dominio probado; eso no acredita física cuántica ni no localidad.
- CORE17: el operador reducido conserva diez mundos/406pasos, con416filas de traza al incluirT0. No hay diferencias RAW/clocks en esas filas. La reparación funcional se observa en12/12 brazos de tratamiento y12/12 controles fuera de ruta, frente a0/12 en cada uno de cinco controles de fuente, dirección, ruta o receptor.

El campo histórico `fresh_worlds=12` de la reparación designa doce casos base de desafío. El archivo contiene84ejecuciones y84seeds distintas, una por brazo y caso. No son doce ejecuciones totales, ni microestados iniciales o coordenadas idénticos entre brazos. El recálculo informa ambos denominadores sin cambiar los datos originales.

## Fórmulas explícitas

`n_aprobados = suma(indicador(criterio_fila))`; `n_total = número de filas del grupo`.

`discrepancias = suma(discrepancias_por_paso)`; además se comprueba igualdad de cada par de hashes primarios cuando se dispone de ellos.

Para reparación se agrupa por `mode`, se cuentan `fresh_function_after_reconstruction == true` y se reconcilia el total con los doce desafíos y sus siete brazos. Los416registros de factor no se cuentan como416transiciones: diez corresponden al estado inicial.

## Alcance

Se comprueban integridad, denominadores y congruencia interna de esos datos históricos. No se demuestra una nueva adquisición de E1, una correspondencia con nuestro universo ni reproducción independiente del motor. Las fuentes originales y sus limitaciones siguen siendo parte de la genealogía; no se ocultan porque esta campaña priorice funciones semánticas.
