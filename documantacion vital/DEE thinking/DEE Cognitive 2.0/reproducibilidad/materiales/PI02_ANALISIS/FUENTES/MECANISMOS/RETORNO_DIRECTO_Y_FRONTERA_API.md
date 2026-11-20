# PI02: retorno directo, actualización y límites de las API

Lectura estática dirigida, 8 de noviembre de 2026. Este bloque no importó DEE, no creó mundos, no ejecutó ticks ni modificó el producto. Las propuestas son hipótesis de implementación; sólo los ensayos de la campaña pueden convertirlas en resultados.

## Qué ya existe

`sistema/capacidades/pi01_traza_legal_base.py`, líneas 13–16 y 39–59, prepara una traza retornante con políticas A=(1,0,0), B=(0,1,0), SENSOR=(-1,0,1), NORMALIZER=(1,0,-1), PENALTY0=(-1,1,0) y PENALTY1=(1,-1,0). En la vida actual su origen declarado es (0,5,20), establecido por `progresion_integrada_01.py`, no la constante de desarrollo antigua (41,43,47). No reinstalar la preparación ni sembrar otra vez su memoria.

`progresion_integrada_01.py:native_route` (49–61) inyecta un sensor por oportunidad y lee ACTION0=(0,0,1) o ACTION1=(-1,1,1) en un q calculado por Python. `use_selected_access` (63–80) traduce 0 a MA/alfa y 1 a FI128. `feedback` (104–117) aplica normalizador y, cuando corresponde, valencia a q+4N. La dirección de política se adquiere físicamente, pero el calendario y el despacho entre capacidades son asistencia preparada.

El antecedente CORE09 (`DECISIVO_C9_DISENO.py.txt`, constantes y `run_world`) tiene esa misma cancelación sensor/normalizador. Sus clocks artificiales y el borrado de scaffold no se trasladan a Cognitive; la variante legal de PI01 ya los eliminó. CORE09 no es CPC9 ni antepasado físico de MAIN.

## Deducción mínima para ensayar, no resultado ejecutado

Si la traza A/B vuelve al origen sin el sensor, puede detectarse su llegada material a cada tick mediante `a.run_until(t)` y `runtime.observe`/`exact_observation`. El instrumento debe tener sitio, firmas, ventana y regla de flanco fijados antes de puntuar. Un retorno preparado no demuestra iniciativa aprendida: la ganancia potencial es que una llegada producida por el propio mundo dispara una actuación, sin una orden material de oportunidad en cada episodio.

Para ese retorno directo **no debe reutilizarse sin cambios el normalizador de PI01**. SENSOR+NORMALIZER=(0,0,0); si no hubo SENSOR, NORMALIZER transformaría por sí mismo la dirección. En cambio:

- A+PENALTY0=(0,1,0)=B.
- B+PENALTY1=(1,0,0)=A.

Por tanto el candidato mínimo es conservar la traza sin nueva entrada tras un resultado útil y aplicar sólo una contribución de valencia 5, eco de la dirección realmente emitida, en un retorno posterior tras el perjuicio. No se transmite el acceso correcto ni se escribe el bit de política. El tipo de la contribución se deriva de la acción efectivamente formada, no del target privado.

La base exacta está en el código oficial de sólo lectura `4.5/DEE_thinking_4_5_0/source/src/kernel_v27.cpp`, `buscar_fuente_demux`, líneas 187–226. Con varias fuentes direccionales que apuntan al destino, suma s_reg con cota y toma el signo de cada componente de la suma de direcciones; el producto es state1/SEM_NORMAL. La rama de destino state0 aplica ese DEMUX en torno a las líneas 303–326. Esta deducción exige destino disponible, ausencia de contribuciones adicionales y admisión efectiva. No sustituye la comprobación física en el paisaje heredado.

La inyección legal puede reutilizar los puertos penalty0/penalty1 ya declarados, `trace.submit_arrival` (33–35), sin crear otro Runtime ni editar RAW/clocks. Su estado programado no basta: el recibo debe terminar applied. La observación incluye RAW aun cuando state=0.

## Ensayo y controles que resolverían la pregunta

1. Copias completas equivalentes: avanzar una ventana finita sin nuevas entradas, con/sin registro pasivo. Comparar RAW, clocks, agenda, recibos y metadatos causales al final. Identidades documentales diferentes no cuentan como física distinta.
2. Calibración no puntuable: encontrar con el lector prefijado el primer retorno A/B; aplicar una sola valencia en un retorno legal posterior y observar el producto y al menos otro retorno. No añadir normalizador si no se añadió sensor.
3. Rama sin valencia y sham de carga/dirección iguales fuera de la interacción, verificando que no intercepta otra función. Un sham no es comparable sólo por llamarlo así.
4. Actuador anulado después de formarse la salida: si el entorno obtiene el mismo recurso, la utilidad no procede de esa salida DEE.
5. Reserva posterior: contingencia o efecto del dispositivo invertido sin cambiar decoder ni geometría; contar primeras decisiones, errores, retornos, silencios, rechazos y coste total.

Una referencia mantener-tras-acierto/cambiar-tras-fallo con la misma información separa la ganancia de una alternancia trivial. Puede ser igualada sin invalidar el mecanismo físico; no deberá dirigir al ente evaluado.

Si las llamadas MA/FI internas avanzan más de un tick, un detector externo que sólo observa antes/después no cubre las llegadas intermedias. Debe registrar esa cobertura parcial o instalar un observador en el avance correcto del propietario, sin saltar agendas/protocolos ni llamar directamente otra capa de Runtime. Una regla de refractario/backpressure debe quedar fija y declarada; el host no puede rescatar selectivamente eventos tardíos.

## Frontera real de las API oficiales

`motor/python313/site-packages/dee_thinking/_native.pyi`:

- `ActionCoupling` (328–335) es un descriptor (`sites`, `roles`, `observation_ticks`, `scope`); no contiene una política ni un callback que permita delegar decisiones al kernel.
- `OrganizationalWorld.declare_interface/submit/probe` (490–494), `run_until` (500) y `Runtime.observe` (66) son las fronteras legales reutilizables en el mundo existente. `probe`, aun con carga cero, es material.
- `NativeAssociationSession.create` (566–585) crea otra preparación; el `train` oficial exige tick0 en `source/src/cognitive.cpp:176`. No se puede invocarlo sobre la vida heredada y afirmar continuidad de ese aprendizaje.
- `FinitePolicySession.create` (659–681) prepara otro aparato N67; `NativeInformationSession.create` (683 y siguientes) otro aparato N47. Compartir dimensión o fábrica no los fusiona con MAIN.
- `prepare_integrated_u0` y `RemoteReaderSession` pertenecen a sus preparaciones/protocolos. Reutilizar sus mecanismos requiere trasladar sólo un diseño compatible por entradas legales y probarlo aquí, no importar recuerdos de U0.

## Regulación y advertencia: frontera adicional

Una acción DEE puede operar un dispositivo ambiental con regla fija: desviar una fuente perturbadora o mantener una entrada abierta. Python podrá ejecutar esa transducción sin consultar la respuesta esperada. No podrá detectar congestión y elegir por el participante cuándo protegerse. La capacidad debe seguir siendo útil en ventanas sin perturbación; bloquear toda entrada no cuenta como regulación competente.

El código oficial `experimental_regulation.py` se leyó como antecedente acotado: `SCOPE` línea19 declara pulso direccional adquirido por emparejamiento, no estrategia de regulación seleccionada por recompensa; `CPC5RegulationSession.create` (104–112) instala un mundo nuevo N67/T0 y currículo finito hasta437. Sus pulsos de carga cero son materiales. No reutilizar su fábrica como supuesto ECI02 ni llamar a ese pulso autorregulación general.

Una futura advertencia necesita dos historias con igual señal actual y distinta asociación previa, retorno emparejado frente a desacoplado, variaciones temporales reservadas y falsas alarmas. Un pulso que simplemente redirige A/B al llegar es reacción preparada; un segundo portador preparado por el investigador no demuestra aprendizaje contextual. Este bloque no identifica todavía un mecanismo nuevo de advertencia aprendido y compatible que pueda declararse validado sin ensayarlo.

## Alcance

Se reutilizaron las notas MAR/LBM y CORE09 de PI01. Se reabrieron únicamente el código instalado PI01, los contratos de tipos oficiales y las secciones de fuente necesarias para la cancelación direccional y el límite de las fábricas. No se hizo otra lectura completa de los manuales ni auditoría masiva. La lectura de fuentes C++ no modificó el kernel ni certifica por sí sola su correspondencia binaria; la identidad del motor debe quedar en la comprobación breve central de PI02.
