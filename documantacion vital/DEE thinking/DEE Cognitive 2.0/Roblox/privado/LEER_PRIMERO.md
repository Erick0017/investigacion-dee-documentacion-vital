# Privado y despliegue

El instalador actual está en [instalacion](../instalacion/Instalar_Roblox.ps1) y consume el payload verificado de `dependencias/`. No depende de Cognitive externo ni del archivo histórico para una instalación ordinaria.

`consumidores_R03` conserva la adaptación de reconstrucción desde fuentes canónicas y su procedencia; no es el instalador de transferencia ni debe abrir sesiones. `localizar_runtime.py` es un localizador de la instalación local previa, no un fallback del instalador actual. Para otra computadora se exige un destino explícito nuevo. Ninguna conexión privada real se distribuye.

[Procedimiento portable R06](../documentacion/INSTALACION_TRANSFERIBLE_R06.md) · [continuidad](../documentacion/CONTINUIDAD_Y_REPRODUCCION_R06.md).
