# Entrega CPC9 y DEE Cognitive Core

Dos ZIP privados verificados. Las partes son segmentos binarios; no se abren por separado. Cada archivo de transferencia mide como máximo16.000.000bytes.

## Leer primero

[Lectura inicial](LEER_PRIMERO.md) · [Conclusiones](CPC9_CONCLUSIONES_Y_PENDIENTES.md) · [20 respuestas científicas](CPC9_INFORME_TRANSVERSAL_FINAL.md) · [Verificación final](VERIFICACION_FINAL.json)

## Partes para descargar

### DEE_COGNITIVE_CORE_CPC01_A_CPC08.zip

Comprimido: 73,601,685 bytes. Expandido: 95,481,181 bytes.
SHA-256: `412a6819e36203a0086790003301a13722bd14fd3a3213b03681d827f7cca1a2`.

- [Parte001](DEE_COGNITIVE_CORE_CPC01_A_CPC08.zip.001) — 14,720,337 bytes.
- [Parte002](DEE_COGNITIVE_CORE_CPC01_A_CPC08.zip.002) — 14,720,337 bytes.
- [Parte003](DEE_COGNITIVE_CORE_CPC01_A_CPC08.zip.003) — 14,720,337 bytes.
- [Parte004](DEE_COGNITIVE_CORE_CPC01_A_CPC08.zip.004) — 14,720,337 bytes.
- [Parte005](DEE_COGNITIVE_CORE_CPC01_A_CPC08.zip.005) — 14,720,337 bytes.

[ZIP canónico completo](DEE_COGNITIVE_CORE_CPC01_A_CPC08.zip) (opcional; supera el límite de transferencia).

### CPC9_ONTOGENIA_SEMANTICA_NATIVA65_RESULTADOS.zip

Comprimido: 65,870,122 bytes. Expandido: 722,011,116 bytes.
SHA-256: `917a559b917388fc63a6948762d73c3e87a00c30199c5b65c635a8d39bf96bad`.

- [Parte001](CPC9_ONTOGENIA_SEMANTICA_NATIVA65_RESULTADOS.zip.001) — 13,174,025 bytes.
- [Parte002](CPC9_ONTOGENIA_SEMANTICA_NATIVA65_RESULTADOS.zip.002) — 13,174,025 bytes.
- [Parte003](CPC9_ONTOGENIA_SEMANTICA_NATIVA65_RESULTADOS.zip.003) — 13,174,025 bytes.
- [Parte004](CPC9_ONTOGENIA_SEMANTICA_NATIVA65_RESULTADOS.zip.004) — 13,174,025 bytes.
- [Parte005](CPC9_ONTOGENIA_SEMANTICA_NATIVA65_RESULTADOS.zip.005) — 13,174,022 bytes.

[ZIP canónico completo](CPC9_ONTOGENIA_SEMANTICA_NATIVA65_RESULTADOS.zip) (opcional; supera el límite de transferencia).

## Reunir y comprobar

Descargue todas las partes del paquete elegido junto con [PARTES.json](PARTES.json) y [REUNIR_ENTREGA.py](REUNIR_ENTREGA.py). Ejecute `python REUNIR_ENTREGA.py`; el script verifica tamaño y SHA de cada parte y del ZIP. No sobrescribe un archivo diferente.

La unión/publicación atómica usa enlaces físicos: el destino debe admitirlos (NTFS probado). Si su unidad no los admite, elija otra carpeta mediante `--out`. Las instrucciones están en [INSTRUCCIONES_PARTES.txt](INSTRUCCIONES_PARTES.txt).

[Manual de recuperación](DEE_COGNITIVE_CORE_MANUAL_RECONSTRUCCION.md) · [Matriz68filas](CPC01_A_CPC09_MATRIZ_CAPACIDADES.csv) · [Compresión y pérdidas](INFORME_COMPRESION_Y_PERDIDA_DE_INFORMACION.md) · [NSM65](NSM65_EVIDENCIAS.json)

Tiempo total y límite original: véase VERIFICACION_FINAL.json, escrito como última señal de cierre; pruebas finitas, sin simulaciones propias pendientes.

La lectura en teléfono no requiere reconstruir losZIP. Para ejecutar el motor se necesita Windowsx64/CPython3.13x64; el Core declara NumPy2.2.6 sólo para CORE06/07.
