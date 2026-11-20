"""Final evidence synthesis. Reads closed records only, never imports DEE."""
from pathlib import Path
import csv,datetime,hashlib,json,shutil,re
P=Path(__file__).resolve().parent.parent;R=P.parent.parent.parent;C=R/'DEE Cognitive 2.0';S=C/'sistema';E=P/'entrega/EXPEDIENTE'
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def desc(p):p=Path(p);return {'path':str(p),'bytes':p.stat().st_size,'sha256':sha(p)}
def write(p,v):p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def text(p,v):p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(v,encoding='utf-8')
def readable(v):
    """Editorial spacing on authored prose only, never primaries or JSON IDs."""
    v=v.replace('GenesisNativeWorld','`GenesisNativeWorld`')
    for old,new in [('sinvalencia','sin valencia'),('actuadoranulado','actuador anulado'),('memoriaalfa','memoria alfa'),('selecciónpersonalyaplicación','selección personal y aplicación'),('paquetesdecontrol','paquetes de control'),('estadoexistente','estado existente'),('unpropietario','un propietario'),('vidae','vida e'),('DCS11-MM-0011.29','DCS11-MM-001 / edición 1.29'),('Universev27','Universe v27'),('W/Uemparejados','W/U emparejados'),('Gde','G de'),('Wde','W de'),('Ugenérico','U genérico'),('Hfue','H fue'),('enlos','en los'),('backendmente_unificada','backend mente_unificada'),('Manualcap','Manual cap'),('puntoinicial','punto inicial'),('ZIPdeanálisis','ZIP de análisis'),('estadosoperativos','estados operativos'),('QueueDBliteral','`QueueDB` literal')]:v=v.replace(old,new)
    for old,new in [('MAINtiene','MAIN tiene'),('Bsin','B sin'),('Bde','B de'),('Bprevio','B previo'),('Binmediatamente','B inmediatamente'),('Hdependiente','H dependiente'),('RAWpor','RAW por'),('RAMes','RAM es'),('raw0y','raw0 y'),('bytesdelparcompleto','bytes del par completo'),('bytesde','bytes de'),('64B','64 bytes '),('enuna','en una'),('enel','en el'),('conavisos','con avisos'),('yusosposterioresdealfa','y usos posteriores de alfa'),('yavanzaron','y avanzaron'),('decalibración','de calibración'),('Aincluidodesarrollo','A incluido desarrollo'),('deadvertenciaprototipo','de advertencia prototipo'),('delcontrol','del control'),('dereserva','de reserva'),('depanel','de panel'),('decontinuación','de continuación'),('horasno','horas no'),('recálculosdocumentales','recálculos documentales'),('primerosavisos','primeros avisos'),('mincontinuos','minutos continuos'),('mincontado','minutos contado'),('clonar_prefijo.pyy','`clonar_prefijo.py` y'),('IDsya','IDs ya')]:v=v.replace(old,new)
    parts=re.split(r'(`[^`]*`)',v)
    for i,s in enumerate(parts):
        if s.startswith('`'):continue
        protected={}
        technical=['raw0','v27','P0/R0','P1/R1','P2/R2','SQLite','utf8','--eci01']+re.findall(r'\bR\d+[A-Z]\b',s)
        for j,token in enumerate(dict.fromkeys(technical)):
            key='§'+chr(97+j)+'§';protected[key]=token;s=s.replace(token,key)
        s=re.sub(r'(?<=\d)(?=[a-záéíóúñ])',' ',s)
        s=re.sub(r'(?<=[a-záéíóúñ])(?=\d)',' ',s)
        s=re.sub(r'\b(MAIN|SYNC|ASYNC)(?=\d)',r'\1 ',s)
        s=re.sub(r'(?<=\d)(?=NULL|Native|MiB|B\b)',' ',s)
        s=re.sub(r',(?=\S)',', ',s)
        s=re.sub(r':(?=\d)',': ',s)
        for key,token in protected.items():s=s.replace(key,token)
        parts[i]=s
    return ''.join(parts)
adopt=read(P/'control/ADOPCION_PRODUCTO_PI02.json');pub=read(P/'documentos/DOCUMENTOS_PUBLICADOS_PI02_FINAL.json')
card=read(S/'estado/vidas/ECI02_PI02_MAIN/VIDA.json');active=read(S/'estado/ACTIVO.json');project=read(C/'PROYECTO.json');ret=read(P/'ensayos/RESUMEN_RETENCION_PI02.json');reop=read(P/'control/REAPERTURA_Y_CONTINUACION_PI02.json')
manual=C/'DEE_Cognitive_2_0_Manual_Maestro_DCS11_MM_001_Edicion_1_21.docx';comp=R/'CPC - Experimentos y mecanismos/COMPENDIO_MAESTRO_DE_MECANISMOS_Y_RESULTADOS_DEE.docx'
if adopt['phase']!='COMMITTED'or active['life_id']!='ECI02_PI02_MAIN'or active['tick']!=753346 or project['manual_internal_edition']!='1.29':raise ValueError('Actual final adoption/publication required; no future tense deliverable')
for k,p in [('Manual',manual),('Compendium',comp)]:
    expected=read(P/'documentos/ACTUALIZACION_DOCUMENTAL_PI02_FINAL_1_29.json')[k]['sha256']
    if sha(p)!=expected:raise ValueError('Published complete document differs')
arms=[];allrows=[]
for name in('MAIN','UNPAIRED','NO_TRAIN','WARNING_CUT','VALENCE_OMIT','ACTUATOR_NULL'):
    x=read(P/'ensayos'/('RESUMEN_PI02_R04_RES_'+name+'.json'));cs=x['device_commands'];fi=[v for v in x['opportunities']if v['effect']['kind']=='WORK_EFFECT']
    arms.append({'arm':name,'life':x['life'],'start_tick':740937,'end_tick':750137,'planned':12,'completed':len(x['opportunities']),'FI_responses':len(fi),'FI_NULL':sum(v['effect']['physical_choice']is None for v in fi),'material_zero':sum(v['effect']['physical_choice']==0 for v in fi),'resources':x['opportunities'][-1]['resources_total'],'CLOSE_formed':len(x['warning_signatures']),'CLOSE_applied':sum(v['origin']=='learned_warning'and v.get('applied')is True for v in cs),'control_packets_spent':sum(v.get('applied')is True for v in cs),'primary':str(P/'ensayos'/('RESUMEN_PI02_R04_RES_'+name+'.json'))})
    for o in x['opportunities']:
        eff=o['effect'];isfi=eff['kind']=='WORK_EFFECT';device=eff.get('device',{});allrows.append({'arm':name,'life':x['life'],'episode':o['episode'],'q':o['q'],'end_tick':o['tick'],'native_route':o['route'],'effect_kind':eff['kind'],'FI_physical_choice':('NULL'if eff.get('physical_choice')is None else eff['physical_choice'])if isfi else'OUTSIDE_FI_DOMAIN','FI_applied_command':('NULL'if eff.get('applied_command')is None else eff['applied_command'])if isfi else'OUTSIDE_FI_DOMAIN','device_formed':device.get('command','OUTSIDE_DEVICE_DOMAIN'),'device_applied':device.get('applied','OUTSIDE_DEVICE_DOMAIN'),'useful':eff['useful'],'resources_total':o['resources_total'],'feedback_status':'ABSENT'if o['feedback']is None else o['feedback']['status'],'source':'EVIDENCIA/D_R04/INDICE_D_R04.json'})
maps=E/'MAPAS';maps.mkdir(parents=True,exist_ok=True)
for name,rows in [('COMPARACION_BRAZOS_R04.csv',arms),('OPORTUNIDADES_RESERVADAS_R04.csv',allrows)]:
    with(maps/name).open('w',encoding='utf-8',newline='')as f:w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
matrix=[
 ['Inicio de oportunidades','PI01: sensor y normalizador por oportunidad','Retornos físicos O inician trabajos bajo tiempo genérico','Native recurrente; período 67 y capacidad 308 ticks en A / 710 en R04, preparados','P0 + selección dependiente de historia','MAIN A/R04','Incorporado, sin iniciativa temporal aprendida'],
 ['Selección por consecuencia','PI01:16/18 vs12/18, despachadorMA/FI','A:10/12 vs7/12omit; referenciaWSLS10/12','Native cambia dirección por valencia; host conecta salida/acceso','Local, no política general','MAIN T740343','Incorporado; R04sinvalencia7>6MAIN'],
 ['Comparación y admisión','FI128 disponible; lector temprano fijado','Interferencia cambia0/+ a−; retirar competencia recupera uso','Codec/lector preparados; Native produce la respuesta','P0 funcional, recuperación sin restauración','MAIN T740937','Instrumentación asíncrona y diagnóstico incorporados'],
 ['Advertencia','CPC/experimental_regulation disponibles en otras preparaciones','MAIN adquiereW/U; firma H gobierna válvula y sostieneFI','Soporte adquirido Native; sensor, G, decoder y dispositivo externos','P1/R1 local con P0/R0, no estrategiaP2/R2','MAIN R04 T750137','Incorporado; falsa alarma e inversión perjudicial'],
 ['Uso útil integrado','Repertorio disponible, no todos sus usos son planes propios','6/12; CLOSE cortada 4/12; historia desfasada 4/12; actuadores anulados 0/12 productos, 6 FI válidos y 0 NULL','H→válvula→admisiónFI→actuación→consecuencia→O','Organización funcional híbrida con frontera declarada','MAIN misma genealogía','Incorporado con alcance local'],
 ['Memoria/etiquetas anteriores','luma+,nara−,clasifica−,suma+,alfa−','12/12 testigos hastaT751546;929/929entradas','Contenido Native; consultas y secuencia del operador','Retención observada, no65significados','MAIN T750137–751546','Conservadas bajo panel, no otro panel enT753346'],
 ['Composición aritmética','Operación directa preparada disponible','6+7→13; resultado real13−5→8','Cálculo Native; transporte/orden externos','Encadenamiento asistido, no plan autogenerado','MAIN T751068–751464','Conservado'],
 ['Continuidad y trabajo nuevo','Par completoPI01; diversas ramas históricas','Guardar/reabrir:2/2 nuevos trabajos sinU; finalT753346','Estado adquirido propio; ofertaexterna0ticks','Uso posterior y retención local','MAIN T751546–753346','COMMITTED; producto importado/guardado0ticks']]
with(maps/'MATRIZ_ANTES_DESPUES.csv').open('w',encoding='utf-8',newline='')as f:w=csv.writer(f);w.writerow(['familia','antes','despues_observado','atribucion','nivel','vida_corte','incorporacion_limite']);w.writerows(matrix)
roots={'product':str(C),'campaign':str(P),'official_thinking':str(R/'4.5'),'protected_parent':str(S/'estado/vidas/ECI02_PI01_MAIN')}
db=S/'estado/servicios_persistentes/ECI02_PI02_MAIN/cola.sqlite3'
continuity={'schema':'DEE.PI02.final.actual_continuity.v1','inspection_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'principal':{'life_id':card['life_id'],'world_id':card['world_id'],'N':67,'tick':753346,'profile':card['profile'],'selection':'COMMITTED'},'physical_parent':adopt['record']['PI02_migration']['physical_parent'],'transport_parent_is_separate':card['parent'],'snapshots':{'current_product':desc(S/card['snapshot']),'full_source_pair':read(P/'control/PAR_FINAL_PI02.json')['pair'],'product_transport_seed':str(S/'estado/pares_iniciales/ECI02_PI02_MAIN'),'seed_does_not_override_a_later_future':True},'state_components':{'VIDA':desc(S/'estado/vidas/ECI02_PI02_MAIN/VIDA.json'),'SQLite_current_closed':desc(db),'interfaces_agenda_native_receipts':'Included in the Native snapshot, not RAW/clocks alone','worker_artifacts_and_environment':str(S/'estado/servicios_locales/ECI02_PI02_MAIN'),'outbox_results':str(S/'estado/servicios_persistentes/ECI02_PI02_MAIN/resultados'),'paired_manifest':desc(S/'estado/pares_iniciales/ECI02_PI02_MAIN/EXPORTACION_SERVICIO.json'),'current_WAL_SHM_policy':'No incoherent live copy; product0tick witness requires no nonemptyWAL and reconciled closed queue'},'roots':roots,'manual':{**desc(manual),'identifier':'DCS11-MM-001','internal_edition':'1.29','same_filename_for_compatibility':True},'caps':{'R02_A_resources':10,'R04_resources_total':8,'R04_opportunities_consumed':14,'R04_control_packets_spent':10,'R04_control_packets_available':6,'retention_panel_cut':751546,'retention_panel':[12,12],'Native_panel_inputs':[929,929],'last_new_work':[2,2]},'source_candidate_store_status':'Archived frozen provenance of the adopted same identity, not a second principal to advance; continue only the product store. Controls retain independent identities.','budget':{'Native_ticks_all_branches':93340,'ceiling':100000,'counts_are_not_concepts_or_independent_learning_samples':True,'hard_stop_unchanged':'2026-11-08T21:04:20-06:00'},'reopening_command':'motor/python313/python.exe -I -B -X utf8 sistema/gestionar.py --system-root sistema mente-unificada-iniciar --vida ECI02_PI02_MAIN --backend mente_unificada --eci01 --pausado --intervalo 60 --guardar-cada 3600','proofs':{'adoption':desc(P/'control/ADOPCION_PRODUCTO_PI02.json'),'product_reopening0':desc(P/'control/REAPERTURA_PRODUCTO_PI02.json'),'actual_new_function_after_reopen':desc(P/'control/REAPERTURA_Y_CONTINUACION_PI02.json'),'manual_publication':desc(P/'documentos/DOCUMENTOS_PUBLICADOS_PI02_FINAL.json')},'scope':'Analysis package, not an executable backup. No control memories merged, no T0, no kernel/WHL change.'}
write(P/'CONTINUIDAD_PI02.json',continuity);write(maps/'CONTINUIDAD_PI02.json',continuity)
facts={'life':card['life_id'],'parent':'ECI02_PI01_MAIN T735843','runtime':'One inherited N67 OrganizationalWorld under existing single-owner contract','classification':'Functional composite Native organization coupled to an external finite simulated workbench; O/H/FI are regions/mechanisms, not separate autonomous minds','components':[{'name':'O','role':'Inherited acquired direction selection; returnsX/Y','prepared':'Recurrence and fixed decoder','history':'PI01/A/actual consequencesR04'},{'name':'H','role':'W/U acquired support and warning-dependent direction','prepared':'W/U/G channels, fixed output signature and readout','history':'Actual MAIN first failure pairing, never copied from prototype'},{'name':'FI128','role':'Inherited physical comparator, output−1/0/+1','prepared':'Independent-operand codec, sampling/query calendar and E/q+4reader','history':'Inherited plus current uses, admission perturbations and recovery'},{'name':'Legacy memory/associations/arithmetic','role':'Retained representative12use panel','prepared':'Existing interfaces/readers and operator task order','history':'Inherited and sequentially used in this MAIN'}],'external_apparatus':'ValveTTL1474, work/resource/control packet files, fixtures, rejection sensor and transducers. Its metadata/log is unavailable as an actor policy or external memory.','Native_modification':'Physical directions, charges, fields, supports and encounters under frozenv27. No RAW/clock writes.','host_decisions':'Anatomy, public opportunities, phase/capacity, fixed codecs/connections, scoring actual consequence, time, technical save/promotion, interpretation.','Native_decisions_observed':'ActualOdirection selects work/device; acquiredHsignature selects fixedCLOSE. Timing/utility generalization beyond these conditions not shown.'}
write(maps/'FICHA_ENTE_Y_ASISTENCIA.json',facts)
docdir=E/'MANUAL';docdir.mkdir(exist_ok=True)
for source in(manual,comp):shutil.copyfile(source,docdir/source.name)
code=E/'CODIGO/SISTEMA_INCORPORADO';decision=read(P/'control/DECISION_FINAL_PI02.json')
for item in decision['approved_code_files']:
    src=S/item['file'];dst=code/item['file'];dst.parent.mkdir(parents=True,exist_ok=True)
    if sha(src)!=item['sha256']:raise ValueError('Actual incorporated source changed')
    shutil.copyfile(src,dst)
for filename in('servicio_ensayo.py','clonar_prefijo.py','ejecutar_habitat_R04.py','panel_retencion_PI02.py','reabrir_y_cerrar_PI02.py','preparar_operacion_R04_OP1.py','incorporar_PI02.py','construir_decision_PI02.py','reabrir_producto_PI02_0ticks.py'):
    dst=E/'CODIGO/EJECUCION_Y_CONTINUIDAD'/filename;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(P/'codigo'/filename,dst)
head='| Brazo | Productos | FI / NULL | CLOSE formada / aplicada | Paquetes gastados |\n|---|---:|---:|---:|---:|\n'
table=head+'\n'.join('| '+a['arm']+' | '+str(a['resources'])+'/12 | '+str(a['FI_responses'])+' / '+str(a['FI_NULL'])+' | '+str(a['CLOSE_formed'])+' / '+str(a['CLOSE_applied'])+' | '+str(a['control_packets_spent'])+' |'for a in arms)
report=f'''# PI02: una advertencia adquirida interviene en un ciclo de actuación útil

Corte real: 8 de noviembre de 2026, America/Mexico_City. Principal adoptado: **ECI02_PI02_MAIN, N67, T753346, COMMITTED**. Padre físico: ECI02_PI01_MAIN T735843. Universe v27 y Thinking 4.5.0 oficiales permanecen congelados. Manual DCS11-MM-001, edición interna 1.29, mismo nombre operativo 1_21.

## Resultado y decisión

Se incorporó una mejora local real: un soporte adquirido por experiencia en la misma vida cambia su respuesta ante una advertencia; la salida gobierna un dispositivo fijo, conserva la admisión de una comparación posterior y permite una actuación útil. La secuencia integra historia Native, acceso FI, acción externa, consecuencia y modificación posterior del selector. No acredita iniciativa temporal aprendida ni una política general competente. El control sin valencia obtuvo más productos que MAIN: ese negativo acompaña la incorporación.

MAIN adquirió y utilizó los mecanismos sucesivamente, conservó doce usos anteriores y utilizó la nueva función después de guardar, cerrar y reabrir. Se migró su conjunto operativo completo, se comprobó la apertura técnica desde el producto a cero ticks y se adoptó mediante Store.promote COMMITTED. No se copiaron memorias de controles ni se eligió la rama de7productos para atribuírsela a MAIN.

## Qué se reutilizó y qué se leyó

PI01 ya había registrado lectura técnica completa de los dos manuales oficiales Thinking y cobertura amplia de CORE, Ingenierías, Procesos, CPC, Pensamiento y basal. PI02 reutilizó esa cobertura; no la cuenta como nueva lectura integral. Reabrió los contratos instalados, código PI01 y partes pertinentes del motor como texto, informes y primarios necesarios para el diseño. La síntesis dirigida identifica17fuentes y13afirmaciones con rutas, hashes y localizadores en `FUENTES/CONTRASTES/AFIRMACIONES_Y_FUENTES.json` y las notas de mecanismo. Los originales Thinking grandes permanecen locales, identificados por sus hashes; este expediente no incluye sus copias completas.

Las correcciones científicas que importan son concretas. ECI02C documenta densificación y rechazos, no dolor ni asfixia acreditados. En el R04 histórico, el portador temprano apareció tanto con consulta como sin ella, mientras otros campos sí cambiaron; no se confunde con el cero FI128 en q+4. CORE09 no es CPC9. CORE08/10/17 incluyen protección, redundancia y reparación preparadas con dominios propios; no autorizan copiar recuerdos al principal. En Ingeniería06 la diferencia de historias ya existía en HOST_STOP+0, y los cierres OBP no atribuyeron todos sus cambios al retorno. Actuar en Pendulum fue interacción real, no una política motora competente. No se repitieron esas campañas.

La lectura se distingue de los recálculos y de las nuevas ejecuciones. La clausura estática de los13archivos incorporados inspeccionó57módulos:44dependencias se reutilizan sin cambio. No equivale a ejecutar todas las ramas históricas del producto.

## Organización y frontera

Existe un solo Runtime N67 por vida. O es el mecanismo retornante de selección heredado; H es un soporte de advertencia adquirido en esta trayectoria; FI128 es el comparador heredado. Son componentes funcionales de una organización, no tres individuos autónomos. El entorno externo contiene una válvula, dos cargas por oportunidad, disponibilidad periférica y archivos de recurso/control. Compartir Runtime no convierte todo el universo en mente, y la memoria no se limita por definición a los puertos de lectura.

El anfitrión prepara geometría e interfaces, sensores, transductores, oportunidades, fase, capacidad de trabajo y ley de consecuencias. La conversión FI usa operandos públicos independientes y una escala fija; no calcula el signo conveniente para suministrárselo a DEE. La salida física determina el movimiento de una unidad; sólo después el entorno evalúa el efecto y emite una valencia genérica. Ningún diario, target, nombre de control, semilla, futuro o modelo externo decide por el participante. El puente no tiene red, shell libre ni acceso arbitrario a archivos.

El dispositivo y sus reglas son preparación P0/R0. La respuesta que cambia por su estado adquirido se atribuye localmente a P1/R1. No se rebautiza el decoder fijo como una estrategia P2/R2. No se atribuye conciencia, dolor subjetivo ni superioridad general.

## A: inicio menos asistido y selección por consecuencias

Dos copias completas compararon registro pasivo O con ausencia de registro,134ticks. Coincidieron campos físicos, agenda/recibos y metadatos causales no administrativos. En la calibración, el retorno A observado sin sensor se transformó a B después de una valencia legal; el brazo sin ella mantuvo A. No se reutilizó el normalizador que hubiera requerido el sensor omitido. Los recibos reales y las observaciones fijadas sostienen esa transformación; no hubo edición RAW/clock.

Después se congeló R02B. Cada uno de cuatro brazos avanzó4500ticks y completó12trabajos. MAIN obtuvo10/12productos, sin valencia7/12, sham7/12 y actuación anulada0/12. Todos formaron12respuestas. MAIN tuvo1100solicitudes Native,1100aplicadas,0rechazos; las consultas MA/FI siguen siendo materiales. Hubo67retornos detectados por brazo,12trabajos admitidos,48eventos durante capacidad ocupada y7tras agotarse el banco. Esos límites de capacidad son del aparato, no abstenciones cognitivas.

Se retiraron SENSOR y NORMALIZER **de la selección O por oportunidad**, no todos los sensores/normalizadores de PI02. La traducción A→MA/alfa y B→FI128 siguió externa y fija en A. La referencia mantener-tras-acierto/cambiar-tras-fallo obtuvo el mismo10/12 y la misma secuencia que MAIN. El sham solicitó5valencias y sólo admitió1: sus4rechazos impiden llamarlo un control global de igual dosis. El primer contacto admitido permite una comparación acotada; no se oculta el resto.

La ganancia es ejecución de trabajos desde eventos propios y selección modificada por consecuencias bajo conexiones fijas. La recurrencia y su período preparado no prueban que aprendiera cuándo iniciar ni que explore espontáneamente.

## B: interferencia, instrumento y recuperación de uso

La descomposición FI asíncrona conservó estados globales, marcos y respuestas frente al acceso síncrono en tres casos, incluido cero material en q+4 y NULL en q+6. Su verificación es instrumental, no aprendizaje.

Una solicitud legal de carga7 simultánea en la fuente raw0 produjo competencia de admisión: también fue rechazada, junto con otras entradas. El mecanismo no fue un portador7admitido que destruyera contenido. En las parejas6/6,12/4y3/11el brazo ACTIVE dio−1enlos tres casos; sólo el último era funcionalmente correcto. Rechazo de entrada no implica error universal.

SYNC, ASYNC y guarda preparada dieron0,+1,−1. SHAM2también dio0,+1,−1con531/531entradas aplicadas y0rechazos; su estado600001difiere del perturbador de estado1, por lo que no representa igualdad completa de dosis/geometría. El primer SHAM falló por el contrato inmutable antes de avanzar ticks, pero dejó176eventos pendientes. Su futuro se preservó y se impidió reintentar como si nada hubiera ocurrido: cero nuevos ticks no significa igualdad causal completa.

MAIN vivió la interferencia en12/4→−1y luego la retirada→+1; una consulta posterior6/6produjo0. No se restauró ni reenseñó. Se recuperó el uso del comparador, no se demostró recuperar información previamente borrada. Esa retirada fue del experimentador, no regulación adquirida.

## C: de huella adquirida a actuación anticipatoria local

En desarrollo se compararon cinco historias del mismo prefijo. W/Uemparejados formaron un soporte Y18enH. Ante el primer estímulo común W/G, sólo la historia emparejada produjo la firma CLOSE. Desfase y sólo-reporte admitieron la nueva señal sin producir esa firma. La condición sólo-advertencia rechazó su primera W; ese negativo no tiene la misma admisión. Gde carga0es material y las pruebas también cambian los controles: los usos posteriores no son réplicas independientes ni lecturas inocuas.

Estas ramas de desarrollo no se copiaron a MAIN. MAIN adquirió su propia asociación durante el primer rechazo real del marco FI de R04. El montaje emitió Wde calentamiento y un reporte Ugenérico del recibo rechazado. No proporcionó la actuación correcta ni sembró el producto Y. Hfue leído con una firma y posición congeladas, en todos los ticks; no se buscaron retrospectivamente puertos ni ventanas favorables.

Se comparó además la lectura O/H frente a ausencia de lectura durante134ticks por brazo, con igual segmentación de un tick. Coincidieron íntegramente los estados Native salvo metadatos administrativos declarados. El archivo OH derivado conserva sin pérdida el prefijo causal común y ambos sufijos; el recálculo reconstruye todos sus bytes. No acredita igualdad SQLite ni pasividad universal.

## Prueba conjunta R04

El desarrollo fue una rama aparte,4600ticks y seis oportunidades:2productos. La única advertencia de uso prevista cayó en una oportunidad Bsin solicitud FI y por ello no se presentó W. Sus cero CLOSE no se presentaron como una prueba negativa de incapacidad. El código, lectores y doce casos reservados se congelaron antes de ejecutarse; no se ajustaron a esos resultados.

Los seis brazos reservados parten del mismo prefijo completo T740937y avanzan9200ticks. Cada oportunidad propone cargas públicas nuevas; no es un robot ni un controlador que equilibre repetidamente un mismo objeto. La válvula y sus recursos sí persisten entre oportunidades y afectan las entradas posteriores. Una salida FI mueve una unidad y su resultado queda en el estado del entorno; una acción útil libera un archivo64Bverificable. El cero material válido de una carga ya equilibrada puede ser útil; NULL nunca se reemplaza por una acción inteligente.

{table}

MAIN tiene9marcosFI:6útiles,3perjudiciales,0NULL. Uno de los6productos corresponde a cero material que conserva el equilibrio; los otros5a movimientos útiles. Las otras3oportunidades fueron actuaciones Bde dispositivo, con coste inmediato. Los384bytesde productos y512bytesde paquetes gastados son recursos distintos del entorno, no una moneda común ni energía. No se ocultan los costes para presentar6como una ganancia económica neta.

### Enlace causal decisivo

En la oportunidad5, MAIN y el control WARNING_CUT tuvieron iguales solicitudes W/G, mismos176eventos FI registrados y la misma firma H/clock. En el control, la orden formada fue cortada antes del actuador. El trabajo inmediato de5fue útil en ambos porque una guarda anterior seguía cerrada.

Antes de la entrada6caducó la protección del Bprevio. Las CLOSE5y6de MAIN renovaron/cerraron la válvula antes de raw0. MAIN admitió raw0y produjo+1útil para19/8; el corte y el desfase dejaron la entrada en conflicto y produjeron−1perjudicial. Se acredita la contribución del enlace y de esa secuencia; no se afirma que CLOSE5aislada fuera necesaria, ya que CLOSE6también podía intervenir.

El ciclo observable es: experiencia de rechazo→soporte Hdependiente de historia→respuesta a aviso→dispositivo externo→cambio real de admisión Native→comparación→acción sobre cargas→consecuencia→valencia→cambio posterior de O. La microdinámica no se reconstruyó exhaustivamente en todo el dominio. Los logs abarcan O/H, hitos FI, fuentes y recibos decisivos; no contienen todas las colisiones ni todo el RAWpor tick.

### Fallos que limitan la interpretación

Las cinco CLOSEde MAIN encontraron guard_before=true: buena parte de su efecto fue mantener el plazo, no crear por sí mismas una protección inicial. Hubo una falsa alarma con gasto de paquete. La conexión invertida hizo que CLOSEabriera la válvula y causara un fallo en18/5. No se aprendió a revisar esa estrategia ni a abstenerse por utilidad actual.

El control sin valencia obtuvo7/12frente6/12MAIN. La ley de recompensa penaliza Binmediatamente aunque proteja una comparación posterior; no asigna crédito diferido a ese efecto. La omisión elimina todas las valencias y no aísla únicamenteB, por lo que tampoco prueba que otra regla funcionaría sin ensayarla. La política de selección actual no domina una alternativa simple.

Se usaron avisos con adelantos61/128/195enuna familia de fase módulo67, falsas alarmas, ausencia de señal y cambio de conexión. Es transferencia local a nuevas cargas y plazos compatibles, no aprendizaje general del tiempo ni invariancia de fase. La válvula controla una línea periférica ya preparada; no aprendió a separar señales útiles y ruido dentro de una entrada mixta, ni cuándo reabrirla. Permanecen entradas FI útiles. Caducar por TTLno es una regulación aprendida de apertura.

## Conservación y continuidad de una sola vida

El puente R04se desactivó externamente a cero ticks después de la reserva. Native siguió evolucionando durante el panel. MAIN conservó12/12primeras respuestas hastaT751546: luma+,nara−,clasifica−,suma+,memoriaalfa−,comparación+,−,0,6+7→13,resultado13−5→8yusosposterioresdealfa/luma. Se aplicaron929/929entradas únicas sin rechazo. El operador eligió la secuencia y transportó el resultado13; no se atribuye ese orden a un plan nativo ni se afirma aprendizaje de un algoritmo aritmético.

Otro proceso reabrió ese estado completo con N/T/RAW/clocks iniciales idénticos. La API operativa añadió dos oportunidades externas acotadas,13/5y7/16,conavisos128/195. Sólo suministró recursos/condiciones públicas; no reintrodujo U,palabra,referencia correcta,snapshot ni lectura favorable. Durante1800ticks, las salidas+1/−1hicieron dos trabajos útiles y materializaron2recursos. El corte final esT753346con8productosR04,14oportunidades consumidas y6de16paquetesdecontrol disponibles.

El panel12/12pertenece al corteT751546. Después se comprobó la función nueva2/2enel corte final; no se anuncia otro panel completo allí. Las consultas son experiencias materiales y sus efectos forman parte de esa historia, no se rebobinan.

## Incorporación efectivamente realizada

Se desplegaron13archivos de Cognitive y se reutilizaron44dependencias sin cambio. Se importaron3365miembros/158174090bytesdelparcompleto, conservando la misma identidad PI02, cola, recibos, outbox, artefactos y progreso. Los IDs ya ejecutados se conciliaron; no se reenviaron operaciones inciertas. La reapertura técnica desde el producto se mantuvo pausada: cargar, guardar y cerrar a cero ticks con igualdad física/causal y progreso R04igual. Después la promoción quedóCOMMITTED, con ACTIVO,PROYECTO,selecciónpersonalyaplicación sincronizados.

La interfaz habitat-trabajo evita que un banco agotado obligue a reconstruir la vida: añade una oportunidad pública y su suministro64Bsin avanzar Native, sin reiniciar contadores y sin escribir memoria cognitiva. La extensión OP1conserva por ASTtodas las funciones evaluadas de R04; sus dos ofertas se utilizaron realmente en la reapertura. Los paquetes de control siguen siendo finitos, sin reposición oculta. El código de la reserva y el OP1se preservan por separado.

El único principal operativo queda en el producto. El store de campaña es procedencia congelada de la migración, no otra vida principal a continuar. PI01y los futuros adversos permanecen intactos. El Manual completo1.29yCompendio se publicaron después de renderizar y revisar los cambios; las ediciones anteriores se preservan. No se renombró el archivo1_21ni se reescribieron los manuales Thinking. No hubo limpieza ni nueva eliminación.

La aplicación gráfica fue revisada estáticamente: su lanzador abre la vida seleccionada mediante GenesisNativeWorld/backendmente_unificada. No se abrió GUI. Las operaciones PI02están disponibles por el mismo gestor/QueueDBliteral; no se inventaron botones en su gramática visible.

## Fuentes, instrumentos, presupuesto y reproducción

Las solicitudes canónicas de campaña fueron100yavanzaron93340ticks entre todas las ramas:804decalibración/observadorR01,19600deAincluidodesarrollo,3564deFI,6095deadvertenciaprototipo,4600deDEVhabitat,268delcontrolOH,55200dereserva,1409depanel y1800decontinuación. Ticks y clones no son conceptos ni aprendizajes independientes. La migración/promoción y comprobación técnica posterior añadieron0ticks. El presupuesto fijado100000/6horasno se reinició.

Los procesos propios se supervisaron bajo un límite externo512MiB. Esa RAMes del anfitrión, no memoria cognitiva ni recurso metabólico de DEE. Fueron propietarios secuenciales y pruebas de relevo; no un ensayo de80–90mincontinuos. No se acreditó ni descartó una fuga general de Windows oMac. No hubo un reinicio preventivo45mincontado como supervivencia. Un fallo de proceso se distinguiría del paisaje; no se observó ninguno en los100materiales salvo errores de preparación explícitamente preservados sin avance.

`RECALCULO/RECALCULO_TODO.py` ejecuta14recálculosdocumentales portátiles: A,B,C,siete trayectoriasR04,OH,dos primerosavisos y E_FINAL. Reconstruye evidencia exportada, comprueba bytes/hashes/recibos/resultados y no importaDEE. La verificación final se ejecuta otra vez desde extracción limpia, no desde rutas originales. F_INCORPORACIONes evidencia estática de implementación y selección; el manifiesto la cubre, no se llama reproducción Native.

Una reproducción Native distinta necesita los estados completos locales y el motor oficial; use el prefijo completoPAR_POST_B_MAIN, clonar_prefijo.pyy un IDdiagnóstico nuevo para ejecutar el protocolo reservado. Los protocolos no creanT0. No ejecute un runner sobre IDsya utilizados ni envíe de nuevo una operación ambigua. El ZIPno es un respaldo operativo completo.

## Límites localizados después del avance

Se recomienda continuar desde el principal adoptado investigando crédito diferido y elección contextual entre trabajar/proteger, comparando un enlace físico candidato con control de retorno desacoplado; una prueba debe preservar el panel y no suministrar la acción conveniente. Otra pregunta concreta es generalizar la advertencia fuera de fase sin mover el lector retrospectivamente. La tercera es si una historia puede modificar cuándo acceder, frente a la misma recurrencia fija. Son preguntas pendientes de mecanismo, no capacidades incorporadas ni excusa para omitir el avance real obtenido.

Los negativos no establecen una imposibilidad universal de v27. Los positivos tampoco acreditan una mente general. El resultado es una continuidad real con una asociación adquirida que interviene causalmente en una función protegida y utilizable, con sus costes, asistencia y fallos verificables.
'''
text(E/'01_INFORME_CIENTIFICO_PI02.md',readable(report))
text(E/'00_LEER_PRIMERO.txt',readable(f'''PI02 — corte 2026-11-08, America/Mexico_City
Principal: ECI02_PI02_MAIN / N67 / T753346 / COMMITTED.
Padre físico: ECI02_PI01_MAIN T735843. Una genealogía, ningún recuerdo fusionado.
Base: Universev27 y Thinking4.5.0 congelados. Manual completo DCS11-MM-0011.29.

Resultado: advertencia adquirida y dispositivo fijo sostienen una comparación útil antes de una entrada posterior. MAIN6/12; corte/desfase/sin adquisición4/12; actuadoranulado0/12. Sin valencia7/12: la política no es óptima. Falsa alarma e inversión perjudicial incluidas.
Conservación:12/12 y929/929entradas hastaT751546. Tras reapertura:2/2 trabajos sinU, finalT753346. No otro panel12/12en ese último corte.
Uso disponible: mismo gestor, backendmente_unificada, --eci01, vidaexistente, unpropietario. Estado completo local en MAPAS/CONTINUIDAD_PI02.json. No usar --nueva ni restaurar una semilla sobre un futuro posterior.

Orden: informe → Manualcap45/puntoinicial → MAPAS → EVIDENCIA/D_R04yE_FINAL → F_INCORPORACION. Los índices indican archivos comprimidos sin pérdida y códigos exactos. A/B/C conservan su ámbito propio.
Recálculo: python -I -B -X utf8 RECALCULO/RECALCULO_TODO.py --root . --out-dir NUEVA_CARPETA_VACIA
Es un recálculo documental, no otra ejecución del motor. La reproducción Native requiere los originales operativos locales y motor oficial; este ZIPdeanálisis no los sustituye.
El Manual viaja íntegro y literal. Dos manuales Thinking, estadosoperativos grandes y telemetría profunda permanecen locales, identificados en omisiones. Ninguna publicación externa, video, Mac o limpieza en esta campaña.
'''))
sources=E/'FUENTES';sources.mkdir(exist_ok=True)
for folder in('CONTRASTES','MECANISMOS'):
    for src in(P/'lecturas'/folder).glob('*'):
        if src.is_file()and src.suffix in('.json','.md')and src.stat().st_size<2000000:
            dst=sources/folder/src.name;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,dst)
for name in('FUENTES_Y_COBERTURA_MECANISMO.json','AFIRMACIONES_Y_FUENTES.json'):
    found=list((P/'lecturas').glob('**/'+name))
    if not found:raise ValueError('Directed source coverage missing:'+name)
# Actual current scientific register: a completed phase, not the old startup0.
regpath=P/'REGISTRO_CAMPANA.json';reg=read(regpath)
reg.setdefault('historical_prefix_before_final_closure',{'phase':reg.get('phase'),'new_native_ticks_so_far':reg.get('new_native_ticks_so_far')})
reg.update(phase='SCIENTIFIC_AND_OPERATIONAL_CLOSED_PACKAGING_VERIFICATION_PENDING',new_native_ticks_so_far=93340,principal_final={'life_id':card['life_id'],'N':67,'tick':753346,'selection':'COMMITTED'},manual_internal_edition='1.29',closure={'continuity':str(P/'CONTINUIDAD_PI02.json'),'adoption':str(P/'control/ADOPCION_PRODUCTO_PI02.json'),'actual_product0tick_load_save_close':str(P/'control/REAPERTURA_PRODUCTO_PI02.json'),'all_originals_and_controls_preserved':True,'no_cleanup_performed':True})
write(regpath,reg)
print(json.dumps({'report':str(E/'01_INFORME_CIENTIFICO_PI02.md'),'principal':card['life_id'],'tick':753346,'manual':desc(manual),'new_Native_ticks_by_this_script':0},ensure_ascii=False))
