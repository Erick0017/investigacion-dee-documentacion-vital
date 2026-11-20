# DEE thinking 4.5.0 — private source distribution

DEE v27 remains byte-identical. The 4.0 Runtime, C++ target `DEE::thinking`,
catalogue, protocols, nine functional families and session interfaces remain.
New optional bounded preparations and readout are implemented in
`include/dee_thinking/consolidated.hpp`, `src/consolidated.cpp` and their
bindings; Python sessions are in `python/dee_thinking/consolidated.py`.
They prepare and evolve real native worlds, not cached research answers.

For this delivery use `../tools/build45.ps1` (wheel, cpp and consumer stages),
`../LEEME.md`, `../PRODUCT_CONTRACT.json` and `../VALIDATION_REPORT.json`.
Build with C++20 and CPython3.13 x64; install the supplied cp313-win_amd64 wheel
without a source checkout. No other platform or binary ABI is certified.
Direct Runtime use does not require or install a cognitive recipe.
The NSM catalogue records evidence states; it is not 65 acquired meanings.

The material below is inherited reference documentation, not new4.5 results.
Historical build scripts keep their identity and are not the4.5 release path.

## Inherited 3.0 reference below (provenance, not an install dependency)

DEE thinking 3.0.0 is a C++20 library and CPython 3.13 extension built from
one implementation of the frozen DEE v27 transition. It preserves the 2.2.0
Runtime, catalog, composition, snapshot and H1–H4/F1–F2 APIs and adds bounded,
reusable MBP4-derived basal-world construction, passive observation and
explicit fork-only diagnostics.

The wheel is an instrument, not a learned individual. A snapshot stores one
physical execution. The packaged T32 seed is an identified fresh basal seed;
the public constructors install declared physical recipes before evolution and
do not load a terminal learned answer.

## Install and first use

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --no-index `
  .\wheel\dee_thinking-3.0.0-cp313-cp313-win_amd64.whl
```

```python
import dee_thinking as dt

world = dt.create_relational_world(dt.BasalHistory.AB)
print(world.observe().delta)       # prepared pre-experience state: 0
world.advance(1)                   # executed by v27
print(world.observe().delta)       # bounded AB fixture: +1

world.save_snapshot("world.deetsnap")
restored = dt.BasalWorld.load_snapshot("world.deetsnap")
restored.advance(8)

gate = dt.inspect_write_gate(restored.runtime, restored.ports.b, True)
print(gate.local_clock, gate.n_active, gate.branch)
```

Contextual reference execution and an explicit diagnostic fork:

```python
world = dt.create_contextual_world()
world.advance(131)
edit = dt.ResearchStateEdit()
edit.coordinate = world.ports.b
edit.clock = world.runtime.observe(world.ports.b).clock + 1
edit.label = "phase_plus_one"
comparison = dt.compare_diagnostic_fork(world, [edit], 1, True)
assert comparison.parent_unchanged
```

The boolean is software authorization for an intervention on a deep clone. It
never modifies the parent. Passive inspection and tracking perform no
ablations.

## C++

```cmake
find_package(dee_thinking 3 CONFIG REQUIRED)
target_compile_features(my_program PRIVATE cxx_std_20)
target_link_libraries(my_program PRIVATE DEE::thinking)
```

Headers added in 3.0.0 are `basal.hpp`, `observation.hpp`, `genealogy.hpp` and
`diagnostics.hpp`. See `examples/basal_product.cpp` for construction,
observation, checkpoint continuation, bounded tracking and diagnostics.

## Build and test

From a Visual Studio x64 developer shell with CPython 3.13:

```powershell
cmake -S . -B build -G Ninja -DCMAKE_BUILD_TYPE=Release `
  -DDEE_THINKING_BUILD_TESTS=ON -DDEE_THINKING_BUILD_EXAMPLES=ON
cmake --build build --parallel
ctest --test-dir build -C Release --output-on-failure
cmake --install build --config Release --prefix install
python -I -m build --wheel --no-isolation --outdir dist .
```

Exact Windows reconstruction details and dependency versions are in
`docs/BUILD_AND_RECONSTRUCTION.md`.

## Scope

Published basal presets are validated at N=47, T0 tick 32, action distance 5,
and origins `(15,15,15)`, `(22,20,24)` and `(28,26,18)`. `Research` mode makes
representable translations available without claiming them validated. An
accepted geometry or composition is not itself evidence of a functional
organization; run it through v27 and measure it.

The contextual fixture reproduces B 100→101 and relational delta +1→0 at
relative tick 131→132. Selective MBP4 controls showed that the exterior action
products tested there were not necessary for that rewrite. This release does
not publish an exterior-feedback causal claim, and does not turn that bounded
finding into a universal prohibition.

No C++ ABI compatibility with 2.x is promised. Runtime snapshot v1/v2 read
compatibility and physical future equivalence are tested. The binding retains
the 2.2.0 GIL policy, and one mutable Runtime has one writer.

Author: Ivan Erick Tlaltecatl Morales. No new license has been invented for
this delivery; existing notices are retained in `THIRD_PARTY_NOTICES.md`.
