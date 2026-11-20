# Arquitectura y separación

La frontera de confirmación conserva también los intentos fallidos: si una llamada admite entradas o evoluciona antes de arrojar una excepción, se registra un checkpoint FAILED con el estado alcanzado. El puntero activo se sustituye atómicamente y la promoción usa registro PREPARED/COMMITTED. Esto no equivale a una garantía ACID ante fallos físicos del dispositivo; una inconsistencia de diario se informa y no provoca un rebobinado silencioso.

Motor: el WHLoficial4.5.0, kernel27. La capa1.1 sólo administra preparaciones, protocolos, estados, interfaces y supervisión. No recompila ni modifica el motor. La transición física sigue siendo X(t+1)=F_v27(X(t), entradas admitidas).

sistema/ funciona sin laboratorio/, evidencia/, entregas/ ni CPC históricos. Incluye constructores, contratos y snapshots completos. Las colas pendientes, interfaces, cadencia del lector y progreso operativo se conservan en metadata del mundo, no se eliminan como telemetría. Los registros de experiencia no se consultan como tablas para decidir respuestas.

laboratorio/ conserva variantes y ejecutores nuevos. evidencia/ contiene datos, controles, diagnósticos y auditores. entregas/ nunca es origen de importación. El núcleo de recuperación bajo sistema/capacidades/core sólo se abre en la operación explícita probar-herencia; el CLI ordinario lo bloquea como fuente de respuestas.

Cada vida tieneID, worldID, perfil, padre, rama, snapshot, hash y tick. Una vista regional no crea materia. En los experimentos sociales A/B/C comparten el mismoRuntime; existe un único snapshot autorizado del mundo por checkpoint. Perfiles distintos no se comunican automáticamente. No se implementó puente externo entreRuntime.

Los escritores se excluyen por worldID. Se guardan snapshots nativos comprimidos, sin pickle ni código ejecutable incrustado. La carga verifica hashes y estado exacto, incluye colas y metadata. El diario y puntero deben coincidir; incoherencias interrumpen la carga sin restaurar un pasado favorable.

El autor de experiencias es externo. Un puerto puede estar preparado, un signo quedar adquirido y una respuesta ser nueva: son hechos distintos. El lector móvil es preparado y solicitado por el usuario. Las comparaciones adquiridas y mensajes se realizan mediante encuentros nativos. No hay política externa que lea el target y escriba la respuesta.

La preservación es acumulativa por perfiles.34familias son contratos auxiliares finitos, no34conocimientos simultáneos deE1. Las16filas documentales pendientes conservan su causa. Las referencias originales y sus correcciones permanecen en el registro.
