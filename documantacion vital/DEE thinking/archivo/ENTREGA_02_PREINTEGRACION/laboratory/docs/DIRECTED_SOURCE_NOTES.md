# Fuentes dirigidas reutilizadas

La revisión se limitó a las piezas necesarias para decidir los dos aparatos;
no se hizo un inventario del corpus.

- `ENTREGA_02_CIERRE/docs/ORGANIZATION_CATALOG.md`: contratos del catálogo,
  límite explícito de una conexión por salida física y ausencia de clonación de
  portadores.
- Durante el diseño del laboratorio, CORE05 aún figuraba en la copia de trabajo
  como deuda sin constructor/oráculo integrado; por ello no se usó como tercera
  familia. Después, en la línea técnica independiente de esta misma
  continuación, se recuperó y portó `temporal_phase_memory.core05.v1`. Ese port
  posterior no modifica retrospectivamente los dos aparatos ejecutados aquí.
- `ENTREGA_02_CIERRE/examples/composition_c6_later_query.cpp`: montaje C6
  validado de aprendizaje relacional y consulta posterior (respuesta `s_reg=25`).
- `pensamiento/PENSAMIENTO_01_DEE_V27_RESULTADOS.zip`, informe de la
  continuación `HISTORIA_NATIVA_ACTUALIZACION_ACCION_20261002`: cadenas nativas
  finitas con actualización transportada y controles de corte.
- `pensamiento/PENSAMIENTO_02_DEE_V27_RESULTADOS.zip`, informe y runner
  `run_environment_second_use.py`: segundo uso finito mediado por recursos
  preinstalados y distinción entre continuidad nativa y entrada acoplada.

Estas fuentes motivaron dos preguntas nuevas y estrechas: (1) si un producto
actualizado se dirige por contexto sin copiarse y (2) si la interfaz física C6
admite una consulta posterior sobre el mismo mundo, conservando explícitamente
la modalidad acoplada.
