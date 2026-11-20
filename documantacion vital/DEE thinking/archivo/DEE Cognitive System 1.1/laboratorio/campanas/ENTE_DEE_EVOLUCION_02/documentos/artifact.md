# Contrato editorial del Manual Maestro ENTE02

## Autoridad y referencia conservada

Se actualizará la edición documental 1.10 ENTE01 conservada en la raíz original de DEE Cognitive System 1.1. Sus bytes son 107328 y su SHA256 es `c9b962d1efa14145b6c7d93d3695892475dc4ca0ba52c66731c86b07de33abf5`. La edición 1.11 no cambia la versión de Cognitive, thinking ni Universe. El resultado estará en esa misma raíz; la distribución lo incorporará mediante su actualizador, no mediante una segunda autoría.

El destinatario es un colaborador investigador que necesita saber qué puede ejecutar, con qué entradas, desde qué vida y con qué asistencia. Primero se explicará la función utilizable y la continuidad; después sus resultados y límites. No se publicará código ni reglas de reconstrucción del kernel.

## Lectura y fidelidad

Se leyeron portada y control documental, índice, perfiles y capítulos 19, 26 y 27 completos, con encabezado y pie, directamente del OOXML 1.10. Se conserva una sección A4 vertical, primera página distinta, márgenes top 1134, right 1077, bottom 1020, left 1162 twips y header/footer 482 twips. Se conservan estilos, tablas, relaciones, geometría, medios y campos PAGE/NUMPAGES. El índice estático usa TOCline y no tiene páginas que puedan actualizarse falsamente sin render. Los capítulos 26 y 27 y todos los apéndices permanecen como historia íntegra.

La comparación por miembros garantizará la preservación byte por byte de todas las partes salvo document.xml, header1.xml, footer1.xml y core.xml. Se compararán además la sección, campos y texto de capítulos históricos y apéndices.

## Sitios que pueden modificarse

Portada y control de edición; corte real y fuente; nota de autoridad que remite al capítulo 28; perfiles de investigación directa; identidad de versión en capítulo 19 y registro de cambios; encabezado y pie conservando sus campos; propiedades documentales. Se añadirá el capítulo 28 y su entrada estática antes del apéndice A. El cuerpo nuevo utilizará estilos existentes Heading1, Heading2, Heading3, Normal, Code, Source y Small.

El contenido de ENTE02 distinguirá información relevante de canales y tasa; usos nuevos de reutilización demostrada; transferencia isomorfa de abstracción entre tareas; dos políticas conservadas de un solo acumulador que se modifica; regulación preparada de selección aprendida. Las cifras sólo entrarán tras recibir el corte final aprobado y sus primarios. La capacidad de ocho variables no se declarará reutilizable por un solo éxito exploratorio.

## Puerta de autoría

Durante la preparación no se modifica Word ni se ejecuta el marcador EDIT. El editor exige el archivo de resultados con estado FINAL_RESULTS_APPROVED_FOR_MANUAL. Inmediatamente antes de la primera autoría se ejecutará exactamente una vez el marcador de operación edit del bundle. No se sobrescribe ninguna edición existente.

## Render y entrega

Se usará el Python y Node del bundle 26.1011.51657 resuelto por load_workspace_dependencies. El renderizador será el canónico render_docx.py con PATH limitado al bundle y timeout de 50 segundos. No se utilizará LibreOffice desktop del usuario ni se instalará otra plataforma. Si el bundle sigue sin soffice.exe se conservará el error exacto, la edición se identificará SIN_VALIDACION_VISUAL y no se afirmará que hubo inspección de páginas. La comprobación estructural no sustituye la visual.

No se modifican sistema/, snapshots, vidas, motor ni original protegido desde esta tarea. No se ejecuta ningún tick. El archivo final será una modificación real del Word, no un addendum presentado como reemplazo.
