# Incorporación operativa acotada R1

Se incorporó `ACCESO_NATIVO_BASAL_MUFI01` al mismo gestor y catálogo de Cognitive1.1 después del cierre del servicio persistente, sin modificar MU_MAIN, el predeterminado, el kernel ni el motor oficial.

Tres mundos completos de T30957 conservan sus genealogías separadas y permanecen listos antes de usar: `MUFI_ACCESO_BASAL_T_READY`, `MUFI_ACCESO_BASAL_H_READY`, `MUFI_ACCESO_BASAL_T_GAMMA_MINUS_READY`. Admitir sólo agrega metadatos de contrato; no enseña ni avanza ticks.

Uso real verificado:

```text
bifurcar MUFI_ACCESO_BASAL_T_READY COPIA_DE_TRABAJO
unificada-acceso-usar --vida COPIA_DE_TRABAJO --detalle
guardar --vida COPIA_DE_TRABAJO
unificada-acceso-estado --vida COPIA_DE_TRABAJO
```

La comprobación ejecutada utilizó `MUFI_ACCESO_BASAL_T_USO_OPERATIVO_01`, no las referencias READY: consulta31046, lector fijo de todos los12puertos31092, resultado único gamma+, futuro real guardado T31095, estado recargado en otro proceso. Un segundo uso devuelve error y conserva exactamente RAW, clocks y tick del futuro ya consumido. ACTIVO y las tres referencias READY quedaron intactos. Los15recibos de operación y los primarios del único uso viajan completos; el recálculo portátil no ejecuta DEE.

Alcance: perfil auxiliar de un solo uso material y destructivo. El contenido y el selector dependen de las historias físicas propias; la consulta basal, los suministros y el momento de iniciar son preparación externa P0. No demuestra iniciativa nativa, política general aprendida, P2/R2 ni acceso repetible estable. Los controles científicos originales, incluidos no-query y corte con sham, permanecen en MECANISMO/EVIDENCIA/acceso_nativo_b; esta comprobación no los repite.

Los snapshots completos siguen locales, con localizadores y SHA en `RESULTADO.json` y `ESTADOS_COMPLETOS_LOCALES.json`. Este suplemento compacto no permite continuar las vidas por sí solo.
