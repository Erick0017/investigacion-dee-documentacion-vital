"""One concise scientific account and the affected manual sections.
No runtime import, simulation, target search or changes to historical evidence.
"""
from pathlib import Path
import hashlib,json,re
L=Path(__file__).resolve().parent;R=L.parents[2];E=R/'evidencia/campanas/CONSOLIDACION_EVOLUCION_E1_CICLO_02'
M=json.loads((E/'CALCULOS_REPETIBLES.json').read_bytes());C=json.loads((R/'CONTINUIDAD_CICLO02.json').read_bytes());O=E/'EXPORTACION';O.mkdir(exist_ok=True)
def life(name):return next(x for x in C['lives']if x['life_id']==name)
def readable(text):
    fixes={'Ciclo02':'Ciclo 02','WHL4.5.0':'WHL 4.5.0','las34familias':'las 34 familias','reconstrucciónT0':'reconstrucción T0','aT':'a T','hastaT':'hasta T','enT':'en T','N67':'N67','comparador anteriorTM':'comparador anterior TM','actual0..100':'actual 0..100','útiles; no':'útiles; no','9/9 decisiones/acciones':'9/9 decisiones/acciones','no32aprendizajes':'no 32 aprendizajes','realizó8actualizaciones':'realizó 8 actualizaciones','con191entradas':'con 191 entradas','RAW/clocks coincidan':'RAW/clocks coincidan','de carga5':'de carga 5','ocupación341/340':'ocupación 341/340','con297664':'con 297664','sin-record342':'sin-record 342','carga0':'carga 0','fase3':'fase 3','no hay P2 aprendido':'no hay P2 aprendido','positivo previo se recupera4/4y':'positivo previo se recupera 4/4 y','negativo nuevo permanece4/4':'negativo nuevo permanece 4/4','componente fijo':'componente fijo','preparación de dos capas190permite':'preparación de dos capas 190 permite','capa191y':'capa 191 y','contenido193':'contenido 193','previa192es3/4':'previa 192 es 3/4','normal210se':'normal 210 se','transformadoras y4usos':'transformadoras y 4 usos','ambos contenidos reservados110/113 tienen4usos':'ambos contenidos reservados 110/113 tienen 4 usos','cinco recorridos después:160/1624/4frente a1610/4al':'cinco recorridos después: 160/162, 4/4 frente a 161, 0/4 al','X+7yX+Z+7en posicionesvecinas':'X+7 y X+Z+7 en posiciones vecinas','X+Z+14':'X+Z+14','exactamenteRAW':'exactamente RAW','opuestas de7pasan':'opuestas de 7 pasan','dirección0y carga14':'dirección 0 y carga 14','nueva consulta. Su pasado anterior a21108no':'nueva consulta. Su pasado anterior a 21108 no','mensajes230conserva':'mensajes 230 conserva','revisión240/242':'revisión 240/242','permite4/4actualizaciones':'permite 4/4 actualizaciones','a2/4en':'a 2/4 en','sham241':'sham 241','lateral270permite':'lateral 270 permite','a297938':'a 297938','remotos280/281no':'remotos 280/281 no','sinB272no':'sin B 272 no','corte273tiene':'corte 273 tiene','intervención330redirige':'intervención 330 redirige','lectorYAexistente':'lector ya existente','En3usos':'En 3 usos','negativo-z26, positivo-z23y':'negativo-z26, positivo-z23 y','sham331conserva':'sham 331 conserva','pulso332conserva':'pulso 332 conserva','privada52,330pierde':'privada 52, 330 pierde','de queBrespondiera':'de que B respondiera','alcanzaT21711con':'alcanza T21711 con','comparadores anteriores':'comparadores anteriores','asistenciaP0y utilización condicionadaP1':'asistencia P0 y utilización condicionada P1','iniciativa/estrategiaP2':'iniciativa/estrategia P2','ni65significados':'ni 65 significados','noP2':'no P2','Episodioexterno198/200':'Episodio externo 198/200','AcciónXY140en':'Acción XY140 en','deMAIN':'de MAIN','reemplazaE1_SOCIAL_11ni':'reemplaza E1_SOCIAL_11 ni','el código anterior':'el código anterior','delSO':'del SO','CPython3.13':'CPython 3.13','ya existente':'ya existente','producev27':'produce v27','torque0no':'torque 0 no','torque2saturado':'torque 2 saturado','selector020–041no':'selector 020–041 no','SHA256originales':'SHA-256 originales','Word1.6':'Word 1.6','gestionar.py` y':'gestionar.py` y','varianteP0con':'variante P0 con','panelbreve':'panel breve','Manual1.6':'Manual 1.6','previa y':'previa y','aE1':'a E1','noP2por':'no P2 por','de0y':'de 0 y','señal0':'señal 0','suministrados a':'suministrados a','v27conserva':'v27 conserva','Bcompara':'B compara','no65':'no 65'}
    fixes.update({'corteT20927':'corte T20927','control330':'control 330','buffers21309':'buffers 21309','con330':'con 330',
      'actuales0..100':'actuales 0..100','C02_GATE050:9/9':'C02_GATE_050: 9/9','utilidad4':'utilidad 4','utilidad10':'utilidad 10',
      'omitido051':'omitido 051','ruta053:2/9':'ruta 053: 2/9','utilidad−5':'utilidad −5','anulada052:salidas':'anulada 052: salidas',
      'MAIN:21/21':'MAIN: 21/21','son21':'son 21','reservadas140/141:tras':'reservadas 140/141: tras','desgaste6o13':'desgaste 6 o 13',
      'objeto9':'objeto 9','físicas11o18':'físicas 11 o 18','sham142/143':'sham 142/143','y8semillas':'y 8 semillas','regulaciónR2':'regulación R2',
      'carga7':'carga 7','dirección0':'dirección 0','estacionarias070/071':'estacionarias 070/071','privadaB':'privada B','transitorios080/081':'transitorios 080/081',
      'sham082':'sham 082','En130–133':'En 130–133','tiene191':'tiene 191','pendientes;0658…pre-arm tiene0aunqueRAW':'pendientes; 0658… pre-arm tiene 0 aunque RAW',
      'En340/343':'En 340/343','los191':'los 191','sham341':'sham 341','297664sitios':'297664 sitios','record342':'record 342','T4435con340':'T4435 con 340',
      'MAIN120':'MAIN 120','frente a0/4':'frente a 0/4','T21035:preestado':'T21035: preestado','diagnóstico221reproduce':'diagnóstico 221 reproduce',
      'T21118:contribuciones':'T21118: contribuciones','adicionales21170':'adicionales 21170','desgaste1':'desgaste 1','ramasC2':'ramas C2',
      '3.13ya':'3.13 ya','verificaRAW':'verifica RAW','simularv27':'simular v27','realizó21de21':'realizó 21 de 21 ',
      'produjo9de9':'produjo 9 de 9','produjo2de9':'produjo 2 de 9','21oportunidades':'21 oportunidades','fue341o340':'fue 341 o 340',
      'a297664en':'a 297664 en','asistidaP0y':'asistida P0 y','condicionadaP1':'condicionada P1','recuperaciónP2':'recuperación P2',
      'privada52':'privada 52','T3312y':'T3312 y','0y no':'0 y no','3.13x64':'3.13 x64','programaNSM65ni':'programa NSM65 ni',
      'Bcompara':'B compara','YAexistente':'ya existente'})
    for a,b in fixes.items():text=text.replace(a,b)
    # Numeric citations remain IDs; add missing word-space only where prose is unambiguous.
    text=re.sub(r'(?<=\d)(?=(?:entradas|eventos|con|familias|actualizaciones|usos|individuos|entes|formas|significados|pasos|seconserva)\b)',' ',text)
    text=re.sub(r'(?<=\d)(?=(?:y el|y la|pero|conserva|permite|frente)\b)',' ',text)
    return text
def save(name,text):(O/name).write_text(readable(text),encoding='utf8')
triple=life('E1_CICLO02_SEPARACION_TRIPLE_01');main=life('E1_CICLO02_MAIN')
report='''# Consolidación y evolución real de E1 — Ciclo02

Resultado: integración operativa acotada, no mente general. Se admitieron las cinco funciones IC01 en el gestor existente y se incorporaron mecanismos nuevos con estados utilizables. No se modificaron v27 ni el WHL4.5.0, no se reconstruyó Cognitive y no se reejecutaron las34familias CPC. Los perfiles y pendientes anteriores conservan sus alcances; la biblioteca no es el conocimiento simultáneo de E1.

## 1. Qué organización y qué continuidad se ensayaron

El padre principal se eligió antes de evaluar: E1_INTEGRADO_RECUPERACION_01 T17155, con comparación, contenido social recuperado y puente persistente. E1_CICLO02_MAIN es su bifurcación exacta, no una reconstrucciónT0 ni una fusión de memorias. Llegó realmente aT21711, con pérdidas que se conservan. El predeterminado E1_SOCIAL_11 T3154 y el adverso IC01MAIN T3899 mantienen sus hashes anteriores.

El mundo N67 contiene soportes de referencia/comparación, el comparador anteriorTM, un selector finito, B con referencia física propia y soportes sociales. Son regiones/participantes del mismo Runtime, no neuronas ni varias mentes completas por tener varios puertos. Los snapshots guardan el mundo una vez con sus pertenencias, clocks, canales, colas y progreso. La puerta escalar y Pendulum son entornos externos declarados, no nuevas leyes v27 ni hábitat endógeno cerrado.

Se conservó un corteT20927 ANTES de las nuevas actualizaciones adversas. Sus futuras bifurcaciones son otras historias, no reparaciones retroactivas de MAIN. La continuación operativa de tres códigos se preparó desde ese padre y experimentó sus propios acontecimientos; no recibió el estado entrenado del control330. La igualdad de sus buffers21309 con330 es reproducción técnica, no una réplica de aprendizaje independiente ni identidad de toda la agenda.

## 2. Aprendizaje que ayudó a actuar

La puerta ofrece fuerzas actuales0..100. Un intento real modifica la resistencia ambiental mediante el desgaste declarado; retirada y acción anulada no lo hacen. Sólo vuelve el desgaste realmente producido como recurso material, nunca la resistencia, la utilidad o la acción correcta. El comparador/actuador, la fase y la ley ambiental están preparados. La referencia acumulada y las emisiones posteriores evolucionan en DEE.

- C02_GATE050:9/9 decisiones/acciones útiles, utilidad4. Retorno omitido051 y mismo aporte fuera de ruta053:2/9 útiles y utilidad−5. Acción anulada052:salidas físicas presentes, pero ninguna acción efectiva útil; no se atribuye esa anulación a una decisión del ente.
- MAIN:21/21 oportunidades válidas y útiles a lo largo de una sola historia, utilidad10. No son21individuos.
- Historias reservadas140/141:tras desgaste6o13, el mismo objeto9 encuentra referencias físicas11o18 y produce decisiones opuestas, ambas útiles en su mundo. Omisión y sham142/143 conservan la tentativa incorrecta en el mundo desgastado. El anfitrión no escoge esa dirección.
- Se conservaron usos después de nuevos valores, desgastes y bloques sociales. Referencias externas siempre-intentar, retirar, neutral y8semillas aleatorias se calculan aparte; ninguna controlaE1. Se comparten estado ambiental inicial y perturbaciones, no un futuro forzado tras acciones distintas.

Esto demuestra adquisición/utilización de una referencia contextual que mejora acciones en esta tarea. No demuestra descubrimiento de la ley de control, política de Pendulum competente, inversión general de reglas ni regulaciónR2. La igualdad produce una forma material de carga7 y dirección0 fuera del codec de actuación, no silencio ni NO aprendido (145/146).

## 3. Interferencia social: corrección real y límite separado

Las guardas estacionarias070/071 impidieron la entrada, pero también la función privadaB: no son una corrección válida. Dos contraflujos cero transitorios080/081 mantienen aplicadas ambas entradas back.record de carga5 y conservan el mensaje de cada signo. El sham082 produce expansión; no bastó igualar la dosis. En130–133 cada vida realizó8actualizaciones privadas correctas, no32aprendizajes independientes.

Se comprobó también el estado histórico correcto de agenda: fa46… tiene191entradas pendientes;0658…pre-arm tiene0aunqueRAW/clocks coincidan. En340/343, con los191eventos conservados, la protección mantiene ambos signos privados hastaT4425 y terminaT4435con ocupación341/340. El sham341 terminaT3899con297664sitios ocupados; sin las entradas record342 terminaT4435con340. Ambos record y ambos protectores se aplican. Ésta es eficacia P0 en el régimen medido, no atención aprendida ni inmunidad infinita.

El selector corporal termina en carga0 en protegidos y sin-record; el control de guardas no resolvió su agotamiento. Las observaciones de puertos sólo se puntúan en fase3: una foto fuera de fase no se cuenta como olvido.

## 4. Información, recuperación y tres soportes utilizables

La recuperación asistida IC01 se conserva. Los nuevos accesos preposicionados aportan ceros antes de una pérdida: ambos contenidos reservados110/113 tienen4usos posteriores, mientras sham/ausencia/no-contenido no recuperan ese contenido. En MAIN120 el positivo previo se recupera4/4y el negativo nuevo permanece4/4; en sham/ausencia se pierde sólo el acceso positivo. No se reenseña la palabra, signo o referencia.

Un recurso ancestral siguió siendo útil cinco recorridos después:160/1624/4frente a1610/4al desviarlo. No se infiere una identidad única de portador sólo por igual carga. La preparación de dos capas190permite dos consultas transformadoras y4usos, frente a0/4con una capa191y sin contenido193. El control sin pérdida previa192es3/4, no perfecto. La variante normal210se guardó, recargó y continuó en otro proceso hasta cinco usos. Son recursos finitos; el operador inicia preguntas y prepara accesos, no hay P2 aprendido.

Dos pérdidas diferentes se localizaron con estados completos:

1. T21035:preestado X+7yX+Z+7en posicionesvecinas pasan a X+Z+14. La dirección cambia y el código deja de ser legible por separado; no se demostró borrado global. El diagnóstico221reproduce exactamenteRAW/clocks/interfaces/agenda/recibos/contadores de la continuación original.
2. T21118:contribuciones opuestas de7pasan a dirección0y carga14. Ocurre tanto con nuevas entradas como sin ellas, antes de las entradas adicionales21170. No puede explicarse ese primer fallo sólo por la nueva consulta. Su pasado anterior a21108no se asigna por coincidencia de cargas.

El desvío de mensajes230conserva el código anterior durante una actualización, pero pierde funciones después. Su revisión240/242, que desvía productos de los recursos de giro, permite4/4actualizaciones frente a2/4en el sham241, sin conservar siempre el código antiguo. Se incorporó esa variante con sus pérdidas.

La codificación lateral270permite dos códigos separados al principio, pero posteriores exposiciones pierden acceso y expanden la ocupación a297938. Los soportes remotos280/281no corrigen el problema. El control sinB272no crea el código lateral; el corte273tiene un futuro adverso propio. No se convirtió esa arquitectura en una solución estable.

La intervención330redirige con dos pulsos cero una contribución negativa ya transformada a un lectorYAexistente, y evita su anulación con el positivo. En3usos posteriores conserva negativo-z26, positivo-z23y el nuevo positivo lateral. El sham331conserva sólo el lateral; un pulso332conserva el positivo pero no recupera el uso negativo. No se suministra contenido ni se cambian lectores según la respuesta. Tras otra experiencia privada52,330pierde el nuevo acceso lateral, pero conserva ambos anteriores durante nueva adquisición escalar y usos posteriores. Este contraejemplo no se ocultó.

La operación equivalente se incorporó al gestor como separar-soportes y se programó ANTES de queBrespondiera. E1_CICLO02_SEPARACION_TRIPLE_01 alcanzaT21711con tres códigos usables después de adquirir desgaste1, utilizar dos comparadores anteriores y continuar el entorno externo. Hay cuatro usos de los tres códigos después de la restauración; el primer uso anterior a ella tiene sólo dos. Esto es asistenciaP0y utilización condicionadaP1, no iniciativa/estrategiaP2, tres palabras nuevas ni65significados.

## 5. Qué queda utilizable y qué no

| Vida actual | Tick | Dominio accesible comprobado | Pérdida o límite |
|---|---:|---|---|
| E1_SOCIAL_11 |3154|Predeterminado heredado protegido|Sin sondas nuevas; no hereda ramasC2|
| E1_CICLO02_MAIN |21711|Referencia de puerta y mensaje negativo; continuidad|Antiguo positivo pierde acceso|
| E1_CICLO02_SEPARACION_TRIPLE_01 |21711|Tres códigos separados, referencia nueva y comparadores anteriores|Futuras actualizaciones sociales limitadas; noP2|
| E1_CICLO02_RETENCION_01 |21510|Dos códigos anteriores tras nueva consecuencia|No incluye mensajes nuevos de otras ramas|
| E1_CICLO02_COMUNICACION_01 |22783|Actualización social protegida y referencia de puerta|No conserva todo el repertorio antiguo|
| E1_CICLO02_LATERAL_LOCAL_01 |21309|Código lateral nuevo|Perdió acceso al positivo anterior|
| C02_CAPAS_210_OPERATIVO_R2 |17155|Acceso finito de dos capas, cinco usos|Episodioexterno198/200; reset explícito del entorno|
| C02_SELECTOR_USO_151 |3431|AcciónXY140en frontera finita|No selector actual deMAIN ni política general|

No se promovió globalmente ninguna rama. Los cinco mecanismos IC01 y los nuevos procedimientos se admiten por dominio; el catálogo completo conserva los demás estados históricos sin convertirlos en integrados. El mismo gestor carga, usa, guarda, recarga y continúa. El lanzador PowerShell está bloqueado por la política de scripts delSO; se utiliza el CPython3.13ya existente, sin alterar esa política ni reinstalar el motor.

Las rutas, fases, recursos y oportunidades las prepara el investigador. La adquisición escalar, las transformaciones de portadores y las emisiones las producev27. El puente aplica una transducción fija y puede sumar/cancelar/saturar contribuciones: torque0no equivale a silencio y torque2saturado no prueba la utilidad independiente de cada código. No hubo nuevo aprendizaje NSM65, YO/TÚ funcional, lenguaje general, control competente de Pendulum ni detector aprendido de pérdida. Las pruebas del selector020–041no proporcionan una estrategia de acceso sostenida.

## 6. Evidencia y alcance de la entrega

Los datos de todos los ensayos, también los negativos y errores instrumentales, se conservan localmente. Los archivos PRIMARIOS son extracciones lossless de subárboles JSON, no bytes idénticos a los JSON completos; contienen rutas, SHA256originales y localizadores/hash de partes omitidas. Los testigos seleccionados sí conservan bytes completos de snapshots originales. Los diagnósticos capturados en medio de una operación anfitriona se distinguen de checkpoints operativos en fronteras de comandos.

El recálculo portátil verificaRAW/clocks enteros, decisiones, efectos ambientales declarados, señales y controles sin importar el motor ni simularv27. El libro de recibos distingue solicitudes nuevas, aplicaciones de solicitudes ya pendientes y rechazos; no se mezclan esos denominadores. Se conserva contexto suficiente mediante testigos y fuentes omitidas localizables; no se afirma una cartografía exhaustiva ni linajes únicos tras encuentros.

Este ZIP es un análisis con delta de la capa Cognitive, no un respaldo operativo autosuficiente ni otra copia del motor. Los estados completos, interfaces, colas y progreso del puente necesarios para continuar cada vida están en los localizadores de CONTINUIDAD_CICLO02.json. El Word1.6 fue actualizado realmente; la comprobación estructural no sustituye el render visual, cuyo resultado se informa aparte. La verificación externa identifica el ZIP exacto, no un directorio anterior.
'''
save('INFORME_CIENTIFICO.md',report)
sections=[
 {'title':'Corte operativo y vidas que no deben confundirse','paragraphs':[
  'La continuación principal E1_CICLO02_MAIN llegó realmente aT21711, con su futuro adverso conservado. E1_CICLO02_SEPARACION_TRIPLE_01 también está enT21711pero tiene otra genealogía futura y otro estado; no se intercambian sus conocimientos por coincidir el tick. El segundo se ofrece como complemento operativo acotado, no como nuevo predeterminado. E1_SOCIAL_11 permanece protegido enT3154.',
  'El complemento de separación experimentó su propio mensaje privado, recuperó el uso de una contribución anterior y conservó tres códigos separados después de una nueva consecuencia escalar y dos comparaciones anteriores. E1_CICLO02_RETENCION_01 está enT21510con dos códigos anteriores; E1_CICLO02_COMUNICACION_01 está enT22783con actualización social y pérdidas antiguas. E1_CICLO02_LATERAL_LOCAL_01 T21309conserva sólo su código lateral nuevo. Los localizadores y hashes completos están en CONTINUIDAD_CICLO02.json, junto al manual.']},
 {'title':'Decisiones más útiles mediante historia adquirida','paragraphs':[
  'En una tarea escalar preparada, una acción real desgasta la oportunidad ambiental y el desgaste vuelve como experiencia material. DEE adquiere una referencia física y modifica una decisión posterior. El retorno no contiene la resistencia, la utilidad ni la respuesta correcta. La ley de comparación y el actuador están preparados; no se atribuye al ente haberlos inventado.',
  'MAIN realizó21de21oportunidades válidas y útiles. En el contraste inicial, retorno intacto produjo9de9usos útiles, mientras omitirlo o aportarlo fuera de ruta produjo2de9. Historias con desgastes diferentes produjeron decisiones opuestas para el mismo objeto9. Es adquisición y uso contextual, no política competente de Pendulum, descubrimiento de leyes ni regulaciónR2. Una igualdad genera una forma material fuera del codec de acción; no se traduce automáticamente como silencio o negación.']},
 {'title':'Protección social que conserva la comunicación','paragraphs':[
  'Dos contraflujos cero preparados reducen la interferencia de las entradas históricas de registro sin impedir su admisión. Se verificó comunicación privada de ambos signos y ocho actualizaciones en cada una de varias vidas de ensayo. No son treinta y dos individuos independientes ni atención aprendida.',
  'La prueba se extendió al estado histórico con191entradas futuras comprometidas: se conservaron los signos hastaT4425y la ocupación final fue341o340, frente a297664en su control fuera de ruta. El selector corporal terminó sin carga útil también en el control sin esas entradas. La protección corrigió una interferencia, no todos los fallos de acceso ni el aprendizaje de una política.']},
 {'title':'Recuperación sin reenseñanza y asistencia que permanece','paragraphs':[
  'La recuperación asistida anterior sigue admitida. Los recursos genéricos preposicionados permiten utilizar contenido adquirido sin una reparación decidida después de observar el fallo. Ambos contenidos reservados tuvieron cuatro usos posteriores, con controles negativos. La variante de dos capas se cargó, usó, guardó, restauró y continuó; sus recursos siguen siendo finitos y el operador inicia las preguntas.',
  'En un encuentro se localizaron dos contribuciones de signos opuestos que perdían legibilidad independiente. Dos pulsos cero redirigen una contribución ya presente hacia un lector existente y evitan esa anulación. El complemento de separación conserva tres códigos y los utiliza tras otra adquisición escalar. Los ceros no aportan la palabra, signo o referencia anterior. Es preparación asistidaP0y utilización local condicionadaP1; no se demostró una estrategia de recuperaciónP2 ni iniciativa general aprendida.']},
 {'title':'Ganancias locales, pérdidas y perfiles complementarios','paragraphs':[
  'El desvío espacial de mensajes con transformación de productos conserva nuevas actualizaciones dentro de su dominio, pero no preserva siempre las anteriores. La codificación lateral por sí sola funciona en el primer episodio y después puede perder acceso o expandir la actividad. Los soportes remotos ensayados no corrigieron ese fallo. Los futuros negativos permanecen disponibles.',
  'Una continuación de separación conservó los códigos anteriores después de otra experiencia privada52, pero perdió el acceso al mensaje lateral nuevo. No se declara aprendizaje acumulativo arbitrario ni estabilidad ilimitada. Esa pérdida no cancela la recuperación acotada comprobada, ni se oculta reemplazando el individuo por un checkpoint favorable.',
  'El selector finito listo se conserva en E1_SELECTOR_CONSERVADO_C02 T3312y su utilización efectiva en C02_SELECTOR_USO_151 T3431. El corte anterior IC01_SISTEMA_NATIVO_163 tiene carga0y no se anuncia como selector listo. Nada de ello se suma ficticiamente al conocimiento actual deMAIN.']},
 {'title':'Continuar con el mismo gestor','paragraphs':[
  'Utilice el CPython3.13x64 ya instalado que identifica el campo python_executable de CONTINUIDAD_CICLO02.json. La ejecución del lanzador PowerShell está bloqueada por la política delSO; no se cambió esa política. La llamada directa a sistema/gestionar.py está comprobada y no necesita otra instalación.',
  'Ejemplos: integrado-estado --vida E1_CICLO02_SEPARACION_TRIPLE_01; integrado-externo --vida E1_CICLO02_SEPARACION_TRIPLE_01 --pasos 1; guardar --vida E1_CICLO02_SEPARACION_TRIPLE_01. Cada interacción modifica y guarda la historia real; un proceso nuevo restaura el mismo mundo, sus colas y el entorno externo.',
  'Para investigar, bifurque una vida con un identificador nuevo. No active automáticamente una candidata ni retroceda MAIN. Las preparaciones adicionales se programan mediante integrado-experiencia: acceso-previo, acceso-consultar, proteger-retorno, proteger-mensaje, preparar-lateral y separar-soportes, además de las experiencias anteriores. La guía instalada declara precondiciones y límites. Los paquetes de análisis no sustituyen los snapshots completos locales.']},
 {'title':'Interpretación y límites científicos','paragraphs':[
  'Una lectura ausente no prueba borrado global; una dirección nula con contenido tampoco equivale a negación o silencio. Se verificaron encuentros, controles y continuaciones, conservando enteros exactos y diferenciando observación pasiva de preguntas materiales. No se resolvió la procedencia única de toda contribución anterior por coincidencia de cargas.',
  'No se elevaron las entradas del programaNSM65ni se atribuyó conocimiento de sesenta y cinco significados aE1. No se demostró lenguaje general, YO/TÚ funcional, conciencia, mente general o control competente del simulador. Las nuevas capacidades son mecanismos y vidas físicamente ejecutables con dominio explícito.']}
]
for section in sections:section['paragraphs']=[readable(t)for t in section['paragraphs']]
(E/'RESULTADOS_INCORPORADOS.json').write_text(json.dumps({'manual_sections':sections,'source':'CALCULOS_REPETIBLES.json and CONTINUIDAD_CICLO02.json; exact raw source indices in the analysis package','native_ticks':0},ensure_ascii=False,indent=2),encoding='utf8')
save('CAMBIOS_SISTEMA.md','''# Incorporaciones efectivas

Se conservan los cinco mecanismos IC01 en su implementación existente. No se reemplazaE1_SOCIAL_11ni se trasplanta conocimiento.

- `gate_world.py`: referencia adquirida por desgaste real y acción útil en una tarea escalar preparada. Estado propio de MAIN y continuaciones.
- `social_guard.py`: contraflujos nativos transitorios, ambos signos y agenda histórica191 verificados. Guardas estacionarias fallidas permanecen identificadas, no recomendadas.
- `recovery.py`: accesos genéricos preposicionados y dos capas finitas; recuperación asistida anterior sin cambio físico de implementación.
- `message_detour.py`: varianteP0con desvío de productos de giro; mejora actualizaciones acotadas, conserva pérdidas anteriores.
- `lateral_social.py`: preparación experimental con efecto inicial y futuros adversos explícitos, no una arquitectura estable certificada.
- `support_separation.py`: dos ceros preparados antes de responderB; recuperación/reorientación hacia lectores existentes. Vida operativa de tres códigos y adquisición escalar posterior.
- `gestionar.py` y `__init__.py`: extensiones del mismo gestor; panelbreve material, no otra plataforma.
- Catálogo/contratos, guía, fichas de estados y Manual1.6: dominios por vida, asistencia, fallos y comandos actuales. El delta no incluye motor ni modifica el estado de otras vidas.

P2/iniciativa aprendida no se incorporó. Se preservan el selector histórico acotado, la recuperación asistida y las alternativas útiles. Fuente y evidencia se identifican por archivo/hash; disponer del mecanismo no significa que todas las vidas lo hayan aprendido.
''')
save('FLUJOS_DE_INFORMACION.md','''# Frontera de información

| Flujo | Información que entra | Transformación y decisión | Qué no se atribuye aE1 |
|---|---|---|---|
| Puerta | Fuerza actual; después desgaste causado por el intento real | v27conserva referencia y emite±X; transducción fija decide intento/retirada | Ley de comparación, calendario, ley del mundo escalar y métrica útil preparados |
| Social | Objeto privado sólo paraB; recursos idénticos en ambas ramas | Bcompara nativamente; portadores y encuentros modifican soportesE1 | Ninguna copia del signo porPython; canal compatible no es lenguaje general |
| Acceso | Ceros genéricos, sin palabra, signo ni referencia pasada | Contenido existente participa en transformación y llegada a un lector fijo | Operador prepara oportunidades/preguntas; noP2por llamarlo adaptación |
| Separación | Dos ceros en tiempos derivados del episodio, sin inspeccionar respuesta correcta | La contribución previa se redirige; decodificador igual en controles | Prevención/reorientaciónP0, no reconstrucción de información destruida ni detector aprendido |
| Pendulum | Codec fijo de observación visible y coste real | Campos nativos→ganancias fijas→torque saturado→modelo externo | Puente no es capacidad aprendida, torque no prueba competencia, cancelación no es silencio |
| Auditor | Archivos, snapshots, control y target después de trayectoria | Cuenta/recalcula con RAW/clocks exactos | No devuelve el target ni la mejor rama a otra vida |

Las agendas legítimas y el progreso del puente permanecen en los snapshots operativos. Los informes, semillas, atlas y resultados del auditor no se consultan para responder. No se limpiaronRAW, clocks o paisajes, ni se editaron recuerdos. Las intervencionesSEM4de diagnóstico se declararon como aportes físicos legales y no como regulación autónoma.
''')
print(json.dumps({'report_bytes':(O/'INFORME_CIENTIFICO.md').stat().st_size,'manual_sections':len(sections),'current_triple_tick':triple['tick'],'native_ticks':0},ensure_ascii=False))
