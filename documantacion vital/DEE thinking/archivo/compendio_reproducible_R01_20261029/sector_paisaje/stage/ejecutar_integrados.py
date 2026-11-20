"""Reproduce protocolos integrados históricos en un Store aislado por grupo.

El evaluador compara después de terminar; no elige decisiones de E1.
"""
from pathlib import Path
import tempfile
import argparse,sys,json,gzip,hashlib,shutil,subprocess,os,time,importlib.util
BASE=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):
 p=Path(p);b=p.read_bytes();return json.loads(gzip.decompress(b)if p.suffix=='.gz'else b)
def save(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def get(d,p):
 for k in p.strip('/').split('/'):d=d[int(k)]if isinstance(d,list)else d[k]
 return d
def unpack(raw):
 assert not isinstance(raw,float);v=int(raw);assert 0<=v<2**64
 def s(k):q=(v>>k)&15;return q-16 if q&8 else q
 return {'state':v&0xffffffff,'s_reg':(v>>32)&65535,'direction':[s(k)for k in(48,52,56)],'semantic':(v>>60)&15}
def walk(v,p='$'):
 if isinstance(v,dict):
  yield p,v
  for k,x in v.items():
   if k not in('parent','before','after','final_record','first3_snapshot','code'):yield from walk(x,p+'.'+k)
 elif isinstance(v,list):
  for i,x in enumerate(v):yield from walk(x,p+'['+str(i)+']')
def artifacts(m):
 for v in m['variants']:
  yield from v.get('phase_artifacts',[v])
def normalized(v):
 if isinstance(v,dict):return {k:normalized(x)for k,x in v.items()if k not in('host_worker_seconds','source_path')}
 if isinstance(v,list):return[normalized(x)for x in v]
 return v
def recalc(m,out):
 errors=[];count=0;rows=[]
 sources=list(artifacts(m))+[{'id':Path(p).stem,'reference':p,'archived_only':True}for p in m.get('archived_additional_primaries',[])]
 for v in sources:
  p=BASE/v['reference'];d=read(p);native=[];submitted=set();receipts={};actions=[]
  for loc,r in walk(d):
   if {'raw','state','s_reg','direction','semantic'}<=r.keys():
    q=unpack(r['raw']);count+=1
    if any(q[k]!=r[k]for k in q):errors.append([v['id'],loc,'RAW_FIELDS_MISMATCH'])
    if isinstance(r.get('clock'),float):errors.append([v['id'],loc,'FLOAT_CLOCK'])
   if isinstance(r.get('id'),int)and'payload'in r:submitted.add(r['id'])
   if isinstance(r.get('id'),int)and'status'in r:
    old=receipts.get(r['id'])
    if old is None or old.get('status')in('scheduled','pending'):receipts[r['id']]=r
   # Comando del péndulo obtenido exclusivamente del registro físico.
   if'native_read'in r and'actuator'in r:
    q=unpack(r['native_read']['raw']);vec=q['direction'];cmd=2*vec[0]if q['state']==1 and q['semantic']==1 and vec in([1,0,0],[-1,0,0],[0,0,0])else 0
    if cmd!=r['actuator']['command']:errors.append([v['id'],loc,'NATIVE_ACTUATOR_CODEC_MISMATCH'])
    actions.append({'tick':r.get('tick'),'native_command':cmd,'executed_torque':r['executed_torque']})
   if'native'in r and'native_command'in r and'raw_quantity_command_gain2'in r:
    q=unpack(r['native']['raw']);vec=q['direction'];raw=2*vec[0]if q['state']==1 and q['semantic']==1 and vec in([1,0,0],[-1,0,0])else 0
    if raw!=r['raw_quantity_command_gain2']:errors.append([v['id'],loc,'QUANTITY_CODEC_MISMATCH'])
    social=0
    for b in r.get('social_reads',[]):
     z=unpack(b['native']['raw']);ok=z['state']==1 and z['semantic']==1 and z['s_reg']>0 and z['direction']==[b['bank'],0,0]
     if ok:social+=b['bank']
     if ok!=b['qualified']:errors.append([v['id'],loc,'SOCIAL_QUALIFICATION_MISMATCH'])
    cmd=max(-2,min(2,raw//2+social))if r.get('external_motor_wiring')=='quantity_gain1_plus_social_gain1'else raw
    if cmd!=r['native_command']:errors.append([v['id'],loc,'FIXED_MIXED_WIRING_MISMATCH'])
    actions.append({'tick':r.get('tick'),'native_command':cmd,'executed_torque':r['executed_torque']})
   if'native_response'in r and'native_action'in r and'environment'in r:
    q=unpack(r['native_response']['raw']);vec=q['direction'];valid=q['state']==1 and q['semantic']==1 and q['s_reg']==7 and vec in([1,0,0],[-1,0,0]);action=-vec[0]if valid else 0
    if action!=r['native_action']or valid!=r['valid']:errors.append([v['id'],loc,'GATE_NATIVE_ACTION_MISMATCH'])
    env=r['environment'];executed=r['executed_action'];opened=executed==1 and env['force']>env['resistance_before'];jam=executed==1 and not opened
    useful=opened or(executed==-1 and env['force']<=env['resistance_before'])
    if opened!=env['opened']or jam!=env['jam']or int(opened)-int(jam)!=r['utility_auditor_only']or bool(useful)!=r['useful_auditor_only']:errors.append([v['id'],loc,'GATE_ENVIRONMENT_RECALCULATION_MISMATCH'])
    actions.append({'tick':r.get('tick'),'native_action':action,'executed_action':executed,'useful':useful,'utility':int(opened)-int(jam),'resistance_after':env['resistance_after']})
  statuses={}
  for i in submitted:
   s=receipts.get(i,{}).get('status','final_receipt_not_in_primary');statuses[s]=statuses.get(s,0)+1
  rows.append({'id':v['id'],'reference':v['reference'],'sha256':sha(p),'actions':actions,'requested_IDs':len(submitted),'recorded_final_statuses':statuses,'correct_native_torques':sum(x.get('executed_torque')==x.get('native_command')for x in actions if'native_command'in x),'gate_useful':sum(x.get('useful',False)for x in actions),'gate_utility':sum(x.get('utility',0)for x in actions)})
 r={'mechanism':m['id'],'mode':'RECALCULO_ARCHIVADO_SIN_MOTOR','new_native_ticks':0,'variants':rows,'raw_fields_recomputed':count,'errors':errors,'interpretation':'Decodificación y efectos calculados desde primarios; no sustituye reproducción nativa ni acredita decisiones nuevas.'}
 save(out/'RECALCULO.json',r);print(json.dumps({'mechanism':m['id'],'artifacts':len(rows),'raw_fields':count,'errors':len(errors)}));return int(bool(errors))
def prepare(m,out,common,external):
 job=out/'trabajo';system=job/'sistema'
 shutil.copytree(common,system,ignore=shutil.ignore_patterns('__pycache__','*.pyc','estado'),dirs_exist_ok=False)
 for name in ['vidas','checkpoints','locks']:(system/'estado'/name).mkdir(parents=True,exist_ok=True)
 for par in m['bundle']['parents']:
  record=read(BASE/par['record']);snap=BASE/par['snapshot'];assert sha(snap)==par['sha256'];dst=system/record['snapshot'];dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(snap,dst);save(system/'estado/vidas'/record['life_id']/'VIDA.json',record)
 for campaign in m['bundle']['scripts']:
  src=BASE/'codigo'/campaign
  shutil.copytree(src,job/'laboratorio/campanas'/campaign,dirs_exist_ok=True)
  # Algunos protocolos históricos reservan3000s mediante una resta fija.
  # Ese margen es de administración, no de calendario físico. Se conserva
  # además del tiempo de ejecución; el launcher mantiene su timeout real.
  lab=job/'laboratorio/campanas'/campaign;end=time.monotonic()+m['native']['timeout_seconds']+3000
  for file in ['PRESUPUESTO_Y_PADRE.json','PRESUPUESTO.json','PRESUPUESTO_Y_DISENO_INICIAL.json']:
   save(lab/file,{'schema':'COMPENDIO.REPRODUCCION.LIMITE_DE_PROCESO','monotonic_deadline_seconds':end,'monotonic_deadline':end,'reserved_closure_seconds':0,'legacy_fixed_closure_margin_seconds':3000,'real_outer_timeout_seconds':m['native']['timeout_seconds'],'physical_calendar_modified':False})
 for item in m['bundle'].get('inputs',[]):
  target=job/item['target'];target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(BASE/item['source'],target)
 if m['bundle']['external']:
  if not external or not external.is_file():raise FileNotFoundError('Puente requiere --external-python CPython3.12 x64 con NumPy2.3.5/typing_extensions4.16, sin instalación global automática.')
  deps=system/'runtime/habitat_externo_deps';deps.mkdir(parents=True,exist_ok=True)
  for source in [common.parent/'terceros312',BASE/'terceros312']:
   if source.is_dir():shutil.copytree(source,deps,ignore=shutil.ignore_patterns('__pycache__','*.pyc'),dirs_exist_ok=True)
  worker=BASE/'codigo/HABITAT_CAUSAL_Y_ESTRES_E1_01/external/pendulum_worker.py';target=system/'app/habitat_externo/pendulum_worker.py';target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(worker,target)
  # Preflight externo N0. No crea ni avanza un Runtime DEE.
  probe=subprocess.run([str(external),'-I','-B',str(worker),'--deps',str(deps)],input='{"op":"info"}\n{"op":"close"}\n',capture_output=True,text=True,encoding='utf8',timeout=60,check=True)
  info=json.loads(probe.stdout.splitlines()[0])['identity']
  if info['gymnasium']!='1.4.0'or info['numpy']!='2.3.5'or info['source_sha256']!='f349a2160b54fce73b197a9f94f38b1e27964390bbc32acf2f71671ede984288':raise RuntimeError('Identidad externa distinta del contrato histórico')
  save(out/'IDENTIDAD_EXTERNA.json',info)
  original=read(BASE/'codigo/contratos/HABITAT_EXTERNO_01.original.json');original.update(external_python=str(external.resolve()),external_python_sha256=sha(external),worker_sha256=sha(target));save(system/'contratos/HABITAT_EXTERNO_01.json',original)
  legacy=job/'laboratorio/campanas/HABITAT_CAUSAL_Y_ESTRES_E1_01/external/deps'
  if legacy.parent.exists():shutil.copytree(deps,legacy,dirs_exist_ok=True)
 return job
def native(m,out,common,external,only_script=None,reference_prefix=None):
 if bool(only_script)!=bool(reference_prefix):raise ValueError('Una reproducción parcial exige --only-script y --reference-prefix explícitos; no se ocultan los artefactos excluidos.')
 selected=list(artifacts(m));unselected=[]
 if reference_prefix:
  unselected=[v['id']for v in selected if not v['id'].startswith(reference_prefix)];selected=[v for v in selected if v['id'].startswith(reference_prefix)]
  if not selected:raise ValueError('El prefijo no selecciona primarios del mecanismo')
 done=out/'REPRODUCCION.json'
 if done.exists():print(json.dumps({'existing_result':str(done),'not_repeated':True}));return int(read(done)['failed']>0)
 job=prepare(m,out,common,external);env=dict(os.environ,OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1');env.pop('PYTHONPATH',None)
 if external:env['DEE_EXTERNAL_PYTHON']=str(external.resolve())
 executions=[];commands=[]
 for campaign,names in m['bundle']['scripts'].items():
  for name in names:
   if name in('comun.py','habitat.py'):continue
   if only_script and name!=only_script:continue
   if m['id']=='M132'and name=='external_trial.py':
    for trial in m['bundle']['habitat_trials']:
     args=[]
     for key,value in trial.items():
      if key=='reset_environment':
       if value:args.append('--reset-environment')
      else:args.extend(['--'+key.replace('_','-'),str(value)])
     commands.append((campaign,name,args,trial['name']))
   else:commands.append((campaign,name,[],Path(name).stem))
 for campaign,name,args,label in commands:
  source=job/'laboratorio/campanas'/campaign/name;cmd=[sys.executable,'-I','-B','-X','utf8',str(BASE/'protocolo_portable.py'),str(source),*args];t=time.monotonic()
  with(out/(label+'.stdout.log')).open('w',encoding='utf8')as so,(out/(label+'.stderr.log')).open('w',encoding='utf8')as se:
   try:p=subprocess.run(cmd,cwd=tempfile.gettempdir(),env=env,stdout=so,stderr=se,timeout=m['native']['timeout_seconds']);exit_code=p.returncode
   except subprocess.TimeoutExpired:exit_code=124
  executions.append({'script':name,'label':label,'exit_code':exit_code,'seconds':time.monotonic()-t,'command':cmd});print(json.dumps(executions[-1]),flush=True)
 results=[]
 if not commands:raise ValueError('No se seleccionó un protocolo ejecutable')
 for v in selected:
  path=job/v['output'];checks=[]
  if path.is_file():
   actual=read(path);reference=read(BASE/v['reference'])
   for ptr in v['checks']:
    try:a=normalized(get(actual,ptr));b=normalized(get(reference,ptr));checks.append({'pointer':ptr,'matches':a==b,'actual':a,'reference':b})
    except(KeyError,IndexError,TypeError)as e:checks.append({'pointer':ptr,'matches':False,'error':str(e)})
  results.append({'variant':v['id'],'available':path.exists(),'matched':bool(checks)and all(c['matches']for c in checks),'checks':checks})
 report={'mechanism':m['id'],'mode':'PROTOCOLOS_HISTORICOS_NATIVOS_EN_COPIAS_AISLADAS','executions':executions,'results':results,'matched':sum(v['matched']for v in results),'failed':sum(not v['matched']for v in results),'artifact_checks':len(results),'experimental_variants':sum(not reference_prefix or v['id'].startswith(reference_prefix)for v in m['variants']),'experimental_variants_in_manifest':len(m['variants']),
  'instrumental_adaptations':['Límites monotónicos del proceso reiniciados con margen administrativo heredado3000s; timeout exterior real sin ampliar. Sin cambiar ticks/eventos.','Ruta/hash del intérprete externo configurados en copia del contrato.','Sólo source_path y host_worker_seconds se excluyen de la igualdad: son ubicación y tiempo CPU; no resultados físicos.'],
  'no_original_Cognitive_state_used':True,'no_new_scientific_protocol':True,'selected_script':only_script,'selected_reference_prefix':reference_prefix,'artifacts_not_executed_by_request':unselected}
 save(done,report);return int(report['failed']>0)
def main():
 p=argparse.ArgumentParser();p.add_argument('mode',choices=['native','recalc']);p.add_argument('mechanism');p.add_argument('--out',type=Path,required=True);p.add_argument('--common',type=Path);p.add_argument('--external-python',type=Path,default=os.environ.get('DEE_EXTERNAL_PYTHON'));p.add_argument('--only-script');p.add_argument('--reference-prefix');a=p.parse_args();m=next(m for m in read(BASE/'sector.json')['mechanisms']if m['id']==a.mechanism);a.out.mkdir(parents=True,exist_ok=True)
 return recalc(m,a.out)if a.mode=='recalc'else native(m,a.out,a.common,a.external_python,a.only_script,a.reference_prefix)
if __name__=='__main__':raise SystemExit(main())
