# Incorporaciones y continuidad

Se añadieron al gestor existente `habitat-estado --vida ECO_EXT_01` y `habitat-externo --vida ECO_EXT_01 --pasos 1`. El primero es pasivo; el segundo es una operación externa explícita con proceso de entorno fijo y estado completo persistente. No selecciona un target ni cambia de vida. Su excepción al cerco de procesos sólo pertenece a ese instrumento opt-in; los comandos ordinarios mantienen el cerco. El módulo no importa laboratorio ni evidencia.

El contrato identifica Python, worker y fuente Pendulum por hash. Las dependencias externas se conservan localmente en sistema/runtime/habitat_externo_deps; NumPy pertenece al intérpretebundled. Cloudpickle no está disponible: el camino síncrono probado no lo ejercita, y no se anuncia soporte general de Gym.

Prueba real INCORPORACION_CLI_23: ECO_EXT_01 T6100→6167, índice24→25,67ticks, guardado y lectura en otro proceso. No T0 ni reset silencioso. Conservar el snapshot completo indicado en CONTINUIDAD y esas dependencias. Para resetear un episodio del entorno tras200 pasos use `--reiniciar-entorno` explícito; eso no reinicia DEE.

MAIN T7509 se conserva como futuro adverso, no como nuevo predeterminado. Las ramas listas AA y E1_SOCIAL_11 siguen protegidas y separadas. No se incorporan respuestas de controles a MAIN, ni se cambia NSM65. Los procedimientos de estrés, comunicación y autopsia permanecen ejecutables en laboratorio con sus fuentes exactas y controles, sin declararlos funciones autónomas del ente.
