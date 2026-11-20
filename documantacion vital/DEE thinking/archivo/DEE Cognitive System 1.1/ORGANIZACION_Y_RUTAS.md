# Organización definitiva — 26 de octubre de 2026

Esta carpeta es la fuente principal completa de DEE Cognitive System 1.1. Procede del traslado íntegro de `casos practicos/trabajo_codex/DEE Cognitive System 1.1`; no es una reconstrucción de entes ni una fusión de snapshots.

La estructura solicitada es `4.5`, `DEE Cognitive System 1.1` y `archivo`. Las versiones 2.2.0, 3.0, 3.5, 4.0 y las carpetas raíz `trabajo_codex` y `4.5/trabajo_codex` se conservaron bajo `archivo/estructura_anterior_20261026`, con sus nombres y subárboles. El `archivo` preexistente permanece intacto. El producto oficial de thinking permanece en `../4.5/DEE_thinking_4_5_0`.

**Excepción pendiente:** Windows deniega el renombrado de `../casos practicos`, incluso con ejecución autorizada y desde otro proceso. Por seguridad se conserva allí su contenido histórico y su distribución colaboradora; la raíz tiene por ahora una cuarta carpeta. No se borró ni se forzó su vaciado. No se atribuye el impedimento a un proceso concreto sin evidencia suficiente. El sistema principal sí salió completo de esa carpeta y fue comprobado en su ubicación nueva. El mapa de traslado incluye destinos propuestos; el comprobante de conservación identifica qué origen permaneció sin mover.

## Uso actual

Abra `INICIAR.bat` para ver los comandos. No crea una vida ni modifica el activo al mostrar la ayuda.

```bat
INICIAR.bat usar --nueva MI_COPIA
INICIAR.bat usar --vida MI_COPIA
INICIAR.bat gestor estado
INICIAR.bat gestor --help
```

`--nueva` importa explícitamente una copia completa del par seleccionado APD03_MAIN T604825. `--vida` continúa la misma copia ya guardada. Las consultas materiales pueden modificar esa copia. No use otra identidad ni `--nueva` para aparentar continuidad. La terminal admite `estado`, `reanudar`, operaciones del contrato, `guardar`, `detener` y `salir`.

El lanzador nuevo sólo delega al gestor y a la entrada existentes. Usa CPython 3.13 x64 incluido en `motor/python313`, verifica el WHL oficial de `sistema/runtime` y, si hace falta, lo extrae localmente sin red, pip ni compilación. Mantiene OriginalBackend y el almacén `sistema/estado`. No copie aquí `actualizaciones/arrancar.py` de la distribución: seleccionaría otro backend y otra ubicación de vidas.

## Vidas y estados preservados

- Activo protegido: MA_MAIN_R9, N26, T230379. El traslado no lo promueve, consulta ni avanza.
- Opción operativa más reciente acreditada: APD03_MAIN, N67, T604825, descendiente de APD02_MAIN T548407. Está disponible mediante importación de copia completa, no mediante enseñanza desde T0.
- El par indispensable está en `sistema/estado/fuentes_emparejadas/APD03_MAIN_T604825_R01/`. Incluye snapshot, SQLite, interfaces, resultados, colas y progreso del protocolo. No lo sustituya por un snapshot aislado.
- Las vidas y futuros adversos históricos permanecen separados. La prueba de reubicación crea sólo REORG_APD03_01; no convierte sus experiencias en recuerdos de APD03_MAIN.

La comprobación real alcanzó REORG_APD03_01 T609662, N67, con dos propietarios consecutivos y una sola importación. Reabrió el mismo RAW/clocks antes de una nueva entrada; conservó el panel heredado y produjo el archivo27 para el objetivo18+9. No hubo reenseñanza ni cambio del activo. Puede continuar esa copia con `INICIAR.bat usar --vida REORG_APD03_01`; se conserva como prueba operativa, no como promoción científica de una nueva arquitectura.

El Manual Maestro vigente sigue siendo la edición documental 1.17 APD03, conservada byte por byte en esta raíz. Su falta previa de validación visual no se resuelve ni se disimula por este traslado. Los dos DOCX originales solicitados de thinking 4.5 no fueron localizados; el comprobante de búsqueda se conserva en `../4.5/BUSQUEDA_MANUALES_45.json`. No se sustituyeron por textos de otra versión.

## Referencias históricas y dependencias

Los absolutos antiguos en informes, recibos, VIDA.json y SQLite son procedencia histórica. No se reescribieron estados físicos ni diarios para hacerlos parecer producidos en la nueva ruta. Las referencias operativas de Store y del par APD03 son relativas y se conservan. El mapa exacto de traslado está en `evidencia/reubicacion_20261026/MAPA_TRASLADOS.json`.

El entorno CPython 3.13 previamente instalado en `tests/_dcs11_env_20261020_002458` sigue disponible, pero el inicio nuevo no depende de él. También se conserva Python 3.12 portable en `motor/python312`. El contrato de hábitat externo mantiene su Python 3.12 previamente verificado en la caché de Codex, fuera de la raíz trasladada; su ubicación no cambió. No se sustituyó silenciosamente ese contrato ni se repitió el experimento del péndulo.

La distribución `cognitive sistem`, sus entregas y su actualizador permanecen históricos en `../casos practicos/trabajo_codex/cognitive sistem`, debido al bloqueo indicado. Su actualizador conserva supuestos de rutas antiguos: no ejecutarlo contra la fuente nueva sin adaptar explícitamente origen y destinos. No se generó un ZIP nuevo para disfrazar los ZIP históricos como posteriores al traslado.

Los comprobantes distinguen conservación N0 y pruebas físicas sobre una copia. El inventario de traslado comprueba presencia, tamaño y fecha de contenido de todos los archivos; la comprobación criptográfica adicional cubre código/configuración, metadatos de vidas y par APD03. No equivale a volver a ejecutar todas las campañas científicas.
