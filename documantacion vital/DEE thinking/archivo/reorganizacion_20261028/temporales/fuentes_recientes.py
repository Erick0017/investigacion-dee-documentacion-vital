"""Fuente editorial de solo datos para el compendio. No ejecuta DEE.

Las rutas parten de la carpeta original DEE Cognitive System 1.1. El autor
del compendio resolverá su ubicación final; no se reescriben expedientes.
"""

BASE_ORIGINAL = "DEE Cognitive System 1.1"
ALCANCE = (
    "Lectura dirigida de informes cerrados MI01 a APD05 y primarios seleccionados. "
    "Cero nuevos ticks, campañas o verificaciones físicas. La incorporación que "
    "describen los informes es histórica al gestor 1.1; la disponibilidad efectiva "
    "en Cognitive 2.0 requiere el cotejo operativo del responsable de reorganización."
)

FUENTES = [
    {
        "id": "R01", "campana": "MENTE_DEE_INTEGRAL_MI01",
        "ruta": "entregas/DEE_COGNITIVE_1_1_MENTE_DEE_INTEGRAL_MI01_ANALISIS.zip",
        "sha256": "5672ae4110d326b969bca0640d52f457ad5c9e73772e8ac07d0b754c5764ae3f",
        "miembro": "INFORME_CIENTIFICO.md",
        "sha256_miembro": "48326feb953079ba1d2ae909f5bfa43f77cf3af7164b85ecaf238745a3d3f223",
        "localizadores": ["3 Capacidades positivas y contraejemplos de construcción", "4 Evaluación integral fijada", "9 Qué quedó demostrado y qué no"],
        "primarios": [{
            "ruta": "evidencia/campanas/MENTE_DEE_INTEGRAL_MI01/MI01_411_MAIN_RESERVA_1.json",
            "sha256": "010448295b967d41d4e56c78d6423b5e37b28a4cc8a2c85c49ddcc8cb4057081",
            "localizador": "/result/result/rows",
            "observado": "16 pasos; torques [0,2,0,0,0,0,0,0,0,0,0,0,0,0,0,0]; recompensa total -126.84941375827731."
        }],
    },
    {
        "id": "R02", "campana": "MI02_ARQUITECTURA_DISTRIBUIDA",
        "ruta": "laboratorio/campanas/MI02_ARQUITECTURA_DISTRIBUIDA/INFORME_CIENTIFICO_MI02.md",
        "sha256": "c0ef7f221da2fcf44298532773783afca073535cb8d4bb9b6969edc753f73fc2",
        "localizadores": ["Aprendizaje por consecuencias y utilidad", "Acceso ruido y recuperación sin reenseñar", "Funciones reutilizables y nueva alternativa R9", "Español y alcance semántico"],
    },
    {
        "id": "R03", "campana": "CF01_CIERRE_FUNCIONAL",
        "ruta": "entregas/DEE_COGNITIVE_CF01_CIERRE_FUNCIONAL_ANALISIS.zip",
        "sha256": "ec38fa921c90066e1487d56ebf162dd6ed2e714638e7b98ba552977f3b6bab51",
        "miembro": "INFORME_CIENTIFICO.md",
        "sha256_miembro": "3f3b6fd05f39ab58594d217581c26fef21d9c26890b216f95fbe5ce98967fc92",
        "localizadores": ["Resultados integrados y controles", "Una consecuencia cambia una decisión útil posterior", "Comunicación y composición que sí ocurrieron", "Panel final y continuidad"],
        "primarios": [
            {"ruta": "evidencia/campanas/CF01_CIERRE_FUNCIONAL/CAL8_MAIN.json.gz", "sha256": "a46d18a0d64cc50cbd0115b945d99a8e04dbd60811d6890fb3fbd7070496ca84", "localizador": "/result/result/rows/*/job_passed y /native/after/own", "observado": "Cinco filas, cuatro útiles; comandos [-1,1,-1,1,1]; diferencias propias posteriores [4,4,4,4,4]."},
            {"ruta": "evidencia/campanas/CF01_CIERRE_FUNCIONAL/CAL8_OMIT.json.gz", "sha256": "13a9a2c74f16d49300ea924538cd7fae8969e22a10ca7485c60279b5b423d513", "localizador": "/result/result/rows/*/job_passed y /native/after/own", "observado": "Cinco filas, dos útiles; comandos [-1,-1,-1,1,-1]; diferencias propias posteriores [3,3,3,3,3]."},
        ],
    },
    {
        "id": "R04", "campana": "ENTE_DEE_OPERATIVO_01",
        "ruta": "entregas/DEE_ENTE_OPERATIVO_01_ANALISIS.zip",
        "sha256": "e66b159bb44cc84eda47f5dcd59bf11448c7340a4226e7bb0243c0b704357c51",
        "miembro": "INFORME_CIENTIFICO.md", "sha256_miembro": "1c606e9d08b468d154e2151be6e7bab35390115a0d979120a57441d04d3a7542",
        "localizadores": ["El avance causal frente a CF01", "Contrastes emparejados independientes de MAIN", "B: límite directo y acoplamiento ambiental explícito", "Uso práctico: cola con retorno realmente externo", "Continuidad final, recursos y acceso"],
    },
    {
        "id": "R05", "campana": "ENTE_DEE_EVOLUCION_02",
        "ruta": "entregas/DEE_ENTE_EVOLUCION_02_ANALISIS.zip",
        "sha256": "2d4534c012246e0dc36fced9721f4f8c01af14f6c7d057cb37135fcfd0ea6c6b",
        "miembro": "INFORME_CIENTIFICO.md", "sha256_miembro": "8b73aeec54ec5f89d938faab8ebec968445240137aff58c2b3ba38580ba43771",
        "localizadores": ["1. Más información, sin agregación del anfitrión", "2. Qué se transfirió y qué no", "3. Composición, interfaz de fase y contraejemplo", "4. Una vida A→B→C→A, con pérdidas"],
        "primarios": [{"ruta": "evidencia/campanas/ENTE_DEE_EVOLUCION_02/34_R10_MISMA_VIDA_B8.json.gz", "sha256": "120f0d2f6e3ae11dae61991f288b580c6329f3871da2a10b1414059126ec8781", "localizador": "/result/result/rows/0/raw_components y /sensory_extra", "observado": "Primer vector [7,8,8,9,9,10,10,11], ocho puertos crudos independientes y cuatro recursos genéricos; no sumas anfitrión inyectadas."}],
    },
    {
        "id": "R06", "campana": "MENTE_ACUMULATIVA",
        "ruta": "laboratorio/campanas/MENTE_ACUMULATIVA/INFORME_RESULTADOS.md",
        "sha256": "5639a315a37c3f84b66ecd51a6dc6ddb6f3cefb98134d2a48d62b608fa52df8d",
        "localizadores": ["Trayectoria principal, sin reinicios", "Contraste causal de consecuencias", "Perfil complementario incorporado: U0 acumulativo asistido", "Entrada común y elección nativa: fallos conservados"],
    },
    {
        "id": "R07", "campana": "MENTE_ACUMULATIVA_R02",
        "ruta": "laboratorio/campanas/MENTE_ACUMULATIVA_R02/INFORME_RESULTADOS.md",
        "sha256": "ba8a2d224e04df07aec8c56b3406c7366ec7cca40ed2717a21645d5caa8cf182",
        "localizadores": ["2. Trayectoria principal y resultados", "3. Mecanismo de acceso repetible y sus controles", "4. Composición nativa: retorno comprobado y coste real", "5. Un residuo útil sin convertirlo en memoria semántica", "7. Selección P1 complementaria y límites del ciclo por consecuencias"],
        "primarios": [{"ruta": "evidencia/campanas/MENTE_ACUMULATIVA_R02/51_PANEL_FINAL_CINCO_MAIN5.json.gz", "sha256": "98e85324b06fbd161fcee5d612e70747a0285faa65cbc60a12948f9b528c0338", "localizador": "/result/result/rows/*/reader/formed_native_command", "observado": "epsilon -1, gamma +1, beta +1, alfa -1, delta -1; candidato único en cada fila; reader_uses_target_or_token falso."}],
    },
    {
        "id": "R08", "campana": "MENTE_UNIFICADA_Y_FI01",
        "ruta": "laboratorio/campanas/MENTE_UNIFICADA_Y_FI01/INFORME_RESULTADOS.md",
        "sha256": "b4a5c9135c014be2793f9418655bcd6d6ca16805bb0597d710a57c53f8bdf26f",
        "localizadores": ["Reserva final propia R17 de MU_MAIN_FASE_R3", "Causa delimitada del deterioro tardío y protección preparada", "Bloque B: acceso escalar reutilizable y nueva aplicación", "Entradas conjuntas y conservación después de la carga", "Transferencia: alcance y límites", "Cadencia, perturbación y tamaño del dominio"],
        "recalculo_leido": {"ruta": "evidencia/campanas/MENTE_UNIFICADA_Y_FI01/RECALCULO_APLICACION_B_CON_128.json", "localizador": "raw_checks, reader_checks, artifact_checks, worker_checks, cases", "observado": "96724 observaciones RAW, 45 lectores, 8 comprobaciones de artefactos y 8 actuaciones, sin discrepancias; recálculo archivado, no reproducción nueva."},
    },
    {
        "id": "R09", "campana": "ASISTENTE_PROPOSITO_LENGUAJE_DELEGACION_01",
        "ruta": "entregas/DEE_ASISTENTE_PROPOSITO_LENGUAJE_DELEGACION_ANALISIS.zip",
        "sha256": "ffb71607fe4cf8d0daa444916c8213df82f7cb19aa407e7ca0b324119c55e487",
        "miembro": "INFORME_CIENTIFICO.md", "sha256_miembro": "4bcb63f03a13513f461ebda590723e61587da136e851566a27689b0a57902622",
        "localizadores": ["Resultado ya demostrado y organización examinada", "Flujo causal revisado en el código R04 congelado", "Experiencia, capacidad y asistencia", "Selección modificada por consecuencias: positivo local y negativo importante", "SERVICIO_R04: uso consecutivo y continuidad operacional acotada"],
    },
    {
        "id": "R10", "campana": "APD02_CONTINUIDAD_CALIDAD_ADAPTACION",
        "ruta": "entregas/DEE_APD02_CONTINUIDAD_CALIDAD_ADAPTACION_ANALISIS.zip",
        "sha256": "d81332caac57ee5dc7a87f07049c6afd44d702fc2817800073762427547ff5d6",
        "miembro": "INFORME_CIENTIFICO.md", "sha256_miembro": "3c618ae69e285f28625a7bf42e1019943627b4e2a82ce9589791ef3b65aa8324",
        "localizadores": ["Qué mejoró respecto a APD01", "Historia de consultas y deterioro de acceso", "Selector por consecuencias y preparación adversa R03", "Agregación, composición y objetivo que requiere preguntar", "Petición pendiente y continuación verificable", "Una hora con aprendizaje y uso en la misma organización", "Selección útil por calidad a precios iguales"],
    },
    {
        "id": "R11", "campana": "APD03_AUTONOMIA_DESARROLLO_DEMOSTRACION",
        "ruta": "entregas/DEE_APD03_AUTONOMIA_DESARROLLO_DEMOSTRACION_ANALISIS.zip",
        "sha256": "1cf0db455e60e7490c5fac59a4ca8a00e01cb0a44f9d4738137d44de14875109",
        "miembro": "DEE_APD03_ANALISIS/INFORME_CIENTIFICO_APD03.md", "sha256_miembro": "9ae5bffc643e21fc64d63cd6bbb90c1124d17b95879028ee7cda0da7f8b1b408",
        "localizadores": ["Resultado central", "Cobertura de las cinco fronteras", "Historia que habilita acceso no equivale a metaaprendizaje", "Combinación útil y límite de planificación", "Incorporación, manual y distribución"],
        "primarios": [{"ruta": "laboratorio/campanas/APD03_AUTONOMIA_DESARROLLO_DEMOSTRACION/main/exportacion/CIERRE_MAIN_APD03_R01/RESULTADOS/RECALCULO_MAIN_FINAL.json", "sha256": "2f4208e4d1fc4575772685672640ecff66e0b7092b6c9fd3e680feda24917ab8", "localizador": "/counts, /window, /opportunities, /APD02_quality_uses", "observado": "ACT8, QUERY6, 8 archivos reales correctos, cuatro hechos nuevos, 14 oportunidades y12 acciones útiles; 8195 checks, issues vacío. Error de calidad: Native23 y archivo perturbado24."}],
    },
    {
        "id": "R12", "campana": "APD04_ECOSISTEMA_COGNITIVO",
        "ruta": "entregas/DEE_APD04_ECOSISTEMA_COGNITIVO_ANALISIS.zip",
        "sha256": "bc5242f30c48216fcce2eda0a3b47ae5f6889162b392ad0e734d5ec75e071e1f",
        "miembro": "INFORME_CIENTIFICO_RESULTADOS.md", "sha256_miembro": "07a28f0125831d64454752606529e554f05424bcb2654999e84524e08c9b5cb8",
        "localizadores": ["1 Resultado y atribución", "3 Frontera sensorial y contraste A B C", "4 Historia de consecuencias y decisión local", "6 Pérdida de acceso y límites de supervisión", "7 Acceso consecutivo del descendiente diagnóstico", "10 Full exacto: uso, revisión adquirida y continuación de una sola copia"],
    },
    {
        "id": "R13", "campana": "APD05_GENESIS_SIN_LLM",
        "ruta": "entregas/DEE_APD05_GENESIS_SIN_LLM_ANALISIS.zip",
        "sha256": "310c6f062bbd55840d73af05877b75380a22ec6b6d53bbd02a25160e7399ae49",
        "miembro": "INFORME_CIENTIFICO.md", "sha256_miembro": "98a4bb696cc90b9e6731104d223d7020219ca1390eb4434091ba46dafd3ecc1c",
        "localizadores": ["Aplicación y atribución", "Nuevo acceso preparado y vida principal", "Reserva integrada de una hora", "Reposo y deterioro"],
        "primarios": [{"ruta": "evidencia/campanas/APD05_GENESIS_SIN_LLM/RESERVA_INTEGRADA_60_R02/RECALCULO_RAW_R03_RECIBOS_CON_ALIAS.json", "sha256": "1229d97614965c25a08fe429c9134003f856f071ebc257ef41bb975bcbf0ea48", "localizador": "/access_formed, /access_correct_in_reference20_domain, /access_useful_environmental_effects, /native_receipt_statuses", "observado": "40 formadas y conformes; 16 efectos útiles; 9604 IDs: 9600 aplicados y4rechazos;52 transportes completos,28 usos numéricos y42 consultas léxicas."}],
    },
]

FICHAS = [{'id': 'MR01',
  'titulo': 'Adquisición de referencias y actuación útil por consecuencias',
  'sencillo': 'Una experiencia puede modificar una relación física que cambia la actuación posterior y '
              'permite resolver una oportunidad antes fallida, dentro de dominios delimitados.',
  'mecanismo': 'Entradas crudas y soportes preparados generan una dirección nativa. El retorno de un '
               'contacto transforma la diferencia entre soportes y una oportunidad posterior común utiliza '
               'esa diferencia. Python no escribe directamente la referencia correcta en RAW.',
  'resultados': ['MI02 controlador R8 obtuvo 16 contactos útiles en las 18 oportunidades posteriores a un '
                 'bloque inicial con cinco errores en seis oportunidades. Los controles sin retorno y con '
                 'corte selectivo obtuvieron 7/18 cada uno. La rama heredada N67 obtuvo 10/15 frente a 5/15 '
                 'sin retorno.',
                 'CF01 R9 N26 completó 24/24 trabajos en 33 intentos, con nueve errores; sin retorno '
                 'completó 3/24 en 36 intentos. Al cambiar la calibración ambiental de 7 a 8, MAIN obtuvo '
                 '4/5 frente a 2/5 y su diferencia propia cambió de 3 a 4.',
                 'ENTE01 corrigió la frontera externa de CF01: sólo devuelve el contacto realmente producido '
                 'después de ejecutar. En controles emparejados, contacto intacto y sham cambiaron delta 4 a '
                 '5 y resolvieron una oportunidad común; acción anulada, retorno omitido, desacoplado y '
                 'corte no lo hicieron. La FIFO completó seis trabajos en ocho intentos, cinco al primer '
                 'intento; sin retorno no completó el primer trabajo en doce intentos.',
                 'APD02 R04 produjo doce emisiones, números y archivos correctos: ocho entregas bajo '
                 'presupuesto y cuatro RESOURCE_LIMIT. Después del primer fallo informativo de cada bloque, '
                 '4/4 oportunidades siguientes fueron útiles.',
                 'En calidad con precios iguales, APD02 MAIN obtuvo 4/7 resultados útiles frente a 3/7 de '
                 'OMIT; cambios útiles después de fallo, 3/3 frente a 0/2. Es evidencia compatible con P2 '
                 'local. El contrafactual siempre externo también sería 4/7.',
                 'APD04 cambió selecciones por historia sin utilidad sostenida: en R02 ambos brazos '
                 'obtuvieron 1/10 útiles; en R03 el beneficio antiguo fue 0/10 en ambos y la calidad nueva '
                 '1/10 frente a 0/10.'],
  'controles': 'Historias emparejadas sin retorno, acción anulada después de formarse, retorno desacoplado, '
               'corte selectivo y sham, según el expediente. Las bifurcaciones no son aprendices '
               'independientes ni experiencias sumadas a MAIN.',
  'asistencia': 'Geometría, rutas, fuentes, oportunidades, sensores, lectores y transducción son preparados. '
                'La evidencia de cierre realmente externo pertenece a ENTE01: el retorno nativo de CF01 '
                'podía estar preparado antes de ejecutar externamente.',
  'dominio': 'MI02 R8 y R9, CF01_MAIN y EO01_MAIN N26, APD02_MAIN N67 y sus controles. Cada vida conserva '
             'una historia distinta.',
  'estado_actual': 'Mecanismos históricamente incorporados al gestor 1.1 bajo contratos propios; '
                   'disponibilidad efectiva en 2.0 pendiente del cotejo operativo de esta reorganización.',
  'limites': 'No acredita política general, recuperación autónoma general, R2 general o superioridad '
             'universal. Se distingue cambio de campo, actuación válida y resultado útil.',
  'fuentes': ['R02', 'R03', 'R04', 'R10', 'R12']},
 {'id': 'MR02',
  'titulo': 'Memorias independientes revisión selectiva y retención',
  'sencillo': 'Varias correspondencias físicas pueden adquirirse, revisarse y reutilizarse en una genealogía '
              'continua, con límites explícitos de retención y acceso.',
  'mecanismo': 'Un soporte circulante adquirido participa en una consulta común. Recursos genéricos forman '
               'una emisión dependiente de historia y restauran la ruta; el operador todavía indica contexto '
               'e iniciativa.',
  'resultados': ['MA01 R9 no sostuvo cuatro políticas: después de adquirir c4, sus primeros usos antiguos '
                 'fueron 0/3; después de revisar c1, 1/3. Su final 8/8 pertenecía al criterio actual c3. El '
                 'U0 complementario, otra vida, sí adquirió cinco asociaciones y dio 5/5 después de guardar '
                 'y cargar.',
                 'MA02, vida nueva N67, utilizó cuatro asociaciones en 12/12 consultas intercaladas y una '
                 'revisión en 5/5. MAIN_5 añadió epsilon conservando las cuatro anteriores, mantuvo 64/64 '
                 'usos y terminó con panel 5/5 en T11196.',
                 'MU/FI01 continuó MA02_MAIN_5, adquirió zeta y revisó beta conservando las otras cinco. Su '
                 'reserva R17 obtuvo 120/120 lecturas. Enseñar un signo nuevo no significa retener el signo '
                 'anterior.',
                 'APD03 adquirió luma+ y nara−; panel final 14/14 firmas antiguas, 6/6 accesos MA y 2/2 '
                 'nuevos. APD04 añadió clasifica+ y equilibra−; un descendiente diagnóstico utilizó '
                 'consecutivamente 16 heredadas, seis MA y dos nuevas, con 168/168 entradas.',
                 'APD05 archivó 42 emisiones léxicas únicas y un último panel alfa−, beta+, luma+, nara−, '
                 'clasifica+, equilibra−. El signo positivo posterior de clasifica procedió de docencia '
                 'explícita.'],
  'controles': 'Historias opuestas, ausencia de docencia, recursos omitidos o no restaurativos y orden de '
               'consultas. El primario final MA02 muestra un candidato único por contexto y un lector sin '
               'target ni token.',
  'asistencia': 'Acceso contextual y recursos restaurativos son P0; contenido y uso son P1 cuando los '
                'contrastes lo sostienen. Las consultas materiales modifican el paisaje.',
  'dominio': 'U0 complementario, MA02_MAIN_5 y descendientes MU/APD. Sus experiencias no completan '
             'ficticiamente el repertorio R9.',
  'estado_actual': 'Perfiles y vidas históricamente utilizables; no implica que la selección actual de 2.0 '
                   'posea todos los máximos históricos.',
  'limites': 'Dieciocho formas y seis contextos MA no son 24 conceptos. Consultar una casilla no adquirida '
             'puede bloquear otras: MA02 NOEVENT tuvo 4/10 respuestas; APD02 A→B dejó 9/12 accesos '
             'anteriores, frente a 12/12 con consultas aisladas.',
  'fuentes': ['R06', 'R07', 'R08', 'R10', 'R11', 'R12', 'R13']},
 {'id': 'MR03',
  'titulo': 'Composición nativa y coste de reutilización',
  'sencillo': 'Productos adquiridos pueden encontrarse y generar otro uso funcional. La composición puede '
              'consumir accesos originales; no constituye por sí sola un plan autónomo.',
  'mecanismo': 'Una primera contribución adquirida se transporta y participa con otra contribución y '
               'recursos comunes en un producto nuevo. En ciertos casos se reconstruyó un retorno toroidal '
               'concreto con contexto causal suficiente.',
  'resultados': ['MI01 30–34 combinó selección Y y contenido Z adquiridos por separado: forma XYZ161 y uso '
                 'YZ175. MAIN sostuvo la primera composición, pero no la segunda acumulativa.',
                 'MA02 R08 verificó 66 pasos de predecesor y el encuentro 270+461+7→738. R10 contrastó ambos '
                 'signos y el encuentro 308+461+7→776: +/+ produce +, −/− produce − y las mezclas no '
                 'producen emisión válida. El corte anula y el sham conserva.',
                 'En todas las ramas R10 sobrevivieron gamma/delta y se perdieron los dos accesos '
                 'individuales compuestos. MAIN utilizó el producto para un trabajo, preservó el fallo y '
                 'reenseñó alfa/beta. La alternativa MA02_COMPOSICION_PLUS_LISTA tiene su propio +/+; MAIN_5 '
                 'conserva alfa−/beta+ y no comparte esa composición válida.',
                 'MU/FI01 combinó memoria y datos reales de archivos. Gamma/epsilon/zeta seleccionaron '
                 'trabajadores; tras guardar y reabrir, tamaños reales 13/32/13 produjeron emisiones y '
                 'cerraron 3/3 transacciones, conservando seis asociaciones.',
                 'APD01–APD03 encadenaron suma y resta reutilizando resultados reales; el orden de las '
                 'etapas provenía del operador.'],
  'controles': 'Componentes omitidos, signos mezclados, recurso ausente, desplazamiento temporal, corte del '
               'producto formado y sham. Los errores de coordenadas R07 y sus dosis distintas se conservan; '
               'no se proyectan sobre R08/R10.',
  'asistencia': 'Compositor, ruta y encadenamiento preparados. Los algoritmos SHA y compresión pertenecen a '
                'herramientas externas.',
  'dominio': 'MI01 local, MA02 consumidor y MU/FI01 operativo; son realizaciones distintas.',
  'estado_actual': 'Composición consumidora conservada como alternativa y pipeline asistido incorporado '
                   'históricamente al mismo gestor.',
  'limites': 'No hay copia gratuita de significado, retención intacta de accesos consumidos, gramática '
             'productiva o planificación multietapa adquirida.',
  'fuentes': ['R01', 'R07', 'R08', 'R09', 'R10', 'R11']},
 {'id': 'MR04',
  'titulo': 'Información privada comunicación y lector reutilizable',
  'sencillo': 'Una solicitud material puede activar un participante con historia privada. Su emisión puede '
              'modificar contexto o actuación en otra región del mismo mundo.',
  'mecanismo': 'Solicitud nativa, encuentro con referencias privadas, emisión dependiente del contenido, '
               'transporte por canales preparados y encuentro posterior con el receptor. Cortes posteriores '
               'a la formación del mensaje separan su aporte de una causa externa común.',
  'resultados': ['MI01 110/111 recibió privados 20/52 en B y produjo códigos 145 opuestos. La protección '
                 '170/171 permitió 3/3 usos por signo. MAIN adquirió su propio 145 y lo utilizó cuatro veces '
                 'conservando códigos anteriores.',
                 'MI01 270 produjo una solicitud XY−145 a partir de un fallo. Omitir retorno o cortar el '
                 'producto la eliminó; sham conservó. El segundo acceso a B falló: solicitar no equivale a '
                 'recuperar completamente.',
                 'MI02 R9 permite vaciar el lector B a RAW0, conservar privados 61/19 y responder a '
                 'solicitudes posteriores sin limpieza manual. Continuación 240: 9/12 contactos útiles y '
                 'ventanas vacías entre trenes. En una preparación nueva, cerrar el hueco central redujo '
                 'muestras activas de 655 a 49, frente a 655 con sham, conservando referencia y uso.',
                 'CF01: el privado 52 formó una emisión negativa que, con aportes de transporte, produjo '
                 'contexto izquierdo 7. El corte postformación eliminó el efecto y sham lo conservó; '
                 'referencias propias y privadas permanecieron.',
                 'ENTE01 recibió ambos signos de B, pero no actualizó persistentemente contexto 7/5 por esa '
                 'vía. La alternativa de válvula externa permitió a B modificar el mundo y a A aprender de '
                 'sus consecuencias; no reparó la recepción social cerrada.'],
  'controles': 'Historia privada opuesta o ausente, corte de consulta, corte de mensaje formado, actuador '
               'anulado y sham. Una oportunidad resuelta por defecto no prueba necesidad del mensaje.',
  'asistencia': 'B, rutas, fuentes y lectores preparados. Una corriente equilibrada tenía papeles de '
                'consulta e izquierda por defecto; no se acreditó elección exclusiva aprendida entre ambos.',
  'dominio': 'MI01 N67 y alternativas MI02/CF01/ENTE01 N26, con genealogías separadas.',
  'estado_actual': 'Lector social R9 incorporado como alternativa histórica ejecutable. No se importaron sus '
                   'recuerdos a MAIN.',
  'limites': 'B no es una segunda mente completa. Se transmite una distinción relativa, no necesariamente '
             'los valores privados completos. No acredita negociación, lenguaje general o coordinación '
             'cerrada v27 en la variante externa.',
  'fuentes': ['R01', 'R02', 'R03', 'R04']},
 {'id': 'MR05',
  'titulo': 'Conservación restauración de acceso y material residual útil',
  'sencillo': 'El fallo de un lector no basta para declarar destruida la información. Recuperación asistida, '
              'prevención de interferencia y readquisición son resultados diferentes.',
  'mecanismo': 'Se contrastan contenido físico, admisión, fase y encuentros. Un recurso genérico puede '
               'restablecer un uso sin aportar el contenido; en otros casos se requiere docencia nueva.',
  'resultados': ['MI02 FASE33/RESERVA38 mantuvo los RAW de referencias 174/162 y un recurso genérico '
                 'recuperó 5/6 contactos útiles, frente a 0/6 sin recurso y 0/6 sham. No aportó palabra, '
                 'signo, referencia original o snapshot favorable.',
                 'MA02 R09: un portador previo 5 encontró docente 11 y produjo Z−16. Cortarlo anuló el '
                 'acceso alfa posterior; sham conservó; gamma/delta sobrevivieron. Es reutilización de '
                 'material en enseñanza explícita, no recuperación del signo antiguo sin docente.',
                 'MU R15: sólo consulta+dato 29 cambió A105 a104, con B125; consulta sola, dato solo y sham '
                 'no. Tras 2N y una trama común el real quedó fuera de las puertas. Un RAW difería y los '
                 'clocks coincidían.',
                 'MU R16 previno el encuentro mediante calendario P0 de 0–10 ticks, sin mirar valor/target. '
                 'La candidata MU_MAIN_FASE_R3 partió del futuro adverso T68924 y recibió B0 explícita '
                 'D−21→−20: reenseñanza declarada.',
                 'APD03 paired admitió 95/95; desync, 89/95 y cue B bloqueado. La ROI mostró X−5 en '
                 'K=(47,7,47) justo al admitir, RAW0 antes y después y diez recurrencias separadas 67 ticks. '
                 'No establece por sí sola recorrido toroidal completo.',
                 'APD05: 8192 ticks de reposo desde el padre accesible conservaron 8/8 y 222/222. Después de '
                 'tres tareas ordinarias, REAL/OMIT dieron 0/8 con insumos completos. Reposo 4096 desde el '
                 'padre denso no recuperó y rechazó 219/222.'],
  'controles': 'Sin recurso, sham, factorial consulta/dato, fase emparejada, historia opuesta y docente '
               'omitido. Igualdad RAW/clocks no equivale a identidad causal completa con interfaces, colas y '
               'recibos.',
  'asistencia': 'Recuperación MI02 y protección MU son P0 iniciadas externamente. La B0 y el nuevo encuentro '
                'docente MA02 son readquisiciones.',
  'dominio': 'Perfiles y ventanas particulares; no una explicación única de todas las pérdidas.',
  'estado_actual': 'Procedimientos históricos reutilizables y diagnósticos conservados como mecanismos o '
                   'instrumentos; no recuperación autónoma general.',
  'limites': 'No limpiar material a ciegas. Diferencia externamente detectable no equivale a uso nativo; '
             'coincidencia parcial no demuestra borrado global.',
  'fuentes': ['R02', 'R07', 'R08', 'R11', 'R13']},
 {'id': 'MR06',
  'titulo': 'Agregación sensorial y escala funcional',
  'sencillo': 'Componentes independientes pueden reunirse mediante encuentros nativos. Contar portadores no '
              'basta para contar variables relevantes o conceptos.',
  'mecanismo': 'Árboles y cabezas de encuentro preparados reciben componentes crudos separados, producen un '
               'agregado material y lo enfrentan a una referencia adquirida mediante un lector congelado.',
  'resultados': ['ENTE02 R9: cuatro componentes, 3/3 agregaciones exactas pero 1/3 actuaciones útiles; la '
                 'interfaz anterior funcionó 2/2 después. R10, nueva N26 desde T0, contrastó relevancia de '
                 'ocho componentes; 46/46 agregaciones exactas y corte final 52 actos, 45 útiles y siete '
                 'errores.',
                 'Serial16 R10 son dos tramas8, no una decisión16. Serial32 R10 no se ejecutó. BURST16 '
                 'admitió52/52 sin producir dos decisiones atribuibles; CONCURRENT16 rechazó24 y admitió28.',
                 'MU/FI01: 128 contrastes de un componente 0→2 cambiaron baseline negativo a positivo; 126 '
                 'reservados y dos repeticiones. Hubo176/176 entradas por caso y seis accesos conservados. '
                 'MAIN recibió tres tramas128,528/528 entradas y18/18 accesos intercalados.',
                 'R17 produjo12/12 tramas frente a10/12 R11, sin emparejamiento causal completo. Δ2 '
                 'admitió352/352 en dos tramas pero bloqueó el panel antiguo0/6; éste rechazó39/42 entradas. '
                 'Δ16/67/200 conservó6/6.',
                 'N67/N101 no mostró mejora nominal general. Δ2 densificó ambos; con Δ16 apareció cambio '
                 'tardío de referencia en N101. Volumen disponible no garantiza memoria funcional.'],
  'controles': 'Perturbación individual de componentes, cortes del producto convergente, sham, historias '
               'opuestas, cadencias y horizontes comunes. Número de variables se separa de dosis y tasa.',
  'asistencia': 'Árbol, rutas, calendario, recursos de giro, codec y lector preparados. Los ceros genéricos '
                'no cuentan como datos relevantes.',
  'dominio': 'EO02 R9 compatible, R10 nueva N26 y MU/FI01 con auxiliares N67/N101. Cambiar N no continúa la '
             'misma vida.',
  'estado_actual': 'Frentes sensoriales preparados incorporados históricamente; relevancia exhaustiva128 '
                   'corresponde a auxiliares, no128 aprendizajes de MAIN.',
  'limites': 'Admisión no implica acceso; agregación no implica conceptos; una cadencia fallida no establece '
             'una cota universal de v27.',
  'fuentes': ['R05', 'R08']},
 {'id': 'MR07',
  'titulo': 'Transferencia entre tareas con representación compartida',
  'sencillo': 'Una referencia adquirida puede reutilizarse en otro destino y ahorrar errores iniciales, pero '
              'perjudicar cuando cambia la ley.',
  'mecanismo': 'La historia física permanece al cambiar el trabajo y la transducción declarada. El destino '
               'utiliza el estado adquirido antes de su propio feedback, sin copiar valores de un control o '
               'trasplantar regiones.',
  'resultados': ['ENTE02 servicios: T6/6,U4/6,H3/6; acción anulada0/3. C2: T4/4 pasos y dos transacciones, '
                 'U2/4 y una, H0/4. Con ley contraria T1/3 frente a U3/3.',
                 'R10 reutilizó dos experiencias previas de dos entradas en cuatro trabajos nuevos de ocho: '
                 'T4/4 frente a U3/4; el primer acto T+ fue útil y U− falló.',
                 'MU/FI01: primer destino sin feedback T4/4 frente a U/H2/4; ley contraria T0/4. B14 '
                 'intercaló cuantitativo/gamma: T8/8 commits y U/H0/8 con148/148 entradas. U/H cambiaron '
                 'referencias pero no obtuvieron utilidad en esas ocho oportunidades.'],
  'controles': 'Historia adquirida T, retorno omitido U, desacoplado H, actor anulado y ley contraria. Las '
               'bifurcaciones comparten prefijo, no biografías que puedan sumarse.',
  'asistencia': 'Representación compartida, tareas, fases, transductores y herramientas preparados. El coste '
                'de adaptación U/H está censurado por encima de ocho oportunidades, no estimado exactamente '
                'en ocho.',
  'dominio': 'EO02 y MU/FI01 en trabajos de archivos y leyes delimitadas.',
  'estado_actual': 'Realizaciones históricas ejecutadas y conservadas en sus vidas; no generalidad '
                   'independiente del soporte.',
  'limites': 'No transferencia abstracta universal, clonación de significado o retención simultánea de todas '
             'las calibraciones.',
  'fuentes': ['R05', 'R08']},
 {'id': 'MR08',
  'titulo': 'Señales aprendidas selección de función y aritmética preparada',
  'sencillo': 'Una señal adquirida puede decidir físicamente qué interacción preparada se utiliza, además de '
              'producir una etiqueta. Eso no demuestra aprendizaje del algoritmo de esa interacción.',
  'mecanismo': 'Un codec fijo presenta una forma arbitraria; cue y docente modifican soportes. Una consulta '
               'común emite un signo que se transduce a una función preparada. La rama Native procesa '
               'operandos por encuentros; la externa se reconoce como herramienta convencional.',
  'resultados': ['APD01 LEX_R03: mismas formas y operandos sin docente produjeron11/11/11 frente a3/21/−7 en '
                 'historia opuesta;619/619 entradas por historia. No se importaron memorias AUX a MAIN.',
                 'APD01 acumulador MAIN: offset10 adquirido desde resultado17; incrementos1,4,0,7,2 '
                 'produjeron11,15,15,22,24. El contrato de cinco quedó agotado, sin acreditar destrucción '
                 'del contenido.',
                 'APD02 renovó materialmente el acceso sin reset: desde24, ocho incrementos '
                 'produjeron25,29,29,36,38,41,42,42; después43,45,46 y46. Sin retorno genérico y sham no '
                 'dieron cifras.',
                 'APD02 compara/recuerda: docencias opuestas intercambiaron comparación actual y consulta '
                 'previa. APD03 luma/nara y APD04 clasifica/equilibra ampliaron formas finitas utilizables; '
                 'no inventaron las funciones.'],
  'controles': 'Docencia opuesta, omitida y desacoplada, cortes/sham y retención de formas anteriores. Los '
               'controles adversos conservaron rechazos y pérdidas al ampliar el hub.',
  'asistencia': 'SUMA/DIFERENCIA, codecs32−derecho y carga−32, conteo de muestras0/1, lector y contexto '
                'siguen preparados. El operador especifica el orden de las composiciones.',
  'dominio': 'Formas y valores finitos APD; no español libre ni sintaxis general.',
  'estado_actual': 'Formas y operaciones incorporadas históricamente al gestor y Génesis; disponibilidad 2.0 '
                   'pendiente del cotejo actual.',
  'limites': 'No algoritmo aritmético aprendido, cardinalidad general o nuevo significado NSM65. No sumar '
             'aliases o contextos y formas como facultades independientes. Renovación del acumulador sigue '
             'siendo P0 iniciada externamente.',
  'fuentes': ['R09', 'R10', 'R11', 'R12', 'R13']},
 {'id': 'MR09',
  'titulo': 'Selección ACT QUERY y acceso a información ambiental',
  'sencillo': 'Dentro de oportunidades preparadas, la historia puede cambiar si se consulta o actúa. Obtener '
              'y usar un hecho no prueba por sí solo su almacenamiento en memoria nativa.',
  'mecanismo': 'Sensores limitados presentan diferencias accesibles. El estado adquirido forma una emisión '
               'interpretada por un codec fijo. QUERY revela un hecho del entorno para la oportunidad '
               'posterior; ACT ejecuta la transformación seleccionada.',
  'resultados': ['APD02 AUX: con retorno, QUERY→ACT; omitido, cuatro QUERY sin archivo. Con ambos datos '
                 'visibles también preguntó inicialmente: no detector semántico general de ausencia.',
                 'APD03 MAIN:8/8 objetivos de archivos,14 oportunidades,8ACT y6QUERY; cuatro hechos nuevos y '
                 'dos consultas redundantes;12/14 acciones útiles. El sensor presenta int(second is None), '
                 'no el valor privado ni la acción correcta.',
                 'APD03 calidad/disponibilidad2/3: una suma Native23 fue perturbada externamente a24. No se '
                 'atribuye24 al cálculo nativo.',
                 'APD04 no presentaba al selector ID, frescura, versión o magnitud de caché;20 fuentes '
                 'compartían dos tags. Clasificar27 frente a20 podía ser correcto para caché obsoleta e '
                 'inútil para objeto actual14: límite de percepción preparada.',
                 'APD05 añadió un sensor P0 de versiones actual y previamente observada hacia FI128: prefijo '
                 'más reserva44/44 selecciones conformes,18/44 efectos útiles; reserva sola40/40 y16/40. '
                 'REAL/OMIT cambió la segunda elección USE/WAIT, pero USE no fue útil.'],
  'controles': 'Retorno omitido, historias emparejadas, información presente/ausente, proveedor perturbado y '
               'contrastes de sensor. El hecho revelado queda público en el entorno; eso no demuestra '
               'memoria física nativa entre pasos.',
  'asistencia': 'Objetivos, calendario, gramática finita, caché, cursor, codec y repertorio de acciones '
                'preparados. La organización no elige libremente nuevos hechos u objetivos.',
  'dominio': 'APD02/03 en objetivos aritméticos con archivos y APD04/05 en fuentes ambientales con '
             'codificación limitada.',
  'estado_actual': 'Selección y acceso P0/P1 con usos locales incorporados históricamente. El sensor APD05 '
                   'es ingeniería perceptiva, no atención aprendida.',
  'limites': 'No exploración general, política atencional útil sostenida o estrategia general de consulta. '
             'NULL no se traduce como WAIT: WAIT requiere cero material formado.',
  'fuentes': ['R10', 'R11', 'R12', 'R13']},
 {'id': 'MR10',
  'titulo': 'Continuidad operativa y estado emparejado',
  'sencillo': 'La continuidad de una vida comprende mundo físico y estado del servicio. Un snapshot aislado '
              'puede omitir colas, recibos, artefactos y progreso indispensables.',
  'mecanismo': 'Un propietario único serializa Runtime, interfaces, agenda, FIFO, IDs, recibos y archivos '
               'del protocolo. La reapertura concilia el mismo ID pendiente sin reinsertarlo y no repite '
               'automáticamente efectos externos inciertos.',
  'resultados': ['MA02 guardó un archivo pendiente; otro proceso restauró exactamente12 bytes y lo verificó. '
                 'MAIN realizó diez actuaciones aceptadas y cuatro commits.',
                 'MU R17 registró3684.0006458 segundos operativos no pausados,120/120 lecturas,12/12 '
                 'tramas128 y18 transacciones efectivas de19 oportunidades nominales. Actuación '
                 'simple89/215. Corte T104472 con epoch4 abierto y par completo.',
                 'APD01 R04:3720.089 segundos,25/25 peticiones materiales y4244/4244 entradas;17 signos, '
                 'números y artefactos,15/17 bajo presupuesto. Preserva el fallo de reversión de ruta.',
                 'APD02:3600.0955 segundos,42 eventos materiales y cuatro controles completos;4296/4296 '
                 'inputs,19SUCCESS,3RESOURCE_LIMIT y1EXECUTION_ERROR. El mismo ID pendiente continuó entre '
                 'procesos sin reinsertarlo.',
                 'APD03:3600.00059 segundos, dos asociaciones nuevas y objetivo final14+15→29 después de '
                 'continuar el ID pendiente. Su Full en otra ruta continuó otra vida, sin añadir esas '
                 'experiencias a MAIN.',
                 'APD04 conservó reservas adversas con STOP no confirmado y futuros inciertos. Un Full '
                 'separado revisó clasifica y obtuvo panel final24/24 y691/691 entradas; pendiente insertado '
                 'una vez. Otra ruta no equivale a otro equipo.',
                 'APD05:3603.173 segundos, MAIN T656741→684418,52 transportes completos y9604 IDs '
                 'Native:9600 aplicados y cuatro rechazos; cero pendientes finales. R01 pausada no avanzó '
                 'ticks; R02 continuó sus tres IDs heredados después de reanudar.'],
  'controles': 'Recarga en proceso nuevo, conservación de ID, payload, hash y secuencia; conciliación '
               'SQLite/outbox/VIDA/recibos; registro pasivo ON/OFF en protocolos representativos.',
  'asistencia': 'Persistencia, FIFO, supervisión, epochs y trabajadores son infraestructura, no memoria '
                'accesible para resolver respuestas. No borrar colas legítimas o efectos inciertos para '
                'embellecer el corte.',
  'dominio': 'Cada vida y par con contrato propio. CF01→EO01→EO02 son forks R9 N26; MA02 es otra preparación '
             'N67 y MU/APD descienden de ella. No son E1 histórico renombrado.',
  'estado_actual': 'Protocolos persistentes incorporados históricamente y necesarios para continuidad. La '
                   'comprobación actual de 2.0 resuelve selección y dependencias efectivas.',
  'limites': 'ZIP científico reducido no es respaldo operativo completo. Duración no acredita estabilidad '
             'ilimitada, número de entradas no cuenta aprendizajes y cierre limpio no certifica cognición '
             'general.',
  'fuentes': ['R03', 'R04', 'R05', 'R06', 'R07', 'R08', 'R09', 'R10', 'R11', 'R12', 'R13']}]

COBERTURA = {'campanas_con_artefactos_abiertos': ['MI01',
                                      'MI02',
                                      'CF01',
                                      'ENTE01',
                                      'ENTE02',
                                      'MENTE_ACUMULATIVA',
                                      'MENTE_ACUMULATIVA_R02',
                                      'MENTE_UNIFICADA_Y_FI01',
                                      'APD01',
                                      'APD02',
                                      'APD03',
                                      'APD04',
                                      'APD05'],
 'no_afirmado': 'No apareció APD06 en los directorios de campañas examinados; esto no acredita inexistencia '
                'en toda la computadora. El responsable actual coteja Cognitive 2.0 y su selección efectiva.',
 'integracion': 'No inferir integración actual por API o biblioteca compartida ni sumar memorias de ramas. '
                'NSM65 no recibe mejoras semánticas por contar formas, señales o entradas.',
 'lectura': 'Informes MI01, MI02, CF01, ENTE01, ENTE02, MA01, MA02, MUFI, APD03 y APD05 examinados; APD01, '
            'APD02 y APD04 por secciones dirigidas identificadas. Primarios y recálculos seleccionados se '
            'individualizan en FUENTES.',
 'escrituras': 'Únicamente este módulo editorial pedido por root. No documentos finales, cambios científicos '
               'ni archivos administrativos visibles.'}
