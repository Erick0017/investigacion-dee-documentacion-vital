"""Prospective continuation of MAIN after its actual adverse S49 future.

All stimuli fixed before use. No command consumes an auditor prediction to
choose a native action. Distinct guarded processes share one full living state.
"""
from pathlib import Path
import argparse,sys,subprocess,json,gzip,hashlib,time
p=argparse.ArgumentParser();p.add_argument('--system',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--case',required=True);a=p.parse_args();sys.path[:0]=[str(a.system),str(a.system.parent/'laboratorio/campanas/PAISAJE_CAUSAL_01')]
from app.lives import Store
from app.native_tools import physical
from app.process_control import protect_current
from instrumentos_pc01 import sha,frame,receipts,witness,native_digest
protect_current(output=a.out/'RECURSOS.json');a.out.mkdir(parents=True,exist_ok=False);s=Store(a.system);life='E1_ACCESO_ADAPTATIVO_01';initial=s.record(life)
if initial['physical']['tick']!=44695:raise ValueError('MAIN continued legitimately or differs from sealed reserve start. No rewind/substitution is allowed')
design=Path(__file__).with_name('DISENO_CONFIRMATORIO_36.json');data={'case':a.case,'life':life,'initial_record':initial,'source_sha256':sha(__file__),'sealed_design_file_sha256':sha(design),'inputs_fixed_before_outcomes':True,'technical_scope':'Existing manager, separate guarded processes, owner run_until, no targets or historical files read by participant. Predictions in the sealed design are auditor-only.','commands':[],'samples':[]}
def command(*tokens,options=None):
    if options is not None:tokens=(*tokens,'--parametros',json.dumps(options,separators=(',',':'),ensure_ascii=False),'--max-segundos','90')
    argv=[sys.executable,'-I','-B','-X','utf8',str(a.system/'gestionar.py'),'--system-root',str(a.system),*tokens];number=len(data['commands']);began=time.perf_counter();source_hashes={str(p.relative_to(a.system)):sha(p)for p in(a.system/'gestionar.py',a.system/'app/lives.py',a.system/'app/advance_budget.py',a.system/'capacidades/acceso_adaptativo_01.py')};r=subprocess.run(argv,cwd=a.out,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=150);(a.out/(str(number).zfill(2)+'.stdout.json')).write_bytes(r.stdout);(a.out/(str(number).zfill(2)+'.stderr.txt')).write_bytes(r.stderr);result=json.loads(r.stdout)if r.stdout else None;data['commands'].append({'number':number,'argv':argv,'returncode':r.returncode,'seconds':time.perf_counter()-began,'sources_at_child_start':source_hashes,'stdout_sha256':hashlib.sha256(r.stdout).hexdigest(),'stderr_sha256':hashlib.sha256(r.stderr).hexdigest(),'result':result});(a.out/'PROGRESO.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    if r.returncode:raise RuntimeError('Manager recorded actual failed future: '+r.stderr.decode('utf8','replace'))
    return result
def passive(stage):
    rec,x=s.load(life);before=native_digest(x.world.runtime);data['samples'].append({'stage':stage,'tick':x.tick,'record_snapshot':rec['snapshot'],'record_snapshot_sha256':rec['snapshot_sha256'],'physical':physical(x.world,occupation=True),'native_exact':before,'policy_witness':witness(x.world,[15,15,50]),'frame':frame(x.world),'receipts':receipts(x.world.runtime)});assert before==native_digest(x.world.runtime)
try:
    command('guardar','--vida',life);passive('actual_lived_start')
    command('experiencia','--vida',life,'acceso-preparar-local',options={'episode':'AA36_CONFIRMA','availability':[-1,1],'contents':[-1,1],'delay':67})
    for stage in('first','learned','content','access','transformed','received','social','use'):
        command('experiencia','--vida',life,'acceso-avanzar-episodio',options={'stage':stage,'max_seconds':90});passive(stage)
        if stage=='learned':command('guardar','--vida',life);command('acceso-estado','--vida',life)
    data['reserved_old_functions']={}
    for value in(73,121):data['reserved_old_functions'][str(value)]=command('experiencia','--vida',life,'espanol-contexto',options={'value':value,'method':'B'})
    for word,opt in(('cerca',{'parameter':5,'load':3}),('lejos',{'parameter':-5,'load':3})):data['reserved_old_functions'][word]=command('experiencia','--vida',life,'paisaje-contexto-dosis',options=opt)
    for word,name in(('toca','contactoA'),('no toca','freeRepair5')):data['reserved_old_functions'][word]=command('experiencia','--vida',life,'espanol-contacto-consultar',options={'frame':name})
    data['first_common_recovery']=command('experiencia','--vida',life,'acceso-recuperar-receptor',options={'old_reader':True,'max_seconds':90});passive('after_reserved_functions_and_recovery')
    data['later_experiences']=[]
    for value in(72,116,79,118):
        row={'actual_object':value,'current_use':command('experiencia','--vida',life,'espanol-contexto',options={'value':value,'method':'B'}),'common_recovery':command('experiencia','--vida',life,'acceso-recuperar-receptor',options={'old_reader':False,'max_seconds':90})};data['later_experiences'].append(row)
    data['final_panel']={}
    for value in(61,119):data['final_panel'][str(value)]=command('experiencia','--vida',life,'espanol-contexto',options={'value':value,'method':'B'})
    for word,opt in(('cerca',{'parameter':3,'load':4}),('lejos',{'parameter':-3,'load':6})):data['final_panel'][word]=command('experiencia','--vida',life,'paisaje-contexto-dosis',options=opt)
    for word,name in(('toca','contactoA'),('no toca','freeRepair5')):data['final_panel'][word]=command('experiencia','--vida',life,'espanol-contacto-consultar',options={'frame':name})
    data['last_common_recovery']=command('experiencia','--vida',life,'acceso-recuperar-receptor',options={'old_reader':True,'max_seconds':90});command('guardar','--vida',life);passive('final');data['final_record']=s.record(life)
except Exception as error:
    data['failure']={'type':type(error).__name__,'detail':str(error)};data['reached_record']=s.record(life);raise
finally:
    with gzip.open(a.out/'PRIMARIOS.json.gz','wt',encoding='utf8',compresslevel=9)as f:json.dump(data,f,ensure_ascii=False,separators=(',',':'))
print(json.dumps({'life':life,'tick':data['final_record']['physical']['tick'],'opaque_codes_by_stage':[(r['result']['result']['INSTRUMENTO']['stage'],r['result']['result']['CONTENT_CODES'])for r in data['commands']if isinstance(r.get('result'),dict)and isinstance(r['result'].get('result'),dict)and r['result']['result'].get('INSTRUMENTO',{}).get('kind')=='LOCAL_S50'and'stage'in r['result']['result']['INSTRUMENTO']],'reserved_old_functions':{k:v['result'].get('SPANISH_DECODED',v['result'].get('TRADUCCION',{}).get('SPANISH_DECODED'))for k,v in data['reserved_old_functions'].items()},'final_panel':{k:v['result'].get('SPANISH_DECODED',v['result'].get('TRADUCCION',{}).get('SPANISH_DECODED'))for k,v in data['final_panel'].items()},'final_B_codes':data['last_common_recovery']['result']['CONTENT_CODES']},ensure_ascii=False))
