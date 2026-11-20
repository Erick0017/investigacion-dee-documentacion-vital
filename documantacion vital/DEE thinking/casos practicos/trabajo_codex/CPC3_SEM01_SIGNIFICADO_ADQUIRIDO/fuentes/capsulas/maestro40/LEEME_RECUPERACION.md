# DEE thinking 4.0.0: capsula del Documento Maestro

Autor del proyecto: Ivan Erick Tlaltecatl Morales.
Documento: DEET-MAR-400-01, edicion1.0, 14 de octubre de2026.

## Contenido preservado

Producto_oficial contiene el ZIP oficial4.0 exacto: fuente C++/Python, WHL, contratos, aplicaciones, pruebas, evidencia, snapshots y resultados. Su SHA256 es c78609a7d0d501324324408ed955f60f127965c77efbcbe3b3d04fc14dbb16cf.

Documentos_origen conserva los Word3.5 originales y dos documentos de contexto cientifico. No es la nueva edicion del Libro Blanco. Contexto conserva texto extraido de Procesamiento Nativo, con hash de su DOCX fuente y sin sus imagenes. Los originales recibidos no se modificaron.

comprobacion_editorial separa las comprobaciones nuevas de integridad y C++ Linux de las pruebas Windows originales de Codex. Criterios_editoriales identifica el uso de las conversaciones como requisitos e hipotesis.

## Verificar y extraer

Python3.11 o posterior, solo biblioteca estandar:

    py -3.13 herramientas/recuperar_maestro40.py verificar Documento.docx
    py -3.13 herramientas/recuperar_maestro40.py extraer Documento.docx recuperado
    py -3.13 herramientas/recuperar_maestro40.py verificar Producto_oficial/DEE_thinking_4_0_0_ENTREGA_FINAL_RESULTADOS.zip

El comando extraer sobre un Word recupera su capsula. Sobre un ZIP extrae ese contenedor. El destino debe ser nuevo o estar vacio. La herramienta verifica CRC y hashes y rechaza rutas inseguras; no ejecuta codigo del contenido.

Para extraer el producto:

    py -3.13 herramientas/recuperar_maestro40.py extraer Producto_oficial/DEE_thinking_4_0_0_ENTREGA_FINAL_RESULTADOS.zip producto_recuperado

Los miembros del producto expanden 1,179,024,141bytes. Reserve mas espacio para compilaciones y reproducciones. La capsula en si conserva ese producto comprimido.

## Usar o reconstruir

El WHL se encuentra dentro del producto extraido, en wheel/. Requiere Windows x64 y CPython3.13 estandar. Su fuente puede compilarse separadamente con el toolchain documentado. Los capitulos27-30 del maestro y los scripts originales describen instalacion, build y pruebas.

El documento no sustituye el snapshot de una experiencia particular. Para continuar un individuo conserve el estado fisico y la metadata operativa de su perfil.

## Integridad y edicion

CAPSULE_MANIFEST.json identifica todos los miembros excepto si mismo. Esta verificacion comprueba bytes, no valida por si sola una conclusion cientifica.

Algunos editores pueden eliminar partes personalizadas al volver a guardar un DOCX. Conserve el Word entregado y el respaldo; verifique la capsula despues de editar.
