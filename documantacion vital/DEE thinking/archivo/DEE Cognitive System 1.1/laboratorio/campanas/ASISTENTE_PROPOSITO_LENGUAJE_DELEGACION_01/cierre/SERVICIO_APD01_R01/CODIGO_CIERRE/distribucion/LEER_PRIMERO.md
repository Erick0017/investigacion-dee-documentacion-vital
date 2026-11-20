# DEE: paquete privado para investigación y desarrollo

Universe v27 es la dinámica física; thinking4.5.0 es el motor y su instrumental congelados; Cognitive System1.1 administra experiencias, perfiles y vidas persistentes. Esta carpeta es una distribución del sistema existente, no otra plataforma ni una mente que conozca toda su biblioteca.

## Comenzar en Windows x64

1. Extraiga **toda** la carpeta en una ubicación escribible, corta y ASCII. No ejecute dentro del ZIP.
2. Se incluye CPython3.13.11 x64 portátil y un único WHL oficial thinking4.5.0. No necesita instalar Python, pip ni un compilador. Si falta la biblioteca Microsoft C++v14, ejecute manualmente `motor/VC_redist.x64.exe`, instalador oficial firmado que puede pedir permisos de administrador. El paquete no lo instala silenciosamente.
3. Abra `INICIAR.bat`. El primer uso despliega el WHL incluido localmente, sin red. `INICIAR.bat catalogo` muestra vidas, perfiles, ticks, asistencia y límites.
4. Abra una **copia** con identidad nueva: `INICIAR.bat abrir E1_PROTEGIDO COLAB_E1_01`. Restaura un estado completo, no una receta vacía deT0.
5. Guarde su trabajo en `trabajo_personal/`. Las actualizaciones no lo borran ni copian sus resultados a otra vida.

El Manual Maestro vigente está **una sola vez en esta raíz**. `documentos/MANUAL_VIGENTE.json` identifica su nombre, SHA-256 y situación editorial; es un puntero, no otro Word actual. Las fuentes, guías y resultados conservados tienen su propia procedencia.

## Asistente DEE de propósito y lenguaje acotados

La opción nueva es **`ASISTENTE_PROPOSITO`**. Es una copia de la vida real `ASISTENTE_MAIN`, descendiente de la organización unificada; no sustituye al E1 protegido ni reúne memorias de controles. `entes/CATALOGO.json` identifica el corte completo distribuido y su alcance efectivamente comprobado. Las lecciones programadas que no se admitieron no cuentan como conocimientos adquiridos.

Desde **CMD**, abra una copia con identidad nueva y mantenga su propietario en la primera ventana:

```bat
INICIAR.bat abrir ASISTENTE_PROPOSITO COLAB_APD_01
INICIAR.bat asistente COLAB_APD_01 iniciar --pausado
```

En otra ventana CMD situada en esta misma carpeta:

```bat
INICIAR.bat asistente COLAB_APD_01 estado
INICIAR.bat asistente COLAB_APD_01 reanudar --id APD_USUARIO_RESUME_01
INICIAR.bat asistente COLAB_APD_01 usar --texto suma --operandos 6 13 --id APD_USUARIO_USO_01
INICIAR.bat asistente COLAB_APD_01 contar --presencias 0 1 1 --id APD_USUARIO_CONTEO_01
INICIAR.bat asistente COLAB_APD_01 componer --formas suma resta --datos 5 14 3 --id APD_USUARIO_COMPOSICION_01
INICIAR.bat asistente COLAB_APD_01 pausar --id APD_USUARIO_PAUSA_01
INICIAR.bat asistente COLAB_APD_01 guardar --id APD_USUARIO_SAVE_01
INICIAR.bat asistente COLAB_APD_01 exportar --id APD_USUARIO_EXPORT_01 --esperar 180
INICIAR.bat asistente COLAB_APD_01 detener --id APD_USUARIO_STOP_01
```

Para continuar, inicie otra vez **esa misma identidad personal** y reanúdela con un ID nuevo; no vuelva a importar un pasado para ocultar errores. El propietario avanza entre peticiones cuando no está pausado. Un ID ya usado consulta/deduplica esa operación: no sirve para repetir una acción nueva. Ante demora, consulte `asistente COLAB_APD_01 resultado --id ID_ORIGINAL`; no reenvíe ciegamente acciones inciertas.

La interfaz admite seis formas físicas finitas (`suma`, `diferencia`, `agrega`, `resta`, `total`, `quita`) que se asocian por experiencia a **dos clases de operador ya preparadas**; admisión de un canal no significa dominio de esa palabra por cada vida. No hay un intérprete libre del español. El árbol aritmético y el conteo son mecanismos preparados; el calculador Python, cuando una salida DEE lo solicita, es una herramienta externa declarada. La secuencia de dos/tres formas la especifica el usuario; el compilador serializa emisiones reales, no inventa un plan ni decide la ruta conveniente. Conteo admite dos/tres presencias individuales0/1, no una lista arbitraria. Los resultados numéricos, el código aprendido, el artefacto material y el coste modelado se informan por separado.

Para variar una experiencia en **su copia**, `asistente ... ensenar --texto FORMA --senal SIGNO --id NUEVO` es docencia explícita; `--revision` sólo se utiliza donde el contrato la admita. No es una decisión autónoma del ente. El comando se escribe `ensenar`, sin acento. Cambiar una asociación no aprende el algoritmo aritmético. No copie registros o edite RAW/clocks para insertar conocimientos.

Conserve siempre el **par completo** snapshot+SQLite+colas+artefactos. Exportar no equivale a copiar sólo el snapshot. La cola local acotada, el puente y el registro son instrumentación; no un almacén externo de respuestas al que el código decisor deba recurrir. El audit-hook Python no es un sandbox del sistema operativo ni una prohibición universal de leer archivos históricos. No se prometen regulación general, recuperación autónoma, planificación, 65 significados ni asistencia general.

## Mente unificada y servicio continuo anteriores

`MENTE_UNIFICADA` conserva el corte anterior seleccionado explícitamente en MUFI01. Consulte `entes/CATALOGO.json` y su ficha: no se elige una vida por la respuesta esperada. El futuro R11 y el E1 protegido se conservan separados. Las memorias de esas ramas no se fusionan ni reciben por etiqueta las experiencias posteriores de `ASISTENTE_MAIN`.

Desde **Símbolo del sistema / CMD**, en esta carpeta:

```bat
INICIAR.bat abrir MENTE_UNIFICADA COLAB_MU_01
INICIAR.bat gestor mente-unificada-iniciar --vida COLAB_MU_01 --backend mente_unificada --pausado
```

El segundo comando mantiene un propietario local en esa ventana. No abre puertos públicos ni se inicia automáticamente. En otra ventana CMD, situada en la misma carpeta:

```bat
INICIAR.bat gestor mente-unificada-estado --vida COLAB_MU_01
INICIAR.bat gestor mente-unificada-reanudar --vida COLAB_MU_01 --id USUARIO_REANUDAR_01 --esperar 40
INICIAR.bat gestor mente-unificada-pedir --vida COLAB_MU_01 --id USUARIO_DATO_01 --situaciones "[{\"modo\":\"dato\",\"valor\":13}]" --retorno omit --esperar 40
INICIAR.bat gestor mente-unificada-pausar --vida COLAB_MU_01 --id USUARIO_PAUSA_01 --esperar 40
INICIAR.bat gestor mente-unificada-guardar --vida COLAB_MU_01 --id USUARIO_GUARDAR_01 --esperar 40
INICIAR.bat gestor mente-unificada-detener --vida COLAB_MU_01 --id USUARIO_STOP_01 --esperar 40
```

Use identificadores nuevos para experiencias nuevas: repetir el mismo ID no repite una acción ya registrada. No reenvíe ciegamente una acción de resultado incierto. «Pausar» conserva sin ticks; «reanudar» permite avanzar entre peticiones. El estado mostrado es una observación cacheada con antigüedad, no el tick instantáneo.

Para continuar, ejecute otra vez `mente-unificada-iniciar` sobre **la misma identidad personal**, no `abrir` de nuevo. La vida requiere snapshot completo, SQLite, colas y artefactos: **no use una bifurcación ordinaria ni copie sólo RAW/clocks**. Para crear otra rama operativa use `mente-unificada-exportar` y `mente-unificada-importar` según `sistema/documentacion/GUIA_SERVICIO_PERSISTENTE_MU01.md`. El ejemplo5 rechaza preventivamente vidas persistentes en vez de producir una copia incompleta.

La protección temporal R3 es preparaciónP0, no regulación aprendida. La revisión de asociaciones es enseñanza explícita. Las cadenas de trabajo usan dos peticiones asistidas y archivos reales; no son un planificador autónomo. Silencio, rechazo, respuesta incorrecta e incertidumbre se conservan como resultados distintos. No se anuncian 65 significados, lenguaje general ni inteligencia general.

## Capacidades y perfiles anteriores

El mismo gestor conserva las funciones instaladas y perfiles complementarios, con sus propias vidas e historias. `INICIAR.bat gestor --help` muestra los comandos. Los cinco ejercicios existentes de `ejemplos/` permiten importar un ente, observar, utilizar una función, cambiar una experiencia y guardar/continuar dentro del dominio correspondiente. No ejecutan las suites científicas históricas completas.

`INICIAR.bat mente` continúa el contratoR9 anterior; `INICIAR.bat mente2` utiliza el contratoMA02. Un activo fuera de su dominio genera un error y se conserva: el lanzador no lo sustituye por un individuo favorable. Los auxiliares `MUFI_ACCESO_BASAL_*_READY` son participantes **distintos**, con uso material finito; no añaden sus conocimientos a MAIN.

## Qué incluye

- `motor/`: WHL oficial, intérpretes portátiles y dependencias necesarias; el intérprete3.12 separado sirve al entorno externo conservado, no decide por DEE.
- `sistema/`: gestor Cognitive completo, app, capacidades, contratos, organizaciones, documentación y persistencia; no sólo el delta de una campaña.
- `entes/`: estados completos seleccionados, genealogías y paquetes emparejados de servicio. Un checkpoint nativo se almacena una vez por corte en la distribución.
- `documentos/` y el Word de la raíz: documentación vigente y ciencia esencial disponible. Un documento describe; el estado operativo y los contratos determinan qué se puede continuar.
- `fuentes/`: código disponible para estudiar y modificar experimentos, sin recompilar el kernel congelado.
- `investigacion/`: resultados cerrados, primarios compactos, controles y recálculos. No son memoria accesible al participante ni un respaldo de toda la telemetría profunda.

Las rutas antiguas dentro de informes son localizadores históricos, no dependencias de esta copia. Para ejecutar aquí, anteponga `INICIAR.bat gestor` a los comandos del gestor. No cambie kernel/WHL ni originales; experimente sobre copias identificadas.

## Actualizaciones sin perder trabajo propio

Al finalizar una campaña en el equipo de investigación, después de guardar estados completos y cerrar el corte, ejecute `ACTUALIZAR.bat`. Se busca el origen hermano `DEE Cognitive System1.1`; `actualizaciones/COMO_ACTUALIZAR.md` explica cómo registrar cierre, manual y vidas nuevas. Se incorporan sólo diferencias cerradas, no campañas en curso.

En otro equipo no existe sincronización automática. Reciba un ZIP completo nuevo o un incremental y aplíquelo con `ACTUALIZAR.bat --aplicar archivo.zip`. El actualizador conserva `trabajo_personal/`, archiva versiones gestionadas anteriores y detiene conflictos en vez de sobrescribir cambios personales silenciosamente. Una actualización de código no rebobina vidas ni transfiere aprendizajes.

`CREAR_ZIP.bat` sella el corte ya copiado, sin ejecutar investigación. `entregas/`, respaldos y resultados personales no se anidan dentro del ZIP de colaboración. El paquete está destinado a una persona de confianza: todo es privado, sin publicación ni envío automático a servicios externos.
