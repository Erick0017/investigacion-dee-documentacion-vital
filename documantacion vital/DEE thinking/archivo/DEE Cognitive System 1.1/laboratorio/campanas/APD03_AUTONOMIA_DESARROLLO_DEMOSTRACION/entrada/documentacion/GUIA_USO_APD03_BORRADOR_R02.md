# APD03: una entrada y una vida continuable

Corte editorial intermedio: la UI typed se utiliza en la trayectoria real `APD03_MAIN`; están cerrados los bloquesB0–B3. La hora completa, su STOP/reapertura, el corte seleccionado final y la prueba Full todavía no se certifican aquí. Este documento no reemplaza los contratos ni actualiza el Word.

## Abrir, usar, guardar y volver

En la raíz original de DEE Cognitive System1.1, utilizar el CPython3.13x64 que ya está instalado:

```powershell
& 'D:\GENESIS AI\GENESIS 5.0\simulador de universo ab-initio\dee_libreria\VERSION_27\tests\_dcs11_env_20261020_002458\Scripts\python.exe' -I -B -X utf8 '.\sistema\app\usar_dee.py' --nueva MI_APD03_01
```

`--nueva` importa una sola vez el par completo seleccionado en `sistema/contratos/ENTRADA_SENCILLA_APD03.json`; no crea T0 ni reemplaza ACTIVO. Si el nombre ya existe, se rechaza en vez de rebobinarlo. No utilizar el ID de MAIN para hacer pruebas personales. Root prevé seleccionar el corte final APD03_MAIN, que ya contiene el sensor y K admitidos; no repetir su preparación. El contrato y su ficha deben indicar el snapshot realmente cerrado antes de liberar esta guía: esa selección final sigue pendiente en el presente borrador.

La misma terminal muestra `DEE>`. El propietario Native se administra en segundo plano; no hay que coordinar otra terminal. Arranca en pausa:

```text
estado
reanudar
usar suma 18 7 --retorno omit
guardar
detener
salir
```

`estado` lee una publicación pasiva con antigüedad de caché. `usar`, `lenguaje`, `panel`, enseñanza y objetivos sí presentan material o interacciones. Sus resultados no son respuestas precargadas: pueden fallar, ser ambiguos o rechazar entradas. La suma de la prueba UI diagnóstica seleccionó un proveedor externo; no toda aritmética de `usar` es cálculo v27.

Para continuar esa misma copia:

```powershell
& 'D:\GENESIS AI\GENESIS 5.0\simulador de universo ab-initio\dee_libreria\VERSION_27\tests\_dcs11_env_20261020_002458\Scripts\python.exe' -I -B -X utf8 '.\sistema\app\usar_dee.py' --vida MI_APD03_01
```

Después, `estado`, `reanudar`, una interacción nueva, `guardar`, `detener`, `salir`. No usar `--nueva` de nuevo. `continuar` carga otra vez esa identidad después de un STOP dentro de una sesión; vuelve a empezar pausada. `detener`/`salir` afectan sólo el propietario creado por esa sesión, no procesos ajenos.

## Comandos APD03 y qué hace cada uno

Las órdenes nuevas empaquetan situaciones literales para el mismo gestor, sin elegir acciones por el ente. `ayuda` muestra la sintaxis exacta.

| Orden | Función y asistencia |
|---|---|
| `ensenar-nueva luma -1 --revision --retorno omit` | Docencia explícita de una de las dos ranuras genéricas finitas, `luma`/`nara`, con signo±1. El operador decide enseñar; no aprendizaje sin docente. |
| `lenguaje-nuevo luma 23 gamma --retorno omit` | La señal adquirida puede seleccionar comparación preparada o consulta MA; el operador aporta dato y contexto. No español libre. |
| `objetivo suma 24 5 --oculto --contexto-ambiente 1` | Presenta un problema ambiental. El segundo hecho no es inicialmente accesible al participante; el wrapper lo conserva como parte del mundo. No ordena QUERY/ACT. |
| `paso 4` | Ofrece hasta cuatro oportunidades a la evolución Native. La organización emite una acción física o no responde; la UI no selecciona la más favorable. |
| `panel --nuevas --memorias --retorno omit` | Consultas materiales de repertorio y contenido; no observación inocua. No repetir constantemente para tranquilizar al auditor. |

Las situaciones correspondientes son `apd03-admitir`, `apd03-docencia`, `apd03-lenguaje`, `apd03-tarea-iniciar`, `apd03-paso` y `apd03-panel`. El actor y contrato deciden si están admitidas en una vida. Instalar código no entrega aprendizajes a una copia anterior. `usar`, `meta` y `meta-paso` mantienen sus protocolos APD02: no se retargetean silenciosamente.

El uso ordinario desde el par APD03 seleccionado es cargar→reanudar→objetivo/paso o palabras→guardar/STOP; **no necesita `admitir-apd03` otra vez**. Esa orden se conserva para investigación P0 en copias de un prefijo aún no admitido, no como reparación, reaprendizaje ni reinicio de la vida seleccionada.

El ejemplo de enseñanza luma− modifica realmente la asociación previa luma+ en la copia Full de prueba. No es un procedimiento que deba ejecutarse sobre cada apertura para aparentar retención. Para evaluar conservación, consultar sin repetir la lección. El comando físico− de la forma selecciona la consulta MA preparada; la respuesta de esa memoria puede ser+, como GAMMA. Comando y contenido no son la misma variable. `--retorno omit` omite la consecuencia material común; no elimina suministros ni convierte una enseñanza explícita en recuerdo espontáneo.

## Contexto ambiental no equivale a información privada entregada

La interfaz fija transduce el indicador actual de presencia/ausencia del segundo hecho. No transmite el resultado correcto, la acción útil ni el futuro. El argumento `--contexto-ambiente`0/1 permanece en Python/wrapper: no está transducido al selector Native R04. No atribuir al participante percepción o selección contextual de ese bit por haberlo escrito en `objetivo`. El operador sigue escogiendo el objetivo y cuándo ofrecer oportunidades.

La consecuencia real de una acción puede entrar por el canal fijo y modificar referencias físicas. QUERY conserva el operando revelado en el estado público del **ENTORNO**; una ACT posterior recibe los operandos actualmente observables. Esto no demuestra que Native haya memorizado el número entre oportunidades. La referencia física que cambia la selección y el dato numérico ambiental son soportes distintos. Que haya un resultado útil no certifica R2 general, iniciativa propia ni invención de programas. Las dos formas nuevas son asociaciones sobre interacciones disponibles, no nuevos algoritmos ni primitivas NSM automáticamente adquiridas.

## Petición pendiente: consultar el mismo ID, no reenviar

Si una espera termina antes del resultado, conservar el identificador y usar:

```text
resultado ID_QUE_YA_APARECIO
```

Es una lectura del recibo existente. No reenviar la tarea con otro ID ni importar otro padre. El supervisor conserva el hash y la identidad pendiente; una incertidumbre externa bloquea nuevas interacciones/reanudación hasta examinarla. La prueba MAIN prepara una petición pausada, la guarda y continúa ese ID en otro proceso; todavía está pendiente en este corte editorial. No declarar esa prueba completada a partir de los fixtures.

## Estado de comprobación y distribución

La entrada original R02 se verificó nativamente en `DIAG_APD03_UI_R01`: importación emparejada, docencia COMPARA−, dos usos, archivo real25 por proveedor externo y reapertura de la misma vida en T550353→T550490. Su recálculo1822 no son1822ensayos.

La revisión typed conserva por genealogía el identificador `APD03.single_terminal.R03.typed_contextual_candidate`. Sus35fixtures son N0. Además, sus modos ya se utilizan en MAIN B0–B3; eso no equivale todavía a una liberación final ni prueba independiente del Full.

El Full exacto tendrá una comprobación local desde otra carpeta, con su Python incluido y tres propietarios UI secuenciales sobre una sola vida: baseline luma+/nara−, docencia luma−, objetivo nuevo SUM24,5 oculto y reapertura. Sólo podrá anunciarse cuando se cierre y verifique ese ZIP. No es otro usuario humano ni otra computadora, y sus tres sesiones no constituyen la hora continua de MAIN. El comando previsto `INICIAR.bat usar` no se anuncia aquí como Full ya comprobado.

## Recursos y evidencias

La CPU/RAM total del árbol exterior y los límites anidados Native se registran con ámbitos separados y no se suman. `IoInfo` dentro de la estructura Windows de clase9 es reservado: sus ceros no miden ausencia de E/S. El monitor OS posterior usa clase8 y registra contadores lógicos acumulados desde la creación del Job Native, incluidos sus trabajadores; no incluye todo el supervisor y no es tráfico físico de disco. Energía: **NO MEDIDA**.

Fuentes: `ENTRADA_NATIVA_R01/`, `MAIN_INTEGRADO_R01/EVENTOS/`, `MEDICION_IO_OS_R01/` y los recálculos complementarios `entrada/servicio_hora/` y `main/recalcular_main_integrado_n0.py`. La entrega compacta no contiene todos los estados operativos. Para continuar una vida se necesita su par completo, no sólo tablas o RAW exportados.
