# Build y reconstrucción — DEE thinking 3.0.0

## Toolchain fijado

La reconstrucción de referencia es Windows x64/Release y usa una sola
instancia de Visual Studio de extremo a extremo:

| Componente | Versión/ruta auditada |
|---|---|
| Visual Studio | Community 2026, rama 18, `18.5.11709.299` |
| MSVC | `cl.exe` 19.50.35729.0; toolset `14.50.35717`, Hostx64/x64 |
| Windows SDK | 10.0.26100.0 |
| CMake | 4.2.3-msvc3 |
| Ninja | 1.12.1 |
| Python | CPython 3.13.11 x64, `D:\Descargas\ANACONDA MINICONDA\python.exe` |
| Backend PEP 517 usado | build 1.5.0, setuptools 81.0.0, wheel 0.48.0, pybind11 3.1.0 |

`CMakeLists.txt` exige CMake >=3.20 y C++20, pero las cifras anteriores son las
de la reconstrucción exacta. `pyproject.toml` limita el wheel a Python
`>=3.13,<3.14`, setuptools `>=81,<82`, wheel `>=0.48,<0.49` y pybind11
`>=3.1,<3.2`. No mezcle CMake/Ninja de otra instalación de Visual Studio ni
reutilice caches de 2.2.0, de otra ruta o de otro host.

## Comprobación del entorno

Desde PowerShell, en la raíz fuente 3.0.0:

```powershell
$vsRoot = 'C:\Program Files\Microsoft Visual Studio\18\Community'
& "$vsRoot\Common7\Tools\Launch-VsDevShell.ps1" `
  -Arch amd64 -HostArch amd64 -SkipAutomaticLocation

$cmake = "$vsRoot\Common7\IDE\CommonExtensions\Microsoft\CMake\CMake\bin\cmake.exe"
$ctest = "$vsRoot\Common7\IDE\CommonExtensions\Microsoft\CMake\CMake\bin\ctest.exe"
$ninja = "$vsRoot\Common7\IDE\CommonExtensions\Microsoft\CMake\Ninja\ninja.exe"
$python = 'D:\Descargas\ANACONDA MINICONDA\python.exe'

& cl.exe
& $cmake --version
& $ninja --version
& $python -I -c "import platform,struct,sys; print(sys.version); print(platform.python_implementation(), struct.calcsize('P')*8)"
& $python -I -c "import build,setuptools,wheel,pybind11; print(build.__version__,setuptools.__version__,wheel.__version__,pybind11.__version__)"
```

Las salidas deben identificar MSVC 19.50.35729, CMake 4.2.3-msvc3, Ninja
1.12.1 y CPython 3.13.11 de 64 bits. Si no coinciden, la compilación puede ser
útil, pero ya no es la reconstrucción fijada aquí.

## Biblioteca C++, pruebas e instalación

Use directorios nuevos. Estos comandos configuran el target estático
`DEE::thinking`, ejemplos, benchmark y las pruebas declaradas por el
`CMakeLists.txt` vigente:

```powershell
$sourceRoot = (Get-Location).Path
$buildRoot = Join-Path $sourceRoot 'build\reconstruct-3.0.0-release'
$installRoot = Join-Path $sourceRoot 'install\reconstruct-3.0.0-release'

& $cmake -S $sourceRoot -B $buildRoot -G Ninja `
  "-DCMAKE_MAKE_PROGRAM=$ninja" `
  '-DCMAKE_BUILD_TYPE=Release' `
  '-DCMAKE_CXX_FLAGS_RELEASE=/O2 /Ob2 /DNDEBUG' `
  '-DDEE_THINKING_BUILD_TESTS=ON' `
  '-DDEE_THINKING_BUILD_EXAMPLES=ON' `
  '-DDEE_THINKING_BUILD_BENCHMARKS=ON' `
  '-DDEE_THINKING_BUILD_PYTHON=OFF'

& $cmake --build $buildRoot --parallel
& $ctest --test-dir $buildRoot -C Release --output-on-failure
& $cmake --install $buildRoot --config Release --prefix $installRoot
```

No se registra aquí un número de pruebas aprobadas: la autoridad es el código
de salida y el log de esa ejecución. `ctest --test-dir $buildRoot -N` enumera
la matriz realmente configurada antes de ejecutarla.

Los nombres de producto nuevos son el target `dee_basal_product` y los tests
CTest `basal_product_contract` y `basal_product_e2e`; el segundo se registra
sólo cuando `DEE_THINKING_BUILD_EXAMPLES=ON`.

La instalación debe aportar headers, `lib/dee_thinking.lib`, el package config
en `lib/cmake/dee_thinking/` y la semilla bajo
`share/dee_thinking/fixtures/mbp4/`. El build usa el kernel integrado; no tiene
dependencia de ejecución en Python ni en un laboratorio MBP4 externo.

## Consumidor C++ fuera del árbol de build

Esta comprobación evita incluir headers o biblioteca directamente desde el
source. El consumidor basal pide major 3 mediante
`find_package(dee_thinking 3 CONFIG REQUIRED)`:

```powershell
$consumerBuild = Join-Path $sourceRoot 'build\consumer-basal-3.0.0'
$packageDir = Join-Path $installRoot 'lib\cmake\dee_thinking'

& $cmake -S (Join-Path $sourceRoot 'tests\consumer_basal') `
  -B $consumerBuild -G Ninja `
  "-DCMAKE_MAKE_PROGRAM=$ninja" `
  '-DCMAKE_BUILD_TYPE=Release' `
  "-Ddee_thinking_DIR=$packageDir" `
  '-DCMAKE_FIND_USE_PACKAGE_REGISTRY=OFF' `
  '-DCMAKE_FIND_USE_SYSTEM_PACKAGE_REGISTRY=OFF'
& $cmake --build $consumerBuild --parallel

$installedSeed = Join-Path $installRoot `
  'share\dee_thinking\fixtures\mbp4\OBP_FRESH_VALIDATED_T32.deetsnap'
& (Join-Path $consumerBuild 'dee_thinking_basal_consumer.exe') `
  $installedSeed (Join-Path $consumerBuild 'consumer-basal.deetsnap')
```

El ejemplo de producto construido junto a la biblioteca se invoca de forma
análoga:

```powershell
& (Join-Path $buildRoot 'bin\dee_basal_product.exe') `
  (Join-Path $sourceRoot 'fixtures\mbp4\OBP_FRESH_VALIDATED_T32.deetsnap') `
  (Join-Path $buildRoot 'basal-product-example.deetsnap')
```

## Wheel CPython 3.13

El wheel se construye por PEP 517, sin aislamiento, para que las versiones
auditadas sean las que realmente se usan. El target `_native` compila los
mismos sources C++ que la biblioteca y `bindings/dee_thinking_pybind.cpp` tiene
un `static_assert` para CPython 3.13.

```powershell
$wheelBuild = Join-Path $sourceRoot 'build\wheel-cp313-3.0.0'
$distRoot = Join-Path $sourceRoot 'dist\reconstruct-3.0.0'
$env:CMAKE_EXECUTABLE = $cmake
$env:CMAKE_MAKE_PROGRAM = $ninja
$env:DEE_THINKING_CMAKE_BUILD_ROOT = $wheelBuild
$env:DEE_THINKING_RC_COMPILER = (Get-Command rc.exe).Source
$env:DEE_THINKING_MT = (Get-Command mt.exe).Source
$env:CXX = (Get-Command cl.exe).Source
$env:CC = $env:CXX

& $python -I -m build --wheel --no-isolation --outdir $distRoot $sourceRoot
```

El nombre esperado por el contrato es
`dee_thinking-3.0.0-cp313-cp313-win_amd64.whl`. La mera presencia del archivo
no equivale a validación.

## Instalación limpia y pruebas del wheel

No instale 3.0.0 encima de un entorno que ya contenga 2.2.0. Cree un venv
nuevo, instale sólo el wheel local y ejecute desde un directorio ajeno al
source para impedir que el paquete fuente enmascare al instalado:

```powershell
$wheel = Join-Path $distRoot 'dee_thinking-3.0.0-cp313-cp313-win_amd64.whl'
$venvRoot = Join-Path $sourceRoot 'build\venv-wheel-3.0.0'
$wheelWork = Join-Path $sourceRoot 'build\wheel-validation-work'
& $python -I -m venv $venvRoot
$venvPython = Join-Path $venvRoot 'Scripts\python.exe'
& $venvPython -I -m pip install --no-index --no-deps --force-reinstall $wheel
New-Item -ItemType Directory -Force -Path $wheelWork | Out-Null

Push-Location $wheelWork
try {
  & $venvPython -I -c "import dee_thinking as d, pathlib; print(pathlib.Path(d.__file__).resolve()); print(d.build_info()); print(d.reference_seed_path())"
  & $venvPython -I (Join-Path $sourceRoot 'tests\python\test_wheel_api.py')
  & $venvPython -I (Join-Path $sourceRoot 'tests\python\test_integrated_protocols.py')
  & $venvPython -I (Join-Path $sourceRoot 'tests\python\test_basal_api.py')
  & $venvPython -I (Join-Path $sourceRoot 'tests\python\test_mbp4_regressions.py')
} finally {
  Pop-Location
}
```

Para comprobar continuación basal bidireccional C++↔Python con el ejecutable
producido por CMake:

```powershell
$bridgeWork = Join-Path $sourceRoot 'build\basal-cross-language-work'
& $venvPython -I `
  (Join-Path $sourceRoot 'tests\python\basal_cross_language_driver.py') `
  (Join-Path $buildRoot 'bin\dee_basal_checkpoint_bridge.exe') `
  (Join-Path $sourceRoot 'fixtures\mbp4\OBP_FRESH_VALIDATED_T32.deetsnap') `
  $bridgeWork
```

Cada comando debe conservarse con su salida y código de retorno. Este
documento define cómo ejecutar la reconstrucción; no anticipa sus resultados.

La suite MBP4 lee `fixtures/mbp4/regressions/` como oráculos de prueba; ese
árbol no es una dependencia del Runtime instalado. Su manifest fija la
procedencia de cada fixture y descarta los flags históricos `PASS` como
oráculos. En particular, R5 verifica evidencia primaria congelada, pero no
recrea el rescate desde cero.

## Ensamblado y verificación de la entrega

Empaquete sólo después de reunir wheel, instalación C++ y evidencia real de
esta reconstrucción. Los dos directorios de evidencia deben existir, ser no
vacíos y contener los logs/artefactos que se desean publicar; el empaquetador
no los inventa ni ejecuta las pruebas por el llamador.

```powershell
$validationRoot = Join-Path $sourceRoot 'artifacts\validation-3.0.0'
$evidenceRoot = Join-Path $sourceRoot 'artifacts\evidence-3.0.0'
$deliveryRoot = Join-Path (Split-Path -Parent $sourceRoot) 'delivery-3.0.0'
$archive = Join-Path $deliveryRoot `
  'DEE_thinking_3_0_0_ENTREGA_FINAL_RESULTADOS.zip'
$verificationReport = Join-Path $deliveryRoot 'verification-3.0.0.json'

& $python -I (Join-Path $sourceRoot 'tools\package_3_0.py') `
  --project-root $sourceRoot `
  --wheel $wheel `
  --install-root $installRoot `
  --validation-root $validationRoot `
  --evidence-root $evidenceRoot `
  --output $archive `
  --verification-report $verificationReport

& $python -I (Join-Path $sourceRoot 'tools\verify_delivery_3_0.py') `
  --archive $archive `
  --report $verificationReport
```

`package_3_0.py` selecciona un árbol fuente limpio, genera `MANIFEST.json` y
`HASHES.sha256`, crea un ZIP determinista, verifica primero un candidato y
publica mediante reemplazo atómico sólo si pasa. Rechaza otro nombre de wheel
u otro nombre de archivo final. Si el destino ya existe, se detiene; use
`--replace` únicamente cuando se pretenda sustituir deliberadamente esa ruta.
`verify_delivery_3_0.py` comprueba estructura, CRC, hashes, declaraciones de
versión, limpieza del source, wheel CPython 3.13, kernel congelado y nombre
canónico. No use scripts de empaquetado 2.2.0 para esta entrega. Ningún ZIP ni
resultado de verificación queda implícito por estos comandos: deben conservarse
el código de retorno y el reporte generados en la ejecución final.

## Controles de identidad y limpieza

Antes de publicar, compruebe al menos:

```powershell
Get-FileHash -Algorithm SHA256 `
  (Join-Path $sourceRoot 'src\kernel_v27.cpp')
Get-FileHash -Algorithm SHA256 `
  (Join-Path $sourceRoot 'fixtures\mbp4\OBP_FRESH_VALIDATED_T32.deetsnap')
```

Los valores esperados son, respectivamente,
`fbd8190381ed76085f404e6578ff15fe185ab66cd48c67300d2abad61ddc7e31` y
`cd09a4d94f72e00d9a5163c8dfd1d62e1528f1d146e4cb44ae23d261b3da09e6`.
No distribuya caches CMake, `.obj`, `.pyc`, `__pycache__`, `.egg-info`, venvs ni
un `_native.pyd` procedente de otra compilación. Los árboles `build` e
`install` son resultados regenerables, no fuentes.
