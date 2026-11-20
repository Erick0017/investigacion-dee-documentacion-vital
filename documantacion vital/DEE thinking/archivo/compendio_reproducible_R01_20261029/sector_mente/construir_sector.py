"""Select historical protocols without executing Native or modifying a source."""
from pathlib import Path
import json,gzip,hashlib,shutil,sys,ast
ROOT=Path(r"D:\GENESIS AI\GENESIS 5.0\simulador de universo ab-initio\dee_libreria\VERSION_27\tests\documantacion vital\DEE thinking")
WORK=Path(__file__).resolve().parent
STAGE=WORK/'stage';OLD=ROOT/'archivo/DEE Cognitive System 1.1'
LAB=OLD/'laboratorio/campanas';EVID=OLD/'evidencia/campanas'
S=ROOT/'DEE Cognitive 2.0/sistema'
sources=[]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):
    p=Path(p);return json.loads(gzip.decompress(p.read_bytes())if p.suffix=='.gz'else p.read_bytes())
def copy(p,rel,compress=False):
    p=Path(p);dst=STAGE/rel;dst.parent.mkdir(parents=True,exist_ok=True)
    data=p.read_bytes()
    if not dst.exists()or(gzip.decompress(dst.read_bytes())if compress else dst.read_bytes())!=data:dst.write_bytes(gzip.compress(data,mtime=0)if compress else data)
    item={'original':str(p),'relative':str(dst.relative_to(STAGE)).replace('\\','/'),'sha256':sha(p),'bytes':len(data)}
    if compress:item['encoding']='gzip original bytes';item['stored_sha256']=sha(dst)
    sources.append(item);return str(dst.relative_to(STAGE)).replace('\\','/')
def snapshot_file(record):
    filename=Path(record['snapshot']).name;expected=record['snapshot_sha256']
    dirs=[S/'estado/checkpoints',OLD/'sistema/estado/checkpoints',ROOT/'casos practicos/trabajo_codex/DEE Cognitive System 1.1/sistema/estado/checkpoints']
    for folder in dirs:
        candidate=folder/filename
        if candidate.is_file()and sha(candidate)==expected:return candidate
    # Some historical names were shortened on export. Match only known checkpoint roots.
    for folder in dirs:
        if folder.exists():
            for candidate in folder.glob('*'+expected[:12]+'*'):
                if candidate.is_file()and sha(candidate)==expected:return candidate
    raise FileNotFoundError('Complete parent '+filename+' SHA '+expected)
def parent_from(camp,name,life=None):
    row=read(EVID/camp/name)
    rec=row.get('before')or row.get('previous_checkpoint_record')
    if not rec:raise ValueError('No exact before record in '+name)
    file=snapshot_file(rec);rel='recursos/estados/'+sha(file)+'.deetsnap.gz'
    if not(STAGE/rel).exists():copy(file,rel)
    return {'life':life or rec['life_id'],'profile':rec['profile'],'snapshot':rel,'sha256':sha(file),'tick':rec['physical']['tick'],'physical':rec['physical']}
def parent_for_operation(camp,name,alias):
    row=read(EVID/camp/name);wrap=row if'INSTRUMENTO'in row else row.get('result',row.get('data',{}))
    info=wrap.get('INSTRUMENTO',{})
    if not info:raise ValueError('No original Store receipt in '+name)
    life=info['life_id'];after=info['snapshot_sha256'];found=None
    for base in [OLD/'sistema/estado/vidas',S/'estado/vidas',ROOT/'casos practicos/trabajo_codex/DEE Cognitive System 1.1/sistema/estado/vidas']:
        journal=base/life/'HISTORIA.jsonl'
        if journal.exists():
            with journal.open(encoding='utf8')as f:
                for line in f:
                    x=json.loads(line)
                    if x.get('snapshot_sha256')==after:found=x;break
        if found:break
    if not found:raise FileNotFoundError('Exact journal link before '+name+' afterSHA '+after)
    physical=found['operation'].get('before')
    if not physical:raise ValueError('No complete before physical fingerprint for '+name)
    digest=found['previous_snapshot_sha256'];file=None
    for folder in [OLD/'sistema/estado/checkpoints',S/'estado/checkpoints',ROOT/'casos practicos/trabajo_codex/DEE Cognitive System 1.1/sistema/estado/checkpoints']:
        for p in folder.glob(life+'.T'+str(physical['tick'])+'.*.deetsnap.gz'):
            if sha(p)==digest:file=p;break
        if file:break
    if not file:raise FileNotFoundError('Exact before snapshot '+life+'T'+str(physical['tick'])+' SHA '+digest)
    rel='recursos/estados/'+digest+'.deetsnap.gz'
    if not(STAGE/rel).exists():copy(file,rel)
    return {'life':alias,'profile':info['profile'],'snapshot':rel,'sha256':digest,'tick':physical['tick'],'physical':physical,'historical_life':life,'original_operation':info['operation']}
def args_of(row):
    v=row['argv'];i=next(i for i,x in enumerate(v)if x.endswith('gestionar.py'));v=v[i+1:]
    if v and v[0]=='--':v=v[1:]
    command=v[0];opts={};i=1
    while i<len(v):
        key=v[i]
        if '='in key:key,value=key.split('=',1);opts[key]=value;i+=1
        elif i+1<len(v)and not v[i+1].startswith('--'):opts[key]=v[i+1];i+=2
        else:opts[key]=True;i+=1
    return command,opts
def api_spec(row):
    cmd,o=args_of(row);kw={};module=None;fn=None
    if cmd=='cf01-tarea':
        module='cierre_funcional_cf01';fn='task';kw={'opportunities':list(map(int,str(o['--oportunidades']).split(','))),'steps':int(o.get('--pasos',1)),'reset':bool(o.get('--reiniciar-entorno',False)),'actuator':o.get('--actuador','closed'),'feedback':o.get('--retorno','intact')}
    elif cmd in('cf01-servicio','ente-servicio'):
        module='cierre_funcional_cf01'if cmd=='cf01-servicio'else'ente_operativo_01';fn='classify';kw={'measurements':[list(map(int,p.split(':')))for p in o['--mediciones'].split(',')],'reference':int(o['--referencia-entorno'])if'--referencia-entorno'in o else None,'actuator':o.get('--actuador','closed'),'feedback':o.get('--retorno','intact'if cmd=='cf01-servicio'else'real'),'reset':bool(o.get('--reiniciar-entorno',False))}
        if cmd=='ente-servicio':kw.update(trace=bool(o.get('--detalle',False)),offset=int(o.get('--desfase',0)),cut=o.get('--corte','none'))
    elif cmd=='ente-tarea':
        module='ente_operativo_01';fn='task';kw={'jobs':[list(map(int,p.split(':')))for p in o['--trabajos'].split(',')],'steps':int(o.get('--pasos',1)),'reference':int(o['--referencia-entorno'])if'--referencia-entorno'in o else None,'reset':bool(o.get('--reiniciar-entorno',False)),'actuator':o.get('--actuador','closed'),'feedback':o.get('--retorno','real')}
    elif cmd in('evolucion-servicio','evolucion-sensorial'):
        module='ente_evolucion_02'if cmd=='evolucion-servicio'else'ente_evolucion_02_sensorial';fn='classify';kw={'observations':json.loads(o['--observaciones']),'domain':o.get('--dominio','puertas'),'reference':int(o['--referencia-entorno'])if'--referencia-entorno'in o else None,'reset':bool(o.get('--reiniciar-entorno',False)),'actuator':o.get('--actuador','closed'),'feedback':o.get('--retorno','real'),'trace':bool(o.get('--detalle',False)),'directory':'{work}'}
        if cmd=='evolucion-servicio':kw.update(visible_phase=bool(o.get('--fase-visible',False)),zero_phase=bool(o.get('--fase-cero',False)))
    elif cmd in('mente-sesion','mente2-sesion','unificada-sesion'):
        module={'mente-sesion':'mente_acumulativa_01','mente2-sesion':'mente_acumulativa_r02','unificada-sesion':'mente_unificada_01'}[cmd];fn='session';kw={'situations':json.loads(o['--situaciones']),'directory':'{work}','actuator':o.get('--actuador','closed'),'feedback':o.get('--retorno','real'),'detailed':bool(o.get('--detalle',False))}
    elif cmd=='mente2-extender':module='mente_acumulativa_r02';fn='extend';kw={'context':o.get('--contexto','epsilon')}
    else:raise ValueError('Unadapted original command '+cmd)
    return {'module':'capacidades.'+module,'function':fn,'kwargs':kw,'original_command':cmd}

def api_cases(m,camp,names,groups=None):
    """Recover exact pre-operation worlds and the historical scientific function."""
    m.setdefault('api_program',[])
    names=list(names)
    grouped={name:group for group in(groups or[])for name in group}
    group_parents={}
    for index,name in enumerate(names):
        row=read(EVID/camp/name);spec=api_spec(row);group=grouped.get(name,[name]);key=tuple(group)
        if key not in group_parents:
            alias=m['id']+'_P'+str(index)
            par=parent_for_operation(camp,name,alias);m['parents'].append(par);group_parents[key]=alias
        alias=group_parents[key];rel=primary(camp,name)
        if rel not in m['references']:m['references'].append(rel)
        overlay=[];revision=row.get('code_revision_sha256')
        rev=EVID/camp/'codigo_ejecutado'/str(revision)/'sistema/capacidades'
        if rev.is_dir():
            for p in rev.glob('*.py'):
                common=S/'capacidades'/p.name
                if not common.is_file()or sha(p)!=sha(common):
                    overlay.append({'relative':copy(p,'recursos/revisiones/'+str(revision)+'/capacidades/'+p.name),'destination':'capacidades/'+p.name})
        m['api_program'].append({'reference':rel,'parent':alias,'case':Path(name).name.removesuffix('.gz').removesuffix('.json'),**spec,'overlay':overlay})
    m['mode']='original_manager_function_with_complete_historical_parent'
def script(camp,name):return copy(LAB/camp/name,'laboratorio/campanas/'+camp+'/'+name)
def primary(camp,name):
    p=EVID/camp/name
    rel='referencias/'+camp+'/'+name+(''if p.suffix=='.gz'else'.gz')
    return copy(p,rel,compress=p.suffix!='.gz')
def glob_primary(camp,patterns):
    items=[]
    for pat in patterns:
        items.extend(sorted((EVID/camp).glob(pat)))
    return [primary(camp,p.relative_to(EVID/camp).as_posix())for p in dict.fromkeys(items)if p.is_file()]
def add(mid,name,function,campaigns,families,entries,parents,patterns,variants,timeout=1800,mode='native_protocol',notes=None):
    per=[]
    for camp,pats in patterns.items():per.extend(glob_primary(camp,pats))
    code=[]
    for camp,name0 in entries:code.append(script(camp,name0))
    m={'id':mid,'name':name,'function':function,'campaigns':campaigns,'word_families':families,
       'variants':variants,'parents':parents,'entries':code,'references':per,'mode':mode,'timeout_seconds':timeout,
       'history_status':'POSITIVE_HISTORICAL_WITH_ESSENTIAL_NEGATIVE_CONTROLS','integrity_status':'SOURCE_BYTES_AND_PARENT_SNAPSHOT_HASHES_RECOVERED',
       'current_validation':'NOT_EXECUTED_YET','pending':[],'assistance':'Prepared anatomy, fixed codec/reader and environmental protocol; physical contents and consequences arise in official v27.',
       'limitations':notes or[]}
    mechanisms.append(m);return m
mechanisms=[]
MI='MENTE_DEE_INTEGRAL_MI01';D='MI02_ARQUITECTURA_DISTRIBUIDA';MA='MENTE_ACUMULATIVA_R02'
# Exact helpers are copied once, shared by all selected protocols.
for camp,name in [(MI,'comun.py'),(D,'comun_mi02.py')]:script(camp,name)

add('M201','Composición de ruta y contenido adquirido en E1 tardío','Dos experiencias de selección de ruta y un contenido opaco enseñado por separado confluyen y producen un uso receptor en la bifurcación tardía de E1.',[MI],['Composición','Aprendizaje','Acceso'],[(MI,'composicion_local.py')],
    [parent_from(MI,'MI01_COMPOSICION_30.json','E1_MI01_MAIN')],
    {MI:['MI01_COMPOSICION_3[0-4].json','COMPOSICION_PROTOCOLO_030.json']},['route history1','opposite route history','swapped content','omitted feedback','no content'],notes=['Reproduce el prefijo nativo exacto hasta DESPUES_USO. El paso externo posterior queda fuera de este mecanismo y no se repite. Preparación AA01 e iniciativa del currículo son externas.'])
mechanisms[-1]['prefix_only_external']=True
mechanisms[-1]['omit_comparison_keys']=['external']
for i in range(30,35):
    p=EVID/MI/('MI01_COMPOSICION_'+str(i)+'.DESPUES_USO.deetsnap.gz')
    if p.exists():copy(p,'recursos/estados/'+sha(p)+'.deetsnap.gz')

add('M202','Solicitud material y respuesta privada MI01','An acquired directional selector physically initiates a request; B private input produces content-dependent return. The query is not scheduled after observing its answer.',[MI],['Consulta','Comunicación','Acceso'],[(MI,'consulta_material_completa.py')],
    [parent_from(MI,'MI01_CONSULTA_110.json','MI01_SELECTOR_PREFIJO_11'),parent_from(MI,'MI01_CONSULTA_112.json','MI01_SELECTOR_PREFIJO_10')],
    {MI:['MI01_CONSULTA_11[0-5].json','CONSULTA_COMPLETA_PROTOCOLO_110.json']},['private20','private52','opposite learned selector','formed-query cut','same-dose sham','no command'],notes=['Starts from complete learned historical prefixes; this command reproduces request and use, not a fresh T0 acquisition of the selector. The selector acquisition code remains in the common capability.','P1 bounded initiation, not general missing-information detection or learned query utility.'])
add('M203','La respuesta social modifica una decisión posterior','Actual private-dependent reply reaches the same selector and changes a later native XY action. Generic P0 protection and route setup are fixed.',[MI],['Comunicación','Aprendizaje por consecuencias'],[(MI,'proteccion_retorno.py')],
    [parent_from(MI,'MI01_RETORNO_PROTEGIDO_210.json','MI01_BASE_HISTORICA_T23453')],
    {MI:['MI01_RETORNO_PROTEGIDO_21[0-5].json','PROTECCION_RETORNO_PROTOCOLO_210.json']},['two private contents','resource-only-path guard sham','formed reply cut','formed reply sham'])
add('M204','Un producto de fallo inicia una consulta','An actual failed native action contributes to a later information request through prepared physical paths; neither Python failure detection nor a correct reply is supplied.',[MI],['Consecuencias','Consulta','Regulación'],[(MI,'fallo_consulta_compartido.py')],
    [parent_from(MI,'MI01_COMPARTIDO_270.json','MI01_BASE_HISTORICA_T23453')],
    {MI:['MI01_COMPARTIDO_27[0-4].json','FALLO_COMPARTIDO_PROTOCOLO_R4_270.json']},['intact','omit failure return','postformed failure cut','sham failure cut','reply cut'],notes=['Local P1 chain is positive; second B access and general recovery remain failed/conditioned in the original trajectory.'])
add('M205','Reutilización de contenido propio sin reenseñanza','A generic interaction diverts a physically acquired positive return code for later use without a new B sample or teacher.',[MI],['Recuperación','Memoria distribuida'],[(MI,'recuerdo_para_continuar.py')],
    [parent_from(MI,'MI01_REUSO_280.json','MI01_PROTECCION_170'),parent_from(MI,'MI01_REUSO_281.json','MI01_PROTECCION_171')],
    {MI:['MI01_REUSO_28[0-3].json','REUSO_CONTENIDO_PROTOCOLO_280.json']},['positive history','negative history failed','formed content cut','sham'],notes=['The negative history is not generally recovered. Matter is diverted, not cloned; operator initiates the generic resource.'])
add('M206','Composición adquirida de contacto y orden','Separately experienced contact and event order participate in one native conjunction and a downstream consequence.',[MI],['Composición','Orden','Contacto'],[(MI,'relaciones_compuestas.py')],
    [parent_from(MI,'MI01_COMPUESTA_220.json','E1_MI01_MAIN')],
    {MI:['MI01_COMPUESTA_22[0-3].json','RELACIONES_COMPUESTAS_PROTOCOLO_220.json']},['contact plus AB','missing contact','missing B event','reversed BA'],notes=['Consumptive one-shot composition; not a learned grammar.'])
add('M207','Selección local revisada por consecuencias R8','Native action/failure returns change acquired fields and later materially useful contacts under reversed availability.',[D],['Aprendizaje por consecuencias','Acción útil','Regulación'],[(D,'retorno_exterior_11.py'),(D,'acumulacion_consecuencias_13.py')],[],
    {D:['CONTROLADOR_PREPARAR_9[0-2].json','CONTROLADOR_VIVIR_9[0-2].json','ACUMULACION13_9[0-2].json','PROTOCOLO_RETORNO_EXTERIOR_11.json','PROTOCOLO_ACUMULACION_13.json']},['intact','omitted return','selective return cut'],timeout=2400,notes=['6 initial plus18 later opportunities in each original trajectory; repeated opportunities are not independent learners.'])
add('M208','Consulta social con lector reutilizable R9','A locally acquired request activates private B, transfers a context contribution, and later reactivates a reader that became empty without clearing or manual reactivation.',[D],['Comunicación','Acceso','Retención','Composición'],[(D,'lector_social_recurrente_44.py'),(D,'reutilizacion_social_45.py'),(D,'reserva_social_reusable_46.py')],[],
    {D:['SOCIAL44_ACQUIRE_24[0-5].json','SOCIAL44_USE_24[0-5].json','SOCIAL45_REUSE.json','SOCIAL45_WITHOUT_EXTRA_OBSERVER.json','RESERVA46_ACQUIRE_*.json','RESERVA46_USE_*.json','LECTOR_SOCIAL44_FIJADO.json','RESERVA_REUSABLE46_FIJADA.json']},['intact private61/19','opposite private history','no private teaching','no refresh source','query cut','message cut','sham','reserved13/13 and91/29 or29/91','passive observation control'],timeout=3000,notes=['R9 is a new T0 architecture, not MAIN memory transplantation. Private context updating is not arbitrary; not language.'])
add('M209','Referencia conservada con lector efímero','Two native acquired fields outlast a consumable reader, permit repeated common queries and new-content comparisons after a passive delay.',[D],['Memoria','Comparación','Acceso reutilizable'],[(D,'lector_efimero_32.py'),(D,'reserva_efimera_35.py')],[],
    {D:['EFIMERO32_ACQUIRE_21[0-2].json','EFIMERO32_READ_21[0-2].json','EFIMERO35_PASSIVE.json','EFIMERO35_RESERVED210.json','EFIMERO35_NO_PROBE.json','EFIMERO35_LATE_TEACH212.json','EFIMERO35_LATE_USE212.json','EFIMERO35_ACQUIRE213.json','EFIMERO35_RESERVED213.json','PROTOCOLO_EFIMERO_32.json','RESERVA_EFIMERA35_FIJADA.json']},['32/10','10/32','no teaching','845tick passive retention','no probe','late explicit teaching','reserved65/11'],notes=['Prepared baseline bias2 and finite output cone; no unbiased quantity semantics or autonomous query initiation.'])
add('M210','Recuperación de acceso mediante recurso genérico de fase','The same symmetric material input restores useful contact in a previously failed noisy history, with no word, sign or original reference reintroduced.',[D],['Recuperación','Retención','Interferencia'],[(D,'reserva_recuperacion_38.py')],
    [parent_from(D,'RESERVA38_none_RESOURCE.json','MI02_ESTRES37R2_nominal')],
    {D:['RESERVA38_*_RESOURCE.json','RESERVA38_*_USE.json','RESERVA38_FIJADA.json']},['no resource','off-body sham','symmetric generic treatment'],notes=['Assisted P0 procedure selected by operator; not self-selected recovery or general regulation.'])

# Exact original MA02 T0 construction and its supporting implementation.
for name in ['enrutador_comun_sin_giros.py']:script('MENTE_ACUMULATIVA','mecanismo/'+name)
for name in ['sonda_coincidencia_r01.py','restauracion_r02.py','restauracion_r03.py','continuar_r04.py','composicion_r05.py','composicion_r06.py','composicion_reserva_r07.py','composicion_reserva_r08.py','composicion_signos_r10.py']:
    script(MA,'entrada_comun/'+name)
add('M216','Memoria contextual restaurativa y revisión selectiva','One common material input retrieves separately acquired signs, restores circulating supports, and allows a double physical teaching to revise one while using the others.',[MA],['Aprendizaje','Memoria relativa móvil distribuida','Actualización','Acceso repetido'],[(MA,'entrada_comun/restauracion_r03.py'),(MA,'entrada_comun/continuar_r04.py')],[],
    {MA:['entrada_comun/MA02_RESTAURACION_R03B_*.R02.json.gz','entrada_comun/MA02_R04_*.R04.json.gz']},['T0 own signs','opposite acquired signs','no terminator guards','double revision','single revision control','same-dose revision sham','query resources','no query','no markers','no restoration'],timeout=3000,notes=['Four initial opaque context-sign associations, not four policies. Original R04NoRestore2/5 versus resource5/5. Fifth/sixth continuation materials are catalogued separately below.'])
add('M217','Composición de recorridos aprendidos y coste de acceso','Two acquired signed streams return through concrete toroidal paths, combine with a generic resource, and yield concordance; selective cut removes the formed product.',[MA],['Composición','Retornos','Conservación y pérdida de acceso'],[(MA,'entrada_comun/composicion_signos_r10.py')],[],
    {MA:['entrada_comun/MA02_R10_*.R10.json.gz']},['plus plus','minus minus','plus minus','minus plus','formed plus stream cut','sham'],timeout=2400,notes=['Consumes individual alfa/beta accesses; gamma/delta survive. A mixed result or absence is not learned NO. Diagnostic field edit is external on a copy.'])
prefix=EVID/MA/'entrada_comun/MA02_R10_PLUS.history_T2616.deetsnap.gz'
# Parent path is fixed in original R10; recover the exact explicit T2486 argument.
r10=next((LAB/MA/'entrada_comun').glob('composicion_signos_r10.py'))
refs=[read(EVID/MA/p) for p in ['entrada_comun/MA02_R10_PLUS.R10.json.gz'] if (EVID/MA/p).exists()]
if refs:
    rec=refs[0].get('initial',{});file=Path(rec.get('path',''))
    digest=refs[0].get('explicit_parent_sha256',rec.get('sha256'))
    if not file.is_file():
        candidates=[S/'estado/checkpoints'/file.name,OLD/'sistema/estado/checkpoints'/file.name,EVID/MA/'entrada_comun'/file.name]
        file=next((x for x in candidates if x.is_file()and sha(x)==digest),file)
    if file.is_file()and sha(file)==digest:
        rel='recursos/estados/'+digest+'.deetsnap.gz';copy(file,rel)
        mechanisms[-1]['explicit_snapshot']={'relative':rel,'sha256':digest,'tick':2486}
    else:mechanisms[-1]['pending'].append('Exact R10 T2486 parent '+str(file)+' SHA '+str(digest))
else:mechanisms[-1]['pending'].append('R10 positive primary absent')

for name in ['selector_huella_p1_piloto.py','selector_huella_p1_causales.py','selector_huella_p1_corte_critico.py','tap_nativo_no_consumo.py','restauracion_u0_piloto.py']:
    script(MA,'mecanismo_repetible/'+name)
add('M218','Selección nativa de acceso condicionada por una experiencia previa','Un contacto anterior cambia la selección física X/Y ante una consulta común; invertir los contenidos cambia la respuesta y no el banco seleccionado.',[MA],['Acceso selectivo','Historia','Selector P1'],[(MA,'mecanismo_repetible/selector_huella_p1_piloto.py'),(MA,'mecanismo_repetible/selector_huella_p1_causales.py'),(MA,'mecanismo_repetible/selector_huella_p1_corte_critico.py')],[],
    {MA:['mecanismo_repetible/MA02_P1_TOUCH.json.gz','mecanismo_repetible/MA02_P1_NO_TOUCH.json.gz','mecanismo_repetible/MA02_P1_OPPOSITE.json.gz','mecanismo_repetible/MA02_P1_NO_QUERY.json.gz','mecanismo_repetible/MA02_P1_CAUSAL_*.json.gz','mecanismo_repetible/MA02_P1_RESERVE_*.json.gz','mecanismo_repetible/MA02_P1_CRITICAL_*.json.gz']},['touch','no touch','opposite contents','no query','history cut/sham','content cut/sham','timing reserve197','critical time cut/sham/block'],notes=['Primer acceso finito. La segunda consulta no quedó demostrada; no es P2 ni recuperación general. Los cortes de campos son diagnósticos externos identificados.'])
add('M223','Detección material sin consumir el portador original','Un portador completa un contexto XNOR preparado y deja una señal física mientras continúa con la misma carga y dirección en la ventana comprobada.',[MA],['Observación material','Reutilización de soporte'],[(MA,'mecanismo_repetible/tap_nativo_no_consumo.py')],[],
    {MA:['mecanismo_repetible/MA02_TAP_*.json.gz']},['full context and packet','no packet','six-support context','no frame','different payload53'],notes=['Calibración física preparada, no copia de significado, memoria semántica o estrategia aprendida.'])
add('M224','Restauración genérica de soportes en U0','Recursos de ambas polaridades restauran de forma acotada el uso de contenidos adquiridos en una organización U0 con rutas solicitadas externamente.',[MA],['Memoria','Acceso reutilizable','U0'],[(MA,'mecanismo_repetible/restauracion_u0_piloto.py')],[],
    {MA:['mecanismo_repetible/MA02_U0_RESTORE_*.json.gz']},['requested-bank restoration','no restoration','all-bank restoration','no new query'],notes=['Nuevo protocolo auxiliar T0, no nueva ley ni política de acceso aprendida. Se conserva el dominio y los negativos completos.'])

CF='CF01_CIERRE_FUNCIONAL';EO='ENTE_DEE_OPERATIVO_01';EV='ENTE_DEE_EVOLUCION_02';M1='MENTE_ACUMULATIVA';MU='MENTE_UNIFICADA_Y_FI01'
m=add('M211','Trabajo contextual continuado CF01','Una cola externa obtiene acciones de una organización R9 con referencias propias y privadas; sus recursos e historia conservan actuación a través de cambios de oportunidades.',[CF],['Trabajo contextual','Continuidad','Comunicación'],[],[],{CF:['CF01_MAIN_R[1-3].json.gz','CF01_ACCION_ANULADA_R[1-3].json.gz','CF01_SIN_RETORNO_R[1-3].json.gz','SERVICIO_CF01_MAIN_V[1-3].json.gz']},['main three blocks','annulled actions','omitted return','measurements service'],timeout=3600,notes=['El retorno CF01 se programaba antes de conocer la ejecución externa real. No demuestra el ciclo causal cerrado que ENTE01 examinó posteriormente. 24/24 trabajos en33 intentos pertenecen a la trayectoria histórica completa, no a réplicas independientes.'])
api_cases(m,CF,[f'CF01_{arm}_R{i}.json.gz'for arm in('MAIN','ACCION_ANULADA','SIN_RETORNO')for i in(1,2,3)],groups=[[f'CF01_{arm}_R{i}.json.gz'for i in(1,2,3)]for arm in('MAIN','ACCION_ANULADA','SIN_RETORNO')])
api_cases(m,CF,['SERVICIO_CF01_MAIN_V1.json.gz'])

m=add('M212','Consecuencia real posterior y uso de la referencia modificada','La acción nativa produce contacto en una ley externa fija; la transducción de ese contacto modifica la referencia física y una oportunidad común posterior distingue las historias.',[EO],['Acción por consecuencias','Referencia adquirida','Control causal'],[],[],{},['real intact return','annulled action','omitted return','decoupled return','formed return cut','sham','common7:16'],timeout=1800,notes=['Transducción y postura del actuador preparadas; selección posterior acotada, no política competente general. La contribución táctil es de carga cero; Python no escribe la corrección.'])
src=script(EO,'mecanismo/retorno_posterior_aux_r01.py')
for i,mode in enumerate(['normal','annulled','omit_return','decoupled','sham','cut']):
    name='EO01_AUX_R01_'+{'omit_return':'OMIT_RETURN'}.get(mode,mode.upper())+'.json.gz'
    p=EVID/EO/name
    if not p.exists():continue
    alias='M212_'+mode;par=parent_for_operation(EO,name,alias);m['parents'].append(par);rel=primary(EO,name);m['references'].append(rel)
    m.setdefault('api_program',[]).append({'reference':rel,'parent':alias,'case':Path(name).stem.removesuffix('.json'),'source_module':src,'function':'episode','configure':True,'refresh_deadline':True,'kwargs':{'system':'{system}','mode':mode,'public':[18,27],'environment_reference':9,'trace':True}})
    commonname=name.replace('.json.gz','_COMMON.json.gz')
    if (EVID/EO/commonname).exists():
        rel=primary(EO,commonname);m['references'].append(rel);m['api_program'].append({'reference':rel,'parent':alias,'case':Path(commonname).stem.removesuffix('.json'),'source_module':src,'function':'episode','configure':True,'refresh_deadline':True,'kwargs':{'system':'{system}','mode':'normal','public':[7,16],'environment_reference':9,'trace':True}})
m['mode']='original_source_function_with_complete_historical_parent'

m=add('M213','Transferencia de referencia entre tareas y leyes','La misma referencia nativa adquirida se utiliza sin nueva enseñanza en puertas, trabajadores o transacción; las historias intacta, sin retorno y opuesta conservan resultados diferentes.',[EV],['Transferencia','Composición','Límites de generalización'],[],[],{},['T intact history','U absent return','H opposite history','annulled action','contrary law'],timeout=3000,notes=['La ley contraria reduce la utilidad de la misma referencia. Transferir un código no acredita una política universal; conservar los resultados H y U inferiores o superiores según el dominio.'])
api_cases(m,EV,['10_DESTINO_B_T.json.gz','11_DESTINO_B_U.json.gz','12_DESTINO_B_H.json.gz','13_DESTINO_B_NULLED.json.gz','14_C_TRANSACCION_T.json.gz','15_C_TRANSACCION_U.json.gz','16_C_TRANSACCION_H.json.gz','28T_TRANSFER.json.gz','28U_TRANSFER.json.gz','28H_TRANSFER.json.gz','30T_CONTRARIA.json.gz','30U_CONTRARIA.json.gz'])

m=add('M214','Sensores R10: componentes crudos y transferencia2→8','Componentes entregados por separado se agregan en v27; una referencia adquirida con dos componentes se utiliza con ocho sin entregar la suma al lector.',[EV],['Percepción nativa','Cantidad','Transferencia'],[],[],{},['2 component acquired history','matched no-return','8 component reserved use','counterfactual individual components'],timeout=2400,notes=['Anatomía de agregación preparada. El entorno puede sumar después de emitida la acción para calcular su consecuencia; esa suma no se entrega como percepción nativa. No confundir magnitud con cardinalidad.'])
api_cases(m,EV,['33T_R10_TRANSFER_B8.json.gz','33U_R10_TRANSFER_B8.json.gz'])
for name in ['piloto_sensorial_r10.py','sensorial_r10.py','validacion_final_r10.py','reserva_escala_r10.py']:
    if (LAB/EV/'capacidad'/name).exists():script(EV,'capacidad/'+name)
glob_primary(EV,['capacidad/*BASE*.json.gz','capacidad/*FRONTERA*.json.gz','capacidad/*RESERVA*.json.gz'])

m=add('M215','Tres contextos acumulados y revisión con límites explícitos','Una organización aprende referencias por contextos sucesivos y vuelve a utilizarlas en nuevos casos; añadir un cuarto contexto permite medir pérdida y no se borra del expediente.',[M1],['Aprendizaje acumulativo','Retención','Actualización'],[],[],{M1:['0[2-9]_*.json.gz']},['three acquired contexts','no-return controls','fourth acquisition with loss','explicit first-context revision'],timeout=3600,notes=['Las referencias no son cuatro políticas independientes. La cuarta adquisición destruyó parte del acceso previo en esta preparación; no se afirma repertorio de cuatro retenido.'])
api_cases(m,M1,['02_ADQUIRIR_C1.json.gz','03_ADQUIRIR_C2.json.gz','04_ADQUIRIR_C3.json.gz','05_RETENCION_3.json.gz','06_ADQUIRIR_C4.json.gz','07_RETENCION_4.json.gz','08_REVISAR_C1.json.gz','09_OTRAS_TRAS_REVISION.json.gz'],groups=[['02_ADQUIRIR_C1.json.gz','03_ADQUIRIR_C2.json.gz','04_ADQUIRIR_C3.json.gz','05_RETENCION_3.json.gz','06_ADQUIRIR_C4.json.gz','07_RETENCION_4.json.gz','08_REVISAR_C1.json.gz','09_OTRAS_TRAS_REVISION.json.gz']])
api_cases(m,M1,['02_ADQUIRIR_C1_U.json.gz','03_ADQUIRIR_C2_U.json.gz','04_ADQUIRIR_C3_U.json.gz','05_RETENCION_3_U.json.gz'],groups=[['02_ADQUIRIR_C1_U.json.gz','03_ADQUIRIR_C2_U.json.gz','04_ADQUIRIR_C3_U.json.gz','05_RETENCION_3_U.json.gz']])

m=add('M225','Quinta asociación y uso material repetido MA02','La misma vida incorpora epsilon, retiene las cuatro asociaciones y permite uso repetido con restauración material; las historias opuesta y sin enseñanza contrastan el contenido.',[MA],['Aprendizaje acumulativo','Retención','Continuidad','Acceso repetido'],[],[],{MA:['25_PREPARAR_EPSILON_MAIN_5.json.gz','28_ADQUIRIR_EPSILON_MAIN_5.json.gz','29_ADQUIRIR_EPSILON_OPPOSITE.json.gz','31_PANEL_MAIN_5.json.gz','32_PANEL_OPPOSITE.json.gz','33_PANEL_NOEVENT.json.gz','43_USO_REPETIDO_64.json.gz','45_REABRIR_CORTE_5.json.gz','51_PANEL_FINAL_CINCO_MAIN5.json.gz']},['fifth prepared support','acquisition minus','opposite plus','no event','64 consecutive uses','reload retained panel'],timeout=3600,notes=['Recursos restaurativos y consulta son preparados. Los64 usos son oportunidades de una vida, no64 individuos. No se trasplantan asociaciones entre variantes.'])
api_cases(m,MA,['25_PREPARAR_EPSILON_MAIN_5.json.gz','28_ADQUIRIR_EPSILON_MAIN_5.json.gz','31_PANEL_MAIN_5.json.gz'],groups=[['25_PREPARAR_EPSILON_MAIN_5.json.gz','28_ADQUIRIR_EPSILON_MAIN_5.json.gz','31_PANEL_MAIN_5.json.gz']])
api_cases(m,MA,['29_ADQUIRIR_EPSILON_OPPOSITE.json.gz','32_PANEL_OPPOSITE.json.gz'],groups=[['29_ADQUIRIR_EPSILON_OPPOSITE.json.gz','32_PANEL_OPPOSITE.json.gz']])
api_cases(m,MA,['33_PANEL_NOEVENT.json.gz','43_USO_REPETIDO_64.json.gz','51_PANEL_FINAL_CINCO_MAIN5.json.gz'])

m=add('M219','Sexta asociación, revisión selectiva y retención MU','Una continuación de MA02 incorpora zeta, conserva el panel anterior y revisa beta; las memorias se utilizan consecutivamente en esa vida.',[MU],['Aprendizaje acumulativo','Actualización','Retención'],[],[],{MU:['A0[5-9]_*.json.gz','A1[0-7]_*.json.gz']},['new zeta','opposite acquisition','no zeta event','six-context panel','selective beta revision','old associations after work'],timeout=3600,notes=['Los seis códigos son asociaciones opacas funcionales en este protocolo, no seis significados NSM ni una política general. La protección de fase posterior es una preparación distinta.'])
api_cases(m,MU,['A05_EXTENSION_ZETA.json.gz','A08_ADQUIRIR_ZETA.json.gz','A13_MAIN_PRIMER_PANEL.json.gz','A14_REVISION_BETA.json.gz','A15_MAIN_RETENCION_TRAS_REVISION.json.gz'],groups=[['A05_EXTENSION_ZETA.json.gz','A08_ADQUIRIR_ZETA.json.gz','A13_MAIN_PRIMER_PANEL.json.gz','A14_REVISION_BETA.json.gz','A15_MAIN_RETENCION_TRAS_REVISION.json.gz']])
api_cases(m,MU,['A10_H_ADQUIRIR_OPUESTO.json.gz','A12_H_PRIMER_PANEL.json.gz'],groups=[['A10_H_ADQUIRIR_OPUESTO.json.gz','A12_H_PRIMER_PANEL.json.gz']])
api_cases(m,MU,['A11_U_PRIMER_PANEL.json.gz'])

m=add('M220','Percepción cruda de128 componentes con memoria previa','Un árbol material preparado incorpora128 entradas individuales en v27 y su salida se usa en tareas; paneles previos intercalados muestran el coste o conservación de seis asociaciones.',[MU],['Percepción nativa','Composición','Retención conjunta','Escalabilidad'],[],[],{MU:['B_MAIN_09_TRAMA128_*.json.gz','B_MAIN_10_RETENCION_TRAMA_*.json.gz','escalamiento/PLAN_B01_128.json.gz','escalamiento/RESULTADOS*.json']},['three native128 frames','six old associations between frames','component relevance','rate and scale negatives'],timeout=3600,notes=['126 perturbaciones nuevas y2 repeticiones técnicas no se suman como128 aprendizajes. Cadencia2 perdió acceso aunque admitió352/352 entradas; dominios16/67/200 conservaron el panel en la comparación histórica. N101 no acredita mejora universal.'])
api_cases(m,MU,[item for i in(1,2,3)for item in(f'B_MAIN_09_TRAMA128_{i}.json.gz',f'B_MAIN_10_RETENCION_TRAMA_{i}.json.gz')],groups=[[item for i in(1,2,3)for item in(f'B_MAIN_09_TRAMA128_{i}.json.gz',f'B_MAIN_10_RETENCION_TRAMA_{i}.json.gz')]])
for name in ['controles_b05_r3.py','relevancia_b05_r2.py','recalcular_escalamiento_b.py','recalcular_b06_b07.py','probar_proteccion_fase_r16.py']:
    if (LAB/MU/'escalamiento'/name).exists():script(MU,'escalamiento/'+name)
for name in ['RESULTADOS_ESCALAMIENTO_B05.md','RESULTADOS_B06_CADENCIA_RUIDO.md','RESULTADOS_B07_ESCALA_Y_CONTROL_FASE.md','RESULTADOS_PROTECCION_R16.md']:
    if (LAB/MU/'escalamiento'/name).exists():copy(LAB/MU/'escalamiento'/name,'documentacion/'+MU+'/'+name)

m=add('M221','Cadena material: memoria, archivo real y nueva decisión','Una señal de memoria determina una acción que modifica un archivo local; el tamaño resultante se transduce como acontecimiento posterior y modifica una segunda respuesta.',[MU],['Composición','Acción externa','Uso consecutivo de memoria'],[],[],{MU:['B_MAIN_05_CADENA_*_INICIO.json.gz','B_MAIN_05_CADENA_*_FIN.json.gz','composicion_b/*.json.gz']},['gamma file13','epsilon file32','zeta file13','annulled first action','input cut','sham'],timeout=3000,notes=['El archivo es un entorno externo real local, no memoria oculta del target. El código de la asociación se obtiene de la dinámica; el actuador y la transducción de tamaño son fijos y preparados.'])
api_cases(m,MU,[name for i in(1,2,3)for name in(f'B_MAIN_05_CADENA_{i}_INICIO.json.gz',f'B_MAIN_05_CADENA_{i}_FIN.json.gz')],groups=[[f'B_MAIN_05_CADENA_{i}_INICIO.json.gz',f'B_MAIN_05_CADENA_{i}_FIN.json.gz']for i in(1,2,3)])
script(MU,'composicion_b/controles_cadena_b01.py')

m=add('M222','Servicio persistente emparejado MU01 y protección preparada de fase','Un propietario de Runtime, cola SQLite y mundo completo permiten guardar y continuar peticiones materiales sin duplicar transacciones; R17 conserva el servicio y un calendario P0 que protege lecturas concretas.',[MU],['Persistencia','Continuidad entre procesos','Instrumento de servicio','Protección de fase'],[],[],{},['exact final R17 paired export','archived60minute protocol and denominators','R16 matched causal calendar controls','short new technical paired continuation'],timeout=600,mode='short_paired_continuation_not_sixty_minute_replay',notes=['La reproducción técnica nueva no repite la hora R17 ni acredita acceso actual a sus seis memorias. El recálculo archivado verifica los120/120 usos anteriores y los12/12 casos crudos. La pareja completa conserva registros de transporte necesarios; no son memoria cognitiva consultable. Calendario y reenseñanza B0 son P0, no recuperación autónoma.'])
r17=EVID/MU/'servicio/SERVICIO_60MIN_FASE_R17'
paired=r17/'PAQUETE_FINAL_POSTSTOP'
for p in paired.rglob('*'):
    if p.is_file():copy(p,'recursos/servicio_r17/pareja/'+p.relative_to(paired).as_posix())
m['paired_export']='recursos/servicio_r17/pareja'
for p in r17.rglob('*'):
    if p.is_file()and not p.is_relative_to(paired):
        if 'ERROR'in p.name or p.name in('RECALCULO_FASE_R3.json','OWNER_1_STDERR.txt','OWNER_2_STDERR.txt'):continue
        copy(p,'recursos/servicio_r17/ensayo/'+p.relative_to(r17).as_posix())
for name in ['recalcular_ensayo_fase_r3.py','recalcular_tiempo_fase_r3.py','resumir_funciones_fase_r3.py']:
    script(MU,'servicio/'+name)
for relative in ['contratos/SERVICIO_PERSISTENTE_MU01.json','documentacion/GUIA_SERVICIO_PERSISTENTE_MU01.md']:
    if (S/relative).exists():copy(S/relative,'documentacion/'+relative)
m['recalc_original']={'command':['{python}','sectores/mente/laboratorio/campanas/'+MU+'/servicio/recalcular_ensayo_fase_r3.py','--evidencia','sectores/mente/recursos/servicio_r17/ensayo','--salida','{out}/RECALCULO_R17.json'],'native_ticks':0}
for group in ['servicio/PROTECCION_FASE_R16','servicio/AUTOPSIA_FASE_R15']:
    for p in (EVID/MU/group).glob('*'):
        if p.is_file()and p.suffix in('.json','.gz','.py','.md'):primary(MU,p.relative_to(EVID/MU).as_posix())

m=add('M226','Relevancia causal individual de128 componentes','Bifurcaciones con idéntica referencia reciben128 ceros o una sola contribución2 en cada posición; la salida y las seis memorias se miden con el mismo lector y calendario.',[MU],['Percepción nativa','Composición','Causalidad','Retención'],[],[],{},['128 component perturbations','zero baseline','missing raw','no query','opposite/no acquired history','equal-reference diagnostic','aggregate cut/sham','datum cut/sham'],timeout=5400,notes=['128 bifurcaciones de un prefijo común;126 posiciones reservadas y2 repeticiones exploratorias, no128 aprendizajes independientes. Reproduce desde el estado completo ya preparado de cada rama. Los cortes de RAW son intervenciones diagnósticas externas. El resumen histórico detectó un cambio documental del registro padre y no debe transformarse en certificado de integridad global.'])
for name in ['arbol_umbral_adquirido_b01.py','arbol_en_selector_b05.py','arbol_en_selector_b02.py','preflight_arbol_crudo.py']:
    script(MU,'escalamiento/'+name)
script(MU,'transferencia_b/frontend_b01_r2.py')
for folder in ['B05_RELEVANCE_R2_N128_0_128','B05_TREE_R1_N128','B05_CONTROLS_R3_N128']:
    for p in sorted((EVID/MU/'escalamiento'/folder).glob('*.json.gz')):
        if p.stem.endswith('_PREP.json')or'.pre_'in p.name:continue
        row=read(p)
        if'INSTRUMENTO'not in row:continue
        inner=row['result']
        if'label'not in inner:continue
        label=inner['label'];index=inner['raw_components'].index(2)if folder.startswith('B05_RELEVANCE')else None
        name=p.relative_to(EVID/MU).as_posix();alias='M226_'+folder.split('_')[1]+'_'+p.name.removesuffix('.json.gz')
        alias=alias.replace('-','_');par=parent_for_operation(MU,name,alias);m['parents'].append(par);rel=primary(MU,name);m['references'].append(rel)
        source='relevancia_b05_r2.py'if index is not None else'controles_b05_r3.py'if folder.startswith('B05_CONTROLS')else'ensayar_arbol_b05_r1.py'
        src=script(MU,'escalamiento/'+source)
        kwargs={'level':128,'label':label,'old_panel':inner.get('old_six_panel_after_2N')is not None}
        if index is not None:kwargs['component_index']=index
        elif source=='controles_b05_r3.py':
            interventions=inner.get('diagnostic_edits',[])
            kwargs['intervention']=({'site':'C'if interventions[0]['site']==inner['geometry']['remote_aggregate_site']else'S','mode':interventions[0]['mode'],'directory':'{work}','case':p.name.removesuffix('.json.gz')}if interventions else None)
        m.setdefault('api_program',[]).append({'reference':rel,'parent':alias,'case':folder+'_'+p.name.removesuffix('.json.gz'),'source_module':src,'function':'execute','native_imports':True,'kwargs':kwargs})

m=add('M227','Una señal residual participa en una readquisición posterior','La contribución antigua5 y el docente nuevo11 forman un soporte16. Cortar selectivamente la contribución ya formada impide el nuevo uso de alfa mientras gamma y delta continúan utilizables.',[MA],['Reutilización de soporte','Historia útil','Readquisición'],[(MA,'residuo_reutilizable_r09.py')],[],{MA:['residuo/MA02_R09_RESIDUO_*.json.gz']},['formed residue cut','exact RAW and clock sham','other gamma/delta retained'],timeout=1800,notes=['Hay docente nuevo explícito: es readquisición con reutilización, no recuperación de un signo antiguo intacto. El corte es diagnóstico externo y no selección de la organización.'])
p=parent_for_operation(MA,'residuo/MA02_R09_RESIDUO_SHAM.json.gz','MA02_MAIN');p['checkpoint_alias']='MA02_MAIN.T2955.reproduction.deetsnap.gz';m['parents'].append(p)


expected_snapshots={}
for m in mechanisms:
    for rel in m['references']:
        v=read(STAGE/rel);final=v.get('final',v.get('final_snapshot',v.get('snapshot',{})))
        if isinstance(final,dict)and final.get('path')and final.get('sha256'):
            digest=final['sha256'];name=Path(final['path']).name
            camp=Path(rel).parts[1];sub=Path(*Path(rel).parts[2:-1])
            choices=[EVID/camp/sub/name,EVID/camp/name,S/'estado/checkpoints'/name,OLD/'sistema/estado/checkpoints'/name]
            file=next((p for p in choices if p.is_file()and sha(p)==digest),None)
            if file:
                dest='recursos/estados/'+digest+'.deetsnap.gz'
                if not(STAGE/dest).exists():copy(file,dest)
                expected_snapshots[rel]=dest
            else:m.setdefault('reference_state_missing',[]).append({'primary':rel,'name':name,'sha256':digest})
        if m.get('prefix_only_external')and v.get('id'):
            f=EVID/MI/(v['id']+'.DESPUES_USO.deetsnap.gz')
            if f.exists():expected_snapshots[rel]='recursos/estados/'+sha(f)+'.deetsnap.gz'
# Record every included exact source once in the sector catalogue.
for m in mechanisms:
    mids={*m['entries'],*m['references'],*(x['snapshot']for x in m['parents'])}
    for op in m.get('api_program',[]):
        if op.get('source_module'):mids.add(op['source_module'])
        mids.update(x['relative']for x in op.get('overlay',[]))
    if m['id']=='M222':mids.update(x['relative']for x in sources if '/servicio_r17/'in x['relative']or '/servicio/'in x['relative'])
    m['source_files']=[x for x in sources if x['relative']in mids]
    m['native']={'command':['{python}','sectores/mente/ejecutar_mente.py','--id',m['id'],'--out','{out}'],'timeout_seconds':m['timeout_seconds']}
    m['recalc']={'command':['{python}','sectores/mente/recalcular_mente.py','--id',m['id'],'--out','{out}']}
    m['expected']={'equality':'Exact tick, RAW SHA256 and clocks SHA256 for original Store outcomes; exact native observations for direct MA02 protocols. Identities and paths differ explicitly.'}
    if m['id']=='M222':
        m['native']={'command':['{python}','sectores/mente/servicio_mente.py','--out','{out}'],'timeout_seconds':600}
        m['recalc']=m['recalc_original'];m['expected']={'historical':'Archived exact source recalculation, no new60minute trial.','technical':'Full paired import then one legal advance, save, second-process reload and one legal advance; previous complete state preserved.'}
    if m['pending']:m['native']=None
doc={'schema':'DEE.compendio.sector.mente.v1','sector':'mente','engine':'dee_thinking4.5.0 cp313 win_amd64 / v27','mechanisms':mechanisms,'shared_source_files':list({x['relative']:x for x in sources}.values()),'expected_snapshots':expected_snapshots,'native_ticks_executed_in_preparation':0}
(STAGE/'sector_config.json').write_text(json.dumps(doc,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
(STAGE/'sector.json').write_text(json.dumps(doc,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
(WORK/'sector.json').write_text(json.dumps(doc,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print('Prepared',len(mechanisms),'mechanisms',len(sources),'source selections; no Native executed')
