# CPC3 — continuidad, comparación y comunicación DEE

Proyecto de Ivan Erick Tlaltecatl Morales. Windows x64, CPython 3.13 estándar.
Motor congelado: DEE thinking 3.5.0 / kernel v27. No utiliza LLM, red, reward ni un
diccionario externo de respuestas. Las palabras y los alias son una interfaz.

## Instalar y empezar

Extraiga el ZIP. Desde su carpeta `CPC3`, use un entorno aislado nuevo:

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --no-index .\runtime\dee_thinking-3.5.0-cp313-cp313-win_amd64.whl
.\.venv\Scripts\python.exe -I -B .\conversar.py
```

La instalación no necesita las carpetas CP01/CP02 ni el laboratorio original.
No incluya el entorno virtual al volver a empaquetar. Los avisos del producto
se conservan en `runtime/`. No se declara una licencia nueva.

## Conversar: una sesión, una MAIN

Gramática disponible (se aceptan variantes explícitas de acentos y puntuación):

- `Observa otra vez`: presenta un resultado observado del hábitat externo por
  un sensor físico; espera la siguiente fase de interfaz declarada.
- `Presenta experiencia A` o `Presenta experiencia B`: entrada solicitada por el
  interlocutor; no equivale a una observación autónoma.
- `¿Qué pasará después?`, `Predice antes de observar`, `¿Ocurrirá lo mismo?`:
  presentan el pronóstico actual de persistencia del paso de un paquete. La
  tercera frase no implementa una comparación arbitraria de dos episodios.
- `Avanza el entorno`: avanza treinta ticks y evalúa objetivos ya vencidos.
- `Muestra el estado`: lectura pasiva del panel y de los recibos.
- `A esto lo llamaremos X`: alias externo para una señal de la interfaz; no
  demuestra que DEE haya adquirido el significado de la palabra.
- `Guarda la sesión`, `Continúa desde la sesión guardada`, `Ayuda`, `Salir`.

Se conserva el mismo propietario nativo en memoria entre órdenes. Una nueva
instancia y una carga son acciones explícitas. El log no sirve como memoria
operativa para producir respuestas. Los recibos rechazados se muestran.

Un recorrido real está en `DIALOGOS.jsonl`; contiene errores de pronóstico y una
respuesta posterior modificada. Para reproducir el protocolo por archivo:

```powershell
.\.venv\Scripts\python.exe -I -B .\conversar.py --eventos .\experimentos\comunicacion\DIALOGO_EVENTOS.txt --sesion .\mi_sesion --transcripcion .\mi_dialogo.jsonl
```

Los diálogos adicionales `DIALOGO_CONTINUA.txt` y los de carga indican sus
operaciones de persistencia. No se concatenan ocultamente individuos distintos.

## Perfil de comparación física

```powershell
.\.venv\Scripts\python.exe -I -B .\conversar.py --perfil comparacion
```

Primero `Observa otra vez`, después `¿Qué pasará después?`, y finalmente
`Compara esto con lo anterior`. Se adquiere la historia en 32–34, se emite en37
para83, se codifica la consecuencia realmente observada en83 y v27 produce el
marcador en84. Puede guardar/cargar el episodio pendiente sin reinstalarlo.

Este perfil tiene **un encuentro de comparación** comprobado. Después no usa el
marcador como otro pronóstico: devuelve un límite de interfaz. La comparación
interfiere con la admisión posterior en el aparato ensayado. No es un sistema
de comparación y reaprendizaje indefinidamente renovables.

`¿Qué fuente necesitas observar?` sólo se activa si el perfil implementa esa
emisión. Los perfiles centrales no la inventan a partir de la verdad oculta.
La selección física finita se ofrece en el recorrido separado siguiente.

## Perfil de política revisable finita

```powershell
.\.venv\Scripts\python.exe -I -B .\conversar.py --perfil politica
```

Secuencia: `Observa otra vez` → `Compara esto con lo anterior` →
`¿Qué fuente necesitas observar?` → `Observa otra vez`. La selección se presenta
desde la acción nativa actual en11; la segunda observación lee el dato que llega
por esa ruta en14. Puede guardar/cargar en mitad del protocolo.

Es un individuo N67 distinto del MAIN central. Su regla instalada conservaP
si su primer dato coincide con la consecuencia observada y cambiaQ si discrepa;
el entorno de prueba tiene fuentes complementarias. La revisión depende del
encuentro físico, pero esa regla y la complementariedad no se aprendieron de
cero. Una sola revisión finita está comprobada; no promete pronóstico ilimitado
ni inventa selección histórica cuando ya pasó su ventana actual.

| Perfil | Organización | Función comprobada |
|---|---|---|
| continuidad | N47, mismo MAIN32→1032 | entrada, lectura y actualización contextual |
| comparacion | N47, episodio37→84 | expectativa y consecuencia se encuentran |
| politica | N67, episodio0→14 | revisión física P/Q y recepción posterior |

No son tres órganos de un único individuo ni snapshots fusionados.

## Recorridos públicos y evidencia

Cada salida debe ser un directorio nuevo/vacío:

```powershell
.\.venv\Scripts\python.exe -I -B .\ejecutar.py continuidad --output .\mi_continuidad
.\.venv\Scripts\python.exe -I -B .\ejecutar.py comparacion --output .\mi_comparacion
.\.venv\Scripts\python.exe -I -B .\ejecutar.py seleccion --output .\mi_seleccion
.\.venv\Scripts\python.exe -I -B .\ejecutar.py politica --output .\mi_politica
.\.venv\Scripts\python.exe -I -B .\ejecutar.py restaurar --snapshot .\checkpoints\continuidad\BA_FULL\MAIN_FINAL.deetsnap --output .\mi_continuacion
.\.venv\Scripts\python.exe -I -B .\ejecutar.py verificar
```

`seleccion` ejecuta en un Runtime otra preparación: historia adquirida →
emisión → consecuencia → comparación → ruta P/Q → información → uso posterior.
Es un protocolo finito con recursos preparados y consecuencia externa
declarada, no una fusión del MAIN central ni una política óptima aprendida.

El último checkpoint de continuidad está en el horizonte comprobado1032.
Restaurarlo y evolucionar más es investigación fuera de ese horizonte, no una
promesa de función. La comprobación independiente usa además una nueva
pregunta dentro del dominio, desde un estado anterior conservado.

Asociaciones numéricas y composición adquiridas se estudian por separado en
`src/lenguaje/association.py`, `run_language.py` y
`experimentos/comunicacion/casos/`. Sus formas opacas identifican puertos;
no constituyen un léxico arbitrario ni gramática aprendida.

## Reproducir y verificar

`compartido/clean_reproduction.py` prepara una extracción/copia independiente,
un entorno limpio e intenta los testigos dirigidos sin abrir las cinco rutas
históricas retiradas. Sus comandos y comprobaciones reales quedan en
`resultados/CLEAN_REPRODUCTION.json`. El alcance del bloqueo de rutas se
declara: no se presenta un hook Python como auditoría universal del sistema.

`compartido/package_cpc3.py --verify RUTA_ZIP` verifica CRC, inventario, SHA-256,
fuentes congeladas y cada miembro migrado. `MANIFEST.json` excluye su propio
hash; el hash del ZIP se informa fuera del ZIP. La migración y limpieza exactas
figuran en `MIGRACION_Y_LIMPIEZA.json`.

Los supervisores y el reloj de esta campaña son evidencia, no una renovación
del presupuesto al reproducirla. No ejecute `guard.py` con el presupuesto
histórico vencido. Los ensayos dirigidos pueden ejecutarse en procesos con
timeout propio. `conversar.py` limita cada orden a treinta segundos y sólo
termina a su hijo propietario si vence el plazo.

Consulte `CAPACIDADES.json`, `INFORME_CIENTIFICO.md` y los resultados primarios.
No interpretar los tests técnicos como veredicto ontológico.
