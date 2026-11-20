"""Add prepared E3 recipes/evidence to existing RP, no Native or S2 changes.

The historical root batch was executed. This helper does NOT claim that the
new generic RP CLI recipe has itself been Native-executed. Default dry-run;
--apply writes only new stable RP materials/recipe and one additive registry
entry, protected by a compare-and-swap of the entire prior registry bytes.
"""
from pathlib import Path
import argparse,copy,datetime,hashlib,json,os
P=Path(__file__).resolve().parents[2];C=P.parents[2]/'DEE Cognitive 2.0';RP=C/'reproducibilidad'
RECIPE='pi04_e3_contingencia_R02'
CAPSULE='PI03_PI04_E3_R02'
CAP_SHA='e9f4aadcb4dc711ddfaa62f3c85bd2596b30ccef5217212e913fbd2caec24631'
BASE='PI03_FINAL_T775355';POST='PI03_PI04_POST_E3_T789431'
RAW='2289d1e01c934e982e0f8813146dbadace232f284a822e3eb518105572c4afce'
CLOCKS='93e353b5f71f4cd18702c5977e96643ac978e505c395c48266f09e082f14ae47'
def sha(b):return hashlib.sha256(b).hexdigest()
def encoded(v):return(json.dumps(v,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def stable(p):
    if not p.is_file()or p.is_symlink():raise ValueError('Regular stable source only '+str(p))
    a=p.stat();b=p.read_bytes();z=p.stat()
    if(a.st_size,a.st_mtime_ns)!=(z.st_size,z.st_mtime_ns):raise ValueError('Source changed '+str(p))
    return b
def write_literal(p,b):
    p.parent.mkdir(parents=True,exist_ok=True)
    if p.exists():
        if p.read_bytes()!=b:raise ValueError('Prior stable content differs, preserve '+str(p))
    else:
        with p.open('xb')as f:f.write(b);f.flush();os.fsync(f.fileno())
def step(label,literal,**kw):return{'label':label,'literal':literal,'feedback':'omit',**kw}
def make_recipe(plan,manifest_sha):
    variants={}
    supplies={2:(-1,2),6:(1,4),10:(-1,2),14:(1,4)}
    for arm,expected_products in(('real',14),('desacoplado',18)):
        literal={'modo':'eci01-pi04-e3-admitir','brazo':arm}
        if arm=='desacoplado':literal['plan']=plan
        if len(json.dumps(literal,ensure_ascii=False).encode('utf-8'))>=8192:raise ValueError('Transport literal exceeds unchanged8192 limit')
        batch=[step('admit',literal,require_zero_ticks=True)]
        for i in range(18):
            if i in supplies:
                sign,delay=supplies[i];batch.append(step('supply_%02d'%i,{'modo':'eci01-pi03-tarea-suministrar','cantidad':4,'conexion':sign,'demora_periodos':delay},require_zero_ticks=True))
            batch.append(step('opportunity_%02d'%i,{'modo':'eci01-pi04-e3-oportunidad'},read_path=['result','rows',0,'reader','choice'],receipt_paths=[['result','rows',0,'requests']],stop_on_NULL=True))
        batch.append(step('final_state',{'modo':'eci01-pi04-e3-estado'},require_zero_ticks=True))
        checks=[{'label':'actual_useful_products_not_global_score','operation':'sum_true','values':[{'step':'opportunity_%02d'%i,'path':['result','rows',0,'useful_product']}for i in range(18)],'expected':expected_products},
                {'label':'exact_completed_opportunities','operation':'value','values':[{'step':'final_state','path':['result','rows',0,'progress','ordinal']}],'expected':18}]
        for key,val in(('N',67),('tick',789431),('RAW_sha256',RAW),('clocks_sha256',CLOCKS)):
            checks.append({'label':'exact_final_physical_'+key,'operation':'value','values':[{'step':'final_state','path':['committed_snapshot','physical',key]}],'expected':val})
        variants[arm]={'batches':[batch],'final_checks':checks,'native_receipt_expectations':{'unique_requested':90,'applied':90,'rejected':0,'pending_or_other':0}}
    return{'schema':'DEE.reproduction.recipe.v1','id':RECIPE,'title':'PI04 E3: contingencia real y retorno permutado con dosis/fase iguales; extensión desde775355',
           'revision':'PI04_E3_R02_PREPARED_RP','prefix':BASE,'code_capsule_key':CAPSULE,'reproduction_enabled':True,
           'required_life_prefix':'ECI02_PI03_REPRO_PI04_',
           'variants':variants,
           'modalities':{'A':'Records and actual file bytes recalculated from preserved stable evidence','B':'Use of learned inherited selection plus eighteen new environmental opportunities in a fresh clone','C':'New adaptation within the inherited genealogy, not acquisition fromT0','D':'Original Root Native batches are complete; this new generic RP CLI recipe has not yet been Native executed','E':'Not recovery, restoration or autonomous repair'},
           'assistance':'Prepared anatomy, q+6 reader,0->motor-1, explicit supply, device law and eighteen opportunity schedule. The Native output chooses every actual actuator. The permuted branch is an auditor intervention and never a promoted main.',
           'limitations':'PREPARED RP RECIPE, not a recorded Native CLI replay. Original real14/18 vs permuted18/18 does not favor true contingency; the fixed control signals precede reversals. A matched-received-signal maintain/switch rule describes both. Same-prefix futures are not independent organisms.18/18 control must not be called autonomous anticipation. Stop and preserve any NULL/rejection; never reset counters/retry IDs.',
           'protocol':{'product_relative':'reproducibilidad/evidencia/PI04_E3_R02/datos/protocol.json','sha256':sha(stable(P/'codigo/E3_R02/PROTOCOLO_E3_R02.json')),'opportunities':18,'supplies':'Inherited2offers plus four explicit4offer blocks; no source recalculation'},
           'materials':{'product_relative':'reproducibilidad/evidencia/PI04_E3_R02','manifest':'MANIFIESTO_ESTABLE.json','manifest_sha256':manifest_sha},
           'verification':{'state':'PREPARED_NATIVE_CLI_NOT_RUN','original_root_batch_modality':'Executed through original supervised owner, not through this newly registered RP recipe','original_real_products':14,'original_permuted_products':18,'original_unique_applied_inputs_each':90,'expected_physical_is_same_for_both':{'N':67,'tick':789431,'RAW_sha256':RAW,'clocks_sha256':CLOCKS},'Native_executions_by_this_helper':0},
           'blockers':[]}
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--apply',action='store_true');a=ap.parse_args()
    registry=RP/'RECURSOS.json';before=stable(registry);cfg=json.loads(before);old=copy.deepcopy(cfg)
    cap=cfg['code_capsules'][CAPSULE]
    if cap['manifest_sha256']!=CAP_SHA or sha(stable(C/cap['product_relative']/cap['manifest']))!=CAP_SHA:raise ValueError('Exact stable E3 code capsule required')
    if cfg['pairs'][BASE]['tick']!=775355 or cfg['pairs'][POST]['tick']!=789431:raise ValueError('Stable initial/post prefixes differ')
    for alias in(BASE,POST):
        e=cfg['pairs'][alias]
        if sha(stable(C/e['product_relative']/'EXPORTACION_SERVICIO.json'))!=e['manifest_sha256']:raise ValueError('Stable pair manifest changed')
    closed=read(P/'control/E3_real_R02.json');plan=closed['final']['result']['rows'][0]['replay_plan_encoded']
    source=P/'ensayos/EVIDENCIA_E3_PORTABLE';target=RP/'evidencia/PI04_E3_R02'
    selection={}
    for f in sorted(source.rglob('*')):
        if f.is_file():selection['datos/'+f.relative_to(source).as_posix()]=stable(f)
    extras={
      'RECALCULAR_ALINEACION_E3.py':P/'codigo/E3/RECALCULAR_ALINEACION_E3.py',
      'RESULTADO_E3_CONTRASTADO.json':P/'control/E3_VALIDACION_PORTABLE_R02/RECALCULO/RECALCULO_E3.json',
      'RESULTADO_ALINEACION_CONTRASTADO.json':P/'control/E3_ALINEACION_SENALES_Y_REFERENCIA_EMPAREJADA_R02.json',
      'VERIFICACION_EXTRACCION_LIMPIA.json':P/'control/PORTABILIDAD_RECALCULO_E3_R02.json',
      'adversos/E3_FALLO_SUPPLY_R01.json':P/'control/E3_FALLO_SUPPLY_R01.json',
      'adversos/E3_FUTURO_ADVERSO_R01_PRESERVADO.json':P/'control/E3_FUTURO_ADVERSO_R01_PRESERVADO.json',
      'adversos/E3_CUOTA_METADATA_MEDIDA_PASIVA.json':P/'control/E3_CUOTA_METADATA_MEDIDA_PASIVA.json',
      'codigo_original/pi03_suministro_explicito_R03_ORIGINAL.py':P/'codigo/E3_R02/pi03_suministro_explicito_R03_ORIGINAL.py'}
    for name,file in extras.items():selection[name]=stable(file)
    procedure='''# PI04 E3 — procedimiento preservado

La ejecución original Root Native ya terminó: real14/18 y desacoplado18/18,
90/90 entradas por brazo. La nueva receta del gestor está PREPARADA; no se
ha ejecutado nuevamente Native mediante ese CLI. No iniciar sobre ACTIVO.

Desde la raíz de Cognitive:

    motor\\python313\\python.exe -I -B -X utf8 sistema\\gestionar.py reproducibilidad verificar pi04_e3_contingencia_R02
    motor\\python313\\python.exe -I -B -X utf8 sistema\\gestionar.py reproducibilidad reproducir pi04_e3_contingencia_R02 --variante real --vida ECI02_PI03_REPRO_PI04_RP_REAL_01 --destino D:\\DIAGNOSTICOS_DEE\\E3_REAL_NUEVO
    motor\\python313\\python.exe -I -B -X utf8 sistema\\gestionar.py reproducibilidad reproducir pi04_e3_contingencia_R02 --variante desacoplado --vida ECI02_PI03_REPRO_PI04_RP_YOKE_01 --destino D:\\DIAGNOSTICOS_DEE\\E3_YOKE_NUEVO

El padre del destino debe existir. Usar IDs no usados y destinos nuevos en la
misma unidad del producto. Se comparten motor/cápsula y se clona el conjunto
completo; nunca se recreaT0 ni se cambian selectores. La variante desacoplada
reproduce el plan de señales del contraste histórico; no busca un mejor plan.
Los cuatro suministros explícitos son pasos del protocolo, no autoabastecimiento.

Recálculo documental independiente del motor, desde esta misma raíz:

    motor\\python313\\python.exe -I -B -X utf8 reproducibilidad\\evidencia\\PI04_E3_R02\\datos\\RECALCULAR_E3.py --evidence reproducibilidad\\evidencia\\PI04_E3_R02\\datos --out D:\\DIAGNOSTICOS_DEE\\RECALCULO_E3_NUEVO
    motor\\python313\\python.exe -I -B -X utf8 reproducibilidad\\evidencia\\PI04_E3_R02\\RECALCULAR_ALINEACION_E3.py --recalculo D:\\DIAGNOSTICOS_DEE\\RECALCULO_E3_NUEVO\\RECALCULO_E3.json --out D:\\DIAGNOSTICOS_DEE\\ALINEACION_E3_NUEVA.json

Estas órdenes sólo leen registros y escriben resultados nuevos, sin importar
DEE ni abrir un mundo. Las rutas históricas que aparecen en PROCEDENCIA y
registros son procedencia, nunca requisitos del recálculo o del runner.

El control recibió cuatro fallos falsos antes de las inversiones de conexión;
no se atribuye su18/18 a anticipación autónoma. La regla descriptiva mantener/
cambiar según señal recibida coincide con las18acciones de ambos brazos.
R01 conserva el fallo técnico de cuota y su mundo adverso permanece aparte;
la adaptación R03_R02 mantiene el límite Native1MiB, los seis antecedentes y
la fuente actual completa, archivando sólo nuevas duplicaciones por hash.

Los materiales grandes quedan en reproducibilidad/materiales: el prefijo
PI03_FINAL_T775355 y el estado real posterior PI03_PI04_POST_E3_T789431.
Son cortes reproducibles, no dos principales ni una fusión de memorias.
'''
    selection['PROCEDIMIENTO_E3_R02.md']=procedure.encode('utf-8')
    manifest={'schema':'PI04.E3.stable_product_evidence.v1','files':[{'file':name,'bytes':len(b),'sha256':sha(b)}for name,b in sorted(selection.items())],
              'Native_executions_by_preservation':0,'original_Root_Native_batches_executed':True,'new_RP_recipe_Native_verified':False,
              'runtime_paths_relative_to_product':True,'historical_source_paths_are_provenance_only':True}
    manifest_bytes=encoded(manifest);manifest_hash=sha(manifest_bytes);recipe=make_recipe(plan,manifest_hash);recipe_bytes=encoded(recipe)
    entry={'product_relative':'reproducibilidad/evidencia/PI04_E3_R02','manifest':'MANIFIESTO_ESTABLE.json','manifest_sha256':manifest_hash,
           'recipe':RECIPE,'prefix':BASE,'post_prefix':POST,'code_capsule_key':CAPSULE,
           'modalities':{'documentary_recalculation':'VERIFIED_FROM_CLEAN_EXTRACTION','original_Native_batch':'EXECUTED_BY_ROOT','new_generic_RP_CLI_recipe':'PREPARED_NOT_NATIVE_EXECUTED'},
           'scope':'Local generic-return selection with dose/phase controlled replay. True contingent14/18, permuted18/18; no general autonomy/anticipation claim.'}
    cfg.setdefault('analysis_deltas',{})
    if CAPSULE in cfg['analysis_deltas']and cfg['analysis_deltas'][CAPSULE]!=entry:raise ValueError('Prior E3 registration differs')
    cfg['analysis_deltas'][CAPSULE]=entry
    # Every previous registry branch, especially F1, remains literal by value.
    check=copy.deepcopy(cfg);check['analysis_deltas'].pop(CAPSULE)
    if 'analysis_deltas'not in old:check.pop('analysis_deltas')
    if check!=old:raise ValueError('An unrelated existing resource would change')
    proof={'schema':'PI04.E3.additive_RP_incorporation.v1','mode':'APPLY_NO_NATIVE'if a.apply else'DRY_RUN_NO_WRITES','at':datetime.datetime.now().astimezone().isoformat(),
           'recipe':RECIPE,'stable_materials':str(target),'members':len(selection)+1,'content_bytes':sum(map(len,selection.values())),
           'manifest_sha256':manifest_hash,'recipe_sha256':sha(recipe_bytes),'registry_before_sha256':sha(before),
           'old_registry_branches_preserved':True,'F1_preserved':old.get('instrument_deltas',{}).get('PI04_F1')==cfg.get('instrument_deltas',{}).get('PI04_F1'),
           'S2_ACTIVO_Manual_modified':False,'Native_imports':0,'new_native_ticks':0,'generic_RP_recipe_Native_executed':False,
           'code_capsule_key':CAPSULE,'prefix':BASE,'post_prefix':POST}
    if a.apply:
        for name,b in selection.items():write_literal(target/name,b)
        write_literal(target/'MANIFIESTO_ESTABLE.json',manifest_bytes)
        for row in manifest['files']:
            b=stable(target/row['file'])
            if len(b)!=row['bytes']or sha(b)!=row['sha256']:raise ValueError('Stable copied evidence differs')
        write_literal(RP/'recetas'/f'{RECIPE}.json',recipe_bytes)
        write_literal(P/'control/RECURSOS_RP_ANTES_E3_R02.json',before)
        if stable(registry)!=before:raise ValueError('Registry changed concurrently; preserve new artifacts and merge from latest registry, no overwrite')
        new_bytes=encoded(cfg);temp=registry.with_name('RECURSOS.E3_R02.pending.json')
        with temp.open('xb')as f:f.write(new_bytes);f.flush();os.fsync(f.fileno())
        if stable(registry)!=before:raise ValueError('Registry changed before atomic replacement; preserve pending file')
        os.replace(temp,registry);proof['registry_after_sha256']=sha(stable(registry))
        write_literal(P/'control/E3_INCORPORACION_RP_R02.json',encoded(proof))
    print(json.dumps(proof,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
