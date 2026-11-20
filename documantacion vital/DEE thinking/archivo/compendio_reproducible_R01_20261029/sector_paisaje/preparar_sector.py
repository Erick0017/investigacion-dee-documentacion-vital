from pathlib import Path
import json,gzip,hashlib,shutil,re,ast,sys

ROOT=Path(__file__).resolve().parents[3]
ARCH=ROOT/'archivo/DEE Cognitive System 1.1'
HERE=Path(__file__).resolve().parent
STAGE=HERE/'stage';STAGE.mkdir(exist_ok=True)
LAB=ARCH/'laboratorio/campanas';EV=ARCH/'evidencia/campanas'
SYS=ROOT/'DEE Cognitive 2.0/sistema'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):
    b=Path(p).read_bytes()
    return json.loads(gzip.decompress(b)if str(p).endswith('.gz')else b)
def save(p,d):
    p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def cp(src,rel):
    dst=STAGE/rel;dst.parent.mkdir(parents=True,exist_ok=True)
    if dst.exists():assert sha(dst)==sha(src),(dst,src)
    else:shutil.copy2(src,dst)
    return {'original':str(src),'relative':str(rel).replace('\\','/'),'sha256':sha(src),'bytes':src.stat().st_size}

OBJECT_DIRS=[LAB/c/'versiones_codigo/objetos'for c in ['PAISAJE_CAUSAL_01','ACCESO_ADAPTATIVO_01']]
def by_hash(h,fallback=None):
    if fallback and fallback.is_file()and sha(fallback)==h:return fallback
    for dd in OBJECT_DIRS:
        f=dd/(h+'.py')
        if f.is_file()and sha(f)==h:return f
    return None

# IDs identify mechanisms, not the number of branches or probes.
SPECS=[
 ('M101','Asociación léxica arbitraria y acceso por fase',['2','11'],'ESPANOL_FUNCIONAL_01',[
  ('LEXICO_ARBITRARIO_04','lexico_arbitrario_04.py',None)]),
 ('M102','Puente léxico y uso contextual de varios accesos',['3','5','11'],'ESPANOL_FUNCIONAL_01',[
  ('PUENTE_LEXICO_11','puente_lexico_11.py',None),('INTEGRACION_PUENTE_12','integracion_puente_12.py',None)]),
 ('M103','Comunicación de una asociación y uso por el receptor',['6','11'],'ESPANOL_FUNCIONAL_01',[
  ('COMPRENSION_Y_SOCIAL_13','comprension_y_social_13.py',None)]),
 ('M104','Readquisición cuantitativa protegida',['3','4'],'ESPANOL_FUNCIONAL_01',[
  ('REAPRENDIZAJE_MAGNITUD_26','reaprendizaje_magnitud_26.py',None)]),
 ('M105','Composición de orden y contacto con consecuencia',['5'],'ESPANOL_FUNCIONAL_01',[
  ('COMPOSICION_01','composicion_01.py',None)]),
 ('M110','Historia y retorno útil con composición y receptor',['1','5','6'],'PAISAJE_CAUSAL_01',[
  ('FACTORIAL_E1_07','factorial_e1_07.py',None),('RETORNO_UTIL_15','retorno_util_15.py',None)]),
 ('M111','Protección bidireccional bajo uso multifuncional',['1','3','5'],'PAISAJE_CAUSAL_01',[
  ('PROTECCION_BIDIRECCIONAL_33','continuidad_carga_28.py',None)]),
 ('M112','Acceso preparado a información transformada y contexto mixto',['1','3'],'PAISAJE_CAUSAL_01',[
  ('LECTOR_POST_TRANSFORMACION_41','lector_post_transformacion_41.py',None),('CONTEXTO_UTIL_MIXTO_44','contexto_util_mixto_44.py',None)]),
 ('M120','Protocolo común de recuperación y uso sin reenseñar',['3','11'],'ACCESO_ADAPTATIVO_01',[
  ('RECUPERACION_COMUN_07','recuperacion_comun_07.py',None)]),
 ('M121','Selección local revisada por consecuencias y nuevo contenido',['2','6','7'],'ACCESO_ADAPTATIVO_01',[
  ('ACCESO_LOCAL_SEPARADO_33','acceso_local_separado_33.py',None),('CONTROLES_Y_RESERVAS_33','acceso_local_separado_33.py',None)]),
 ('M122','Pérdida causal contrastada y readquisición explícita',['3'],'ACCESO_ADAPTATIVO_01',[
  ('PERDIDA_Y_REAPRENDIZAJE_13','perdida_y_reaprendizaje_13.py',None)])
]

mechanisms=[]
for mid,title,families,campaign,groups in SPECS:
    m={'id':mid,'name':title,'function':title,'campaigns':[campaign],'word_families':families,'variants':[],
       'history_status':'Resultado positivo histórico y controles originales recuperados; no nuevo aprendizaje de la vida activa.',
       'integrity_status':'Selección exacta por SHA y snapshots completos cuando el protocolo los exige.',
       'current_validation':'Pendiente de ejecución desde ZIP final extraído','pending':[],
       'assistance':'Preparación, calendario, puertos y decodificador definidos por el investigador; transformación y contenido posterior mediante v27.',
       'limitations':['Realizaciones diferentes y ramas de control no son aprendizajes simultáneos de un mismo individuo.'],
       'source_files':[],'native':{'command':['{python}','{sector}/ejecutar.py','native',mid,'--out','{out}','--common','{common}'],'timeout_seconds':2400},
       'recalc':{'command':['{python}','{sector}/ejecutar.py','recalc',mid,'--out','{out}'],'timeout_seconds':120},
       'expected':'Igualdad exacta de RAW/clocks,N,tick y de las lecturas/resultados funcionales seleccionados; se mantienen errores y controles.'}
    for group,fallback_name,chosen in groups:
        files=sorted((EV/campaign/group).rglob('PRIMARIOS.json*'))
        if not files:m['pending'].append('No se encontraron primarios de '+group)
        for p in files:
            d=read(p);case=d.get('case',p.parent.name)
            if chosen and case not in chosen:continue
            key=group+'__'+case
            ref_rel=Path('mecanismos')/mid/'primarios'/(key+'.json.gz')
            target=STAGE/ref_rel;target.parent.mkdir(parents=True,exist_ok=True)
            original=p.read_bytes();uncompressed=gzip.decompress(original)if p.suffix=='.gz'else original
            if p.suffix=='.gz':target.write_bytes(original)
            else:target.write_bytes(gzip.compress(original,compresslevel=9,mtime=0))
            v={'id':key,'historical_case':group+'/'+case,'case':case,'reference':ref_rel.as_posix(),'reference_uncompressed_sha256':hashlib.sha256(uncompressed).hexdigest(),
               'source_files':[{'original':str(p),'relative':ref_rel.as_posix(),'sha256':sha(p),'stored_sha256':sha(target),'bytes':len(original),'compression':'original gzip'if p.suffix=='.gz'else'lossless gzip of exact original bytes'}],
               'pending':[],'protocol':'','parent_record':None,'parent_snapshot':None,'overrides':[],
               'checks':['/post'],'output_primary':'PRIMARIOS.json.gz'if p.suffix=='.gz'else'PRIMARIOS.json'}
            if d.get('commit',{}).get('result')is not None:v['checks'].append('/commit/result')
            if group=='RETORNO_UTIL_15':v['checks']+=['/milestones/'+str(i)+'/records'for i in range(len(d['milestones']))]
            h=d.get('source_sha256',d.get('code_sha256'));fallback=LAB/campaign/fallback_name
            source=by_hash(h,fallback)if h else fallback
            if not source:
                v['pending'].append('No se recuperaron bytes del protocolo con SHA '+str(h));m['variants'].append(v);continue
            rel=Path('codigo')/campaign/(source.stem+'.py'if len(source.stem)==64 else source.name)
            v['source_files'].append(cp(source,rel));v['protocol']=rel.as_posix();v['protocol_sha256']=sha(source)
            par=d.get('parent')
            if isinstance(par,dict):
                encoded=par['snapshot_sha256'];record_rel=Path('mecanismos')/mid/'padres'/(encoded+'.json');save(STAGE/record_rel,par)
                snapshot=ARCH/'sistema'/par['snapshot']
                if not snapshot.exists():snapshot=SYS/par['snapshot']
                if not snapshot.exists():v['pending'].append('Snapshot padre completo ausente '+par['snapshot'])
                elif sha(snapshot)!=encoded:v['pending'].append('Snapshot padre hash no coincide '+par['snapshot'])
                else:
                    snap_rel=Path('estados')/(encoded+'.deetsnap.gz');v['source_files'].append(cp(snapshot,snap_rel));v['parent_snapshot']=snap_rel.as_posix()
                v['parent_record']=record_rel.as_posix();v['parent_life']=par['life_id'];v['parent_tick']=par['physical']['tick']
                v['native_mode']='adquisición/uso en copia exacta del padre histórico'
            else:v['native_mode']='preparación T0 auxiliar y protocolo completo, no E1'
            deps=d.get('dependencies',{})
            for module,h2 in deps.items():
                mpath=Path(*module.split('.')).with_suffix('.py');src=by_hash(h2,SYS/mpath)
                if not src:
                    v['pending'].append('Revisión de dependencia histórica no recuperada '+module+' SHA '+h2)
                    continue
                rel2=Path('objetos_codigo')/(h2+'.py');v['source_files'].append(cp(src,rel2));v['overrides'].append({'module':mpath.as_posix(),'source':rel2.as_posix(),'sha256':h2})
            # Registros locales completos del retorno y los testigos compactos,
            # sin snapshots densos redundantes de cada tick.
            for name in ['CAMPO_COMPLETO.jsonl.gz','CAMPOS_LOCALES.jsonl.gz','CAMPOS_SELECCION.jsonl.gz']:
                f=p.parent/name
                if f.is_file():v['source_files'].append(cp(f,Path('mecanismos')/mid/'testigos'/(key+'__'+name)))
            m['variants'].append(v)
    mechanisms.append(m)

# Dependencias de protocolos que se importan por nombre local o por el
# camino estructural laboratorio/campanas/PAISAJE_CAUSAL_01.
helpers=['instrumentos_pc01.py','agenda_binaria_pc01.py']
for name in helpers:
    cp(LAB/'PAISAJE_CAUSAL_01'/name,Path('codigo/PAISAJE_CAUSAL_01')/name)
cp(LAB/'ACCESO_ADAPTATIVO_01/avance_acotado.py','codigo/ACCESO_ADAPTATIVO_01/avance_acotado.py')

save(HERE/'sector.json',{'schema':'DEE.compendio.sector.v1','sector':'paisaje','root_original':str(ROOT),'mechanisms':mechanisms,
 'required_common':['app/lives.py','app/native_tools.py','app/process_control.py','organizaciones/cpc9/src','capacidades','runtime/dee_thinking-4.5.0-cp313-cp313-win_amd64.whl'],
 'covered_campaigns':['ESPANOL_FUNCIONAL_01','PAISAJE_CAUSAL_01','ACCESO_ADAPTATIVO_01'],
 'remaining_campaigns':['AUDITORIA_RETROSPECTIVA_01','HABITAT_CAUSAL_Y_ESTRES_E1_01','INTEGRACION_COGNITIVA_SITUADA_E1_01','CONSOLIDACION_EVOLUCION_E1_CICLO_02']})
save(STAGE/'sector.json',read(HERE/'sector.json'))
print(json.dumps({'mechanisms':len(mechanisms),'variants':sum(len(m['variants'])for m in mechanisms),'pending':[(m['id'],v['id'],v['pending'])for m in mechanisms for v in m['variants']if v['pending']],'files':sum(1 for p in STAGE.rglob('*')if p.is_file()),'bytes':sum(p.stat().st_size for p in STAGE.rglob('*')if p.is_file())},ensure_ascii=False,indent=2))
