"""Serialize authored, provisional interpretations alongside exact primary witnesses.

AUDITOR only. This is neither a participant nor an automatic semantic verdict.
Run before sealing. Calculations never feed back into any Runtime.
"""
from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parents[1]
def read(name):return json.loads((ROOT/name).read_text(encoding='utf8'))
def witness(name,pointer=''):
    p=ROOT/name
    return {'member':name,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'pointer':pointer}
def put(name,data):
    p=ROOT/'revision'/name;p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def report(name,text):(ROOT/'revision'/name).write_text(text.strip()+'\n',encoding='utf8')
def main():
    life=read('revision/VIDA_PRINCIPAL.json')
    main='resultados/vida_integral/EI_D01/MEDICIONES.json'
    upd='resultados/continuacion/E1_MAIN_884_1220/MEDICIONES.json'
    k65='resultados/continuacion/E1_MAIN_K65_1907_2353/MEDICIONES.json'
    tail='resultados/continuacion/E1_MAIN_TAIL_2353_2493/MEDICIONES.json'
    cmp='resultados/auditoria/COMPOSICION_E1/MEDICIONES.json'
    late='resultados/auditoria/MEMORIAS_TARDIAS_2283_R1/MEDICIONES.json'
    wave='resultados/auditoria/CRECIMIENTO_OCUPACION/MEDICIONES.json'
    occ='resultados/auditoria/OCUPACION_Y_RESTAURACION/MEDICIONES.json'
    c=read(cmp);l=read(late);w=read(wave)
    put('ARQUITECTURA_E1.json',{
      'individual':'EI_D01 and exact serialized continuations, one T0 preparation',
      'N':67,'backend':'Lazy, official4.5/v27','initial_material_sites':107,'initial_interfaces':328,
      'basic_buffers_bytes':32*67**3,'measured_not_estimated_process_costs':'RECURSOS_Y_COSTES.json and jobs/*/COMMAND.json',
      'prepared':'Geometry, comparators, candidate ports, supplies, normalizers, periodic opportunities and sensing protocol. No trained target snapshot imported.',
      'acquired':'Actual temporal/contact histories and forms; moving/relative reference; two quantitative operands; social receiver/reference and return form; local query response; later quantitative revision and new65 correspondences attempted.',
      'interface_changes':[{'tick':1220,'new_empty_interfaces':18},{'tick':1907,'new_empty_interfaces':325}],
      'interface_attribution':'External measurement/entry registry changes; verified identical physical RAW/clocks at installation. Not native bodily growth.',
      'integration_vs_coexistence':'INTEGRACION_CAUSAL.json lists actual native edges. Sharing a Runtime does not establish all modules mutually integrated.',
      'witnesses':[witness(main),witness('revision/VIDA_PRINCIPAL.json'),witness('revision/INTEGRACION_CAUSAL.json')]})
    put('RETENCION_Y_PLASTICIDAD.json',{
      'domain':'One finite E1 genealogy; max positive horizon is not terminal availability',
      'old_operands':{'reference':36,'object':16,'positive_response':{'load':7,'direction':[1,0,0]},
        'last_positive_measured_tick':2283,'later_failed_tick':2350,'causal_content_check':[
          {'condition':r['condition'],'post':r['post'],'branch_exact':r['branch_exact'],'full_MAIN_equal':r['full_MAIN_equal'],
           'current_boundary_receipts':r['current_boundary_receipts']}for r in l['rows']],
        'interpretation':'Actual old contents influence late comparison. Removing the whole reference also removes structural support, so same-support load changes are the informative content interventions. No diagnostic edit returns to MAIN.'},
      'selective_update':{'reference_before':54,'additional_material':13,'reference_after':67,
         'observed_directions_X_at_941_1008_1075_1142':[-1,1,-1,1],
         'offpath_equal_dose_directions':[-1,-1,-1,1],
         'timing':'At941 the comparator still uses old54; updated67 reaches its reference hub after that comparison. Later comparisons use67.',
         'prediction_attribution':'AUDITOR predictions stored before targets; not evidence E1 independently forecast the future.',
         'nonmodified_operands':'36/16 remain useful943/1010/1077/1144 and later2283'},
      'old_count':'Strict952..1220 cadence/phase predicate failed, but relevant carrier remained and later1287/1354 probes recovered without reteaching. Protocol failure is not erasure.',
      'repertoire':{'auxiliary':{'first':[65,65],'later':[186,186]},
        'E1_first_across_blocks':[60,65],'E1_complete_rounds':[[57,65],[53,65],[4,65]],
        'E1_no_event_and_unpaired':'Both0/65 first,0/186 later in matched continuations',
        'scope':'Opaque correspondences. Cumulative first responses occurred at different ticks, not65 simultaneous semantic concepts.'},
      'terminal':{'tick':2493,'new_requests':178,'applied':1,'rejected_occupied':177,
        'attempted_new_teaching':'All4 intended late revision inputs rejected; no new acquisition claimed',
        'later_TM':'2417/2484 active semantic7/load1/direction0 is not the earlier qualified7X response',
        'interpretation':'Access severely lost in this preparation. Retained RAW fragments alone are not available knowledge; rejected input alone is not forgetting.'},
      'witnesses':[witness(main),witness(upd),witness(k65),witness(tail),witness(late),witness(occ)]})
    put('COMPOSICION_FUNCIONAL.json',{
      'domain':'Native composition of previously acquired order/contact contributions in E1, not open productive grammar',
      'actual_join206':c['actual_formed206'],'native_branch':c['native_branch'],'local_branch_exact':c['local_branch_exact'],
      'rows':[{'condition':r['condition'],'parents_unchanged':r['parents_unchanged'],'full_original884_equal':r['full_original884_equal'],
        'observations':[{'tick':f['tick'],'join':f['view']['common_join'],'target_use':f['view']['joint']['plus.changed']['use_site']}for f in r['frames']]}for r in c['rows']],
      'interpretation':'Incoming26(1,0,1) and30(0,1,0) yield56(1,1,1). Either cut or removal of X/Z with aggregate load56 preserved abolishes target63(1,0,1) at210; sham retains it and the complete final state. A7(0,-1,0) remains, so the apparatus is not simply dead.',
      'semantic_scope':'Order-sensitive routing and functional integration are demonstrated; current words/ports do not prove every role or referent abstractly bound. No global E4 primitive award.',
      'witnesses':[witness(cmp),witness(main),witness('revision/NSM65_EVIDENCIAS.json')]})
    put('CONSULTAS_Y_ACCESO.json',{
      'conditions':'Same accessible external opportunity, different local/remote acquired histories',
      'observed':'Unknown local state emits active zero-load question at76/143. Native remote response is acquired at137, used204, changes gate210 to active direction0/load28. Question recurs277.',
      'known_local':'First76 request inhibited; later access changes and questions recur. Finite consumable access, not permanent sufficiency detection.',
      'causal_E1':'Cut actual remote return before137 removes local acquisition/response and restores question210. Sham and exact restoration retain inhibition; TM206/order555 stay functional.',
      'not_demonstrated':'Learned general choice of when/whom/what to ask, exhaustion detection, curiosity or policy selecting most informative source. Period and destination are prepared.',
      'failure_families':'Three bounded access/conservation families retained; no automatic matter/clock cleanup.',
      'witnesses':[witness('resultados/consulta/QA_INTEGRAL_CAUSAL/MEDICIONES.json'),witness(main)],
      'additional_primary_members':'resultados/consulta/QA_*/MEDICIONES.json and resultados/consulta_conservada/'})
    put('COMUNICACION_Y_APRENDIZAJE_SOCIAL.json',{
      'E1_native_path':'E1 independently experienced backup → physical transfer → B acquired reference80 → B own object → comparison147 → physical return148 → E1 form149 → query216 → use221 → delivery225',
      'backup_cost':'Acquired through its own extra cue/resource exposures, never free memory cloning.',
      'positive_return':{'query_load':24,'use_and_delivery_load':37,'direction_delivery':[1,1,1]},
      'negative_return':{'query_load':31,'use_and_delivery_load':44,'direction_delivery':[-1,1,1]},
      'causal_limits':'Positive message cut removes intended37 but a wrong negative32 remains. Negative cut retains negative32 rather than44: negative direction alone is not attributable to that message. Do not claim every response disappears on cut.',
      'reserved_return':'Frozen V3 source23/object16→24/37 and source23/object35→31/44 both matched, after preserving failed V1/V2 load predictions.',
      'additional_social_result':'Auxiliary order-message receiver learns then uses new relationship; current role reversal/translation/delay tests are auxiliary, not added to E1 knowledge.',
      'bidirectional_scope':'Bounded two-way physical information path and receiver use, not general dialogue, general deictic language or bidirectional teaching of all primitive meanings.',
      'witnesses':[witness(main),witness('resultados/retorno/RET_CAUSAL/MEDICIONES.json'),witness('resultados/retorno/RET_CAUSAL_MINUS/MEDICIONES.json'),witness('resultados/retorno/RET_V3_R31_SOURCE23_OBJECT16/MEDICIONES.json'),witness('resultados/retorno/RET_V3_R32_SOURCE23_OBJECT35/MEDICIONES.json')]})
    put('REGULACION_NATIVA.json',{
      'R0':'Prepared zero-load counterflows, guards, route separation and interceptors; their inputs/resources are recorded, not hidden cleanup.',
      'R1':'The physically acquired P/Q direction selects the useful prepared regulating path; secondary quantity137 differs. This is conditional realization from learned state.',
      'R2':'NOT_DEMONSTRATED_IN_E1: no causal evidence that consequences train a general choice of regulation strategy. There are no subjective preference claims.',
      'causal_domain':'Offpath/equal-cargo and sham controls retain sensing/actuation. A useful guard is not by name learned attention.',
      'late_auxiliary_regulation':'R0 intervention can restore a local acquisition near1956/1962 on a fork; later2029 access fails. It was not imported into MAIN.',
      'MAIN_edits':'No RAW deletion, clock reset, trained-memory transplant or favorable rollback in MAIN.',
      'witnesses':[witness(main),witness('revision/VIDA_PRINCIPAL.json')],
      'additional_members':'front_relations/resultados/ and CALCULOS#/integral_cases/*/observations/regulation'})
    put('DESCUBRIMIENTOS_NATIVOS.json',{
      'occupation_wave':{'profile':w['profile'],'first_birth':{k:v for k,v in w['first_birth'].items()if k not in('pre_Moore27',)},
        'interventions':w['rows'],'passive_replay_exact2353':w['replay_exact2353'],
        'interpretation':'Fast occupation growth precedes the first semantic7 birth. Removing one opposite-neighbour symmetry member prevents that specific EMPTY_XNOR birth but does not stop the global wave; not a single-cause explanation.',
        'not_a_claim':'Not19664 load saturation, word capacity limit, quantum nonlocality or general cognitive discovery. The native field named semantic is a physical kernel field, not a count of linguistic meanings.',
        'history_controls2353':{'MAIN_occupied':298024,'no_event_occupied':348,'unpaired_occupied':297334,'interpretation':'Unpaired material also produces near-total occupation. The wave is not isolated as caused by successful semantic learning or by65correct correspondences; doses/routes/recurrences are relevant.'},
        'fork_accounting':'Two causal diagnostic forks plus73 pre-tick passive preservation copies before2292; the latter are technical copies, not independent individuals.'},
      'pending_probe_intervention':'A reader-cut empties the entry site and admits a pending current probe that the occupied baseline rejects. A prestate-only auditor without current inputs cannot certify this branch. Exact receipts expose the distinction.',
      'functional_access':'Occupied-destination precedence can destroy a travelling reader despite preserved source records. Direction/amount alone cannot identify actual transport.',
      'finite_RAW_plateau':'2493→2498 can preserve RAW while clocks differ. No full-state fixed-point or unlimited stability assertion.',
      'witnesses':[witness(wave),witness(late),witness(occ)]})
    put('CONTROLES_Y_RESERVAS.json',{
      'controls_executed':['opposite history','no experience','uncoupled cue/event','omitted signal','equal cargo offpath','actual message cut','single acquired record cut','same-support content edit on diagnostic fork','sham exact full state','new object/load','new order/interval','role/actor inversion in auxiliary action trace','restoration and next interaction'],
      'reserve_examples':[{'case':'EI_R31','outcome':'Adverse temporal read collision at531; retain failure, other module outcomes separate'},
        {'case':'EI_R32','outcome':'AB1 loads13/17 reserved new preparation produces35/42/53 in current order apparatus'},
        {'case':'RET_V3_R31/R32','outcome':'Frozen new source/object pairs both positive after failed prior predictions'},
        {'case':'MAIN_884_1220','outcome':'Four prior quantitative predictions match; control offpath has different pattern'}],
      'scope':'Each reservation only certifies its varied axis/domain. Fresh auxiliary preparations and deterministic reruns are not replicas of MAIN acquisition.',
      'failed_audit_preserved':{'native_V1':'resultados/auditoria/MEMORIAS_TARDIAS_2283: all native fork outputs retained; assertion based on omitted current-input assumption failed',
        'syntax_V2':'jobs/ROOT_LATE_MEMORY_CAUSAL_AUDIT_R1: parser failed before Runtime; archived source97b178eb..., not a physical negative',
        'corrected_auditor':'R1 certifies only branches including declared application boundary; reader-cut row explicitly not certified by passive local checker'},
      'sources':'INDICE_EVIDENCIA.json and front reports give exact case-level locators; no favorable-case filtering',
      'witnesses':[witness(cmp),witness(late),witness('revision/CALCULOS.json')]})
    report('LECTURA_PROVISIONAL.md','''# CPC9 — lectura provisional

E1 adquirió y utilizó relaciones de orden y contacto, referencias comparables,
formas posteriores y respuestas recibidas durante una misma vida N67, T0–2493.
Los controles conservan diferencias dependientes de experiencia: no basta el
nombre del ensayo ni la presencia de material. El kernel y el WHL oficiales
permanecen intactos.

La composición206 necesita dos llegadas físicas; preservando carga56 pero
retirando X o Z desaparece la consecuencia63 de210, mientras queda actividad7.
Una respuesta recibida cambia la pregunta210; cortarla no paraliza las otras
funciones medidas. La oportunidad y el destinatario estaban preparados.

La revisión54→67 cambió comparaciones posteriores sin borrar los operandos36/16.
Estos todavía causaban la respuesta2283: cambiar sólo36→5 la invierte;36→16
produce7 activo sin dirección. No se editó MAIN: son copias diagnósticas.

El escalado fue adverso. Una preparación auxiliar sostuvo65 correspondencias,
pero E1 pasó de60/65 primeras respuestas acumuladas a57/65,53/65 y4/65 en rondas
completas. La ocupación llegó a298024/300763 sitios en2353. Los rechazos tardíos
no son nuevas adquisiciones ni prueban por sí solos borrado de memoria.

NSM65 tiene65 preguntas individuales y14 ensayos de función limitada o
prerrequisito. La adjudicación máxima de episodios E1 es60E0,4E2 y1E3: DOS
calibrado, ANTES, TOCAR, COMO y MÁS cuantitativo. No se afirman cinco significados
humanos completos ni cinco relaciones accesibles al final2493. E3 sólo corresponde
a transferencia cuantitativa finita; no hay concesión globalE4/E5.

La recuperación histórica es otro resultado: el Cognitive Core distingue
reconstrucción ejecutada, preservación documental y capacidades no integradas.
No se atribuye toda esa biblioteca a E1. No se demostró regulaciónR2, elección
general aprendida de interlocutor ni lenguaje productivo abierto.

Datos: `VIDA_PRINCIPAL.json`, `CALCULOS.json`, `INDICE_EVIDENCIA.json` y sus
localizadores primarios. Interpretaciones: informes por función y fichasNSM.
La prueba limpia y el hash del ZIP exacto están fuera del contenedor.
''')
    report('LIMITACIONES_Y_PENDIENTES.md','''# Alcances y límites observados

## Preparación y adquisición

Los comparadores, las rutas, guardas, normalizadores, horarios de oportunidades y
puertos son preparación externa. Sus contenidos/referencias/formas pueden
adquirirse físicamente. Trasladar una decisión a C++ no cambia esa atribución.
Las previsiones cuantitativas del informe son del AUDITOR; no se añade por ellas
una facultad de pronóstico general a E1.

## Generalización

El mismo E1 utilizó objetos cuantitativos nuevos y una referencia revisada.
ANTES/TOCAR tienen usos y reservas finitas, pero nuevas situaciones tardías fallan
por interferencia/ocupación. Las reservas temporales/calibraciones auxiliares no
se suman como transferencia adquirida de MAIN. YO/TÚ sólo tienen una traza causal
auxiliar de roles; no signos deícticos adquiridos. NO no se equipara con invertir
una dirección y HAY no se equipara con silencio o un sensor externo.

## Integración y comunicación

Hay enlaces causales comprobados entre experiencias, formas, composición, retorno
y uso. Otras capacidades sólo coexisten en la misma geometría. El retorno negativo
tiene un residual por defecto: su dirección persiste tras un corte; el contenido
completo44 no. No se afirma conversación libre ni enseñanza bidireccional de
significados completos. El respaldo recibió experiencias propias adicionales.

## Conservación y regulación

No existe evidencia de memoria infinita ni de máximo universal65. La preparación
integrada se densifica; la auxiliar de65 no tiene el mismo conflicto. En2493 la
mayoría de entradas están ocupadas y no se certifica acceso a los cinco candidatos.
Se conserva el estado adverso, no se repara MAIN. RegulaciónR0/R1 no demuestraR2.

## Auditoría y reproducción

Se conservan fallos técnicos, predicciones erróneas y revisiones identificadas.
Un auditor local inicial omitió una entrada pendiente; el corte de lector la
admitía y cambiaba el protocolo. La corrección acota el comprobador, no alterav27.
Las reproducciones idénticas no son muestras independientes. Python audit hooks
verifican aperturas de Python, no constituyen una prueba universal de cada syscall.
El núcleo preserva16 capacidades documentales sin afirmar reproducción fresca
completa; sus matrices son la autoridad del alcance histórico final.

## Crecimiento semántico

Se ejecutaron relaciones nativas reales, no65 conceptos humanos. Las otras51
entradas tienen preguntas y bloqueos específicos, no resultados fabricados.
Productividad abierta, regulación aprendida general y crecimiento a10000 palabras
siguen indeterminados. El límite observado corresponde a organizaciones y
protocolos finitos; no prueba imposibilidad fundamental del kernel.
''')
    print(json.dumps({'reports_written':11,'NSM_maximum_levels':read('revision/NSM65_EVIDENCIAS.json')['summary']['E1_levels'],'no_Runtime_created':True}))
if __name__=='__main__':main()
