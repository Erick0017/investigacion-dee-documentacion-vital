# Acceso adaptativo en el sistema 1.1

Componente opcional de investigación; no cambia el motor ni el predeterminado. Contrato: `contratos/ACCESO_ADAPTATIVO_01.json`. Estados listos: `AA01_ACCESO_LISTO_plus` y `AA01_ACCESO_LISTO_minus`, T45857, con contenido previamente adquirido, estrategia de acceso aprendida y entradas pendientes. Son ramas históricas explícitas, no el futuro de MAIN T47146.

Use el CPython3.13x64 ya instalado. No ejecute el instalador de nuevo. El iniciador admite `-PythonExecutable` cuando el entorno está fuera de `sistema/.entorno`. Desde la raíz del sistema, una inspección sin avance es:

```powershell
.\sistema\iniciar_sistema.ps1 -PythonExecutable 'RUTA_AL_ENTORNO_EXISTENTE\Scripts\python.exe' acceso-estado --vida AA01_ACCESO_LISTO_plus
```

Las operaciones y sus argumentos JSON fueron ejecutados mediante el gestor en procesos separados en49. En el modo interactivo se pueden pegar las siguientes líneas, que conservan el estado listo y consumen sólo la nueva rama:

```text
bifurcar AA01_ACCESO_LISTO_plus MI_PRUEBA_AA01 --modalidad CANDIDATE
experiencia --vida MI_PRUEBA_AA01 acceso-avanzar-episodio --parametros '{"stage":"access","max_seconds":90}'
experiencia --vida MI_PRUEBA_AA01 acceso-avanzar-episodio --parametros '{"stage":"received","max_seconds":90}'
experiencia --vida MI_PRUEBA_AA01 acceso-avanzar-episodio --parametros '{"stage":"use","max_seconds":90}'
guardar --vida MI_PRUEBA_AA01
restaurar MI_PRUEBA_AA01
experiencia --vida MI_PRUEBA_AA01 espanol-contexto --parametros '{"value":79,"method":"B"}' --max-segundos 90
```

El identificador de la hija debe ser nuevo. No se reinicia silenciosamente si ya existe. La primera consulta modifica el mundo; volver a ejecutar una etapa consumida no garantiza otra respuesta ni restaura la memoria. No consulte continuamente para “comprobar” conservación. `acceso-recuperar-receptor` no está admitido en el modo de uso inmediato: informa fuera de dominio en vez de reproducir una respuesta.

El código opaco recuperado no es una afirmación nueva en español. Las respuestas actuales de magnitud/espacio/contacto conservan sus contratos heredados; las traducciones se identifican como instrumento. No hay conversación libre o LLM interno.

MAIN E1_ACCESO_ADAPTATIVO_01 T47146 conserva sus seis funciones del último panel y su fallo receptor tardío. No seleccione un checkpoint distinto para cada pregunta y lo presente como una sola vida. Las ramas14/21 de receptor y las variantes read_only tienen ventajas y pérdidas diferentes. Consulte la continuidad y el informe antes de emplearlas.

La ficha de continuidad en la raíz identifica snapshots completos locales y hashes. El ZIP de análisis no los contiene y no permite restaurar las vidas por sí solo. No exporte ni publique el estado privado.
