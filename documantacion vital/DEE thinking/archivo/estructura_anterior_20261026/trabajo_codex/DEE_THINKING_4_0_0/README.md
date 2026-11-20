# DEE thinking 4.0.0

Proyecto DEE Universe / INVESTIGACION DEE. Autor: Ivan Erick Tlaltecatl Morales.
Windows x64, CPython 3.13 estándar, C++20; kernel DEE v27 conservado.

La continuación autorizada por el usuario conserva el corte parcial y completa
sus pendientes. El estado técnico final y los límites están en
`VALIDATION_REPORT.json`; el registro anterior sigue en `validation/partial_cut`.

## Instalar y abrir

Desde una extracción nueva, instale el WHL como se muestra debajo y ejecute
`iniciar_mente.ps1 -Perfil mundo_nativo -Python .\.venv\Scripts\python.exe`
para abrir el demostrador de un mismo mundo con contacto, adquisición y consulta.
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

`VALIDATION_REPORT.json` registra pruebas, reutilización por identidad y cierre.
`EXPERIMENT_REPORT.md` y `experiments/` conservan los nuevos ensayos BLOQUE II,
incluidos controles, reservas y transcripciones. Los replays CPC3 son validación
de portabilidad, no ciencia nueva. Las correcciones de interfaz preservadas en
el parcial se incorporaron al WHL final y superaron la prueba afectada; su
genealogía sigue en `evidence/UNBUILT_CLOSURE_FIXES/` y
`validation/RESUMPTION_INTEGRATION.json`.

Ejemplo de sesión `mundo_nativo`: `Instancia nueva`, `Vive el encuentro`,
`A esto lo llamaremos brisa`, `Presenta consulta 13`, `Observa respuesta`,
`Guarda mi_historia.deetsnap`, `Carga mi_historia.deetsnap`,
`Presenta consulta 19`, `Observa respuesta`. Son dos sondas consumibles en una
organización móvil finita. No se reconstruye el individuo entre preguntas.

## Reconstruir y comprobar

`source/` conserva fuentes, bindings, tests y fixtures. `tools/build40.ps1`
selecciona una instancia Visual Studio, CMake y Ninja de la misma instalación.
Requiere las dependencias externas declaradas en `BUILD_PROVENANCE.json`.
No se distribuyen Windows, Visual Studio ni entornos virtuales.

```powershell
python .\tools\verify40.py --root .
python .\tools\reproduce40.py --root . --case online_contact_main --output .\mi_reproduccion
```

Los manifiestos excluyen su propia identidad. El SHA-256 del ZIP se informa
fuera del contenedor. Los productos y expedientes originales no se modifican.
