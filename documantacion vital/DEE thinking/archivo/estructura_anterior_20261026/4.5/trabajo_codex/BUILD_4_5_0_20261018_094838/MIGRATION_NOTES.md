# Migración y coexistencia 4.0 → 4.5

La importación continúa siendo `dee_thinking` y el target CMake `DEE::thinking`.
Las clases Runtime/BasalWorld/OrganizationalWorld, protocolos H1–H4/F1–F2,
catálogo, composición y sesiones 4.0 mantienen sus nombres. `API_DIFF.json`
compara las instalaciones efectivamente probadas; no promete ABI universal.

## Física y preparaciones

La fuente v27 y las otras fuentes de transición heredadas se conservan.
El constructor Runtime directo no instala recetas cognitivas ni modifica
clocks. Importar la biblioteca no crea un mundo. Observación pasiva y sondas
físicas son operaciones diferentes. Un fallo de consulta no dispara limpieza.

Las preparaciones nuevas tienen IDs `repertoire.cpc5.v1` e
`integrated_u0.cpc7.v1`. No sustituyen con el mismo ID los aparatos históricos
N47/N67/N127/N131. N se conserva durante una trayectoria. Cualquier cambio
de geometría o recursos es una preparación nueva, no una migración física.

## Snapshots

El lector nativo heredado admite los formatos Runtime1/2 y el formato
organizacional. Un snapshot operacional conserva también canales, cola,
recibos y progreso. La sesión4.5 añade sólo metadata JSON y un descriptor
inerte de preparación, no reconstruye ni reenseña al cargar.

En el adaptador CPC7 seleccionado, ese progreso es el de los protocolos nativos.
No se reconstruyen retrospectivamente capturas ni el journal externo Python del
runner histórico (`prior_protocol_queries_not_reconstructed=true`). La prueba
del snapshot real T204→472 compara física y operativo; no promete restaurar
todos los archivos auxiliares de cualquier aplicación histórica.

`save_snapshot` puede comprimir sin pérdida con gzip. La capa de almacenamiento
comprueba CRC, tamaños y SHA cuando se proporciona; no usa pickle ni ejecuta
código de los datos. La carga comprimida está acotada y el original no se edita.

Las rutas `std::string` del snapshot/traza nativos se interpretan en4.5 como UTF-8
y se convierten al tipo de ruta de Windows antes de abrir/reemplazar. Esta corrección
repara el fallo comprobado con nombres japoneses. No cambia los bytes del formato
ni la física. Un consumidor C++ que producía rutas codificadas en una página local
debe convertirlas explícitamente a UTF-8; el dominio ASCII4.0 permanece. Las cuatro
conversiones están separadas de las secciones de transición en el diff auditado.

Los adaptadores de metadata CPC son explícitos y opt-in para perfiles concretos.
Un snapshot desconocido, otra geometría o una identidad incompatible se rechazan:
no se interpreta silenciosamente un cuerpo65-puertos como otro69-puertos.
Una carga4.0 →4.5 conserva física y estado operativo; la versión del sobre
documental puede diferir. Los objetos comparados y exclusiones están registrados
en los informes diferenciales. Nunca se descartan RAW/clocks para igualar metadata.

## Repertorio, lectura y revisión

Las formas son correspondencias opacas entre dos clases direccionales. K65 no
significa dominio de65primitivas NSM. Las experiencias introducen consecuencias
actuales por interfaces; no se precarga un mapa de respuestas en la sesión.
Una consulta es una sonda material y puede cambiar el estado. Primero se conserva
su recibo y después se evalúa la ventana declarada; silencio, ocupado, rechazo,
cero observado y fuera de dominio tienen estados separados.

M1 (`double_teacher`) necesita un segundo docente. M2 (`symmetric_counterflow`) añade dos
contraflujos antes de una nueva experiencia. Son protocolos externos declarados
con transformación nativa, no políticas generales aprendidas de regulación.
Los controles fuera de ruta igualan dosis, no garantizan inocuidad para cualquier
K: una ruta sham puede atravesar otra memoria y debe validarse en esa geometría.

## Integración y lenguaje

U0 comienza sin las asociaciones objetivo. La comparación y las posibilidades
de pregunta están preparadas; su utilización concreta depende del estado físico.
La regla no demuestra una elección general aprendida de cuándo/a quién preguntar.
Las guardas son interceptores fijos, no atención aprendida. El horizonte comprobado
es finito y consta en VALIDATION_REPORT.json.

El parser español reconoce comandos estructurados. El renderer presenta lecturas,
no calcula respuestas desde el historial de enseñanza. `ENTE`, `INSTRUMENTO` e
`INTERPRETACIÓN` conservan procedencias distintas. El catálogo NSM documenta65
entradas y sus estados de evidencia; el portado de software no acredita nuevas
adquisiciones semánticas.

Los perfiles experimentales de ausencia y lectura remota, cuando se distribuyen,
permanecen separados del constructor integrado; sus pruebas y límites propios
no se transfieren automáticamente a U0 ni a todos los backends.
