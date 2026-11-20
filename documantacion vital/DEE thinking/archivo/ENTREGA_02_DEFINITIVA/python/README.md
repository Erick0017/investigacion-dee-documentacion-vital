# Binding Python nativo

`dee_thinking` 2.2.0 enlaza el mismo target CMake y los mismos fuentes C++ que
la biblioteca independiente. No importa ni delega en `dee_universe_v27`.

Requisitos de construcción comprobados para el wheel de esta entrega:

- CPython 3.13 x64;
- setuptools 81, wheel 0.48, build 1.5 y pybind11 3.1;
- CMake y Ninja suministrados por un Visual Studio con el componente C++.

Construcción reproducible desde PowerShell:

```powershell
.\cmake\python\build_wheel.ps1 -PythonExecutable <python-3.13-x64> -OutputDirectory dist
```

El wrapper descubre Visual Studio mediante `vswhere`; no fija una ruta de
instalación privada. Alternativamente pueden definirse `CMAKE_EXECUTABLE` y
`CMAKE_MAKE_PROGRAM` o poner ambas herramientas en `PATH`.

El binding conserva el GIL durante `Runtime.advance()` y `run_until()`. Esto
evita carreras entre mutación, observación y restauración del mismo mundo; el
backend `DENSE_PARALLEL` continúa ejecutando sus workers nativos C++. No se
promete ejecución simultánea de dos mundos desde dos hilos Python en 2.2.0.

