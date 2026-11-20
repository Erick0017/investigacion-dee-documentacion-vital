# Reproducción técnica — sección 24

Use el Python donde está instalado `dee_thinking==2.2.0`. Desde la raíz
extraída del paquete, el replay y los contrastes pueden reconstruirse con:

```powershell
python -I -B .\24_CONTEXTUAL_CAUSAL_MECHANISM\RUNNER\run_contextual_mechanism.py `
  --package-root . --reproduce
```

`--reproduce` escribe en una copia de la sección 24; no debe ejecutarse contra
el ZIP canónico montado como evidencia. Las intervenciones son forks
diagnósticos. El replay MAIN parte del checkpoint heredado y no recibe
escrituras del host.

La ventana binaria `LOCAL_WINDOW_120_133.u64.gz` contiene, por frame, primero
47^3 uint64 RAW y luego 47^3 uint64 clock, little-endian. Su índice JSON asocia
cada frame con tick relativo y absoluto.
