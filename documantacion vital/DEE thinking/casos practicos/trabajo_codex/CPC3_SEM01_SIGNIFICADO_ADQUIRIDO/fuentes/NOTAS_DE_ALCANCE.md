# Fuentes dirigidas y alcance de recuperación

Se verificaron pasivamente CPC3, la entrega4.0, los dos DOCX4.0 y las fuentes seleccionadas CORE06/07. No se importaron ni ejecutaron runners históricos. Los originales no fueron modificados.

- El padre CPC3 tiene envolvente `CPC3/`,1563 miembros y SHA-256 `75ab357f41f6214c1798efbf69bd0708ab891038d30d770fdfe4a379208f793e`. El prompt no proporcionaba un hash esperado del CPC3; este es el corte local identificado por contenido, inventario y manifiestos. `PARENT_MEMBERS.json` conserva todos sus miembros, incluidos los manifiestos históricos.
- El ZIP de producto4.0 coincide con `DELIVERY_RECEIPT.json`. El WHL suelto y el incluido coinciden con el SHA esperado17c07745…; su PYD coincide con20d7c764… y `kernel_v27.cpp` con fbd81903…. Estos son controles de archivos; el registro de importación y ruta del runtime pertenece a las pruebas de instalación/campaña, no a esta recuperación pasiva.
- Los textos4.0 recuperados están en `textos/manual40.txt` y `textos/maestro40.txt`. Ambas cápsulas pasaron CRC y su manifiesto:72 y20 entradas, respectivamente. Se conserva completa la cápsula pequeña del Manual. Del Maestro se recuperaron manifiesto y miembros pertinentes; no se duplicó su ZIP completo de producto.
- `producto4/` contiene implementaciones, bindings, contratos y pruebas pertinentes: es la superficie publicada4.0. `NativeAssociationSession` publica relaciones móviles de una familia específica; su nombre no demuestra por sí solo una asociación arbitraria señal–consecuencia. La adquisición publicada exige su frontera inicial y no autoriza recrear una organización para simular reversión.
- `CORE06/` conserva el mecanismo de escritura/lectura por encuentros y fuentes exactas de adquisición, consultas y reversión. `CORE07/` conserva transferencia y reprogramación. Son experimentos históricos: cualquier componente utilizado ahora requiere comprobación corta bajo el WHL4.0, no sustitución por su antiguo kernel.
- `CPC3/fuentes_pertinentes/I01/` y `I02/` conservan constructores históricos de soporte, realimentación, memoria relativa y lectura renovada. `CPC3/genealogia/CP02_B/` conserva antecedentes de la línea predictiva. Se incluyen como fuentes, no como una dependencia operativa de la nueva respuesta.
- Los textos de OBP2.1 y Procesamiento Nativo se recuperaron de la genealogía CPC3; el contexto de Procesamiento Nativo también tiene procedencia verificada desde la cápsula del Maestro4.0.

`PROVENANCE.json` registra archivo origen, miembro interno, hash y clasificación de cada recuperación. La clasificación distingue publicado4.0, experimento histórico y constructor de investigación; un resultado documental no sustituye al estado, recibos o controles de SEM01.

## Actualización acumulativa preparada

`src/package_append.py` y `src/verify_append.py` no ejecutan experimentos. Copian el ZIP padre y añaden únicamente `CPC3/experimentos/SEM01_SIGNIFICADO_ADQUIRIDO/`; conservan todos los datos y el prefijo binario de los registros locales comprimidos heredados. Generan un nuevo manifiesto y HASHES dentro de esa sección, sin reescribir los de la raíz histórica.

Nueve comprobaciones sintéticas pasaron en `staging/PACKAGE_TOOLS_TEST.json`, sin tocar el CPC3 oficial. El empaquetador exige hash padre explícito; sin `--publish-atomic` no puede reemplazarlo, incluso cuando el input es una copia sellada con otro nombre. No se publicó ningún candidato científico durante esta preparación. Antes de empaquetar debe cerrarse la escritura de datos; `staging/` y caches no forman parte de la sección añadida.
