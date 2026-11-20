# Contrato editorial del Manual Maestro ENTE_DEE_OPERATIVO_01

## Referencia retenida y autoridad

La edición de referencia es `DEE_Cognitive_System_1_1_Manual_Maestro_Continuidad_Edicion_1_9_CF01_SIN_VALIDACION_VISUAL.docx`, en la raíz del proyecto original. Tiene 102787 bytes y SHA256 `a48eb2c28d26ce7162a851800e98d2fff82775a672aa3cd64cc62ec4f338269e`. Se conserva intacta. El resultado será una edición documental 1.10, no una versión nueva de Universe ni de thinking. El estado completo y los contratos operativos prevalecen sobre las descripciones históricas.

El texto completo de la referencia, incluidas tablas, encabezado y pie, fue extraído a `textos/`. La extracción conserva los tokens OMML en orden, pero no acredita su presentación visual ni aplica OCR a imágenes. Las partes y hashes están en `INDICE_FUENTES_EXTRAIDAS.json`.

## Diseño que se conserva

Una sección A4 vertical; márgenes izquierdo 0.81, derecho 0.75, superior 0.79 e inferior 0.71 pulgadas; primera página diferente. Se mantienen estilos, numeración, tablas, relaciones, medios y partes no afectadas. El índice estático usa `TOCline` y no contiene páginas inventadas. El pie conserva los campos PAGE y NUMPAGES. No se aplica una plantilla genérica ni se modifica el tamaño de página.

## Modificaciones previstas

- Portada y control documental: edición 1.10, corte real final, vida operativa nueva y predeterminado protegido.
- Nota de autoridad: el capítulo 27 distingue el resultado de esta campaña del antecedente CF01; no reescribe los resultados anteriores.
- Índice estático: añadir 27 antes de los apéndices sin asignar páginas no renderizadas.
- Referencias vigentes de capítulos 5 y 19: incluir la continuación real y separar versión de software, protocolo y edición documental.
- Nuevo capítulo 27: anatomía, padre, contenido heredado, aprendizaje producido por consecuencias observadas, asistencia instrumental, resultados y controles positivos y negativos, vida continuable y comandos reales. Sólo se redactará con resultados finales aprobados.
- Encabezado, pie y propiedades: nueva identidad documental; se mantienen los campos dinámicos y su solicitud de actualización.
- Los capítulos 1–26 y los apéndices conservan su función histórica. Los límites de CF01, incluido el retorno nativo que continuaba con actuador externo anulado, no se convierten retrospectivamente en un bucle externo validado.

## Puerta de autoría

No se edita el Word ni se ejecuta el marcador EDIT durante esta preparación. El editor exige un JSON con estado `FINAL_RESULTS_APPROVED_FOR_MANUAL`. Al recibir autorización final del agente principal se ejecutará el marcador EDIT exactamente una vez inmediatamente antes de la primera operación de autoría Word. No se modificará `sistema/`, la vida principal, snapshots, ni el motor desde esta tarea documental.

## Comprobación

Se verifican CRC y XML, identidad y preservación de la referencia, mismos miembros, estilos y relaciones no alterados, campos y sección conservados, capítulos e índice en orden, texto vigente y hashes finales. El intento de render utilizará sólo el Python y las herramientas del bundle anunciadas por `load_workspace_dependencies`, nunca la instalación desktop de LibreOffice del usuario. Si no existe un renderizador autorizado, se conserva el error exacto y se declara que la comprobación visual está pendiente; el Word actualizado no se sustituye por Markdown ni por un PDF artificial.

## Entrega

El Word 1.10 quedará en la raíz original junto a las ediciones conservadas. El actualizador existente copiará la edición vigente a la raíz de `cognitive sistem` como parte del cierre del agente principal. `CAMBIOS_MANUAL.md` y la verificación JSON de esta carpeta identificarán cambios, resultados autorizados, hashes y alcance de la revisión editorial. La edición no divulgará código ni reglas internas de v27.
