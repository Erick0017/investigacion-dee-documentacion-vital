# Identidad funcional Phi_B

El panel fue congelado antes de holdout. Una instancia pertenece a la clase funcional `E_B` cuando:

1. la recurrencia produce la dirección esperada en los 32 medios ciclos;
2. cuatro fuentes semantic=4 permanecen disponibles;
3. la primera acción esperada se expresa;
4. la recurrencia sigue disponible al agotarse la secuencia finita;
5. una perturbación off-path congelada no cambia la firma.

No se comparan microestados mediante una tolerancia elegida después de observar holdout. Los hashes RAW se conservan como diagnóstico, no como definición de identidad.

Colapso se define como pérdida conjunta de recurrencia y readiness/primera acción sin recuperación antes de tick 32. No ocurrió en los tratamientos ni holdouts.
