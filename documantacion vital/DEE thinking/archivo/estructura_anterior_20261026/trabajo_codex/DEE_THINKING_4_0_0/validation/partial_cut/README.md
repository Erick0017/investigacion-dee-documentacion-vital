# DEE thinking 4.0.0

Proyecto DEE Universe / INVESTIGACION DEE. Autor: Ivan Erick Tlaltecatl Morales.
Windows x64, CPython 3.13 estándar, C++20; kernel DEE v27 conservado.

ESTADO DE ENTREGA: PARTIAL — producto candidato compilado y pruebas dirigidas
conservadas; no es RELEASE_VERIFIED. El deadline venció durante la espera de un
permiso del sistema. No se ejecutó BLOQUE II. Consulte VALIDATION_REPORT.json.

## Instalar y abrir

Desde una extracción nueva, instale el WHL como se muestra debajo y ejecute
`iniciar_mente.ps1 -Python .\.venv\Scripts\python.exe` para abrir la gramática.
No requiere CPC3, los productos anteriores, internet ni un modelo de lenguaje.
La aplicación imprime el perfil, tick, entrada, recibos y procedencia de cada
respuesta. Consulte `app/LEEME.md` para el vocabulario exacto y los perfiles.

Instalación manual:

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --no-index .\wheel\dee_thinking-4.0.0-cp313-cp313-win_amd64.whl
.\.venv\Scripts\python.exe .\app\conversar.py --help
```

## Producto y evidencia

Las nueve familias 3.5 permanecen. Se añaden sesiones nativas de continuidad,
comparación direccional, información y política finita; adquisición online de
relaciones móviles y composición; persistencia y una interfaz española.
Son realizaciones N34/N47/N67/N127 distintas, no un único individuo universal.
`PRODUCT_CONTRACT.json` fija modalidades y dominios. Las respuestas son lecturas
de la evolución v27; los nombres son interfaz, no un diccionario de soluciones.

`VALIDATION_REPORT.json` registra pruebas y omisiones reales. No hubo ensayos
nuevos de BLOQUE II. `EXPERIMENT_REPORT.md` identifica el plan no ejecutado.
Los replays de referencia son validación de portabilidad, no ciencia nueva.
`evidence/UNBUILT_CLOSURE_FIXES/` conserva correcciones posteriores de interfaz
que NO están incorporadas al WHL entregado. `source/` corresponde al candidato
compilado, no a esas correcciones sin recompilación/pruebas.

## Reconstruir y comprobar

`source/` conserva fuentes, bindings, tests y fixtures. `tools/build40.ps1`
selecciona una instancia Visual Studio, CMake y Ninja de la misma instalación.
Requiere las dependencias externas declaradas en `BUILD_PROVENANCE.json`.
No se distribuyen Windows, Visual Studio ni entornos virtuales.

```powershell
python .\tools\verify40.py --root .
```

Los manifiestos excluyen su propia identidad. El SHA-256 del ZIP se informa
fuera del contenedor. Los productos y expedientes originales no se modifican.
