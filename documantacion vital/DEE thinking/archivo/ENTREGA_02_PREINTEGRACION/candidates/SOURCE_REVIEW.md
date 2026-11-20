# Revisión dirigida H3/H4

## H3 — reparación funcional CORE17

Fuentes primarias consultadas:

- `CORE17/EXTENSION/RUNNERS/run_e02_redundant_policy_repair.py`, SHA-256
  `4049a7f9dd846e6a65fb86bc2a08a0c09964fa9cc3285dd99e5d126c5e055af8`.
- `run_e03_policy_repair_holdout.py`, SHA-256
  `4ed5c01ae297a733289f23d627928cc844ee741dde7803edf2e40ad7a10aee65`.
- Lock C17E03 y challenge fresco de 12 mundos del ZIP oficial CORE17.

El holdout histórico registró 12/12 para tratamiento y corte fuera de ruta, y
0/12 para copia no entrenada, dirección reseteada, copia ausente, corte de ruta
y receptor incorrecto. El mecanismo es transporte desde una copia aprendida
redundante. Las dos copias reciben experiencias de aprendizaje por separado;
no existe un evento que replique la primera para crear la segunda.

## H4 — accesibilidad Ingeniería 03–04.5/POST

Fuentes primarias consultadas:

- NRD01 discovery, runner SHA-256
  `d9c025a1b0f6c10766b6e4eaacda2957dcd6daf6a91b1a6445d8541478f63cfd`.
- NRD02 fresh, runner SHA-256
  `469ec7bf3f4499c5f522d7f38e4f21e25bcdacc253cfe1057af6f694b9913eef`.
- `U1_PILOT_01R_MATCHED_CONTROLS.json`, SHA-256
  `3000278f42e7650d8031c868a28db82d3933f760ce7f44018ff23814ac5c34b2`.
- Runner P01R, SHA-256
  `88fdb31801bbdf0e98ab2caf514461edcb3444cfa0370a4db8f4ed12a0a9af58`.
- Grafo de reachability y mapa causal transversal de Ingeniería 04.5.

NRD compara `challenge(H)-baseline(H)` entre historias, evitando confundir
mundos ya distintos con efectos de una misma consulta. POST corrige el
identificador de receptores y conserva el acoplamiento condicionado por
historia, pero no reinstancia la función ni construye competencia renovada.
Por ello H4 queda como contrato finito de observación/diagnóstico y no como
organización disponible.
