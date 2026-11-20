# CPC4 — ejecución y demostración

Proyecto DEE Universe. Autor: Ivan Erick Tlaltecatl Morales.

Requisitos: Windows x64, CPython 3.13 estándar de 64 bits. No requiere un LLM, internet, CPC3 instalado ni recompilar DEE. El WHL oficial 4.0.0 incluido contiene kernel v27. No se distribuye un entorno virtual ni un toolchain.

Desde esta carpeta extraída, en PowerShell:

```powershell
py -3.13 -m venv .venv
& .\.venv\Scripts\python.exe -m pip install --no-index --no-deps .\runtime\dee_thinking-4.0.0-cp313-cp313-win_amd64.whl
& .\.venv\Scripts\python.exe -I -B .\ejecutar.py identity
& .\.venv\Scripts\python.exe -I -B .\ejecutar.py verify
```

## Demostración interactiva finita

```powershell
& .\.venv\Scripts\python.exe -I -B .\demostracion.py --salida .\mi_sesion
```

Gramática principal:

```text
crear semilla 42
vivir - coherente -
observar
enseñar HAY
enseñar NO
guardar "mi_estado.deetsnap"
consultar HAY
consultar NO
por qué
salir
```

`vivir + coherente +` usa la historia y el contexto opuestos. `vivir - invertida -` invierte la experiencia del receptor. Son condiciones externas declaradas, no decisiones aprendidas del host. La semilla traslada conjuntamente la geometría toroidal: no determina una respuesta del decoder.

`guardar` preserva el Runtime físico, clocks, canales, recibos y progreso neutral. En una sesión nueva, `cargar "mi_estado.deetsnap"` permite continuar con `consultar HAY` y `consultar NO`, sin repetir `crear` ni `vivir`. No se carga una tabla externa de asociaciones. Los alias, por ejemplo `nombre zuvi W1`, sólo nombran una interfaz; no enseñan significado.

Hay dos oportunidades léxicas y dos consultas en el recorrido publicado. Se consulta en el orden enseñado. Las sondas transforman la organización; tras el corte finito no se simula una conversación ilimitada. Una orden no implementada se rechaza. `observar` es lectura pasiva, no una nueva sonda. `catálogo NSM65.NOT` muestra documentación, no un resultado de aprendizaje.

Las respuestas conservan procedencia: ENTE para un producto nativo válido; INSTRUMENTO para observación/operación; EXPLICACIÓN_DOCUMENTAL o INTERFAZ para explicación y gramática. Una salida desconocida mantiene sus campos físicos, sin asignarle el nombre más próximo.

Después de la primera enseñanza HAY, en t172, `diagnóstico` compara referencia, corte de memoria y sham en tres forks explícitos. Presenta sus emisiones y deja MAIN exactamente en t172; después se puede continuar con `enseñar NO`. No devuelve ninguna rama modificada al individuo. `observar` incluye ahora un atlas pasivo resumido de dirección y conectividad toroidal, sin homología persistente.

También se acepta `--eventos archivo.txt`, con una orden por línea UTF-8 y una carpeta nueva `--salida`. Las transcripciones conservan preguntas, recibos, emisiones y atribución. No se sobrescriben sesiones ni snapshots existentes.

Las plantillas `configuraciones/demo_principal.txt` y `demo_continuacion.txt` contienen `@SALIDA@`; el validador portable lo sustituye por su carpeta de trabajo. Para uso manual, reemplácelo por una ruta propia o escriba un archivo de órdenes con rutas explícitas. La comprobación completa de dos procesos se lanza con:

```powershell
& .\.venv\Scripts\python.exe -I -B .\src\demo_validation.py --output .\validacion_demo_nueva --expected .\resultados\confirmacion\MAIN_MINUS\MEASUREMENTS.json
```

El fixture `--expected` sólo lo utiliza el evaluador después de las respuestas; el proceso del participante no lo lee. Hay un testigo de semilla42 y una instalación limpia ejecutados en `resultados/CLEAN_REPRODUCTION.json`.

## Reproducción y reanudación

```powershell
& .\.venv\Scripts\python.exe -I -B .\ejecutar.py reproduce --case MAIN_MINUS --output .\reproduccion_principal
& .\.venv\Scripts\python.exe -I -B .\ejecutar.py reproduce --case CUT_MINUS --output .\reproduccion_corte
```

Estos comandos generan nuevas trayectorias mediante v27; no leen respuestas terminales para producirlas. Cada proceso tiene timeout. Una reproducción posterior se identifica como tal y no altera el presupuesto original de cuatro horas.

Entrada única alternativa para la interfaz: `ejecutar.py demonstrate --output .\otra_sesion`. El acceso inverso condicional puede reproducirse por separado, sin redefinir el resultado no asistido:

```powershell
& .\.venv\Scripts\python.exe -I -B .\ejecutar.py reproduce-access2 --case ASSISTED_RESCUE_W1 --output .\reproduccion_acceso_asistido
```

Ese comando restaura el padre diagnóstico identificado, emite sondas físicas y sigue la dinámica; no devuelve una respuesta almacenada. El caso `ORIGINAL_MAIN_NO_RESCUE` es su control. El expediente conserva también los dos métodos anteriores con sus silencios, rechazos y guardas no aplicables.

`ejecutar.py run` / `resume` pertenecen a la campaña fechada y a su `BUDGET.json` inmutable. Verifican y saltan casos ya concluidos; no reinician el plazo ni sobrescriben evidencia. Para investigar después se usa `reproduce` con salida nueva, no se borra el ledger.

## Evidencia

La configuración fijada está en `EXPERIMENT_CONFIG.json`. Los 33 resultados centrales están en `resultados/confirmacion`, con `MEASUREMENTS.json` y `COMPLETED.json`. Los checkpoints centrales se conservan junto al caso, no por tick. `MENSAJES.jsonl`, `DIALOGOS.jsonl` y `PREDICCIONES.jsonl` son índices con referencias, no réplicas adicionales.

Discovery, referencias heredadas, relecturas SEM01, instrumentos, inversa y rescates están separados y etiquetados. Consulte `INFORME.md`, `CAPACIDADES.json` y los resúmenes de cada módulo. Las dependencias históricas seleccionadas se incluyen como fuentes pasivas con hashes; el funcionamiento normal no las importa.

Los preparadores de referencias son utilidades de procedencia del desarrollador, no dependencias normales. El material que obtuvieron ya está incluido. `src/observers.py` ofrece observadores pasivos reutilizables sobre un mundo actual; no necesita reconstruir CPC3. Si el lanzador `py` no registra 3.13, utilice la ruta del ejecutable CPython 3.13 x64 disponible para crear el venv.

`MANIFEST.json` inventaría los miembros del expediente salvo él mismo y `HASHES.sha256`. `HASHES.sha256` añade el hash del manifiesto y excluye sólo su propio archivo. El hash del ZIP se informa fuera del contenedor para evitar identidades circulares.
