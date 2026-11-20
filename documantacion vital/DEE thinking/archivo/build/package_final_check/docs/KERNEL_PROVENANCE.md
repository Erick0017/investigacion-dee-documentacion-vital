# Procedencia del kernel v27

## Identidad dirigida

Los hashes siguientes se calcularon el 2026-10-03 sobre los artefactos locales
usados para esta entrega:

| Artefacto | Identidad | SHA-256 |
|---|---|---|
| Source canónico | `VERSION_27/dee_universe_v27/dee_kernel_v27.cpp`, 28 762 bytes | `44a80f7863d78f596099ddf7d41c9947fa8513503f65067097f1f3b05a8207ab` |
| WHL oficial | `VERSION_27/dist/dee_universe_v27-27.0.0-cp313-cp313-win_amd64.whl`, 100 035 bytes | `69297e6f06761c8b2f65d24a3fd7a2f16a3f67595a7f9660739ab65f47abc939` |
| Source miembro del WHL | `dee_universe_v27/dee_kernel_v27.cpp`, 28 762 bytes | `44a80f7863d78f596099ddf7d41c9947fa8513503f65067097f1f3b05a8207ab` |
| Binario de referencia instalado | `dee_kernel_v27.cp313-win_amd64.pyd` | `0b17ba32037935a255b0f2182a52137bceab424f7e09126b761076b63e42c6ff` |
| Inicializador del paquete instalado | `dee_universe_v27/__init__.py` | `7e2991b1fc8a053ee44ead6e177b129855ae9265dea68505a8e545f0c3fdf8b4` |

El miembro source del WHL y el source canónico son byte-idénticos por hash. El
binario informa:

```text
DEE Universe Kernel v27.0-PKCANON (v26-SYM1 fork; canonical P_KERNEL=19665)
```

## Método de derivación

`tools/extract_native_kernel.py` recibe una ruta explícita, verifica primero el
hash canónico y aborta ante cualquier discrepancia. Después:

1. elimina únicamente includes y alias de pybind11;
2. conserva las secciones puras de representación y regla hasta DEMUX;
3. añade el namespace y las funciones públicas de empaquetado/decodificación;
4. añade un driver denso, secuencial y determinista para el tick;
5. conserva la copia final `gB -> gA` y `clockB -> clockA` del source histórico.

La biblioteca no carga el `.pyd`, no embebe Python y no delega el tick al WHL.
El WHL se mantiene como oráculo externo de desarrollo para fixtures.

## Regla que se preserva

La copia derivada conserva, entre otros elementos causalmente relevantes:

- palabras de 64 bits y campos `state`, `s_reg`, dirección y semántica;
- componentes direccionales de cuatro bits con signo;
- indexación `(x*N+y)*N+z` y toro tridimensional;
- vecindad Moore-26 y su orden;
- prioridad y condiciones de ramas;
- lectura del estado inicial común de cada tick;
- escritura del destino, acumulación y aplicación de DEMUX;
- actualización de clocks de 64 bits;
- sectores many-to-one y ramas reversibles presentes en el source;
- `P_KERNEL = 19665` y el cap operativo del reducer `19664`.

La API nativa no elimina palabras cuyo `state` sea cero. La presencia RAW y la
ocupación decodificada son observables distintos.

## Autoridad ante discrepancias

Para esta entrega el orden de contraste es:

1. source canónico con hash exacto;
2. ejecución del binario WHL identificado;
3. fixtures RAW/clock completos generados por ese binario;
4. telemetría histórica con aparato y protocolo identificables;
5. documentos interpretativos.

El archivo histórico `dee_constants_v27.py` instalado contiene una constante
`P_KERNEL` que no coincide con la constante canónica del source/binario. La
biblioteca nativa no lo usa como autoridad; usa `19665`, presente en el source
con hash anterior. Esta diferencia se conserva como nota de procedencia, no se
resuelve seleccionando silenciosamente el valor conveniente.

## Alcance de la equivalencia

La igualdad del source de partida no sustituye la validación del producto
derivado. La aceptación requiere comparaciones exactas de RAW y clock en
trayectorias no vacías, ramas límite y ejemplos integrados. Los resultados
concretos y el primer estado discrepante, si existe, pertenecen a
`validation/`.

Una batería finita sólo respalda el dominio probado. No implica equivalencia
universal para todo tamaño, estado representable, compilador o plataforma.

