# Criterios fijados antes de la validación — SDK0.1.0

Estado inicial: PENDIENTE en el paquete consolidado. Estos criterios no se cambian tras ver el resultado. La evidencia históricaP08 se referencia, sin puntuar automáticamente esta nueva copia.

K1 - Instalación: con los requisitos y el acceso al backend declarados disponibles, la persona importa el paquete en una escena limpia siguiendo la guía. No debe necesitar consultar el chat, adivinar archivos o editar el núcleo. Se registran pasos, asistencia requerida y bloqueos.
K2 - Enlace real: una observación del mapa llega al backend DEE oficial y devuelve una salida Native con ID y vida diagnóstica identificables. Un doble técnico no cumple este criterio.
K3 - Efecto observable: el cuerpo ejecuta esa salida una vez, produce el efecto fijado en el mapa de ejemplo y devuelve su consecuencia. Queda trazado observación -> Native -> acción/ACK -> efecto -> retorno.
K4 - Cierre y continuidad: la instancia guarda y cierra sin solicitudes ambiguas; se verifica una reapertura y un uso posterior breve si el SDK ofrece continuación persistente. Si no se valida, se declara por separado sin negar K2/K3.
K5 - Uso en mapa ajeno: el desarrollador adapta geometría/sensores/actuadores mediante la configuración documentada, sin tocar DEE, y obtiene otro ciclo real. Es portabilidad, no aprendizaje general de todo mapa.

El piloto básico de integración aprueba si K1-K3 se cumplen con las ayudas previstas. K4 y K5 tienen su resultado propio. Aprobar integración no equivale a demostrar aprendizaje nuevo, escalabilidad comercial o satisfacción de clientes.

Registra también tiempo de instalación observado, latencia, recursos, utilidad percibida y restricciones aceptables. No impongas ni prometas tres minutos de instalación o respuesta en tiempo real si no se midieron.

Una prueba realizada por Codex es VALIDACIÓN LOCAL, aunque use una escena limpia; no es una evaluación independiente externa. Prepara una ficha breve para uno o dos desarrolladores, pero no inventes participantes, respuestas ni aceptación comercial. No contactes a nadie sin una instrucción específica posterior.


## Registro obligatorio

Para cada K: resultado APROBADO / NO CUMPLE / BLOQUEADO / PENDIENTE, fuente/ID, asistencia, tiempos observados y límite. K1–K3 se evalúan con el backend y requisitos declarados disponibles. Preview, dobles técnicos, importaciónXML o hashes aislados no acreditanK2/K3. Si Native devuelve espera/null, se respeta y se informa el efecto real; no se cambia la salida para lograr movimiento. El cierre/reapertura y uso posterior deben observarse paraK4; la existencia de unaAPIrestore no lo aprueba. K5 exige otro mapa y ciclo real, no sólo editarconfig.
