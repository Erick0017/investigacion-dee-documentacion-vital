"""Selecciona primarios, protocolos y padres completos ya existentes."""
from pathlib import Path
import json,gzip,hashlib,shutil,importlib.util
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];ARCH=ROOT/'archivo/DEE Cognitive System 1.1'
STAGE=HERE/'stage';LAB=ARCH/'laboratorio/campanas';EV=ARCH/'evidencia/campanas';SYS=ROOT/'DEE Cognitive 2.0/sistema'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):
 p=Path(p);b=p.read_bytes();return json.loads(gzip.decompress(b)if p.suffix=='.gz'else b)
def save(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def cp(p,rel):
 p=Path(p);out=STAGE/rel;out.parent.mkdir(parents=True,exist_ok=True)
 if out.exists():assert sha(p)==sha(out)
 else:shutil.copy2(p,out)
 return {'original':str(p),'relative':str(rel).replace('\\','/'),'sha256':sha(p),'bytes':p.stat().st_size}
def packref(mid,p):
 rel=Path('mecanismos')/mid/'primarios'/(p.name+'.gz'if p.suffix!='.gz'else p.name);out=STAGE/rel;out.parent.mkdir(parents=True,exist_ok=True)
 raw=p.read_bytes();out.write_bytes(raw if p.suffix=='.gz'else gzip.compress(raw,mtime=0,compresslevel=9))
 return {'original':str(p),'relative':rel.as_posix(),'sha256':sha(p),'stored_sha256':sha(out),'bytes':len(raw),'compression':'original gzip'if p.suffix=='.gz'else'lossless gzip of original bytes'}
spec=importlib.util.spec_from_file_location('observer',SYS/'capacidades/observador_causal_retrospectivo_01.py');obs=importlib.util.module_from_spec(spec);spec.loader.exec_module(obs)
cp(SYS/'capacidades/observador_causal_retrospectivo_01.py','codigo/observador_snapshot.py')
def parent(mid,record=None,path=None,source=None):
 if path is None:path=ARCH/'sistema'/record['snapshot']
 if not path.exists():path=SYS/record['snapshot']
 s=obs.Snapshot(path);summary=s.summary();native=json.loads(s.metadata[obs.LIFE_KEY])
 if record:
  assert sha(path)==record['snapshot_sha256']
  for k in ['N','tick','RAW_sha256','clocks_sha256']:assert summary[k]==record['physical'][k],(path,k)
 else:
  # Sólo restituye la ficha de carga del mismo snapshot. La materia, colas,
  # interfaces, memoria y genealogía nativas permanecen byte a byte intactas.
  record={'schema':'DCS1.1.life.v1',**{k:native[k]for k in ['life_id','world_id','profile','branch','parent']},
   'snapshot':path.relative_to(ARCH/'sistema').as_posix(),'snapshot_sha256':sha(path),'physical':{k:summary[k]for k in ['N','tick','RAW_sha256','clocks_sha256','occupied']},
   'operations':[],'operation_count_offset':native['operation_count'],'knowledge':'Continuidad exacta del snapshot; ficha documental extraída pasivamente de metadatos y campos, no nueva adquisición.',
   'record_recovery':{'method':'EXTRACCION_PASIVA_DE_FICHA_DESDE_SNAPSHOT_COMPLETO','source':source,'checksum_valid':s.checksum_valid,'all_native_bytes_unchanged':True}}
 rec=Path('mecanismos')/mid/'padres'/(sha(path)+'.json');save(STAGE/rec,record);snapshot=Path('estados')/(sha(path)+'.deetsnap.gz');f=cp(path,snapshot)
 return {'record':rec.as_posix(),'snapshot':snapshot.as_posix(),'life':record['life_id'],'tick':summary['tick'],'sha256':sha(path),'source':f,'native_metadata':native,'pending_count':len(s.pending)}
def checkpoint(life,tick,h=None):
 files=sorted((ARCH/'sistema/estado/checkpoints').glob(life+'.T'+str(tick)+'.*.deetsnap.gz'))
 if h:files=[p for p in files if sha(p)==h]
 if len(files)!=1:raise ValueError(('No unique exact checkpoint',life,tick,h,[str(p)for p in files]))
 return files[0]
def copy_protocols(campaign,names):
 out=[];todo=list(names);seen=set()
 while todo:
  name=todo.pop(0)
  if name in seen:continue
  seen.add(name);p=LAB/campaign/name
  out.append(cp(p,Path('codigo')/campaign/name))
  if p.suffix=='.py':
   import ast
   tree=ast.parse(p.read_text(encoding='utf8'))
   for n in ast.walk(tree):
    names2=[q.name for q in n.names]if isinstance(n,ast.Import)else[n.module]if isinstance(n,ast.ImportFrom)and n.module else[]
    for module in names2:
     file=module.split('.')[0]+'.py'
     if(LAB/campaign/file).is_file()and file not in seen:todo.append(file)
 return out
def mechanism(mid,name,families,campaigns,scripts,parents,refs,external=False,inputs=None):
 m={'id':mid,'name':name,'function':name,'word_families':families,'campaigns':campaigns,'variants':[],
    'history_status':'Primarios históricos, protocolos y padres completos exactos recuperados; sin nueva investigación ni cambio de la vida activa.',
    'integrity_status':'SHA de código, datos y snapshots; identidad física del padre comprobada pasivamente.',
    'current_validation':'Pendiente desde ZIP extraído','pending':[],'source_files':[],'bundle':{'scripts':scripts,'parents':parents,'inputs':inputs or [],'external':external},
    'native':{'command':['{python}','{sector}/ejecutar_integrados.py','native',mid,'--out','{out}','--common','{common}'],'timeout_seconds':3600},
    'recalc':{'command':['{python}','{sector}/ejecutar_integrados.py','recalc',mid,'--out','{out}'],'timeout_seconds':240},
    'expected':'Igualdad de campos nativos y resultados frente a primarios originales; paths/timing CPU instrumentales se declaran fuera de la comparación física.',
    'assistance':'Calendario, aparatos, lectores y transducción preparados. La salida nativa decide el comando; el entorno recibe la acción y devuelve su consecuencia por el codec fijo.',
    'limitations':['No fusión de estados entre vidas. No se atribuye competencia de control de Pendulum por emitir torque. No P2/R2 general.']}
 for p,checks,group in refs:
  info=packref(mid,p);m['source_files'].append(info);m['variants'].append({'id':p.stem,'historical_case':p.stem,'reference':info['relative'],'output':(Path('evidencia/campanas')/group/p.name).as_posix(),'checks':checks,'pending':[]})
 for campaign,names in scripts.items():m['source_files']+=copy_protocols(campaign,names)
 return m

manifest=read(HERE/'sector.json');manifest['mechanisms']=[m for m in manifest['mechanisms']if int(m['id'][1:])<130]
IC='INTEGRACION_COGNITIVA_SITUADA_E1_01';C2='CONSOLIDACION_EVOLUCION_E1_CICLO_02';HAB='HABITAT_CAUSAL_Y_ESTRES_E1_01'
ie=EV/IC;ce=EV/C2;he=EV/HAB

# IC01 reproduce nueva experiencia social/ambiental, después utiliza objeto230
# común con tres demoras y conserva los controles de acción y retorno.
refs=[]
integrated=[p for p in sorted(ie.glob('INTEGRATED_*_1[3-4][0-9].json'))if p.name not in ['INTEGRATED_RESERVE_SPEC_132.json']]
integrated=[p for p in integrated if isinstance(read(p),dict)and'first3_file'in read(p)]
for p in integrated:
 d=read(p)
 for name in [d['first3_file'],d['continuation_file']]:refs.append((ie/name,['/physical','/result/rows','/result/reference_after'],IC))
for p in sorted(ie.glob('COMMON_ACTION_*_D*_160.json')):refs.append((p,['/physical','/result/quantity','/result/reference_hub','/result/frames'],IC))
for p in sorted(ie.glob('LATE_SOCIAL_*_166.json')):
 if p.name.endswith('SPEC_166.json'):continue
 refs.append((p,['/physical','/result/external/rows','/result/passive_frames'],IC))
p0=read(ARCH/'sistema/estado/vidas/IC01_COST_NATIVE_73/VIDA.json');assert p0['physical']['tick']==4894
p1=read(ARCH/'sistema/estado/vidas/E1_INTEGRADO_CONTINUABLE_01/VIDA.json');assert p1['physical']['tick']==16485
M=mechanism('M130','Experiencias ambientales y privadas con referencia adquirida y actuación posterior',['2','4','6','8','12'],[IC],
 {IC:['integrated_cost_social.py','common_action_credit.py','late_social_update.py']},[parent('M130',p0),parent('M130',p1)],refs,True)
M['limitations']+=['El objeto común230 discrimina historias; no demuestra una política competente de control. La actualización social tardía conserva ganancias y pérdidas originales.'];manifest['mechanisms'].append(M)

parents=[];inputs=[]
for name in ['INTEGRATED_COST_SOCIAL_132.json','INTEGRATED_OPPOSITE_133.json','INTEGRATED_NO_B_134.json']:
 d=read(ie/name);parents.append(parent('M131',d['final_record']));rel=Path('mecanismos/M131/entradas')/name;save(STAGE/rel,{'final_record':d['final_record']});inputs.append({'source':rel.as_posix(),'target':str(Path('evidencia/campanas')/IC/name),'extracted_from':str(ie/name),'source_sha256':sha(ie/name),'pointer':'$.final_record'})
refs=[(p,['/physical','/result/generic_requests','/result/local_frames','/result/external/rows'],IC)for p in sorted(ie.glob('GENERIC_RECOVERY_R2_*_167.json'))]
refs += [(p,['/after/physical','/data/result/frames','/data/result/external/rows'],C2)for p in sorted(ce.glob('C02_PRE_11*.json'))]
M=mechanism('M131','Recuperación social de ambos signos por recurso genérico y acceso preparado',['3','6','12'],[IC,C2],
 {IC:['generic_social_recovery.py'],C2:['reserva_acceso_previo.py','comun.py']},parents,refs,True,inputs)
M['assistance']='Recuperación asistida P0/R0; ambos signos reciben los mismos recursos genéricos y puertos. El contenido recuperado depende de la historia. Se incluye preparación anterior a la pérdida como variante, sin atribuir iniciativa aprendida.';manifest['mechanisms'].append(M)

# Hábitat usa su interfaz histórica de67ticks y añade la continuación técnica.
refs=[(he/name,['/physical','/result/rows','/result/final_environment'],HAB)for name in ['EXTERNAL_CLOSED_12.json','EXTERNAL_NULL_13.json','EXTERNAL_DELAY_14.json','EXTERNAL_RESERVE_15.json','EXTERNAL_RESUME_17.json']]
parents=[]
for life in ['ECO_EXT_01','ECO_EXT_NULL_13','ECO_EXT_DELAY_14','ECO_EXT_RESERVE_15']:
 parents.append(parent('M132',path=checkpoint(life,4492),source='Initial native fields from EXTERNAL_*_12..15.result.initial_native; metadata from exact complete snapshot'))
M=mechanism('M132','Puente E1 Pendulum con acción anulada retardo y continuidad',['8','12'],[HAB],{HAB:['external_trial.py','habitat.py']},parents,refs,True)
M['bundle']['habitat_trials']=[read(he/n)['result']['condition']for n in ['EXTERNAL_CLOSED_12.json','EXTERNAL_NULL_13.json','EXTERNAL_DELAY_14.json','EXTERNAL_RESERVE_15.json','EXTERNAL_RESUME_17.json']]
M['source_files'].append(cp(LAB/HAB/'external/pendulum_worker.py','codigo/HABITAT_CAUSAL_Y_ESTRES_E1_01/external/pendulum_worker.py'))
M['source_files'].append(packref('M132',he/'INCORPORACION_CLI_23.json'));M['limitations']+=['La batería externa histórica de73pasos incluye un paso del gestor; el protocolo directo aquí reproduce72pasos en cinco tramos. El paso CLI se conserva para recálculo y continuidad documentada, sin contarlo como ya reproducido.'];manifest['mechanisms'].append(M)

admission=read(ce/'C02_ADMISION_OPERATIVA_IC01.json');base=admission['main'];assert base['physical']['tick']==17289
rel='mecanismos/M140/entradas/C02_ADMISION_OPERATIVA_IC01.json';save(STAGE/rel,{'main':base})
refs=[(p,['/after/physical','/data/result/rows'],C2)for p in sorted(ce.glob('C02_GATE_05*.json'))]
refs += [(p,['/after/physical','/data/result/gate/rows'],C2)for p in sorted(ce.glob('C02_HIST_14[0-3]*.json'))]
M=mechanism('M140','Acciones útiles mediante referencia adquirida por desgaste',['4','7','8'],[C2],{C2:['puerta_causal_R1.py','historias_reservadas_puerta.py','comun.py']},[parent('M140',base)],refs,False,[{'source':rel,'target':'evidencia/campanas/'+C2+'/C02_ADMISION_OPERATIVA_IC01.json','source_sha256':sha(ce/'C02_ADMISION_OPERATIVA_IC01.json'),'pointer':'$.main'}]);manifest['mechanisms'].append(M)

refs=[(p,['/after/physical','/data/result/frames','/data/result/record_requests','/data/result/protection_requests'],C2)for p in sorted(ce.glob('C02_COMMIT_34[0-3]*.json'))]
M=mechanism('M141','Protección social conservando agenda comprometida y comunicación',['1','3','6'],[C2],{C2:['proteger_agenda_comprometida.py','comun.py']},[parent('M141',path=checkpoint('E1_INTEGRADO_MAIN',3312,'fa46e6cfec7516ed799723a6bc4edc71869bb6f80780bf78059f1b416936a512'),source='C02_COMMIT_340/343.before.parent + native metadata')],refs)
M['limitations']+=['Protección P0 de rutas back.minus.record/back.plus.record; conserva la comunicación en la fase ensayada y reduce expansión específica. El selector corporal puede agotarse también bajo protección.'];manifest['mechanisms'].append(M)

entry=read(ce/'C02_LATOP_306_USO.json')['result']['INSTRUMENTO'];hh=entry['snapshot_sha256'];snap=checkpoint('E1_CICLO02_LATERAL_LOCAL_01',21108,hh)
rel='mecanismos/M142/entradas/C02_LATOP_306_USO.json';save(STAGE/rel,{'result':{'INSTRUMENTO':entry}})
refs=[(p,['/after/physical','/data/result/frames','/data/result/first_uses/rows','/data/result/new_use/rows','/data/result/last_use/rows'],C2)for p in sorted(ce.glob('C02_SEPARA_33[0-2]*.json'))if '.T'not in p.name]
M=mechanism('M142','Separación física de soportes previos y nueva contribución',['3','5','6','12'],[C2],{C2:['separar_soportes.py','comun.py']},[parent('M142',path=snap,source='C02_LATOP_306_USO.result.INSTRUMENTO + native metadata')],refs,True,[{'source':rel,'target':'evidencia/campanas/'+C2+'/C02_LATOP_306_USO.json','source_sha256':sha(ce/'C02_LATOP_306_USO.json'),'pointer':'$.result.INSTRUMENTO'}]);M['limitations']+=['Redirección P0 de materia ya adquirida, no fusión de recuerdos ni detección autónoma de fallo. Se conserva la nueva experiencia posterior con las pérdidas que produjo.'];manifest['mechanisms'].append(M)

# Las comprobaciones retrospectivas acompañan los mecanismos donde cambian
# la interpretación. La herramienta se clasifica como instrumento externo.
for m in manifest['mechanisms']:
 if m['id']in ['M112','M122']:
  m['campaigns'].append('AUDITORIA_RETROSPECTIVA_01')
  for name in ['CALCULOS_R5.json']:
   m['source_files'].append(packref(m['id'],EV/'AUDITORIA_RETROSPECTIVA_01'/name))
 if m['id']=='M122':
  for v in m['variants']:
   group,case=v['historical_case'].split('/',1);source=EV/'ACCESO_ADAPTATIVO_01'/group/case/'ESTADO_COMPLETO_DESPUES_6.deetsnap.gz'
   if source.exists():v['causal_state6']=cp(source,Path('mecanismos/M122/convergencia')/(case+'.deetsnap.gz'))

third=[]
for folder in ['gymnasium','gymnasium-1.4.0.dist-info','farama_notifications','farama_notifications-0.0.6.dist-info']:
 for f in (SYS/'runtime/habitat_externo_deps'/folder).rglob('*'):
  if f.is_file()and'__pycache__'not in f.parts and f.suffix!='.pyc':third.append(cp(f,Path('terceros312')/f.relative_to(SYS/'runtime/habitat_externo_deps')))
manifest['third_party']={'components':['Gymnasium1.4.0','farama_notifications0.0.6'],'files':third,'dependencies_declared':['CPython3.12.x64','NumPy2.3.5','typing_extensions4.16.0'],'pendulum_source_sha256':'f349a2160b54fce73b197a9f94f38b1e27964390bbc32acf2f71671ede984288','license_locations':['terceros312/gymnasium-1.4.0.dist-info/licenses/LICENSE','terceros312/farama_notifications-0.0.6.dist-info/LICENSE']}
manifest['covered_campaigns']+=['AUDITORIA_RETROSPECTIVA_01',HAB,IC,C2];manifest['remaining_campaigns']=[]
manifest['common_instrument_adaptations']=['Ruta y hash del intérprete externo se fijan explícitamente en cada copia de contrato; la versión y fuente del entorno se verifican.','Los plazos monotónicos históricos se reemplazan sólo como límite de proceso de reproducción; el calendario físico de cada protocolo no cambia.','No se requiere el gestor completo ni la interfaz gráfica de Cognitive.']
# Dos procesos consecutivos FIRST3/CONTINUE9 pertenecen a la misma variante,
# no a dos aprendizajes ni a dos condiciones experimentales independientes.
integrated=next(m for m in manifest['mechanisms']if m['id']=='M130');combined=[];seen=set()
for v in integrated['variants']:
 key=v['id']
 if key.endswith('_FIRST3')or key.endswith('_CONTINUE9'):
  base=key.removesuffix('_FIRST3').removesuffix('_CONTINUE9')
  if base in seen:continue
  seen.add(base);phases=[x for x in integrated['variants']if x['id']in[base+'_FIRST3',base+'_CONTINUE9']]
  first=dict(phases[0]);first.update(id=base,historical_case=base,phase_artifacts=phases,continuity='3 pasos y continuación en otro proceso de9pasos; una misma condición e historia')
  combined.append(first)
 else:combined.append(v)
integrated['variants']=combined
save(HERE/'sector.json',manifest);save(STAGE/'sector.json',manifest)
print(json.dumps({'mechanisms':len(manifest['mechanisms']),'variants':sum(len(m['variants'])for m in manifest['mechanisms']),'files':sum(p.is_file()for p in STAGE.rglob('*')),'bytes':sum(p.stat().st_size for p in STAGE.rglob('*')if p.is_file())},ensure_ascii=False))
