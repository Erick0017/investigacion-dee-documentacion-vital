# Registro de cambios

## Entrega 01 — 2026-10-03

### Añadido

- API pública C++ para packing, decoding y tick v27.
- Núcleo nativo derivado mecánicamente del source canónico con verificación de
  SHA-256.
- Runtime persistente con cuatro buffers, tick, pausa/reanudación, canales,
  experiencias, lotes, sondas, recibos y observación pasiva.
- Admisión en la frontera efectiva, preservación de clock, conflictos explícitos
  y ausencia de política “última escritura gana”.
- Forks independientes.
- Snapshot binario little-endian versionado, checksum, límites de lectura y
  restauración transaccional.
- Constructores de referencia para transporte, reprogramación, historia y
  recurrencia multicanal.
- Infraestructura de pruebas diferenciales contra fixtures generados por el WHL
  y regresiones de runtime.
- Consumidor C++ independiente y demostración de continuidad/restauración.
- Documentación de contrato, procedencia, alcance, pruebas y reproducción.

### Decisiones de contrato

- El producto nativo no carga Python, el WHL ni el `.pyd`.
- `state == 0` no se utiliza como criterio para descartar palabras RAW.
- El kernel mantiene el copy-back histórico; no se añade un swap.
- `observe()` es pasivo; `probe()` es una intervención explícita.
- `run_until(T)` termina antes de aplicar eventos pendientes de `T`.
- Los nombres de canales y eventos son metadatos externos y no codifican una
  respuesta en el microestado.
- Las organizaciones preparadas declaran recursos y geometría; no se rotulan
  como autonomía ambiental.

### Fuera de alcance

- Catálogo ampliado y composición de alto nivel (Entrega 02).
- Operación prolongada, gestión de capacidad y adaptadores (Entrega 03).
- GPU/FPGA, servidor, GUI, plugins, hardware o producto comercial.
- Veredictos de consciencia, mente, AGI, autonomía o equivalencia universal.

### Validación

El estado de compilación y pruebas de la copia empaquetada no se infiere de este
changelog. Consulte el informe técnico y los logs bajo `validation/` del ZIP.

