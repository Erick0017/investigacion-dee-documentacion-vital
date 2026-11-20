# Motor de la entrega DEE Cognitive 2.0

Abra ABRIR_DEE_COGNITIVE.bat en la raíz completa y elija la opción de sistema. Se incluye CPython 3.13 x64 ya preparado y la instalación local del WHL oficial thinking 4.5.0, que utiliza Universe v27. El inicio no instala, descarga ni recompila nada. No depende de Python ni de la caché de Codex de otra carpeta.

La biblioteca nativa requiere el runtime C++ de Microsoft. Si Windows informa que falta MSVCP140.dll u otra DLL del runtime, utilice el instalador firmado VC_redist.x64.exe incluido aquí; puede requerir permisos de administrador. No se ejecuta automáticamente.

Para las otras opciones del menú, Windows necesita un reproductor MP4 H.264/AAC y un lector DOCX. Estos programas de Windows no forman parte de DEE.

Los paquetes numéricos y del entorno externo conservados en sistema/runtime pertenecen a funciones históricas auxiliares. Esta entrega comprueba la aplicación y la vida seleccionada; no anuncia como verificadas aquí todas las campañas opcionales ni incorpora Python 3.12. La identidad y los orígenes de las dependencias se conservan en DEPENDENCIAS_DISTRIBUCION_ORIGEN.json.
