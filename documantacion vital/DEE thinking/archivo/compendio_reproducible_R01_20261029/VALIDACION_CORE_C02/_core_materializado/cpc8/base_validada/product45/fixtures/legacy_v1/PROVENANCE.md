# Snapshot legacy v1

`pending_event_v1.deetsnap` fue escrito por la biblioteca Release extraída de
`DEE_thinking_ENTREGA_01_RESULTADOS.zip`, no por el escritor v2.

- SHA-256 del ZIP Entrega 01 usado:
  `e263f27243e73cb8f348319ecfe858310cb1ff8e4b137bbe014b99429dc16661`
- SHA-256 del snapshot:
  `3d770caad476e655e4121f96c964a6c03909e592bcf05ce207a5065dd6bae531`
- frontera guardada: `t=1`
- evento pendiente: probe solicitado para `t=5`
- recibos presentes: dos

El generador C++ y el comando de enlace contra Entrega 01 se conservan en
`tools/generate_legacy_v1_pending.cpp` y `tools/build_legacy_v1_fixture.cmd`.
La prueba de integración carga este archivo, no inventa metadatos ausentes y
compara el futuro completo RAW+clock con una continuación equivalente.
