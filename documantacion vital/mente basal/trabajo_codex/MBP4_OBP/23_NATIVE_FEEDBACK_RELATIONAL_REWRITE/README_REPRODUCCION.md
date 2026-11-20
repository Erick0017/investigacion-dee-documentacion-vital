# Reproducción técnica — sección 23

Desde la raíz extraída del paquete, use el Python 3.13 donde está instalado
`dee_thinking==2.2.0`:

```powershell
python -I -B .\23_NATIVE_FEEDBACK_RELATIONAL_REWRITE\RUNNER\run_feedback_rewrite.py `
  --package-root . --validate-only
```

Para reproducir la campaña congelada en una copia aislada:

```powershell
python -I -B .\23_NATIVE_FEEDBACK_RELATIONAL_REWRITE\RUNNER\run_feedback_rewrite.py `
  --package-root . --run-campaign
```

El runner no modifica v27 ni las secciones heredadas. Las escrituras de
preparación ocurren antes de T0; después sólo avanza, observa y guarda.
`RETURN_CUT` es el control que impide atribuir al retorno la escritura B
observada en esta preparación.
