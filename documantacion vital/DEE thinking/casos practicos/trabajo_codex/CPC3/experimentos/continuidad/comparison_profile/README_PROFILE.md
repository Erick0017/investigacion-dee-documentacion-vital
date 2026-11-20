# Perfil operativo de comparación

`core.comparison_entity.CentralComparisonEntity` usa el mismo Runtime MAIN
desde H0. Declara dos interfaces inertes antes de la primera experiencia; no
instala otra organización aprendida. La primera consulta física cero deja un
pronóstico nativo en37, con objetivo83. `compare()` avanza hasta83, recibe sólo
el resultado externo actual, lo codifica por un canal fijo y evoluciona v27
hasta84. El marcador se calcula por el gradiente nativo, no por una resta de
Python ni por un error inyectado.

La comparación tiene dominio finito de expectativa binaria representada:
dx±1, dz0 antes del informe. Coincidencia deja dx0 con dz no nulo; discrepancia
deja dx±1 con dz no nulo. La carga del informe es1 y su dirección/sitio sólo
dependen del resultado observado actual, nunca de la expectativa guardada.
No equivale a un comparador universal de magnitudes o a detectar una ausencia
sin un sensor externo.

El perfil admite un episodio pendiente. Rechaza un informe tardío, una
expectativa indeterminada, una experiencia interpuesta que cambie el episodio
y snapshots sin sus interfaces/metadatos. Cargar no reinstala materia.

Tras comparar, `predict()` devuelve `OUTSIDE_FORECAST_DOMAIN`: el marcador de
comparación no se presenta como otro pronóstico. `observe()` puede mostrar el
marcador físico actual en su ventana declarada. La evidencia posterior de la
prueba central muestra entradas ocupadas; no se anuncia actualización repetida
de memoria después de este encuentro.

Las23 comprobaciones de `VALIDATION.json` son validación de API/persistencia,
no23 capacidades ni nuevas réplicas científicas. Incluyen save/load con un
episodio pendiente, continuidad física al comparar, lectura pasiva, continuación,
rechazo H0, rechazo de informe tardío y rechazo de una sesión antigua sin perfil.
Las ramas restauradas se usan sólo como controles técnicos, nunca para leer o
decidir por MAIN ni para devolverle estados.

Ejemplo con el wheel3.5 oficial instalado y `CPC3/src` en `sys.path`:

```python
from core.comparison_entity import CentralComparisonEntity
e = CentralComparisonEntity.create()
e.sense()                   # dos acontecimientos pasados realmente codificados
forecast = e.predict()      # emisión37 -> objetivo83
result = e.compare()       # consecuencia83 -> comparación física84
e.save('sesion_comparacion.deetsnap')
f = CentralComparisonEntity.load('sesion_comparacion.deetsnap')
current_marker = f.observe()
not_a_forecast = f.predict()  # OUTSIDE_FORECAST_DOMAIN, sin respuesta inventada
```

El perfil de continuidad original permanece separado. No se combina su mejora
de expresión en813 con la trayectoria de comparación84 para fingir una única
genealogía que haya realizado ambas pruebas.
