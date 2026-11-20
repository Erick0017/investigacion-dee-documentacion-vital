# Reproducción de Entrega 01

## Plataforma registrada

- Sistema: Windows 10 x64.
- Compilador detectado: MSVC 19.44.35222.
- Visual Studio: Community 2022 17.14.25, toolset 14.44.35207.
- Windows SDK: 10.0.26100.0.
- Generador previsto: `Visual Studio 17 2022`, arquitectura `x64`.
- Configuración de binarios entregados: `Release`.

La validación final ejecutada, sus comandos y códigos de salida se conservan en
`validation/`. Esta página define el procedimiento; no convierte una prueba no
ejecutada en aprobada.

## Construcción nativa

Abra PowerShell desde la raíz del paquete extraído. Use un entorno donde MSVC
esté instalado. El camino ejecutado y verificado en el equipo de producción es:

```powershell
& .\tools\build_windows.cmd
& .\tools\test_windows.cmd
```

El script abre el entorno x64 de Visual Studio 2022, usa Ninja y deja la
configuración Release en `build\release`. Como alternativa, desde un Developer
PowerShell/Command Prompt donde MSVC ya esté inicializado, se localizó CMake
aquí:

```powershell
$cmake = 'C:\Program Files\Microsoft Visual Studio\18\Community\Common7\IDE\CommonExtensions\Microsoft\CMake\CMake\bin\cmake.exe'
& $cmake --version
& $cmake -S . -B build\manual -G Ninja -DCMAKE_BUILD_TYPE=Release
& $cmake --build build\manual --parallel
```

Todos los productos quedan bajo `build/`. La compilación no accede al WHL ni
ejecuta Python.

## Pruebas

```powershell
& "$env:ProgramFiles\Microsoft Visual Studio\18\Community\Common7\IDE\CommonExtensions\Microsoft\CMake\CMake\bin\ctest.exe" `
  --test-dir build\release --output-on-failure
```

La segunda orden ofrece salida detallada. Consulte también `TEST_MATRIX.md`
para saber qué propiedad cubre cada familia. El estado técnico real debe
deducirse de la salida guardada, no del nombre del ejecutable.

## Consumidor independiente

El target del consumidor se compila como ejecutable separado y enlaza el
artefacto `dee_thinking`; no incluye directamente fuentes `.cpp`. Ejecútelo
desde el directorio de configuración generado, por ejemplo:

```powershell
& .\build\release\bin\dee_thinking_consumer.exe
```

La demostración debe terminar con código 0 sólo cuando la ejecución continua y
la restaurada tienen el futuro esperado y el control causal difiere en el modo
predefinido. Verifique el nombre exacto del target en `CMakeLists.txt` si el
generador elegido organiza los binarios en otra subcarpeta.

Para comprobar ausencia de Python en el producto, ejecute el consumidor sin
activar Conda y revise sus dependencias nativas con una herramienta de Visual
Studio como `dumpbin /dependents`. No es necesario ni apropiado desinstalar
Python.

## Regeneración del núcleo derivado (opcional, desarrollo)

El paquete ya contiene `src/kernel_v27.cpp`; regenerarlo no es necesario para
usar la biblioteca. Para auditar la extracción, suministre una copia del source
canónico con el hash documentado:

```powershell
py -3.13 -I -B .\tools\extract_native_kernel.py `
  'RUTA_A\dee_kernel_v27.cpp' `
  '.\src\kernel_v27.regenerated.cpp'
Get-FileHash -Algorithm SHA256 '.\src\kernel_v27.regenerated.cpp'
```

La herramienta aborta si el source no tiene SHA-256
`44a80f7863d78f596099ddf7d41c9947fa8513503f65067097f1f3b05a8207ab`.
Compare el resultado regenerado con el incluido; no reemplace silenciosamente
el núcleo si difiere.

## Fixtures diferenciales contra el WHL

Python sólo se necesita para regenerar las referencias. Use exactamente el WHL
oficial identificado en `KERNEL_PROVENANCE.md`, en un entorno compatible con
CPython 3.13 x64. La herramienta de fixtures debe:

1. verificar el SHA-256 del WHL y, cuando proceda, del `.pyd` cargado;
2. construir los estados iniciales de forma independiente;
3. ejecutar el oráculo v27;
4. guardar entrada y RAW/clock esperados completos;
5. registrar hashes y protocolo en el manifiesto de fixtures.

El producto C++ consume esos fixtures sin cargar Python. Si el WHL no se puede
ejecutar, no regenere resultados con la nueva biblioteca y no los rotule como
referencia WHL.

## Verificación desde una extracción limpia

La verificación de paquete debe hacerse dentro de una carpeta nueva bajo el
proyecto:

```powershell
$verify = '.\build\package-verify'
New-Item -ItemType Directory -Force -Path $verify | Out-Null
Expand-Archive -LiteralPath '.\DEE_thinking_ENTREGA_01_RESULTADOS.zip' -DestinationPath $verify
Push-Location $verify
& .\tools\build_windows.cmd
& .\tools\test_windows.cmd
Pop-Location
```

La extracción no debe depender de rutas absolutas a runners históricos, del
corpus completo o de una biblioteca vieja encontrada en `PATH`. Las herramientas
de regeneración WHL constituyen una auditoría separada y sí requieren que el
usuario indique el artefacto externo.

## Reproducción de snapshot

Para una comprobación válida no basta comparar bytes del archivo:

1. cree un mundo y programe al menos una entrada futura;
2. avance hasta una frontera anterior a esa entrada;
3. guarde el snapshot;
4. continúe la instancia original;
5. cargue otra instancia desde el snapshot y aplique la misma continuación;
6. compare RAW y clock completos, tick y recibos en el futuro final.

Pruebe también un snapshot truncado o con checksum alterado y confirme que
`restore_snapshot()` deja intacta la instancia receptora.
