# Ruta operativa corta en Windows

En R06, RUNTIME_SOURCE en ruta larga falló antes de Store. El despliegue SHORT completó import0 con prefijo físico/causal igual y 0 ticks. Ese fallo de carga no mide la inteligencia de DEE.

Para extraer el runtime privado autorizado, el propietario debe elegir una raíz corta, por ejemplo C:\DEE_SDK. El KIT compartible no contiene ese runtime. Las fuentes originales pueden permanecer aparte; no mueva un runtime activo ni otra vida para corregir una ruta.

Use el despliegue y manifiesto autorizados del runtime completo. No copie sólo RAW/relojes ni elimine dependencias. No se presupone que longpaths del registro arregle el cargador DLL/PYD. Este preflight no modifica el registro.

pruebas/preflight_rutas_EXT_R06.py inspecciona sólo las rutas explícitas de PYD, Python y lanzador. No importa Native, carga DLL, crea Store, conecta red ni inicia procesos. 240 unidades UTF-16 es sólo una advertencia de longitud, no garantía de carga. El operador debe hacer después el preflight real autorizado.

Ejemplo FS, reemplazando las rutas relativas por las del manifiesto privado efectivo:

```text
<python autorizado> pruebas/preflight_rutas_EXT_R06.py --runtime-root C:\DEE_SDK --native-pyd <ruta_relativa_al_native.pyd> --python <ruta_relativa_python.exe> --launcher <entrypoint_EXT_relativo>
```

El entrypoint EXT procede de su fuente privada congelada. No se inventa un lanzador que busque otra carpeta del laboratorio. Si falta, se informa FALTANTE y no se abre Native. La extensión pública no arranca procesos.
