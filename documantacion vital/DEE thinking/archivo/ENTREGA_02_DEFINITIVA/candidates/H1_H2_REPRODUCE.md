# Reproducción limpia H1/H2

Los targets tienen nombres internos cortos (`h1t`, `h2t`) para respetar el
límite de paths de MSVC. Desde la raíz de `ENTREGA_02_PREINTEGRACION`, en un
Developer Command Prompt x64:

```powershell
cmake -S candidates -B candidates\b -G Ninja -DCMAKE_BUILD_TYPE=Release
cmake --build candidates\b --parallel
.\candidates\bin\h1_delay_position_candidate_tests.exe
.\candidates\bin\h2_destination_repertoires_candidate_tests.exe
```

El CMake local importa `build/Release/lib/dee_thinking.lib` y los headers de
`include/`; no añade targets al build estable ni recompila el kernel. Salidas
esperadas:

```text
H1_CANDIDATE_PASS native=11/11 reversed=1/11 absent=1 dense_lazy_exact=1
H2_CANDIDATE_PASS separated=3,7 budgets_exact=1 overlap_identity_lost=1 off_fiber=1 dense_lazy_exact=1
```
