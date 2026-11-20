# DEE thinking — Entrega 03, primera etapa

Laboratorio aislado sobre DEE thinking 2.2.0 y el kernel DEE v27 congelado.
La biblioteca publicada no se modifica. El runner C++ construye un mundo
compartido donde cuatro coincidencias ambientales pueden modificar un único
portador, revisar un linaje móvil y afectar dos consultas posteriores.

El resultado oficial de esta etapa es descriptivo y acotado. No publica un
catálogo nuevo ni afirma aprendizaje universal, consciencia o autonomía.

Contenido principal:

- `src/native_environment_learning.cpp`: constructor, ejecución, telemetría y
  reanudación;
- `configs/environmental_learning_v1.json`: contrato y predicciones congeladas;
- `results/panel_final`: panel de tratamiento, dosis, controles y holdout;
- `checkpoints/learned_dose4_t40.deetsnap`: estado tras la experiencia y antes
  de la consulta reservada;
- `docs/SCIENTIFIC_REPORT.md`: interpretación de las mediciones;
- `docs/REPRODUCIBILITY.md`: compilación y recorrido reproducible.

