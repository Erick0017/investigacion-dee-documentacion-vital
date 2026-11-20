# Entorno externo: transporte, no política

`pendulum_worker.py` ejecuta **Gymnasium Pendulum-v1**, no una recreación propia de sus ecuaciones. Es un proceso separado del intérprete que importa DEE thinking. No importa snapshots, diarios ni código de DEE.

Cada línea JSON solicita una operación. `reset` acepta una semilla de auditor y la gravedad física del entorno; `step` recibe exclusivamente un torque solicitado, que se limita a [-2, 2] N·m y registra su saturación. `info`, `snapshot`, `restore` y `close` no seleccionan acciones. La neutralidad ante silencio pertenece al puente y debe fijarse antes del ensayo.

El sensor visible del entorno publicado entrega `[cos(theta), sin(theta), velocidad_angular]`, en float32. El puente puede usar un subconjunto fijo declarado; no debe utilizar el estado oculto ni la recompensa para calcular la acción adecuada. El worker no cuantiza, clasifica relaciones ni selecciona estímulos útiles. La recompensa se devuelve como consecuencia del modelo, no como actualización de una memoria nativa.

Un paso del entorno representa 0.05 segundos simulados, independiente de latencia del anfitrión. El episodio se trunca a los 200 pasos y requiere un `reset` explícito; eso no autoriza reiniciar el estado de DEE. La relación ticks DEE/paso y cualquier demora se congelan en el contrato del puente.

La instantánea exporta el estado físico de dos float64 como cadenas hexadecimal exactas, último torque, generadores aleatorios del entorno y espacios y atributos operativos de los envoltorios. `restore` exige versión de Gymnasium/NumPy y hash de fuente Pendulum compatibles; no reconstruye sólo a partir de la observación. Estos campos son estado de instrumentación y auditoría, no entradas accesibles al ente. Para almacenarlos en un metadato nativo que no admite float, se puede guardar el objeto JSON serializado como una cadena, sin descartarlos.

La prueba `test_worker.py` compara ocho pasos en dos procesos desde una instantánea exacta y comprueba la truncación y el efecto de gravedad. Sus torques son órdenes técnicas explícitas del investigador: **no son acciones de E1 ni evidencia de aprendizaje**.

Fuentes oficiales consultadas el 21 de octubre de 2026:

- [Contrato Pendulum-v1](https://gymnasium.farama.org/environments/classic_control/pendulum/).
- [Código publicado Pendulum](https://github.com/Farama-Foundation/Gymnasium/blob/main/gymnasium/envs/classic_control/pendulum.py).
- [Metadatos oficiales de instalación](https://github.com/Farama-Foundation/Gymnasium/blob/main/pyproject.toml).

No se declara robot industrial, LiDAR, fricción modelada ni realismo físico fuera del modelo publicado. Los detalles efectivos y hashes de la versión instalada deben registrarse en el informe técnico generado, no deducirse de la rama `main` de la documentación.

## Corte técnico ejecutado

La ruta realmente comprobada utiliza el Python **3.12.14 incluido en las dependencias de Codex**, no el Python 3.11 explorado inicialmente. Gymnasium **1.4.0** y farama-notifications **0.0.6** están en `external/deps`; NumPy **2.3.5** y typing-extensions **4.16.0** provienen del runtime externo existente. La identidad exacta, ubicaciones y hashes están en `PROVENIENCIA_EXTERNA.json` de evidencia. Cloudpickle no está instalado en esa ruta: el recorrido síncrono Pendulum y su persistencia JSON se ejecutaron sin utilizarlo; no se anuncia disponibilidad general de todos los componentes de Gymnasium.

`WORKER_PRUEBA_TECNICA.json` registra la ejecución real del transporte y de la continuación exacta entre procesos. `recalcular_externo.py` puede comprobar la cuantización y transducción archivadas sin importar DEE. La opción `--replay` repite únicamente el entorno publicado con los torques archivados; es **reproducción externa**, no una nueva prueba nativa ni nuevo aprendizaje.

Para los ensayos E1 ejecutados, el sensor utiliza solamente `sin(theta)`: `q = max(1, min(145, round(73 + 40*sin(theta))))`. Se descartan coseno y velocidad angular. Cada paso solicita tres entradas físicas a la comparación ya preparada con referencia heredada; se conservan rechazos. El actuador traduce SEM1 activo +X a +2 N·m, −X a −2 N·m; otras salidas o silencio producen cero fijo. No se calcula torque óptimo desde el ángulo ni se entrega recompensa como corrección de memoria. Esta preparación no demuestra que E1 haya aprendido una política de estabilización del péndulo.
