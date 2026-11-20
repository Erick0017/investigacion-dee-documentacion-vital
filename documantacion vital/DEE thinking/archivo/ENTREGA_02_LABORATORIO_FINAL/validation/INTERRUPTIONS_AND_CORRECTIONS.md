# Interrupciones y correcciones de instrumentación

1. La primera calibración DenseSequential se interrumpió sin producir un
   resultado científico: el coste observado no era adecuado para explorar el
   panel N=127. Se sustituyó por Lazy para exploración y DenseParallel para
   cuatro confirmaciones. No se mezclaron salidas de la corrida interrumpida.

2. En el primer piloto F2, el sesgo usó aproximación `(-1,0,0)` y cruzó el
   soporte preparado en `environment+(1,0,0)`. El sesgo no alcanzó el receptor:
   `environment(t38)=4149`, `overflow_total=0`. El archivo
   `results/exploratory/pilot_route_blocked_results.json` conserva ese caso.

3. Se cambió únicamente la ruta del sesgo a `(0,-1,0)`, que no cruza ninguno
   de los seis soportes. El piloto corregido produjo
   `environment(t38)=19664` y un overflow. El kernel, las constantes, el
   soporte, el reloj objetivo y los demás brazos permanecieron sin cambios.

