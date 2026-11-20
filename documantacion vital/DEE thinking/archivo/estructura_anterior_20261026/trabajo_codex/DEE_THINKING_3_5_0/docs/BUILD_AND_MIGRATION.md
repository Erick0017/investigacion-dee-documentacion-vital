# Build y migración — DEE thinking 3.5.0

Windows x64, CPython3.13 estándar, C++20. Build final: una instalación Visual
Studio18 Community, MSVC14.50.35717/19.50, SDK10.0.26100.0, CMake4.2 y Ninja
de esa instalación. Dependencias Python de build utilizadas: setuptools81.0.0,
wheel0.48.0, pybind11 3.1.0, build1.5.0. El producto instalado no requiere esas
dependencias ni `dee_universe_v27`; los runtimes MSVC de Windows son externos.

```powershell
python -m pip install setuptools==81.0.0 wheel==0.48.0 pybind11==3.1.0 build==1.5.0
.\source\tools\build_3_5.ps1 -PythonExecutable C:\ruta\python.exe -BuildRoot C:\ruta_corta\dt35 -Wheel -Tests
python -m venv C:\ruta_corta\venv35
C:\ruta_corta\venv35\Scripts\python.exe -m pip install --no-index C:\ruta_corta\dt35\wheel\dee_thinking-3.5.0-cp313-cp313-win_amd64.whl
C:\ruta_corta\venv35\Scripts\python.exe -I -B .\source\examples\organizational_public.py
```

El build registra comandos, salida y códigos reales. No usa otra instalación
VS para resolver un fallo. Los scripts de publicación3.0 conservados como
referencia están deshabilitados en este árbol; usar `package_3_5.py` y
`verify_delivery_3_5.py`. No se distribuye Visual Studio ni Windows.

Consumidor externo desde Developer PowerShell x64:

```powershell
cmake -S .\source\examples\external_3_5 -B C:\ruta_corta\consumer -G Ninja -DCMAKE_PREFIX_PATH=C:\ruta_corta\dt35\install -DCMAKE_BUILD_TYPE=Release
cmake --build C:\ruta_corta\consumer
C:\ruta_corta\consumer\dee_public_consumer.exe create C:\ruta_corta\cpp_mid.deetsnap
C:\ruta_corta\consumer\dee_public_consumer.exe continue C:\ruta_corta\cpp_mid.deetsnap C:\ruta_corta\cpp_end.deetsnap
```

Si Windows bloquea archivos PowerShell por su política, el consumidor puede
compilarse con el auxiliar Python, sin cambiar dicha política:

```powershell
python -I -B .\source\tools\build_external_3_5.py --install .\install --build-root C:\ruta_corta\consumer
```

El auxiliar obtiene una única instalación VS y ejecuta sus programas CMake,
Ninja y compilador. No ejecuta el `.ps1` bloqueado ni modifica la ley física.

El target `DEE::thinking` y `_native` compilan el mismo source C++; no se promete
ABI binaria entre toolchains. La extensión3.5 es un nuevo build, no un binario
3.0 renombrado. Versiones CMake, wheel, nativa, dist-info, stubs y Python son3.5.

## Compatibilidad

Runtime, catálogo, CompositionPlanner, H1–H4/F1–F2, BasalWorld, PassiveTracker,
inspección y diagnósticos heredados conservan sus contratos. `Runtime` pasa a
un holder compartido en pybind para retener la vida útil de vistas inertes;
no cambia su física, canales ni admisión. No se estrechan APIs antiguas.

Las nuevas recetas validan parámetros propios; usar `OrganizationRecipe.research`
para placements personalizados. Crear otra receta no continúa un individuo.
Restaurar sí conserva estado y colas; attach no instala material.

Snapshot Runtime v1/v2: heredado. Metadatos BasalWorld v1: heredados.
OrganizationalWorld v1: añadidos sobre Runtime v2, con límites y tipos validados.
Un snapshot3.0 se carga mediante Runtime/BasalWorld, o attach inerte si se desea
la capa nueva. No se normalizan clocks, cargas ni relaciones al cargar.

## Reproducción de la validación

```powershell
python -I -B -m unittest discover -s .\source\tests\python -v
python -I -B .\source\tools\compare_native_recipes.py --science .\evidence\DEE_thinking_3_0_0_FRONTERAS_COGNITIVAS_MULTIRRAMA_01_RESULTADOS.zip --output C:\ruta_corta\recipe_comparison.json
python -I -B .\source\tools\replay_primary_cases.py --science .\evidence\DEE_thinking_3_0_0_FRONTERAS_COGNITIVAS_MULTIRRAMA_01_RESULTADOS.zip --suite inherited --output C:\ruta_corta\regression\inherited
python -I -B .\source\tools\replay_primary_cases.py --science .\evidence\DEE_thinking_3_0_0_FRONTERAS_COGNITIVAS_MULTIRRAMA_01_RESULTADOS.zip --suite extension --output C:\ruta_corta\regression\extension
```

Para comparación3.0→3.5 usar entornos separados.3.0 no es dependencia del
producto. El adaptador es sólo ingeniería: importa módulos exactos de la
evidencia y reejecuta sus preparaciones/intervenciones para comparar full-state,
receipts y paneles. Los constructores públicos se contrastan por separado con
esas preparaciones, desde t0 y desde checkpoint intermedio. No carga un snapshot
terminal como sustituto de evolución.

La reanudación omite informes ya aprobados para idéntico expediente/binario;
conserva intentos fallidos y normalizaciones instrumentales explícitas. El
ledger de fuente no recuperada no es ejecución nativa aprobada. Los manifiestos
de ampliación se verifican con raíz `02_REPERTORIO_NATIVO_Y_CIERRES`.
