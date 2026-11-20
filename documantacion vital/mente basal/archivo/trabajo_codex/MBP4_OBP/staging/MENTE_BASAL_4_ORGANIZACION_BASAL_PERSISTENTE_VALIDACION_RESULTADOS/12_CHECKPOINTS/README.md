# Checkpoints resumibles

- `OBP_FRESH_LOCKED_T0.deetsnap`: arquitectura congelada antes de evolución.
- `OBP_FRESH_VALIDATED_T32.deetsnap`: MAIN científico de MBP4.
- `../11_MBP3_INTEGRATION/tick_000000276832_...deetsnap`: padre MBP3 inmutable verificado.
- `../11_MBP3_INTEGRATION/POST_ENV_INSTALL_T0_T276832.deetsnap`: instalación declarada, sin aprendizaje.
- `../11_MBP3_INTEGRATION/MBP3_WITH_FROZEN_OBP_T276864.deetsnap`: rama histórica preservada pero no integrada funcionalmente.

La reanudación usa `dee_thinking.Runtime.load_snapshot`. No llama al constructor t0.
