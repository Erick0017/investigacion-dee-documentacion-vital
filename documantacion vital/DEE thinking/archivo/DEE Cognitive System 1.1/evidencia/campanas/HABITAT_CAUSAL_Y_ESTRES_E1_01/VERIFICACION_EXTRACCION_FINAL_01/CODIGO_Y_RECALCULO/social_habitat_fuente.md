# Contrato del soporte social — revisión 1

Fuente ejecutable: `social_habitat.py`.

SHA-256 congelado antes de ejecución física: `150212491e4b012e2377ef7a6e89d4bd264277de1b0c24eb50567a2f5df9808b`.

Comprobación realizada: AST, importación, apertura de E1_SOCIAL_11 T3154 y construcción de 15 planes prospectivos. No se programaron entradas, no se guardó el padre y se ejecutaron cero ticks. Esto comprueba preparación del instrumento, no comunicación efectiva.

## Dominio y procedencia

Reutiliza `a.transferred_quantity` del perfil existente cpc9_integral_n67 y `geometry['cpc9_return']['banks']`, sin crear Runtime ni introducir soportes entrenados. Procedencia técnica:

- `sistema/organizaciones/cpc9/base_validada/cpc8/src/integracion/quantity_core.py`: entradas físicas de objeto y lector.
- `sistema/organizaciones/cpc9/base_validada/cpc8/src/transferencia_magnitud/transferencia.py`: referencias recibidas por transporte y alias fijos B.quantity.*.
- `sistema/organizaciones/cpc9/src/retorno_social.py`: oportunidades bidireccionales de retorno a E1.

Magnitudes privadas principales18/45 fijadas por historia anterior a esta campaña: contrastan con la referencia material36 documentada. Su estado actual debe medirse, no suponerse. Las magnitudes50/82 siguen disponibles como prueba distinta pero no son clases opuestas respecto de36.

## Cronología fijada

Sea `s=147+67k+phase_offset`. Offset0 conserva la cadencia histórica;1 y3 son desafíos de fase explícitos, no ventanas seleccionadas después de observar la respuesta.

- B recibe cue5 y magnitud privada en s−5.
- Lector B7 en s−1; captura de su salida en s.
- Ambos bancos E1 reciben el mismo recurso record5 en s−1, read7 en s+66 y use13 en s+71.
- Capturas E1 en s+2/s+3, s+69, s+74 y s+78.
- Los dos contenidos se separan3*67ticks. No se cambia de vida entre ellos.

Desde T3154, primer objeto3157, salida B3162, lector E13231, uso3236, entrega3240; segundo objeto3358, salida3363, entrega3441.

## Intervenciones y límites

`full`: protocolo completo.

`no_partner`: omite nuevas experiencias privadas y lector de B; mantiene exactamente las oportunidades de E1. No elimina el cuerpo de B ni sus influencias históricas. No es un control de universo vacío o dosis total idéntica.

`unpaired_message`: desplaza un tick las oportunidades record de ambos bancos. Cantidad material, B privado y lectores restantes iguales. Mide desacople de asociación, no demuestra por su nombre ausencia total de comunicación.

`message_cut`: después de capturar la salida B ya formada, intenta depositar dos interceptores SEM4 estacionarios de carga0 en los dos sitios de tránsito fijos. Si cualquiera conserva RAW no nulo, incluso con state0, el corte completo es no soportado: no sobreescribe ni selecciona el sitio favorable. Los recibos finales determinan qué se aplicó. Los interceptores próximos también pueden modificar futuros de B: comparar su salida anterior al corte y el control sham, sin atribuir una lesión perfectamente localizada.

`message_sham`: dos interceptores idénticos fuera de ambas rutas, desplazamiento fijo[0,9,7], con la misma condición RAW==0. No se adaptan las ubicaciones por resultados.

## Flujo de información

Anfitrión entrega el objeto sólo a B. No calcula comparación, no traduce18/45 a una respuesta y no escoge un banco de E1. Ambos bancos reciben siempre recursos genéricos. Las respuestas exportadas son RAW/clocks/direcciones físicas, sin texto de acierto.

Plan, recibos y progreso se guardan en metadatos instrumentales para continuar el protocolo; el kernel no los consulta como memoria cognitiva. La continuación debe guardarse mediante el dueño existente y Store, no mediante arrays parciales. `schedule` no avanza; `advance` usa únicamente `a.run_until` y permite detenerse en un boundary para guardar el mundo completo. El llamador conserva el lock y decide commits; el módulo no carga, bifurca ni promueve vidas.

Los nombres de modo, planes y capturas no acreditan comunicación, aprendizaje nuevo, negociación, elección autónoma de interlocutor ni español funcional. Esas conclusiones exigen contrastes de la ejecución real.
