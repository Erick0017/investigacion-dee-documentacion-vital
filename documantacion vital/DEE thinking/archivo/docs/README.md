# DEE thinking — Entrega 01 de 03

DEE thinking es una biblioteca C++ para ejecutar la regla congelada de DEE
Universe v27 dentro de mundos persistentes. Esta entrega separa tres capas:

1. el núcleo v27, derivado mecánicamente del source canónico;
2. un runtime que conserva estado, agenda entradas, avanza, observa, bifurca y
   restaura ejecuciones;
3. organizaciones de referencia que ejercitan transporte, reprogramación,
   historia contextual y recurrencia multicanal.

Los términos *thinking*, memoria o aprendizaje nombran contratos operacionales
y aparatos experimentales. No son un dictamen de consciencia, autonomía,
inteligencia general ni capacidad ilimitada.

## Dependencias

Uso nativo:

- Windows x64;
- runtime de C++ requerido por los binarios construidos;
- ninguna dependencia de Python, del WHL ni del `.pyd` al ejecutar la
  biblioteca, el consumidor o los ejemplos.

Construcción reproducida para esta entrega:

- MSVC 19.44.35222, Visual Studio 2022 Community 17.14.25;
- Windows SDK 10.0.26100.0;
- CMake incluido en Visual Studio (se detectó también una instalación de CMake
  bajo Visual Studio 18 Community).

Python 3.13 y el WHL oficial sólo intervienen en herramientas de desarrollo que
generan fixtures diferenciales. No forman parte del proceso nativo del producto.

No se promete compatibilidad binaria con otro compilador, arquitectura o
sistema operativo que no aparezca en el informe de validación.

## Estructura

```text
include/dee_thinking/   API pública
src/                    núcleo derivado, runtime y organizaciones
tests/                  regresiones del núcleo, runtime y aparatos
examples/               demostración y consumidor C++ independiente
tools/                  extracción y generación de fixtures (desarrollo)
fixtures/               referencias generadas con el WHL oficial
docs/                   contrato, alcance, procedencia y reproducción
build/                  artefactos compilados incluidos en la entrega
validation/             salidas de la validación ejecutada
```

## Compilación y prueba rápida

Desde la raíz extraída del paquete:

```powershell
& .\tools\build_windows.cmd
& .\tools\test_windows.cmd
```

Si `cmake` ya está en `PATH`, puede sustituirse `$cmake` por `cmake`. Los
comandos exactos usados y cualquier diferencia de ruta quedan en
[REPRODUCIBILITY.md](REPRODUCIBILITY.md).

El consumidor independiente incluye únicamente headers públicos y enlaza la
biblioteca; no incluye los `.cpp` del producto. Su secuencia crea una
organización, programa experiencias, avanza el mismo mundo, observa, guarda,
restaura en otra instancia y compara la continuación con la rama no
interrumpida. Incluye además un control causal no favorable esperado.

## Uso mínimo de la API

```cpp
#include <dee_thinking/organizations.hpp>

auto reference = dee::thinking::make_transport_world();
auto& world = reference.runtime;
const auto receipt = world.experience("carrier", world.current_tick(), 7);
world.advance(5);
const auto observation = world.observe(reference.landmarks.at("destination"));
world.save_snapshot("world.deetsnap");
auto restored = dee::thinking::Runtime::load_snapshot("world.deetsnap");
```

`experience()` programa una intervención; no garantiza admisión posterior,
respuesta ni aprendizaje. Debe consultarse el recibo después de alcanzar la
frontera correspondiente. `observe()` es pasivo. `probe()` agenda una
intervención declarada y no es una observación.

## Mapa de entregas

| Requisito | Entrega | Implementación o condición |
|---|---:|---|
| Núcleo v27 independiente de Python | 01 | Regla C++ derivada del source canónico con contrato de cuatro buffers |
| Runtime persistente, eventos y observación | 01 | Implementado en `Runtime`; validación técnica en `validation/` |
| Pausa, fork, snapshot y continuación | 01 | Implementado; formato documentado y futuro restaurado verificado |
| Memoria móvil, relativa y distribuida | 01/02 | Entrega 01 aporta casos de historia/contexto; catálogo ampliado queda para 02 |
| Aprendizaje y reprogramación | 01/02 | Entrega 01 aporta un aparato de referencia y control; composiciones adicionales quedan para 02 |
| Integración y separación multicanal | 01/02 | Entrega 01 aporta un caso acotado; repertorio/composición de alto nivel queda para 02 |
| Recurrencia y retorno | 01/02/03 | Entrega 01 reproduce continuidad finita y corte; ampliación de contratos en 02 y operación prolongada en 03 |
| Observación y sondas | 01 | API separada: lectura pasiva frente a intervención física declarada |
| Persistencia y reproducción | 01 | Snapshot binario versionado, checksum y restauración transaccional |
| Capacidad y saturación | 01/03 | Límites exactos del kernel y métricas pasivas; gestión prolongada queda para 03 |
| Adaptadores de aplicaciones | 03 | Fuera de esta entrega; no se exportan funciones vacías que aparenten disponibilidad |

## Límites importantes

- El estado `Q0` conservado por el runtime son las palabras RAW y clock
  completas. `state`, `s_reg`, dirección y semántica son decodificaciones de
  RAW.
- `state == 0` no equivale a `raw == 0`.
- Una carga cero no equivale a ausencia de portador.
- Las consultas físicas pueden transformar el mundo; sólo `observe()` es
  lectura pasiva.
- Las organizaciones de referencia incluyen geometría y recursos preparados.
  No demuestran creación autónoma de esos recursos.
- Una batería diferencial finita establece equivalencia sólo en los estados,
  trayectorias y plataforma probados.
- La biblioteca no gestiona automáticamente capacidad, no borra memoria, no
  integra hardware y no contiene una política de supervisor escondida en
  `advance()`.

Consulte [API_CONTRACT.md](API_CONTRACT.md) antes de integrar el runtime y
[SCIENTIFIC_SCOPE.md](SCIENTIFIC_SCOPE.md) antes de interpretar sus ejemplos.
